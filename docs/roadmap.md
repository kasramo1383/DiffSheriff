# Live implementation roadmap

This is the single live record of project status, completion gates, and next work.
The instructor's Persian assignment in [`course_assignment.pdf`](course_assignment.pdf)
is authoritative. [`specification.md`](specification.md) is a working English digest
and yields to the PDF. [`target_scenarios.md`](target_scenarios.md) is the sole record
of target identity, provenance, approvals, exact refs, input scope, and independent
ground truth. This roadmap links to those records instead of copying their mutable
facts.

Keep the project understandable to a student who has not written every line.
Implementation may be delegated to one or two coding agents. The project does not use
an issue board, sprint plan, CI/CD activity bureaucracy, or required per-task log. CI
is part of the product and its verification only.

## Completion standard

The project is complete only when the generic tool, two approved target evaluations,
retained evidence, standalone delivery, and four individual defenses satisfy the gates
below. A working generic pipeline, synthetic tests, harmless native fixture, or a
successful CI run alone does not complete the assignment.

A stage is complete when its acceptance criteria pass, the tested source revision and
commands are recorded, durable evidence is checked into `artifacts/` where appropriate,
and the next stage is explicit. Agents stop for Kasra's review after each bounded
implementation stage. Do not mark human review, instructor approval, target acceptance,
or student defense complete on anyone's behalf.

## Current state

- The generic Python CLI, Docker execution, source comparison, triage/correlation,
  minimization/replay, regression generation, ELF hardening inspection, JSON/reporting,
  exit priorities, and tool-verification workflows are implemented. See
  [`architecture.md`](architecture.md) for module boundaries and [`usage.md`](usage.md)
  for operator behavior.
- Minimized-result classification has implementation and evidence in
  [`minimized-results`](../artifacts/checkpoints/minimized-results/README.md). The
  checkpoint reports focused and full test runs plus a harmless native run. This is
  synthetic/infrastructure evidence, not real-target acceptance. Kasra's acceptance
  is not recorded.
- The local Black/CI configuration correction is recorded in
  [`ci-format`](../artifacts/checkpoints/ci-format/README.md). Its checkpoint says the
  workflow was not rerun on GitHub after the formatting correction.
- Stage 2 below, regression-cache reconciliation, remains unimplemented.
- No course target, vulnerability, four-version scenario set, functional oracle, or
  expected-output corpus is recorded as instructor-approved. The zlib/libpng entries
  in [`target_scenarios.md`](target_scenarios.md) are unapproved proposals. Neither was
  built or executed in the recorded target research. The harmless echo fixture is not
  a course target.
- No approved-target scenario matrix, hosted target validation, blind/unseen-patch
  evaluation, clean-room delivery run, or individual defense has been completed.

Never transfer a passing result to a different source revision or container image.
Re-check source hashes before treating a checkpoint as evidence for current code.

## Requirement-to-evidence map

The PDF grading categories are the completion checklist. Status means what the
repository currently proves, not what code appears to support in principle.

| PDF category | Points | Current evidence | Required completion evidence |
| --- | ---: | --- | --- |
| Patch validation, version comparison, precise diff correlation | 25 | Generic synthetic checks and code exist; no approved-target matrix proves correlation on real source changes. | On both targets, retain fixed, incomplete, new-issue where applicable, regression, and inconclusive evidence. Relate findings to changed files/functions/paths using runtime and diff evidence, or report attribution inconclusive. |
| Dynamic tests, boundaries, build separation, error classification | 25 | Synthetic tests and harmless native release/sanitized matrix exist. | Same approved valid, boundary, invalid corpora/settings across baseline and patch. Compare release with release and sanitized with sanitized. Retain category, mechanism, actual termination, signals, stdout/stderr, limits, and replay stability. |
| Reproducibility, minimization, regression generation | 15 | Generic implementation, synthetic reports, replay tests, and minimized-results checkpoint exist. | For every confirmed target finding, preserve exact input/version/binary/build/environment/command, original and minimized bytes, at least three replay results, and an automatically enrolled regression that checks baseline finding plus independent patched behavior. Resolve unknown expectations before claiming a completed regression test. |
| Two target scenarios and unseen-patch behavior | 15 | Candidate research only; instructor approval pending; no target scenario refs or matrices. | Two independent approved C/C++ Linux x86_64 targets, at least one real non-toy project/library. Each has baseline, correct, incomplete, and regression versions. Retain a blind/unseen evaluation without target-specific recognition. Instructor defense-day testing remains external. |
| CI/CD, JSON, exit codes | 10 | Reusable/manual target workflow and main verification workflow exist; local verification is recorded. | Fix cache-import conflict, verify all codes/priorities without overriding results, check hosted tool verification after the Black correction, and retain an approved correct-patch hosted run and artifacts. |
| Binary hardening and protection changes | 5 | ELF parser and synthetic/native evidence exist. | For ordinary target binaries, retain NX, PIE, RELRO level, and canary evidence and compare baseline/patch downgrades. PIE does not prove runtime ASLR; a canary symbol does not prove every function is protected. |
| Documentation, modularity, standalone execution | 5 | README, architecture, usage, CI notes, package, and artifacts exist. | A clean checkout installs/builds/runs/replays using delivered instructions and declared dependencies. Include target sources/refs/licenses, configs, inputs, reports, pipeline definition, and reproducer bundles. |

