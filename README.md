# DiffSheriff

DiffSheriff is a defensive patch-validation and functional-regression tool for authorized Linux x86_64 C/C++ targets.

The CLI compares exact source commits in isolated containers and retains its evidence.
It fails closed when the designated baseline flaw, independent expected behavior, or
mandatory checks cannot be established. It does not provide exploit tooling; the course's incomplete-patch alternative-input
case is limited to the documented local target scope and safe test inputs. Verification limits and staged acceptance work are recorded in
[the live roadmap](docs/roadmap.md).

## Authority and derived documentation

The instructor's Persian assignment is the only authoritative specification: [docs/course_assignment.pdf](docs/course_assignment.pdf).

The Markdown files in `docs/` are maintained working notes:

- [Requirements digest](docs/specification.md) is a traceable English summary of the PDF. If it conflicts with the PDF, the PDF controls.
- [Architecture](docs/architecture.md) distinguishes implemented modules from planned integration.
- [Roadmap](docs/roadmap.md) lists acceptance gates, not claims of completion.
- [Target scenarios](docs/target_scenarios.md) records target scope, provenance, and the course team's approval waiver.
- [Reference comparison](docs/reference_comparison.md) records a historical DNS-P1 comparison; current acceptance belongs in the roadmap.
- [Defense preparation](docs/defense_guide.md) gives each engineering role a code/evidence study path.

## Assignment requirements at a glance

- Dynamically execute both pre-patch and post-patch versions of configurable C/C++ ELF x86_64 targets.
- Compare corresponding release and instrumented builds without mixing their evidence.
- Test valid, boundary, and invalid/malicious inputs against independent, pre-approved functional ground truth.
- Classify fixed, incomplete, new, regressive, and inconclusive outcomes and correlate findings to patch changes using runtime evidence.
- Minimize confirmed failure inputs while preserving error type and relevant location, retain original and minimized inputs, replay at least three times, and add regression tests automatically.
- Inspect NX, PIE, RELRO, and stack-canary status on ordinary binaries and report protection degradation.
- Produce human-readable and JSON reports with exact exit codes and priority `30 > 10 > 20 > 40 > 0`.
- Demonstrate two independent targets, including at least one real non-toy project or library, with vulnerable, correct-patch, incomplete-patch, and regression-patch variants.

## Current implementation

The sole live record of implemented capabilities, missing work, blockers, and the next
action is [docs/roadmap.md](docs/roadmap.md). It is maintained so another agent can
resume the project without relying on chat history. This README and the architecture
document must not maintain parallel progress lists.

## Contributors and engineering ownership

This table is the authoritative ownership record. Roles define review, study, and
defense responsibility; they do not imply that each member must personally type
every line in the subsystem. Implementation may be delegated to one or two coding
agents, but every member must understand the complete pipeline at a high level and
their assigned subsystem in detail.

| Engineer role | Contributor | Student ID | Ownership |
| --- | --- | --- | --- |
| Engineer 1 - Build and execution | Mohammadreza Javadi | 402105868 | Source preparation, release/sanitized builds, isolated execution, limits, and ELF hardening |
| Engineer 2 - Triage and correlation | Mohammadmahdi Abedini | 402106191 | Signals and sanitizer parsing, finding identity, Git-diff parsing, and evidence-based correlation |
| Engineer 3 - Reproduction and regression | Mohammadreza Izadi | 402110916 | Stability replay, input minimization, reproducer bundles, and generated regression tests |
| Engineer 4 - Integration and targets | Kasra Montazeri | 402106575 | Pipeline orchestration, CLI and reports, target scenarios, end-to-end tests, and delivery integration |

The existing [agent handoff prompt](docs/agent_handoff_prompt.md) is a historical snapshot,
not current task guidance; use the roadmap for current gaps. No new handoff is maintained.
with another coding agent. Before handoff, it updates the
live roadmap so the first unfinished action and any real blocker are explicit. The
project does not use an issue board, sprint process, or per-task activity log. CI/CD
is implemented only to the extent required by the assignment as a product capability
and verification mechanism.

## Development

Python 3.10 or newer is required.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

Docker with Linux amd64 containers and Git are required for target validation.
Build the runtime image before running the CLI:

```bash
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
```

On Linux/WSL, run `bash verify.sh` after installing development dependencies and
building the image to check formatting, lint, all tests including the harmless native
matrix, and wheel creation. Its success means tool verification, not target acceptance.

Follow [the standalone guide](docs/usage.md) for schema version 2, independent
expectations, native smoke testing, and replay. The example configuration at
[configs/example_target.yaml](configs/example_target.yaml) is illustrative;
replace its source refs and supply the independently approved test assets.

See [CI setup and retained regressions](docs/ci.md) for the patch-validation job,
regression import/export, and diagnostic cases awaiting independent expectations.

```bash
diffsheriff --config configs/example_target.yaml --output-json validation_report.json
```

An unconfigured example produces code `30`. A correctly configured harmless target
produces code `40` because it cannot reproduce the designated baseline security flaw.

## Exit codes

| Code | Label | Required meaning |
| ---: | --- | --- |
| 0 | `PASS` | Baseline flaw reproduced, absent from the patch within the test scope; no confirmed new security flaw; required functional and other checks complete and successful. |
| 10 | `VULN_REMAINS` / `NEW_ISSUE` | Original flaw remains, or another confirmed memory/security flaw is observed. |
| 20 | `FUNC_REGRESSION` | A valid functional test that passed on the baseline fails on the patch. |
| 30 | `BUILD_OR_CONFIG_ERROR` | Target build, configuration, execution environment, or tool operation fails. |
| 40 | `INCONCLUSIVE` | Required analysis is incomplete or evidence is insufficient, unstable, or unclassified. |

