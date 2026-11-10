"""
Unit tests for DiffSheriff reporter and exit code priority logic.
"""

from diffsheriff.reporter import (
    EXIT_BUILD_OR_CONFIG_ERROR,
    EXIT_FUNC_REGRESSION,
    EXIT_INCONCLUSIVE,
    EXIT_PASS,
    EXIT_VULN_REMAINS_OR_NEW,
    resolve_priority_exit_code,
)


def test_exit_code_pass():
    code, verdict = resolve_priority_exit_code(False, False, False, False)
    assert code == EXIT_PASS
    assert verdict == "PASS"


def test_exit_code_vuln_over_regression():
    # Priority: 10 > 20
    code, verdict = resolve_priority_exit_code(
        build_failed=False,
        vuln_detected=True,
        regression_detected=True,
        is_inconclusive=False,
    )
    assert code == EXIT_VULN_REMAINS_OR_NEW


def test_exit_code_build_error_over_all():
    # Priority: 30 > 10 > 20
    code, verdict = resolve_priority_exit_code(
        build_failed=True,
        vuln_detected=True,
        regression_detected=True,
        is_inconclusive=False,
    )
    assert code == EXIT_BUILD_OR_CONFIG_ERROR


def test_exit_code_regression():
    code, verdict = resolve_priority_exit_code(
        build_failed=False,
        vuln_detected=False,
        regression_detected=True,
        is_inconclusive=False,
    )
    assert code == EXIT_FUNC_REGRESSION


def test_exit_code_inconclusive():
    code, verdict = resolve_priority_exit_code(
        build_failed=False,
        vuln_detected=False,
        regression_detected=False,
        is_inconclusive=True,
    )
    assert code == EXIT_INCONCLUSIVE
