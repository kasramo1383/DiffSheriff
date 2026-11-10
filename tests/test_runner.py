"""Unit tests for process execution behavior."""

from pathlib import Path
import os
import sys

from diffsheriff.runner import execute_target


def test_custom_environment_does_not_remove_parent_environment():
    result = execute_target(
        Path(sys.executable),
        b"payload",
        input_method="argv",
        fixed_args=[
            "-c",
            "import os; "
            "print(os.environ['DIFFSHERIFF_TEST']); "
            "print(bool(os.environ.get('PATH')))",
        ],
        env_vars={"DIFFSHERIFF_TEST": "present"},
    )
    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["present", "True"]
    assert os.environ.get("DIFFSHERIFF_TEST") is None


def test_output_is_bounded():
    from diffsheriff.runner import capture_command

    result = capture_command(
        [sys.executable, "-c", 'import sys; sys.stdout.write("x" * 100000)'],
        5,
        limit=4096,
    )
    assert len(result.stdout) == 4096
    assert result.output_limited


def test_timeout_retains_output():
    result = execute_target(
        Path(sys.executable),
        b"",
        input_method="stdin",
        fixed_args=["-c", 'import time; print("started", flush=True); time.sleep(5)'],
        timeout_sec=0.2,
    )
    assert result.timed_out
    assert "started" in result.stdout


def test_file_input_and_argv_utf8(tmp_path, monkeypatch):
    import tempfile

    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    result = execute_target(
        Path(sys.executable),
        b"content",
        file_flag=None,
        fixed_args=[
            "-c",
            "import pathlib,sys; print(pathlib.Path(sys.argv[1]).read_text())",
        ],
    )
    assert result.stdout.strip() == "content"
    assert not list(tmp_path.iterdir())
