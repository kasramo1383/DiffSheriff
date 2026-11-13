"""Runtime stack evidence against actual changed lines, on either diff side."""

from dataclasses import dataclass, field
import ast
import re
from typing import Optional
from diffsheriff.triage import StackFrame


@dataclass
class DiffHunk:
    file_path: str
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    function_header: Optional[str]
    old_file_path: Optional[str] = None
    old_lines: list[int] = field(default_factory=list)
    new_lines: list[int] = field(default_factory=list)


@dataclass
class CorrelationVerdict:
    is_correlated: bool
    correlation_type: str
    matched_file: Optional[str]
    matched_line: Optional[int]
    matched_frame: Optional[StackFrame]
    hunk: Optional[DiffHunk]
    reason: str


HUNK_HEADER_REGEX = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:\s+(.*))?"
)
FUNCTION_HEADER_REGEX = re.compile(
    r"^(?P<type>(?:[A-Za-z_]\w*[\s*&]+)+)(?P<name>[A-Za-z_]\w*)"
    r"\s*\([^(){};]*\)\s*\{?\s*$"
)


def source_path(path):
    path = path.replace("\\", "/")
    return path.removeprefix("/src/").removeprefix("./")


def _paths_match(frame_path, diff_path):
    frame_path = source_path(frame_path)
    return bool(diff_path) and (
        frame_path == diff_path
        or (
            (frame_path.startswith("/") or re.match(r"^[A-Za-z]:/", frame_path))
            and frame_path.endswith("/" + diff_path)
        )
    )


def _diff_path(value, strip_prefix=True):
    value = value.split("\t", 1)[0]
    if value.startswith('"'):
        value = ast.literal_eval(value)
        value = value.encode("latin1").decode("utf-8")
    if value == "/dev/null":
        return None
    return value[2:] if strip_prefix and value.startswith(("a/", "b/")) else value


def parse_unified_diff(diff_text):
    hunks = []
    old_file = new_file = None
    current = None
    old_line = new_line = 0
    old_remaining = new_remaining = 0
    for line in diff_text.splitlines():
        match = HUNK_HEADER_REGEX.match(line)
        if match:
            current = DiffHunk(
                new_file or old_file,
                int(match[1]),
                int(match[2] or 1),
                int(match[3]),
                int(match[4] or 1),
                match[5],
                old_file,
            )
            if not current.file_path:
                raise ValueError("Diff hunk has no file header")
            hunks.append(current)
            old_line, new_line = current.old_start, current.new_start
            old_remaining, new_remaining = current.old_length, current.new_length
        elif current and (old_remaining or new_remaining):
            if line.startswith("-"):
                current.old_lines.append(old_line)
                old_line += 1
                old_remaining -= 1
            elif line.startswith("+"):
                current.new_lines.append(new_line)
                new_line += 1
                new_remaining -= 1
            elif line.startswith(" "):
                old_line += 1
                new_line += 1
                old_remaining -= 1
                new_remaining -= 1
        elif line.startswith("diff --git "):
            current = None
            old_file = new_file = None
        elif line.startswith("--- "):
            old_file = _diff_path(line[4:])
        elif line.startswith("+++ "):
            new_file = _diff_path(line[4:])
        elif line.startswith("rename from "):
            old_file = _diff_path(line[12:], strip_prefix=False)
        elif line.startswith("rename to "):
            new_file = _diff_path(line[10:], strip_prefix=False)
            hunks.append(DiffHunk(new_file, 0, 0, 0, 0, None, old_file))
    return hunks


def correlate_stack_to_diff(frames, hunks, side="patch"):
    if side not in {"base", "patch"}:
        raise ValueError("side must be base or patch")
    for index, frame in enumerate(frames):
        for hunk in hunks:
            path = hunk.old_file_path if side == "base" else hunk.file_path
            lines = hunk.old_lines if side == "base" else hunk.new_lines
            if _paths_match(frame.file, path) and frame.line in lines:
                return CorrelationVerdict(
                    True,
                    "Direct Match" if index == 0 else "Indirect (Caller/Callee)",
                    path,
                    frame.line,
                    frame,
                    hunk,
                    "Runtime frame intersects an edited line; "
                    "comparative evidence is required for attribution.",
                )
    if side == "base":
        candidates = []
        for hunk in hunks:
            if (
                hunk.old_length
                or not hunk.new_lines
                or len(hunk.new_lines) != hunk.new_length
            ):
                continue
            declaration = FUNCTION_HEADER_REGEX.fullmatch(hunk.function_header or "")
            if not declaration or set(declaration["type"].split()) & {
                "return",
                "typedef",
                "throw",
                "goto",
            }:
                continue
            # Match an executed function, never just a nearby file/line or symbol.
            frame = next(
                (
                    f
                    for f in frames
                    if (
                        f.function == declaration["name"]
                        and _paths_match(f.file, hunk.old_file_path)
                        and f.line > hunk.old_start
                    )
                ),
                None,
            )
            if frame:
                candidates.append((frame, hunk))
        if len(candidates) == 1:
            frame, hunk = candidates[0]
            return CorrelationVerdict(
                True,
                "Insertion in observed function",
                hunk.old_file_path,
                frame.line,
                frame,
                hunk,
                "One insertion hunk belongs to a function observed on the baseline "
                "stack before its recorded execution location. This is function-level "
                "evidence, not proof that an inserted branch executed; repeated "
                "comparative results and independent expectations are required.",
            )
    return CorrelationVerdict(
        False,
        "Inconclusive",
        None,
        None,
        None,
        None,
        "No unambiguous edited-line or inserted-function runtime evidence; "
        "attribution is unsupported.",
    )


def finding_signature(report, side="base", hunks=()):
    """Keep exact source locations; map only unchanged patch lines across edits."""
    if report.detection_mechanism not in {
        "AddressSanitizer",
        "UndefinedBehaviorSanitizer",
    }:
        return None
    if report.error_type in {"undefined-behavior", "DEADLYSIGNAL", "SEGV"}:
        return None
    for frame in report.stack_trace:
        path = source_path(frame.file)
        if frame.line <= 0 or path == "unknown" or path.startswith("/"):
            continue
        line = frame.line
        if side == "patch":
            delta = 0
            old_path = path
            for hunk in hunks:
                if path != hunk.file_path:
                    continue
                if line in hunk.new_lines:
                    if hunk.old_length == hunk.new_length and hunk.old_length > 0:
                        return {
                            "error_type": report.error_type,
                            "file": hunk.old_file_path or path,
                            "function": frame.function,
                            "line": line - hunk.new_start + hunk.old_start,
                        }
                    # shortcut: changed locations cannot be mapped uniquely, retain
                    # their patch coordinate until richer execution evidence exists.
                    return {
                        "error_type": report.error_type,
                        "file": path,
                        "function": frame.function,
                        "line": line,
                        "side": "patch",
                    }
                if hunk.new_start + hunk.new_length <= line:
                    delta += hunk.new_length - hunk.old_length
                old_path = hunk.old_file_path or old_path
            line -= delta
            path = old_path
        return {
            "error_type": report.error_type,
            "file": path,
            "function": frame.function,
            "line": line,
        }
    return None
