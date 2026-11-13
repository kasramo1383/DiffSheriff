# Live implementation roadmap

This is the single current record of implementation state, known gaps, and next work.
The instructor's PDF (`course_assignment.pdf`) is authoritative, with its English digest
in `specification.md`. Target facts and approval evidence belong in
`target_scenarios.md`. Contributor ownership remains in the README. The copyable agent
handoff instructions are in [`agent_handoff_prompt.md`](agent_handoff_prompt.md).

## Current assessment

The three implementation defects identified in the audit are fixed in the current
source. Their focused tests, full-suite records, and package builds are retained under
`artifacts/checkpoints/`. The final checkpoint records 134 passing Linux tests with no
skips, including a harmless native Docker fixture. The Windows run records 133 passes
and the Docker test skipped. Formatting, lint, packaging, source hashes, and runtime
details are also documented in the [final checkpoint](../artifacts/checkpoints/insertion/README.md).

The native fixture is infrastructure evidence only. It does not demonstrate a real
vulnerability or course-target acceptance. The project remains incomplete because no
course targets, instructor approval, independent target oracle, or target acceptance
reports have been supplied.

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
3. Insertion-only patches can be related to a baseline finding when a single
   unambiguous inserted function declaration matches the runtime stack across three
   baseline observations. This is function-level relation evidence, not proof that
   the inserted branch executed. Ambiguous evidence remains inconclusive. See the
   [insertion checkpoint](../artifacts/checkpoints/insertion/README.md).
4. Synthetic CLI coverage exercises verdicts, replay, and generated regression loading.
   The native smoke fixture checks Docker execution and input handling. These checks
   establish implementation behavior within the tested cases, not correctness for all
   targets.

## Remaining project work

### 1. Select and obtain approval for two targets

The team must provide source provenance, licenses, exact references, and instructor
approval evidence for two C/C++ targets. At least one must be a real non-toy project or
library. Record these facts in `target_scenarios.md`. No target or approval is currently
recorded.

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

- The audited implementation gaps are fixed and have focused tests plus retained
  verification records.
- The project is not ready for course acceptance. Target selection, approval, scenario
  assets, end-to-end runs, unseen-patch evaluation, and contributor defense remain.
- First next action: record candidate targets and obtain instructor approval in
  `target_scenarios.md`.

## Engineering constraints

- Keep the package flat. Avoid frameworks, databases, services, and unnecessary layers.
- Never select a verdict using target names, file names, branch names, commits, or patch
  hashes.
- Keep target execution local, isolated, resource-limited, and offline.
- A confirmed patch finding and evidence that the patch caused it are separate judgments.
- Preserve complete run bundles and document external image and tool dependencies.
- Do not claim target approval, acceptance, or human defense from synthetic fixtures.
