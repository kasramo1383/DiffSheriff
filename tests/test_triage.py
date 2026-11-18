"""Unit tests for sanitizer and signal classification."""

import pytest

from diffsheriff.triage import triage_execution_result

EXPECTED_BASELINE_SIGNATURE = {
    "error_type": "out-of-bounds",
    "file": "trees.c",
    "function": "compress_block",
    "line": 1092,
}
DIAGNOSIS = {
    "observed_error": (
        "trees.c:1092:20: runtime error: index 734 out of bounds "
        "for type 'const uch[512]'"
    ),
    "sanitizer_warning": (
        "==5684==WARNING: invalid path to external symbolizer!\n"
        "==5684==WARNING: Failed to use and restart external symbolizer!"
    ),
    "expected_function": "compress_block",
}


def recorded_ubsan_stderr(
    frames,
    summary="SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior "
    "trees.c:1092:20 in",
    warning=True,
):
    """The raw stderr retained in the symbolizer diagnosis, with its frame block.

    The warning and runtime-error lines are the recorded evidence verbatim; only
    the warning block and frame block vary between the two cases.
    """
    return (
        (DIAGNOSIS["sanitizer_warning"] + "\n\n" if warning else "")
        + DIAGNOSIS["observed_error"]
        + "\n"
        + frames
        + "\n"
        + summary
        + "\n"
    )


def test_negative_subprocess_return_code_is_signal():
    report = triage_execution_result(-11, "", "")
    assert report.is_crash is True
    assert report.signal_name == "SIGSEGV"
    assert report.detection_mechanism == "OS Signal"


def test_shell_style_return_code_is_signal():
    report = triage_execution_result(134, "", "", shell_status=True)
    assert report.is_crash is True
    assert report.signal_name == "SIGABRT"


def test_ubsan_runtime_error_is_classified_separately():
    report = triage_execution_result(
        1,
        "",
        "source.c:8:3: runtime error: division by zero",
    )
    assert report.is_crash is True
    assert report.error_type == "division-by-zero"
    assert report.detection_mechanism == "UndefinedBehaviorSanitizer"


@pytest.mark.parametrize(
    "code,shell,expected",
    [(-6, False, "SIGABRT"), (134, True, "SIGABRT"), (134, False, None)],
)
def test_ubsan_preserves_actual_termination(code, shell, expected):
    report = triage_execution_result(
        code, "", "source.c:8:3: runtime error: division by zero", shell_status=shell
    )
    assert report.signal_name == expected
    assert report.exit_code == code
    assert report.detection_mechanism == "UndefinedBehaviorSanitizer"


def test_asan_nonzero_exit_is_not_invented_as_a_signal():
    report = triage_execution_result(
        1,
        "",
        "ERROR: AddressSanitizer: heap-buffer-overflow",
    )
    assert report.is_crash is True
    assert report.signal_name is None


def test_high_ordinary_exit_is_not_invented_as_signal():
    assert triage_execution_result(134, "", "").signal_name is None


def test_timeout_is_not_a_signal():
    report = triage_execution_result(-1, "", "", timed_out=True)
    assert report.error_type == "timeout"
    assert not report.is_crash


def test_output_echo_is_not_a_sanitizer_report():
    report = triage_execution_result(
        0, "ERROR: AddressSanitizer: heap-buffer-overflow", ""
    )
    assert not report.is_crash


def test_cpp_stack_and_column_are_preserved():
    report = triage_execution_result(
        1,
        "",
        "ERROR: AddressSanitizer: heap-buffer-overflow\n"
        "    #0 0xabcdef in Parser::read(char const*) /src/parser.cc:42:8\n",
    )
    frame = report.stack_trace[0]
    assert (frame.function, frame.file, frame.line) == (
        "Parser::read(char const*)",
        "/src/parser.cc",
        42,
    )


def test_relative_sanitizer_source_path():
    from diffsheriff.triage import parse_sanitizer_stack

    frame = parse_sanitizer_stack(" #0 0x1234 in parse source.c:10:5")[0]
    assert frame.file == "source.c" and frame.line == 10


def test_utf8_source_paths_preserve_raw_output_bytes():
    stderr = (
        (
            "ERROR: AddressSanitizer: heap-buffer-overflow\n"
            " #0 0x123 in parse /src/caf\u00e9.c:10:1"
        )
        .encode("utf-8")
        .decode("latin1")
    )
    report = triage_execution_result(1, "", stderr)
    assert report.stack_trace[0].file == "/src/caf\u00e9.c"
    assert report.raw_stderr == stderr


