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
| Independent behavior for valid/invalid inputs, instructor design approval (pp. 1-2, 4) | Static expected manifests exist, but their independent basis and selected driver contracts are not sufficiently documented. Both targets now have documented bounded contracts. PNG uses only reviewed fixture expectations and rejects unknown reference inputs. Review the selected cases, not every possible library input. Instructor approval was waived by the course team. |
| Correlation and Fixed/Incomplete/New/Regression/Inconclusive (p. 2) | Generic implementation and tests exist. F08 added conservative handling of multiple function-edit candidates. Real-target reports must explain the supported relation and uncertainty; function-level evidence does not require proof of causation. |
| Valid/boundary/invalid suites, corresponding release/sanitized builds, error/mechanism/termination/output/limits (p. 2) | Implemented generically. Target suites exist; verify their chosen cases and labels. zlib memory-error triggers are not semantically invalid merely because they crash. An empty PNG can be an invalid boundary case; add cases only where the agreed boundary/functional behavior is otherwise untested. |
| Reproducers, automatic reduction, three replays and enrolled later-run regressions (p. 3) | Implemented generically; F06 records reduction limits/outcomes. Selected-target full run bundles are absent. The two zlib functional manifests now have independently justified true validity; the old PNG cases were retired as legacy evidence after the driver/source refs changed. New-baseline later-run acceptance remains pending. Keep unknown expectations inconclusive instead of inventing them. |
| Release hardening inspection and downgrade warnings (p. 3) | F04 records native release observations for both targets and generic downgrade tests. Retain the tool's release hardening results from the delivery environment during F09. |
| CLI, JSON, independent statuses and priority `30 > 10 > 20 > 40 > 0` (p. 3) | F11 verifies all 16 combinations through CLI and JSON. CI now prepares the bundle-backed source directories and refuses existing destinations; full selected-target CI results remain pending. |
| Two independent programs, at least one real, four versions each (p. 4) | Two real libraries and all eight local snapshot refs exist. libpng uses system zlib rather than Target 1's tree. Inspect scenario behavior in the required six comparisons; deliberate driver regressions are acceptable within the declared/approved contract. |
| Standalone delivery (pp. 4-5) | Source/assets/instructions exist; demonstrate target validation and replay from delivered files. Combine that check with the matrix work where possible rather than adding another full duplicate campaign. |
| Participation, unaided individual defense and unseen patches (pp. 4-6) | Existing ownership/study material is preparation. Actual participation and defenses remain external requirements, not agent implementation tasks. |

Generic verification is retained under [artifacts](../artifacts/README.md), including
the rebuilt-runtime retry. Earlier claims of completed selected-target matrices lack
full delivered reports/reproducer runs; they remain unverified rather than disproved.

## Remaining fixes and acceptance checks

The course team waived instructor approval; E01 is closed and removed from the
remaining work. F09 is the remaining technical acceptance track: finish the real
target comparisons, review every report, and demonstrate later-run regression
acceptance. F12's generic clean-checkout work is recorded; target-specific delivery
evidence comes from completing F09. F06, F08, F10 and F11 retain their generic
verification, with the target-specific F08 gap tracked in F09.

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
  supports the Target 1 labels. The native release probe records exit behavior and
  does not establish memory safety. Target 2 supplies rejected inputs. This scope interpretation is accepted.
  The review evidence is retained
  under the [F03 corpus-review checkpoint](../artifacts/checkpoints/f03-corpus-review/README.md).
- **Fix:** Correct validity and unsupported expectations for existing files. Ensure
  representative valid, boundary and invalid cases are documented. Add the smallest
  missing case only if a required category or chosen boundary behavior lacks coverage.
- **Check:** The same cases/settings run on corresponding versions/builds. Expected
  results and validity come from independent evidence; no fixed corpus count or
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

- **Operational gap (Containerized minimization latency):** Under containerized environments
  (specifically WSL/Docker with bind mounts), delta-debugging with default `max_oracle_calls: 256`
  initiates up to 256 sequential `docker run` and `docker rm` container lifecycles. At ~1.5–2s
  per container, a single failing case minimization takes 8–10 minutes. For real-target matrix
  runs, `max_oracle_calls` must be bounded in target configs (e.g., 16–32) to prevent excessive
  runtime during functional regression checks.

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

**Generic tests verified; target-specific correlation gap observed in F09.** [Correlation evidence](../artifacts/checkpoints/correlation-priority/README.md)
covers attribution limits and replay consistency. The PDF permits file/function/caller
relations supported by runtime and comparative evidence. Do not add branch tracing,
root-cause proof or a universal single-hunk requirement. If the current conservative
rule blocks a legitimate selected-target relation, review the actual evidence and
report its supported level instead of expanding the assignment.

