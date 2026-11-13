import hashlib
import json

import pytest

from diffsheriff.config import ConfigError
from diffsheriff.regressions import copy_regressions


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
