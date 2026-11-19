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

## Resolved and recorded in the current history

The implementation and evidence gaps that were safe to close without a target-acceptance
campaign are now recorded as completed:

- Sanitizer symbolization, stack triage, and the related runner configuration are in
  place and covered by focused tests (`8c18782`).
- The reproducible six-row matrix runner and evidence verifier are delivered
  (`86890a9`), and the completed target matrix is retained under the
  [target-matrix checkpoint](../artifacts/checkpoints/target-matrix/README.md).
- Bundle-backed source preparation, clean-checkout dependency handling, and the
  retained generic delivery evidence are documented (`4e7db03` and later history).
- The bounded zlib and PNG contracts, corpus review, native build/hardening checks,
  generated-regression enrollment/replay behavior, and exit-priority checks are
  implemented and covered by their F01-F07 and F11 checkpoints.
- Same-function multi-hunk correlation and confirmed-baseline security handling are
  implemented with focused correlator and pipeline regression tests; cross-function
  ambiguity remains conservative.

These resolutions establish reusable implementation and preparation behavior. The
six target scenarios and local delivery gate are recorded, but three variant reports
still contain incomplete analyses (details under F09). A hosted CI run would provide
additional provider-specific evidence; the PDF does not require GitHub-hosted execution.

## Requirement-to-implementation check

| PDF requirement | Current assessment and necessary remainder |
| --- | --- |
| Configurable C/C++ Linux x86_64 targets and actual dynamic execution (p. 1) | Generic source/build/runner/ELF pipeline and both real library bundles are delivered. The six retained target runs execute the declared release and sanitized builds. |
| Independent behavior for valid/invalid inputs, instructor design approval (pp. 1-2, 4) | The selected bounded contracts and fixture basis are documented in `target_scenarios.md`; instructor approval was waived by the course team. The matrix records confirmed baseline identities and keeps ordinary expectation gaps separate from security outcomes. |
| Correlation and Fixed/Incomplete/New/Regression/Inconclusive (p. 2) | Generic implementation and tests support direct, single-hunk, same-function multi-hunk, and conservative cross-function correlation; the target reports retain those relations and replay results. |
| Valid/boundary/invalid suites, corresponding release/sanitized builds, error/mechanism/termination/output/limits (p. 2) | Both target matrices execute their documented suites in both modes. Valid zlib streams remain valid even when the vulnerable baseline crashes; PNG completion/rejection expectations are retained independently. |
| Reproducers, automatic reduction, three replays and enrolled later-run regressions (p. 3) | All six rows retain reproducible bundles, minimized inputs and three baseline replays where a finding is retained. Generated regression manifests are present; unknown minimized expectations remain explicitly inconclusive. |
| Release hardening inspection and downgrade warnings (p. 3) | F04 records native release observations for both targets and generic downgrade tests. The six target reports retain their release hardening observations; no uniform all-protections-enabled requirement is imposed. |
| CLI, JSON, independent statuses and priority `30 > 10 > 20 > 40 > 0` (p. 3) | F11 verifies all 16 combinations through CLI and JSON. The completed matrix and local CI-equivalent target gate preserve the actual exit codes; hosted workflows still own their normal image rebuild. |
| Two independent programs, at least one real, four versions each (p. 4) | Two real libraries and all eight local snapshot refs exist. Both correct/incomplete/regression triples are retained with the justified 0/10/20 outcomes; deliberate driver regression behavior is documented and independently observed. |
| Standalone delivery (pp. 4-5) | Source bundles, configs, reports, reproducers and replay instructions are retained under delivered paths; clean-checkout and local CI-equivalent checks are recorded below. |
| Participation, unaided individual defense and unseen patches (pp. 4-6) | Existing ownership/study material is preparation. Actual participation and defenses remain external requirements, not agent implementation tasks. |

Generic verification and the completed selected-target evidence are retained under
[artifacts](../artifacts/README.md), including the rebuilt-runtime retry and the
target-matrix checkpoint.

## Remaining fixes and acceptance checks

The course team waived instructor approval and all six target scenarios have been run.
The matrix exit-code gate passed, but three reports retain incomplete analysis reasons;
see F09. No generic implementation defect was established in this review. The remaining evidence work is to resolve or explicitly accept those case-specific
gaps. Hosted CI rebuild and artifact upload are optional provider-specific checks, not
course requirements. The local target2 matrix used a derived image as described in the
target-matrix checkpoint.

## Completion gate

The six real-target comparisons, retained evidence review, clean-checkout delivery
check and local CI-equivalent target gate are complete at the process/report level.
Three reports remain analytically incomplete. Hosted GitHub execution is optional
provider-specific evidence and is not represented as a completed local run.

### F01 - Justify the bounded zlib functional contract

**Implemented and verified for the documented completion/status scope.** The
[zlib/CI checkpoint](../artifacts/checkpoints/zlib-contract-ci/README.md) retains
independent API expectations, corrected validity and native baseline/correct/regression
checks in both modes. The contract does not claim validation of discarded output bytes.
The six-row real-target security matrix is retained under the [target-matrix checkpoint](../artifacts/checkpoints/target-matrix/README.md).

