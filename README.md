# DiffSheriff

DiffSheriff is a defensive patch-validation and functional-regression tool for authorized Linux x86_64 C/C++ targets.

The CLI compares exact source commits in isolated containers and retains its evidence.
It fails closed when the designated baseline flaw, independent expected behavior, or
mandatory checks cannot be established. It does not provide exploit tooling; the course's
incomplete-patch alternative-input case is limited to approved local targets and safe
test inputs. Verification limits and staged acceptance work are recorded in
[the live roadmap](docs/roadmap.md).

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
| Engineer 1 - Build and execution | Mohammadreza Izadi | 402110916 | Source preparation, release/sanitized builds, isolated execution, limits, and ELF hardening |
| Engineer 2 - Triage and correlation | Mohammadmahdi Abedini | 402106191 | Signals and sanitizer parsing, finding identity, Git-diff parsing, and evidence-based correlation |
| Engineer 3 - Reproduction and regression | Mohammadreza Javadi | 402105868 | Stability replay, input minimization, reproducer bundles, and generated regression tests |
| Engineer 4 - Integration and targets | Kasra Montazeri | 402106575 | Pipeline orchestration, CLI and reports, target scenarios, end-to-end tests, and delivery integration |

An agent may take over or stop at any coherent point. Before handoff, it updates the
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

Follow [the standalone guide](docs/usage.md) for schema version 2, independent
expectations, native smoke testing, and replay. The example configuration at
[configs/example_target.yaml](configs/example_target.yaml) is illustrative;
replace its source refs and supply the independently approved test assets.

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

## Repository layout

```text
.
├── .github/workflows/       Unit and native container verification
├── configs/                 Illustrative target configuration
├── diffsheriff/             Validator pipeline and supporting modules
├── docker/                  Development/container baseline
├── docs/                    Source PDF and derived working documents
├── targets/                 Future approved target source trees
├── tests/                   Unit, simulated integration, and harmless native tests
└── pyproject.toml           Package metadata and dependencies
```
