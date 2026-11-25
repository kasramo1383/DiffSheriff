# DiffSheriff representation: group guide

This is the common script for the four-person presentation. It assumes no prior
knowledge. DiffSheriff is a **defensive validator**: it compares an approved
base commit with an approved patch commit, runs supplied tests in isolated Linux
containers, and reports whether a known diagnostic was fixed, left behind, or
replaced by a functional regression. We do not generate exploits and we do not
claim that a crash alone proves causation.

## 1. What the assignment is grading

The Persian assignment's section 6 is easiest to remember as two scores:

| Part | Maximum | What we must demonstrate |
| --- | ---: | --- |
| Group technical work | 10 | Diff-to-finding evidence, dynamic/build modes, target scenarios, CI/JSON/exit codes, ELF hardening, documentation/design |
| Individual defense | 10 | Each person explains their code, one result, and makes one bounded safe code/config change |

Treat the technical group result as the PDF's group score out of 10; use the
category weights exactly as the instructor/portal displays them rather than
re-summing them from memory. The individual defense has three axes (3 + 3 + 4):
architecture/code, evidence analysis, and a bounded change. The defense must be
at least 5/10 and must score at least 1 on every axis. The normalized formula
printed in the document is:

```text
final score = 2.5 * (group technical score / 10) + individual defense score
```

So a perfect group score and a 6/10 defense gives 8.5/12.5 (the first term is
2.5; the defense is not multiplied again).

## 2. The one picture everyone must know

### Fair presentation responsibilities

This allocation is for preparation and defense; it does not change the historical
authorship of the code. Work is balanced by concepts, evidence, and demonstration
effort. Markdown length, file counts, and lines of code do not measure difficulty.

| Person | Main code to explain | Evidence to read aloud | Bounded change to demonstrate |
| --- | --- | --- | --- |
| Eng 1 | `config.py`, `builder.py`, `runner.py`, `hardening.py`: validate settings, build exact snapshots, contain execution, inspect protections | One build/hash record and one release-binary hardening record | Change a practice binary path from contained to escaping and explain rejection |
| Eng 2 | `triage.py`, `correlator.py`, and `pipeline.observe`: parse a diagnostic, identify it, relate runtime frames to changed lines | One frame/signature and its correlation reason | Change a practice frame's line from edited to unedited and explain the result |
| Eng 3 | `minimizer.py`, `reproduce.py`, `regressions.py`; `pipeline.stable_observations` and `record_reproducer` | Replay stability, input/binary hashes, reduction stop reason | Change the minimization call budget and explain retained size/stop reason |
| Eng 4 | `pipeline.discover_cases`, `matches_expected`, `compare_case`, and `run_pipeline`; `cli.py`, `reporter.py`, matrix/CI entry points | One case's base/patch expectation comparison, final JSON verdict, and process exit | Change a practice report flag and explain exit-code priority |

Engineer 1 has more concrete setup/protection concepts; Engineer 2 has fewer
components with denser reasoning. Engineer 3 owns the repeatability/reduction
lifecycle. Engineer 4 owns the comparison decisions and integration boundaries,
using the other engineers' helpers without re-explaining their internals. No
person is expected to defend every function in `pipeline.py` alone.

Use the same **8-minute practice slot** for each person: 3 minutes explaining
code, 2 interpreting evidence, 2 demonstrating a change, and 1 answering a
question. This is a rehearsal budget, not a timing rule from the assignment.
Each person reads the shared guide and their own guide in depth, learns the
input/output handoff to their neighbors, and prepares one result and one change.

Use retained target evidence during rehearsal. Live execution/review of the six
real-target comparisons, clean-checkout delivery, and the target CI gate remains
the separate instructor-guided task. Preparing these guides does not rerun it.

```text
CLI/config
  -> validate exact commits and safe paths
  -> export base and patch source snapshots
  -> build release and sanitized binaries independently
  -> inspect ELF hardening
  -> run the same supplied inputs three times per side
  -> parse sanitizer/signal output
  -> correlate source frames with the actual Git diff
  -> compare functional expectations and baseline identity
  -> minimize only a supplied reproducer
  -> retain replayable evidence and generated regressions
  -> write JSON/readable output and choose one exit code
```

The code map is:

| Stage | File | Beginner explanation |
| --- | --- | --- |
| Configuration | `diffsheriff/config.py` | Rejects missing fields, mutable refs, traversal paths, bad limits, and invalid execution settings before work starts. |
| Source/build | `diffsheriff/builder.py` | Exports exactly one Git commit and builds release and sanitized copies from clean snapshots. |
| Isolation | `diffsheriff/runner.py` | Runs commands with no network, dropped capabilities, a read-only root, bounded CPU/RAM/PIDs/output, and a timeout. |
| Triage | `diffsheriff/triage.py` | Turns stderr/exit status into an error type, signal, and source frames. |
| Correlation | `diffsheriff/correlator.py` | Parses the real unified diff and checks whether a runtime frame intersects an edited line. |
| Comparison | `diffsheriff/pipeline.py` | Replays, compares base/patch corresponding modes, and records evidence. |
| Reduction | `diffsheriff/minimizer.py` | Delta-debugging removes chunks only when the same failure invariant remains. |
| Replay/regressions | `diffsheriff/reproduce.py`, `regressions.py` | Verifies hashes and replays retained bundles; refuses conflicting cached data. |
| Reporting | `diffsheriff/reporter.py`, `cli.py` | Writes atomic JSON, readable output, and prioritized CI exit codes. |

