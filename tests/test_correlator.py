"""
Unit tests for diff parsing and stack frame correlation.
"""

import pytest
import subprocess

from diffsheriff.correlator import correlate_stack_to_diff, parse_unified_diff
from diffsheriff.triage import StackFrame

SAMPLE_DIFF = """
--- a/src/parser.c
+++ b/src/parser.c
@@ -40,6 +40,8 @@ void parse_header(char *input) {
     char key[64];
     char val[128];
+    if (strlen(input) > 180) return;
     sscanf(input, "%[^:]: %[^\r\n]", key, val);
 }
"""


def test_parse_unified_diff():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    assert len(hunks) == 1
    hunk = hunks[0]
    assert hunk.file_path == "src/parser.c"
    assert hunk.new_start == 40
    assert hunk.new_length == 8


def test_correlate_stack_direct_match():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    frames = [
        StackFrame(
            index=0,
            address="0x401234",
            function="parse_header",
            file="src/parser.c",
            line=42,
        )
    ]
    verdict = correlate_stack_to_diff(frames, hunks)
    assert verdict.is_correlated is True
    assert verdict.correlation_type == "Direct Match"


def test_correlate_stack_indirect_match():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    frames = [
        StackFrame(
            index=0,
            address="0x405555",
            function="inner_copy",
            file="src/string_utils.c",
            line=12,
        ),
        StackFrame(
            index=1,
            address="0x401234",
            function="parse_header",
            file="src/parser.c",
            line=42,
        ),
    ]
    verdict = correlate_stack_to_diff(frames, hunks)
    assert verdict.is_correlated is True
    assert verdict.correlation_type == "Indirect (Caller/Callee)"


def test_correlate_stack_inconclusive():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    frames = [
        StackFrame(
            index=0,
            address="0x409999",
            function="unrelated_function",
            file="src/unrelated.c",
            line=200,
        )
    ]
    verdict = correlate_stack_to_diff(frames, hunks)
    assert verdict.is_correlated is False
    assert verdict.correlation_type == "Inconclusive"


def test_hunk_end_is_exclusive():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    frames = [
        StackFrame(
            index=0,
            address="0x401234",
            function="after_hunk",
            file="src/parser.c",
            line=48,
        )
    ]
    assert correlate_stack_to_diff(frames, hunks).is_correlated is False


def test_same_basename_in_different_directory_does_not_match():
    hunks = parse_unified_diff(SAMPLE_DIFF)
    frames = [
        StackFrame(
            index=0,
            address="0x401234",
            function="parse_header",
            file="other/parser.c",
            line=42,
        )
    ]
    assert correlate_stack_to_diff(frames, hunks).is_correlated is False


def test_deleted_only_hunk_has_no_new_line_match():
    deleted = """
--- a/src/parser.c
+++ b/src/parser.c
@@ -40,2 +40,0 @@ void parse_header(char *input) {
-old_line();
-another_old_line();
"""
    hunks = parse_unified_diff(deleted)
    frames = [
        StackFrame(
            index=0,
            address="0x401234",
            function="parse_header",
            file="src/parser.c",
            line=40,
        )
    ]
    assert correlate_stack_to_diff(frames, hunks).is_correlated is False


def test_context_is_not_an_edit():
    frames = [StackFrame(0, "", "parse_header", "src/parser.c", 44)]
    assert not correlate_stack_to_diff(
        frames, parse_unified_diff(SAMPLE_DIFF)
    ).is_correlated


def test_deleted_file_does_not_inherit_previous_name():
    diff = """diff --git a/a.c b/a.c
--- a/a.c
+++ b/a.c
@@ -1 +1 @@
-old
+new
diff --git a/deleted.c b/deleted.c
--- a/deleted.c
+++ /dev/null
@@ -8 +0,0 @@
-gone
"""
    hunks = parse_unified_diff(diff)
    assert hunks[1].old_file_path == "deleted.c"
    frame = StackFrame(0, "", "gone", "deleted.c", 8)
    assert correlate_stack_to_diff([frame], hunks, "base").is_correlated
    assert not correlate_stack_to_diff([frame], hunks).is_correlated


