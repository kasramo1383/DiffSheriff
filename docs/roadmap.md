# Implementation roadmap

This roadmap records acceptance gates. A checked item must be supported by tests and reproducible evidence; file presence alone is not completion.

## Current baseline

- [x] Package layout and install metadata
- [x] Fail-closed configuration parser for the present schema
- [x] Primitive release/sanitized build helper
- [x] Primitive process runner and timeout capture
- [x] Basic sanitizer/signal triage
- [x] Basic unified-diff and stack-frame correlation
- [x] Standalone byte-level delta debugger
- [x] ELF hardening primitives
- [x] Exit-code priority resolver and basic report writer
- [ ] Any end-to-end patch validation
- [ ] Any approved target or required target scenario

## Gate 1: trustworthy execution substrate

- Define an explicit, versioned configuration schema for exact base and patch source refs, build commands, binary paths, input delivery, test suites, independent oracle, environment, and limits.
- Materialize base and patch in separate immutable work directories.
- Build four independent artifacts: base release, base sanitized, patch release, patch sanitized.
- Run target processes inside a Linux x86_64 isolated environment with enforced time, CPU, memory, process, and filesystem limits.
- Preserve commands, compiler settings, environment, commits, binary hashes, and complete logs.
- Test clean failures, build failures, missing artifacts, timeouts, signals, binary payloads, and cleanup.

Acceptance: a synthetic fixture proves that all four artifacts and runs are distinct, reproducible, and fully described without claiming a security verdict.

## Gate 2: evidence and comparison model

- Discover and classify valid, boundary, and invalid/malicious test inputs.
- Execute the same corpus under corresponding conditions for all four artifacts.
- Evaluate valid behavior through the independent oracle established before testing.
- Normalize sanitizer errors and stack signatures without collapsing release and sanitized observations.
- Represent security, functional, hardening, and completeness outcomes independently.
- Implement the `Fixed`, `Incomplete Fix`, `New Issue`, `Functional Regression`, and `Inconclusive` state machine.

Acceptance: table-driven fixtures cover all statuses, concurrent outcomes, flaky reproduction, and exit-code priority `30 > 10 > 20 > 40 > 0`.

## Gate 3: correlation and reproducibility

- Parse renames, additions, deletions, and multi-file Git diffs reliably.
- Retain direct stack-to-hunk evidence and add execution-path/caller-callee evidence where required.
- Mark unsupported causal attribution inconclusive.
- Replay each confirmed finding at least three times and record stability.
- Minimize while preserving error category and relevant location/signature.
- Package original/minimized input, commits, binary hashes, build settings, environment, command, and replay logs.
- Insert minimized cases into the regression suite and verify baseline-fail/patch-pass expectations.

Acceptance: an integration fixture produces a self-contained, independently replayable bundle and regression test.

## Gate 4: complete reporting and CI

- Define and validate the final JSON evidence schema.
- Produce a concise developer summary without discarding simultaneous findings.
- Integrate hardening evidence and degradation warnings.
- Guarantee that `PASS` is impossible when a mandatory stage is missing or incomplete.
- Run unit and integration fixtures in CI; separately run the complete validator against target scenarios.

Acceptance: CI verifies JSON schema, all exit codes, simultaneous findings, and fail-closed behavior.

## Gate 5: approved targets and defense readiness

- Record instructor approval for two targets, including one real non-toy project/library.
- Preserve exact provenance and four required versions per target.
- Establish independent functional ground truth and valid/boundary/invalid suites.
- Demonstrate expected `0`, `10`, and `20` outcomes without target-name, file-name, or patch-ID shortcuts.
- Test unseen patches created independently of the implementation team.
- Ensure every member can explain owned code, trace a finding to evidence, and implement and test a limited live change.

Acceptance: a fresh isolated checkout reproduces all required deliverables and defense scenarios from the standalone instructions.
