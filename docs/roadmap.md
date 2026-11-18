# Course requirements and remaining work

The [original Persian assignment](course_assignment.pdf) is authoritative.
[specification.md](specification.md) is its English digest. This roadmap owns current
acceptance status; [target_scenarios.md](target_scenarios.md) owns source identities
and scope, and [evaluation.md](evaluation.md) owns execution commands.

## Scope corrections after re-reading the assignment

The PDF assesses a configurable validator within an agreed target/input domain.
It does not require a production platform or exhaustive library validation. Earlier
roadmap items mixed necessary correctness checks with stronger engineering choices.
Use the following interpretation for all remaining work:

| Earlier demand or criticism | What the PDF requires |
| --- | --- |
| Independent decoder/reference executable for arbitrary reduced bytes | Define valid/invalid behavior, output and exit expectations before evaluation from documentation or independent tests (pp. 1-2). Fixed reviewed fixture expectations are sufficient. The reference command is optional; justify newly reduced cases individually when necessary. |
| Compressed bytes or pixel digests as mandatory output | Check independently specified correct behavior in the agreed scope (pp. 1-2). Choose a small meaningful observable contract. A particular output encoding or full decoder is not prescribed. Discarding output is not itself a violation; silently masking failures or unsupported expectations is a correctness concern. |
| Every format variant and broad boundary coverage | A documented valid, boundary and invalid suite under equivalent settings (p. 2). Use representative cases for the chosen interface; no corpus size, exhaustive feature coverage or scalability target is specified. |
| All targets must enable NX, PIE, full RELRO and canary | Inspect all four on release binaries, distinguish RELRO levels and warn about unintended downgrades (p. 3). Missing protection on both versions is not automatically a failed patch. The six target configs now use neutral absolute minima; inspection and downgrade detection remain active. |
| Pin every OS/compiler/dependency package or rebuild without caches | Preserve exact source, binary hash, build settings, relevant environment, commands and replay evidence; deliver runnable instructions (pp. 3-4). Record the actual toolchain/runtime used. Universal package locking and no-cache rebuilds are optional unless a concrete reproduction problem requires them. |
| Regression must be an organic library bug | Prepare a version fixing the flaw while breaking independently valid behavior (p. 4). A deliberately constructed driver regression can qualify if the driver is part of the declared target and independently valid behavior supports it. It must be described honestly, not replaced solely for realism. |
| Correlation must prove an edited branch executed or identify one unique hunk | Runtime file/function/stack or execution-path evidence plus comparative runs is acceptable (p. 2). No branch instrumentation or unique-hunk rule is prescribed. The current conservative ambiguity handling is an implementation choice; do not demand stronger tracing merely to satisfy it. |
| Prove minimum input size or add more reduction-management features | Automatically shrink a failing input while preserving error type/relevant location, keep both inputs and replay at least three times (p. 3). Demonstrate actual reduction where possible. No global-minimum proof, tuning UI or large-input optimization is required. |
| A separate New Issue target scenario | Support the finding category (p. 2); deliver baseline/correct/incomplete/regression versions for each target (p. 4). Extra target variants are optional. |
| Hosted GitHub runs, complex caches and workflow infrastructure | Working CLI/CI automation, readable and JSON results and the exact exit hierarchy (p. 3). Use the existing workflow; a named provider and elaborate cache scenarios are not grading requirements. |
| Hidden-label rehearsal package, answer key and worksheet | Handle unseen patches at the actual defense within the agreed domain/interface (p. 4). Rehearsal is optional preparation, not another mandatory deliverable. |
| 20 MB archive cap or mandatory archive format | Deliver the listed source, target versions, tests, reports, reproducers, pipeline and instructions (p. 4). No such size cap or archive format appears. |

Do not remove existing useful tests or features merely because they exceed the minimum.
Do not add new work for these optional choices. Historical checkpoints preserve what
was implemented and tested; they do not create new assignment requirements.

## Requirement-to-implementation check

