#!/usr/bin/env python3
"""Verify one retained comparison: exit code, report contract, reproducer bundles.

The matrix runner calls this after every comparison. It asserts only what the
delivery requires: the process exit code, the retained report's own exit code,
an established baseline identity, and replayable reproducer bundles with both
inputs and at least three baseline replays.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

MINIMUM_REPLAYS = 3


def _reproducer_problems(bundle):
    problems = []
    metadata = bundle / "reproducer.json"
    if not metadata.is_file():
        return [f"{bundle.name}: missing reproducer.json"]
    try:
        item = json.loads(metadata.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"{bundle.name}: unreadable reproducer.json: {error}"]
    if item.get("kind") not in {"security", "functional"}:
        problems.append(f"{bundle.name}: unknown reproducer kind")
    if item.get("finding_side") not in {"base", "patch"}:
        problems.append(f"{bundle.name}: unknown finding side")
    if len(item.get("runs", {}).get("base", [])) < MINIMUM_REPLAYS:
        problems.append(f"{bundle.name}: fewer than three baseline replays")
    for name in ("original.input", "minimized.input"):
        if not (bundle / name).is_file():
            problems.append(f"{bundle.name}: missing {name}")
    minimized = bundle / "minimized.input"
    if minimized.is_file() and hashlib.sha256(minimized.read_bytes()).hexdigest() != (
        item.get("minimized_sha256")
    ):
        problems.append(f"{bundle.name}: minimized input hash mismatch")
    return problems


def verify(out, target, variant, actual, expected):
    """Return the list of contradictions between the run and its expectations."""
    root = Path(out)
    problems = []
    report_path = root / "report.json"
    report = None
    if not report_path.is_file():
        problems.append("no retained report.json")
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            problems.append(f"unreadable report.json: {error}")
    if report is not None:
        if report.get("schema_version") != "2.0":
            problems.append("report schema_version is not 2.0")
        if report.get("exit_code") != int(actual):
            problems.append("report exit_code differs from the process exit code")
        if report.get("exit_code") != int(expected):
            problems.append("report exit_code differs from the justified outcome")
        if not report.get("evidence", {}).get("baseline_identity_modes"):
            problems.append("baseline flaw was not established in any build mode")
    run_root = root / "runs"
    bundles = sorted(run_root.glob("run-*/reproducers/*")) if run_root.is_dir() else []
    if not bundles:
        problems.append("no retained reproducer bundle")
    for bundle in bundles:
        problems.extend(_reproducer_problems(bundle))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="artifacts/<target>/<variant>")
    parser.add_argument("--target", required=True)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--actual", type=int, required=True)
    parser.add_argument("--expected", type=int, required=True)
    args = parser.parse_args()
    problems = verify(
        args.output, args.target, args.variant, args.actual, args.expected
    )
    for problem in problems:
        print(f"FAIL {args.target}/{args.variant}: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"OK {args.target}/{args.variant}: exit {args.actual}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
