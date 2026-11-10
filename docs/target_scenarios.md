# Target selection and scenario record

## Current status

No course target, vulnerability, patch set, functional oracle, or expected-result
corpus is recorded as instructor-approved. `configs/example_target.yaml` is only a
schema example. `tests/fixtures/harmless/main.c` is an engineering smoke fixture,
not a course target: it safely echoes bytes and contains no vulnerability or exploit.
Synthetic sanitizer logs in unit/integration tests verify report logic only.

Exploit development, bypass inputs, and intentionally vulnerable target variants
are excluded by the user's scope. The approval table below must remain pending until
the team supplies real target facts and instructor confirmation.

This document becomes the authoritative project record for target facts once the team and instructor establish them. Do not duplicate mutable target facts in the README or roadmap; link here instead.

## Approval record

Complete this section only from primary upstream sources and instructor confirmation.

| Field | Target 1 | Target 2 |
| --- | --- | --- |
| Name and role | Pending | Pending |
| Real non-toy project/library? | Pending | Pending |
| Upstream source URL | Pending | Pending |
| License | Pending | Pending |
| Vulnerability identifier/source | Pending | Pending |
| Vulnerable source ref | Pending | Pending |
| Correct upstream patch ref | Pending | Pending |
| Input interface | Pending | Pending |
| Independent functional specification/tests | Pending | Pending |
| Instructor approval evidence/date | Pending | Pending |

At least one target must be a real, non-toy project or library. Both must be C/C++, buildable from source as Linux x86_64 ELF executables, and configurable without target-specific logic in DiffSheriff.

## Scenario contract for each target

| Version | Required behavior | Expected overall exit |
| --- | --- | ---: |
| Vulnerable baseline | At least one memory error is reproducible and described by stable evidence. | Not evaluated alone |
| Correct patch | Target error absent within the test scope; valid functional suite passes; no other confirmed security flaw; mandatory analysis complete. | 0 |
| Incomplete patch | Original trigger is blocked, but a distinct recorded input still reaches the same underlying flaw. | 10 |
| Regression patch | Target flaw is blocked, but at least one independently valid behavior that passed on baseline fails. | 20, unless code 10 or 30 also applies |

For every version, record an exact commit/ref and ensure the source is stored or reproducibly obtainable under the delivery rules. Do not select results by branch name, file name, commit ID, or patch hash.

## Per-target evidence checklist

### Provenance and builds

- Exact upstream source and license
- Exact four source refs
- Reproducible release and instrumented build commands
- Produced binary paths and SHA-256 hashes
- Linux x86_64 ELF confirmation
- NX, PIE, RELRO, and canary evidence for ordinary binaries

### Independent functional ground truth

- Authoritative specification or upstream tests
- Instructor-approved expected outputs and exit codes
- Valid input suite
- Boundary input suite
- Invalid/malicious input suite
- Identical corresponding execution settings across versions

### Vulnerability evidence

- Original trigger and at least one distinct bypass input for the incomplete patch
- Error category and detection mechanism
- Release and instrumented observations kept separate
- Relevant stack/execution-path evidence
- Patch diff and correlation evidence
- Original and minimized inputs
- Three or more replay results and stability classification

### Regression evidence

- Valid input that succeeds on baseline
- Independent expected behavior
- Patch result demonstrating the violation
- Evidence that the result is functional, not merely an unrelated build/config failure

## Selection risks to reject early

- The target is actually a script, service-only web application, or managed runtime.
- The historical version no longer builds reproducibly in the agreed environment.
- The alleged vulnerability or patch cannot be tied to a primary upstream source.
- The trigger is unreliable or requires prohibited external infrastructure.
- Functional correctness would be inferred from the patched binary itself.
- The proposed incomplete patch merely creates a different bug instead of leaving the same flaw reachable.
- The regression scenario lacks a legitimate valid input and independent expected result.
- Licensing or redistribution prevents inclusion or reproducible acquisition for delivery.

## Defense-day validation

Before delivery, have someone outside the implementing subsystem prepare unseen patches within the agreed target domain and interface. Retain only the input configuration and observed evidence; do not add patch-specific recognition logic.
