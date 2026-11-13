# Live implementation roadmap

This is the single current record of implementation state, known gaps, and next work.
The instructor's PDF (`course_assignment.pdf`) is authoritative, with its English digest
in `specification.md`. Target facts and approval evidence belong in
`target_scenarios.md`. Contributor ownership remains in the README. The copyable agent
handoff instructions are in [`agent_handoff_prompt.md`](agent_handoff_prompt.md).

## Current assessment

The three earlier audited defects and four workflow/pipeline gaps have implementations
with focused checks. Of the two subsequent audit findings below, Stage 1 now has an
implementation and verification evidence ready for review in the
[minimized-results checkpoint](../artifacts/checkpoints/minimized-results/README.md).
Stage 2 remains open. The earlier
[workflow checkpoint](../artifacts/checkpoints/workflow/README.md) records its own
source and verification scope. Neither checkpoint records team or instructor acceptance.

The native fixture is infrastructure evidence only. It does not demonstrate a real
vulnerability or course-target acceptance. See the [target record](target_scenarios.md)
for proposals and approval status. Hosted GitHub execution with an approved target
still depends on that target's assets and approval.

## Completed implementation checkpoints

1. Security minimization runs unknown candidate inputs against the same diagnostic
   invariant, without requiring a functional expected-output oracle. If a minimized
   case lacks independent expected output, diagnostic replay is available, while
   functional regression checks use the original input. See the
   [minimization checkpoint](../artifacts/checkpoints/minimization/README.md).
2. Functional regression classification follows the independent `valid_input`
   designation. Valid boundary cases contribute to functional results and can produce
   exit 20. Invalid cases do not become regressions unless explicitly marked valid.
   See the [boundary checkpoint](../artifacts/checkpoints/boundary/README.md).
3. Insertion-only patches can be related to a baseline finding when one unambiguous
   function declaration in the hunk context matches the runtime stack across three
   baseline observations. The match establishes a function-level relation.
   Ambiguous evidence remains inconclusive. See the
   [insertion checkpoint](../artifacts/checkpoints/insertion/README.md).
4. Synthetic CLI coverage exercises verdicts, replay, and generated regression loading.
   The native smoke fixture checks Docker execution and input handling. These checks
   establish implementation behavior within the tested cases, not correctness for all
   targets.

## Workflow and pipeline implementation ready for review

1. **CI patch validation (§§3.5, 5).** The reusable/manual
   [target workflow](../.github/workflows/validate_target.yml) runs the CLI using a
   config with exact source refs. The actual process exit code gates the job, and
   report/run artifacts are uploaded on every outcome where they exist. Regression
   caches are restored and updated across runs, with a retained artifact copy.
   Configure the main verification workflow with `DIFFSHERIFF_TARGET_CONFIG` after
   target approval. See [CI usage](ci.md); no hosted target run is claimed.
2. **Minimized regression enrollment (§3.3).** Unknown reduced inputs are enrolled as
   diagnostic regressions and executed in their recorded build mode on later runs.
   The original input retains its independent expectation. Missing reduced-input
   expectations make analysis inconclusive immediately; an independent reference
   or supplied expectation is required to complete the full regression check.
3. **Finding identity across inputs (§3.1).** Suite observations establish the
   designated baseline identity per build mode before classification. A matching
   patch diagnostic on a different input is an incomplete fix even when that input
   is processed first. Unstable baselines and evidence from other build modes do not
   establish that identity. Distinct findings and inconclusive attribution stay
   separate; matching a signature does not prove causation.
4. **Hardening evidence (§3.4).** JSON includes GNU stack flags, ELF type, interpreter
   presence, the PIE marker, RELRO-segment presence, binding flags, and canary symbol
   names. `ET_DYN` alone does not establish PIE; an interpreter or `DF_1_PIE` marker
   is required. Sectionless dynamic flags are read through program headers.

## Remaining implementation: audit findings

Complete these stages in order. Keep each stage focused, add regression tests for the
specific failure cases, run the relevant focused checks and existing suite, inspect the
resulting report/manifests, and stop for Kasra's review before taking the next stage.
Do not combine these changes with target selection, hosted CI acceptance, or unrelated
cleanup.

### Stage 1 — Classify minimized diagnostic results

**Status: implemented and verified, awaiting Kasra's review.** See the
[checkpoint](../artifacts/checkpoints/minimized-results/README.md) for the source
identity, focused/full checks, inspected synthetic reports, native run, and package.
Stable minimized observations now use ordinary comparison and exit-priority logic,
with parent-scoped deduplication and no recursive minimization. Reduced-input
validity comes from an independent corpus or an explicit boolean from the independent
reference; it is not inherited from different original bytes. Stage 2 has not started.

**Original issue.** `record_reproducer()` in `diffsheriff/pipeline.py` replays the minimized
input against both baseline and patch and retains both observations. Its caller only
uses the minimizer's stability and whether an independent expectation is available.
It does not feed those minimized observations back through the normal comparison and
verdict-priority logic. A stable minimized input can therefore expose a finding on the
patch, or an independently expected behavior mismatch, without that newly observed
result affecting the final verdict. The original input's comparison does not cover
this newly reduced input.

**Implementation steps.**

1. Trace how `compare_case()`, finding creation, `vulnerability`/`regression` flags,
   `incomplete`, and `resolve_priority_exit_code()` contribute to the report and final
   verdict in `diffsheriff/pipeline.py` and `diffsheriff/reporter.py`.
