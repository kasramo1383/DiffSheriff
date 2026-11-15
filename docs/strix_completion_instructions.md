# Strix instructions: finish the remaining DiffSheriff project

## Mission

Finish every repository-implementable requirement in the DiffSheriff course project.
Do the work, run the real local target evaluations, repair failures, retain honest
evidence, and leave the repository ready for submission and immediate handoff. Do not
stop after analysis, a plan, target selection, one target, or one successful scenario.

The Persian assignment PDF is the requirements authority. The repository currently has
a substantially implemented and verified generic pipeline; the main unfinished work is
the complete two-target workflow. Read the live records before acting and correct stale
claims as evidence changes.

## Authority and boundaries

1. `docs/course_assignment.pdf` is authoritative. `docs/specification.md` is only a
   working digest and yields to the PDF.
2. `docs/roadmap.md` owns live status, stage order, and completion gates.
3. `docs/target_scenarios.md` owns target identities, source refs, licenses, drivers,
   input scope, independent expectations, selection rationale, and scenario facts.
4. Source, tests, run artifacts, hashes, and CI results establish verification. Prose
   does not turn an unexecuted claim into evidence.
   If `.codex/context.md` exists, it contains an optional local link to the Codex handoff
   conversation; use it only as background, never as requirements or verification.
5. There is no team/instructor selection loop. The project owner authorizes you to
   determine the pair and bounded test scope from the PDF, primary upstream sources,
   and local feasibility results. Never call this instructor approval. If the PDF
   requires such approval, record that evidence as unavailable and continue the
   requested implementation.
6. Work only on this repository and public upstream source needed for the selected
   historical C/C++ targets. Execute targets only in isolated, resource-limited local
   Linux/Docker environments. Do not contact deployed systems, create exploit tooling,
   add persistence, or expand the recorded corpus beyond what the assignment needs.
7. Preserve existing user changes. Do not reset, discard, pull, commit, push, open
   issues, or create CI/agile process records. The user will review version-control
   actions separately.

## Required work sequence

Work through the following checkpoints in order. Verify each checkpoint before using it
as a foundation for the next, update the owning records, then continue automatically.
Stop only for a genuine safety or technical blocker after trying reasonable in-scope
alternatives and documenting exact evidence.

### 1. Establish the real starting state

- Inspect `git status --short --branch`, current HEAD, staged and unstaged diffs, and
  repository instructions. Do not overwrite the staged roadmap/verification updates.
- Read the full relevant PDF sections, roadmap, target record, evaluation procedure,
  usage/CI docs, generic source/tests, and retained checkpoint manifests.
- Verify retained hashes before relying on checkpoint evidence. Correct stale or
  contradictory status text, but do not rerun accepted generic checks without a reason.

### 2. Select two feasible targets and freeze scope

- Evaluate the existing zlib/CVE-2018-25032 and libpng/CVE-2019-7317 proposals first.
  Use primary upstream commits, issues, specifications, licenses, and bounded local
  build/reproduction evidence.
- Exact baseline/fix archives are already downloaded under
  `targets/candidates/upstream/`, with hashes and source URLs in its README. Disposable
  extracted copies are under `.diffsheriff/candidate-sources/`. Verify the hashes before
  use; do not redownload these four snapshots unless verification fails.
- A target is acceptable only if it is C/C++, builds to Linux x86_64 ELF, has exact
  vulnerable and correct-patch refs, a deterministic minimal interface, an independent
  functional oracle, safe local inputs, and feasible baseline/correct/incomplete/
  regression variants. At least one target must be a real non-toy project/library and
  the pair must be defensibly independent.
- For libpng, pin one fixed zlib dependency across every libpng variant. If the pair's
  dependency relationship or any required scenario is not defensible, replace the weak
  candidate with a small number of better documented alternatives. Do not keep a target
  merely because earlier notes proposed it.
- Record exact evidence, decision, scope, exclusions, and rejected-candidate reasons in
  `docs/target_scenarios.md`. Complete the selection table. Do not leave mutable target
  facts duplicated in the roadmap.

### 3. Build and package all eight scenario versions

For each selected target, create reproducible source/build assets for:

1. vulnerable baseline;
2. correct upstream patch;
3. incomplete patch that blocks the original trigger while a distinct in-scope input
   still reaches the same underlying flaw; and
