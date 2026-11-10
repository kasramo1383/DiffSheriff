"""
Finding-to-diff correlator.
Maps runtime stack traces to unified git diff hunks and classifies finding statuses.
"""

from dataclasses import dataclass
import re
from typing import List, Optional
from diffsheriff.triage import StackFrame


@dataclass
class DiffHunk:
    file_path: str
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    function_header: Optional[str]


@dataclass
class CorrelationVerdict:
    is_correlated: bool
    correlation_type: str  # "Direct Match", "Indirect (Caller/Callee)", "Inconclusive"
    matched_file: Optional[str]
    matched_line: Optional[int]
    matched_frame: Optional[StackFrame]
    hunk: Optional[DiffHunk]
    reason: str


HUNK_HEADER_REGEX = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:\s+(.*))?"
)


def _paths_match(frame_path: str, diff_path: str) -> bool:
    normalized_frame = frame_path.replace("\\", "/")
    normalized_diff = diff_path.replace("\\", "/")
    return normalized_frame == normalized_diff or normalized_frame.endswith(
        f"/{normalized_diff}"
    )


def _line_in_new_hunk(line: int, hunk: DiffHunk) -> bool:
    return (
        hunk.new_length > 0
        and hunk.new_start <= line < hunk.new_start + hunk.new_length
    )


def parse_unified_diff(diff_text: str) -> List[DiffHunk]:
    """
    Parses a unified git diff into individual DiffHunk records.
    """
    hunks: List[DiffHunk] = []
    current_file: Optional[str] = None

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            continue

        match = HUNK_HEADER_REGEX.match(line)
        if match and current_file:
            old_start = int(match.group(1))
            old_len = int(match.group(2)) if match.group(2) else 1
            new_start = int(match.group(3))
            new_len = int(match.group(4)) if match.group(4) else 1
            func_hdr = match.group(5).strip() if match.group(5) else None

            hunks.append(
                DiffHunk(
                    file_path=current_file,
                    old_start=old_start,
                    old_length=old_len,
                    new_start=new_start,
                    new_length=new_len,
                    function_header=func_hdr,
                )
            )

    return hunks


def correlate_stack_to_diff(
    frames: List[StackFrame], hunks: List[DiffHunk]
) -> CorrelationVerdict:
    """
    Correlates stack trace frames against diff hunks.
    Checks frame 0 directly, then caller-callee propagation in outer frames.
    """
    if not frames:
        return CorrelationVerdict(
            is_correlated=False,
            correlation_type="Inconclusive",
            matched_file=None,
            matched_line=None,
            matched_frame=None,
            hunk=None,
            reason="No stack frames available to correlate.",
        )

    # 1. Direct match on innermost crash site (frame 0)
    crash_frame = frames[0]
    for hunk in hunks:
        if _paths_match(crash_frame.file, hunk.file_path):
            if _line_in_new_hunk(crash_frame.line, hunk):
                return CorrelationVerdict(
                    is_correlated=True,
                    correlation_type="Direct Match",
                    matched_file=hunk.file_path,
                    matched_line=crash_frame.line,
                    matched_frame=crash_frame,
                    hunk=hunk,
                    reason=(
                        f"Crash occurred directly on line {crash_frame.line} "
                        "in modified hunk."
                    ),
                )

    # 2. Indirect match: Caller-callee propagation in outer stack frames
    for frame in frames[1:]:
        for hunk in hunks:
            if _paths_match(frame.file, hunk.file_path):
                if _line_in_new_hunk(frame.line, hunk):
                    return CorrelationVerdict(
                        is_correlated=True,
                        correlation_type="Indirect (Caller/Callee)",
                        matched_file=hunk.file_path,
                        matched_line=frame.line,
                        matched_frame=frame,
                        hunk=hunk,
                        reason=(
                            f"Crash in {crash_frame.function} was invoked by "
                            "modified caller "
                            f"{frame.function} at {frame.file}:{frame.line}."
                        ),
                    )

    # 3. No match found
    return CorrelationVerdict(
        is_correlated=False,
        correlation_type="Inconclusive",
        matched_file=None,
        matched_line=None,
        matched_frame=None,
        hunk=None,
        reason=(
            "Stack trace frames do not intersect with lines modified in the "
            "git diff."
        ),
    )
