"""End-to-end orchestration with synthetic diagnostics, never vulnerable code."""

import json
from dataclasses import replace
from pathlib import Path
import subprocess

from click.testing import CliRunner
import pytest
import yaml

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


def test_late_execution_error_keeps_completed_findings(
    tmp_path, pipeline_fixture, monkeypatch
):
    import diffsheriff.pipeline as pipeline

    cfg, _, state = pipeline_fixture
    state["scenario"] = "regression"
    execute = pipeline.execute_container

    def fail_later(source, binary, payload, settings):
        if payload == b"diagnostic":
            raise OSError("later runtime failure")
        return execute(source, binary, payload, settings)

    monkeypatch.setattr(pipeline, "execute_container", fail_later)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.functional_status == "FAIL"
    assert any(f.status == "Functional Regression" for f in summary.findings)
    assert any("later runtime failure" in note for note in summary.notes)


def test_missing_expected_case_is_configuration_error(tmp_path, pipeline_fixture):
    cfg, _, _ = pipeline_fixture
    (tmp_path / "expected.json").write_text("{}")
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.total_tests_run == 0


@pytest.mark.parametrize("baseline_passes", [True, False])
def test_compare_case_accepts_independently_valid_boundary(
    pipeline_fixture, baseline_passes
):
    import diffsheriff.pipeline as pipeline

    cfg, _, _ = pipeline_fixture
    base = pipeline.observe(
        Path("base/sanitized"), "program", b"boundary", cfg.execution, "base", []
    )
    patch = {**base, "execution": {**base["execution"], "stdout": "wrong\n"}}
    if not baseline_passes:
        base = patch
    case = {
        "suite": "boundary",
        "valid_input": True,
        "expected": {"exit_code": 0, "stdout": "ok\n", "stderr": ""},
    }
    result = pipeline.compare_case(
        case,
        "sanitized",
        {"base": [base] * 3, "patch": [patch] * 3},
        cfg.baseline_signature,
    )
    assert result["regression"] == baseline_passes
    if not baseline_passes:
        assert any("Baseline does not satisfy" in note for note in result["notes"])


@pytest.mark.parametrize("valid_input,code", [(True, 20), (False, 40), (None, 40)])
@pytest.mark.parametrize("security_remains", [False, True])
def test_boundary_regression_uses_independent_validity(
    tmp_path, pipeline_fixture, monkeypatch, valid_input, code, security_remains
):
    import diffsheriff.pipeline as pipeline
    from diffsheriff.reproduce import replay

    _, config_path, state = pipeline_fixture
    if security_remains:
        state["scenario"] = "remaining"
        code = 10
    expected_path = tmp_path / "expected.json"
    expected = json.loads(expected_path.read_text())
    if valid_input is not None:
        expected["boundary/input"]["valid_input"] = valid_input
    expected_path.write_text(json.dumps(expected))
    execute = pipeline.execute_container

    def wrong_boundary(source, binary, payload, settings):
        if source.parent.name == "patch" and payload == b"boundary":
            return ExecutionResult(0, "wrong\n", "", False)
        return execute(source, binary, payload, settings)

    monkeypatch.setattr(pipeline, "execute_container", wrong_boundary)
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
    assert report["functional_status"] == ("FAIL" if valid_input else "PASS")
    assert report["functional_failed"] == (2 if valid_input else 0)
    findings = [f for f in report["findings"] if f["status"] == "Functional Regression"]
    assert len(findings) == (2 if valid_input else 0)
    if valid_input:
        bundles = [
            Path(report["evidence"]["run_directory"]) / p
            for p in report["evidence"]["reproducers"]
        ]
        functional = [
            b
            for b in bundles
            if json.loads((b / "reproducer.json").read_text())["kind"] == "functional"
        ]
        assert len(functional) == 2
        assert all(replay(b) for b in functional)
        cfg = DiffSheriffConfig.from_yaml(config_path)
        cases, _ = pipeline.discover_cases(cfg)
        assert any(
            c["id"].startswith("regression/") and c["valid_input"] for c in cases
        )
        assert run_pipeline(cfg, tmp_path / "second-run").exit_code == code


