"""Unit tests for fail-closed configuration validation."""

from pathlib import Path

import pytest

from diffsheriff.config import ConfigError, DiffSheriffConfig

VALID_CONFIG = """
target:
  name: sample
  language: c
  repository_path: targets/sample
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
test_suites: {}
"""


def write_config(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "target.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_configuration_loads(tmp_path):
    config = DiffSheriffConfig.from_yaml(write_config(tmp_path, VALID_CONFIG))
    assert config.target_name == "sample"
    assert config.execution.input_method == "stdin"


def test_missing_build_command_is_rejected(tmp_path):
    invalid = VALID_CONFIG.replace("    command: make release\n", "", 1)
    with pytest.raises(ConfigError, match="build.release.command"):
        DiffSheriffConfig.from_yaml(write_config(tmp_path, invalid))


def test_unknown_input_method_is_rejected(tmp_path):
    invalid = VALID_CONFIG.replace("input_method: stdin", "input_method: socket")
    with pytest.raises(ConfigError, match="input_method"):
        DiffSheriffConfig.from_yaml(write_config(tmp_path, invalid))
