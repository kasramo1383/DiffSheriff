# Live implementation roadmap

This is the sole authoritative record of implementation state, blockers, and next
work. It is intentionally not divided into phases, chunks, sprints, or assignments.
Any coding agent should be able to stop after a coherent change, update this file, and
hand the repository to another agent without transferring chat history.

## Handoff rules

Before changing code, read:

1. `course_assignment.pdf` and `specification.md` for requirements;
2. `architecture.md` for invariants and simplicity constraints;
3. `target_scenarios.md` for approved target facts;
4. the next actionable work below.

Before stopping:

- run the tests proportionate to the change;
- update the checked capabilities and rewrite the next actionable work if necessary;
- put target facts only in `target_scenarios.md` and contributor ownership only in the
  README;
- record only a current blocker or durable technical decision, never a dated progress
  diary, chat summary, sprint artifact, or generated activity log;
- leave the repository in a state where the next agent can identify the first useful
  action from this file alone.

## Verified capabilities

- [x] Flat Python package and install metadata
- [x] Fail-closed configuration parsing for the present example schema
- [x] Release/sanitized build helper with retained artifact copies and hashes
- [x] Process execution through stdin, argv, or a temporary file with timeout capture
- [x] Basic ASan, UBSan, stack-canary, and signal triage
- [x] Basic unified-diff parsing and stack-frame correlation
- [x] Standalone invariant-preserving byte-level delta debugging
- [x] ELF NX, PIE, RELRO, and canary inspection primitives
- [x] Exit-code priority resolver and basic JSON writer
- [x] Unit tests for the current primitives and fail-closed CLI behavior

These are primitives, not an end-to-end validator. The CLI correctly returns
`INCONCLUSIVE` until mandatory orchestration and evidence are complete.

## Next actionable work

Implement the minimal explicit end-to-end path using one synthetic integration target.
Work from the first unchecked item downward; an agent may complete any coherent subset
and then update this section.

- [ ] Extend configuration with exact base and patch refs, build commands, binary
  paths, test-suite locations, independent functional oracle, execution environment,
  and resource limits.
- [ ] Add one direct orchestrator module, preferably `pipeline.py`; do not introduce a
  framework or additional architectural layer.
- [ ] Prepare base and patch source trees separately and build release and sanitized
  artifacts for both.
- [ ] Discover valid, boundary, and malicious inputs and execute corresponding builds
  under equivalent settings in the isolated Linux environment.
- [ ] Compare functional and security observations without mixing release and
  sanitized evidence.
- [ ] Implement the five finding statuses and prevent `PASS` unless the baseline flaw
  was reproduced and every mandatory check completed.
- [ ] Emit the complete JSON evidence report and concise developer summary.
- [ ] Add an integration fixture covering exit codes `0`, `10`, `20`, `30`, and `40`.

Completion condition: the synthetic fixture exercises the complete CLI-to-report path
and demonstrates fail-closed behavior. Once complete, replace this section with the
next highest-value unfinished capability rather than appending a historical summary.

## Other required capabilities

These remain required but do not define separate implementation phases. Work may move
between them whenever dependencies permit, provided the next actionable work stays
accurate.

- [ ] Normalize and retain ordinary exits, signals, sanitizer findings, stack-canary
  failures, timeouts, stdout, and stderr.
- [ ] Identify corresponding findings across builds using error type and relevant
  location rather than a generic nonzero exit.
- [ ] Parse multi-file diffs, additions, deletions, and renames robustly.
- [ ] Add caller/callee or execution-path evidence where stack-to-hunk intersection is
  insufficient; unsupported attribution remains inconclusive.
- [ ] Integrate hardening comparison for ordinary base and patch binaries.
- [ ] Replay confirmed findings at least three times and classify instability.
- [ ] Minimize inputs while preserving the finding signature.
- [ ] Produce a self-contained reproducer bundle with original/minimized input,
  versions, hashes, settings, command, and replay logs.
- [ ] Insert minimized cases into the regression suite and verify baseline-fail and
  correct-patch-pass behavior.
- [ ] Record instructor approval for two targets, including one real non-toy project
  or library.
- [ ] Preserve exact target provenance, four required versions, independent ground
  truth, and valid/boundary/malicious corpora.
- [ ] Demonstrate expected `0`, `10`, and `20` outcomes without recognizing target
  names, file names, commit IDs, or patch hashes.
- [ ] Test unseen patches prepared independently from the validator implementation.
- [ ] Verify a fresh checkout can build, run, inspect, and reproduce all deliverables.
- [ ] Complete the team comprehension and defense review described in the README.

## Current blockers

- The two target programs, their vulnerability/patch provenance, functional ground
  truth, and instructor approval are not yet established. Their status belongs only in
  `target_scenarios.md`.

The synthetic end-to-end fixture and generic orchestration can proceed without target
approval.

## Durable implementation constraints

- Keep the package flat and the main call flow explicit.
- Prefer plain functions and dataclasses over class hierarchies.
- Add an abstraction only when both targets or a tested invariant require it.
- Do not add plugin systems, dependency-injection containers, event buses, databases,
  web services, or forwarding-only service layers.
- Keep target-specific behavior in configuration and target assets, not Python
  conditionals keyed by target identity.
- Do not create issue-board, sprint, story-point, or activity-log files.
- Use CI/CD only for the assignment's validator integration and automated verification.
- Agent-generated implementation is acceptable only when the assigned contributor can
  explain its logic, failure behavior, and tests accurately and efficiently.
