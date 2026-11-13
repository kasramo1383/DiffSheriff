"""Explicit source -> build -> execute -> compare -> reproduce pipeline."""

from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from diffsheriff.builder import build_isolated_matrix, compute_sha256
from diffsheriff.config import ConfigError, relative_path
from diffsheriff.correlator import (
    correlate_stack_to_diff,
    finding_signature,
    parse_unified_diff,
)
from diffsheriff.hardening import compare_hardening, inspect_elf_hardening
from diffsheriff.minimizer import FailureInvariant, ddmin
from diffsheriff.reporter import (
    FindingReport,
    ValidationSummary,
    resolve_priority_exit_code,
)
from diffsheriff.runner import execute_container, resolve_image, run_container
from diffsheriff.triage import triage_execution_result


def empty_summary(name):
    return ValidationSummary(
        name,
        40,
        "INCONCLUSIVE",
        0,
        0,
        0,
        0,
        0,
        False,
        [],
        analysis_complete=False,
        notes=[],
    )


def expected_result(value):
    if not isinstance(value, dict) or set(value) != {"exit_code", "stdout", "stderr"}:
        raise ConfigError(
            "Each expectation needs exactly exit_code, stdout, and stderr"
        )
    if type(value["exit_code"]) is not int or not 0 <= value["exit_code"] <= 255:
        raise ConfigError("Expected exit_code must be an integer from 0 to 255")
    if not all(isinstance(value[key], str) for key in ("stdout", "stderr")):
        raise ConfigError(
            "Expected stdout and stderr must be strings (Latin-1 byte mapping)"
        )
    return value


def contained_file(root, name):
    relative_path(name, "input path")
    path = root / name
    if (
        not path.is_file()
        or path.is_symlink()
        or not path.resolve().is_relative_to(root.resolve())
    ):
        raise ConfigError(f"Expected a regular file within {root}: {name}")
    return path


def discover_cases(cfg):
    """Read independent expectations once, before any target build or execution."""
    root = cfg.config_directory
    manifest = contained_file(root, cfg.test_suites.expectations)
    expected = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(expected, dict):
        raise ConfigError("expectations must map suite/path to expected results")
    cases = []
    for suite in ("valid", "boundary", "malicious"):
        directory = root / getattr(cfg.test_suites, suite + "_directory")
        if not directory.is_dir() or not directory.resolve().is_relative_to(root):
            raise ConfigError(f"Missing or uncontained {suite} suite: {directory}")
        files = sorted(p for p in directory.rglob("*") if p.is_file())
        if not files:
            raise ConfigError(f"The {suite} suite is empty")
        for path in files:
            path = contained_file(root, path.relative_to(root).as_posix())
            key = suite + "/" + path.relative_to(directory).as_posix()
            if key not in expected:
                raise ConfigError(f"No independent expectation for {key}")
            if not isinstance(expected[key], dict):
                raise ConfigError(f"Expectation for {key} must be a mapping")
            expectation = dict(expected[key])
            valid_input = expectation.pop("valid_input", suite == "valid")
            if type(valid_input) is not bool:
                raise ConfigError("valid_input must be a boolean")
            payload = path.read_bytes()
            cases.append(
                {
                    "id": key,
                    "suite": suite,
                    "payload": payload,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "expected": expected_result(expectation),
                    "valid_input": valid_input,
                }
            )
    if set(expected) != {case["id"] for case in cases}:
        raise ConfigError("Expectation keys must match the discovered suite exactly")
    regressions = root / cfg.test_suites.regression_directory
    if regressions.exists():
        if not regressions.resolve().is_relative_to(root):
            raise ConfigError(
                "Regression directory escapes the configuration directory"
            )
        for manifest_path in sorted(regressions.glob("*.json")):
            item = json.loads(
                contained_file(
                    root, manifest_path.relative_to(root).as_posix()
                ).read_text(encoding="utf-8")
            )
            input_path = contained_file(regressions, item["input"])
            payload = input_path.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            if digest != item["sha256"]:
                raise ConfigError("Generated regression input hash does not match")
            if item["base_ref"] != cfg.base_ref:
                continue
            valid_input = item.get("valid_input", item.get("kind") == "functional")
            if type(valid_input) is not bool:
                raise ConfigError("Generated regression valid_input must be a boolean")
            cases.append(
                {
                    "id": "regression/" + manifest_path.stem,
                    "suite": (
                        "valid" if item.get("kind") == "functional" else "regression"
                    ),
                    "payload": payload,
                    "sha256": digest,
                    "expected": expected_result(item["expected"]),
                    "valid_input": valid_input,
                    "baseline_signature": item["signature"],
                    "baseline_mode": item["mode"],
                }
            )
    return cases, compute_sha256(manifest)


