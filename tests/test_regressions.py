import hashlib
import json
from pathlib import Path
import sys

import pytest
from click.testing import CliRunner

from diffsheriff.cli import main
from diffsheriff.config import ConfigError
from diffsheriff.regressions import copy_regressions
from diffsheriff.pipeline import run_pipeline
from .test_pipeline import pipeline_fixture as _shared_pipeline_fixture  # noqa: F401


@pytest.fixture
def pipeline_fixture(_shared_pipeline_fixture):  # noqa: F811 (pytest fixture)
    """Reuse the synthetic pipeline fixture from the end-to-end test module."""
    return _shared_pipeline_fixture


def retained_suite(path):
    path.mkdir()
    (path / "case.input").write_bytes(b"harmless")
    item = {
        "base_ref": "a" * 40,
        "input": "case.input",
        "sha256": hashlib.sha256(b"harmless").hexdigest(),
        "mode": "sanitized",
        "signature": {
            "error_type": "heap-buffer-overflow",
            "file": "sample.c",
            "function": "parse",
            "line": 8,
        },
        "finding_signature": {
            "error_type": "heap-buffer-overflow",
            "file": "sample.c",
            "function": "parse",
            "line": 8,
        },
        "finding_side": "base",
        "kind": "security",
        "check": "diagnostic",
        "valid_input": False,
        "expected": None,
    }
    (path / "case.json").write_text(json.dumps(item))
    return item


def test_copy_filters_baseline_and_preserves_files(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    retained_suite(source)
    copy_regressions(source, destination, "b" * 40)
    assert not list(destination.iterdir())
    copy_regressions(source, destination, "a" * 40)
    for path in source.iterdir():
        assert (destination / path.name).read_bytes() == path.read_bytes()
    copy_regressions(source, destination, "a" * 40)


@pytest.mark.parametrize("problem", ["hash", "traversal", "conflict"])
def test_copy_rejects_corruption_without_partial_writes(tmp_path, problem):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    destination.mkdir()
    if problem == "hash":
        item["sha256"] = "0" * 64
    elif problem == "traversal":
        item["input"] = "../elsewhere.input"
    else:
        (destination / "case.json").write_bytes(b"local expectation")
    (source / "case.json").write_text(json.dumps(item))
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)
    assert not (destination / "case.input").exists()
    if problem == "conflict":
        assert (destination / "case.json").read_bytes() == b"local expectation"


def test_export_can_refresh_owned_snapshot(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    copy_regressions(source, destination, "a" * 40)
    item["expected"] = {"exit_code": 0, "stdout": "", "stderr": ""}
    item["check"] = "full"
    (source / "case.json").write_text(json.dumps(item))
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert (source / "case.json").read_bytes() == (
        destination / "case.json"
    ).read_bytes()


def reviewed_case(source, destination):
    item = retained_suite(source)
    copy_regressions(source, destination, "a" * 40)
    local = {
        **item,
        "expected": {"exit_code": 0, "stdout": "ok", "stderr": ""},
        "check": "full",
        "valid_input": True,
    }
    (destination / "case.json").write_text(json.dumps(local, indent=4) + "\n")
    return item, local


def test_stale_diagnostic_preserves_reviewed_local_bytes(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    reviewed_case(source, destination)
    before = {p.name: p.read_bytes() for p in destination.iterdir()}
    for _ in range(2):
        copy_regressions(source, destination, "a" * 40)
        assert {p.name: p.read_bytes() for p in destination.iterdir()} == before


def test_cache_only_expectation_cannot_create_ground_truth(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    item.update(
        expected={"exit_code": 0, "stdout": "cache says so", "stderr": ""}, check="full"
    )
    (source / "case.json").write_text(json.dumps(item))
    with pytest.raises(ConfigError, match="independent local expectation"):
        copy_regressions(source, destination, "a" * 40)
    assert not destination.exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("base_ref", "b" * 40),
        ("mode", "release"),
        ("finding_side", "patch"),
        ("signature", None),
        ("finding_signature", {"error_type": "other"}),
        ("kind", "functional"),
        ("input", "other.input"),
        ("future_replay_setting", "changed"),
    ],
)
def test_reconciliation_rejects_identity_conflicts(tmp_path, field, value):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item, _ = reviewed_case(source, destination)
    before = {p.name: p.read_bytes() for p in destination.iterdir()}
    item[field] = value
    if field == "input":
        (source / value).write_bytes(b"harmless")
    (source / "case.json").write_text(json.dumps(item))
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)
    assert {p.name: p.read_bytes() for p in destination.iterdir()} == before