@pytest.mark.parametrize("value", ["true", 1, None, [], {}])
def test_input_validity_must_be_boolean(tmp_path, pipeline_fixture, value):
    cfg, _, _ = pipeline_fixture
    path = tmp_path / "expected.json"
    expected = json.loads(path.read_text())
    expected["boundary/input"]["valid_input"] = value
    path.write_text(json.dumps(expected))
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 30
    assert summary.total_tests_run == 0
    assert any("valid_input must be a boolean" in note for note in summary.notes)


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


@pytest.mark.parametrize(
    "header,scenario,code",
    [
        ("int caller(char *input) {", "fixed", 0),
        ("", "fixed", 40),
        ("int unrelated(char *input) {", "fixed", 40),
        ("int caller(char *input) {", "remaining", 10),
        ("int caller(char *input) {", "new", 10),
        ("int caller(char *input) {", "regression", 20),
        ("int caller(char *input) {", "unstable", 40),
        ("int caller(char *input) {", "no-baseline", 40),
        ("int caller(char *input) {", "operation-error", 30),
        ("int caller(char *input) {", "hardening", 40),
    ],
)
def test_cli_insertion_only_patch_requires_runtime_function_evidence(
    tmp_path, pipeline_fixture, monkeypatch, header, scenario, code
):
    from diffsheriff.reproduce import replay
    import diffsheriff.pipeline as pipeline

    _, config_path, state = pipeline_fixture
    state["scenario"] = scenario
    execute = pipeline.execute_container

    def shifted_patch_frames(source, binary, payload, settings):
        result = execute(source, binary, payload, settings)
        if source.parent.name == "patch":
            result = replace(
                result,
                stderr=result.stderr.replace(":8:1", ":9:1").replace(":7:1", ":8:1"),
            )
        return result

    monkeypatch.setattr(pipeline, "execute_container", shifted_patch_frames)
    if scenario == "hardening":
        monkeypatch.setattr(
            pipeline,
            "inspect_elf_hardening",
            lambda p: HardeningResult(True, False, "full", True),
        )
    diff = (
        f"--- a/source.c\n+++ b/source.c\n@@ -6,0 +7 @@ {header}\n"
        "+    if (!input) return 0;\n"
    )
    monkeypatch.setattr(
        "diffsheriff.pipeline.subprocess.run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, diff.encode(), b""),
    )
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
    if code == 0:
        finding = next(f for f in report["findings"] if f["status"] == "Fixed")
        assert finding["correlation_type"] == "Insertion in observed function"
        assert finding["evidence"]["correlation"]["hunk"]["old_lines"] == []
        assert report["analysis_complete"]
        bundle = (
            Path(report["evidence"]["run_directory"])
            / report["evidence"]["reproducers"][0]
        )
        assert replay(bundle, check_regression=True)
        cfg = DiffSheriffConfig.from_yaml(config_path)
        assert run_pipeline(cfg, tmp_path / "second-run").exit_code == 0
    elif code == 40 and scenario != "hardening":
        assert report["security_flaws_fixed"] == 0
    if scenario in {"remaining", "new"}:
        status = "Incomplete Fix" if scenario == "remaining" else "New Issue"
        finding = next(f for f in report["findings"] if f["status"] == status)
        assert not finding["evidence"]["correlation"]["is_correlated"]


def test_insertion_requires_matching_function_evidence_in_every_replay(
    tmp_path, pipeline_fixture, monkeypatch
):
    import diffsheriff.pipeline as pipeline

    cfg, _, _ = pipeline_fixture
    diff = (
        b"--- a/source.c\n+++ b/source.c\n"
        b"@@ -6,0 +7 @@ int caller(char *input) {\n+guard();\n"
    )
    monkeypatch.setattr(
        pipeline.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a, 0, diff, b""),
    )
    execute = pipeline.execute_container
    calls = 0

    def changing_caller(source, binary, payload, settings):
        nonlocal calls
        result = execute(source, binary, payload, settings)
        if (
            source.parent.name == "base"
            and source.name == "sanitized"
            and payload == b"diagnostic"
        ):
            calls += 1
            if calls % 3 == 2:
                return replace(
                    result, stderr=result.stderr.replace("in caller", "in unrelated")
                )
        return result

    monkeypatch.setattr(pipeline, "execute_container", changing_caller)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 40
    assert summary.security_flaws_fixed == 0


