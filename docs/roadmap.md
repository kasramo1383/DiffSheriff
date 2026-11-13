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
vulnerability or course-target acceptance. The workflow gaps below remain open.
See the [target record](target_scenarios.md) for proposals and approval status.

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

## Remaining workflow and pipeline implementation

The CLI already builds exact baseline and patch revisions, runs corresponding
release and sanitized binaries in isolated containers, and produces JSON, replay
bundles, and prioritized exit codes. Four parts of the assignment still need code.

1. **Run patch validation in CI (§§3.5, 5).** The current
   [workflow](../.github/workflows/verify_patch.yml) runs unit tests and the harmless
   container fixture. Add a job that runs the existing CLI with a target config and
   exact baseline and patch refs. Retain the report and run bundle on every outcome.
   Use the actual CLI exit code to decide whether a patch passes. A separate scenario
   demonstration can compare the observed code with its expected code (0, 10, or 20).
2. **Carry minimized regressions into later runs (§3.3).** The pipeline generates and
   reloads regression manifests, but when a reduced input has no independent expected
   output it saves the original input to the suite and keeps the reduction in the
   replay bundle only. Enroll the reduced input with a diagnostic check and use an
   independent expectation for its patched behavior before crediting the full
   regression check. Keep the original case with its own expectation. The CI job
   must load the retained regression suite on subsequent runs.
3. **Classify a known baseline finding across inputs (§3.1).** `compare_case()` calls
   a patch diagnostic an incomplete fix only when the same input produces the same
   signature on the baseline. Use the designated baseline identity once it has been
   reproduced in the same build mode, even if a different input exposed it. Keep
   genuinely distinct diagnostics separate and report uncertain identity or
   attribution as such.
4. **Include raw hardening indicators in the report (§3.4).** The release audit
   currently stores NX, PIE, RELRO, and canary statuses and warns on downgrades.
   Retain the indicators behind those results in JSON, including GNU stack flags,
   the PIE marker, the GNU RELRO segment and binding flags, and any canary symbol
   found. Distinguish PIE executables from shared objects rather than treating every
   `ET_DYN` file as PIE.

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

- The audited implementation gaps are fixed and have focused tests plus retained
  verification records.
- Start with the CI entry point for the existing CLI. The other workflow changes
  above can also proceed independently of target approval.
- See `target_scenarios.md` for the approval checkpoint.

## Engineering constraints

- Keep the package flat. Avoid frameworks, databases, services, and unnecessary layers.
- Never select a verdict using target names, file names, branch names, commits, or patch
  hashes.
- Keep target execution local, isolated, resource-limited, and offline.
- A confirmed patch finding and evidence that the patch caused it are separate judgments.
- Preserve complete run bundles and document external image and tool dependencies.
- Do not claim target approval, acceptance, or human defense from synthetic fixtures.
