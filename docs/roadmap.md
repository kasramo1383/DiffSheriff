# Live implementation roadmap

This is the single current record of implementation state, known gaps, and the next
work step. The instructor's PDF (`course_assignment.pdf`) is authoritative; its English
digest is `specification.md`. Target facts and approval evidence belong only in
`target_scenarios.md`. Contributor roles remain in the README.

## Current assessment

The defensive validator is implemented, with the gaps below still open. Course
acceptance depends on the approved targets, scenario matrices, and evidence in
Step 6.

The Windows audit of `07914aa` reproduced 90 passing tests with one Docker test
skipped. Black, Flake8, and wheel construction also passed. The GitHub Actions run
for that commit passed its unit jobs and native smoke test.
[GitHub Actions run 42911443863](https://github.com/kasramo1383/DiffSheriff/actions/runs/42911443863)

The retained Linux test results and separate standalone CLI run are indexed in the
[artifact inventory](../artifacts/README.md). Both native runs exercised the harmless
echo fixture. The test results cover the existing suite, and the CLI bundle provides
the inputs, builds, and report for that run. Steps 1 and 5 describe the remaining
test coverage, and Step 6 covers course acceptance.

The following defects remain open:

1. A correct insertion-only guard patch can remain inconclusive: the fixed verdict
   requires baseline stack correlation to an old changed line, which such a patch
   does not have. See `pipeline.py` `compare_case()` and `correlator.py`.

Security minimization now executes unknown reductions against the diagnostic
invariant without requiring expected functional output. Replay distinguishes those
checks, and generated functional checks keep the original input when necessary.
Verification is retained in [the minimization checkpoint](../artifacts/checkpoints/minimization/README.md).

Functional regression classification now uses the independent expectation's
`valid_input` designation. Approved valid boundary cases count in functional totals,
can produce exit 20, and retain that designation in generated regressions. Existing
manifests keep their suite defaults. Verification is retained in
[the boundary checkpoint](../artifacts/checkpoints/boundary/README.md).

## Agent handoff and review contract

Use this roadmap as the task source when handing work to an agent. Do one numbered step
at a time. Each step must be a small, reviewable change with a focused test, a concise
report of files and behavior changed, and exact verification results. Give Kasra the
commands to reproduce the checks, including expected failures and any skips. Stop
for Kasra's review before beginning the next step. Follow the repository's Git
instructions in [AGENTS.md](../AGENTS.md). Update the checkpoint and link its
evidence here after Kasra accepts the step.

If a step's requirements are ambiguous, inspect the PDF and relevant implementation,
state the narrow uncertainty, and ask before making a behavior-changing assumption.
Use small local/synthetic fixtures for code tests. Security tests must stay within
explicitly authorized local targets and safe lab inputs. Do not create weaponized
payloads, target real third-party systems, or expand the task into exploit tooling. If
a safety system blocks a narrowly defensive test, stop that step and report the exact
blocked action and a safe test substitute; do not disguise or route around the block.

## Staged implementation

### Step 1 — Add failing tests for the three confirmed defects

Add focused tests only. Cover: (a) insertion-only guard fix with baseline failure,
patch success, and defensible comparative evidence; (b) minimization of a synthetic
sanitizer failure when no independent functional oracle is configured; and (c) a
baseline-passing boundary input whose patched result violates the independent expected
behavior. Tests should fail for the current defects and pass independently when their
respective behavior is corrected. Do not change production code in this step.

Extend the existing pipeline and correlator tests where they fit. The Linux JUnit
record predates these cases. For review, give the test node IDs, the exact command,
and the assertion each case fails on. Confirm each failure comes from the behavior
under test and keep the existing assertions intact.

### Step 2 — Correct failure-input minimization

Adjust the minimization oracle so security findings preserve the same classified error
and relevant source location independently of expected functional output. Execute
candidate reductions in the same constrained environment and verify that the reduced
case reproduces across at least three runs. Reject timeouts and resource limits as
minimization matches. A nonzero exit alone cannot establish the invariant.

Retain both inputs and record the invariant and reduction attempts. A reduced input
without an independent expected result can support diagnostic replay. Keep the
original input for functional regression checks until an independent expectation is
available for the reduced input. Replay and generated regression reports must
reflect which checks the evidence supports.

Acceptance: Step 1(b), regression/replay cases, and focused minimizer tests pass; no
security assertion is weakened; the report explains byte-for-byte what is retained.

### Step 3 — Correct functional regression classification

Define suite semantics from the assignment rather than treating `valid` as the only
functional suite. Valid boundary cases with independent expected behavior must be
eligible for regression classification. Invalid/malicious inputs must not be mislabeled
as functional regressions unless independently designated as valid behavior. Make the
smallest schema or comparison change that expresses this distinction; avoid a broad
configuration redesign.

Acceptance: Step 1(c), valid regression, ordinary invalid-input, and exit-priority tests
pass. Confirm exit `20` for an isolated functional regression and preserve `30 > 10 >
20 > 40 > 0` when conditions coexist.

### Step 4 — Make fixed-finding evidence work for insertion-only patches

Revise correlation/fix assessment so a baseline finding can be linked to a patch that
adds a guard without modifying the vulnerable source line. Use comparative executions,
stack/path evidence, and the actual diff; report inconclusive whenever evidence does not
support attribution. Do not infer causality from file proximity, patch names, known
commits, or the fact that a test stopped crashing. Keep new findings distinct from
patch-caused findings.

Acceptance: Step 1(a), existing diff/correlation tests, and negative tests with missing
or ambiguous attribution pass. A correct insertion-only patch can reach `PASS` only
when every mandatory check and independent functional expectation also passes.

### Step 5 — End-to-end synthetic acceptance matrix

Run the focused tests from Steps 1–4 alongside the existing parameterized CLI tests.
Add CLI cases only where those fixes lack coverage at the command-line entry point.
Keep coverage for fixed, incomplete, new, functional regression, inconclusive,
unstable, and tool failure outcomes. Verify that replay works and that a subsequent
run loads a generated regression. Run the existing native Docker smoke test where
Docker is available and report it as infrastructure coverage.

For acceptance, run the focused cases, full suite, formatting, lint, and package
build. Record the tested revision, commands and outcomes, including what was mocked,
what ran natively, and any skips. Follow the [artifact policy](../artifacts/README.md)
for evidence the team needs to retain.

### Step 6 — Onboard approved targets when assets are available

This step depends on human-supplied target facts and instructor approval. Do not invent
targets, refs, approval, ground truth, or vulnerability claims. For each approved
target, record provenance, license, exact four source scenarios, independent valid /
boundary / invalid expectations, permitted safe test inputs, build instructions, and
approval evidence in `target_scenarios.md` or its linked target assets.

Evaluate vulnerable baseline, correct patch, incomplete patch with the distinct
approved alternative input required by the assignment, and regression patch. Run both
release and sanitized modes, retain three or more replays and artifacts, and verify the
expected exit codes in the [scenario contract](target_scenarios.md#scenario-contract-for-each-target).
At least one target must be a real non-toy project. Record any missing assets or
approval in the target scenario record.

Acceptance: two target matrices, including one real non-toy project, are reproducible
from delivered source/assets and have instructor approval and independent expected
behavior evidence. Until then, course acceptance remains incomplete.

### Step 7 — Defense and delivery review

After target acceptance, verify standalone instructions from a clean environment,
inspect reports/artifacts for completeness, and have each contributor explain their
owned logic and make a small reviewed change. Record only completed acceptance state,
not a transcript or activity log.

## Current checkpoint

- The user authorized implementing, verifying, and committing each gap before moving
  to the next. Steps 1(b/c), 2, and 3 are implemented and locally verified; this does
  not record human acceptance or course-target approval.
- Next: Step 1(a) and Step 4, insertion-only patch attribution.
- Step 6 depends on instructor-approved targets and the assets in the
  [target scenario record](target_scenarios.md).

## Durable engineering constraints

- Keep the package flat. No plugin framework, database, web service, or unnecessary
  forwarding layers.
- No verdict selection based on target name, file name, branch, commit, or patch hash.
- Keep target execution local, isolated, resource-limited, and offline.
- A confirmed patch finding and a claim that the patch caused it are separate judgments.
- Preserve full run bundles and report external image/tool dependencies accurately.
- Never mark target approval, real-target acceptance, or human defense complete based
  on synthetic fixtures or documentation alone.