The group technical score is out of 100. Each student also needs a separate defense out
of 10: architecture and owned logic (3), finding/evidence analysis (3), and a limited
live change plus test (4). Participation must be genuine. A defense score of at least
5, with at least one point in each category, and effective participation are required
for individual credit.

## Completion path

### Stage 1 - Review minimized-result classification

**Status: implementation and verification evidence recorded; Kasra's acceptance is
pending.** Read the complete
[`minimized-results` checkpoint](../artifacts/checkpoints/minimized-results/README.md)
and inspect its source identity. It reports that stable minimized observations enter
ordinary comparison and exit-priority rules, findings are deduplicated against the
parent case, reduced-input validity is independently established, and minimization is
not recursive. Synthetic and harmless-native limits are explicit.

**Review gate:** accept this bounded change or return specific defects. It must retain
independent statuses and exit priority, preserve distinct minimized findings, avoid
duplicate parent findings, and keep unknown expected behavior inconclusive. Do not
repeat its full verification without a review finding, changed source hash, or
incomplete evidence. Do not claim Kasra accepted it until that decision is recorded.

### Stage 2 - Reconcile trusted regression-cache imports

**Status: open; next implementation stage after Stage 1 review.**
`copy_regressions()` in `diffsheriff/regressions.py` rejects byte-different source and
destination files. A cache can carry an older `expected: null` diagnostic manifest and
block a matching checked-in manifest after the team independently approves an
expectation. Manual cache retirement is not a durable CI behavior.

**Work:**

1. Inspect the manifest schema, generated filenames, import/export CLI, discovery,
   cache workflow, and current conflict tests. Define identity before treating two
   manifests as the same case: exact baseline ref, input bytes and verified digest,
   build mode, finding identity, case kind, and any other field that changes replay
   meaning.
2. Prefer a checked-in, independently reviewed expectation to an incoming diagnostic
   `null` expectation only when all identity fields and payload bytes match. Never
   trust a non-null expectation solely because it came from cache. Fail closed for
   mismatched identity, different payload, corrupt hash, traversal, symlink, or
   conflicting non-null expectations.
3. If metadata cannot safely distinguish the approved local case from unrelated cache
   conflicts, add the smallest explicit operator-controlled cache bypass and document
   it. Do not silently overwrite/discard files, weaken hash/path checks, or guess which
   expectation is correct.
4. Add focused tests for stale diagnostic cache plus approved local expectation,
   byte-identical/idempotent transfer, every identity mismatch, conflicting non-null
   expectations, corrupt hash, traversal, symlink, and preservation of local bytes.
   Exercise CLI import/export as well as the helper.
5. Run focused tests, the complete suite, Black, and Flake8. Inspect manifests and
   verify local expectations remain unchanged. Record tested commit, commands/results,
   and limitations in a checkpoint under `artifacts/checkpoints/`; update [`ci.md`](ci.md)
   and link the evidence here.

**Accept when:** stale diagnostic cache data cannot block a matching approved local
expectation; cache cannot manufacture or overwrite ground truth; unrelated/corrupt
conflicts still fail safely; repeated transfers are idempotent. Stop for review.

### Stage 3 - Obtain target and test-scope approval

**Status: external team/instructor decision.** Current candidates are proposals, not
approval. Review or replace them using [`target_scenarios.md`](target_scenarios.md).
Do not build, execute, or create target-specific inputs before the team/instructor
confirms target pair, vulnerability/patch sources, interface, functional specification,
and permitted test scope.

For each target, record in the target approval table:

- upstream project, exact source URL, license and redistribution conditions;
- vulnerable baseline and correct upstream fix as full commit hashes, with source
  parent relationship checked;
- why the target is compiled C/C++ producing Linux x86_64 ELF; at least one of the two
  must be a real non-toy project/library, and the pair must be independent;
- stable input interface and any separately written C/C++ driver;
- primary independent specification/reference tests and expected exit/stdout/stderr;
- valid, boundary, and invalid-input scope;
- instructor confirmation and date, preserved as actual evidence.

