"""Retained checkpoint manifests must describe the delivered evidence bytes."""

import hashlib
import json
from pathlib import Path

import pytest

CHECKPOINTS = Path(__file__).resolve().parents[1] / "artifacts" / "checkpoints"


@pytest.mark.parametrize(
    "manifest",
    sorted(CHECKPOINTS.glob("*/artifact-sha256.json")),
    ids=lambda p: p.parent.name,
)
def test_checkpoint_artifact_hashes(manifest):
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    assert entries, f"Empty artifact manifest: {manifest}"
    for name, expected in entries.items():
        artifact = manifest.parent / name
        assert artifact.resolve().is_relative_to(manifest.parent.resolve()), name
        assert artifact.is_file(), f"Missing retained artifact: {artifact}"
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        assert actual == expected, f"Stale artifact checksum: {artifact}"