| PDF requirement | Current assessment and necessary remainder |
| --- | --- |
| Configurable C/C++ Linux x86_64 targets and actual dynamic execution (p. 1) | Generic source/build/runner/ELF pipeline is implemented and tested. Both real library source bundles are delivered. Retain selected-target runs, not just harmless infrastructure tests. |
| Independent behavior for valid/invalid inputs, instructor design approval (pp. 1-2, 4) | The selected bounded contracts and fixture basis are documented in `target_scenarios.md`; instructor approval was waived by the course team. The live Target 1 reports expose an unresolved contract interaction: security-trigger inputs are labeled valid and expected to exit 0, while the vulnerable baseline aborts on them. Resolve and document that distinction before accepting the report; see F09. |
| Correlation and Fixed/Incomplete/New/Regression/Inconclusive (p. 2) | Generic implementation and tests exist, but the live Target 1 report leaves attribution inconclusive when multiple edited hunks match observed stack functions. Resolve this target-level F08 gap and report the supported function-level relation; the assignment does not require branch tracing or proof of causation. |
| Valid/boundary/invalid suites, corresponding release/sanitized builds, error/mechanism/termination/output/limits (p. 2) | Generic support and selected corpus review are complete. Do not relabel valid zlib streams as invalid merely because the vulnerable baseline crashes. The unresolved issue is how the independent success contract applies to those security-trigger executions; see F09. No additional format coverage or corpus-size work is identified. |
| Reproducers, automatic reduction, three replays and enrolled later-run regressions (p. 3) | Generic behavior is verified. Target 1 has partial retained bundles, but its current correct/incomplete reports are analysis-incomplete, its regression attempt has no final report, and Target 2 has no runs. Selected-target minimization, replay, and later-run regression acceptance remain open. The two zlib functional manifests have independently justified validity; the retired PNG cases remain historical evidence. Keep unknown expectations inconclusive. |
| Release hardening inspection and downgrade warnings (p. 3) | F04 records native release observations for both targets and generic downgrade tests. Retain the tool's release hardening results from the delivery environment during F09. |
| CLI, JSON, independent statuses and priority `30 > 10 > 20 > 40 > 0` (p. 3) | F11 verifies all 16 combinations through CLI and JSON. CI now prepares the bundle-backed source directories and refuses existing destinations; full selected-target CI results remain pending. |
| Two independent programs, at least one real, four versions each (p. 4) | Two real libraries and all eight local snapshot refs exist. libpng uses system zlib rather than Target 1's tree. The course team waived instructor approval. The six scenario outcomes remain unaccepted until their reports are complete and match the declared contracts; deliberate driver regressions remain acceptable only when they break independently valid behavior. |
| Standalone delivery (pp. 4-5) | Source/assets/instructions exist; demonstrate target validation and replay from delivered files. Combine that check with the matrix work where possible rather than adding another full duplicate campaign. |
| Participation, unaided individual defense and unseen patches (pp. 4-6) | Existing ownership/study material is preparation. Actual participation and defenses remain external requirements, not agent implementation tasks. |

Generic verification is retained under [artifacts](../artifacts/README.md), including
the rebuilt-runtime retry. Earlier claims of completed selected-target matrices lack
full delivered reports/reproducer runs; they remain unverified rather than disproved.

## Remaining fixes and acceptance checks

The course team waived instructor approval; no approval request remains. The remaining
technical work is not only a final matrix run: resolve F08 correlation and the Target 1
valid-input expectation conflict first, set a usable minimization budget, then complete
and review all six target comparisons. Demonstrate selected-target regression
re-enrollment/replay, the target CI gate (F10), and clean-checkout delivery/replay (F12).
Generic F06/F08/F10/F11 checks are recorded separately from those target-specific
acceptance results.

### F01 - Justify the bounded zlib functional contract

**Implemented and verified for the documented completion/status scope.** The
[zlib/CI checkpoint](../artifacts/checkpoints/zlib-contract-ci/README.md) retains
independent API expectations, corrected validity and native baseline/correct/regression
checks in both modes. The contract does not claim validation of discarded output bytes.
The full security matrix remains separate work.

- **Fix:** Define what the selected driver promises for the chosen valid, boundary and
  trigger inputs and cite the independent documentation/test basis. Existing exact
  expected manifests may be enough if they genuinely check that contract. If they do
  not, add one simple observable result or independent round-trip check; do not build
  a general-purpose compression oracle. Review the constant reference's validity claims.
