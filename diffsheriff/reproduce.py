"""Replay retained evidence, optionally checking baseline-fail/patch-pass."""

import argparse
import json
from pathlib import Path

from diffsheriff.builder import compute_sha256
from diffsheriff.config import TargetExecutionSection
from diffsheriff.correlator import parse_unified_diff
from diffsheriff.pipeline import (
    contained_file,
    expected_result,
    functional_failure,
    matches_expected,
    observe,
    stable_observations,
)


def replay(bundle, check_regression=False):
    bundle = Path(bundle)
    if bundle.is_symlink() or (bundle / "replay.json").is_symlink():
        raise ValueError("Replay bundle and output cannot be symlinks")
    metadata = json.loads(
        contained_file(bundle, "reproducer.json").read_text(encoding="utf-8")
    )
    if metadata["kind"] not in {"security", "functional"}:
        raise ValueError("Unknown reproducer kind")
    if metadata["kind"] == "security" and (
        not isinstance(metadata["signature"], dict) or not metadata["signature"]
    ):
        raise ValueError("Security reproducer needs a nonempty finding signature")
    if metadata["expected"] is not None or metadata["kind"] == "functional":
        expected_result(metadata["expected"])
    if set(metadata["artifacts"]) != {"base", "patch"} or metadata[
        "finding_side"
    ] not in {"base", "patch"}:
        raise ValueError(
            "Reproducer needs baseline and patch artifacts and a valid finding side"
        )
    root = bundle.resolve().parents[1]
    payload_path = contained_file(bundle, "minimized.input")
    if compute_sha256(payload_path) != metadata["minimized_sha256"]:
        raise ValueError("Reproducer input hash mismatch")
    settings = TargetExecutionSection(**metadata["settings"])
    hunks = parse_unified_diff(
        contained_file(root, "patch.diff").read_text(encoding="utf-8")
    )
    runs = {}
    for side, item in metadata["artifacts"].items():
        binary = contained_file(root, item["source"] + "/" + item["binary"])
        if compute_sha256(binary) != item["sha256"]:
            raise ValueError(f"{side} binary hash mismatch")
        runs[side] = [
            observe(
                root / item["source"],
                item["binary"],
                payload_path.read_bytes(),
                settings,
                side,
                hunks,
            )
            for _ in range(3)
        ]
    side = metadata["finding_side"]
    reproduced = (
        functional_failure(runs, metadata["expected"], metadata["functional_mismatch"])
        if metadata.get("kind") == "functional"
        else all(item["signature"] == metadata["signature"] for item in runs[side])
    )
    stable = all(stable_observations(items) for items in runs.values())
    regression_pass = (
        metadata["finding_side"] == "base"
        and reproduced
        and stable
        and metadata["expected"] is not None
        and all(matches_expected(item, metadata["expected"]) for item in runs["patch"])
    )
    result = {
        "reproduced": reproduced,
        "stable": stable,
        "regression_pass": regression_pass,
        "functional_expectation_available": metadata["expected"] is not None,
        "runs": runs,
    }
    (bundle / "replay.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return regression_pass if check_regression else reproduced and stable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--check-regression", action="store_true")
    args = parser.parse_args()
    try:
        success = replay(args.bundle, args.check_regression)
    except Exception as error:
        parser.exit(30, f"Replay error: {error}\n")
    parser.exit(0 if success else 40)


if __name__ == "__main__":
    main()
