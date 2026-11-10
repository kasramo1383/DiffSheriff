# Requirements digest

This document is a working English digest of [`course_assignment.pdf`](course_assignment.pdf). It is not an independent specification. The instructor's PDF is authoritative whenever wording or interpretation differs.

## Administrative facts

- Course: Data and Network Security, Sharif University of Technology
- Instructor: Solmaz Salimi
- Released: 28 Mehr 1405
- Due: 18 Aban 1405
- Team size: four students
- Course-grade weight: 2.5 of 20 points

## 1. Objective

Build an automated tool for a CI/CD pipeline that executes real target programs and answers, within a defined test scope:

1. After the original security failure is reproduced on the baseline, is it still observed on the patched version?
2. Does the patched version preserve independently defined correct behavior for valid inputs?

The tool must connect observed findings to code changes and retain reproducible evidence. Not observing a failure in the test suite is not proof that no vulnerability exists.

## 2. Scope and ground truth

- Targets are source-available C or C++ programs compiled as Linux x86_64 ELF executables.
- A target may receive input through a file, command-line arguments, or standard input. A new target must be onboarded through configuration describing its build, binary, input delivery, and tests; the analysis must not depend on target-specific names or structure.
- Python scripts, web applications, and interpreted code are not valid target programs. This restriction does not constrain the implementation language of DiffSheriff.
- Real dynamic execution is mandatory; static analysis or source-text inspection alone is insufficient.
- Functional correctness must be defined before evaluation from program documentation or independent reference tests and approved by the instructor. The patched program's output and an LLM's opinion are not ground truth.

## 3. Required analysis

### 3.1 Patch-to-finding correlation

The tool receives pre-patch and post-patch versions and their Git diff. It must explain how a fixed, remaining, or newly observed finding relates to modified files, functions, or execution paths.

A crash need not occur on a modified line. A changed caller may affect a failure in a callee. Stack traces and comparative execution evidence are acceptable evidence; mere proximity between a static warning and a changed line is insufficient. If the evidence does not support attribution, report the relation as inconclusive.

Findings must distinguish:

- `Fixed`
- `Incomplete Fix`
- `New Issue`
- `Functional Regression`
- `Inconclusive`

A newly observed crash alone does not prove that the patch caused it. A functional regression requires evidence that the baseline satisfied independent expected behavior and that the patch violated it under corresponding conditions.

### 3.2 Dynamic tests and termination evidence

Run valid functional inputs as well as boundary and invalid inputs. For abnormal termination, retain separately:

- error category, such as buffer overflow, use-after-free, null dereference, or division by zero;
- detection mechanism, such as an OS signal, binary guard, or sanitizer;
- process exit code and received signal;
- stdout and stderr;
- timeout or resource-limit outcome, which is not automatically an exploitable vulnerability.

Run ordinary release binaries and instrumented/sanitized binaries separately. Compare pre-patch and post-patch evidence only between corresponding build modes. The ordinary binary shows delivered behavior; the instrumented binary provides diagnostic detail.

The same documented valid, boundary, and invalid suites and equivalent settings must be used on both versions and corresponding builds.

### 3.3 Reproducibility, minimization, and regression tests

For every confirmed finding, retain a reproducer containing:

- triggering input;
- exact source version or commit and binary hash;
- build settings and relevant environment variables;
- exact execution command;
- results of at least three replays, with unstable findings identified.

Automatically minimize the triggering input, for example with delta debugging. The minimized input must preserve the same error type at the relevant location; a generic nonzero exit code is not an adequate invariant. Preserve both original and minimized inputs.

Automatically add the minimized input to the regression suite. The resulting test must expose the expected failure on the vulnerable baseline and check the absence of that failure plus expected behavior on the correct patch.

### 3.4 Binary hardening

On ordinary ELF binaries, inspect and retain evidence for:

- NX
- PIE
- RELRO, distinguishing none, partial, and full
- stack canary

Warn when a protection present on the baseline is unintentionally removed or downgraded by the patch. PIE does not prove that runtime ASLR is enabled, and a canary symbol does not prove coverage of every function.

## 4. CLI, reports, and exit codes

The tool must be runnable from the command line and emit both a readable developer summary and structured JSON. JSON must preserve independent security, functional, and analysis-completeness statuses, evidence, exact versions, and execution settings even when one process exit code is selected.

| Code | Label | Condition |
| ---: | --- | --- |
| 0 | `PASS` | Baseline target flaw reproduced; not observed on the patch within the suite; no other confirmed security flaw; functional and mandatory checks complete and successful. |
| 10 | `VULN_REMAINS` or `NEW_ISSUE` | The original flaw remains, or another memory/security flaw is confirmed with valid evidence. |
| 20 | `FUNC_REGRESSION` | At least one valid test that passed on the baseline fails on the patch. |
| 30 | `BUILD_OR_CONFIG_ERROR` | Target build, configuration, execution environment, or tool operation fails. |
| 40 | `INCONCLUSIVE` | A mandatory check is incomplete or evidence is insufficient, unstable, or unclassified. |

When conditions coexist, use priority `30 > 10 > 20 > 40 > 0` while retaining all independent findings in JSON.

## 5. Required target scenarios

Evaluate two independent C/C++ programs; at least one must be a real non-toy project or library. The team selects and prepares the targets, source provenance, patches, independent reference tests, and expected outcomes, subject to instructor approval. A public known vulnerability and patch may be used; discovering a new vulnerability is not required.

For each target, retain four source versions in the project repository:

1. Vulnerable baseline with at least one reproducible memory error.
2. Correct patch: target error absent within the evaluation scope and functional tests pass; expected exit `0`.
3. Incomplete patch: initial trigger blocked but a team-designed alternative input still exposes the flaw; expected exit `10`.
4. Regression patch: target error blocked but valid behavior broken; absent another confirmed security issue, expected exit `20`.

At defense, the tool will receive unseen patches for the targets or a related program within the agreed domain and interface. Results must not be selected from known file names or patch identifiers.

## 6. Execution and delivery

- Run tests in an isolated environment such as a resource-limited container and only against permitted programs.
- Deliver tool source, configuration, exact target versions, tests, reproducer bundles, generated reports, pipeline definition, and standalone execution instructions.
- All team members must understand the architecture and their work. Each member is assessed independently through explanation, evidence analysis, and a limited live code or configuration change.

## 7. Grading

| Technical area | Points |
| --- | ---: |
| Patch validation, version comparison, and precise diff correlation | 25 |
| Dynamic testing, boundary inputs, build separation, and error classification | 25 |
| Reproducibility, automatic minimization, and regression generation | 15 |
| Correct scenarios for two targets and unseen-patch behavior | 15 |
| CI/CD automation, JSON, and exit codes | 10 |
| Binary hardening and protection-change detection | 5 |
| Documentation, modularity, and standalone execution | 5 |
| Total | 100 |

Individual defense is scored out of 10: architecture and owned logic (3), finding/evidence analysis (3), and live change plus test (4). Credit requires effective participation, at least 5/10 overall, and at least one point in each axis. The final individual project grade is:

`2.5 × (group technical score / 100) × (individual defense score / 10)`