def observe(source, binary, payload, settings, side, hunks):
    result = execute_container(source, binary, payload, settings)
    crash = triage_execution_result(
        result.exit_code,
        result.stdout,
        result.stderr,
        result.timed_out,
        result.resource_limited,
        result.output_limited,
    )
    return {
        "execution": asdict(result),
        "triage": asdict(crash),
        "signature": finding_signature(crash, side, hunks),
        "correlation": asdict(correlate_stack_to_diff(crash.stack_trace, hunks, side)),
    }


def matches_expected(observation, expected):
    execution = observation["execution"]
    return (
        not any(
            execution[key]
            for key in ("timed_out", "resource_limited", "output_limited")
        )
        and not observation["triage"]["is_crash"]
        and all(execution[key] == expected[key] for key in expected)
    )


def stable_observations(observations):
    first = observations[0]
    if first["signature"]:
        return all(
            item["signature"] == first["signature"]
            and not any(
                item["execution"][key]
                for key in ("timed_out", "resource_limited", "output_limited")
            )
            for item in observations
        )
    keys = (
        "exit_code",
        "stdout",
        "stderr",
        "timed_out",
        "resource_limited",
        "output_limited",
    )
    return all(
        item["signature"] is None
        and all(item["execution"][key] == first["execution"][key] for key in keys)
        for item in observations
    )


def compare_case(case, mode, runs, baseline_signature):
    """Compare only corresponding modes, retaining independent functional evidence."""
    base, patch = runs["base"][0], runs["patch"][0]
    stable = all(stable_observations(runs[side]) for side in ("base", "patch"))
    base_ok = all(matches_expected(item, case["expected"]) for item in runs["base"])
    patch_ok = all(matches_expected(item, case["expected"]) for item in runs["patch"])
    base_sig, patch_sig = base["signature"], patch["signature"]
    baseline_seen = stable and base_sig == baseline_signature
    findings = []
    notes = []
    regression = stable and case["valid_input"] and base_ok and not patch_ok
    vulnerability = stable and bool(patch_sig)
    if not stable:
        notes.append("Replay observations are unstable")
    if regression:
        findings.append(
            (
                "Functional Regression",
                patch,
                "Independent expected behavior passed on baseline and failed on patch",
            )
        )
    if stable and patch_sig:
        status = "Incomplete Fix" if patch_sig == base_sig else "New Issue"
        findings.append(
            (
                status,
                patch,
                "Confirmed diagnostic on patch; causation requires "
                "the recorded correlation evidence",
            )
        )
        if not patch["correlation"]["is_correlated"]:
            notes.append("Patch finding is confirmed, but attribution is inconclusive")
    if stable and base_sig and not patch_sig:
        if patch_ok and base["correlation"]["is_correlated"]:
            findings.append(
                (
                    "Fixed",
                    base,
                    "Baseline diagnostic absent in corresponding patch replays "
                    "within this suite",
                )
            )
        else:
            notes.append(
                "Baseline diagnostic disappeared without sufficient expected "
                "behavior or patch correlation"
            )
    for side, first in (("base", base), ("patch", patch)):
        execution = first["execution"]
        if any(
            execution[key]
            for key in ("timed_out", "resource_limited", "output_limited")
        ):
            notes.append(f"{side} execution reached a resource or output limit")
        if first["triage"]["is_crash"] and not first["signature"]:
            notes.append(
                f"{side} abnormal termination has no confirmed source signature"
            )
    if case["valid_input"] and not base_ok:
        notes.append(
            "Baseline does not satisfy the independent valid-input expectation"
        )
    if not patch_ok and not vulnerability and not regression:
        notes.append("Patched behavior does not satisfy the independent expectation")
    if (
        case.get("baseline_signature")
        and case.get("baseline_mode") == mode
        and base_sig != case["baseline_signature"]
    ):
        notes.append(
            "Generated regression did not reproduce its expected baseline signature"
        )
    if notes:
        findings.append(("Inconclusive", patch, "; ".join(notes)))
    return {
        "findings": findings,
        "notes": notes,
        "regression": regression,
        "vulnerability": vulnerability,
        "baseline_seen": baseline_seen,
        "base_ok": base_ok,
        "patch_ok": patch_ok,
        "stable": stable,
    }


