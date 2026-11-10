"""Explicit, fail-closed configuration for authorized local targets."""

from dataclasses import dataclass, field
import math
from pathlib import Path, PurePosixPath
import re
from typing import Optional

import yaml


class ConfigError(ValueError):
    """Configuration cannot be evaluated safely."""


def _mapping(value, name):
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return value


def _string(value, name, empty=False):
    if not isinstance(value, str) or "\0" in value or (not empty and not value.strip()):
        raise ConfigError(f"{name} must be a valid string")
    return value


def _positive(value, name, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a positive number")
    if (
        not math.isfinite(value)
        or value <= 0
        or (integer and not isinstance(value, int))
    ):
        raise ConfigError(
            f"{name} must be a positive {'integer' if integer else 'number'}"
        )
    return value


def relative_path(value, name):
    value = _string(value, name)
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise ConfigError(f"{name} must be a relative POSIX path without traversal")
    if not path.parts or path.parts[0] in {".git", ".diffsheriff"}:
        raise ConfigError(f"{name} uses a reserved or empty path")
    return value


@dataclass
class TargetBuildSection:
    clean_command: str
    release_command: str
    release_binary_path: str
    sanitized_command: str
    sanitized_binary_path: str
    timeout_seconds: float = 120.0


@dataclass
class TargetExecutionSection:
    timeout_seconds: float = 5.0
    input_method: str = "file"
    file_argument_flag: Optional[str] = "--file"
    fixed_arguments: list[str] = field(default_factory=list)
    environment_variables: dict[str, str] = field(default_factory=dict)
    image: str = "diffsheriff:local"
    memory_mb: int = 2048
    cpus: float = 2.0
    pids_limit: int = 128
    output_limit_bytes: int = 1048576


@dataclass
class HardeningBaseline:
    enforce_nx: bool = True
    enforce_pie: bool = True
    min_relro: str = "full"
    enforce_canary: bool = True


@dataclass
class TestSuitesConfig:
    valid_directory: str
    boundary_directory: str
    malicious_directory: str
    expectations: str
    provenance: str
    regression_directory: str = "regressions"
    independent_reference_command: list[str] = field(default_factory=list)


@dataclass
class DiffSheriffConfig:
    target_name: str
    language: str
    repository_path: Path
    build: TargetBuildSection
    execution: TargetExecutionSection
    hardening: HardeningBaseline
    test_suites: TestSuitesConfig
    base_ref: str
    patch_ref: str
    baseline_signature: dict
    config_directory: Path

    @classmethod
    def from_yaml(cls, config_path: Path):
        data = _mapping(yaml.safe_load(config_path.read_text(encoding="utf-8")), "root")
        if str(data.get("version")) != "2.0":
            raise ConfigError("version must be '2.0'; see configs/example_target.yaml")
        target = _mapping(data.get("target"), "target")
        build = _mapping(data.get("build"), "build")
        execution = _mapping(data.get("execution", {}), "execution")
        hardening = _mapping(data.get("hardening_baseline", {}), "hardening_baseline")
        suites = _mapping(data.get("test_suites"), "test_suites")
        language = _string(target.get("language"), "target.language").lower()
        if language not in {"c", "c++", "cpp"}:
            raise ConfigError("target.language must be c, c++, or cpp")
        refs = {}
        for key in ("base_ref", "patch_ref"):
            value = _string(target.get(key), f"target.{key}")
            if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
                raise ConfigError(f"target.{key} must be a full Git commit hash")
            refs[key] = value
        signature = _mapping(
            target.get("baseline_signature"), "target.baseline_signature"
        )
        for key in ("error_type", "file", "function"):
            _string(signature.get(key), f"target.baseline_signature.{key}")
        relative_path(signature["file"], "target.baseline_signature.file")
        _positive(signature.get("line"), "target.baseline_signature.line", integer=True)
        commands = {}
        for mode in ("release", "sanitized"):
            section = _mapping(build.get(mode), f"build.{mode}")
            commands[f"{mode}_command"] = _string(
                section.get("command"), f"build.{mode}.command"
            )
            commands[f"{mode}_binary_path"] = relative_path(
                section.get("binary_path"), f"build.{mode}.binary_path"
            )
        build_cfg = TargetBuildSection(
            clean_command=_string(
                build.get("clean_command", ""), "build.clean_command", empty=True
            ),
            timeout_seconds=_positive(
                build.get("timeout_seconds", 120), "build.timeout_seconds"
            ),
            **commands,
        )
        if set(execution) - set(TargetExecutionSection.__dataclass_fields__):
            raise ConfigError("unknown execution setting")
        exec_cfg = TargetExecutionSection(**execution)
        for name in ("timeout_seconds", "cpus"):
            _positive(getattr(exec_cfg, name), f"execution.{name}")
        for name in ("memory_mb", "pids_limit", "output_limit_bytes"):
            _positive(getattr(exec_cfg, name), f"execution.{name}", integer=True)
        if exec_cfg.input_method not in ("stdin", "file", "argv"):
            raise ConfigError("execution.input_method must be stdin, argv, or file")
        if exec_cfg.file_argument_flag is not None:
            _string(
                exec_cfg.file_argument_flag, "execution.file_argument_flag", empty=True
            )
        if not isinstance(exec_cfg.fixed_arguments, list):
            raise ConfigError("execution.fixed_arguments must be a list")
        for arg in exec_cfg.fixed_arguments:
            _string(arg, "execution.fixed_arguments[]", empty=True)
        _mapping(exec_cfg.environment_variables, "execution.environment_variables")
        for key, value in exec_cfg.environment_variables.items():
            _string(key, "environment key")
            _string(value, "environment value", empty=True)
            if "=" in key:
                raise ConfigError("environment key cannot contain '='")
        _string(exec_cfg.image, "execution.image")
        if exec_cfg.image.startswith("-"):
            raise ConfigError("execution.image cannot start with '-'")
        if set(hardening) - set(HardeningBaseline.__dataclass_fields__):
            raise ConfigError("unknown hardening_baseline setting")
        hard_cfg = HardeningBaseline(**hardening)
        for key in ("enforce_nx", "enforce_pie", "enforce_canary"):
            if not isinstance(getattr(hard_cfg, key), bool):
                raise ConfigError(f"hardening_baseline.{key} must be a boolean")
        if hard_cfg.min_relro not in ("none", "partial", "full"):
            raise ConfigError(
                "hardening_baseline.min_relro must be none, partial, or full"
            )
        suite_paths = {}
        for key in (
            "valid_directory",
            "boundary_directory",
            "malicious_directory",
            "expectations",
            "regression_directory",
        ):
            value = suites.get(
                key, "regressions" if key == "regression_directory" else None
            )
            suite_paths[key] = relative_path(value, f"test_suites.{key}")
        reference = suites.get("independent_reference_command", [])
        if not isinstance(reference, list):
            raise ConfigError(
                "test_suites.independent_reference_command must be an argv list"
            )
        for argument in reference:
            _string(argument, "independent_reference_command argument")
        return cls(
            target_name=_string(target.get("name"), "target.name"),
            language=language,
            repository_path=(
                config_path.resolve().parent
                / _string(target.get("repository_path"), "target.repository_path")
            ).resolve(),
            build=build_cfg,
            execution=exec_cfg,
            hardening=hard_cfg,
            test_suites=TestSuitesConfig(
                provenance=_string(suites.get("provenance"), "test_suites.provenance"),
                independent_reference_command=reference,
                **suite_paths,
            ),
            baseline_signature={
                key: signature[key]
                for key in ("error_type", "file", "function", "line")
            },
            config_directory=config_path.resolve().parent,
            **refs,
        )
