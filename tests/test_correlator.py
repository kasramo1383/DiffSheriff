"""
Unit tests for diff parsing and stack frame correlation.
"""

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
            line=44,
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
            line=44,
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
