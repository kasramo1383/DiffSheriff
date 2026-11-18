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
    # Retained so an unsymbolized run is explained instead of silently becoming
    # a finding with an "unknown" function. Both fields are additive evidence.
    symbolizer_failed: bool = False
    unsymbolized_frames: int = 0


ASAN_ERROR_REGEX = re.compile(r"ERROR: AddressSanitizer: ([\w\-]+)")
UBSAN_ERROR_REGEX = re.compile(r"runtime error:\s*([^\r\n]+)", re.IGNORECASE)
FRAME_REGEX = re.compile(
    r"#(\d+)\s+(0x[0-9a-fA-F]+)\s+(?:in\s+)?(.+?)\s+"
    r"((?:/|[A-Za-z]:|\.?\.?/)[^\r\n]*?|[^\s:]+):"
    r"(\d+)(?::\d+)?(?:\s|$)"
)
# Clang prints these when it cannot map addresses back to source locations.
UNSYMBOLIZED_FRAME_REGEX = re.compile(
    r"#(\d+)\s+(0x[0-9a-fA-F]+)\s+(?:in\s+\S+\s*)?\((.+)\)\s*$"
)
# A frame whose function was resolved but whose source location was not.
FUNCTION_ONLY_FRAME_REGEX = re.compile(r"#(\d+)\s+(0x[0-9a-fA-F]+)\s+in\s+(\S+)\s*$")
SUMMARY_REGEX = re.compile(
    r"^SUMMARY:\s*[A-Za-z]+Sanitizer:\s*\S+\s+"
    r"(?P<file>[^\s:]+):(?P<line>\d+)(?::(?P<column>\d+))?"
    r"(?:\s+in\s*(?P<function>\S*))?\s*$",
    re.MULTILINE,
)
RUNTIME_LOCATION_REGEX = re.compile(
    r"^(?P<file>[^\s:]+):(?P<line>\d+)(?::(?P<column>\d+))?:\s*runtime error:",
    re.MULTILINE,
)
SYMBOLIZER_FAILURE_MARKERS = (
    "invalid path to external symbolizer",
    "Failed to use and restart external symbolizer",
)
UNRESOLVED_FUNCTIONS = {"", "??", "<unknown>", "unknown"}

SIGNALS = {
    11: "SIGSEGV",
    6: "SIGABRT",
    4: "SIGILL",
    8: "SIGFPE",
    7: "SIGBUS",
    9: "SIGKILL",
}


def _signal_from_return_code(exit_code: int, shell_status=False) -> Optional[str]:
    if exit_code < 0:
        signal_number = -exit_code
    elif shell_status and exit_code >= 128:
        signal_number = exit_code - 128
    else:
        return None
    return SIGNALS.get(signal_number, f"SIGNAL_{signal_number}")


def symbolizer_failure(stderr: str) -> bool:
    """True when the sanitizer runtime reported that it could not symbolize."""
    return any(marker in stderr for marker in SYMBOLIZER_FAILURE_MARKERS)


def _reported_location(log: str):
    """The sanitizer's own reported source location, with its function if known.

    The summary line is preferred because it survives a stack whose individual
    frames could not be symbolized; the runtime-error line is the fallback.
    """
    location = None
    for match in SUMMARY_REGEX.finditer(log):
        location = (
            match["file"],
            int(match["line"]),
            (match["function"] or "").strip(),
        )
    if location is not None:
        return location
    match = RUNTIME_LOCATION_REGEX.search(log)
    if match:
        return (match["file"], int(match["line"]), "")
    return None


def _reported_function(log: str):
    """Any function name the sanitizer emitted, even without a usable frame."""
    for match in SUMMARY_REGEX.finditer(log):
        function = (match["function"] or "").strip()
        if function not in UNRESOLVED_FUNCTIONS:
            return function
    for line in log.splitlines():
        match = FUNCTION_ONLY_FRAME_REGEX.search(line)
        if match and match.group(3) not in UNRESOLVED_FUNCTIONS:
            return match.group(3)
    return None


def _source_frames(log: str) -> List[StackFrame]:
    """Source-level frames; synthesize the reported location when none resolve."""
    frames = parse_sanitizer_stack(log)
    if frames:
        return frames
    location = _reported_location(log)
    if location is None:
        # Keep a resolved function name even when no source line is available;
        # such a frame never becomes a source signature.
        function = _reported_function(log)
        return [StackFrame(0, "", function, "unknown", 0)] if function else []
    path, line, function = location
    if function in UNRESOLVED_FUNCTIONS:
        function = _reported_function(log) or "unknown"
    return [StackFrame(0, "", function, path, line)]


def triage_execution_result(
    exit_code: int,
    stdout: str,
    stderr: str,
    timed_out=False,
    resource_limited=False,
    output_limited=False,
    shell_status=False,
) -> CrashReport:
    """
    Classifies an execution result and extracts available stack frames.
    """
    if timed_out or resource_limited or output_limited:
        category = (
            "timeout"
            if timed_out
            else "resource-limit" if resource_limited else "output-limit"
        )
        return CrashReport(
            False, category, "Resource Limit", exit_code, None, [], stdout, stderr
        )
    combined_err = stderr
    try:
        combined_err = stderr.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # 1. AddressSanitizer detection
    asan_match = ASAN_ERROR_REGEX.search(combined_err)
    if asan_match:
        error_type = asan_match.group(1)
        frames = _source_frames(combined_err)
        return CrashReport(
            is_crash=True,
            error_type=error_type,
            detection_mechanism="AddressSanitizer",
            exit_code=exit_code,
            signal_name=_signal_from_return_code(exit_code, shell_status),
            stack_trace=frames,
            raw_stdout=stdout,
            raw_stderr=stderr,
            symbolizer_failed=symbolizer_failure(combined_err),
            unsymbolized_frames=count_unsymbolized_frames(combined_err),
        )

    # 2. UndefinedBehaviorSanitizer detection
    ubsan_match = UBSAN_ERROR_REGEX.search(combined_err)
    if ubsan_match:
        frames = _source_frames(combined_err)
        description = ubsan_match.group(1).lower()
        category = "undefined-behavior"
        for needle, label in (
            ("division by zero", "division-by-zero"),
            ("null pointer", "null-dereference"),
            ("out of bounds", "out-of-bounds"),
            ("misaligned address", "misaligned-access"),
            ("signed integer overflow", "signed-integer-overflow"),
        ):
            if needle in description:
                category = label
                break
        return CrashReport(
            is_crash=True,
            error_type=category,
            detection_mechanism="UndefinedBehaviorSanitizer",
            exit_code=exit_code,
            signal_name=_signal_from_return_code(exit_code, shell_status),
            stack_trace=frames,
            raw_stdout=stdout,
            raw_stderr=stderr,
            symbolizer_failed=symbolizer_failure(combined_err),
            unsymbolized_frames=count_unsymbolized_frames(combined_err),
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
            signal_name=_signal_from_return_code(exit_code, shell_status),
            stack_trace=[],
            raw_stdout=stdout,
            raw_stderr=stderr,
        )

    # 4. Terminating signals. subprocess uses negative signal numbers when it
    # executes the process directly; shells conventionally report 128 + signal.
    signal_name = _signal_from_return_code(exit_code, shell_status)
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
    """Frames that carry both a resolved function and a source location."""
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


def count_unsymbolized_frames(log: str) -> int:
    """Count frames printed as `module+offset` with no source information."""
    return sum(
        1
        for line in log.splitlines()
        if UNSYMBOLIZED_FRAME_REGEX.search(line) and " in " not in line
    )
