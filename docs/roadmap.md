# Requirements, evidence, and remaining work

This is the sole live acceptance record. The [original assignment](course_assignment.pdf)
is authoritative; [specification.md](specification.md) is its English digest.
[Target scenarios](target_scenarios.md) owns source identities and scenario construction;
[evaluation.md](evaluation.md) owns execution commands. Checkpoint records describe
historical revisions only. The review below examines checkout `705841e` on 2026-11-17;
it does not assert that missing runs never happened elsewhere.

## Acceptance assessment

The generic validator is substantially implemented. The delivered selected-target
assets do not establish completed course acceptance. Earlier claims that Stages 3-6
were complete, all six runs passed, 214 tests passed on the final revision, every
binary had full hardening, and blind preparation was ready exceeded the locally
retained evidence. No selected-target report, console log, or complete reproducer run
is present under `artifacts/`; generated regression files alone cannot establish those
claims. The recorded hosted verification predates the latest target/pipeline changes.

## Assignment-to-execution audit

Page numbers refer to the six-page Persian PDF. Findings concern the delivered files;
this review did not execute historical vulnerable binaries or dispatch CI.

| Requirement | Delivered implementation/evidence | Gap and consequence |
| --- | --- | --- |
| C/C++ Linux x86_64 targets, real dynamic execution, configuration-based onboarding (p. 1) | Generic Docker runner, ELF validation, separate build snapshots; two source bundles and six configs. Historical harmless native runs exist. | Real library sources are delivered, but their claimed final dynamic outcomes lack retained reports. Generic tests cannot establish target acceptance. |
| Independent expected behavior for valid and invalid inputs, instructor approval before evaluation (pp. 1-2, 4) | Both `evaluation/target*/reference.py` scripts discard stdin and return the same successful empty-output expectation with `valid_input: false`. Manifests also expect only exit 0 and empty output. | These scripts do not validate compression, PNG decoding, or candidate validity. No instructor approval evidence is supplied. Config provenance formerly said “Approved” and now explicitly records the pending review. Project-owner authorization cannot satisfy instructor approval. |
| Preserve actual program functionality (pp. 1-2) | zlib driver calls deflate then discards compressed bytes. PNG driver discards pixels, ignores `png_image_finish_read` failure, and returns 0 even when initial decoding fails. | Corrupted output or rejected valid input can pass. Expose deterministic semantic results, independently check decompression/pixels and error behavior, then define expectations before rerunning. |
| Fixed, incomplete, new, regression, inconclusive; runtime-to-diff evidence (p. 2) | `compare_case`, source signatures, direct/caller/function correlation, generic tests. | Latest “Edit in observed function” evidence establishes a shared function, not execution of the changed branch. That limit is stated in code. Real-target raw stacks/diffs and attribution remain unauditable without run bundles. No additional new-issue target variant is explicitly required by the PDF. |
| Valid, boundary, invalid suites and equivalent release/sanitized execution (p. 2) | Corresponding-mode matrix implemented. zlib has six corpus entries; PNG has four, with an empty invalid PNG as its only boundary case. | Coverage is narrow, especially valid PNG boundaries. zlib accepts arbitrary byte strings, so naming its memory-error triggers “invalid” does not establish semantic invalidity. Document actual validity and meaningful boundaries. |
| Exact identities, environment, commands, three replays, original/minimized inputs (p. 3) | Replay and bundle creation implemented; historical synthetic/native bundles retained. | Selected-target full reports, binary/build hashes, replay observations, commands and original/minimized pair bundles are absent. Seven generated manifests contain inputs/identities but are insufficient reproducer evidence. |
| Automatic minimization preserving error/location (p. 3) | Pipeline checks source signatures and stability; `ddmin` now stops at default `max_granularity=16`. | A reduction attempt is not proof of minimality. The cap can stop while removable bytes remain; no stop reason or achieved minimality is returned. The PDF requires automatic shrinking preserving the finding, not a mathematical global minimum. Retain actual reduction and replay evidence. |
| Automatically enroll and exercise regressions, checking baseline error and correct behavior (p. 3) | Generated inputs/manifests are loaded for exact baselines. | All three generated functional manifests set `valid_input: false`; `compare_case` requires true to classify a functional regression. Their future loading does not establish functional-regression coverage. “Full” expectations obtained from constant references need independent review. No retained later-run demonstration exists. |
| NX, PIE, RELRO, canary, and downgrade warnings on ordinary binaries (p. 3) | ELF inspection/comparison implemented; configs demand all four protections. | Bundled Makefiles do not request stack protection or full RELRO and use `CC ?= clang`, which can yield make's built-in `cc`. Docker installs unversioned packages. No final target ELF evidence supports the prior blanket hardening claim. Required policy is not measured status. |
| CLI, JSON, independent statuses, priority `30 > 10 > 20 > 40 > 0`, CI/CD (p. 3) | CLI/reporting/priority tests and two workflows implemented. | `validate_target.yml` never clones the source bundles into the config's ignored `repository` paths; a fresh runner cannot resolve them. Retained hosted record covers an older generic revision with target job skipped. Six isolated expected codes would not alone prove simultaneous-condition priority. |
| Two independent programs, four versions each (p. 4) | zlib and libpng bundles contain four exact local commits each. Libraries and retained upstream source are real. Incomplete variants edit library code; regression variants edit drivers. | Local bundle refs differ from upstream refs and were previously undocumented. Driver regressions are deliberately constructed examples: zlib rejects a literal prefix and PNG rejects tall images. Disclose that limited scope; they do not demonstrate detection of an organic library semantic regression. libpng uses system zlib, distinct from Target 1's source tree, but its package version is not pinned. |
| Standalone source, tests, reproducers, reports, pipeline, instructions (p. 4) | Bundles, configs, corpora, tool source, instructions and historical generic evidence exist. | No selected-target clean-checkout/replay record or final package tied to current source. The claimed 18.07 MB archive has no retained command/hash. The PDF has no 20 MB cap; remove it as an assignment acceptance condition. |
| Unseen patches at defense (p. 4) | Generic pipeline has no observed branch on target name or known patch identity. | No delivered hidden-label package, answer key or observed blind result supports the prior readiness claim. A local rehearsal package is useful preparation; the PDF requires the actual defense-day evaluation, not a specific package format. |
| Genuine contribution and individual unaided defense (pp. 4-6) | README assigns roles; defense guide provides study paths. | Assigned ownership does not establish actual participation or competence. Each member must demonstrate their real contribution and pass the individual thresholds. Tool implementation cannot complete these human requirements. |