def test_only_designated_baseline_can_pass(tmp_path, pipeline_fixture):
    cfg, _, _ = pipeline_fixture
    cfg = replace(cfg, baseline_signature={**cfg.baseline_signature, "line": 99})
    assert run_pipeline(cfg, tmp_path / "runs").exit_code == 40


@pytest.mark.parametrize("with_reference", [False, True])
def test_security_minimization_and_regression_expectations(
    tmp_path, pipeline_fixture, monkeypatch, with_reference
):
    from diffsheriff.pipeline import discover_cases
    from diffsheriff.reproduce import replay

    cfg, config_path, _ = pipeline_fixture
    if with_reference:
        cfg.test_suites.independent_reference_command = ["reference"]
        config = yaml.safe_load(config_path.read_text())
        config["test_suites"]["independent_reference_command"] = ["reference"]
        config_path.write_text(yaml.safe_dump(config))
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
    assert result.exit_code == (0 if with_reference else 40), result.output
    report = json.loads(report_path.read_text())
    bundle = (
        Path(report["evidence"]["run_directory"]) / report["evidence"]["reproducers"][0]
    )
    assert (bundle / "minimized.input").read_bytes() == b"d"
    assert (bundle / "original.input").read_bytes() == b"diagnostic"
    metadata = json.loads((bundle / "reproducer.json").read_text())
    assert metadata["stable"]
    assert len(metadata["runs"]["base"]) == 3
    assert bool(metadata["expected"]) == with_reference
    assert metadata["baseline_fail_patch_pass"] == with_reference
    assert replay(bundle)
    assert replay(bundle, check_regression=True) == with_reference
    generated = [c for c in discover_cases(cfg)[0] if c["suite"] == "regression"]
    assert generated
    assert {c["payload"] for c in generated} == (
        {b"d"} if with_reference else {b"d", b"diagnostic"}
    )
    diagnostic = [c for c in generated if c["diagnostic_only"]]
    assert bool(diagnostic) == (not with_reference)
    assert all(c["expected"] is None and c["payload"] == b"d" for c in diagnostic)
    second = run_pipeline(cfg, tmp_path / "second-run")
    assert second.exit_code == (0 if with_reference else 40)
    assert any(
        c["id"].startswith("regression/")
        and c["sha256"] == metadata["minimized_sha256"]
        for c in second.evidence["cases"]
    )
    if not with_reference:
        cfg.test_suites.independent_reference_command = ["reference"]
        assert run_pipeline(cfg, tmp_path / "with-expectation").exit_code == 0


@pytest.mark.parametrize(
    "rejection",
    [
        "timed_out",
        "resource_limited",
        "output_limited",
        "signal",
        "location",
        "unstable",
    ],
)
def test_security_minimization_rejects_different_or_limited_failures(
    tmp_path, pipeline_fixture, monkeypatch, rejection
):
    import diffsheriff.pipeline as pipeline

    cfg, _, _ = pipeline_fixture
    execute = pipeline.execute_container
    candidates = []

    def reduced(source, binary, payload, settings):
        if (
            source.name == "sanitized"
            and source.parent.name == "base"
            and payload not in (b"ordinary", b"boundary", b"diagnostic")
        ):
            candidates.append(payload)
            result = execute(source, binary, b"diagnostic", settings)
            if rejection in {"timed_out", "resource_limited", "output_limited"}:
                return replace(result, **{rejection: True})
            if rejection == "signal":
                return ExecutionResult(-11, "", "", False)
            if rejection == "location":
                return replace(result, stderr=result.stderr.replace(":8:1", ":88:1"))
            if len(candidates) % 3 == 0:
                return ExecutionResult(0, "ok\n", "", False)
            return result
        return execute(source, binary, payload, settings)

    monkeypatch.setattr(pipeline, "execute_container", reduced)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 0, summary.notes
    assert candidates, "Unknown reduced candidates must actually be executed"
    bundle = (
        Path(summary.evidence["run_directory"]) / summary.evidence["reproducers"][0]
    )
    assert (bundle / "minimized.input").read_bytes() == b"diagnostic"


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


