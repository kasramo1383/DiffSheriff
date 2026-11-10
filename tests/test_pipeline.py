"""End-to-end orchestration with synthetic diagnostics, never vulnerable code."""

import json
from dataclasses import replace
from pathlib import Path
import subprocess

from click.testing import CliRunner
import pytest

from diffsheriff.cli import main
from diffsheriff.config import DiffSheriffConfig
from diffsheriff.hardening import HardeningResult
from diffsheriff.pipeline import run_pipeline
from diffsheriff.runner import ExecutionResult
from .test_config import VALID_CONFIG, write_config


@pytest.fixture
def pipeline_fixture(tmp_path, monkeypatch):
    config_path = write_config(tmp_path, VALID_CONFIG)
    cfg = DiffSheriffConfig.from_yaml(config_path)
    expected = {}
    for suite, value in [
        ("valid", b"ordinary"),
        ("boundary", b"boundary"),
        ("invalid", b"diagnostic"),
    ]:
        folder = tmp_path / "tests" / suite
        folder.mkdir(parents=True)
        (folder / "input").write_bytes(value)
        expected[("malicious" if suite == "invalid" else suite) + "/input"] = {
            "exit_code": 0,
            "stdout": "ok\n",
            "stderr": "",
        }
    (tmp_path / "expected.json").write_text(json.dumps(expected))
    monkeypatch.setattr(
        "diffsheriff.pipeline.resolve_image", lambda image: "sha256:test-image"
    )
    monkeypatch.setattr(
        "diffsheriff.pipeline.subprocess.run",
        lambda *a, **kw: subprocess.CompletedProcess(
            a,
            0,
            b"--- a/source.c\n+++ b/source.c\n@@ -7 +7 @@\n-old caller\n+new caller\n",
            b"",
        ),
    )

    def build(repository, commit, destination, build, settings, records):
        result = {}
        for mode in ("release", "sanitized"):
            source = destination / mode
            source.mkdir()
            (source / "program").write_bytes(b"harmless fixture")
            result[mode] = (source, "program")
            records[mode] = {"commit": commit, "binary": "program"}
        return result

    monkeypatch.setattr("diffsheriff.pipeline.build_isolated_matrix", build)
    monkeypatch.setattr(
        "diffsheriff.pipeline.inspect_elf_hardening",
        lambda p: HardeningResult(True, True, "full", True),
    )
    state = {"scenario": "fixed", "calls": 0}

    def execute(source, binary, payload, settings):
        state["calls"] += 1
        patch = source.parent.name == "patch"
        sanitized = source.name == "sanitized"
        if state["scenario"] == "operation-error" and patch:
            raise OSError("simulated unavailable runtime")
        if state["scenario"] == "regression" and patch and payload == b"ordinary":
            return ExecutionResult(0, "wrong\n", "", False)
        if state["scenario"] == "timeout" and patch:
            return ExecutionResult(-1, "", "", True)
        if state["scenario"] == "unclassified" and patch and payload == b"diagnostic":
            return ExecutionResult(-11, "", "", False)
        diagnostic = sanitized and payload == b"diagnostic"
        emit = diagnostic and (not patch or state["scenario"] in ("remaining", "new"))
        if state["scenario"] == "no-baseline":
            emit = False
        if state["scenario"] == "unstable" and not patch and state["calls"] % 3 == 0:
            emit = False
        if emit:
            kind = (
                "heap-use-after-free"
                if patch and state["scenario"] == "new"
                else "heap-buffer-overflow"
            )
            return ExecutionResult(
                1,
                "",
                f"ERROR: AddressSanitizer: {kind}\n"
                " #0 0x1234 in parse /src/source.c:8:1\n"
                " #1 0x1235 in caller /src/source.c:7:1\n",
                False,
            )
        return ExecutionResult(0, "ok\n", "", False)

    monkeypatch.setattr("diffsheriff.pipeline.execute_container", execute)
    return cfg, config_path, state


