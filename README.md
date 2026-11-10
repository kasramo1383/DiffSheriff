# DiffSheriff

Automated security patch validation and regression testing in CI/CD pipelines.

Course project for Data and Network Security, Sharif University of Technology, Fall 1405.  
Instructor: Solmaz Salimi.

## Problem Statement

Applying a security patch does not guarantee that a vulnerability is eliminated. Patches frequently address only the immediate proof-of-concept input while leaving the underlying defect open to variant payloads. Patches can also introduce functional regressions by breaking valid application behavior.

DiffSheriff executes target C and C++ programs dynamically to verify two core properties:
1. Does the original vulnerability persist or re-emerge in the patched version?
2. Does the patch preserve expected program behavior on valid inputs?

Testing runs against both production and sanitized builds inside an isolated Linux container.

## Pipeline Architecture

```
                             [ tool_config.yaml ]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
     [ Pre-Patch Baseline ]                        [ Post-Patch Commit ]
     ├─ Release Build (-O2)                        ├─ Release Build (-O2)
     └─ Sanitized (ASan/UBSan)                     └─ Sanitized (ASan/UBSan)
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
                       [ Binary Hardening Audit ]
                       (NX, PIE, RELRO, Stack Canary)
                                      │
                                      ▼
                        [ Dynamic Sandbox Runner ]
                        (Valid, Boundary, PoC Inputs)
                                      │
                                      ▼
                      [ Crash & Correlation Engine ]
                      ├─ Stack trace to git diff mapping
                      ├─ Invariant-preserving Delta Debugging
                      └─ Reproducer bundle packaging
                                      │
                                      ▼
                    [ CI/CD Deterministic Exit Code ]
                    (Priority: 30 > 10 > 20 > 40 > 0)
```

## System Components

- Dual-build execution: Runs targets in release mode (`-O2`) and instrumented mode (`-fsanitize=address,undefined`) without mixing diagnostic outputs with production behavior.
- Finding-to-patch correlation: Traces runtime call stacks back to modified git diff hunks, accounting for caller-callee propagation when crashes occur outside modified lines.
- Finding triage: Classifies results into `Fixed`, `Incomplete Fix`, `New Issue`, `Functional Regression`, or `Inconclusive`.
- Testcase minimization: Uses Delta Debugging (`ddmin`) to reduce crashing inputs while preserving the original error type and crash frame.
- Binary hardening audit: Inspects ELF headers and dynamic segments to catch unintended downgrades in NX, PIE, RELRO levels, or stack canaries.
- Deterministic exit codes: Resolves concurrent outcomes through a fixed priority order: 30 > 10 > 20 > 40 > 0.

## Exit Codes

| Code | Label | Meaning |
| :---: | :--- | :--- |
| 0 | `PASS` | Vulnerability resolved on patch, all functional and hardening tests passed. |
| 10 | `VULN_REMAINS` / `NEW_ISSUE` | Vulnerability persists, or a new memory error was detected. |
| 20 | `FUNC_REGRESSION` | At least one valid input that passed on the base version failed on the patch. |
| 30 | `ERROR_CONFIG_OR_BUILD` | Target compilation failed, configuration was invalid, or the runner faulted. |
| 40 | `INCONCLUSIVE` | Baseline error failed to reproduce, or evidence was insufficient to classify. |

## Repository Structure

```text
DiffSheriff/
├── .github/workflows/       CI workflow definitions
├── configs/                 Target configuration files
├── diffsheriff/             Core Python engine
│   ├── builder.py           Dual-mode build orchestrator
│   ├── cli.py               Command-line interface
│   ├── config.py            Target configuration parser
│   ├── correlator.py        Diff hunk and stack trace mapper
│   ├── hardening.py         ELF checksec auditor
│   ├── minimizer.py         Delta Debugging implementation
│   ├── reporter.py          JSON report generator and exit code resolver
│   ├── runner.py            Subprocess execution harness
│   └── triage.py            ASan, UBSan, and signal parser
├── docker/                  Container definitions and resource limits
├── docs/                    Project specifications and design documents
│   ├── architecture.md      Technical architecture and data schemas
│   ├── course_assignment.pdf Original course specification
│   ├── roadmap.md           Implementation phases and milestone gates
│   ├── specification.md     Detailed academic requirements
│   └── target_scenarios.md  Target benchmark evaluation and branch plans
├── targets/                 Target application source repositories
├── tests/                   Unit tests for the verification engine
└── pyproject.toml           Package configuration
```

## Documentation

Detailed technical references are maintained in `docs/`:
- [Technical Specification](docs/specification.md)
- [Implementation Roadmap](docs/roadmap.md)
- [Target Selection and Branch Scenarios](docs/target_scenarios.md)
- [Architecture and JSON Schemas](docs/architecture.md)

## Team Responsibilities

- Engineer 1: Build system, Docker sandboxing, process execution, and ELF hardening auditor.
- Engineer 2: Crash triage, sanitizer parsing, and stack-to-diff correlation.
- Engineer 3: Delta Debugging minimization, reproducer packaging, and regression test generation.
- Engineer 4: Target application benchmarks, functional test matrices, and CI/CD integration.