## Test and evaluation results

All automated checks and retained target evaluations keep synthetic/harmless tool smoke tests separate from real-target runs; live acceptance gates remain in [docs/roadmap.md](docs/roadmap.md) and [artifacts/README.md](artifacts/README.md).

### Generic tool verification

Verified on the current codebase (`pytest`, `black`, `flake8` in WSL Ubuntu; native container run against `diffsheriff:local`, image `d596e5159a0b`):

- **Unit and simulated integration suite** (`python3 -m pytest -q tests/`): `352 passed, 1 skipped` (native Docker test skipped unless `DIFFSHERIFF_DOCKER_TESTS=1`).
- **Harmless native container integration** (`DIFFSHERIFF_DOCKER_TESTS=1 python3 -m pytest -q tests/test_container_integration.py`): `1 passed` — builds release and sanitized x86_64 ELF binaries for [tests/fixtures/harmless/main.c](tests/fixtures/harmless/main.c), checks ELF hardening/sanitizer symbols, exercises `stdin`/`file`/`argv`, completes 36 suite executions (`functional_status: PASS`), and returns expected exit `40` (`baseline_identity_unestablished`).
- **Formatting and lint**: `black --check diffsheriff tests` (`31 files` unchanged) and `flake8 --select=E,F,W,C90 diffsheriff tests` pass.
- **Clean-checkout & hosted CI**: Local clean-checkout verification ([artifacts/checkpoints/clean-checkout/README.md](artifacts/checkpoints/clean-checkout/README.md)) passed wheel install/CLI checks and `verify.sh` (`309` tests at revision `b0d59125`). Hosted GitHub Actions ([.github/workflows/verify_patch.yml](.github/workflows/verify_patch.yml), run 21 at `006113f5`) passed `unit (3.10)`, `unit (3.12)`, and `native-container`, with `target-patch` skipped because `DIFFSHERIFF_TARGET_CONFIG` was unset.

### Retained six-row target matrix

Executed via [scripts/run_matrix.sh](scripts/run_matrix.sh) against packaged bundles for `target1` (`zlib`, CVE-2018-25032) and `target2` (`libpng`, CVE-2019-7317) in [artifacts/evaluation/matrix.tsv](artifacts/evaluation/matrix.tsv), and re-verified structurally with [scripts/verify_matrix_run.py](scripts/verify_matrix_run.py) (`6/6 OK`: report/process exit agreement, established `baseline_identity_modes`, reproducer metadata, original/minimized input SHA-256 hashes, and ≥ 3 baseline replays). Across all six runs, release binaries observed `NX=True`, `PIE=True`, `RELRO=partial`, `canary=False` with `hardening_degraded=False`.

| Target / variant | Runs | Exit / verdict | Security (fixed / lingering) | Functional (pass / fail) | Reproducers (reduced) | Analysis status & recorded incomplete reasons |
| --- | ---: | --- | --- | --- | ---: | --- |
| `target1` / `correct` | 144 | `0` / `PASS` | `PASS` (6 / 0) | `PASS` (24 / 0) | 6 (3) | Complete |
| `target1` / `incomplete` | 144 | `10` / `VULN_REMAINS_OR_NEW_ISSUE` | `FAIL` (0 / 2) | `INCONCLUSIVE` (24 / 2) | 8 (3) | Incomplete (`fix_evidence_insufficient`, `patch_attribution_unestablished`; 8 inconclusive findings) |
| `target1` / `regression` | 144 | `20` / `FUNC_REGRESSION` | `PASS` (6 / 0) | `FAIL` (18 / 6) | 12 (5) | Complete (6 `Functional Regression`, 6 `Fixed`) |
| `target2` / `correct` | 48 | `0` / `PASS` | `PASS` (4 / 0) | `PASS` (2 / 0) | 4 (3) | Complete |
| `target2` / `incomplete` | 60 | `10` / `VULN_REMAINS_OR_NEW_ISSUE` | `FAIL` (5 / 1) | `PASS` (2 / 0) | 6 (4) | Incomplete (`functional_expectation_missing` on minimized bytes; 1 inconclusive finding) |
| `target2` / `regression` | 78 | `20` / `FUNC_REGRESSION` | `INCONCLUSIVE` (7 / 0) | `FAIL` (0 / 2) | 8 (5) | Incomplete (`fix_evidence_insufficient`, `functional_expectation_unmet_on_patch`, `functional_expectation_missing`; 2 inconclusive findings) |

Local clean-checkout CI-equivalent runs of `validate_target.yml` for both `correct` configs also exited `0` / `PASS` (`analysis_complete: true`): `target1` with `180` executions (`30/0` functional, `5` fixed) and `target2` with `48` executions (`2/0` functional, `4` fixed), retained in [artifacts/checkpoints/target-matrix/README.md](artifacts/checkpoints/target-matrix/README.md). `target2` runs used a local derived image supplying the `docker/Dockerfile`-declared `zlib1g-dev` headers absent from the cached local image.

## Repository layout

```text
.
├── .github/workflows/       Tool verification and configurable target patch validation
├── configs/                 Illustrative target configuration
├── diffsheriff/             Validator pipeline and supporting modules
├── docker/                  Development/container baseline
├── docs/                    Source PDF and derived working documents
├── targets/                 Exact target source bundles and original upstream archives
├── tests/                   Unit, simulated integration, and harmless native tests
└── pyproject.toml           Package metadata and dependencies
```