- **Observed bug (Multi-hunk function correlation):** In `diffsheriff/correlator.py`
  (`_find_edit_candidate`), line 165 checks `if len(edit_candidates) > 1: return
  CorrelationVerdict(False, "Inconclusive", ...)`. When a patch contains multiple edit
  hunks within functions observed on the stack (as in zlib's CVE-2018-25032 fix in
  `deflate.c`), this rule marks attribution as `Inconclusive` with `is_correlated: False`.
  Consequently, `pipeline.py` (`compare_case`) evaluates `if patch_ok and correlated:`
  to `False`, raising `fix_evidence_insufficient` and failing closed with exit code
  `40` instead of `0` (`PASS`).
- **Fix:** Update `diffsheriff/correlator.py` so that multiple edit hunks matching observed
  stack functions are accepted as valid function-level correlation (`Edit in observed function`),
  reporting the supported function-level relation rather than failing attribution.

### F09 - Deliver the required target results

- **Depends on:** F01-F05/F07 where corrective work is needed.
- **Historical attempt:** The earlier target1/correct report exited 40 with incomplete
  analysis and no container image identity. Preserve it as a failed historical attempt;
  it is not an accepted comparison.
- **Diagnosis and remedy verified in Docker.** The previous 40 was not a verdict about the patch.
  Setting `external_symbolizer_path=/usr/bin/llvm-symbolizer` in `ASAN_OPTIONS` and `UBSAN_OPTIONS`,
  defaulting it in the runner, and hardening triage frame parsing resolved the symbolizer issue:
  a live Docker run of `target1/correct` successfully established the baseline identity in sanitized
  mode (`baseline_identity_modes: ["sanitized"]`, resolving `compress_block` at `trees.c:1092`) with
  zero reproducer instability and 20/20 functional passes.
- **Live execution status across comparisons:**
  - `target1/correct`: Baseline reproduced and functional tests passed, but returned exit code `40`
    due to the F08 multi-hunk correlation bug (`analysis_incomplete_reasons: ["fix_evidence_insufficient"]`).
    Resolving F08 is the sole blocker for code `0` (`PASS`).
  - `target1/incomplete`: Executed in Docker and passed with expected exit code `10` (`VULN_REMAINS`).
  - `target1/regression`: Interrupted during delta-debugging minimization of functional regression due to
    256 unbound container oracle calls (see F06).
  - `target2` (`correct: 0`, `incomplete: 10`, `regression: 20`): Unexecuted pending the F08 correlator
    fix and F06 minimization bounding.
- **Test suite isolation fixed:** tests/test_triage.py uses self-contained sanitizer
  fixtures and a fixed signature expectation; it does not depend on Strix packet files.
- **Fix:** Apply the F08 correlator multi-hunk fix, bound minimization oracle calls in target evaluation
  configs, and execute the full 6-row matrix via `scripts/run_matrix.sh` to retain verified reports,
  console logs, and reproducer bundles under `artifacts/evaluation/{target1,target2}/{correct,incomplete,regression}`.
- **Check:** Correct/incomplete/regression variants produce the justified 0/10/20
  outcomes; modes/settings remain equivalent; findings retain correlation, actual
  termination, original/reduced inputs and at least three replays. Demonstrate later
  regression loading, preferably in the necessary correct-patch validation. Never
  force expected codes or combine unrelated run identities.

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

[CI setup instructions](ci.md) describe preflight and recovery from an interrupted
clone. The [clean checkout checkpoint](../artifacts/checkpoints/clean-checkout/README.md)
verifies fresh generic setup, the harmless native test, the delivered source refs,
and a standalone wheel install. Target-specific delivery checks below remain open.

`scripts/run_matrix.sh` and `scripts/verify_matrix_run.py` add a delivered,
path-independent way to execute and check the six comparisons and their reproducer
bundles, and [ci.md](ci.md)/[evaluation.md](evaluation.md) document the symbolizer
requirement and the clean-checkout commands. Running them still requires the committed
source bundles, the cloned repositories and Docker.

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

- **E02:** Genuine contribution, individual unaided defense and defense-day unseen
  patches remain required human/external events (pp. 4-6). Agent-written ownership
  assignments or rehearsal material cannot establish that they occurred.

Keep the single [agent handoff](agent_handoff_prompt.md), the existing target record,
execution guide and [artifact index](../artifacts/README.md). Historical evidence stays
historical. Do not add instructions, snapshots or logs merely to document agent activity.
