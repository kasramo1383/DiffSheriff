# Agent handoff prompt

Use this single prompt with any coding agent. The sole live work list and acceptance
state are [roadmap.md](roadmap.md); this prompt contains no parallel progress checklist.

```text
Continue the DiffSheriff course project through the actionable fixes in docs/roadmap.md.

Read AGENTS.md, the original docs/course_assignment.pdf, and docs/roadmap.md first.
Inspect staged, unstaged, untracked and ignored state. Existing cleanup/documentation
changes may already be staged; preserve them and unrelated work. Follow the repository
instructions for staging, commits and pushes.

Start at the first unfinished fix in the roadmap. Honor its dependencies, implement its
smallest required change, and run its acceptance checks. Skip optional items such as
F13 rehearsal packaging. Treat F06/F08/F11 as completed generic work, not requests for
more features. Reuse existing tests; add coverage for
real missing behavior. Continue through the remaining locally actionable fixes. This
handoff requests implementation, verification and retained evidence within the course
scope. Do not turn optional engineering choices into additional completion conditions.

Keep facts in their owning files:
- docs/roadmap.md: fix status, requirements gaps and next action.
- docs/target_scenarios.md: target provenance, source mapping, exact refs and scope.
- docs/evaluation.md and docs/usage.md: reproducible execution instructions.
- docs/ci.md: CI operation; docs/defense_guide.md: contributor study and practice.
- artifacts/: distinct durable run records with commands, results, identities and hashes.

Justify the selected observable behavior and independent expectations before relying on
target verdicts. Fixed documentation-based or independently reviewed fixture expectations
can suffice; a general-purpose decoder or arbitrary-input reference executable is not
required. Change a driver only where the agreed behavior needs it.
Never derive expectations from patched output, scenario names, branch/commit identifiers
or a model's assertion. A trigger is not semantically invalid merely because it exposes
memory corruption. Keep corresponding release/sanitized builds and inputs equivalent.
Keep the validator generic; target-specific behavior belongs in source/config/test assets.

Treat the original assignment as authority. Do not introduce a 20 MB cap, a particular
CI provider or a special rehearsal-package format as instructor requirements. Do not
require exhaustive formats, universal dependency pins, all binary protections enabled,
branch-execution proof, organic regression bugs or scalability work. Inspection of the
four protections and downgrade warnings remain required. Deliberate driver regressions
can qualify within the declared/approved target contract. Prepare
instructor-review materials, but do not claim approval without the response. Technical
work can continue while external approval is pending. Actual participation, unaided
student defenses and instructor unseen-patch evaluation remain human/external events.

Run historical targets only in the documented isolated, resource-limited local lab.
Preserve source/license provenance and separate run identities. After source changes,
freeze new scenario refs and regenerate affected evidence honestly. Do not rewrite old
observations or relabel synthetic/harmless runs as selected-target acceptance.

After each coherent fix, inspect its actual reports/replays/tests, retain the necessary
evidence, and update that fix in the roadmap. State the tested revision or normalized
source hashes, commands, actual results and limits. A six-row expected-code table or an
unexecuted workflow does not close an acceptance item. Do not mark external events done.

Before handoff, run the required final checks, review the complete diff, remove only
superseded or task-created temporary material, and stage the authorized changes. Report
completed fix IDs, tests actually run, retained evidence, any genuine blocker and the
first unfinished action. Provide the exact commit command; the user commits/pushes.
Keep this file as the single agent handoff; do not create tool- or model-specific copies.
```