@pytest.mark.parametrize(
    "problem", ["expected", "validity", "payload", "local-hash", "promotion"]
)
def test_reconciliation_rejects_semantic_conflicts(tmp_path, problem):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item, local = reviewed_case(source, destination)
    if problem == "expected":
        item.update(
            check="full", expected={"exit_code": 0, "stdout": "different", "stderr": ""}
        )
    elif problem == "validity":
        item.update(check="full", expected=local["expected"])
    elif problem == "payload":
        (source / "case.input").write_bytes(b"different")
        item["sha256"] = hashlib.sha256(b"different").hexdigest()
    elif problem == "local-hash":
        (destination / "case.input").write_bytes(b"corrupt")
    else:
        (destination / "case.json").write_text(json.dumps(item))
        item = local
    (source / "case.json").write_text(json.dumps(item))
    before = {p.name: p.read_bytes() for p in destination.iterdir()}
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)
    assert {p.name: p.read_bytes() for p in destination.iterdir()} == before


def test_equal_metadata_preserves_local_formatting(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    _, local = reviewed_case(source, destination)
    (source / "case.json").write_text(json.dumps(local))
    before = (destination / "case.json").read_bytes()
    copy_regressions(source, destination, "a" * 40)
    assert (destination / "case.json").read_bytes() == before


@pytest.mark.parametrize("mismatch", [None, "payload", "expected", "valid_input"])
def test_new_full_cache_requires_independent_matching_bytes_and_behavior(
    tmp_path, mismatch
):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    item.update(check="full", expected={"exit_code": 0, "stdout": "ok", "stderr": ""})
    (source / "case.json").write_text(json.dumps(item))
    case = {"payload": b"harmless", "expected": item["expected"], "valid_input": False}
    if mismatch:
        case[mismatch] = {"payload": b"other", "expected": None, "valid_input": True}[
            mismatch
        ]
        with pytest.raises(ConfigError, match="independent local expectation"):
            copy_regressions(source, destination, "a" * 40, local_cases=[case])
        assert not destination.exists()
    else:
        copy_regressions(source, destination, "a" * 40, local_cases=[case])
        assert (destination / "case.json").read_bytes() == (
            source / "case.json"
        ).read_bytes()


@pytest.mark.parametrize("location", ["source", "destination"])
@pytest.mark.parametrize("entry", ["root", "case.json", "case.input"])
def test_transfer_rejects_symlinks(tmp_path, location, entry):
    source, destination = tmp_path / "source", tmp_path / "destination"
    reviewed_case(source, destination)
    root = source if location == "source" else destination
    target = root if entry == "root" else root / entry
    moved = tmp_path / "moved"
    target.rename(moved)
    try:
        target.symlink_to(moved, target_is_directory=entry == "root")
    except OSError:
        pytest.skip("Host does not allow test symlinks")
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)


@pytest.mark.parametrize(
    "field,value",
    [
        ("valid_input", 0),
        ("mode", []),
        ("check", "full"),
        ("signature", {"line": True}),
    ],
)
def test_transfer_rejects_invalid_metadata(tmp_path, field, value):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    item[field] = value
    (source / "case.json").write_text(json.dumps(item))
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)
    assert not destination.exists()


def test_later_conflict_does_not_partially_import(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    (source / "z.json").write_text(json.dumps({**item, "sha256": "0" * 64}))
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40)
    assert not destination.exists()