def test_unsymbolized_ubsan_report_keeps_location_and_records_the_gap():
    """The historical F09 failure: no symbolizer, so frames stayed raw."""
    stderr = recorded_ubsan_stderr(
        "    #0 0x4f2f1e  (/src/driver_sanitized+0x4f2f1e)\n"
        "    #1 0x4f3a2b  (/src/driver_sanitized+0x4f3a2b)\n"
    )
    report = triage_execution_result(1, "", stderr)
    assert report.is_crash is True
    assert report.error_type == "out-of-bounds"
    assert report.detection_mechanism == "UndefinedBehaviorSanitizer"
    # The reported source location survives; the function cannot be resolved.
    assert [(f.function, f.file, f.line) for f in report.stack_trace] == [
        ("unknown", "trees.c", 1092)
    ]
    # The degraded symbolization is retained instead of being silently lost.
    assert report.symbolizer_failed is True
    assert report.unsymbolized_frames == 2


def test_summary_function_resolves_when_frames_are_unsymbolized():
    """A summary line still names the function even if the stack cannot."""
    stderr = recorded_ubsan_stderr(
        "    #0 0x4f2f1e  (/src/driver_sanitized+0x4f2f1e)\n",
        summary="SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior "
        "trees.c:1092:20 in compress_block",
    )
    report = triage_execution_result(1, "", stderr)
    frame = report.stack_trace[0]
    assert (frame.function, frame.file, frame.line) == (
        "compress_block",
        "trees.c",
        1092,
    )
    assert report.symbolizer_failed is True
    assert report.unsymbolized_frames == 1


def test_symbolized_ubsan_stack_restores_the_designated_baseline_signature():
    """With a working symbolizer the recorded expectation is reproduced."""
    from diffsheriff.correlator import finding_signature

    stderr = recorded_ubsan_stderr(
        "    #0 0x55a1b2c3d4e5 in compress_block /src/trees.c:1092:20\n"
        "    #1 0x55a1b2c3e6f7 in _tr_flush_block /src/trees.c:1245:9\n"
        "    #2 0x55a1b2c3f809 in deflate /src/deflate.c:900:5\n",
        summary="SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior "
        "trees.c:1092:20 in compress_block",
        warning=False,
    )
    report = triage_execution_result(1, "", stderr)
    assert report.symbolizer_failed is False
    assert report.unsymbolized_frames == 0
    assert report.stack_trace[0].function == DIAGNOSIS["expected_function"]
    assert finding_signature(report, "base") == EXPECTED_BASELINE_SIGNATURE


@pytest.mark.parametrize(
    "frame,summary,expected",
    [
        (
            "    #0 0x55a1b2c3d4e5 in compress_block /src/trees.c:1092:20",
            "SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior "
            "trees.c:1092:20 in compress_block",
            ("compress_block", "/src/trees.c", 1092),
        ),
        (
            "    #0 0x55a1b2c3d4e5 in Parser::read(char const*) " "/src/parser.cc:42:8",
            "SUMMARY: UndefinedBehaviorSanitizer: undefined-behavior "
            "/src/parser.cc:42:8 in Parser::read",
            ("Parser::read(char const*)", "/src/parser.cc", 42),
        ),
        (
            "    #0 0x1234 in compress_block",
            "",
            ("compress_block", "trees.c", 1092),
        ),
        (
            "    #0 0x1234  (/src/driver_sanitized+0x1234)",
            "SUMMARY: AddressSanitizer: heap-buffer-overflow /src/trees.c:1092:20 "
            "in compress_block",
            ("compress_block", "/src/trees.c", 1092),
        ),
    ],
)
def test_frame_function_is_extracted_from_trailing_and_partial_formats(
    frame, summary, expected
):
    stderr = recorded_ubsan_stderr(frame + "\n", summary=summary)
    report = triage_execution_result(1, "", stderr)
    resolved = report.stack_trace[0]
    assert (resolved.function, resolved.file, resolved.line) == expected


def test_symbolizer_warning_alone_does_not_create_a_finding():
    report = triage_execution_result(0, "", DIAGNOSIS["sanitizer_warning"] + "\n")
    assert report.is_crash is False
    assert report.error_type == "none"
