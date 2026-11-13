"""Real native smoke test; enable with DIFFSHERIFF_DOCKER_TESTS=1."""

import json
import os
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace

import pytest
import yaml
from click.testing import CliRunner

from diffsheriff.cli import main
from diffsheriff.config import DiffSheriffConfig
from diffsheriff.runner import execute_container
from .test_config import VALID_CONFIG

pytestmark = pytest.mark.skipif(
    os.environ.get("DIFFSHERIFF_DOCKER_TESTS") != "1",
    reason="requires the built Linux Docker image",
)


def test_real_native_matrix_and_input_interfaces(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    shutil.copy2(
        Path(__file__).parent / "fixtures/harmless/main.c", repository / "main.c"
    )

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repository), *args],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    git("init")
    git("add", "main.c")
    git(
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Harmless fixture",
    )
    base = git("rev-parse", "HEAD")
    with (repository / "main.c").open("a") as stream:
        stream.write("\n/* An independently changed source revision. */\n")
    git("add", "main.c")
    git(
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Harmless change",
    )
    patch = git("rev-parse", "HEAD")
    config = yaml.safe_load(VALID_CONFIG)
    config["target"].update(
        repository_path="repository", base_ref=base, patch_ref=patch
    )
    flags = (
        " -g -fno-omit-frame-pointer -fstack-protector-all "
        "-fPIE -pie -Wl,-z,relro,-z,now "
    )
    config["build"] = {
        "clean_command": "",
        "release": {
            "command": "cc" + flags + "main.c -o program",
            "binary_path": "program",
        },
        "sanitized": {
            "command": "clang -fsanitize=address,undefined"
            + flags
            + "main.c -o program",
            "binary_path": "program",
        },
    }
    config["execution"]["environment_variables"] = {
        "ASAN_OPTIONS": "detect_leaks=0",
        "UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1",
    }
    config["execution"]["image"] = os.environ.get(
        "DIFFSHERIFF_TEST_IMAGE", "diffsheriff:local"
    )
    config["test_suites"]["expectations"] = "expected.json"
    expected = {}
    for suite, directory, payload in [
        ("valid", "valid", b"hello"),
        ("boundary", "boundary", b""),
        ("malicious", "invalid", b"\xff"),
    ]:
        folder = tmp_path / "tests" / directory
        folder.mkdir(parents=True)
        (folder / "input").write_bytes(payload)
        expected[suite + "/input"] = {
            "exit_code": 0,
            "stdout": payload.decode("latin1"),
            "stderr": "",
        }
    (tmp_path / "expected.json").write_text(json.dumps(expected))
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    cfg = DiffSheriffConfig.from_yaml(path)
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(path),
            "--output-json",
            str(tmp_path / "report.json"),
            "--artifacts",
            str(tmp_path / "runs"),
            "--export-regressions",
            str(tmp_path / "retained"),
        ],
    )
    assert result.exit_code == 40, result.output
    report = json.loads((tmp_path / "report.json").read_text())
    summary = SimpleNamespace(**report)
    assert summary.exit_code == 40, summary.notes
    assert summary.functional_status == "PASS"
    assert summary.total_tests_run == 36
    assert summary.notes == [
        "Designated baseline flaw was not reproduced with stable source evidence"
    ]
    for hardening in summary.evidence["hardening"].values():
        assert hardening["indicators"]["gnu_stack_flags"] == [6]
        assert hardening["indicators"]["canary_symbols"]
        assert hardening["indicators"]["df_1_pie"]
    record = summary.evidence["builds"]["patch"]["release"]
    for method, fixed in [("stdin", []), ("file", []), ("argv", ["--argv"])]:
        from dataclasses import replace

        settings = replace(cfg.execution, input_method=method, fixed_arguments=fixed)
        result = execute_container(
            Path(record["source"]), record["binary"], b"check", settings
        )
        assert result.exit_code == 0 and result.stdout == "check", result