@pytest.mark.parametrize(
    "patch_mode,new_kind,unstable,status",
    [
        ("sanitized", False, False, "Incomplete Fix"),
        ("release", False, False, "New Issue"),
        ("sanitized", True, False, "New Issue"),
        ("sanitized", False, True, "New Issue"),
    ],
)
def test_known_baseline_identity_is_shared_only_within_mode(
    tmp_path, pipeline_fixture, monkeypatch, patch_mode, new_kind, unstable, status
):
    cfg, _, state = pipeline_fixture
    if unstable:
        state["scenario"] = "unstable"
    import diffsheriff.pipeline as pipeline

    execute = pipeline.execute_container

    def alternate(source, binary, payload, settings):
        if (
            source.parent.name == "patch"
            and source.name == patch_mode
            and payload == b"ordinary"
        ):
            kind = "heap-use-after-free" if new_kind else "heap-buffer-overflow"
            return ExecutionResult(
                1,
                "",
                f"ERROR: AddressSanitizer: {kind}\n"
                " #0 0x1234 in parse /src/source.c:8:1\n",
                False,
            )
        return execute(source, binary, payload, settings)

    monkeypatch.setattr(pipeline, "execute_container", alternate)
    summary = run_pipeline(cfg, tmp_path / "runs")
    assert summary.exit_code == 10
    # This input is processed before the separate baseline trigger.
    findings = [f for f in summary.findings if f.triggering_input == "valid/input"]
    assert status in {f.status for f in findings}
    assert ("New Issue" if status == "Incomplete Fix" else "Incomplete Fix") not in {
        f.status for f in findings
    }
    assert summary.evidence["baseline_identity_modes"] == (
        [] if unstable else ["sanitized"]
    )
    for finding in findings:
        record = summary.evidence["cases"][finding.evidence["case_index"]]
        assert record["id"] == finding.triggering_input
        assert record["mode"] == finding.evidence["mode"]


def test_cli_exports_and_restores_generated_regressions(tmp_path, pipeline_fixture):
    cfg, config_path, _ = pipeline_fixture
    retained = tmp_path / "retained"
    args = [
        "--config",
        str(config_path),
        "--output-json",
        str(tmp_path / "report.json"),
        "--artifacts",
        str(tmp_path / "runs"),
        "--export-regressions",
        str(retained),
    ]
    first = CliRunner().invoke(main, args)
    assert first.exit_code == 0, first.output
    first_report = json.loads((tmp_path / "report.json").read_text())
    for path in (tmp_path / "regressions").iterdir():
        path.unlink()
    second = CliRunner().invoke(main, args + ["--regressions-from", str(retained)])
    assert second.exit_code == 0, second.output
    second_report = json.loads((tmp_path / "report.json").read_text())
    assert second_report["total_tests_run"] > first_report["total_tests_run"]
    assert list(retained.glob("*.json"))


@pytest.mark.parametrize(
    "scenario,code",
    [
        ("remaining", 10),
        ("regression", 20),
        ("no-baseline", 40),
        ("operation-error", 30),
    ],
)
def test_cli_export_preserves_failure_exit_codes(
    tmp_path, pipeline_fixture, scenario, code
):
    _, config_path, state = pipeline_fixture
    state["scenario"] = scenario
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config_path),
            "--output-json",
            str(tmp_path / "report.json"),
            "--artifacts",
            str(tmp_path / "runs"),
            "--export-regressions",
            str(tmp_path / "retained"),
        ],
    )
    assert result.exit_code == code, result.output
    assert json.loads((tmp_path / "report.json").read_text())["exit_code"] == code


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