## Actionable fixes and acceptance tests

All items below are open. Check an item only after its acceptance tests pass and its
evidence is retained for the exact tested source/image. Update status here; keep
source identities in [target_scenarios.md](target_scenarios.md), commands in
[evaluation.md](evaluation.md), and results in their own artifact records. Extend
existing tests where needed instead of duplicating coverage. F01 is the first action;
F02 and F04 can proceed independently. External review does not prevent technical work.

### F01 - Make zlib behavior observable and independently checked

- **Fix:** Define the driver contract for every byte stream, including empty input.
  Expose deterministic compressed output or independently checked round-trip evidence.
  Replace the constant zlib reference with a specification-based check of recovered
  bytes and failure behavior. Do not require identical compressed bytes from different
  valid compressors. Update all scenario drivers consistently through F05.
- **Tests:** Empty, ordinary text and binary inputs round-trip to the original bytes.
  Truncated or deliberately corrupted compressed output fails the check. A fake target
  that exits 0 while producing incorrect data must fail functional validation. Test
  reduced-input expectations and validity without using either target's observations.
- **Accept:** The frozen contract and reference distinguish actual correct compression
  from constant success, and deterministic expected CLI results are independently derived.

### F02 - Make PNG decode results and failures observable

- **Fix:** Define output using dimensions, a fixed pixel format and deterministic pixel
  bytes/digest. Check both begin-read and finish-read results; handle allocation failure.
  Define explicit malformed-input behavior and replace the constant PNG reference with
  an independent decoder or independently verified fixtures. Keep the vulnerable API
  path exercised without suppressing diagnostics. Apply common driver changes via F05.
- **Tests:** Independently known pixels and dimensions match. Corrupted/truncated files
  and finish-read failures cannot return apparent success. Include valid small images
  and supported format variants. A fake successful decoder with wrong pixels is rejected.
- **Accept:** Both successful decoding and error behavior have independently checked,
  deterministic expectations; the memory-error reproducer still exercises its API path.

### F03 - Correct corpus validity, boundaries and provenance

- **Depends on:** F01, F02.
- **Fix:** Review every existing suite input and expectation. Separate semantic validity
  from whether bytes trigger a memory error. Add meaningful valid boundaries for each
  supported driver contract, including valid PNG boundaries and malformed/truncated PNGs.
  Record each case's purpose, source/specification and validity in the owning target
  record or corpus manifest. Preserve identical corresponding inputs across versions.
- **Tests:** Discover every expected case exactly once; verify payload hashes, missing
  and extra manifest keys, expected outputs and validity. Exercise both valid and invalid
  boundaries. A valid-input mismatch must be distinguishable from a security diagnostic.
- **Accept:** Every suite expectation has a reviewable independent basis and every
  category has meaningful coverage within a documented bounded scope.

### F04 - Make target builds and hardening reproducible

- **Fix:** Choose an explicit compiler rather than relying on `CC ?= clang`. Specify
  intended release/sanitizer flags and the requested protection policy. Pin or provide
  reproducible acquisition of toolchain/system dependencies and retain actual versions,
  including libpng's system zlib. Keep Target 1's experimental zlib out of Target 2.
