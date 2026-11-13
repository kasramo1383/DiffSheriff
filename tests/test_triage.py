"""Unit tests for sanitizer and signal classification."""

import pytest

from diffsheriff.triage import triage_execution_result


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
