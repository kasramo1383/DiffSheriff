"""Transfer retained regression data without replacing conflicting local assets."""

import json
from pathlib import Path

from diffsheriff.builder import compute_sha256
from diffsheriff.config import ConfigError
from diffsheriff.pipeline import contained_file


def copy_regressions(source, destination, base_ref, *, replace_existing=False):
    source, destination = Path(source), Path(destination)
    if not source.is_dir():
        raise ConfigError(f"Missing retained regression directory: {source}")
    pending = {}
    for manifest in sorted(source.glob("*.json")):
        manifest = contained_file(source, manifest.name)
        item = json.loads(manifest.read_text(encoding="utf-8"))
        if item["base_ref"] != base_ref:
            continue
        payload = contained_file(source, item["input"])
        if payload.name != item["input"]:
            raise ConfigError(
                "Retained generated regressions must use flat input paths"
            )
        if compute_sha256(payload) != item["sha256"]:
            raise ConfigError("Retained regression input hash does not match")
        for path in (payload, manifest):
            data = path.read_bytes()
            if path.name in pending and pending[path.name] != data:
                raise ConfigError("Conflicting retained regression files")
            target = destination / path.name
            if target.is_symlink() or (
                not replace_existing and target.exists() and target.read_bytes() != data
            ):
                raise ConfigError(
                    f"Refusing to replace conflicting regression: {target}"
                )
            pending[path.name] = data
    if destination.is_symlink():
        raise ConfigError("Regression destination cannot be a symlink")
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in pending.items():
        (destination / name).write_bytes(data)