def test_rename_spaces_and_shifted_location():
    from diffsheriff.correlator import finding_signature
    from diffsheriff.triage import triage_execution_result

    diff = """diff --git a/old file.c b/new file.c
--- a/old file.c
+++ b/new file.c
@@ -1,0 +2,2 @@
+new
+lines
"""
    hunks = parse_unified_diff(diff)
    report = triage_execution_result(
        1,
        "",
        "ERROR: AddressSanitizer: heap-buffer-overflow\n"
        " #0 0x1234 in parse /src/new file.c:12:3\n",
    )
    signature = finding_signature(report, "patch", hunks)
    assert signature["file"] == "old file.c"
    assert signature["line"] == 10


def test_pure_rename_preserves_real_a_b_directory_names():
    from diffsheriff.correlator import finding_signature
    from diffsheriff.triage import triage_execution_result

    hunks = parse_unified_diff(
        "diff --git a/a/old.c b/b/new.c\nrename from a/old.c\nrename to b/new.c\n"
    )
    report = triage_execution_result(
        1,
        "",
        "ERROR: AddressSanitizer: heap-buffer-overflow\n"
        " #0 0x123 in parse /src/b/new.c:10:1",
    )
    assert finding_signature(report, "patch", hunks)["file"] == "a/old.c"
    assert not correlate_stack_to_diff(report.stack_trace, hunks).is_correlated


@pytest.mark.parametrize("caller", [False, True])
def test_insertion_matches_an_observed_function_without_old_edited_lines(caller):
    diff = (
        "--- a/source.c\n+++ b/source.c\n"
        "@@ -7,0 +8 @@ int parse(char *input) {\n+    if (!input) return 0;\n"
    )
    frames = [StackFrame(0, "", "parse", "/src/source.c", 8)]
    if caller:
        frames.insert(0, StackFrame(0, "", "copy", "/src/copy.c", 20))
    hunks = parse_unified_diff(diff)
    assert hunks[0].old_lines == []
    result = correlate_stack_to_diff(frames, hunks, "base")
    assert result.is_correlated
    assert result.correlation_type == "Insertion in observed function"
    assert result.matched_frame.function == "parse"
    assert result.hunk.new_lines == [8]


@pytest.mark.parametrize(
    "header,function,path,line",
    [
        ("", "parse", "/src/source.c", 8),
        ("int unrelated(char *input) {", "parse", "/src/source.c", 8),
        ("int parse(char *input) {", "unknown", "/src/source.c", 8),
        ("int parse(char *input) {", "parse", "/src/other/source.c", 8),
        ("int parse(char *input) {", "parse", "/src/source.c", 7),
        ("return parse(input)", "parse", "/src/source.c", 8),
        ("int parse(char *input);", "parse", "/src/source.c", 8),
        ("int parse(char *input) {", "parse(int)", "/src/source.c", 8),
    ],
)
def test_insertion_rejects_missing_or_ambiguous_function_evidence(
    header, function, path, line
):
    diff = f"--- a/source.c\n+++ b/source.c\n@@ -7,0 +8 @@ {header}\n+guard();\n"
    frames = [StackFrame(0, "", function, path, line)]
    assert not correlate_stack_to_diff(
        frames, parse_unified_diff(diff), "base"
    ).is_correlated


def test_multiple_candidate_insertions_remain_inconclusive():
    diff = (
        "--- a/source.c\n+++ b/source.c\n"
        "@@ -5,0 +6 @@ int parse(char *input) {\n+first();\n"
        "@@ -7,0 +9 @@ int parse(char *input) {\n+second();\n"
    )
    frames = [StackFrame(0, "", "parse", "/src/source.c", 8)]
    assert not correlate_stack_to_diff(
        frames, parse_unified_diff(diff), "base"
    ).is_correlated


def test_actual_git_insertion_hunk_matches_the_observed_function(tmp_path):
    source = tmp_path / "source.c"
    source.write_text("int parse(int value) {\n    return value;\n}\n")
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "source.c"], check=True, capture_output=True
    )
    source.write_text(
        "int parse(int value) {\n    if (value == 0) return 0;\n    return value;\n}\n"
    )
    diff = subprocess.run(
        [
            "git",
            "-C",
            str(tmp_path),
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--unified=0",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    frames = [StackFrame(0, "", "parse", "/src/source.c", 2)]
    result = correlate_stack_to_diff(frames, parse_unified_diff(diff), "base")
    assert result.is_correlated
    assert result.correlation_type == "Insertion in observed function"
