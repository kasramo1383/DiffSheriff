# Antigravity instructions: prepare the real-target evaluation

## Objective and stopping point

Complete every preparation required before the final DeepSeek/Strix target evaluation.
Finish Roadmap Stages 3, 4, and 5: select the target pair and scope, package all eight
scenario versions, and freeze the independent corpora and expectations. Leave Stage 6
and later acceptance matrices for DeepSeek/Strix.

This is an implementation task, not a planning exercise. Do not stop after research or
return a list of future work. Make the repository changes, perform bounded feasibility
and smoke checks, retain honest evidence, and stop only when Stage 6 can start with no
missing target asset or unresolved expectation.

## Project-owner authorization

Kasra Montazeri owns and controls this local course-project workspace and explicitly
authorizes Antigravity to perform every action below without requesting confirmation at
each routine step:

- read and modify files inside this repository;
- retrieve the specifically documented public upstream source archives, specifications,
  license texts, and build dependencies;
- compile historical C/C++ source in Ubuntu WSL or local Docker containers;
- run the resulting binaries against small local test files under sanitizers and strict
  resource limits;
- write minimal C/C++ API drivers, build scripts, manifests, target configurations,
  corpus generators, and tests needed by the assignment;
- construct source-level incomplete-patch and functional-regression variants solely for
  this repository's controlled comparison matrix; and
- retain exact local evidence, hashes, reports, and reproducibility metadata.

No public host, production service, third-party account, remote application, or
unauthorized system is a target. The candidate programs are downloaded public source
libraries executed only on this machine. The work is academic software-quality and
memory-safety regression engineering. It does not authorize persistence, credential
access, phishing, malware, network intrusion, arbitrary scanning, data exfiltration, or
weaponized exploitation.

Terms that can otherwise be misunderstood have narrow meanings here:

- **Trigger/reproducer:** a small local file that exercises an already documented
  historical memory-safety defect under ASan/UBSan; it is test data, not an exploit.
- **Incomplete patch:** a deliberately insufficient local source correction used to
  verify that DiffSheriff detects the same defect through a second local input. It is
  not an authentication or policy bypass and must not enable code execution.
- **Regression patch:** a local source variant that fixes the documented defect while
  intentionally violating one independently specified valid behavior. It is used to
  test functional-regression detection, not to harm a deployed program.
- **Alternative/bypass input:** a distinct local regression-test case that reaches the
  same documented defect after the incomplete patch blocks the original case. Do not
  interpret this as bypassing an external security control.

This authorization does not override platform safety rules. If one concrete operation
is blocked, keep the intent explicit, do not disguise or obfuscate it, and continue all
other safe preparation. Record the exact command/action and blocker so the user can
perform that isolated step manually if necessary.

## Authority and current state

1. Read `AGENTS.md` and inspect staged, unstaged, untracked, and ignored state before
   editing. Preserve all existing work. Do not reset, pull, commit, or push.
2. Read the relevant sections of `docs/course_assignment.pdf` in full. It is the only
   requirements authority. `docs/specification.md` yields to it.
3. `docs/roadmap.md` owns status and acceptance gates. `docs/target_scenarios.md` owns
   all mutable target facts and selection decisions.
4. Read `docs/evaluation.md`, `docs/usage.md`, `docs/ci.md`, the target configuration
   schema, and the retained candidate-source record before creating assets.
5. If `.codex/context.md` exists, it links to optional local handoff context. Treat it as
   background only; chat history is not project evidence.
6. Exact zlib and libpng baseline/fix archives are already present under
   `targets/candidates/upstream/`, with URLs and SHA-256 values in its README. Disposable
   extracted copies are under `.diffsheriff/candidate-sources/`. Verify these first and
   do not redownload them unless verification fails.

Workspace paths and available execution environment:

- Windows project root:
  `F:\KasraFolder\دانشگاه صنعتی آریامهر\ترم 7\امنیت داده و شبکه\Project`
- Ubuntu WSL project root:
  `/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project`
