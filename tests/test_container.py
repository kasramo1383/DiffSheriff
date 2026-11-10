"""Container boundaries and reliable signal/limit propagation."""

from dataclasses import asdict
import json
import subprocess

import pytest
from diffsheriff.config import TargetExecutionSection
from diffsheriff.runner import ExecutionResult, execute_container, run_container


def test_container_has_no_network_or_writable_source(tmp_path, monkeypatch):
    commands = []

    def capture(args, *a, **kw):
        commands.append(args)
        return ExecutionResult(0, "ok", "", False)

    def docker(args, **kw):
        if args[1] == "inspect":
            return subprocess.CompletedProcess(
                args,
                0,
                json.dumps({"ExitCode": 0, "OOMKilled": False, "Error": ""}),
                "",
            )
        commands.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr("diffsheriff.runner.capture_command", capture)
    monkeypatch.setattr("diffsheriff.runner.subprocess.run", docker)
    run_container(tmp_path, ["/bin/true"], TargetExecutionSection())
    args = commands[0]
    for flag in [
        "--network=none",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--read-only",
    ]:
        assert flag in args
    assert any("dst=/src,readonly" in arg for arg in args)
    assert "--memory" in args and "--pids-limit" in args
    assert commands[-1][:3] == ["docker", "rm", "--force"]


def test_cleanup_runs_after_client_failure(tmp_path, monkeypatch):
    cleaned = []

    def fail(*args, **kwargs):
        raise OSError("client failure")

    monkeypatch.setattr("diffsheriff.runner.capture_command", fail)
    monkeypatch.setattr(
        "diffsheriff.runner.subprocess.run",
        lambda args, **kwargs: cleaned.append(args)
        or subprocess.CompletedProcess(args, 0, "", ""),
    )
    with pytest.raises(OSError):
        run_container(tmp_path, ["/bin/true"], TargetExecutionSection())
    assert cleaned[0][1:3] == ["rm", "--force"]


def test_container_supervisor_preserves_real_signal(tmp_path, monkeypatch):
    child = ExecutionResult(-11, "", "", False, command=["/src/program"])
    monkeypatch.setattr(
        "diffsheriff.runner.run_container",
        lambda *a, **kw: ExecutionResult(0, json.dumps(asdict(child)), "", False),
    )
    result = execute_container(
        tmp_path, "program", b"", TargetExecutionSection(input_method="stdin")
    )
    assert result.exit_code == -11


def test_container_supervisor_failure_is_not_a_target_crash(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "diffsheriff.runner.run_container",
        lambda *a, **kw: ExecutionResult(1, "", "missing Python module", False),
    )
    with pytest.raises(RuntimeError, match="supervisor failed"):
        execute_container(
            tmp_path, "program", b"", TargetExecutionSection(input_method="stdin")
        )
