"""
Delta Debugging (ddmin) testcase minimizer.
Reduces failure-inducing payloads while preserving the exact failure invariant.
"""

from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass
class FailureInvariant:
    expected_error_type: str
    expected_crash_function: str


def ddmin(
    initial_payload: bytes,
    oracle: Callable[[bytes], Tuple[bool, str, str]],
    invariant: FailureInvariant,
) -> bytes:
    """
    Minimizes initial_payload using the classical Delta Debugging algorithm.
    oracle(payload) -> (crashed: bool, error_type: str, crash_function: str)
    """

    def preserves_invariant(candidate: bytes) -> bool:
        if not candidate:
            return False
        crashed, error_type, func_name = oracle(candidate)
        return (
            crashed
            and error_type == invariant.expected_error_type
            and (not invariant.expected_crash_function or func_name == invariant.expected_crash_function)
        )

    payload = initial_payload
    n = 2

    while len(payload) >= 2:
        chunk_size = len(payload) // n
        if chunk_size == 0:
            break

        chunks = [payload[i * chunk_size : (i + 1) * chunk_size] for i in range(n)]
        complements = [
            payload[: i * chunk_size] + payload[(i + 1) * chunk_size :] for i in range(n)
        ]

        reduced = False

        # Try individual chunks
        for chunk in chunks:
            if preserves_invariant(chunk):
                payload = chunk
                n = 2
                reduced = True
                break

        if reduced:
            continue

        # Try complements (removing one chunk at a time)
        for comp in complements:
            if preserves_invariant(comp):
                payload = comp
                n = max(n - 1, 2)
                reduced = True
                break

        if reduced:
            continue

        if n >= len(payload):
            break
        n = min(n * 2, len(payload))

    return payload