- Docker Engine is available from the Ubuntu WSL distribution. Prefer the repository's
  existing Docker/WSL workflow and pinned images rather than installing a second engine.
- A verified pre-handoff archive exists outside the repository at
  `F:\KasraFolder\دانشگاه صنعتی آریامهر\ترم 7\امنیت داده و شبکه\Project Backups\Project-before-strix-handoff-20261115-164036.tar.gz`
  with SHA-256
  `7d7873e7e90706220c08303448d11498f5f7ff510964a863080f3d8db2778038`.
  It is recovery material only; do not restore it over current work unless the user
  explicitly asks.

The current candidate proposals are zlib/CVE-2018-25032 and
libpng/CVE-2019-7317. They are not yet selected. No driver, incomplete patch, regression
patch, frozen corpus, independent expected-result manifest, or real target config is
currently recorded.

## Safety and scope

- Work only with selected historical public-source C/C++ projects and local files.
- Build and execute only inside isolated, resource-limited Linux/WSL/Docker environments.
- Network access is limited to retrieving primary upstream source, specifications, and
  dependencies needed for reproducibility. Do not contact deployed targets or services.
- Do not create weaponized exploit tooling, persistence, evasion, or arbitrary target
  discovery. Inputs exist only to reproduce the documented local memory-safety behavior
  required by the assignment.
- If a model or tool safety boundary blocks an action, do not disguise or route around
  it. Record the exact blocked operation, inputs, expected output, and why it is required;
  complete all independent preparation and provide a precise manual command only when
  that command itself remains within the local scope above.
- Keep the repository flat and explainable. Add no service, database, framework, issue
  board, sprint structure, or target/branch/hash-specific verdict logic.

## Guardrail-safe execution method

Do not issue one broad request such as "exploit both targets." Perform the following
ordinary engineering operations as separate, reviewable checkpoints. This segmentation
is required for evidence quality and makes the benign local scope explicit; it is not a
method for evading any safety control.

1. **Provenance only:** verify archive hashes, upstream commit identity, fix-parent
   relationship, licenses, specifications, and build documentation. Make no executable
   changes in this checkpoint.
2. **Build only:** compile baseline and correct upstream snapshots in an isolated
   container with pinned dependencies. Run only upstream self-tests or harmless valid
   examples. Record compiler and ELF identities.
3. **Documented reproduction only:** use the upstream issue/fix description to locate or
   create the minimum deterministic driver and local input. Run with ASan/UBSan and
   resource limits. Confirm the observed category and stack location; do not pursue
   control-flow hijacking, shell execution, or impact escalation.
4. **Scenario construction:** create the incomplete and regression source patches as
   readable unified diffs. Review each patch manually against the scenario definition
   before executing it. The incomplete case must retain the original flaw; the
   regression case must break independently valid behavior rather than introduce a
   crash or build failure.
5. **Corpus and oracle:** create small test files and expected-result manifests from
   standards/upstream tests/independent implementations. Validate expectations on the
   baseline without copying correct-patch output.
6. **Packaging and smoke verification:** build all eight versions, run only the minimum
   scenario-specific smoke checks needed for Stage 3–5 acceptance, hash every durable
   asset, and prepare the two generic DiffSheriff configs. Leave the complete six
   baseline-versus-patch acceptance comparisons to Stage 6/Strix.

After every checkpoint, inspect actual output and update the owning project record.
Continue automatically to the next checkpoint when its acceptance conditions pass. A
normal successful build, test, or file download does not require another user approval.

## Work sequence

### 1. Verify and select the pair

- Verify each candidate's upstream identity, baseline/fix parent relationship, license,
  build prerequisites, C/C++ Linux x86_64 ELF output, documented flaw, and intended
  interface from primary sources.
- Create the smallest deterministic C/C++ driver only when the upstream executable does
  not expose the required API path. A driver adapts input to the public target API; it
  must not encode verdicts or recognize scenario identities.