4. regression patch that blocks the target flaw but breaks independently valid behavior
   which succeeds on the baseline.

Use one simple driver/config contract per target and the same pinned toolchain and
dependencies across corresponding versions. Preserve upstream license notices, exact
refs or patch files, source/archive hashes, driver source, build commands, produced ELF
paths/hashes, and ordinary-binary NX/PIE/RELRO/canary observations. Avoid nested Git
repositories, target-specific verdict logic, and unnecessary frameworks or services.

### 4. Freeze independent corpora and expectations

- Create small, reviewable valid, boundary, invalid, original-trigger, bypass, and
  regression inputs for each target. Record provenance, validity, and purpose.
- Define expected exit/stdout/stderr and semantic output from a standard, upstream test,
  or genuinely independent implementation. Never copy expected values from the patched
  target or treat an LLM judgment as ground truth.
- Apply identical corresponding inputs, delivery modes, limits, and environment to
  baseline and patch. Hash and manifest all required files, and ensure `.gitignore` does
  not hide deliverables.

### 5. Run and repair the complete real-target matrices

- Run DiffSheriff for each target baseline against its correct, incomplete, and
  regression variants in release and sanitizer modes as required by the PDF.
- Preserve actual commands, environment/tool/image/source/binary identities, stdout,
  stderr, exit/signal, timeout/resource outcomes, JSON, readable reports, correlations,
  and failed attempts. Compare release only with release and sanitizer only with
  sanitizer.
- For every confirmed finding, retain at least three replays, original and minimized
  bytes, stability, category versus detection mechanism, relevant stack/path/function
  evidence, and honest patch attribution. A timeout or nonzero exit alone is not a
  security finding.
- Verify expected results: correct patch `0`, incomplete patch `10`, regression patch
  `20` unless a higher-priority condition applies, with priority
  `30 > 10 > 20 > 40 > 0`. Never rewrite evidence to force these codes.
- Ensure generated regressions are automatically enrolled and pass their later-run
  contract. If a matrix exposes a generic defect or faulty target asset, implement the
  smallest maintainable correction, add focused coverage, and rerun the affected and
  regression checks until the result is correct and reproducible.

### 6. Complete final verification and delivery

- Run focused tests after each correction, then the relevant full Python suite,
  formatting, lint, package build/install, CLI/replay checks, native container checks,
  all target matrices, exit-code checks, and retained-evidence integrity checks.
- Exercise the existing target CI workflow locally. If authenticated GitHub access is
  already available and the workflow can be dispatched without committing/pushing or
  mutating unrelated state, retain the hosted result. Otherwise record hosted execution
  as the only external action still pending; do not fake it and do not let it block all
  local completion.
- Perform a clean-room run from a fresh temporary checkout/directory using only tracked
  deliverables and declared prerequisites. Verify install, image/build, both correct
  patches, JSON/readable output, replay, generated regressions, and exact artifact
  manifests. Remove task-created scratch data afterward.
- Prepare the blind-evaluation package and complete defense-study material for all four
  named contributors. Do not claim any independent human exercise or defense occurred.

### 7. Final audit and handoff

- Re-read the PDF and map every technical requirement to tracked implementation and
  retained evidence. Close every repository-implementable gap; do not leave TODOs that
  can be completed locally.
- Keep the structure simple enough that the students can accurately explain the whole
  flow. Do not add an issue board, sprint records, agent logs, database, web service, or
  abstraction without a direct requirement.
- Update the roadmap to reflect verified final state and name only truly external
  events still pending. Update target, usage, CI, evaluation, defense, and evidence
  records only where they own the relevant fact. Do not edit README for personal notes.
- Run `git diff --check`, inspect staged and unstaged diffs, list all required untracked
  files, and verify no deliverable is ignored. Leave changes uncommitted and unpushed.

## Completion response

Do not return a research memo or future plan. Return only after completing the work or
reaching a genuine blocker. Report:

- selected targets and all eight exact versions;
- implemented files and retained evidence;
- commands actually run and their outcomes, including failures/skips;
- final matrices and exit codes;
- clean-room result;
- remaining external events, if any; and
- exact `git status --short` plus a concise diff summary.

Never claim unrun testing, unavailable instructor approval, hosted execution, an
independent blind exercise, or student defenses.
