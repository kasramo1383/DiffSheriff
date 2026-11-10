# DiffSheriff 🤠🔍

> **Automated Security Patch Validation and Regression Testing in CI/CD**  
> *Course: Data and Network Security (امنیت داده و شبکه) — Sharif University of Technology*  
> *Instructor: Solmaz Salimi (سولماز سلیمی)*  

[![CI Status](https://img.shields.io/badge/CI-Automated%20Patch%20Validation-blue.svg)](#)
[![Target](https://img.shields.io/badge/Target-Linux%20ELF%20x86__64-orange.svg)](#)
[![Sanitizers](https://img.shields.io/badge/Sanitizers-ASan%20%7C%20UBSan-red.svg)](#)
[![Exit Codes](https://img.shields.io/badge/Exit%20Codes-30%20%7C%2010%20%7C%2020%20%7C%2040%20%7C%200-brightgreen.svg)](#)

---

## 📖 Overview

Applying a security patch does not guarantee that a vulnerability is actually resolved or that the application remains functional. Developers frequently write incomplete patches that only block specific proof-of-concept (PoC) inputs while leaving root vulnerabilities exploitable, or inadvertently introduce regressions that break valid software behavior.

**DiffSheriff** is an automated dynamic verification and regression testing engine integrated into CI/CD pipelines. Rather than relying on superficial static analysis, DiffSheriff executes compiled C/C++ Linux ELF binaries inside an isolated container sandbox across both production and sanitizer builds to deterministically answer two fundamental questions:
1. **Security Invariant**: Does the original vulnerability persist or re-emerge in the patched version across the test corpus?
2. **Functional Invariant**: Does the patch preserve expected, standard program behavior on valid and boundary inputs?

---

## 🏛️ System Architecture

```
                                [ tool_config.yaml ]
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼                                             ▼
        [ Pre-Patch Base Commit ]                     [ Post-Patch Commit ]
        ├─ Release Build (-O2)                        ├─ Release Build (-O2)
        └─ Sanitized (ASan + UBSan)                   └─ Sanitized (ASan + UBSan)
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
                         ├─ Match Call Trace vs. Git Diff
                         ├─ Invariant-Preserving Delta Debugging
                         └─ Generate Reproducer Bundle (3x Replay)
                                         │
                                         ▼
                       [ CI/CD Deterministic Exit Code ]
                       (Priority: 30 > 10 > 20 > 40 > 0)
```

---

## ⚡ Key Capabilities

* **Dual-Build Isolation**: Evaluates target software across both **Release** (`-O2`) and **Sanitized** (`-fsanitize=address,undefined`) builds without conflating diagnostic outputs with production behavior.
* **Finding-to-Patch Correlation**: Maps runtime call stacks to exact `git diff` hunks, identifying both direct line matches and indirect caller-callee propagation.
* **Status Classification**: Categorizes every finding into `Fixed`, `Incomplete Fix`, `New Issue`, `Functional Regression`, or `Inconclusive`.
* **Algorithmic Testcase Minimization**: Employs **Delta Debugging (`ddmin`)** to automatically minimize crashing inputs while strictly preserving the failure invariant (exact error type and top stack frame).
* **Reproducer Bundles**: Packages crashing inputs, commit hashes, binary hashes, build flags, and environment variables with verified 3x replay stability.
* **Binary Hardening Auditor**: Inspects ELF headers and dynamic segments to detect unintended degradation of **NX**, **PIE**, **RELRO** (None / Partial / Full), and **Stack Canaries**.
* **Standardized CI/CD Exit Codes**: Enforces an unambiguous exit code hierarchy:
  $$\mathbf{30} \;\succ\; \mathbf{10} \;\succ\; \mathbf{20} \;\succ\; \mathbf{40} \;\succ\; \mathbf{0}$$

| Exit Code | Identifier | Condition |
| :---: | :--- | :--- |
| **`0`** | `PASS` | Flaw reproduced on base, confirmed eliminated on patch; all functional and hardening checks passed. |
| **`10`** | `VULN_REMAINS` / `NEW_ISSUE` | Baseline vulnerability persists in patch OR a new security flaw was introduced. |
| **`20`** | `FUNC_REGRESSION` | At least one valid functional test that succeeded on base fails on the patched build. |
| **`30`** | `ERROR_CONFIG_OR_BUILD` | Target fails to compile, malformed configuration, or runner runtime error. |
| **`40`** | `INCONCLUSIVE` | Required checks incomplete, baseline flaw failed to reproduce, or flaky execution. |

---

## 📚 Project Documentation & Specifications

Complete technical specifications and implementation guides are available in this repository:

* 📄 [Project 1 Official Course Specification (Persian PDF)](./پروژه%20۱.pdf)
* 📋 [Technical Specification & Academic Requirements](./project_1_specification.md)
* 🗺️ [Actionable Implementation Roadmap & Milestone Plan](./IMPLEMENTATION_ROADMAP.md)
* 🎯 [Target Benchmark Selection & 4-Branch Engineering Guide](./TARGET_SELECTION_AND_SCENARIOS.md)
* 📐 [Technical Architecture, Algorithmic Specs & Schemas](./TECHNICAL_ARCHITECTURE_AND_SCHEMAS.md)

---

## 👥 Engineering Team & Subsystem Ownership

| Role | Subsystem Ownership | Key Focus Area |
| :--- | :--- | :--- |
| **Engineer 1** | **Build & Sandbox Harness** | Dual-build pipeline, Docker containerization, process runner, and ELF hardening auditor. |
| **Engineer 2** | **Crash Triage & Correlation** | Signal/sanitizer parser, `git diff` hunk analyzer, and caller-callee call-stack mapper. |
| **Engineer 3** | **Minimizer & Regression** | Delta Debugging (`ddmin`) algorithm, 3x replay reproducer packager, and regression test generator. |
| **Engineer 4** | **Targets, Reporting & CI/CD** | Target benchmarks (4 branches each), JSON audit reporting, and CI/CD workflow orchestration. |