## 3. Install and run (copy these commands)

Run from the repository root. PowerShell users can run the Python commands
directly; `bash` commands require WSL/Git Bash.

```bash
python -m pip install -e ".[dev]"
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
python -m pytest -q tests/
```

The native-container test is an infrastructure smoke test, not real-target
acceptance, because the harmless fixture has no approved baseline flaw:

```bash
DIFFSHERIFF_DOCKER_TESTS=1 python -m pytest -q tests/test_container_integration.py
```

To list and run the six approved target comparisons:

```bash
bash scripts/run_matrix.sh --list
bash scripts/run_matrix.sh
```

The matrix writes durable evidence below `artifacts/evaluation/`. Each row must
produce the justified process exit code and a retained JSON/reproducer bundle.
To verify one row after it finishes:

```bash
python3 scripts/verify_matrix_run.py artifacts/evaluation/target1/correct \
  --target target1 --variant correct --actual 0 --expected 0
```

To replay a retained bundle:

```bash
python -m diffsheriff.reproduce artifacts/evaluation/target1/correct/runs/run-*/reproducers/* \
  --check-regression
```

The six rows are target1/target2 × correct/incomplete/regression. Their expected
exits are 0, 10, and 20. Exit 30 means a build/config/tool failure; 40 means
incomplete or unstable evidence. Priority is 30 > 10 > 20 > 40 > 0.

## 4. Target facts to memorize

The targets are instructor-approved exact snapshots, not branch names:

| Target | Baseline signature | Scenario refs |
| --- | --- | --- |
| zlib CVE-2018-25032 | `out-of-bounds`, `trees.c`, `compress_block`, line 1092 | Full correct/incomplete/regression hashes are in `docs/target_scenarios.md`. |
| libpng CVE-2019-7317 | `stack-use-after-return`, `pngerror.c`, `png_safe_execute`, line 954 | Full correct/incomplete/regression hashes are in `docs/target_scenarios.md`. |

Never replace full hashes with `main`, a tag, or a shortened hash. A
`baseline_signature` identifies what the baseline must reproduce; it is not
permission to invent a new finding.

## 5. Safe behavior-change demonstrations

Each person makes one change in a temporary copy or reverted working tree, runs a
harmless fixture, explains the changed result, and restores the file. Do not
modify official target expectations during the defense.

| Change | Expected effect |
| --- | --- |
| Lower `execution.timeout_seconds` | A slow command becomes `timeout` and can produce exit 40. |
| Lower `minimization.max_oracle_calls` from 256 to 1 | Reduction stops with `oracle_call_limit`; it does not prove a global minimum. |
| Change a local `expected.exit_code` | The validator reports a functional mismatch. |
| Give a missing config path | CLI catches setup failure and emits exit 30 with JSON notes. |
| Add a correlation unit test for an edited line | The finding's correlation type/reason changes without a new trigger. |

After a demo, restore the file and run `git diff --check`.

## 6. Presentation order and shared questions

1. **Group opening:** each person contributes one sentence about their pipeline stage; introduce the rubric and evidence location together.
2. **Engineer 1:** config validation, source export, two builds, container limits, ELF hardening.
3. **Engineer 2:** sanitizer parsing, signals, diff hunks, correlation and uncertainty.
4. **Engineer 3:** replay, minimization, reproducer bundle, regression identity and hashes.
5. **Engineer 4:** independent expectations, comparison decisions, orchestration, CLI/report/exit priority, matrix automation and CI.
6. **Group close:** each person explains their own fields in one retained real-target JSON report; share setup and rehearsal work.

Everyone should be able to answer:

- Why three replays? To reject unstable observations.
- Why release-to-release and sanitized-to-sanitized? Sanitizers change diagnostics.
- Why is a diff intersection not enough? Comparative base/patch evidence is also required.
- What does exit 40 mean? Inconclusive/unstable/insufficient evidence, not a clean pass.
- Where is evidence? Under `artifacts/`, with JSON, logs, hashes, and bundles.

## 7. Finished versus instructor-only

The repository has passed the local CI-equivalent tests and six-row local target
matrix; the latest hosted unit/native run is green. The optional hosted
`target-patch` job runs only when repository variable
`DIFFSHERIFF_TARGET_CONFIG` is set. Manual instructor review of all six real
target comparisons and clean-checkout delivery remains a human evaluation step.

