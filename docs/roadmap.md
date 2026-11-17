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
| Regression must be an organic library bug | Prepare a version fixing the flaw while breaking independently valid behavior (p. 4). A deliberately constructed driver regression can qualify if the driver is part of the declared target and the behavior/approval support it. It must be described honestly, not replaced solely for realism. |
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
| Independent behavior for valid/invalid inputs, instructor design approval (pp. 1-2, 4) | Static expected manifests exist, but their independent basis and selected driver contracts are not sufficiently documented. Both targets now have documented bounded contracts. PNG uses only reviewed fixture expectations and rejects unknown reference inputs. Review the selected cases, not every possible library input. Instructor approval evidence is unavailable. |
| Correlation and Fixed/Incomplete/New/Regression/Inconclusive (p. 2) | Generic implementation and tests exist. F08 added conservative handling of multiple function-edit candidates. Real-target reports must explain the supported relation and uncertainty; function-level evidence does not require proof of causation. |
| Valid/boundary/invalid suites, corresponding release/sanitized builds, error/mechanism/termination/output/limits (p. 2) | Implemented generically. Target suites exist; verify their chosen cases and labels. zlib memory-error triggers are not semantically invalid merely because they crash. An empty PNG can be an invalid boundary case; add cases only where the agreed boundary/functional behavior is otherwise untested. |
| Reproducers, automatic reduction, three replays and enrolled later-run regressions (p. 3) | Implemented generically; F06 records reduction limits/outcomes. Selected-target full run bundles are absent. The two zlib functional manifests now have independently justified true validity; the old PNG cases were retired as legacy evidence after the driver/source refs changed. New-baseline later-run acceptance remains pending. Keep unknown expectations inconclusive instead of inventing them. |
| Release hardening inspection and downgrade warnings (p. 3) | Implemented, with generic downgrade tests. Verify actual release observations on both targets. Absolute all-protections minima were a project policy, not a PDF requirement, and are relaxed in the selected configs. |
| CLI, JSON, independent statuses and priority `30 > 10 > 20 > 40 > 0` (p. 3) | F11 verifies all 16 combinations through CLI and JSON. CI now prepares the bundle-backed source directories and refuses existing destinations; full selected-target CI results remain pending. |
| Two independent programs, at least one real, four versions each (p. 4) | Two real libraries and all eight local snapshot refs exist. libpng uses system zlib rather than Target 1's tree. Inspect scenario behavior in the required six comparisons; deliberate driver regressions are acceptable within the declared/approved contract. |
| Standalone delivery (pp. 4-5) | Source/assets/instructions exist; demonstrate target validation and replay from delivered files. Combine that check with the matrix work where possible rather than adding another full duplicate campaign. |
| Participation, unaided individual defense and unseen patches (pp. 4-6) | Existing ownership/study material is preparation. Actual approval, participation and defenses remain external facts, not agent implementation tasks. |

Generic verification is retained under [artifacts](../artifacts/README.md), including
the rebuilt-runtime retry. Earlier claims of completed selected-target matrices lack
full delivered reports/reproducer runs; they remain unverified rather than disproved.

## Remaining fixes and acceptance checks

F06, F08 and F11 have generic implementation/verification evidence. Keep their IDs for
continuity; their already completed optional safeguards are not further work. The first
action is the remaining F03/F07/F09 target evaluation and regression work. Complete each remaining item with the smallest
change that satisfies the stated course requirement. Keep results with their run and
update status here without introducing another checklist or approval workflow.

### F01 - Justify the bounded zlib functional contract

**Implemented and verified for the documented completion/status scope.** The
[zlib/CI checkpoint](../artifacts/checkpoints/zlib-contract-ci/README.md) retains
independent API expectations, corrected validity and native baseline/correct/regression
checks in both modes. The contract does not claim validation of discarded output bytes.
Instructor approval and the full security matrix remain separate requirements.

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
- **Fix:** Correct validity and unsupported expectations for existing files. Ensure
  representative valid, boundary and invalid cases are documented. Add the smallest
  missing case only if a required category or chosen boundary behavior lacks coverage.
- **Check:** The same cases/settings run on corresponding versions/builds. Expected
  results and validity come from independent evidence; no fixed corpus count or
  exhaustive library coverage is required.

### F04 - Confirm builds and measure hardening

- **Fix:** Establish which compiler, flags, dependencies and runtime are actually used
  and document sufficient setup to build/replay. Make compiler selection explicit only
  if required for consistent builds. Absolute minima in the six configs are neutral;
  retain ELF inspection and unintended downgrade warnings. Do not add package locking
  or force missing baseline protections on unless a demonstrated problem requires it.
- **Check:** Required source versions build to x86_64 ELF in corresponding ordinary and
  instrumented modes; retain actual NX/PIE/RELRO/canary observations and build identities.
  Reuse existing downgrade tests rather than adding an extra target variant for each flag.

### F05 - Update packaged sources only when needed