For proposed zlib/libpng, different names do not establish independence. Hold libpng's
zlib dependency at one separately pinned version in every libpng scenario. Confirm
buildability, fault reproducibility, deterministic behavior, license compatibility,
and a legitimate regression case before finalizing the pair. If a candidate fails a
go/no-go check or approval is unavailable, record the blocker and select a replacement
with the instructor. Continue independent tool work while approval is pending.

**Accept when:** both target records, test scope, independent expected behavior, and
source/license provenance are approved and reproducible. A proposal never becomes a
target merely by being listed.

### Stage 4 - Freeze and package both scenario sets

Proceed only with approved targets. Preserve the four source versions per target in the
delivered project in a form that makes exact versions reproducible without an unmanaged
nested Git checkout. Retain source history or exact source archives, upstream patch
refs, team changes, license notices, and hashes. `targets/` currently contains only a
placeholder.

Prepare four distinct versions per target:

1. **Vulnerable baseline:** at least one memory error is reproducible with recorded
   input.
2. **Correct patch:** target error is absent in the declared scope and valid behavior
   passes.
3. **Incomplete patch:** original trigger is blocked; a different, explicitly
   authorized local input reaches the same underlying flaw. Record its provenance and
   why it remains in scope. It must not merely introduce another bug.
4. **Regression patch:** target error is blocked and at least one independently valid
   behavior passed by baseline is broken. Do not derive expected behavior from patched
   output.

Record exact source identity for each version. Confirm all four build with the same
declared toolchain and dependencies. Use one generic config/input contract per target.
Do not add target/file/branch/commit/hash-specific verdict logic.

**Accept when:** two target source packages and all eight scenario versions are
present, licensed, hash-checked, buildable, and reviewed; refs/configs cannot silently
drift. Stop for review.

### Stage 5 - Freeze independent tests and expectations

Before evaluating patch outcomes, define one approved corpus per target with valid,
boundary, and invalid inputs, plus data needed for vulnerability and regression cases.
Record input provenance and classification. Apply the same corpus, input delivery,
settings, and limits to baseline and patch in corresponding build modes.

For every input, specify independent expected exit code, stdout, stderr, and validity.
Include valid boundary inputs. Explain any output normalization only when it is
deterministic and preserves specified behavior. An approved reference implementation
must be genuinely independent and implement the approved spec. Never copy patched
output or use LLM opinion as ground truth.

Check discovered files exactly match the expected manifest. Verify valid inputs pass on
baseline before using them as regression evidence. Invalid inputs still check expected
behavior but are not valid-input regressions unless independently designated valid.
Keep every test safe, local, and approved.

**Accept when:** approved expectation source, exact corpus, validity flags, and
interface are frozen and hash-recorded for both targets. Missing or ambiguous ground
truth blocks acceptance.

### Stage 6 - Run and repair target acceptance matrices

Run DiffSheriff for each approved baseline against each of its three patch versions.
Keep each target config constant apart from the full baseline/patch refs. Exercise all
valid, boundary, invalid, and vulnerability inputs under release and sanitized builds;
compare only corresponding modes. Preserve exact source and image hashes.

| Scenario | Required evidence | Expected result |
| --- | --- | ---: |
| Vulnerable baseline | Stable designated memory error; independent functional behavior characterized. | Must not pass as fixed. |
| Correct patch | Baseline finding reproduced; absent on patch in scope; expected behavior passes; no other confirmed issue; mandatory checks complete. | 0 |
| Incomplete patch | Original trigger blocked; distinct approved input reproduces same underlying finding; correlation and uncertainty accurate. | 10 |
| Regression patch | Security finding absent; baseline passes independently valid input; patch violates that expectation. | 20 if no code 10 or 30 condition applies. |

Keep confirmed new security findings at code 10 even when causation is inconclusive.
Tool/build/config failure stays code 30. Incomplete mandatory checks retain code 40
status and evidence, subject to priority `30 > 10 > 20 > 40 > 0`. Never rewrite a result
to make a scenario pass.

For every confirmed finding inspect: error category versus detection mechanism; actual
exit/signal; stdout/stderr; timeout/resource-limit outcome; at least three replays;
source/binary hashes; build settings/environment/command; stack and diff/function/path
correlation; original and minimized input; and final report status. Reduction must
preserve error type and relevant location, not merely nonzero exit. Regression findings
must use independent expected behavior and equivalent baseline/patch settings. Inspect
ordinary-binary NX, PIE, RELRO level, and canary evidence and report downgrades.