def test_patch_coordinate_signature_is_supported(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    item = retained_suite(source)
    item["finding_signature"]["side"] = "patch"
    item["finding_side"] = "patch"
    (source / "case.json").write_text(json.dumps(item))
    copy_regressions(source, destination, "a" * 40)
    assert (destination / "case.json").exists()


def functional_export(path, cases, exist_ok=False):
    """Write full-check functional manifests mapping manifest name to input name."""
    path.mkdir(exist_ok=exist_ok)
    for manifest_name, input_name in cases.items():
        payload = f"harmless {input_name}".encode()
        (path / input_name).write_bytes(payload)
        item = {
            "base_ref": "a" * 40,
            "input": input_name,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "mode": "sanitized",
            "signature": {
                "error_type": "functional-mismatch",
                "file": "sample.c",
                "function": "parse",
                "line": 8,
            },
            "finding_signature": None,
            "finding_side": "patch",
            "kind": "functional",
            "check": "full",
            "valid_input": True,
            "expected": {"exit_code": 0, "stdout": "ok", "stderr": ""},
        }
        (path / manifest_name).write_text(json.dumps(item))


def destination_bytes(destination):
    return {path.name: path.read_bytes() for path in destination.iterdir()}


def test_export_refresh_drops_case_missing_from_source(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(
        source, {"kept.json": "kept.input", "retired.json": "retired.input"}
    )
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    (destination / "notes.txt").write_bytes(b"unrelated local notes")
    (source / "retired.json").unlink()
    (source / "retired.input").unlink()
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert sorted(path.name for path in destination.iterdir()) == [
        "kept.input",
        "kept.json",
        "notes.txt",
    ]
    assert (destination / "kept.json").read_bytes() == (
        source / "kept.json"
    ).read_bytes()
    assert (destination / "notes.txt").read_bytes() == b"unrelated local notes"


def test_refresh_keeps_payload_referenced_by_retained_manifest(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(
        source, {"kept.json": "shared.input", "retired.json": "shared.input"}
    )
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    (source / "retired.json").unlink()
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert sorted(path.name for path in destination.iterdir()) == [
        "kept.json",
        "shared.input",
    ]
    assert (destination / "shared.input").read_bytes() == b"harmless shared.input"


def test_invalid_refresh_leaves_prior_snapshot_intact(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(
        source, {"kept.json": "kept.input", "retired.json": "retired.input"}
    )
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    before = destination_bytes(destination)
    (source / "kept.input").write_bytes(b"tampered without a new hash")
    (source / "retired.json").unlink()
    (source / "retired.input").unlink()
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == before


def test_refresh_fails_closed_on_unowned_destination_manifest(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(source, {"kept.json": "kept.input"})
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    (destination / "unknown.json").write_bytes(b"not a retained regression")
    before = destination_bytes(destination)
    (source / "kept.json").unlink()
    (source / "kept.input").unlink()
    with pytest.raises(ConfigError):
        copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == before


def test_refresh_keeps_payload_of_other_baseline_sorted_after_stale_manifest(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir()
    functional_export(
        destination, {"a-stale.json": "shared.input", "z-other.json": "shared.input"}
    )
    other = destination / "z-other.json"
    data = json.loads(other.read_bytes())
    other.write_text(json.dumps({**data, "base_ref": "b" * 40}))
    other_before = other.read_bytes()
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == {
        "z-other.json": other_before,
        "shared.input": b"harmless shared.input",
    }


def test_refresh_refuses_to_change_other_baseline_payload(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(source, {"incoming.json": "shared.input"})
    functional_export(destination, {"other.json": "shared.input"})
    other = destination / "other.json"
    payload = b"different harmless bytes"
    (destination / "shared.input").write_bytes(payload)
    data = json.loads(other.read_bytes())
    other.write_text(
        json.dumps(
            {
                **data,
                "base_ref": "b" * 40,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    )
    before = destination_bytes(destination)
    with pytest.raises(ConfigError, match="Refusing to replace unrelated"):
        copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == before


def test_refresh_retires_old_payload_when_manifest_switches_input(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(source, {"case.json": "new.input"})
    functional_export(destination, {"case.json": "old.input"})
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == destination_bytes(source)


def test_export_rejects_missing_source_path_without_retiring_existing_files(tmp_path):
    source, destination = tmp_path / "missing", tmp_path / "destination"
    functional_export(destination, {"existing.json": "existing.input"})
    before = destination_bytes(destination)
    with pytest.raises(ConfigError, match="Missing retained regression directory"):
        copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert destination_bytes(destination) == before


def stale_snapshot(path):
    """A snapshot the refresh must retire: manifests owned by the same baseline."""
    functional_export(
        path, {"stale.json": "stale.input", "kept.json": "kept.input"}, exist_ok=True
    )
    return path


def test_export_refresh_retires_stale_manifests_for_the_baseline(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(source, {"kept.json": "kept.input"})
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    stale_snapshot(destination)
    # Both snapshots claim baseline "a"*40; only the exported one survives.
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert sorted(path.name for path in destination.iterdir()) == [
        "kept.input",
        "kept.json",
    ]


def test_export_refresh_retains_manifests_of_other_baselines(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    functional_export(source, {"kept.json": "kept.input"})
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    functional_export(destination, {"other.json": "other.input"}, exist_ok=True)
    other = destination / "other.json"
    other.write_text(
        json.dumps({**json.loads(other.read_bytes()), "base_ref": "b" * 40})
    )
    other_before = other.read_bytes()
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert other.read_bytes() == other_before
    assert (destination / "other.input").exists()


def test_mixed_valid_and_invalid_external_manifests_corrupt_nothing(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    retained_suite(source)
    (source / "invalid.json").write_text(json.dumps({"base_ref": "a" * 40}))
    with pytest.raises(ConfigError, match="Invalid retained regression"):
        copy_regressions(source, destination, "a" * 40)
    assert not destination.exists()


def test_unverified_external_expectation_is_rejected_before_transfer(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    retained_suite(source)
    item = json.loads((source / "case.json").read_bytes())
    item.update(
        check="full",
        expected={"exit_code": 0, "stdout": "cache only\n", "stderr": ""},
    )
    (source / "case.json").write_text(json.dumps(item))
    with pytest.raises(ConfigError, match="independent local expectation"):
        copy_regressions(source, destination, "a" * 40)
    assert not destination.exists()


def test_cli_rejects_invalid_retained_manifest_without_touching_the_cache(
    tmp_path, pipeline_fixture
):
    cfg, config_path, _ = pipeline_fixture
    invalid = tmp_path / "invalid-retained"
    invalid.mkdir()
    (invalid / "case.json").write_text(json.dumps({"base_ref": "a" * 40}))
    report = tmp_path / "report.json"
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config_path),
            "--output-json",
            str(report),
            "--artifacts",
            str(tmp_path / "runs"),
            "--regressions-from",
            str(invalid),
        ],
    )
    assert result.exit_code == 30, result.output
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["verdict"] == "BUILD_OR_CONFIG_ERROR"
    assert not (cfg.config_directory / cfg.test_suites.regression_directory).exists()


def test_minimized_baseline_failure_is_enrolled_with_its_bytes(
    tmp_path, pipeline_fixture
):
    cfg, _, _ = pipeline_fixture
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 0, summary.notes
    bundle = (
        Path(summary.evidence["run_directory"]) / summary.evidence["reproducers"][0]
    )
    metadata = json.loads((bundle / "reproducer.json").read_text(encoding="utf-8"))
    assert metadata["kind"] == "security"
    assert metadata["finding_side"] == "base"
    minimized = (bundle / "minimized.input").read_bytes()
    assert (bundle / "original.input").exists()
    manifests = sorted(
        (cfg.config_directory / cfg.test_suites.regression_directory).glob("*.json")
    )
    enrolled = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in manifests
        if path.with_suffix(".input").read_bytes() == minimized
    ]
    assert enrolled
    for item in enrolled:
        assert item["base_ref"] == cfg.base_ref
        assert item["sha256"] == hashlib.sha256(minimized).hexdigest()
        assert item["kind"] == "security"
        assert item["finding_side"] == "base"
        assert item["signature"] == cfg.baseline_signature


def test_later_run_loads_generated_cases_and_confirms_the_patch(
    tmp_path, pipeline_fixture
):
    cfg, _, _ = pipeline_fixture
    first = run_pipeline(cfg, tmp_path / "runs")
    assert first.exit_code == 0, first.notes
    second = run_pipeline(cfg, tmp_path / "runs")
    assert second.exit_code == 0, second.notes
    generated = [
        record
        for record in second.evidence["cases"]
        if record["id"].startswith("regression/")
    ]
    assert generated
    security = [item for item in generated if item["baseline_signature"]]
    assert security
    for record in security:
        assert record["baseline_signature"] == cfg.baseline_signature
        if record["baseline_mode"] == record["mode"]:
            assert all(
                run["signature"] == cfg.baseline_signature
                for run in record["runs"]["base"]
            )
        # The correct patch must show neither the designated failure nor a new one.
        assert all(run["signature"] is None for run in record["runs"]["patch"])


@pytest.mark.parametrize(
    "scenario,check_regression",
    [("fixed", True), ("regression", False)],
)
def test_reproduce_exits_zero_after_three_stable_replays(
    tmp_path, pipeline_fixture, monkeypatch, scenario, check_regression
):
    from diffsheriff import reproduce

    cfg, _, state = pipeline_fixture
    state["scenario"] = scenario
    summary = run_pipeline(cfg, tmp_path / "runs")
    bundles = [
        Path(summary.evidence["run_directory"]) / item
        for item in summary.evidence["reproducers"]
    ]
    kind = "security" if check_regression else "functional"
    bundle = next(
        item
        for item in bundles
        if json.loads((item / "reproducer.json").read_text())["kind"] == kind
    )
    argv = ["reproduce", str(bundle)]
    if check_regression:
        argv.append("--check-regression")
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exit_info:
        reproduce.main()
    assert exit_info.value.code == 0
    replay = json.loads((bundle / "replay.json").read_text(encoding="utf-8"))
    assert replay["reproduced"] is True
    assert replay["stable"] is True
    assert len(replay["runs"]["base"]) >= 3
    assert len(replay["runs"]["patch"]) >= 3
    if check_regression:
        assert replay["regression_pass"] is True
