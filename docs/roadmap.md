# Live implementation roadmap

This is the single live record of project status, completion gates, and next work.
The instructor's Persian assignment in [`course_assignment.pdf`](course_assignment.pdf)
is authoritative. [`specification.md`](specification.md) is a working English digest
and yields to the PDF. [`target_scenarios.md`](target_scenarios.md) is the sole record
of target identity, provenance, selection decisions, exact refs, input scope, and independent
ground truth. This roadmap links to those records instead of copying their mutable
facts.

Keep the project understandable to a student who has not written every line.
Implementation may be delegated to one or two coding agents. The project does not use
an issue board, sprint plan, CI/CD activity bureaucracy, or required per-task log. CI
is part of the product and its verification only.

## Completion standard

The repository implementation is complete only when the generic tool, two selected
target evaluations, retained evidence, standalone delivery, blind-evaluation materials,
and individual-defense preparation satisfy the gates below. The actual four individual
defenses and any instructor-only unseen-patch event are later human/external events and
cannot be performed or claimed by an implementation agent. A working generic pipeline,
synthetic tests, harmless native fixture, or a successful CI run alone does not complete
the repository work.

A stage is complete when its acceptance criteria pass, the tested source revision and
commands are recorded, durable evidence is checked into `artifacts/` where appropriate,
and the next stage is explicit. Keep implementation in bounded, verifiable steps and
update this roadmap so another engineer or agent can resume immediately. The project
owner has directed the implementation agent to determine the target pair and test scope
from the PDF and primary evidence. Do not wait for a nonexistent team/instructor approval
loop. Never label that internal selection as instructor approval, and never claim a
student defense without the corresponding evidence.

## Current state

- The generic Python CLI, Docker execution, source comparison, triage/correlation,
  minimization/replay, regression generation, ELF hardening inspection, JSON/reporting,
  exit priorities, and tool-verification workflows are implemented. See
  [`architecture.md`](architecture.md) for module boundaries and [`usage.md`](usage.md)
  for operator behavior.
- Minimized-result classification has implementation and evidence in
  [`minimized-results`](../artifacts/checkpoints/minimized-results/README.md). The
  checkpoint reports focused and full test runs plus a harmless native run. This is
  synthetic/infrastructure evidence, not real-target acceptance. Implementation and
  recorded generic verification are complete; no personal acknowledgment is project
  evidence.
