"""Bounded delta debugging that retains the reduction outcome and its limits."""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple


@dataclass
class FailureInvariant:
    expected_error_type: str
    expected_crash_function: str


@dataclass
class MinimizationLimits:
    max_granularity: Optional[int] = 16
    max_oracle_calls: Optional[int] = 256

    def __post_init__(self):
        for name, minimum in (("max_granularity", 2), ("max_oracle_calls", 1)):
            value = getattr(self, name)
            if value is not None and (type(value) is not int or value < minimum):
                raise ValueError(f"{name} must be null or an integer >= {minimum}")


@dataclass
class MinimizationResult:
    payload: bytes
    original_size: int
    stop_reason: str
    oracle_calls: int
    limits: MinimizationLimits

    def as_evidence(self):
        return {
            "original_size": self.original_size,
            "minimized_size": len(self.payload),
            "reduced": len(self.payload) < self.original_size,
            "stop_reason": self.stop_reason,
            "oracle_calls": self.oracle_calls,
            "max_granularity": self.limits.max_granularity,
            "max_oracle_calls": self.limits.max_oracle_calls,
            "limit_reached": self.stop_reason
            in {"granularity_limit", "oracle_call_limit"},
        }


class _OracleCallLimit(Exception):
    pass


def minimize(
    initial_payload: bytes,
    oracle: Callable[[bytes], Tuple[bool, str, str]],
    invariant: FailureInvariant,
    limits: Optional[MinimizationLimits] = None,
) -> MinimizationResult:
    """Return the last preserving payload and why the search stopped.

    Oracle calls count candidate evaluations, not child-process executions. Exhausting
    this search does not establish a global minimum or independent input validity.
    """
    limits = limits or MinimizationLimits()
    payload = initial_payload
    calls = 0

    def result(reason):
        return MinimizationResult(payload, len(initial_payload), reason, calls, limits)

    def preserves_invariant(candidate):
        nonlocal calls
        if limits.max_oracle_calls is not None and calls >= limits.max_oracle_calls:
            raise _OracleCallLimit
        calls += 1
        crashed, error_type, func_name = oracle(candidate)
        return (
            crashed
            and error_type == invariant.expected_error_type
            and (
                not invariant.expected_crash_function
                or func_name == invariant.expected_crash_function
            )
        )

    try:
        if not preserves_invariant(payload):
            return result("initial_not_reproduced")
        if not payload:
            return result("empty_reproducer")
        if preserves_invariant(b""):
            payload = b""
            return result("empty_reproducer")
        n = 2
        while len(payload) >= 2:
            chunk_size, remainder = divmod(len(payload), n)
            chunks = []
            start = 0
            for index in range(n):
                end = start + chunk_size + (1 if index < remainder else 0)
                chunks.append((start, end, payload[start:end]))
                start = end

            reduced = False
            for _, _, chunk in chunks:
                if preserves_invariant(chunk):
                    payload = chunk
                    n = 2
                    reduced = True
                    break
            if reduced:
                continue

            for start, end, _ in chunks:
                comp = payload[:start] + payload[end:]
                if preserves_invariant(comp):
                    payload = comp
                    n = max(n - 1, 2)
                    reduced = True
                    break
            if reduced:
                continue

            if n >= len(payload):
                return result("search_exhausted")
            if limits.max_granularity is not None and n >= limits.max_granularity:
                return result("granularity_limit")
            n = min(n * 2, len(payload))
            if limits.max_granularity is not None:
                n = min(n, limits.max_granularity)
        return result("single_byte_reproducer")
    except _OracleCallLimit:
        return result("oracle_call_limit")


def ddmin(
    initial_payload: bytes,
    oracle: Callable[[bytes], Tuple[bool, str, str]],
    invariant: FailureInvariant,
    max_granularity: Optional[int] = 16,
) -> bytes:
    """Compatibility interface returning bytes; use minimize for retained evidence."""
    result = minimize(
        initial_payload, oracle, invariant, MinimizationLimits(max_granularity, None)
    )
    if result.stop_reason == "initial_not_reproduced":
        raise ValueError("Initial payload does not preserve the failure invariant")
    return result.payload