- **Status:** The bounded completion/status contract and independent expectations are
  documented and exercised by the retained six-row matrix. The contract does not claim
  validation of discarded compressed bytes; no general-purpose compression oracle is
  required.

### F02 - Justify PNG behavior and handle failures in that scope

**Implemented and verified for the selected native-format contract.** The
[PNG checkpoint](../artifacts/checkpoints/png-contract/README.md) records begin/finish/
allocation handling, reviewed fixtures and native results across all four variants.
The six-row target matrix records the baseline/incomplete security paths. Findings
from newly reduced bytes without an independent functional expectation remain explicitly
inconclusive; see the target-matrix checkpoint.

- **Status:** The selected PNG completion/rejection contract and checked driver behavior
  are represented in the retained target matrix. Unknown minimized-input expectations
  remain inconclusive; no general decoder or broader format coverage is identified as
  necessary.

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
  inputs. Corpus validity review and the target-run expectation review are complete;
  the matrix records the security result separately from ordinary functional expectations.
  The review evidence is retained
  under the [F03 corpus-review checkpoint](../artifacts/checkpoints/f03-corpus-review/README.md).
- **Remaining status:** F03 found no corpus correction or additional case necessary.
  Preserve the independently justified validity labels. The target matrix records
  valid security triggers separately from their vulnerable-baseline termination.
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
  [build/hardening checkpoint](../artifacts/checkpoints/build-hardening/README.md) and
  the [target-matrix checkpoint](../artifacts/checkpoints/target-matrix/README.md).
  Downgrade reporting was verified on real ELFs: baseline->correct reports no
  degradation; a deliberately weakened build (`-no-pie -z norelro -z execstack
  -fno-stack-protector`) reports NX, PIE and RELRO downgrades. `tests/test_hardening.py`
  passes (7).
- **Status:** The delivered builds and six target reports record compiler, commands,
  build identities and release hardening observations. Generic downgrade behavior is
  covered by the existing tests; no package-locking or forced protection baseline is
  required by the assignment.

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

**Implemented and target-verified.** [Reduction evidence](../artifacts/checkpoints/reduction-limits/README.md)
covers error/location preservation, budgets and replay handling. No further minimizer
feature work is required; the target matrix retains real-target original/reduced inputs
and replay results.

- **Operational budget configured:** all six target configs now set
  `max_oracle_calls: 32` with `max_granularity: 16`. This finite budget avoids the
  impractical 256-call default for containerized oracle calls while preserving the
  minimizer's explicit stop reason. The completed matrix confirms each retained reduced
  reproducer's diagnostic and replay contract; cases without an independent expectation
  remain explicitly inconclusive.

### F07 - Repair generated regression checks

