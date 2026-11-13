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
    (source / "case.json").write_text(json.dumps(item))
    copy_regressions(source, destination, "a" * 40, replace_existing=True)
    assert (source / "case.json").read_bytes() == (
        destination / "case.json"
    ).read_bytes()
