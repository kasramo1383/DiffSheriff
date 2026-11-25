# Eng 4 presentation guide

**Presenter:** Eng 4

**Topic:** Functional comparison decisions, pipeline orchestration, CLI/reports,
target matrix automation, CI, and delivery integration.

Your job is to connect the other three engineers' components into one command
that a clean checkout can run. Engineer 1 now owns configuration validation;
Engineer 2 owns parsing/correlation; Engineer 3 owns stability/reduction/replay.
You explain their inputs/outputs and the comparison/reporting decisions, rather
than re-explaining their implementations. Target setup and presentation rehearsal
are shared by the group. Use the same 8-minute rehearsal structure: 3 minutes
code, 2 evidence, 2 change, 1 question.

## 1. The story to tell

Start with the validated configuration supplied by Engineer 1. An expectation
is the independently specified result a correct program should produce, such as
exit 0 with particular output. A valid-input base-pass/patch-fail comparison
therefore has an explanation beyond “the two programs behaved differently.”

`run_pipeline` then discovers supplied cases, computes the expectation manifest
hash, writes durable inputs, obtains the actual Git diff, builds both commits in
both modes, inspects hardening, runs three observations, compares
findings/regressions, records reproducers, and writes a `ValidationSummary`.

The CLI catches setup/tool errors, always tries to write JSON, prints a readable
summary, and exits with one prioritized code. CI runs unit tests, a native smoke
test, and the optional target-patch gate without pretending a skipped job passed.

## 2. Exact code to know

### `diffsheriff/pipeline.py`

`observe` is the handoff point (the complete code is in Engineer 2's guide).
`compare_case` decides among a fixed vocabulary:

```python
regression = stable and case["valid_input"] and base_ok and not patch_ok
vulnerability = stable and bool(patch_sig)
```

The two build modes are compared separately: release with release and sanitized
with sanitized. Each side is replayed three times. A patch signature equal to
the baseline is an incomplete fix; a valid-input base-pass/patch-fail is a
functional regression. Unstable replays add an incomplete-analysis reason. Your
detailed functions are `discover_cases`, `matches_expected`, and `compare_case`;
for `run_pipeline`, explain the stage order and calls to other owners' helpers.

Walk through one retained case: locate `expected`, `valid_input`, mode, and
base/patch runs; then explain which comparison rule produced the finding. Also
show the baseline signature was established before claiming the patch fixed it.

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

For your change demonstration, run `python` from the repository root, paste the
following example, then press Enter on a blank line:

```python
from diffsheriff.reporter import resolve_priority_exit_code

for vulnerability in (False, True):
    code, verdict = resolve_priority_exit_code(
        build_failed=False, vuln_detected=vulnerability,
        regression_detected=True, is_inconclusive=False)
    print(vulnerability, "->", code, verdict)

```

Expected output: `False` gives 20/`FUNC_REGRESSION`; `True` gives
10/`VULN_REMAINS_OR_NEW_ISSUE`. A remaining diagnostic has higher priority than a
functional regression when both flags are set. This is a synthetic reporting
exercise. Use `exit()` to leave Python. If asked to change implementation
behavior, locate the branch order in `resolve_priority_exit_code` and use
`tests/test_reporter.py` to observe the effect.

To run one approved row during the instructor-guided evaluation:

```bash
diffsheriff --config evaluation/target1/correct.yaml \
  --output-json artifacts/evaluation/manual/report.json \
  --artifacts artifacts/evaluation/manual/runs
```

## 5. Three sentences to memorize

1. “Independent expectations let us distinguish a functional regression from
   an unexplained difference between versions.”
2. “The pipeline compares corresponding modes and reports the highest-priority
   actionable state instead of hiding failures behind a generic boolean.”
3. “The matrix runner verifies retained evidence; it does not manufacture a green
   result.”

For your evidence slot, show a case comparison, JSON verdict, matching process
exit, and workflow condition. Be ready to answer: “Which code wins when both a
remaining diagnostic and a functional regression are confirmed, and why?”

