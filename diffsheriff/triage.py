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


ASAN_ERROR_REGEX = re.compile(r"ERROR: (?:AddressSanitizer|UndefinedBehaviorSanitizer): ([\w\-]+)")
FRAME_REGEX = re.compile(
    r"#(\d+)\s+(0x[0-9a-fA-F]+)\s+(?:in\s+([^\s]+))?\s+(?:([^\s:]+):(\d+))?"
)


def triage_execution_result(exit_code: int, stdout: str, stderr: str) -> CrashReport:
    """
    Analyzes execution exit code and stderr to determine crash nature and extract stack traces.
    """
    combined_err = stderr + "\n" + stdout

    # 1. AddressSanitizer / UBSan detection
    asan_match = ASAN_ERROR_REGEX.search(combined_err)
    if asan_match:
        error_type = asan_match.group(1)
        frames = parse_sanitizer_stack(combined_err)
        return CrashReport(
            is_crash=True,
            error_type=error_type,
            detection_mechanism="AddressSanitizer",
            exit_code=exit_code,
            signal_name="SIGABRT" if exit_code != 0 else None,
            stack_trace=frames,
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 2. Stack smashing detected (__stack_chk_fail)
    if "stack smashing detected" in combined_err or "*** stack smashing detected ***" in combined_err:
        return CrashReport(
            is_crash=True,
            error_type="stack-canary-violation",
            detection_mechanism="Stack Canary",
            exit_code=exit_code,
            signal_name="SIGABRT",
            stack_trace=[],
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 3. Terminating Signal Traps (Linux exit code = 128 + signal)
    if exit_code > 128:
        sig_num = exit_code - 128
        signals_map = {
            11: "SIGSEGV",
            6: "SIGABRT",
            4: "SIGILL",
            8: "SIGFPE",
            7: "SIGBUS",
            9: "SIGKILL",
        }
        sig_name = signals_map.get(sig_num, f"SIGNAL_{sig_num}")
        return CrashReport(
            is_crash=True,
            error_type=sig_name,
            detection_mechanism="OS Signal",
            exit_code=exit_code,
            signal_name=sig_name,
            stack_trace=[],
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 4. Clean or unclassified termination
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
