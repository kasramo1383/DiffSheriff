"""
Unit tests for Delta Debugging (ddmin) minimization algorithm.
"""

import pytest

from diffsheriff.minimizer import (
    FailureInvariant,
    MinimizationLimits,
    ddmin,
    minimize,
)


def test_ddmin_basic_reduction():
    # Vulnerability invariant: payload contains "OVERFLOW"
    target_invariant = FailureInvariant(
        expected_error_type="buffer-overflow",
        expected_crash_function="vulnerable_func",
    )

    def mock_oracle(payload: bytes):
        if b"OVERFLOW" in payload:
            return True, "buffer-overflow", "vulnerable_func"
        return False, "none", "none"

    initial_input = b"HEADER_PADDING_1234567890_OVERFLOW_TRAILING_JUNK_DATA"
    minimized = ddmin(initial_input, mock_oracle, target_invariant)

    assert b"OVERFLOW" in minimized
    assert len(minimized) < len(initial_input)


def test_ddmin_handles_uneven_partitions_without_dropping_remainder():
    target_invariant = FailureInvariant(
        expected_error_type="marker",
        expected_crash_function="tail",
    )

    def mock_oracle(payload: bytes):
        return (b"X" in payload, "marker" if b"X" in payload else "none", "tail")

    assert ddmin(b"abcdX", mock_oracle, target_invariant) == b"X"


def test_empty_input_can_be_the_smallest_reproducer():
    invariant = FailureInvariant("error", "location")
    assert (
        ddmin(b"anything", lambda payload: (True, "error", "location"), invariant)
        == b""
    )


def test_rejects_a_nonreproducing_initial_input():
    import pytest

    with pytest.raises(ValueError, match="Initial payload"):
        ddmin(
            b"data",
            lambda payload: (False, "none", ""),
            FailureInvariant("error", "location"),
        )


def test_does_not_accept_same_error_at_another_location():
    invariant = FailureInvariant("error", "original")

    def oracle(payload):
        return True, "error", "original" if payload == b"AB" else "different"

    assert ddmin(b"AB", oracle, invariant) == b"AB"


@pytest.mark.parametrize("cap", [3, 16])
def test_explicit_granularity_limit_can_hide_removable_bytes(cap):
    initial = bytes(range(64))
    required = initial.replace(b"!", b"")

    def oracle(payload):
        return payload.replace(b"!", b"") == required, "error", "site"

    limited = minimize(
        initial,
        oracle,
        FailureInvariant("error", "site"),
        MinimizationLimits(cap, None),
    )
    assert limited.payload == initial
    assert limited.stop_reason == "granularity_limit"
    assert limited.as_evidence()["limit_reached"]
    expanded = minimize(
        initial,
        oracle,
        FailureInvariant("error", "site"),
        MinimizationLimits(None, 4096),
    )
    assert expanded.payload == required
    assert expanded.stop_reason == "search_exhausted"
    assert expanded.as_evidence()["reduced"]
    assert not expanded.as_evidence()["limit_reached"]


@pytest.mark.parametrize("budget", [1, 3, 5])
def test_oracle_budget_keeps_last_preserving_payload(budget):
    seen = []

    def oracle(payload):
        seen.append(payload)
        return b"X" in payload, "error", "site"

    result = minimize(
        b"abcXdef",
        oracle,
        FailureInvariant("error", "site"),
        MinimizationLimits(None, budget),
    )
    assert b"X" in result.payload
    assert result.payload in seen
    assert result.stop_reason == "oracle_call_limit"
    assert result.oracle_calls == len(seen) == budget
    assert result.as_evidence()["limit_reached"]


@pytest.mark.parametrize(
    "payload,oracle,reason,calls",
    [
        (b"", lambda p: (True, "error", "site"), "empty_reproducer", 1),
        (b"data", lambda p: (True, "error", "site"), "empty_reproducer", 2),
        (b"X", lambda p: (bool(p), "error", "site"), "single_byte_reproducer", 2),
        (b"data", lambda p: (False, "error", "site"), "initial_not_reproduced", 1),
    ],
)
def test_reduction_stop_reason_and_sizes(payload, oracle, reason, calls):
    result = minimize(payload, oracle, FailureInvariant("error", "site"))
    evidence = result.as_evidence()
    assert evidence["stop_reason"] == reason
    assert evidence["oracle_calls"] == calls
    assert evidence["original_size"] == len(payload)
    assert evidence["minimized_size"] == len(result.payload)
    assert evidence["reduced"] == (len(result.payload) < len(payload))
    assert not evidence["limit_reached"]


@pytest.mark.parametrize(
    "key,value",
    [
        ("max_granularity", True),
        ("max_granularity", 1),
        ("max_granularity", 2.5),
        ("max_oracle_calls", False),
        ("max_oracle_calls", 0),
        ("max_oracle_calls", "256"),
    ],
)
def test_invalid_reduction_limits_fail_before_oracle(key, value):
    with pytest.raises(ValueError, match=key):
        MinimizationLimits(**{key: value})


def test_finishing_on_last_allowed_call_is_not_a_limit_stop():
    result = minimize(
        b"abcXdef",
        lambda p: (b"X" in p, "error", "site"),
        FailureInvariant("error", "site"),
        MinimizationLimits(None, 7),
    )
    assert result.payload == b"X"
    assert result.oracle_calls == 7
    assert result.stop_reason == "single_byte_reproducer"
    assert not result.as_evidence()["limit_reached"]
