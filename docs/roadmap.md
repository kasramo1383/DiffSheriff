# Live implementation roadmap

This is the sole record of implementation state, remaining work, and verification
limits. Requirements remain in `course_assignment.pdf` and `specification.md`;
target facts belong in `target_scenarios.md`, and contributor ownership in README.

## Scope of this implementation

The requested work covers the defensive validator and its engineering support.
Exploit development, bypass inputs, intentionally vulnerable target variants, and
other aggressive functionality are excluded. Tests use synthetic diagnostic logs
and a harmless native echo program. They do not establish that a real vulnerability
was reproduced or that a target has instructor approval.

## Implemented and locally checked

- [x] Version 2 configuration: exact Git commit IDs, build commands, contained binary
  and suite paths, designated baseline signature, independent expected outcomes,
  environment, image, time, memory, CPU, process, and output limits.
- [x] Direct CLI-to-report orchestration in `pipeline.py`, with independent security,
  functional, and completeness statuses and priority `30 > 10 > 20 > 40 > 0`.
- [x] Source export without modifying the user's checkout; source archives/hashes,
  separate pristine base/patch release/sanitized trees, build logs and binary hashes.
- [x] Docker command construction: no network, no capabilities, no privilege gain,
  read-only execution mounts, limited resources, cleanup on failure, pinned local
  image identity, and a supervisor preserving actual signal return codes.
- [x] Identical suite discovery, independent expected-result checks, and three
  observations per input/version/mode; unsupported/unstable evidence fails closed.
- [x] Five finding statuses; corresponding modes never share comparison evidence.
- [x] ASan/UBSan categories, ordinary exits, signals, canary messages, timeouts,
  OOM/output limits, stdout/stderr, and source-location signatures.
- [x] Multi-file diffs, additions, deletions, renames, old/new coordinates, actual
  edited-line correlation, and caller frames. Unsupported attribution is inconclusive.
- [x] x86_64 ELF validation, release hardening comparisons, and minimum-policy checks.
- [x] Signature-preserving delta debugging, including empty inputs; independently
  approved expectations constrain reductions. An optional reference command permits
  expectations for additional reduced inputs without trusting target output.
- [x] Original/minimized inputs, replay logs, source versions, binaries, hashes,
  settings, commands, and functional-regression evidence retained in each run bundle.
- [x] Replay CLI with input/binary hash checks; generated regression manifests are
  automatically read on subsequent runs with the same baseline.
- [x] All five CLI exit paths checked using simulated process diagnostics; failure,
  missing correlation, missing baseline, hardening, timeout, unstable replay, archive
  traversal, minimization, and replay tampering tests.
- [x] Standalone instructions, schema migration guidance, runtime image, and CI jobs.
- [x] Clean-source Linux snapshot, runtime-image build, real native build/run/ELF
  inspection, all three input interfaces, and a separate actual CLI invocation.

Verification: **91 tests passed on Linux, including the real Docker smoke test**;
**90 passed on Windows, with the Docker test skipped there**. Black, Flake8, and
wheel packaging pass. A separate native CLI run completed 36 suite executions and
correctly returned `40` with functional PASS, because the harmless fixture has no
baseline security flaw. Local evidence is retained in `.diffsheriff/native-tests.xml`,
`.diffsheriff/native-validation-report.json`, and `.diffsheriff/native-evidence-final/`.
No real security target was executed. The GitHub-hosted workflow itself was not run.

## Next actionable work

The generic defensive implementation and local verification are complete within
the requested scope. No exploit or aggressive target work is assigned to the agent.
The remaining course deliverables require supplied target assets or human participation:

- [ ] Record two instructor-approved targets, including one real non-toy project.
- [ ] Supply exact target provenance, approved independent ground truth, and the four
  source scenarios and existing permitted corpora. See `target_scenarios.md`.
- [ ] Evaluate those supplied scenarios and independently prepared unseen patches.
- [ ] Conduct the contributors' comprehension and live defense review.

## Durable constraints and limitations

- Keep the package flat; no plugin framework, database, web service, or forwarding layers.
- No target-name, filename, branch-name, or patch-hash verdict selection.
- Target/configuration and runtime-image selection are trusted operator inputs.
- Only local source snapshots are used; symlinks and unvendored submodules are
  rejected instead of silently building incomplete or uncontained source.
- Sanitizer identities require a recognized error and source location. Ambiguous
  line mappings or absent stacks cannot establish patch causation.
- Without a reference command, minimization is restricted to independently specified
  corpus payloads; this bound is recorded in each reproducer.
- Preserve the entire run directory when moving a reproducer. Runtime image and
  DiffSheriff installation are external dependencies; the recorded image ID must be
  available. The run is not a standalone VM image.
- Do not check off instructor approval, real-target acceptance, or human defense
  work based on an agent-generated fixture or documentation.
