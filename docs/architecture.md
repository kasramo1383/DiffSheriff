# Architecture and implementation boundary

This is a design record for the repository as it exists. Required behavior comes from [`course_assignment.pdf`](course_assignment.pdf) and the derived digest in `specification.md`.

## Intended pipeline

```text
target config + base ref + patch ref + independent tests
                         |
                         v
             acquire exact source versions
                         |
                         v
       build base and patch in release + sanitized modes
                         |
             +-----------+-----------+
             |                       |
             v                       v
     hardening inspection      isolated test execution
                                     |
                                     v
                       termination + sanitizer triage
                                     |
                                     v
                   compare corresponding build evidence
                                     |
              +----------------------+------------------+
              |                      |                  |
              v                      v                  v
       diff correlation      minimization/replay   functional oracle
              |                      |                  |
              +----------------------+------------------+
                                     |
                                     v
                      full JSON + readable summary
                                     |
                                     v
                         prioritized process exit
```

The comparison layer is the central missing component. Existing modules are primitives and do not collectively implement this pipeline.

## Current module inventory

| Module | Implemented boundary | Important limitation |
| --- | --- | --- |
| `config.py` | Parses and validates the current YAML shape. | Does not establish source refs, an independent oracle contract, or a full schema versioning policy. |
| `builder.py` | Executes configured clean/release/sanitized commands, retains copies, and hashes binaries. | Operates on one source tree at a time; no base/patch checkout isolation or container enforcement. Configured shell commands are trusted input. |
| `runner.py` | Runs one binary with input through stdin, argv, or a temporary file and captures output/timeout. | No resource controller, filesystem sandbox, or batch test discovery. |
| `triage.py` | Recognizes common ASan, UBSan, stack-canary, and signal outcomes and parses simple sanitizer frames. | Parsers are not exhaustive and no stable cross-build finding identity exists. |
| `correlator.py` | Parses unified-diff hunk ranges and matches runtime frames to changed lines/callers. | Stack intersection is evidence of relation, not proof of causation; execution-path/data-flow evidence remains unimplemented. |
| `minimizer.py` | Reduces byte payloads using a caller-provided strict failure oracle. | No integration with execution, replay, bundle creation, or regression-suite insertion. |
| `hardening.py` | Reads ELF NX, PIE, RELRO, and canary indicators and compares versions. | Not wired into builds or reports; symbol presence has the limitations stated by the assignment. |
| `reporter.py` | Resolves exit-code priority and writes a basic JSON summary. | The current model is not the complete evidence contract required for final delivery. |
| `cli.py` | Loads configuration and writes a fail-closed report. | It intentionally returns `INCONCLUSIVE`; it performs no validation pipeline. |

## Required comparison invariants

The orchestrator must enforce these invariants before any `PASS` is possible:

1. The designated baseline flaw was reproduced with valid evidence.
2. Base release is compared only with patch release; base sanitized only with patch sanitized.
3. Corresponding runs use the same input, execution settings, environment policy, timeout, and resource limits.
4. Functional expectations come from the configured independent source, not patch output.
5. A security identity includes error type and a relevant location/signature; nonzero exit alone is insufficient.
6. New abnormal behavior is not attributed to the patch without adequate evidence.
7. Missing, unstable, or ambiguous mandatory evidence produces `INCONCLUSIVE`, not `PASS`.
8. Build/config/tool failure produces code `30`, while all independent findings remain in the report.

## Artifact ownership

- `.diffsheriff/artifacts/`: generated retained binary copies; ignored by Git.
- `validation_report.json`: generated report; ignored unless intentionally retained as evaluation evidence.
- `reproducers/`: future stable reproducer bundles for confirmed findings.
- `targets/`: exact approved target sources/versions and their test assets.

Generated files must never be treated as source-of-truth requirements. Target provenance, approval, ground truth, and scenario definitions belong in `target_scenarios.md` once established.

## Configuration boundary

`configs/example_target.yaml` documents the current parser shape. It is not an approved or runnable target configuration. Before target integration, the schema must be extended to identify exact base/patch refs and a machine-checkable independent functional oracle.
