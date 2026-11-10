"""
Unit tests for Delta Debugging (ddmin) minimization algorithm.
"""

from diffsheriff.minimizer import FailureInvariant, ddmin


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