def functional_failure(runs, expected, mismatch):
    return all(matches_expected(item, expected) for item in runs["base"]) and all(
        item["triage"]["error_type"] == mismatch["error_type"]
        and {key: item["execution"][key] for key in mismatch["limits"]}
        == mismatch["limits"]
        and sorted(key for key in expected if item["execution"][key] != expected[key])
        == mismatch["fields"]
        for item in runs["patch"]
    )


def record_reproducer(
    case,
    mode,
    side,
    observation,
    artifacts,
    settings,
    hunks,
    cfg,
    run_directory,
    known_expectations,
    evidence,
    original_runs,
    functional=False,
):
    """Reduce supplied cases only; never generate a new trigger or bypass."""
    signature = observation["signature"]
    mismatch = {
        "fields": sorted(
            key
            for key in case["expected"]
            if observation["execution"][key] != case["expected"][key]
        ),
        "error_type": observation["triage"]["error_type"],
        "limits": {
            key: observation["execution"][key]
            for key in ("timed_out", "resource_limited", "output_limited")
        },
    }
    identity = (
        {"error_type": "functional-regression", "mismatch": mismatch}
        if functional
        else signature
    )
    source, binary = artifacts[side][mode]
    location = json.dumps(identity, sort_keys=True)
    replay_log = []

    def oracle(payload):
        digest = hashlib.sha256(payload).hexdigest()
        if (
            functional
            and digest not in known_expectations
            and not cfg.test_suites.independent_reference_command
        ):
            return False, "", ""
        if (
            digest not in known_expectations
            and cfg.test_suites.independent_reference_command
        ):
            reference = run_container(
                cfg.config_directory,
                cfg.test_suites.independent_reference_command,
                settings,
                payload=payload,
            )
            if (
                reference.exit_code
                or reference.timed_out
                or reference.output_limited
                or reference.resource_limited
            ):
                raise RuntimeError(
                    "Independent reference command failed during minimization"
                )
            known_expectations[digest] = expected_result(json.loads(reference.stdout))
        observations = [
            observe(source, binary, payload, settings, side, hunks) for _ in range(3)
        ]
        replay_log.append(
            {
                "input_sha256": hashlib.sha256(payload).hexdigest(),
                "observations": observations,
            }
        )
        if functional:
            baseline = [
                observe(*artifacts["base"][mode], payload, settings, "base", hunks)
                for _ in range(3)
            ]
            replay_log[-1]["baseline"] = baseline
            preserved = functional_failure(
                {"base": baseline, "patch": observations},
                known_expectations[digest],
                mismatch,
            )
        else:
            preserved = stable_observations(observations) and all(
                item["signature"] == signature for item in observations
            )
        return preserved, identity["error_type"], location

    minimization_stable = True
    try:
        minimized = ddmin(
            case["payload"], oracle, FailureInvariant(identity["error_type"], location)
        )
    except ValueError as error:
        if str(error) != "Initial payload does not preserve the failure invariant":
            raise
        minimized, minimization_stable = case["payload"], False
    digest = hashlib.sha256(minimized).hexdigest()
    case_id = hashlib.sha256((case["id"] + mode + side).encode()).hexdigest()[:20]
    bundle = run_directory / "reproducers" / case_id
    bundle.mkdir(parents=True)
    (bundle / "original.input").write_bytes(case["payload"])
    (bundle / "minimized.input").write_bytes(minimized)
    runs = {
        version: [
            observe(*artifacts[version][mode], minimized, settings, version, hunks)
            for _ in range(3)
        ]
        for version in ("base", "patch")
    }
    expected = known_expectations.get(digest)
    reproduced = minimization_stable and (
        functional_failure(runs, expected, mismatch)
        if functional
        else stable_observations(runs[side])
        and all(item["signature"] == signature for item in runs[side])
    )
    corrected = expected is not None and all(
        matches_expected(item, expected) for item in runs["patch"]
    )
    stable = reproduced and all(stable_observations(items) for items in runs.values())
    metadata = {
        "case": case["id"],
        "mode": mode,
        "finding_side": side,
        "signature": signature,
        "kind": "functional" if functional else "security",
        "functional_mismatch": mismatch if functional else [],
        "original_sha256": case["sha256"],
        "minimized_sha256": digest,
        "expected": expected,
        "original_expected": case["expected"],
        "valid_input": case["valid_input"],
        "regression_input": "original.input" if expected is None else "minimized.input",
        "settings": asdict(settings),
        "runs": runs,
        "minimization_log": replay_log,
        "reproduced": reproduced,
        "stable": stable,
        "minimization_scope": (
            "reference oracle"
            if cfg.test_suites.independent_reference_command
            else (
                "approved corpus payloads only"
                if functional
                else "diagnostic invariant"
            )
        ),
        "baseline_fail_patch_pass": side == "base" and stable and corrected,
        "versions": {"base": cfg.base_ref, "patch": cfg.patch_ref},
        "artifacts": {
            version: {
                "source": artifacts[version][mode][0]
                .relative_to(run_directory)
                .as_posix(),
                "binary": artifacts[version][mode][1],
                "sha256": compute_sha256(
                    artifacts[version][mode][0] / artifacts[version][mode][1]
                ),
            }
            for version in ("base", "patch")
        },
        "replay_command": [
            "python",
            "-m",
            "diffsheriff.reproduce",
            bundle.relative_to(run_directory).as_posix(),
        ],
    }
    (bundle / "reproducer.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    evidence["reproducers"].append(bundle.relative_to(run_directory).as_posix())
    if stable:
        # Unknown functional behavior must never become a generated expectation.
        regression_payload = case["payload"] if expected is None else minimized
        regression_digest = hashlib.sha256(regression_payload).hexdigest()
        regression_runs = original_runs if expected is None else runs
        regressions = cfg.config_directory / cfg.test_suites.regression_directory
        if not regressions.resolve().is_relative_to(cfg.config_directory):
            raise ConfigError(
                "Regression directory escapes the configuration directory"
            )
        regressions.mkdir(parents=True, exist_ok=True)
        key = hashlib.sha256(
            (cfg.base_ref + location + regression_digest + mode).encode()
        ).hexdigest()
        input_path = regressions / (key + ".input")
        manifest_path = regressions / (key + ".json")
        for path in (input_path, manifest_path):
            if path.is_symlink():
                raise ConfigError(
                    "Refusing to replace a symlink in generated regressions"
                )
        input_path.write_bytes(regression_payload)
        manifest_path.write_text(
            json.dumps(
                {
                    "input": input_path.name,
                    "sha256": regression_digest,
                    "base_ref": cfg.base_ref,
                    "signature": regression_runs["base"][0]["signature"],
                    "finding_signature": signature,
                    "finding_side": side,
                    "mode": mode,
                    "kind": "functional" if functional else "security",
                    "valid_input": case["valid_input"],
                    "expected": case["expected"] if expected is None else expected,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return (bundle.relative_to(run_directory) / "minimized.input").as_posix(), stable


def run_pipeline(cfg, artifact_root):
    summary = empty_summary(cfg.target_name)
    evidence = summary.evidence
    failed = vulnerability = regression = baseline_seen = False
    incomplete = False
    try:
        cases, manifest_hash = discover_cases(cfg)
        artifact_root.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(prefix="run-", dir=artifact_root)).resolve()
        evidence.update(
            run_directory=str(directory),
            versions={"base": cfg.base_ref, "patch": cfg.patch_ref},
            configuration={
                **asdict(cfg),
                "repository_path": str(cfg.repository_path),
                "config_directory": str(cfg.config_directory),
            },
            oracle={"sha256": manifest_hash, "provenance": cfg.test_suites.provenance},
            builds={},
            cases=[],
            reproducers=[],
        )
        (directory / "inputs").mkdir()
        for case in cases:
            case["input_file"] = "inputs/" + case["sha256"] + ".input"
            (directory / case["input_file"]).write_bytes(case["payload"])
        # Docker's client proxy defaults must not silently alter recorded runs.
        environment = dict.fromkeys(
            (
                "HTTP_PROXY",
                "HTTPS_PROXY",
                "ALL_PROXY",
                "NO_PROXY",
                "http_proxy",
                "https_proxy",
                "all_proxy",
                "no_proxy",
            ),
            "",
        )
        environment.update(cfg.execution.environment_variables)
        settings = replace(
            cfg.execution,
            image=resolve_image(cfg.execution.image),
            environment_variables=environment,
        )
        evidence["execution_settings"] = asdict(settings)
        diff = subprocess.run(
            [
                "git",
                "-C",
                str(cfg.repository_path),
                "-c",
                "core.quotePath=false",
                "diff",
                "--no-ext-diff",
                "--no-textconv",
                "--find-renames",
                "--unified=0",
                cfg.base_ref,
                cfg.patch_ref,
                "--",
            ],
            capture_output=True,
            check=True,
            timeout=30,
        )
        diff_text = diff.stdout.decode("utf-8")
        (directory / "patch.diff").write_text(diff_text, encoding="utf-8")
        hunks = parse_unified_diff(diff_text)
        artifacts = {}
        for side, commit in (("base", cfg.base_ref), ("patch", cfg.patch_ref)):
            build_directory = directory / side
            build_directory.mkdir()
            evidence["builds"][side] = {}
            artifacts[side] = build_isolated_matrix(
                cfg.repository_path,
                commit,
                build_directory,
                cfg.build,
                settings,
                evidence["builds"][side],
            )
        hardening = {}
        for side in artifacts:
            for mode in artifacts[side]:
                source, binary = artifacts[side][mode]
                inspected = inspect_elf_hardening(source / binary)
                if mode == "release":
                    hardening[side] = inspected
        summary.hardening_degraded, warnings = compare_hardening(
            hardening["base"], hardening["patch"]
        )
        evidence["hardening"] = {
            side: asdict(value) for side, value in hardening.items()
        }
        for side, value in hardening.items():
            for flag in ("nx", "pie", "canary"):
                if getattr(cfg.hardening, "enforce_" + flag) and not getattr(
                    value, flag
                ):
                    warnings.append(f"{side}: required {flag} protection missing")
            if ["none", "partial", "full"].index(value.relro) < [
                "none",
                "partial",
                "full",
            ].index(cfg.hardening.min_relro):
                warnings.append(f"{side}: RELRO is below the configured minimum")
        summary.notes.extend(warnings)
        incomplete |= bool(warnings)
        known_expectations = {}
        for case in cases:
            if (
                case["sha256"] in known_expectations
                and known_expectations[case["sha256"]] != case["expected"]
            ):
                raise ConfigError(
                    "Identical payloads have conflicting independent expectations"
                )
            known_expectations[case["sha256"]] = case["expected"]
        for case in cases:
            for mode in ("release", "sanitized"):
                runs = {}
                record = {key: value for key, value in case.items() if key != "payload"}
                record.update(mode=mode, runs=runs)
                evidence["cases"].append(record)
                for side in ("base", "patch"):
                    runs[side] = []
                    for _ in range(3):
                        runs[side].append(
                            observe(
                                *artifacts[side][mode],
                                case["payload"],
                                settings,
                                side,
                                hunks,
                            )
                        )
                        summary.total_tests_run += 1
                decision = compare_case(case, mode, runs, cfg.baseline_signature)
                baseline_seen |= decision["baseline_seen"]
                vulnerability |= decision["vulnerability"]
                regression |= decision["regression"]
                incomplete |= bool(decision["notes"])
                if case["valid_input"]:
                    summary.functional_passed += int(
                        decision["base_ok"] and decision["patch_ok"]
                    )
                    summary.functional_failed += int(
                        not (decision["base_ok"] and decision["patch_ok"])
                    )
                for status, observation, reason in decision["findings"]:
                    finding = FindingReport(
                        f"finding-{len(summary.findings) + 1}",
                        status,
                        observation["triage"]["error_type"],
                        observation["triage"]["detection_mechanism"],
                        case["id"],
                        None,
                        observation["correlation"]["correlation_type"],
                        decision["stable"],
                        {
                            "mode": mode,
                            "signature": observation["signature"],
                            "reason": reason,
                            "case_index": len(evidence["cases"]) - 1,
                            "correlation": observation["correlation"],
                        },
                    )
                    summary.findings.append(finding)
                if decision["stable"]:
                    for side in ("base", "patch"):
                        observation = runs[side][0]
                        functional = (
                            side == "patch"
                            and decision["regression"]
                            and not observation["signature"]
                        )
                        if observation["signature"] or functional:
                            minimized, stable = record_reproducer(
                                case,
                                mode,
                                side,
                                observation,
                                artifacts,
                                settings,
                                hunks,
                                cfg,
                                directory,
                                known_expectations,
                                evidence,
                                runs,
                                functional,
                            )
                            incomplete |= not stable
                            if not stable:
                                summary.notes.append(
                                    f"Unstable reproducer: {case['id']} {mode} {side}"
                                )
                            for finding in summary.findings:
                                if (
                                    finding.triggering_input == case["id"]
                                    and finding.evidence["mode"] == mode
                                    and finding.evidence["signature"]
                                    == observation["signature"]
                                ):
                                    finding.minimized_input = minimized
                                    finding.reproduced_cleanly = stable
                                    if not stable:
                                        finding.status = "Inconclusive"
                                        finding.evidence["reason"] = (
                                            "Later reproducer replays were unstable"
                                        )
        vulnerability = any(
            f.status in {"Incomplete Fix", "New Issue"} and f.reproduced_cleanly
            for f in summary.findings
        )
        regression = any(
            f.status == "Functional Regression" and f.reproduced_cleanly
            for f in summary.findings
        )
        if not baseline_seen:
            summary.notes.append(
                "Designated baseline flaw was not reproduced "
                "with stable source evidence"
            )
            incomplete = True
    except Exception as error:
        failed = True
        incomplete = True
        summary.notes.append(f"{type(error).__name__}: {error}")
    summary.security_flaws_fixed = sum(
        finding.status == "Fixed" for finding in summary.findings
    )
    summary.security_flaws_lingering = sum(
        finding.status in {"Incomplete Fix", "New Issue"}
        for finding in summary.findings
    )
    summary.analysis_complete = not incomplete
    summary.security_status = (
        "FAIL"
        if vulnerability
        else "PASS" if baseline_seen and not incomplete else "INCONCLUSIVE"
    )
    summary.functional_status = (
        "FAIL"
        if regression
        else (
            "PASS"
            if summary.functional_passed
            and not summary.functional_failed
            and not failed
            else "INCONCLUSIVE"
        )
    )
    summary.exit_code, summary.verdict = resolve_priority_exit_code(
        failed, vulnerability, regression, incomplete
    )
    if evidence.get("run_directory"):
        try:
            summary.write_json(Path(evidence["run_directory"]) / "report.json")
        except OSError as error:
            summary.exit_code, summary.verdict = 30, "BUILD_OR_CONFIG_ERROR"
            summary.analysis_complete = False
            summary.notes.append(f"Cannot write retained report: {error}")
    return summary