- **Check:** Selected ordinary/empty/boundary cases have independently justified results;
  the chosen functional regression passes on baseline and fails on its variant. A
  successful exit must not conceal a failure of the behavior actually being claimed.

### F02 - Justify PNG behavior and handle failures in that scope

**Implemented and verified for the selected native-format contract.** The
[PNG checkpoint](../artifacts/checkpoints/png-contract/README.md) records begin/finish/
allocation handling, reviewed fixtures and native results across all four variants.
The baseline/incomplete security paths remain observable; full F09 tool acceptance
and independent expectations for newly reduced bytes remain separate work.

- **Fix:** Define the supported decode/error behavior for the chosen fixtures. Check
  relevant read/finish-read/allocation results instead of silently treating failure as
  success. Use independently known fixtures or a small existing reference if needed;
  a general PNG decoder, all format variants and a mandatory pixel-output protocol are
  unnecessary. Change the driver only as required by the agreed contract.
- **Check:** The chosen valid image's required behavior and a representative malformed
  case are independently established; baseline/regression results distinguish them.
  Keep the vulnerable API path observable for the security scenario.

### F03 - Review the existing corpus and expectations

- **Depends on:** F01/F02 contract decisions.
- **Review verified (F03).**
  `python -m pytest -q tests/test_target_assets.py` passes
  (11) and all six configs load: target1 has 10 cases per variant and no
  `valid_input: false` case; target2 has 4 cases per variant with 3 invalid. The
  assignment (p. 2) requires the tool to run valid, boundary and invalid input suites on
  both versions. A native probe of the target1 release
  driver returned 0 for every suite and generated payload and for 65536/65537-byte and
  randomized inputs, and rejected only interface-level conditions (missing/unreadable
  path, missing `--file`) that a payload suite cannot express. The `65537 -> exit 2`
  result is therefore a reference scope check. The independent compression contract
  supports the Target 1 validity labels, but it does not justify the current expected
  exit for vulnerable-baseline runs. F09 reports show valid security-trigger inputs
  aborting in the baseline despite an expected exit of 0. The native release probe
  records exit behavior and does not establish memory safety. Target 2 supplies rejected
  inputs. Corpus validity review is complete;
  the target-run expectation interaction remains open under F09.
  The review evidence is retained
  under the [F03 corpus-review checkpoint](../artifacts/checkpoints/f03-corpus-review/README.md).
- **Remaining status:** F03 found no corpus correction or additional case necessary.
  Preserve the independently justified validity labels. F09 owns the separate issue
  that a valid security trigger is expected to exit 0 even though the vulnerable
  baseline aborts; resolve that contract interaction without changing labels to force
  a passing comparison.
- **Acceptance check:** Run the reviewed corpus/settings on corresponding target
  versions and report expectation mismatches honestly. No fixed corpus count or
  exhaustive library coverage is required.

### F04 - Confirm builds and measure hardening

- **Verified (F04).** All eight selected versions build natively (Debian clang 14.0.6,
  GNU make 4.3) to x86_64 ELF in ordinary and instrumented modes from the delivered
  bundles; no build or packaging change was needed. Every release binary shows NX=True,
  PIE=True, RELRO=partial, canary=False (the bundled default flags omit canary and full
  RELRO, and the six configs impose no absolute all-enabled minimum). Release and
  sanitized sha256 identities are retained under the
  [build/hardening checkpoint](../artifacts/checkpoints/build-hardening/README.md).
  Downgrade reporting was verified on real ELFs: baseline->correct reports no
  degradation; a deliberately weakened build (`-no-pie -z norelro -z execstack
  -fno-stack-protector`) reports NX, PIE and RELRO downgrades. `tests/test_hardening.py`
  passes (7).
- **Fix:** Establish which compiler, flags, dependencies and runtime are actually used
  and document sufficient setup to build/replay. Make compiler selection explicit only
  if required for consistent builds. Absolute minima in the six configs are neutral;
  retain ELF inspection and unintended downgrade warnings. Do not add package locking
  or force missing baseline protections on unless a demonstrated problem requires it.
