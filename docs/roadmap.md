# Implementation roadmap

This roadmap defines three coherent delivery chunks. One or two coding agents may
implement each chunk in a large pass, including its tests and necessary documentation.
The assigned human owner reviews the result and must be able to explain it before the
chunk is accepted. File presence or generated prose is not evidence of completion.

There is no sprint plan, issue-board workflow, story-point system, or per-task activity
log. CI/CD work is limited to the validator behavior and automated verification required
by the assignment.

## Current baseline

- [x] Flat Python package and install metadata
- [x] Fail-closed configuration parsing for the present example schema
- [x] Primitive release/sanitized build helper
- [x] Primitive process runner and timeout capture
- [x] Basic sanitizer/signal triage
- [x] Basic unified-diff and stack-frame correlation
- [x] Standalone byte-level delta debugger
- [x] ELF hardening primitives
- [x] Exit-code priority resolver and basic JSON writer
- [ ] End-to-end patch validation
- [ ] Approved targets and required target scenarios

## Chunk 1: end-to-end core pipeline

Implement the shortest explicit path from configuration to a defensible verdict:

- extend the configuration with exact base and patch refs, build commands, binary
  paths, input delivery, test suites, independent functional oracle, environment, and
  resource limits;
- prepare base and patch source trees separately and build release and sanitized
  artifacts for both;
- discover valid, boundary, and malicious inputs and run corresponding artifacts under
  equivalent settings in the isolated Linux environment;
- compare functional and security observations without mixing release and sanitized
  evidence;
- implement the finding-status model, exit-code priority, complete JSON report, and
  readable CLI summary;
- keep the orchestration in one explicit module and reuse the existing small helpers.

Acceptance: a synthetic integration target exercises `PASS`, remaining vulnerability,
functional regression, build/config error, and inconclusive outcomes. `PASS` is
impossible when the baseline flaw was not reproduced or a mandatory stage is missing.

Human review: Engineer 1 reviews build/execution behavior; Engineer 4 reviews the
orchestrator, reports, and complete call flow.

## Chunk 2: evidence, correlation, and reproducibility

Complete the evidence needed to defend each result:

- normalize ASan, UBSan, stack-canary, signal, timeout, and ordinary exit outcomes;
- identify corresponding findings across builds using error type and relevant location;
- parse multi-file diffs, additions, deletions, and renames and correlate stack or
  execution-path evidence without claiming unsupported causation;
- compare NX, PIE, RELRO, and stack-canary status on ordinary binaries;
- replay confirmed findings at least three times, classify instability, and minimize
  inputs while preserving the error signature;
- create a self-contained reproducer bundle and insert the minimized case into the
  regression suite;
- add focused unit tests and one end-to-end evidence fixture.

Acceptance: an independently invoked replay script reproduces the same finding and the
generated regression case fails on the vulnerable baseline and passes on the correct
patch. Ambiguous evidence remains `INCONCLUSIVE`.

Human review: Engineer 2 reviews triage and correlation; Engineer 3 reviews replay,
minimization, bundles, and regression generation.

## Chunk 3: approved targets and final delivery

- obtain and record instructor approval for two targets, including one real non-toy
  project or library;
- retain exact provenance, independent functional ground truth, test corpora, and the
  four required versions for each target;
- demonstrate expected exits `0`, `10`, and `20` without target-name, file-name,
  commit-ID, or patch-hash shortcuts;
- test unseen patches prepared independently from the validator implementation;
- run unit and integration tests in the repository workflow and run full target
  validation in the required isolated environment;
- finish only the standalone instructions and evidence needed to build, run, inspect,
  and defend the project.

Acceptance: a fresh checkout reproduces every required scenario and deliverable. Each
member can explain the overall pipeline, defend one real finding from evidence, and
make and test a limited change in their assigned subsystem.

Human review: Engineer 4 owns integration and target records; all four contributors
perform the final comprehension and defense review. Contributor identities and role
assignments are maintained only in the README.
