"""Configuration validation and schema migration checks."""

from pathlib import Path
import pytest
import yaml
from diffsheriff.config import ConfigError, DiffSheriffConfig

ROOT = Path(__file__).resolve().parents[1]
SYMBOLIZER = "external_symbolizer_path=/usr/bin/llvm-symbolizer"

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


@pytest.mark.parametrize(
    "settings",
    [
        {},
        {"max_granularity": 3, "max_oracle_calls": 10},
        {"max_granularity": None, "max_oracle_calls": 1},
        {"max_granularity": None, "max_oracle_calls": None},
    ],
)
def test_minimization_configuration(tmp_path, settings):
    data = yaml.safe_load(VALID_CONFIG)
    data["minimization"] = settings
    cfg = DiffSheriffConfig.from_yaml(write_config(tmp_path, yaml.safe_dump(data)))
    assert cfg.minimization.max_granularity == settings.get("max_granularity", 16)
    assert cfg.minimization.max_oracle_calls == settings.get("max_oracle_calls", 256)


@pytest.mark.parametrize(
    "settings",
    [
        None,
        [],
        {"unexpected": 1},
        {"max_granularity": True},
        {"max_granularity": 1},
        {"max_granularity": 2.5},
        {"max_oracle_calls": 0},
        {"max_oracle_calls": False},
        {"max_oracle_calls": "256"},
    ],
)
def test_invalid_minimization_configuration(tmp_path, settings):
    data = yaml.safe_load(VALID_CONFIG)
    data["minimization"] = settings
    with pytest.raises(ConfigError, match="minimization"):
        DiffSheriffConfig.from_yaml(write_config(tmp_path, yaml.safe_dump(data)))


def test_sanitizer_environment_options_round_trip(tmp_path):
    data = yaml.safe_load(VALID_CONFIG)
    data["execution"]["environment_variables"] = {
        "ASAN_OPTIONS": (
            "detect_leaks=0:abort_on_error=1:symbolize=1:"
            "external_symbolizer_path=/usr/bin/llvm-symbolizer"
        ),
        "UBSAN_OPTIONS": (
            "print_stacktrace=1:halt_on_error=1:"
            "external_symbolizer_path=/usr/bin/llvm-symbolizer"
        ),
    }
    config = DiffSheriffConfig.from_yaml(write_config(tmp_path, yaml.safe_dump(data)))
    assert (
        config.execution.environment_variables
        == data["execution"]["environment_variables"]
    )


def shipped_configs():
    return [
        ROOT / "configs/example_target.yaml",
        *sorted((ROOT / "evaluation").glob("target*/*.yaml")),
    ]


@pytest.mark.parametrize("path", shipped_configs(), ids=lambda path: path.name)
def test_shipped_configurations_symbolize_sanitizer_reports(path):
    """Every shipped config must give Clang an explicit external symbolizer.

    Without it, UBSan/ASan frames stay as `module+offset`, triage resolves the
    function as `unknown`, and the designated baseline signature cannot be
    established. See context/symbolizer-diagnosis.json.
    """
    config = DiffSheriffConfig.from_yaml(path)
    required = {
        "ASAN_OPTIONS": ("detect_leaks=0", "abort_on_error=1", "symbolize=1"),
        "UBSAN_OPTIONS": ("print_stacktrace=1", "halt_on_error=1"),
    }
    for variable, options in required.items():
        entries = config.execution.environment_variables[variable].split(":")
        assert SYMBOLIZER in entries, f"{path.name}: {variable} lacks the symbolizer"
        for option in options:
            assert option in entries, f"{path.name}: {variable} lacks {option}"
        assert entries.count(SYMBOLIZER) == 1