- **Check:** Required source versions build to x86_64 ELF in corresponding ordinary and
  instrumented modes; retain actual NX/PIE/RELRO/canary observations and build identities.
  Reuse existing downgrade tests rather than adding an extra target variant for each flag.

### F05 - Update packaged sources only when needed

- **Verified (F05).** The earlier PNG driver update shipped new scenario refs and a
  refreshed source bundle. Legacy refs preserve the prior versions and the
  [PNG checkpoint](../artifacts/checkpoints/png-contract/README.md) records the
  transition. The subsequent recovery check found the four configured commits for
  each target in its delivered bundle. That check required no further packaging changes.

- **Depends on:** Any source changes in F01/F02/F04.
- **Fix:** If drivers/builds change, update the affected four scenario refs, bundles,
  configs and owning target record together. If existing source already meets the
  agreed contract, reuse it. Preserve licenses and local/upstream identity mapping.
- **Check:** All configured commits resolve from the delivered bundles. Correct,
  incomplete and regression versions meet their PDF definitions. Keep a deliberate
  driver regression if it meets those definitions; no realism-driven replacement is needed.

### F06 - Automatic reduction

**Generic implementation verified.** [Reduction evidence](../artifacts/checkpoints/reduction-limits/README.md)
covers error/location preservation, budgets and replay handling. No further minimizer
feature work is required. F09 must retain real-target original/reduced inputs and
three replay results; an unchanged limit stop alone does not demonstrate shrinking.

- **Operational gap (Target 1 minimization budget):** `max_oracle_calls` defaults to 256
  (`diffsheriff/minimizer.py`); none of the six target configs overrides it. The retained
  `target1/regression` attempt was interrupted during minimization and has no final report
  or matrix row. Containerized oracle calls each start a Docker lifecycle, so the current
  default is impractical for this run on the recorded WSL/Docker setup. Set and document a
  finite, usable per-config budget before resuming; preserve the actual stop reason and
  confirm the reduced reproducer still meets the required diagnostic/replay contract.

### F07 - Repair generated regression checks

