"""
Crash triage and sanitizer parser.
Extracts error types, terminating signals, and stack frames from execution outputs.
"""

from dataclasses import dataclass
import re
from typing import List, Optional


@dataclass
class StackFrame:
    index: int
    address: str
    function: str
    file: str
    line: int


@dataclass
class CrashReport:
    is_crash: bool
    error_type: str  # e.g. "stack-buffer-overflow", "heap-buffer-overflow", "SIGSEGV"
    detection_mechanism: str  # e.g. "AddressSanitizer", "Signal", "Stack Canary"
    exit_code: int
    signal_name: Optional[str]
    stack_trace: List[StackFrame]
    raw_stdout: str
    raw_stderr: str


ASAN_ERROR_REGEX = re.compile(r"ERROR: AddressSanitizer: ([\w\-]+)")
UBSAN_ERROR_REGEX = re.compile(r"runtime error:\s*([^\r\n]+)", re.IGNORECASE)
FRAME_REGEX = re.compile(
    r"#(\d+)\s+(0x[0-9a-fA-F]+)\s+(?:in\s+([^\s]+))?\s+(?:([^\s:]+):(\d+))?"
)

SIGNALS = {
    11: "SIGSEGV",
    6: "SIGABRT",
    4: "SIGILL",
    8: "SIGFPE",
    7: "SIGBUS",
    9: "SIGKILL",
}


def _signal_from_return_code(exit_code: int) -> Optional[str]:
    if exit_code < 0:
        signal_number = -exit_code
    elif exit_code >= 128:
        signal_number = exit_code - 128
    else:
        return None
    return SIGNALS.get(signal_number, f"SIGNAL_{signal_number}")


def triage_execution_result(exit_code: int, stdout: str, stderr: str) -> CrashReport:
    """
    Classifies an execution result and extracts available stack frames.
    """
    combined_err = stderr + "\n" + stdout

    # 1. AddressSanitizer detection
    asan_match = ASAN_ERROR_REGEX.search(combined_err)
    if asan_match:
        error_type = asan_match.group(1)
        frames = parse_sanitizer_stack(combined_err)
        return CrashReport(
            is_crash=True,
            error_type=error_type,
            detection_mechanism="AddressSanitizer",
            exit_code=exit_code,
            signal_name=_signal_from_return_code(exit_code),
            stack_trace=frames,
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 2. UndefinedBehaviorSanitizer detection
    ubsan_match = UBSAN_ERROR_REGEX.search(combined_err)
    if ubsan_match:
        frames = parse_sanitizer_stack(combined_err)
        return CrashReport(
            is_crash=True,
            error_type="undefined-behavior",
            detection_mechanism="UndefinedBehaviorSanitizer",
            exit_code=exit_code,
            signal_name=None,
            stack_trace=frames,
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 3. Stack smashing detected (__stack_chk_fail)
    if (
        "stack smashing detected" in combined_err
        or "*** stack smashing detected ***" in combined_err
    ):
        return CrashReport(
            is_crash=True,
            error_type="stack-canary-violation",
            detection_mechanism="Stack Canary",
            exit_code=exit_code,
            signal_name=_signal_from_return_code(exit_code),
            stack_trace=[],
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 4. Terminating signals. subprocess uses negative signal numbers when it
    # executes the process directly; shells conventionally report 128 + signal.
    signal_name = _signal_from_return_code(exit_code)
    if signal_name:
        return CrashReport(
            is_crash=True,
            error_type=signal_name,
            detection_mechanism="OS Signal",
            exit_code=exit_code,
            signal_name=signal_name,
            stack_trace=[],
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 5. Clean or unclassified termination
    return CrashReport(
        is_crash=False,
        error_type="none",
        detection_mechanism="none",
        exit_code=exit_code,
        signal_name=None,
        stack_trace=[],
        raw_stdout=stdout,
        raw_stderr=stderr,
    )


def parse_sanitizer_stack(log: str) -> List[StackFrame]:
    frames: List[StackFrame] = []
    for line in log.splitlines():
        match = FRAME_REGEX.search(line)
        if match:
            idx = int(match.group(1))
            addr = match.group(2)
            func = match.group(3) or "unknown"
            filepath = match.group(4) or "unknown"
            lineno = int(match.group(5)) if match.group(5) else 0
            frames.append(
                StackFrame(
                    index=idx,
                    address=addr,
                    function=func,
                    file=filepath,
                    line=lineno,
                )
            )
    return frames
