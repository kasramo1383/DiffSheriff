# Live implementation roadmap

This is the single current record of implementation state, known gaps, and next work.
The instructor's PDF (`course_assignment.pdf`) is authoritative, with its English digest
in `specification.md`. Target facts and approval evidence belong in
`target_scenarios.md`. Contributor ownership remains in the README. The copyable agent
handoff instructions are in [`agent_handoff_prompt.md`](agent_handoff_prompt.md).

## Current assessment

The three earlier audited defects and the four subsequently identified workflow
and pipeline gaps have implementations with focused checks. The current source,
verification results, native evidence, and package are recorded in the
[workflow checkpoint](../artifacts/checkpoints/workflow/README.md). This checkpoint
is ready for review; it does not record team or instructor acceptance.

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

- The earlier audited fixes and all four listed workflow/pipeline gaps are implemented.
  Review the current checkpoint's evidence before accepting it.
- Next dependency: instructor confirmation for the candidate targets, source pairs,
  input scope, and independent expected behavior in `target_scenarios.md`.
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