Generated regressions must be added automatically and exercised on a later run. Each
must show the expected baseline finding and check its absence plus expected behavior on
the correct patch. If minimized behavior lacks independent expectations, retain the
diagnostic reproducer but mark the functional check incomplete; resolve expectations
from an approved source before acceptance.

If an outcome fails, fix generic pipeline or approved assets and repeat the affected
matrix. Preserve failed attempts honestly; never combine different source/image hashes.
Accept a matrix only when every comparison has a correct explainable result and
reproducible artifacts. Stop for review after each target's bounded matrix.

### Stage 7 - Complete CI and cross-environment validation

Use the existing workflows without target-specific bypass or extra process machinery.

1. Run full local suite, format/lint checks, package build, and harmless native
   container matrix on final tool revision. Use Docker through WSL when required.
2. Check GitHub verification after the latest Black fix. Resolve failures at their
   source; retain run URL/result and artifacts.
3. Configure the reusable/manual target workflow only with approved config/source
   assets. Run correct-patch acceptance on GitHub and retain reports/run artifacts.
   Confirm cache restore/save/export follows Stage 2 behavior.
4. Exercise codes 0, 10, 20, 30, 40. Confirm target CI gates on actual CLI result; only
   0 passes. Record intentionally failing variants as expected nonzero local results.
   Never override their verdicts to make the workflow green.
5. Inspect JSON for independent security, functional, completeness statuses, exact
   versions/settings, findings, evidence, and selected priority exit code.

**Accept when:** final-revision local checks and hosted tool verification pass, and
approved correct-patch hosted validation returns 0 with retained evidence. Do not claim
hosted target validation while approval/configuration is absent.

### Stage 8 - Clean-room delivery and evidence audit

Use a fresh checkout or WSL directory without the project virtual environment, ignored
`.diffsheriff/` state, or developer-only files. Follow the standalone guide using only
delivered inputs and declared prerequisites. Install the package, build the image,
validate both approved correct patches, inspect JSON/readable output, replay at least
one finding per target, and verify generated-regression loading. Record commands,
tool versions, source/image hashes, results, and external dependencies.

Audit delivery includes tool source; configs; exact four source versions per target and
licenses; independent input corpora/expectations; build/runtime/pipeline definitions;
generated regression tests; original/minimized bundles; target reports; hashes; and
standalone instructions. Verify Git tracks required artifacts and `.gitignore` hides
none. Remove task-created temporary files only. Keep evidence from different source
revisions/images separate.

**Accept when:** an uninvolved teammate can reproduce the clean run and replay from the
delivered project without chat history or temporary machine paths, apart from declared
external tools/images.

### Stage 9 - Prepare blind evaluation and individual defenses

Prepare a blind evaluation within the approved target domain/interface. A teammate
outside the implementation of classification supplies unseen patch refs without
revealing labels. Run the generic tool, retain observations, then compare with
independently documented outcomes. Add no patch-specific recognition. Keep this team
exercise separate from instructor defense-day unseen patches; the latter remains an
external event until it occurs.

Each of the four students studies the complete pipeline and their README-owned
subsystem. Each must individually explain architecture/design/owned logic, analyze a
finding and its raw evidence/correlation/priority, and make/test a small relevant
change. The assignment requires this defense without help from other students or
generative tools. Do not fabricate participation evidence.

**Accept when:** blind team exercise is reproducible and accurately labeled; each
student completes their own preparation and defense. Record instructor evaluation only
after it occurs.

## Engineering and evidence rules

- Keep the package flat and the flow explainable: config, snapshot/build, hardening,
  execution, comparison, triage/correlation, replay/reduction, report. Add no framework,
  service, database, task board, sprint process, or abstraction without a requirement.
- Never select a verdict using target, filename, branch, commit, or patch hash. Keep
  target details in config, drivers, approved inputs, and independent expectations.
- Run only permitted targets in isolated, resource-limited, offline environments. Do
  not create exploit tooling or expand approved input scope.
- Separate observed error from category, detection, cause, and patch attribution.
  Missing evidence is inconclusive; absence in a finite suite is not proof no flaw exists.
- Retain real commands/results, tool versions, commit/image identities, hashes, skips,
  and limits. Label synthetic/harmless evidence as such.
- Read `AGENTS.md` and relevant checkpoints before changes/rechecks. Preserve unrelated
  work. Do not commit or push unless Kasra explicitly requests it; prepare requested
  changes for review and give the exact commit command as instructed.

## Next action

Kasra reviews and records a decision on Stage 1's minimized-results checkpoint. If
accepted, Stage 2 is next. If returned, fix only the specified Stage 1 defect first.
Target approval is a team/instructor dependency. While pending, finish Stage 2 and other
independent work; do not invent approval or execute proposed targets.