**zlib validity repaired; legacy PNG cases retired; selected-target later-run acceptance recorded.** Four zlib
manifests retain their original bytes/refs and now mark their valid compression inputs
correctly. Both functional cases are verified as eligible when the pipeline loads them.
PNG no longer enrolls the three obsolete-baseline cases or invents expectations for
unknown bytes; the target-matrix checkpoint records the new-baseline generated regression
demonstration.
Export refresh now retires stale files for the configured baseline. Local transfer
and CLI tests cover empty exports, shared payloads, and preservation on validation
errors. The [harmless CLI round trip](../artifacts/checkpoints/clean-checkout/README.md#actual-cli-in-the-local-ci-shell)
also generated, exported, imported, and reran two functional cases. Selected-target
later-run acceptance is retained in the clean-checkout CI reports.

The enrollment and replay contract is now covered by focused tests: a stable
minimized baseline failure is retained with its bytes, hash and baseline ref; a later
run for the same baseline loads it in its recorded mode and confirms the designated
diagnostic is absent from the correct patch; export refresh retires stale manifests
for that baseline while preserving other baselines; mixed valid and invalid external
manifests, and unverified cache-only expectations, are rejected before any write; and
`python -m diffsheriff.reproduce` returns 0 for a security reproducer with
`--check-regression` and for a functional reproducer, each after three replays per
side. These are generic fixtures; the selected-target later-run acceptance is retained in
the target-matrix checkpoint.

- **Depends on:** F03 and any changed baseline refs.
- **Status:** Generated regressions are checked in and the target-matrix/clean-checkout
  evidence records later-run loading and replay. Cases without an independent expectation
  remain diagnostic/inconclusive; do not infer behavior from patched output.

### F08 - Runtime correlation

**Generic tests verified; same-function and top-frame stack correlation are now supported.** [Correlation evidence](../artifacts/checkpoints/correlation-priority/README.md)
covers generic attribution limits and replay consistency. The PDF permits file/function/caller
relations supported by runtime and comparative evidence; it does not require branch tracing,
root-cause proof or a unique hunk.

- **Resolved in code:** Multiple edited hunks are correlated as `Edits in observed
  function` when all candidates share one runtime file/function. When edited caller
  functions also appear, an edited top runtime frame is correlated as `Edited function
  on observed stack`. Different-function candidates without an edited top frame remain
  inconclusive, and every replay must retain the same relation.
- **Target check complete:** The six retained reports were generated after this
  behavior was implemented; each row passed the evidence verifier and retains its
  observed correlation/replay metadata.

### F09 - Deliver the required target results

- **Depends on:** F01-F05/F07 where corrective work is needed.
- **Historical attempt:** The earlier target1/correct report exited 40 with incomplete
  analysis and no container image identity. Preserve it as a failed historical attempt;
  it is not an accepted comparison.
- **Historical attempt:** Earlier target1/correct reports exited 40 with incomplete
  analysis. They remain in their run directories as historical attempts and are not the
  current comparison.
- **Six-row matrix:** Every expected process/report exit code matches and all six rows
  passed `scripts/verify_matrix_run.py`. The current correct reports for both targets are
  complete `PASS` (target1: 144 executions; target2: 48). The other reports are:

  | Variant | Exit / verdict | Analysis | Remaining diagnostic |
  | --- | --- | --- | --- |
  | target1 / incomplete | 10 / `VULN_REMAINS_OR_NEW_ISSUE` | Incomplete | `fix_evidence_insufficient`; `patch_attribution_unestablished` |
  | target1 / regression | 20 / `FUNC_REGRESSION` | Complete | None |
  | target2 / incomplete | 10 / `VULN_REMAINS_OR_NEW_ISSUE` | Incomplete | `functional_expectation_missing` |
  | target2 / regression | 20 / `FUNC_REGRESSION` | Incomplete | `fix_evidence_insufficient`; `functional_expectation_unmet_on_patch`; `functional_expectation_missing` |

  See the [matrix TSV](../artifacts/evaluation/matrix.tsv) and [target-matrix
  checkpoint](../artifacts/checkpoints/target-matrix/README.md) for retained paths,
  counts, and environment caveats. A verified matrix row means the process/report exit
  and required evidence structure agree; it does not mean every finding is conclusive.
- **Test suite isolation fixed:** `tests/test_triage.py` uses self-contained sanitizer
  fixtures and a fixed signature expectation; it does not depend on Strix packet files.
- **Remaining work:** No generic implementation defect is established by the retained
  review. The three incomplete analyses above are evidence gaps; resolve them with
  case-specific evidence, not by weakening the analyzer or verifier. Actionable next
  steps are:

  1. Review Target 1 incomplete's two `Incomplete Fix` and eight `Inconclusive` bundles.
     Confirm whether patch correlation can be established from recorded frames and edits;
     if it cannot, preserve the inconclusive result and limit the claim to the two
     confirmed lingering findings.
  2. Establish an independent expectation for Target 2 incomplete's
     `minimized/0727fdc603dd5477790e` from the selected PNG contract or independent source
     documentation. Keep it unjudged if no defensible expectation follows.
  3. Review Target 2 regression's
     `regression/aa623b9c6c003303387bbd289e02da44fa7ee81b3be80d11a312c7bd9b16874f`
     expectation and two inconclusive findings; establish expected behavior and
     security/fix evidence where independently supported, then rerun the affected row.
  4. Optionally run the hosted workflow to verify a fresh Docker rebuild and artifact
     upload. This is operational CI evidence, not a separate course requirement.

  The local target2 matrix used a derived image because the cached image lacked the
  Dockerfile-declared zlib headers.

### F10 - Make the existing CI path runnable

**Source preparation implemented and verified.** The workflow checks both bundle
paths and destinations before it clones either. Fresh-runner tests resolve the configured
commits; synthetic bundles verify that a missing second bundle or occupied or symlinked
second destination leaves the first destination untouched. The [clean checkout checkpoint](../artifacts/checkpoints/clean-checkout/README.md)
records local shell gating with both synthetic exit codes and actual CLI results
from the harmless fixture. The local CI-equivalent target gate now also runs both
correct target configs from the delivered bundles; hosted rebuild/upload remains external.

The preflight now also rejects a file that `git bundle list-heads` cannot read, so an
unusable second bundle stops the step before the first checkout is created, and the
job verifies `/usr/bin/llvm-symbolizer` inside the built runtime image before
validation. [ci.md](ci.md) records the exact clean-checkout commands.

Bundle-backed source preflight and actual exit gating are implemented; no additional
workflow infrastructure is identified as necessary.

- **Remaining check:** None locally. Hosted CI may repeat the same workflow with a fresh
  Docker base and its normal cache/artifact services.

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
and a standalone wheel install. Target-specific delivery checks are recorded by the
target-matrix checkpoint.

`scripts/run_matrix.sh` and `scripts/verify_matrix_run.py` add a delivered,
path-independent way to execute and check the six comparisons and their reproducer
bundles, and [ci.md](ci.md)/[evaluation.md](evaluation.md) document the symbolizer
requirement and the clean-checkout commands. Running them still requires the committed
source bundles, the cloned repositories and Docker.

- **Status:** Complete for the local clean-room checkout. The source bundles, configs,
  target repositories, runtime image preflight and correct-target CLI gate were exercised
  from delivered paths; the exact caveat is in the target-matrix checkpoint.

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
