"""Transfer retained regression data without replacing conflicting local assets."""

import json
from pathlib import Path

from diffsheriff.builder import compute_sha256
from diffsheriff.config import ConfigError
from diffsheriff.pipeline import contained_file, expected_result


def read_regression(root, name):
    """Validate transferred metadata and its bytes before considering precedence."""
    try:
        manifest = contained_file(root, name)
        item = json.loads(manifest.read_text(encoding="utf-8"))
        required = {
            "base_ref",
            "input",
            "sha256",
            "mode",
            "signature",
            "finding_signature",
            "finding_side",
            "kind",
            "check",
            "valid_input",
            "expected",
        }
        if not isinstance(item, dict) or not required <= item.keys():
            raise ConfigError("Incomplete retained regression manifest")
        if (
            not isinstance(item["base_ref"], str)
            or item["mode"] not in {"release", "sanitized"}
            or item["finding_side"] not in {"base", "patch"}
            or item["kind"] not in {"security", "functional"}
            or type(item["valid_input"]) is not bool
        ):
            raise ConfigError("Invalid retained regression identity")
        for key in ("signature", "finding_signature"):
            signature = item[key]
            if signature is not None and (
                not isinstance(signature, dict)
                or not {"error_type", "file", "function", "line"} <= signature.keys()
                or ("side" in signature and signature["side"] != "patch")
                or any(
                    not isinstance(signature[k], str)
                    for k in ("error_type", "file", "function")
                )
                or type(signature["line"]) is not int
                or signature["line"] <= 0
            ):
                raise ConfigError("Invalid retained regression signature")
        if item["kind"] == "security" and item["finding_signature"] is None:
            raise ConfigError("Security regression needs a finding signature")
        if item["expected"] is None:
            if (
                item["check"] != "diagnostic"
                or item["kind"] != "security"
                or item["valid_input"]
            ):
                raise ConfigError("Invalid diagnostic regression manifest")
        else:
            expected_result(item["expected"])
            if item["check"] != "full":
                raise ConfigError("Expected regression must use a full check")
        payload = contained_file(root, item["input"])
        if payload.name != item["input"]:
            raise ConfigError(
                "Retained generated regressions must use flat input paths"
            )
        if compute_sha256(payload) != item["sha256"]:
            raise ConfigError("Retained regression input hash does not match")
        return item, payload, manifest
    except (OSError, ValueError, TypeError, KeyError) as error:
        raise ConfigError(f"Invalid retained regression {name}: {error}") from error


def regression_identity(item):
    # Include unknown fields so future replay semantics cannot silently reconcile.
    return json.dumps(
        {
            k: v
            for k, v in item.items()
            if k not in {"expected", "check", "valid_input"}
        },
        sort_keys=True,
    )


def copy_regressions(
    source, destination, base_ref, *, replace_existing=False, local_cases=()
):
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or destination.is_symlink():
        raise ConfigError("Regression directories cannot be symlinks")
    if not source.is_dir():
        raise ConfigError(f"Missing retained regression directory: {source}")
    pending = {}
    for manifest in sorted(source.glob("*.json")):
        item, payload, manifest = read_regression(source, manifest.name)
        target_manifest = destination / manifest.name
        if target_manifest.is_symlink():
            raise ConfigError("Regression manifest cannot be a symlink")
        if item["base_ref"] != base_ref:
            if target_manifest.exists() and not replace_existing:
                raise ConfigError("Conflicting retained regression baseline")
            continue
        manifest_data = manifest.read_bytes()
        if not replace_existing and target_manifest.exists():
            local, local_payload, _ = read_regression(destination, manifest.name)
            if (
                regression_identity(item) != regression_identity(local)
                or payload.read_bytes() != local_payload.read_bytes()
                or not (
                    item == local
                    or (item["expected"] is None and local["expected"] is not None)
                )
            ):
                raise ConfigError(
                    f"Refusing to replace conflicting regression: {target_manifest}"
                )
            manifest_data = target_manifest.read_bytes()
        elif not replace_existing and item["expected"] is not None:
            if not any(
                case["payload"] == payload.read_bytes()
                and case["expected"] == item["expected"]
                and case["valid_input"] == item["valid_input"]
                for case in local_cases
            ):
                raise ConfigError(
                    "Cached result needs a matching independent local expectation"
                )
        for path in (payload, manifest):
            data = manifest_data if path == manifest else path.read_bytes()
            if path.name in pending and pending[path.name] != data:
                raise ConfigError("Conflicting retained regression files")
            target = destination / path.name
            if (
                target.is_symlink()
                or (target.exists() and not target.is_file())
                or (
                    not replace_existing
                    and target.exists()
                    and target.read_bytes() != data
                )
            ):
                raise ConfigError(
                    f"Refusing to replace conflicting regression: {target}"
                )
            pending[path.name] = data
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in pending.items():
        target = destination / name
        if not target.exists() or target.read_bytes() != data:
            target.write_bytes(data)
