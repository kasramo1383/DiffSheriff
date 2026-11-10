# DiffSheriff

DiffSheriff is a course-project scaffold for dynamic security-patch validation and functional-regression testing of Linux x86_64 C/C++ targets.

> [!WARNING]
> The repository is not yet an end-to-end validator. The CLI deliberately exits with code `40` (`INCONCLUSIVE`) after validating configuration, because base/patch orchestration, evidence comparison, reproducer packaging, and target scenarios are not implemented. It must not be used as a CI security gate in its current state.

## Authority and derived documentation

The instructor's Persian assignment is the only authoritative specification: [docs/course_assignment.pdf](docs/course_assignment.pdf).

The Markdown files in `docs/` are maintained working notes:

- [Requirements digest](docs/specification.md) is a traceable English summary of the PDF. If it conflicts with the PDF, the PDF controls.
- [Architecture](docs/architecture.md) distinguishes implemented modules from planned integration.
- [Roadmap](docs/roadmap.md) lists acceptance gates, not claims of completion.
- [Target scenarios](docs/target_scenarios.md) records what must be approved before target work begins.

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

Implemented and unit-testable components:

- YAML model and fail-closed configuration validation
- release/sanitized build helper with retained artifact copies and hashes
- subprocess execution through `stdin`, `argv`, or a temporary input file
- ASan, UBSan, stack-canary, and signal triage primitives
- unified-diff hunk parsing and stack-frame correlation
- invariant-preserving byte-level `ddmin`
- ELF hardening inspection and degradation comparison
- exit-code resolution and basic JSON summary writing

Missing integration:

- base and patched source/ref acquisition and four-way build orchestration
- test discovery, independent functional oracle execution, and result comparison
- robust finding identity across builds and the full classification state machine
- execution-path evidence beyond stack-to-hunk intersection
- stability replay, reproducer bundles, and automatic regression-test insertion
- complete JSON evidence contract and developer summary
- two approved target implementations and all required variants
- isolated execution enforcement and end-to-end CI validation

## Development

Python 3.10 or newer is required.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

The example configuration at [configs/example_target.yaml](configs/example_target.yaml) is illustrative only; its target paths do not exist until an approved target is added.

```bash
diffsheriff --config configs/example_target.yaml --output-json validation_report.json
```

That command currently writes an incomplete report and exits `40` by design.

## Exit codes

| Code | Label | Required meaning |
| ---: | --- | --- |
| 0 | `PASS` | Baseline flaw reproduced, absent from the patch within the test scope; no confirmed new security flaw; required functional and other checks complete and successful. |
| 10 | `VULN_REMAINS` / `NEW_ISSUE` | Original flaw remains, or another confirmed memory/security flaw is observed. |
| 20 | `FUNC_REGRESSION` | A valid functional test that passed on the baseline fails on the patch. |
| 30 | `BUILD_OR_CONFIG_ERROR` | Target build, configuration, execution environment, or tool operation fails. |
| 40 | `INCONCLUSIVE` | Required analysis is incomplete or evidence is insufficient, unstable, or unclassified. |

## Repository layout

```text
.
├── .github/workflows/       Baseline package test workflow
├── configs/                 Illustrative target configuration
├── diffsheriff/             Python primitives
├── docker/                  Development/container baseline
├── docs/                    Source PDF and derived working documents
├── targets/                 Future approved target source trees
├── tests/                   Unit tests
└── pyproject.toml           Package metadata and dependencies
```
