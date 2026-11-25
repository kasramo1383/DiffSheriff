# Engineer 4 presentation guide

**Owner:** Kasra Montazeri (402106575)

**Topic:** Configuration, pipeline orchestration, CLI/reports, target scenarios,
CI, and delivery integration.

Your job is to connect the other three engineers' components into one command
that a clean checkout can run. Explain the schema before showing a target result.

## 1. The story to tell

The YAML file is an executable contract. It names the target/language, exact base
and patch hashes, build commands and binary paths, execution limits, hardening
baseline, test directories/expectations, independent reference behavior, and
minimization limits. `config.py` rejects malformed or unsafe values before
Docker or Git work begins.

`run_pipeline` then discovers supplied cases, computes the expectation manifest
hash, writes durable inputs, obtains the actual Git diff, builds both commits in
both modes, inspects hardening, runs three observations, compares
findings/regressions, records reproducers, and writes a `ValidationSummary`.

The CLI catches setup/tool errors, always tries to write JSON, prints a readable
summary, and exits with one prioritized code. CI runs unit tests, a native smoke
test, and the optional target-patch gate without pretending a skipped job passed.

## 2. Exact code to know

### `diffsheriff/config.py`

The exact-commit rule is fail-closed:

```python
for key in ("base_ref", "patch_ref"):
    value = _string(target.get(key), f"target.{key}")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise ConfigError(f"target.{key} must be a full Git commit hash")
```

`relative_path` rejects absolute paths, traversal (`..`), backslashes, reserved
`.git`/`.diffsheriff` locations, and empty values. Changing `target.patch_ref`
changes which approved snapshot is compared. Changing a test expectation changes
the functional contract, so that belongs only in an instructor-reviewed target
configuration.

### `diffsheriff/pipeline.py`

`observe` is the handoff point (the complete code is in Engineer 2's guide).
`compare_case` decides among a fixed vocabulary:

```python
regression = stable and case["valid_input"] and base_ok and not patch_ok
vulnerability = stable and bool(patch_sig)
```

The three corresponding modes are compared separately. A patch signature equal to
the baseline is an incomplete fix; a valid-input base-pass/patch-fail is a
functional regression. Unstable replays add an incomplete-analysis reason.

### `diffsheriff/reporter.py` and `cli.py`

Exit code choice is centralized:

```python
if build_failed:
    return 30, "BUILD_OR_CONFIG_ERROR"
if vuln_detected:
    return 10, "VULN_REMAINS_OR_NEW_ISSUE"
if regression_detected:
    return 20, "FUNC_REGRESSION"
if is_inconclusive:
    return 40, "INCONCLUSIVE"
return 0, "PASS"
```

The priority prevents a build failure from being hidden by a lower-priority
finding. `ValidationSummary.write_json` writes through a temporary file and an
atomic replace, so an interrupted write does not leave a half-report.

## 3. Target matrix and CI

`docs/target_scenarios.md` and `docs/evaluation.md` contain the two reviewed
programs, full refs, signatures, input contracts, and expected exits:

| Target | Correct | Incomplete | Regression |
| --- | ---: | ---: | ---: |
| target1 zlib | 0 | 10 | 20 |
| target2 libpng | 0 | 10 | 20 |

`scripts/run_matrix.sh` executes all six rows and never forces an exit code.
`scripts/verify_matrix_run.py` checks report schema, process/report/expected exit
agreement, baseline identity, reproducer metadata, hashes, and at least three
baseline replays. The workflows are:

- `.github/workflows/verify_patch.yml`: unit matrix and native-container smoke.
- `.github/workflows/validate_target.yml`: target-specific gate only when
  repository variable `DIFFSHERIFF_TARGET_CONFIG` is set.

The latest hosted run has the unit and native jobs green. A skipped target-patch
job means the variable was not configured, not that the implementation is absent.

## 4. How to run your part

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/
bash scripts/run_matrix.sh --list
bash scripts/run_matrix.sh
```

To demonstrate a setup failure safely, copy a config and change
`target.repository_path` to a missing directory, then run:

```bash
diffsheriff --config /tmp/bad-target.yaml --output-json /tmp/bad-report.json
```

The report should say `BUILD_OR_CONFIG_ERROR` and exit 30. Restore the real
config; never change the official matrix's expected codes. To run one approved row:

```bash
diffsheriff --config evaluation/target1/correct.yaml \
  --output-json artifacts/evaluation/manual/report.json \
  --artifacts artifacts/evaluation/manual/runs
```

## 5. Three sentences to memorize

1. “The YAML is a contract: exact refs, safe paths, independent expectations,
   limits, and evidence settings are validated before execution.”
2. “The pipeline compares corresponding modes and reports the highest-priority
   actionable state instead of hiding failures behind a generic boolean.”
3. “The matrix runner verifies retained evidence; it does not manufacture a green
   result.”