- **Tests:** Fresh release and sanitized builds for all eight source variants produce
  x86_64 ELF files; release has no sanitizer contradiction. Inspect NX, PIE, RELRO and
  canary evidence rather than inferring it from flags. Exercise protection downgrade
  warnings with harmless fixtures. Verify image identity and equivalent per-mode settings.
- **Accept:** Builds from delivered assets satisfy the declared policies and record
  compiler, linker, dependency, binary and image identities. Reuse existing builder,
  source, ELF and container tests; retain actual target build logs through F09.

### F05 - Reconcile scenario source versions and rebuild the bundles

- **Depends on:** F01, F02, F04.
- **Fix:** Review baseline/correct/incomplete/regression diffs for both targets after
  common driver/build changes. Keep the original upstream identity and map local edits.
  Document deliberate driver regressions and their limited scope; do not claim organic
  library regressions. Freeze new exact refs and update all six configs and the owning
  target record together. Keep one source authority in the bundles.
- **Tests:** Verify both self-contained bundles in fresh temporary clones and resolve
  all eight configured commits. Check license notices, upstream-to-local differences
  and shared drivers/build settings. Smoke-check that the incomplete patch blocks the
  original trigger while the distinct input reaches the same underlying flaw, and the
  regression patch fixes that flaw while violating an independently valid behavior.
- **Accept:** Every scenario has an explainable source diff and observed intended
  behavior. Names and intended exit tables cannot substitute for the observations.

### F06 - Report minimization limits and verify the preserved finding

- **Fix:** Make the reduction budget/limit explicit and return a stop reason and
  original/reduced sizes in retained evidence. Review the hidden granularity cap;
  support an appropriate bounded reduction policy without claiming unproved minimality.
  Keep error/location and independent functional invariants intact.
- **Tests:** Add a case with removable bytes beyond the current granularity cap; show
  either further reduction or an explicit limit result. Cover unchanged payload, empty
  payload, wrong location/type, unstable replay, resource limits and unknown reduced
  expectations. Reuse `tests/test_minimizer.py` and pipeline minimization tests.
- **Accept:** Evidence distinguishes successful shrinking, a limit stop and an unchanged
  input, and the retained result repeats the relevant finding at least three times.
  The assignment does not require proof of a mathematical global minimum.

### F07 - Repair generated-regression validity and full checks

- **Depends on:** F03, F05, F06.
- **Fix:** Review all seven existing generated manifests against their exact bytes and
  repaired references. Revalidate or regenerate stale cases for the new baselines.
  Establish validity independently; do not simply flip every flag to true. Unknown
  behavior remains diagnostic-only. Correct the three functional manifests currently
  marked invalid where actual independent validation supports that correction.
- **Tests:** Run a valid minimized functional case on baseline and regression patch;
  require the expected mismatch to be detected. Require baseline security reproduction
  plus correct-patch expected behavior for a full security regression check. Test
  unknown expectations, exact-baseline filtering and preserved build-mode separation.
- **Accept:** Later-run functional checks cannot silently lose regression eligibility,
  and every full expectation has an independent basis. Retain later-run evidence in F09.

### F08 - Validate correlation and its uncertainty

- **Fix:** Review the new function-level edit rule against the PDF's runtime-evidence
  standard. Preserve the distinction between observed function/path relation and proof
  of causation; adjust logic only when a concrete counterexample requires it.
- **Tests:** Extend existing correlator/pipeline coverage for edited callers, shifted
  unchanged lines, same-name functions in other files, absent/ambiguous context, unrelated
  edits in an observed function and disagreement across replays. Unsubstantiated
  attribution stays inconclusive. Inspect real stacks and diffs during F09.
- **Accept:** Direct, caller and function relations are accurately labelled with their
  limits, and no Fixed verdict depends on unsupported attribution or unknown behavior.

### F09 - Retain all six target evaluations and later-run checks

- **Depends on:** F03-F08.
- **Fix:** Follow [evaluation.md](evaluation.md) for both targets against correct,
  incomplete and regression variants. Diagnose unexpected codes without forcing the
  expected result. Retain separate complete runs, including meaningful failed attempts.
- **Tests:** Corresponding release/sanitized settings and inputs; expected overall
  codes 0/10/20 when justified; raw category/mechanism/exit/signal/output/limit records;
  hardening; correlation; exact source/binary/image identities; original/minimized
  inputs; at least three stable replay observations for confirmed findings. Run both
  correct configs again with generated cases loaded and replay a baseline finding per
  target with `--check-regression`.
- **Accept:** Six explainable comparisons and both later correct runs are reproducible
  from retained artifacts under `artifacts/evaluation/`, with independent security,
  functional and completeness statuses. Missing evidence keeps this item open.