- The local Black/CI configuration correction is recorded in
  [`ci-format`](../artifacts/checkpoints/ci-format/README.md). Subsequent hosted
  verification [run #21](https://github.com/kasramo1383/DiffSheriff/actions/runs/43585656728)
  passed both Python jobs and the native-container job on
  `006113f5c7e1bf652bbb3ec198e4f6b3866487cf`; target validation was skipped because
  no target config was supplied. The [evidence-integrity checkpoint](../artifacts/checkpoints/evidence-integrity/README.md)
  records the new retained-artifact hash test, 205 Windows passes with eight
  platform-dependent skips, five focused Linux integrity cases, Black, and Flake8.
  An independent check of the current checkout found all 408 retained manifest
  entries match their artifact bytes. The
  [hosted verification record](../artifacts/checkpoints/ci-format/hosted-verification.json)
  preserves runs #21, #20, #19, and #17. These checks do not complete selected-target
  CI acceptance.
- Stage 2 regression-cache reconciliation is implemented and verified. See the
  [cache-import checkpoint](../artifacts/checkpoints/cache-import/README.md). This is
  generic-tool evidence, not target acceptance.
- The [reference comparison](reference_comparison.md) is supplementary to the PDF and
  maps optional features. Compatible additions (per-build ELF symbol
  evidence, fuller console output, one-command verification, and a UBSan termination
  fix) are verified in the [reference-parity checkpoint](../artifacts/checkpoints/reference-parity/README.md).
  Its full suite passed 203 Linux tests; Windows passed 196 with seven platform skips.
  These additions do not change the assignment's source of truth or establish target
  acceptance.
- A subsequent code audit repaired five reproduced defects in UTF-8 reduction,
  reference decoding, release-mode validation, replay identity, and replay output
  symlinks. The [code-audit checkpoint](../artifacts/checkpoints/code-audit/README.md)
  records 208 Linux passes and 200 Windows passes with eight platform skips, lint,
  formatting, package/source identity, and harmless native verification. No known
  generic implementation gap from that bounded audit is being deferred;
  actual target behavior remains to be evaluated. See the [evaluation procedure](evaluation.md)
  for exact preparation, six comparisons, replay, CI, and delivery steps.
- Stage 3 target selection and feasibility verification is COMPLETE. zlib (CVE-2018-25032)
  and libpng (CVE-2019-7317) have passed bounded Linux x86_64 ELF build and AddressSanitizer
  reproduction gates with deterministic C drivers and staged corpora. Dependency isolation is
  enforced with pinned system zlib for libpng. Packaging of the eight scenario versions
  (Stage 4), independent expectation manifests (Stage 5), and the final evaluation matrices
  (Stage 6+) remain to be completed.
- No selected-target scenario matrix, hosted target validation, blind/unseen-patch
  evaluation, clean-room delivery run, or individual defense has been completed.

Never transfer a passing result to a different source revision or container image.
Re-check source hashes before treating a checkpoint as evidence for current code.

## Requirement-to-evidence map

The PDF grading categories are the completion checklist. Status means what the
repository currently proves, not what code appears to support in principle.

| PDF category | Points | Current evidence | Required completion evidence |
| --- | ---: | --- | --- |
| Patch validation, version comparison, precise diff correlation | 25 | Generic synthetic checks and code exist; no selected-target matrix proves correlation on real source changes. | On both targets, retain fixed, incomplete, new-issue where applicable, regression, and inconclusive evidence. Relate findings to changed files/functions/paths using runtime and diff evidence, or report attribution inconclusive. |
| Dynamic tests, boundaries, build separation, error classification | 25 | Synthetic tests and harmless native release/sanitized matrix exist. | Same selected valid, boundary, invalid corpora/settings across baseline and patch. Compare release with release and sanitized with sanitized. Retain category, mechanism, actual termination, signals, stdout/stderr, limits, and replay stability. |
| Reproducibility, minimization, regression generation | 15 | Generic implementation, synthetic reports, replay tests, and minimized-results checkpoint exist. | For every confirmed target finding, preserve exact input/version/binary/build/environment/command, original and minimized bytes, at least three replay results, and an automatically enrolled regression that checks baseline finding plus independent patched behavior. Resolve unknown expectations before claiming a completed regression test. |
| Two target scenarios and unseen-patch behavior | 15 | Candidate research only; project selection and feasibility testing pending; no target scenario refs or matrices. | Two independent selected C/C++ Linux x86_64 targets, at least one real non-toy project/library. Each has baseline, correct, incomplete, and regression versions. Retain a blind/unseen evaluation without target-specific recognition. Instructor defense-day testing remains external. |
| CI/CD, JSON, exit codes | 10 | Reusable/manual target workflow and main verification workflow exist; local verification and cache reconciliation are recorded. | Verify all codes/priorities on the final revision without overriding results, check its hosted tool verification, and retain a selected correct-patch hosted run and artifacts. |
| Binary hardening and protection changes | 5 | ELF parser and synthetic/native evidence exist. | For ordinary target binaries, retain NX, PIE, RELRO level, and canary evidence and compare baseline/patch downgrades. PIE does not prove runtime ASLR; a canary symbol does not prove every function is protected. |
| Documentation, modularity, standalone execution | 5 | README, architecture, usage, CI notes, package, and artifacts exist. | A clean checkout installs/builds/runs/replays using delivered instructions and declared dependencies. Include target sources/refs/licenses, configs, inputs, reports, pipeline definition, and reproducer bundles. |

The group technical score is out of 100. Each student also needs a separate defense out
of 10: architecture and owned logic (3), finding/evidence analysis (3), and a limited
live change plus test (4). Participation must be genuine. A defense score of at least
5, with at least one point in each category, and effective participation are required
for individual credit.

## Completion path

### Stage 1 - Minimized-result classification

**Status: implementation and recorded verification complete.** Read the complete
[`minimized-results` checkpoint](../artifacts/checkpoints/minimized-results/README.md)
and inspect its source identity. It reports that stable minimized observations enter
ordinary comparison and exit-priority rules, findings are deduplicated against the
parent case, reduced-input validity is independently established, and minimization is
not recursive. Synthetic and harmless-native limits are explicit.

The implementation must retain
independent statuses and exit priority, preserve distinct minimized findings, avoid
duplicate parent findings, and keep unknown expected behavior inconclusive. Do not
repeat its full verification without a review finding, changed source hash, or
incomplete evidence.

### Stage 2 - Reconcile trusted regression-cache imports

**Status: implementation and recorded verification complete.**
The [cache-import checkpoint](../artifacts/checkpoints/cache-import/README.md) records
199 Linux passes (including symlinks and the harmless native container test), 192
Windows passes with seven platform skips, formatter/linter checks, and the wheel.
Matching stale diagnostic cache entries now preserve reviewed local expectations
byte-for-byte. New non-null cached expectations require independently matching local
input bytes, behavior, and validity. Identity conflicts and corrupt metadata fail
before transfer writes. These are generic-tool checks, not selected-target evidence.

The verified behavior is:

1. A matching incoming diagnostic null expectation does not replace a reviewed local
   full expectation; the local manifest and payload remain byte-for-byte unchanged.
2. An incoming full expectation is accepted only with matching independent local
   evidence, including exact input bytes and expected behavior.
3. Identity conflicts, conflicting full expectations, corrupt hashes, invalid paths,
   traversal, and symlinks fail before transfer writes; repeated imports are idempotent.
4. CLI transfer behavior and the helper are covered by the checkpoint's tests.

See the checkpoint for tested revisions, commands, counts, platform skips, and limits.

### Stage 3 - Select and freeze the target pair and test scope

**Status: selection, driver design, and feasibility verification complete.**
The implementing agent has determined the target pair from primary upstream sources,
retained candidate archives, and verified local feasibility evidence under project-owner authorization.

Recorded evidence in [`target_scenarios.md`](target_scenarios.md):
1. **Target 1: zlib / CVE-2018-25032**: Baseline `e99813dbfe9a09e33d42e8da9e550a0c4b7ff734`,
   upstream fix `5c44459c3b28a9bd3283aaceab7c615f8020c531`. Driver `targets/target1/driver/zlib_driver.c`
   exposes `--file <path>` with `Z_FIXED` and `memLevel=1`. Baseline reliably crashes under
   ASan with `global-buffer-overflow` reading `_dist_code` at `trees.c:1093` (`compress_block`)
   on `targets/target1/corpus/cve_2018_25032.input`. Fix cleanly passes with exit code 0.
2. **Target 2: libpng / CVE-2019-7317**: Baseline `8439534daa1d3a5705ba92e653eda9251246dd61`,
   upstream fix `9c0d5c77bf5bf2d7c1e11f388de40a70e0191550`. Driver `targets/target2/driver/png_driver.c`
   exposes `--file <path>` via simplified read API. Baseline crashes under ASan with
   `stack-use-after-return` in `png_safe_execute` at `pngerror.c:954` (`png_image_free_function`).
   Fix cleanly passes with exit code 0.
3. **Dependency Isolation**: libpng dynamically links pinned system zlib (`-lz`), ensuring
   complete independence from Target 1.
4. **Corpus & Drivers Staged**: Drivers and corpora staged in `targets/target1/` and `targets/target2/`.

**Acceptance:** Both target records contain exact reproducible source/license facts, bounded test
scopes are established, and feasibility runs verify that baseline flaws reproduce under sanitizers
and upstream fixes cleanly pass. Proceeding to Stage 4.

### Stage 4 - Freeze and package both scenario sets

**Status: next implementation stage.** Proceed only with selected targets that passed Stage 3. Preserve the four source versions per target in the
delivered project in a form that makes exact versions reproducible without an unmanaged
nested Git checkout. Retain source history or exact source archives, upstream patch
refs, local changes, license notices, and hashes. `targets/` currently contains only a
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
drift. Record the checkpoint and continue to Stage 5.

### Stage 5 - Freeze independent tests and expectations

Before evaluating patch outcomes, define one selected corpus per target with valid,
boundary, and invalid inputs, plus data needed for vulnerability and regression cases.
Record input provenance and classification. Apply the same corpus, input delivery,
settings, and limits to baseline and patch in corresponding build modes.

For every input, specify independent expected exit code, stdout, stderr, and validity.
Include valid boundary inputs. Explain any output normalization only when it is
deterministic and preserves specified behavior. A reference implementation must be
genuinely independent and implement the selected specification. Never copy patched
output or use LLM opinion as ground truth.

Check discovered files exactly match the expected manifest. Verify valid inputs pass on
baseline before using them as regression evidence. Invalid inputs still check expected
behavior but are not valid-input regressions unless independently designated valid.
Keep every test safe, local, and within the recorded scope.

**Accept when:** the independent expectation source, exact corpus, validity flags, and
interface are frozen and hash-recorded for both targets. Missing or ambiguous ground
truth blocks acceptance.

### Stage 6 - Run and repair target acceptance matrices

Run DiffSheriff for each selected baseline against each of its three patch versions.
Keep each target config constant apart from the full baseline/patch refs. Exercise all
valid, boundary, invalid, and vulnerability inputs under release and sanitized builds;
compare only corresponding modes. Preserve exact source and image hashes.

| Scenario | Required evidence | Expected result |
| --- | --- | ---: |
| Vulnerable baseline | Stable designated memory error; independent functional behavior characterized. | Must not pass as fixed. |
| Correct patch | Baseline finding reproduced; absent on patch in scope; expected behavior passes; no other confirmed issue; mandatory checks complete. | 0 |
| Incomplete patch | Original trigger blocked; distinct in-scope input reproduces same underlying finding; correlation and uncertainty accurate. | 10 |
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
from an independent source before acceptance.

If an outcome fails, fix the generic pipeline or selected assets and repeat the affected
matrix. Preserve failed attempts honestly; never combine different source/image hashes.
Accept a matrix only when every comparison has a correct explainable result and
reproducible artifacts. Record each target's bounded matrix before continuing.

### Stage 7 - Complete CI and cross-environment validation

**Generic tool portion: implemented and verified. Target portion: pending selected
targets and their frozen test records.** Use the existing workflows without
target-specific bypass or extra process machinery.

1. The evidence-integrity checkpoint records the new manifest test and its local
   Windows/Linux, format, and lint results. The independent current-checkout audit
   found 408 of 408 retained artifact entries match.
2. Hosted run #21 on `006113f5c7e1bf652bbb3ec198e4f6b3866487cf` passed both unit
   jobs and the native-container job. Target validation was skipped because no target
   config was supplied. Preserve this distinction in all reports.
3. Configure the reusable/manual target workflow only with selected config/source
   assets. Run correct-patch acceptance on GitHub and retain reports/run artifacts.
   Confirm cache restore/save/export follows Stage 2 behavior.
4. Exercise codes 0, 10, 20, 30, 40. Confirm target CI gates on actual CLI result; only
   0 passes. Record intentionally failing variants as expected nonzero local results.
   Never override their verdicts to make the workflow green.
5. Inspect JSON for independent security, functional, completeness statuses, exact
   versions/settings, findings, evidence, and selected priority exit code.

**Generic portion acceptance:** the final tool revision passes local checks and hosted
tool verification. **Target portion acceptance:** selected correct-patch hosted
validation returns 0 with retained evidence. The generic portion is complete; do not
claim target validation while selected configuration or evidence is absent.

### Stage 8 - Clean-room delivery and evidence audit

Use a fresh checkout or WSL directory without the project virtual environment, ignored
`.diffsheriff/` state, or developer-only files. Follow the standalone guide using only
delivered inputs and declared prerequisites. Install the package, build the image,
validate both selected correct patches, inspect JSON/readable output, replay at least
one finding per target, and verify generated-regression loading. Record commands,
tool versions, source/image hashes, results, and external dependencies.

Audit delivery includes tool source; configs; exact four source versions per target and
licenses; independent input corpora/expectations; build/runtime/pipeline definitions;
generated regression tests; original/minimized bundles; target reports; hashes; and
standalone instructions. Verify Git tracks required artifacts and `.gitignore` hides
none. Remove task-created temporary files only. Keep evidence from different source
revisions/images separate.

**Accept when:** an uninvolved engineer can reproduce the clean run and replay from the
delivered project without chat history or temporary machine paths, apart from declared
external tools/images.

### Stage 9 - Prepare blind evaluation and individual defenses

Prepare a reproducible blind-evaluation package within the selected target
domain/interface. Include hidden-label scenario inputs or refs, an independently
recorded answer key, invocation instructions, and a result worksheet. The implementing
agent may verify package mechanics but must not claim that an independent human blind
exercise or the instructor's defense-day unseen patches occurred. Add no patch-specific
recognition.

Each of the four students studies the complete pipeline and their README-owned
subsystem. Each must individually explain architecture/design/owned logic, analyze a
finding and its raw evidence/correlation/priority, and make/test a small relevant
change. The assignment requires this defense without help from other students or
generative tools. Do not fabricate participation evidence.

**Repository accept when:** the blind package and defense-study materials are complete,
accurate, reproducible, and linked from the appropriate documentation. Actual student
practice/defenses and any instructor evaluation remain external facts recorded only
after they occur.

## Engineering and evidence rules

- Keep the package flat and the flow explainable: config, snapshot/build, hardening,
  execution, comparison, triage/correlation, replay/reduction, report. Add no framework,
  service, database, task board, sprint process, or abstraction without a requirement.
- Never select a verdict using target, filename, branch, commit, or patch hash. Keep
  target details in config, drivers, selected inputs, and independent expectations.
- Run only the selected local targets in isolated, resource-limited, offline
  environments. Do not create exploit tooling or expand the recorded input scope.
- Separate observed error from category, detection, cause, and patch attribution.
  Missing evidence is inconclusive; absence in a finite suite is not proof no flaw exists.
- Retain real commands/results, tool versions, commit/image identities, hashes, skips,
  and limits. Label synthetic/harmless evidence as such.
- Read `AGENTS.md` and relevant checkpoints before changes/rechecks. Preserve unrelated
  work. Do not commit or push unless Kasra explicitly requests it; prepare requested
  changes for review and give the exact commit command as instructed.

## Current next work

The generic implementation and its recorded synthetic/harmless-native verification are
complete through the cache-import, reference-parity, code-audit, and latest hosted
verification records. The implementing agent must now complete Stages 3 through 9 in
order: decide and freeze the pair/scope, construct all eight versions, freeze independent
corpora, run and repair both real-target matrices, complete local and available hosted
validation, perform a clean-room delivery audit, and prepare the blind/defense materials.
Work continuously through verified checkpoints; do not stop after research, a plan, one
target, or one successful scenario. Stop only for a genuine technical/safety blocker
after recording attempted alternatives and leaving the repository in a resumable state.

### Preparation-to-evaluation handoff

Stages 3–5 are preparation. They may be completed by Antigravity using
[`antigravity_preparation_instructions.md`](antigravity_preparation_instructions.md).
Bounded build, sanitizer, trigger-feasibility, baseline-validity, and packaging smoke
checks are allowed there because the scenario assets cannot be selected honestly without
them. Those checks do not replace the final matrices.

DeepSeek/Strix begins the final evaluation at Stage 6 after both target records, all eight
versions, both independent corpora/expectation manifests, and both target configs satisfy
their acceptance gates. It must verify the preparation and return to Stage 3–5 only if
the assets are incomplete or contradicted by evidence. Never run both agents concurrently
against the same writable checkout.

## Status correction request

When updating this roadmap or handing off the project, correct any unsupported,
outdated, or contradictory status claim. Derive status from the current source revision,
tests, workflows, and retained evidence. State what is implemented, what was actually
verified, and what remains dependent on an external event. Do not infer project state
from who acknowledged, requested, or authorized a step in chat; remove such attribution
from completion claims unless it is itself applicable evidence. Keep the instructor PDF
authoritative and never turn a proposal or generic test into selected-target acceptance.