**zlib validity repaired; legacy PNG cases retired; full later-run acceptance open.** Four zlib
manifests retain their original bytes/refs and now mark their valid compression inputs
correctly. Both functional cases are verified as eligible when the pipeline loads them.
PNG no longer enrolls the three obsolete-baseline cases or invents expectations for
unknown bytes; new-baseline generated regressions still need F09 demonstration.
Export refresh now retires stale files for the configured baseline. Local transfer
and CLI tests cover empty exports, shared payloads, and preservation on validation
errors. The [harmless CLI round trip](../artifacts/checkpoints/clean-checkout/README.md#actual-cli-in-the-local-ci-shell)
also generated, exported, imported, and reran two functional cases. Selected-target
later-run acceptance is still open.

The enrollment and replay contract is now covered by focused tests: a stable
minimized baseline failure is retained with its bytes, hash and baseline ref; a later
run for the same baseline loads it in its recorded mode and confirms the designated
diagnostic is absent from the correct patch; export refresh retires stale manifests
for that baseline while preserving other baselines; mixed valid and invalid external
manifests, and unverified cache-only expectations, are rejected before any write; and
`python -m diffsheriff.reproduce` returns 0 for a security reproducer with
`--check-regression` and for a functional reproducer, each after three replays per
side. These are generic fixtures. The selected-target later-run acceptance still
requires the six-comparison run below.

- **Depends on:** F03 and any changed baseline refs.
- **Fix:** Review the seven generated cases against their actual bytes and independent
  contract. Correct functional validity where justified; regenerate only stale cases.
  A small fixture-specific expectation is sufficient. An arbitrary-input reference
  service is unnecessary; unknown cases remain diagnostic/inconclusive.
- **Check:** Later runs load the minimized cases, reproduce the expected baseline
  problem and check its absence plus independent behavior on the correct patch.
  Functional cases retain eligibility for regression detection.

### F08 - Runtime correlation

**Generic tests verified; a concrete Target 1 correlation gap remains.** [Correlation evidence](../artifacts/checkpoints/correlation-priority/README.md)
covers generic attribution limits and replay consistency. The PDF permits file/function/caller
relations supported by runtime and comparative evidence; it does not require branch tracing,
root-cause proof or a unique hunk.

- **Observed gap:** `diffsheriff/correlator.py::_find_edit_candidate` returns an
  inconclusive verdict when more than one edit candidate matches observed stack frames.
  The retained Target 1 correct/incomplete reports consequently include
  `fix_evidence_insufficient`; the incomplete report also records
  `patch_attribution_unestablished` for its surviving finding.
- **Remaining issue to resolve:** Determine whether the actual comparative evidence
  supports function-level attribution for this multi-hunk patch. If it does, represent
  that supported relation without requiring a unique hunk. If it does not, retain
  `Inconclusive` and document why the selected target cannot claim the expected
  fixed/incomplete result. Add focused tests for whichever evidence-backed behavior is chosen.

### F09 - Deliver the required target results

- **Depends on:** F01-F05/F07 where corrective work is needed.
- **Historical attempt:** The earlier target1/correct report exited 40 with incomplete
  analysis and no container image identity. Preserve it as a failed historical attempt;
  it is not an accepted comparison.
- **Symbolizer issue resolved; target analysis remains incomplete.** The configured
  `/usr/bin/llvm-symbolizer` establishes Target 1's designated baseline identity in sanitized
  mode (`compress_block`, `trees.c:1092`). The current correct report records 120 executions,
  20 functional checks passed, zero functional failures, `functional_status: PASS`, but
  `analysis_complete: false`, `security_status: INCONCLUSIVE`, exit 40, and reasons
  `fix_evidence_insufficient` and `functional_expectation_unmet_on_baseline`. These facts
  must be reported together; the functional summary does not mean the comparison is accepted.
- **Live execution status across comparisons:**
  - `target1/correct`: Current report is `analysis_complete: false`, exit `40`, security
    `INCONCLUSIVE`, functional `PASS`; reasons are `fix_evidence_insufficient` and
    `functional_expectation_unmet_on_baseline`. In its four valid security-trigger cases
    (`malicious/cve_2018_25032.input`, `malicious/cve_2018_25032_bypass.input`,
    `regression/533609f36db8336c36255e0f4a97624621afe93ebba4349c80a3c650f518d139`, and
    `regression/7c2328b634e431ba1384cf482081177cbf34eab62de1952b1c2893808309b404`),
    the sanitized vulnerable baseline aborts
    with UBSan out-of-bounds (`exit -6`) although the independent expected exit is 0; the
    patched side exits 0. This mismatch is the reported baseline expectation gap. Decide
    and document how security-trigger inputs are represented in the functional contract
    without relabeling valid inputs or adopting outcomes from the patch. The separate
    multi-hunk correlation gap also remains.
  - `target1/incomplete`: Process exit `10` matches the configured code, and the report
    records security `FAIL` with one lingering flaw; however `analysis_complete: false`,
    functional `INCONCLUSIVE`, and reasons are `fix_evidence_insufficient`,
    `functional_expectation_unmet_on_baseline`, and `patch_attribution_unestablished`.
    Its `malicious/cve_2018_25032_bypass.input` reproduces the OOB on the incomplete patch.
    This is not yet a complete accepted comparison.
  - `target1/regression`: A run directory and console log exist, but no finalized report
    or matrix row. The attempt was interrupted during minimization; the default
    256-call budget is still in effect; no target config overrides it (see F06).
  - `target2`: None of its correct/incomplete/regression variants has a report, log, or
    matrix row. Run all three only after resolving shared target/config issues.
- **Test suite isolation fixed:** `tests/test_triage.py` uses self-contained sanitizer
  fixtures and a fixed signature expectation; it does not depend on Strix packet files.
- **Remaining work:** Resolve the Target 1 baseline/expectation interaction and F08
  attribution gap with evidence-backed behavior; choose a practical minimization budget;
  then run all six comparisons and retain a report, console log, and reproducible bundles
  for each. Review `analysis_complete`, both independent statuses, exact correlation,
  termination, original/minimized inputs, hashes and at least three replays. Run the
  correct configs again to demonstrate target-specific regression enrollment/replay.
  The current matrix TSV has only two rows; both are labeled `inconclusive_report`.
  Its verifier checks exit/evidence structure, not report completeness or attribution.

### F10 - Make the existing CI path runnable

**Source preparation implemented and verified.** The workflow checks both bundle
paths and destinations before it clones either. Fresh-runner tests resolve the configured
commits; synthetic bundles verify that a missing second bundle or occupied or symlinked
second destination leaves the first destination untouched. The [clean checkout checkpoint](../artifacts/checkpoints/clean-checkout/README.md)
records local shell gating with both synthetic exit codes and actual CLI results
from the harmless fixture. End-to-end selected-target CI acceptance remains open.

The preflight now also rejects a file that `git bundle list-heads` cannot read, so an
unusable second bundle stops the step before the first checkout is created, and the
job verifies `/usr/bin/llvm-symbolizer` inside the built runtime image before
validation. [ci.md](ci.md) records the exact clean-checkout commands.

Bundle-backed source preflight and actual exit gating are implemented; no additional
workflow infrastructure is identified as necessary.

- **Remaining check:** In a fresh environment, run the existing workflow with each
  correct target and verify its actual CLI/JSON gate. Also confirm incomplete and
  regression outcomes fail the gate with their actual nonzero status. No hosted run is
  mandatory if the same workflow behavior is verified locally.

### F11 - Exit codes and generic verification

**Verified for the recorded source.** The [correlation/priority checkpoint](../artifacts/checkpoints/correlation-priority/README.md)
and [runtime retry](../artifacts/checkpoints/correlation-priority/retry/README.md)
cover the exact hierarchy, independent JSON statuses, tests, native smoke and packaging.
Use focused checks after changes and the existing final verification command when
needed; do not keep rerunning unchanged accepted tests or add new process machinery.

### F12 - Check standalone execution with the delivered assets

[CI setup instructions](ci.md) describe preflight and recovery from an interrupted
clone. The [clean checkout checkpoint](../artifacts/checkpoints/clean-checkout/README.md)
verifies fresh generic setup, the harmless native test, the delivered source refs,
and a standalone wheel install. Target-specific delivery checks below remain open.

`scripts/run_matrix.sh` and `scripts/verify_matrix_run.py` add a delivered,
path-independent way to execute and check the six comparisons and their reproducer
bundles, and [ci.md](ci.md)/[evaluation.md](evaluation.md) document the symbolizer
requirement and the clean-checkout commands. Running them still requires the committed
source bundles, the cloned repositories and Docker.

- **Status:** The listed source/assets and clean-checkout instructions are present; no
  missing delivery file is currently identified. The remaining work is the
  target-specific clean-checkout validation below, combined with F09/F10 where practical.
  No archive format, size limit or repeated duplicate matrix is required.
- **Remaining check:** From a clean checkout using only delivered files and declared
  prerequisites, build and run each correct target, load its generated regressions,
  and replay representative findings. This can be combined with the six-row matrix and
  F10 workflow check; the current generic clean-checkout checkpoint does not establish
  target-specific delivery acceptance.

### F13 - Defense preparation

**Optional rehearsal; no additional mandatory package.** The existing
[study guide](defense_guide.md) is sufficient as a guide. Each member needs real
understanding and participation and must complete the required unaided defense.
A local unseen-patch practice exercise may help, but hidden-label bundles, answer keys,
worksheets and practice records are not repository completion conditions.

### External requirements

- **E02:** Genuine contribution, individual unaided defense and defense-day unseen
  patches remain required human/external events (pp. 4-6). Agent-written ownership
  assignments or rehearsal material cannot establish that they occurred.

The existing [agent handoff](agent_handoff_prompt.md) is a historical snapshot and is
not current task guidance; this roadmap is authoritative. No new handoff prompt is part
of the remaining work. Keep the target record, execution guide and [artifact index](../artifacts/README.md)
consistent with this status. Historical evidence stays historical; do not add snapshots
or logs merely to document agent activity.
