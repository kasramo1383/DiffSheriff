"""
Target configuration parser and validator for DiffSheriff.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml


class ConfigError(ValueError):
    """Raised when a target configuration cannot be evaluated safely."""


def _required_string(mapping: dict, key: str, location: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{location}.{key} must be a non-empty string")
    return value


@dataclass
class TargetBuildSection:
    clean_command: str
    release_command: str
    release_binary_path: str
    sanitized_command: str
    sanitized_binary_path: str


@dataclass
class TargetExecutionSection:
    timeout_seconds: float = 5.0
    input_method: str = "file"  # "stdin", "argv", or "file"
    file_argument_flag: Optional[str] = "--file"
    fixed_arguments: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class HardeningBaseline:
    enforce_nx: bool = True
    enforce_pie: bool = True
    min_relro: str = "full"  # "none", "partial", "full"
    enforce_canary: bool = True


@dataclass
class TestSuitesConfig:
    valid_directory: str = "tests/valid"
    boundary_directory: str = "tests/boundary"
    malicious_directory: str = "tests/malicious"
    independent_reference_command: Optional[str] = None


@dataclass
class DiffSheriffConfig:
    target_name: str
    language: str
    repository_path: Path
    build: TargetBuildSection
    execution: TargetExecutionSection
    hardening: HardeningBaseline
    test_suites: TestSuitesConfig

    @classmethod
    def from_yaml(cls, config_path: Path) -> "DiffSheriffConfig":
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ConfigError("configuration root must be a mapping")

        target_info = data.get("target", {})
        build_info = data.get("build", {})
        exec_info = data.get("execution", {})
        hardening_info = data.get("hardening_baseline", {})
        tests_info = data.get("test_suites", {})

        for section_name, section in (
            ("target", target_info),
            ("build", build_info),
            ("execution", exec_info),
            ("hardening_baseline", hardening_info),
            ("test_suites", tests_info),
        ):
            if not isinstance(section, dict):
                raise ConfigError(f"{section_name} must be a mapping")

        target_name = _required_string(target_info, "name", "target")
        language = _required_string(target_info, "language", "target").lower()
        if language not in {"c", "c++", "cpp"}:
            raise ConfigError("target.language must be one of: c, c++, cpp")
        repository_path = Path(
            _required_string(target_info, "repository_path", "target")
        )

        release_info = build_info.get("release", {})
        sanitized_info = build_info.get("sanitized", {})
        if not isinstance(release_info, dict) or not isinstance(sanitized_info, dict):
            raise ConfigError("build.release and build.sanitized must be mappings")

        build_sec = TargetBuildSection(
            clean_command=build_info.get("clean_command", "make clean"),
            release_command=_required_string(release_info, "command", "build.release"),
            release_binary_path=_required_string(
                release_info, "binary_path", "build.release"
            ),
            sanitized_command=_required_string(
                sanitized_info, "command", "build.sanitized"
            ),
            sanitized_binary_path=_required_string(
                sanitized_info, "binary_path", "build.sanitized"
            ),
        )

        timeout_seconds = float(exec_info.get("timeout_seconds", 5.0))
        if timeout_seconds <= 0:
            raise ConfigError("execution.timeout_seconds must be greater than zero")
        input_method = exec_info.get("input_method", "file")
        if input_method not in {"stdin", "argv", "file"}:
            raise ConfigError("execution.input_method must be stdin, argv, or file")
        fixed_arguments = exec_info.get("fixed_arguments", [])
        environment_variables = exec_info.get("environment_variables", {})
        if not isinstance(fixed_arguments, list) or not all(
            isinstance(value, str) for value in fixed_arguments
        ):
            raise ConfigError("execution.fixed_arguments must be a list of strings")
        if not isinstance(environment_variables, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in environment_variables.items()
        ):
            raise ConfigError(
                "execution.environment_variables must map strings to strings"
            )

        exec_sec = TargetExecutionSection(
            timeout_seconds=timeout_seconds,
            input_method=input_method,
            file_argument_flag=exec_info.get("file_argument_flag", "--file"),
            fixed_arguments=fixed_arguments,
            environment_variables=environment_variables,
        )

        min_relro = hardening_info.get("min_relro", "full")
        if min_relro not in {"none", "partial", "full"}:
            raise ConfigError(
                "hardening_baseline.min_relro must be none, partial, or full"
            )

        hardening_sec = HardeningBaseline(
            enforce_nx=hardening_info.get("enforce_nx", True),
            enforce_pie=hardening_info.get("enforce_pie", True),
            min_relro=min_relro,
            enforce_canary=hardening_info.get("enforce_canary", True),
        )

        tests_sec = TestSuitesConfig(
            valid_directory=tests_info.get("valid_directory", "tests/valid"),
            boundary_directory=tests_info.get("boundary_directory", "tests/boundary"),
            malicious_directory=tests_info.get(
                "malicious_directory", "tests/malicious"
            ),
            independent_reference_command=tests_info.get("ground_truth", {}).get(
                "independent_reference_command"
            ),
        )

        return cls(
            target_name=target_name,
            language=language,
            repository_path=repository_path,
            build=build_sec,
            execution=exec_sec,
            hardening=hardening_sec,
            test_suites=tests_sec,
        )
