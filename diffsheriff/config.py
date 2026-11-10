"""
Target configuration parser and validator for DiffSheriff.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml


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

        target_info = data.get("target", {})
        build_info = data.get("build", {})
        exec_info = data.get("execution", {})
        hardening_info = data.get("hardening_baseline", {})
        tests_info = data.get("test_suites", {})

        build_sec = TargetBuildSection(
            clean_command=build_info.get("clean_command", "make clean"),
            release_command=build_info.get("release", {}).get("command", "make release"),
            release_binary_path=build_info.get("release", {}).get("binary_path", "bin/target"),
            sanitized_command=build_info.get("sanitized", {}).get("command", "make debug"),
            sanitized_binary_path=build_info.get("sanitized", {}).get("binary_path", "bin/target_asan"),
        )

        exec_sec = TargetExecutionSection(
            timeout_seconds=float(exec_info.get("timeout_seconds", 5.0)),
            input_method=exec_info.get("input_method", "file"),
            file_argument_flag=exec_info.get("file_argument_flag", "--file"),
            fixed_arguments=exec_info.get("fixed_arguments", []),
            environment_variables=exec_info.get("environment_variables", {}),
        )

        hardening_sec = HardeningBaseline(
            enforce_nx=hardening_info.get("enforce_nx", True),
            enforce_pie=hardening_info.get("enforce_pie", True),
            min_relro=hardening_info.get("min_relro", "full"),
            enforce_canary=hardening_info.get("enforce_canary", True),
        )

        tests_sec = TestSuitesConfig(
            valid_directory=tests_info.get("valid_directory", "tests/valid"),
            boundary_directory=tests_info.get("boundary_directory", "tests/boundary"),
            malicious_directory=tests_info.get("malicious_directory", "tests/malicious"),
            independent_reference_command=tests_info.get("ground_truth", {}).get(
                "independent_reference_command"
            ),
        )

        return cls(
            target_name=target_info.get("name", "unnamed_target"),
            language=target_info.get("language", "c"),
            repository_path=Path(target_info.get("repository_path", ".")),
            build=build_sec,
            execution=exec_sec,
            hardening=hardening_sec,
            test_suites=tests_sec,
        )
