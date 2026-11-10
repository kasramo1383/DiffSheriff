"""Unit tests for sanitizer and signal classification."""

from diffsheriff.triage import triage_execution_result


def test_negative_subprocess_return_code_is_signal():
    report = triage_execution_result(-11, "", "")
    assert report.is_crash is True
    assert report.signal_name == "SIGSEGV"
    assert report.detection_mechanism == "OS Signal"


def test_shell_style_return_code_is_signal():
    report = triage_execution_result(134, "", "")
    assert report.is_crash is True
    assert report.signal_name == "SIGABRT"


def test_ubsan_runtime_error_is_classified_separately():
    report = triage_execution_result(
        1,
        "",
        "source.c:8:3: runtime error: division by zero",
    )
    assert report.is_crash is True
    assert report.error_type == "undefined-behavior"
    assert report.detection_mechanism == "UndefinedBehaviorSanitizer"


def test_asan_nonzero_exit_is_not_invented_as_a_signal():
    report = triage_execution_result(
        1,
        "",
        "ERROR: AddressSanitizer: heap-buffer-overflow",
    )
    assert report.is_crash is True
    assert report.signal_name is None