### F10 - Repair target CI setup and exercise the real gate

- **Depends on:** F05; successful target acceptance also needs F07-F09.
- **Fix:** Add safe source-bundle cloning before validation in `validate_target.yml`.
  Preserve actual CLI exit gating and regression-cache reconciliation. Never overwrite
  an existing modified target checkout or convert expected failures into passing gates.
- **Tests:** Start without ignored `repository/` directories, resolve the configured
  commits, and run both correct configurations successfully. Confirm incomplete and
  regression variants fail the CI gate with their actual codes. Exercise empty/restored
  caches and artifact retention on failures. Validate workflow syntax and shell quoting.
- **Accept:** Fresh CI setup works from delivered files and available verification
  evidence is retained. A GitHub-hosted run is useful corroboration; the PDF requires
  working CI/CD without prescribing that provider. Keep unrun hosted checks explicit.

### F11 - Verify final exit priority and generic behavior

- **Fix:** Inspect existing reporter/pipeline tests and add only missing simultaneous
  outcome coverage. Keep operational failures and all collected findings in JSON.
- **Tests:** Exercise 0, 10, 20, 30 and 40 and all combinations of operational error,
  confirmed security issue, functional regression and incomplete analysis. Require
  `30 > 10 > 20 > 40 > 0`, matching CLI/JSON results and preserved independent statuses.
  Run focused tests after fixes; run `bash verify.sh` on the final candidate revision
  with prerequisites installed. Distinguish harmless native evidence from target results.
- **Accept:** Relevant tests, formatting, lint, native smoke and packaging pass for the
  final tested source; record actual counts, skips, commands and identities.

### F12 - Verify standalone delivery from a clean checkout

- **Depends on:** F09-F11.
- **Fix:** Complete the delivered install/build/validation/replay instructions and
  package only required source, licenses, configurations, tests, reports and evidence.
  Declare external tools and how the exact recorded image remains available.
- **Tests:** In a fresh location with no ignored developer state, install the package,
  build/acquire the declared runtime, clone bundles, validate both correct patches,
  load generated regressions and replay one finding per target. Verify all retained
  hashes and documentation links. Remove task-created intermediate files afterward.
- **Accept:** Another engineer can execute the delivery without chat history or old
  machine paths. Record archive hash/size only for an actual delivered archive; the
  PDF specifies no 20 MB acceptance cap.

### F13 - Prepare unseen-patch rehearsal and individual study

- **Depends on:** F09, F12.
- **Fix:** Make the existing [defense guide](defense_guide.md) trace real target evidence
  and meaningful small changes for each README-owned subsystem. Prepare optional
  hidden-label scenarios, a separately held answer key, invocation instructions and a
  result worksheet without copying mutable source identities into another authority.
- **Tests:** Verify rehearsal setup from delivered assets, capture the tool result
  before revealing the answer, and check that neutral labels do not change verdicts.
  Have each contributor trace a finding and practice a small change with its tests.
- **Accept:** Materials work and accurately describe observed practice. A prepared
  package or assigned role does not establish a completed independent exercise,
  genuine contribution, or passed defense.

### External requirements

- **E01 - Instructor design approval:** Present the final target provenance, scenarios,
  independent references and expected valid/invalid behavior for review (PDF pp. 1-2,
  4). Record the actual response/source when available; keep provenance pending until
  then. An agent may prepare the materials and continue technical work independently.
- **E02 - Participation and defense:** Each contributor must establish actual work and
  complete the required unaided individual defense and instructor unseen-patch testing
  (PDF pp. 4-6). Retain only real evidence. These events cannot be completed by an agent.

## Retained evidence and verification limits

[artifacts/README.md](../artifacts/README.md) indexes the retained checkpoints and their
scope. Their manifests preserve original bytes and source identities. Newer source
changes prevent transferring historical passes to the current revision automatically.
The instructor PDF controls scoring; no numerical grade is inferred from this review.

## Cleanup verification

Both source bundles passed `git bundle verify` before the disposable checkout cleanup
was attempted. Duplicate corpora matched byte-for-byte, and duplicate drivers matched
bundled baseline source after CRLF normalization. All 373 remaining artifact-manifest
entries and seven generated input hashes matched their delivered bytes; 59 local
Markdown links resolved. `git diff --check` passed. The selected-target matrices were
not rerun for this documentation/artifact cleanup. The host Python lacks pytest, so
the retained-manifest assertions were checked directly with the standard library.

Tracked obsolete artifacts, duplicate source paths and tool-specific handoff prompts
were removed. The stale local chat-context pointer was also removed. Ignored caches
and disposable `evaluation/target*/repository` checkouts remain local pending manual
cleanup; their tracked source bundles are intact. Use the single
[agent handoff prompt](agent_handoff_prompt.md) to continue the fixes above.