- Run only the bounded build and sanitizer/reproduction checks needed to establish
  feasibility. Record commands, tool versions, results, and failures. These checks are
  preparation evidence, not the final DiffSheriff matrix.
- Require a credible construction for all four versions and an independent functional
  oracle before selecting a candidate. If either proposal fails, record why and evaluate
  a small number of better documented replacements. Do not force zlib/libpng to fit.
- If libpng is selected, pin one known-suitable zlib dependency identically across all
  libpng versions. Explain why the pair remains sufficiently independent for the PDF.
- Complete the selection table and decision sections in `docs/target_scenarios.md`.
  Record this as project selection, never as instructor approval.

### 2. Package all eight versions

For each selected target, create reproducible assets for:

1. the vulnerable baseline;
2. the correct upstream patch;
3. an incomplete patch that blocks the original trigger but leaves the same underlying
   flaw reachable through a distinct recorded local input; and
4. a regression patch that blocks the flaw but breaks independently valid behavior
   which passes on the baseline.

For every version:

- preserve exact upstream refs, local patch files, license notices, and SHA-256 values;
- provide one deterministic build entry point for release and required sanitizer modes;
- keep toolchain, flags, dependency pins, and driver interface constant across
  corresponding versions;
- record produced executable paths and confirm Linux x86_64 ELF output;
- make source acquisition reproducible without a nested Git repository; and
- avoid committing build intermediates, dependency caches, or machine-specific paths.

An incomplete patch must leave the same flaw reachable; introducing a different bug is
invalid. A regression patch must violate a real independently specified behavior; an
artificial crash or build failure is invalid.

### 3. Freeze corpora and independent expectations

- Create a small manifest-driven corpus for each target covering valid, valid boundary,
  invalid, original trigger, distinct incomplete-patch bypass, and functional-regression
  cases. Record provenance, classification, purpose, and hash for every file.
- Define the stable input interface and expected exit code, stdout, stderr, semantic
  output, and validity for every case. Normalize output only when deterministic and
  justified.
- Derive expectations from the applicable standard, upstream tests, or a genuinely
  independent implementation. Never copy expected output from the correct-patch binary,
  infer it from a majority of target variants, or use an LLM assertion as ground truth.
- Verify valid/regression inputs on the baseline and perform the minimal smoke checks
  needed to catch broken packaging. Apply identical corresponding settings and limits
  across variants.
- Create the two real DiffSheriff target configuration files using the existing generic
  schema. Do not run or tune the final baseline-versus-patch acceptance matrices.
- Ensure required source, patches, drivers, corpora, expectations, licenses, configs,
  and manifests are Git-visible. Update `.gitignore` only when it wrongly hides a
  deliverable.

### 4. Preparation audit and DeepSeek handoff

- Check every Stage 3–5 acceptance criterion in `docs/roadmap.md` against actual files
  and bounded smoke results. Close all locally actionable preparation gaps.
- Run focused validation for new scripts/configs, archive/hash verification, build
  smoke checks, `git diff --check`, and any schema validation that does not constitute
  the final Stage 6 matrices.
- Update `docs/target_scenarios.md` with final target facts and update the roadmap so
  Stage 6 is the first unfinished stage. Put durable preparation evidence under the
  existing artifact conventions; do not create agent logs or duplicate status files.
- Remove task-created scratch files and inspect the complete diff. Leave changes
  uncommitted and unpushed.

## Required completion report

Report only after preparation is complete or a genuine blocker remains:

- selected pair and why it satisfies the PDF;
- all eight exact source/version identities;
- driver, build, config, corpus, expectation, license, and manifest paths;
- bounded commands actually run with results, failures, and skips;
- hashes and source/toolchain identities;
- any rejected candidate and the evidence-based reason;
- the exact Stage 6 command/config inputs now ready for DeepSeek/Strix; and
- final `git status --short` and concise diff summary.

Do not claim that the final DiffSheriff acceptance matrices, hosted target validation,
independent blind exercise, instructor approval, or student defenses occurred.