@pytest.mark.parametrize(
    "scenario,code,status",
    [
        ("fixed", 0, "Fixed"),
        ("remaining", 10, "Incomplete Fix"),
        ("new", 10, "New Issue"),
        ("regression", 20, "Functional Regression"),
        ("no-baseline", 40, None),
        ("unstable", 40, "Inconclusive"),
        ("unclassified", 40, "Inconclusive"),
        ("operation-error", 30, None),
    ],
)
def test_cli_to_report_all_verdicts(tmp_path, pipeline_fixture, scenario, code, status):
    cfg, config_path, state = pipeline_fixture
    state["scenario"] = scenario
    report_path = tmp_path / "report.json"
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config_path),
            "--output-json",
            str(report_path),
            "--artifacts",
            str(tmp_path / "runs"),
        ],
    )
    assert result.exit_code == code, result.output
    report = json.loads(report_path.read_text())
    assert report["exit_code"] == code
    if status:
        assert status in {finding["status"] for finding in report["findings"]}
    if code == 0:
        assert report["analysis_complete"]
        assert report["security_status"] == report["functional_status"] == "PASS"
        assert report["evidence"]["reproducers"]
        bundle = (
            Path(report["evidence"]["run_directory"])
            / report["evidence"]["reproducers"][0]
        )
        replay = json.loads((bundle / "reproducer.json").read_text())
        assert replay["baseline_fail_patch_pass"]
        assert len(replay["runs"]["base"]) == 3
        assert (tmp_path / "regressions").glob("*.json")


def test_hardening_degradation_blocks_pass(tmp_path, pipeline_fixture, monkeypatch):
    cfg, _, _ = pipeline_fixture
    monkeypatch.setattr(
        "diffsheriff.pipeline.inspect_elf_hardening",
        lambda p: HardeningResult(True, p.parent.parent.name != "patch", "full", True),
    )
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 40
    assert summary.hardening_degraded
    assert not summary.analysis_complete


def test_build_failure_retains_evidence(tmp_path, pipeline_fixture, monkeypatch):
    cfg, _, _ = pipeline_fixture

    def fail(*args):
        args[-1]["release"] = {"stderr": "compiler error"}
        raise RuntimeError("build failed")

    monkeypatch.setattr("diffsheriff.pipeline.build_isolated_matrix", fail)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.evidence["builds"]["base"]["release"]["stderr"] == "compiler error"


def test_missing_expected_case_is_configuration_error(tmp_path, pipeline_fixture):
    cfg, _, _ = pipeline_fixture
    (tmp_path / "expected.json").write_text("{}")
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.total_tests_run == 0


def test_generated_regressions_are_loaded(tmp_path, pipeline_fixture):
    from diffsheriff.pipeline import discover_cases

    cfg, _, _ = pipeline_fixture
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 0
    cases, _ = discover_cases(cfg)
    assert any(case["suite"] == "regression" for case in cases)


def test_missing_correlation_does_not_claim_fixed(
    tmp_path, pipeline_fixture, monkeypatch
):
    cfg, _, _ = pipeline_fixture
    monkeypatch.setattr("diffsheriff.pipeline.parse_unified_diff", lambda text: [])
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 40
    assert not summary.security_flaws_fixed


def test_only_designated_baseline_can_pass(tmp_path, pipeline_fixture):
    cfg, _, _ = pipeline_fixture
    cfg = replace(cfg, baseline_signature={**cfg.baseline_signature, "line": 99})
    assert run_pipeline(cfg, tmp_path / "runs").exit_code == 40


def test_minimization_uses_independent_reference(
    tmp_path, pipeline_fixture, monkeypatch
):
    cfg, _, _ = pipeline_fixture
    cfg.test_suites.independent_reference_command = ["reference"]
    real_execute = __import__(
        "diffsheriff.pipeline", fromlist=["execute_container"]
    ).execute_container

    def execute(source, binary, payload, settings):
        return real_execute(
            source,
            binary,
            (
                b"diagnostic"
                if payload not in (b"ordinary", b"boundary") and b"d" in payload
                else payload
            ),
            settings,
        )

    monkeypatch.setattr("diffsheriff.pipeline.execute_container", execute)
    monkeypatch.setattr(
        "diffsheriff.pipeline.run_container",
        lambda *a, **kw: ExecutionResult(
            0, json.dumps({"exit_code": 0, "stdout": "ok\n", "stderr": ""}), "", False
        ),
    )
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 0, summary.notes
    bundle = (
        Path(summary.evidence["run_directory"]) / summary.evidence["reproducers"][0]
    )
    assert (bundle / "minimized.input").read_bytes() == b"d"
    assert (bundle / "original.input").read_bytes() == b"diagnostic"


