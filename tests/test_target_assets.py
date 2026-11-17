"""Delivered target expectations and fresh-runner source setup."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zlib

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "evaluation/target1"


def test_zlib_corpus_and_generated_validity_agree_with_reference():
    from diffsheriff.config import DiffSheriffConfig
    from diffsheriff.pipeline import discover_cases

    config = DiffSheriffConfig.from_yaml(TARGET / "correct.yaml")
    discovered, _ = discover_cases(config)
    functional_ids = {
        "regression/" + p.stem
        for p in (TARGET / "generated-regressions").glob("*.json")
        if json.loads(p.read_text())["kind"] == "functional"
    }
    enrolled = [c for c in discovered if c["id"] in functional_ids]
    assert len(enrolled) == 2
    assert all(c["valid_input"] and c["suite"] == "valid" for c in enrolled)
    expectations = json.loads((TARGET / "suites/expected.json").read_text())
    cases = []
    for key, expected in expectations.items():
        suite, name = key.split("/", 1)
        directory = "invalid" if suite == "malicious" else suite
        cases.append((TARGET / "suites" / directory / name, expected))
    for manifest in (TARGET / "generated-regressions").glob("*.json"):
        item = json.loads(manifest.read_text())
        path = manifest.parent / item["input"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        cases.append((path, {**item["expected"], "valid_input": item["valid_input"]}))
    for path, expected in cases:
        payload = path.read_bytes()
        # An independent system implementation accepts the selected byte streams.
        assert zlib.decompress(zlib.compress(payload)) == payload
        result = subprocess.run(
            [sys.executable, str(TARGET / "reference.py")],
            input=payload,
            capture_output=True,
            check=True,
        )
        assert json.loads(result.stdout) == expected
        assert expected["valid_input"] is True


@pytest.mark.parametrize("size,code", [(0, 0), (65536, 0), (65537, 2)])
def test_zlib_reference_scope_is_explicit(size, code):
    result = subprocess.run(
        [sys.executable, str(TARGET / "reference.py")],
        input=b"x" * size,
        capture_output=True,
    )
    assert result.returncode == code
    if code:
        assert not result.stdout and b"outside the reviewed" in result.stderr
    else:
        assert json.loads(result.stdout)["valid_input"]


def preparation_script():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/validate_target.yml").read_text()
    )
    steps = workflow["jobs"]["validate"]["steps"]
    prep = next(
        i
        for i, step in enumerate(steps)
        if step.get("name") == "Prepare target sources"
    )
    validate = next(
        i for i, step in enumerate(steps) if step.get("name") == "Run patch validation"
    )
    assert prep < validate
    return steps[prep]["run"]


def copy_bundles(tmp_path):
    for target in ("target1", "target2"):
        (tmp_path / "targets" / target).mkdir(parents=True)
        (tmp_path / "evaluation" / target).mkdir(parents=True)
        shutil.copyfile(
            ROOT / "targets" / target / "source.bundle",
            tmp_path / "targets" / target / "source.bundle",
        )


@pytest.mark.skipif(sys.platform == "win32", reason="CI uses bash on Linux")
def test_workflow_prepares_all_configured_commits_without_developer_state(tmp_path):
    copy_bundles(tmp_path)
    subprocess.run(
        ["bash", "-e", "-c", preparation_script()],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    for config in (ROOT / "evaluation").glob("target*/*.yaml"):
        item = yaml.safe_load(config.read_text())["target"]
        repo = tmp_path / "evaluation" / config.parent.name / "repository"
        for ref in (item["base_ref"], item["patch_ref"]):
            result = subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-t", ref],
                check=True,
                capture_output=True,
                text=True,
            )
            assert result.stdout.strip() == "commit"
    # A second invocation cannot overwrite existing source or local modifications.
    marker = tmp_path / "evaluation/target1/repository/local-work"
    marker.write_text("keep")
    result = subprocess.run(
        ["bash", "-e", "-c", preparation_script()], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0 and marker.read_text() == "keep"
    assert b"Refusing to overwrite" in result.stderr


@pytest.mark.skipif(sys.platform == "win32", reason="CI uses bash on Linux")
def test_workflow_missing_bundle_fails_before_validation(tmp_path):
    copy_bundles(tmp_path)
    (tmp_path / "targets/target1/source.bundle").unlink()
    result = subprocess.run(
        ["bash", "-e", "-c", preparation_script()], cwd=tmp_path, capture_output=True
    )
    assert result.returncode != 0
    assert not (tmp_path / "evaluation/target1/repository").exists()