**PNG driver update packaged and verified.** All four current refs/configs and the
source bundle agree. Legacy refs preserve the prior versions; source-mapping evidence
records the exact transition. No library fix or license was changed.

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

### F07 - Repair generated regression checks

**zlib validity repaired; legacy PNG cases retired; full later-run acceptance open.** Four zlib
manifests retain their original bytes/refs and now mark their valid compression inputs
correctly. Both functional cases are verified as eligible when the pipeline loads them.
PNG no longer enrolls the three obsolete-baseline cases or invents expectations for
unknown bytes; new-baseline generated regressions still need F09 demonstration.

- **Depends on:** F03 and any changed baseline refs.
- **Fix:** Review the seven generated cases against their actual bytes and independent
  contract. Correct functional validity where justified; regenerate only stale cases.
  A small fixture-specific expectation is sufficient. An arbitrary-input reference
  service is unnecessary; unknown cases remain diagnostic/inconclusive.
- **Check:** Later runs load the minimized cases, reproduce the expected baseline
  problem and check its absence plus independent behavior on the correct patch.
  Functional cases retain eligibility for regression detection.

### F08 - Runtime correlation

**Generic implementation verified.** [Correlation evidence](../artifacts/checkpoints/correlation-priority/README.md)
covers attribution limits and replay consistency. The PDF permits file/function/caller
relations supported by runtime and comparative evidence. Do not add branch tracing,
root-cause proof or a universal single-hunk requirement. If the current conservative
rule blocks a legitimate selected-target relation, review the actual evidence and
report its supported level instead of expanding the assignment.

### F09 - Deliver the required target results

- **Depends on:** F01-F05/F07 where corrective work is needed.
- **Fix:** Execute the six baseline/patch comparisons in [evaluation.md](evaluation.md).
  Retain each report and its source/build/input/reproducer evidence. Keep meaningful
  failed attempts without producing redundant checkpoint campaigns.
- **Check:** Correct/incomplete/regression variants produce the justified 0/10/20
  outcomes; modes/settings remain equivalent; findings retain correlation, actual
  termination, original/reduced inputs and at least three replays. Demonstrate later
  regression loading, preferably in the necessary correct-patch validation. Never
  force expected codes or combine unrelated run identities.

### F10 - Make the existing CI path runnable

**Source preparation implemented and verified.** The workflow clones both bundles
before validation; fresh-runner tests resolve all configured commits and exercise
missing-bundle and existing-checkout refusal. End-to-end selected-target CI acceptance
remains pending the target contracts/matrices; this is not a hosted acceptance claim.

- **Fix:** Prepare bundle-backed source repositories before the existing workflow
  invokes the CLI. Retain its actual exit gating and JSON. Do not add another service,
  CI provider, elaborate cache strategy or approval process.
- **Check:** A fresh CI environment can run a correct target comparison and gate on
  actual results. An incomplete/regression verdict fails the gate. Hosted execution
  is one way to show this, not a mandatory provider-specific acceptance event.

### F11 - Exit codes and generic verification

**Verified for the recorded source.** The [correlation/priority checkpoint](../artifacts/checkpoints/correlation-priority/README.md)
and [runtime retry](../artifacts/checkpoints/correlation-priority/retry/README.md)
cover the exact hierarchy, independent JSON statuses, tests, native smoke and packaging.
Use focused checks after changes and the existing final verification command when
needed; do not keep rerunning unchanged accepted tests or add new process machinery.

### F12 - Check standalone execution with the delivered assets

- **Fix:** Finish only missing setup/usage details and supply the PDF-listed files.
  Use a fresh location without ignored developer state; combine this with F09/F10
  where practical. No mandatory archive format, size limit or repeated all-matrix run.
- **Check:** Install/build, validate a correct patch per target, load generated cases
  and replay representative findings using delivered files and declared prerequisites.
  Results must not depend on hidden machine paths or chat history.

### F13 - Defense preparation

**Optional rehearsal; no additional mandatory package.** The existing
[study guide](defense_guide.md) is sufficient as a guide. Each member needs real
understanding and participation and must complete the required unaided defense.
A local unseen-patch practice exercise may help, but hidden-label bundles, answer keys,
worksheets and practice records are not repository completion conditions.

### External requirements

- **E01:** Instructor design approval of target provenance, patches, reference tests and
  expected behavior is explicitly required (pp. 1-2, 4). Prepare the existing material
  for review and record the real response when available. Do not fabricate approval;
  continue independent technical work while it is pending.
- **E02:** Genuine contribution, individual unaided defense and defense-day unseen
  patches remain required human/external events (pp. 4-6). Agent-written ownership
  assignments or rehearsal material cannot establish that they occurred.

Keep the single [agent handoff](agent_handoff_prompt.md), the existing target record,
execution guide and [artifact index](../artifacts/README.md). Historical evidence stays
historical. Do not add instructions, snapshots or logs merely to document agent activity.