2. After a reproducer is stable, classify its already collected baseline/patch
   observations using the same independent expectation, build mode, baseline identity,
   correlation, and exit-priority rules as ordinary cases. Do not launch a second
   minimization pass. Avoid duplicate findings for an observation already represented
   by the original case; retain a distinct minimized-input finding when it adds
   evidence.
3. Ensure results without independent expected behavior remain diagnostic-only and
   make the analysis inconclusive where functional behavior is required. Do not infer
   expected output from patched output.
4. Add focused synthetic tests for (a) a security-minimized input that introduces a
   stable patch-side diagnostic, (b) an independently known minimized input whose patch
   violates expected behavior while baseline satisfies it, and (c) a minimization that
   does not add a result, preserving the existing verdict and avoiding duplicate
   records.
5. Run the focused tests and the full existing test suite; inspect report JSON, finding
   deduplication, exit codes, and reproducer metadata. Record commands and actual results
   in a new checkpoint under `artifacts/checkpoints/` and link it here.

**Acceptance.** A stable minimized case cannot hide a confirmed patch finding or an
independently demonstrated functional regression. The report identifies the minimized
input and mode, respects current verdict priority, retains diagnostic-only uncertainty,
and does not create recursive minimization or duplicate findings. Existing behavior
and tests remain intact.

### Stage 2 — Reconcile trusted regression-cache manifests

**Issue.** `copy_regressions()` in `diffsheriff/regressions.py` compares incoming and
local files byte-for-byte. A CI cache can contain an earlier diagnostic manifest with
`expected: null`; after the team independently approves and checks in an expectation
for the same generated case, importing that stale cache fails with exit 30 before
validation. The present workaround is to review/retire the old cache manually, making
routine CI runs brittle.

**Implementation steps.**

1. Define and document which manifest fields identify the same generated regression:
   at minimum exact baseline reference, input bytes and verified hash, build mode, and
   finding identity. Treat paths as contained files and continue to reject symlinks,
   traversal, corrupt hashes, different payloads, baseline mismatches, and unrelated
   manifest conflicts.
2. When identities and payloads match, prefer an independently approved checked-in
   expectation over an incoming diagnostic `null` expectation. Do not promote an
   expectation from cache into trusted ground truth merely because it is present there.
   Preserve strict conflict errors for differing expectations or any mismatch in the
   identity fields above. If safe reconciliation cannot be established from existing
   metadata, implement an explicit cache-bypass path and document its operator behavior
   instead of guessing.
3. Add tests for stale diagnostic cache versus approved local expectation (must import
   or skip only that stale manifest safely), exact matching files (still idempotent),
   different payload/hash/baseline/mode/finding identity (must reject), conflicting
   non-null expectations (must reject), and path/symlink protections (must remain).
4. Update `docs/ci.md` with the resulting precedence and recovery behavior. Exercise
   the CLI transfer path and CI-relevant import/export tests; run the full existing suite
   and inspect that the approved local expectation remains byte-for-byte unchanged.
   Record exact checks in a checkpoint under `artifacts/checkpoints/` and link it here.

**Acceptance.** A stale cache cannot block validation when a matching checked-in case
has a reviewed expectation; cache data cannot overwrite or establish ground truth;
unrelated or corrupt conflicts still fail safely. Re-running the same transfer is
idempotent.
## Target and delivery work

### 1. Obtain approval for two targets

The team must provide source provenance, licenses, exact references, and instructor
approval evidence for two C/C++ targets. At least one must be a real non-toy project or
library. The proposals are recorded in `target_scenarios.md`. Approval is pending.

### 2. Prepare four scenarios and independent test assets per target

For each target, retain the vulnerable baseline, correct patch, incomplete patch, and
regression patch. Prepare independent valid, boundary, and invalid-input expectations
from approved sources. The incomplete patch needs a distinct, safe input for the
authorized local lab that still reaches the same underlying flaw after the original
trigger is blocked. Do not derive expected behavior from the target's patched output.

### 3. Run and retain target acceptance evidence

Run every scenario in release and sanitized modes. Check the expected exit codes,
functional behavior, finding classification, patch correlation, hardening, minimization,
and at least three replays. Retain complete run bundles and reports under the artifact
policy. Evaluate unseen patches in the approved target domain. The harmless echo
fixture does not satisfy this requirement.

Acceptance requires two reproducible target matrices, including one real non-toy target,
with instructor approval, independent expectations, and required reports and artifacts.

### 4. Complete defense and delivery review

After target acceptance, verify standalone instructions from a clean environment and
inspect the delivered evidence. Each contributor must explain their owned logic and
complete a small live change as required by the assignment. This requires student
participation.

## Current checkpoint

- Stage 1 is implemented and verified, awaiting review of the minimized-results
  checkpoint. After that review, next implementation work is Stage 2. Do not repeat
  Stage 1 or mark it accepted on the team's behalf.
- After those audit findings are fixed, the next external dependency is instructor
  confirmation for candidate targets, source pairs, input scope, and independent
  expected behavior in `target_scenarios.md`.
- Then prepare authorized target scenarios and run their acceptance matrices, including
  hosted CI. Target evidence, unseen-patch evaluation, and contributor defense remain.
- Do not manufacture target approval or mark the project accepted from synthetic or
  harmless native checks.

## Engineering constraints

- Keep the package flat. Avoid frameworks, databases, services, and unnecessary layers.
- Never select a verdict using target names, file names, branch names, commits, or patch
  hashes.
- Keep target execution local, isolated, resource-limited, and offline.
- A confirmed patch finding and evidence that the patch caused it are separate judgments.
- Preserve complete run bundles and document external image and tool dependencies.
- Do not claim target approval, acceptance, or human defense from synthetic fixtures.
