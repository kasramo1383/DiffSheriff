"""Configuration validation and schema migration checks."""

from pathlib import Path
import pytest
import yaml
from diffsheriff.config import ConfigError, DiffSheriffConfig

VALID_CONFIG = """
version: '2.0'
target:
  name: sample
  language: c
  repository_path: targets/sample
  base_ref: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  patch_ref: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
  baseline_signature:
    error_type: heap-buffer-overflow
    file: source.c
    function: parse
    line: 8
build:
  clean_command: make clean
  release:
    command: make release
    binary_path: bin/sample
  sanitized:
    command: make sanitized
    binary_path: bin/sample-asan
execution:
  timeout_seconds: 5
  input_method: stdin
hardening_baseline:
  min_relro: partial
test_suites:
  valid_directory: tests/valid
  boundary_directory: tests/boundary
  malicious_directory: tests/invalid
  expectations: expected.json
  provenance: Independent test specification
"""


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "target.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_configuration_loads(tmp_path):
    config = DiffSheriffConfig.from_yaml(write_config(tmp_path, VALID_CONFIG))
    assert config.target_name == "sample"
    assert config.execution.input_method == "stdin"
    assert config.repository_path == tmp_path / "targets/sample"


def test_missing_build_command_is_rejected(tmp_path):
    invalid = VALID_CONFIG.replace("    command: make release\n", "", 1)
    with pytest.raises(ConfigError, match="build.release.command"):
        DiffSheriffConfig.from_yaml(write_config(tmp_path, invalid))


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("execution", "timeout_seconds", float("nan")),
        ("execution", "timeout_seconds", True),
        ("execution", "memory_mb", 1.5),
        ("execution", "input_method", "socket"),
        ("execution", "file_argument_flag", 1),
        ("execution", "fixed_arguments", "argument"),
        ("execution", "environment_variables", {"X": 1}),
        ("execution", "environment_variables", {"X=Y": "value"}),
        ("execution", "image", "--privileged"),
        ("execution", "unexpected", True),
        ("target", "base_ref", "main"),
        ("hardening_baseline", "enforce_nx", "false"),
        ("test_suites", "expectations", "../expected.json"),
        ("test_suites", "regression_directory", "/tmp"),
    ],
)
def test_invalid_settings_fail_closed(tmp_path, section, key, value):
    data = yaml.safe_load(VALID_CONFIG)
    data[section][key] = value
    with pytest.raises(ConfigError):
        DiffSheriffConfig.from_yaml(write_config(tmp_path, yaml.safe_dump(data)))


def test_binary_path_cannot_escape(tmp_path):
    with pytest.raises(ConfigError, match="relative POSIX"):
        DiffSheriffConfig.from_yaml(
            write_config(tmp_path, VALID_CONFIG.replace("bin/sample", "../sample"))
        )


def test_old_schema_needs_explicit_migration(tmp_path):
    with pytest.raises(ConfigError, match="version"):
        DiffSheriffConfig.from_yaml(
            write_config(
                tmp_path, VALID_CONFIG.replace("version: '2.0'", "version: '1.0'")
            )
        )