def test_reproducer_replays_and_detects_tampering(tmp_path, pipeline_fixture):
    from diffsheriff.reproduce import replay

    cfg, _, _ = pipeline_fixture
    summary = run_pipeline(cfg, tmp_path / "runs")
    bundle = (
        Path(summary.evidence["run_directory"]) / summary.evidence["reproducers"][0]
    )
    assert replay(bundle, check_regression=True)
    (bundle / "minimized.input").write_bytes(b"changed")
    with pytest.raises(ValueError, match="input hash"):
        replay(bundle)


def test_timeout_preserves_functional_regression_without_security_claim(
    tmp_path, pipeline_fixture
):
    cfg, _, state = pipeline_fixture
    state["scenario"] = "timeout"
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 20, summary.notes
    assert summary.security_status != "FAIL"
    assert not summary.analysis_complete


def test_functional_regression_has_replay_bundle(tmp_path, pipeline_fixture):
    from diffsheriff.reproduce import replay

    cfg, _, state = pipeline_fixture
    state["scenario"] = "regression"
    summary = run_pipeline(cfg, tmp_path / "runs")
    bundles = [
        Path(summary.evidence["run_directory"]) / item
        for item in summary.evidence["reproducers"]
    ]
    bundle = next(
        item
        for item in bundles
        if json.loads((item / "reproducer.json").read_text())["kind"] == "functional"
    )
    assert replay(bundle)


def test_second_run_consumes_regressions_without_mixing_modes(
    tmp_path, pipeline_fixture
):
    cfg, _, _ = pipeline_fixture
    first = run_pipeline(cfg, tmp_path / "runs")
    second = run_pipeline(cfg, tmp_path / "runs")
    assert first.exit_code == second.exit_code == 0, second.notes
    assert second.total_tests_run > first.total_tests_run


def test_retained_report_failure_preserves_collected_evidence(
    tmp_path, pipeline_fixture, monkeypatch
):
    cfg, _, _ = pipeline_fixture

    def fail_write(*args):
        raise OSError("disk error")

    monkeypatch.setattr("diffsheriff.reporter.ValidationSummary.write_json", fail_write)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.evidence["cases"]
    assert summary.security_flaws_fixed
    assert not summary.analysis_complete


def test_new_patch_findings_are_added_to_regressions(tmp_path, pipeline_fixture):
    cfg, _, state = pipeline_fixture
    state["scenario"] = "new"
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 10
    manifests = [
        json.loads(path.read_text())
        for path in (tmp_path / "regressions").glob("*.json")
    ]
    assert any(
        item["finding_side"] == "patch"
        and item["finding_signature"]["error_type"] == "heap-use-after-free"
        for item in manifests
    )
    assert (
        summary.evidence["execution_settings"]["environment_variables"]["HTTP_PROXY"]
        == ""
    )


def test_late_replay_instability_revokes_fixed_status(
    tmp_path, pipeline_fixture, monkeypatch
):
    import diffsheriff.pipeline as pipeline

    cfg, _, _ = pipeline_fixture
    execute = pipeline.execute_container
    calls = 0

    def unstable(source, binary, payload, settings):
        nonlocal calls
        if (
            source.parent.name == "base"
            and source.name == "sanitized"
            and payload == b"diagnostic"
        ):
            calls += 1
            if calls > 3:
                return ExecutionResult(0, "ok\n", "", False)
        return execute(source, binary, payload, settings)

    monkeypatch.setattr(pipeline, "execute_container", unstable)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 40
    assert not summary.security_flaws_fixed
    assert all(finding.status != "Fixed" for finding in summary.findings)
