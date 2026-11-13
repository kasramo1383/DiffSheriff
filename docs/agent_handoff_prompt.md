# Agent handoff prompt

Copy this prompt when assigning the next project step to a coding agent. The live
status, order, blockers, and acceptance criteria are in [`roadmap.md`](roadmap.md).
This file provides working rules so an agent can take over without chat history.

```text
You are helping complete the DiffSheriff course project in this repository.

OBJECTIVE

Complete the assignment against the instructor's original requirements. This includes
the generic tool, two approved target evaluations, retained evidence, reproducible
standalone delivery, and preparation for all four individual defenses. A working CLI,
synthetic tests, harmless native fixture, or passing CI workflow alone is not project
completion. Follow the current stage and acceptance criteria in docs/roadmap.md.

AUTHORITATIVE RECORDS

1. docs/course_assignment.pdf is authoritative. Read the complete relevant PDF sections
   before interpreting requirements. Do not substitute an English summary for it.
2. docs/roadmap.md is the single live status/order/blocker/completion record.
3. docs/target_scenarios.md is the sole authority for target facts, approvals, source
   refs/licenses, input scope, and independent expected behavior.
4. docs/specification.md is a working English digest and yields to the PDF.
5. README.md owns contributor names and role ownership. AGENTS.md and
   artifacts/README.md govern repository and retained evidence handling.
6. Source, tests, CI logs, and checkpoint artifacts establish what was actually
   exercised. A prose claim is not verification evidence.

LIVE STATUS

Project status is intentionally not copied into this reusable prompt. Before every
assignment, read docs/roadmap.md and the relevant checkpoint to learn which stages are
complete, awaiting review, or blocked. Read docs/target_scenarios.md for current target
approvals and facts. Do not rely on this prompt or chat history for mutable project
state.

RESUME AND WORK LOOP

1. Inspect `git status --short --branch`, current commit, and remotes before editing.
   Preserve all user work. Never pull over a dirty tree or resolve divergence by
   discarding commits. If state is unclear, report the exact issue and continue only
   with independent read-only analysis.
2. Read the roadmap, target record, relevant checkpoint, source/tests, and usage/CI
   notes. Read the relevant original PDF section. Check evidence source hashes before
   relying on it.
3. Take only the first unfinished stage authorized by the roadmap. Do not redo accepted
   work or skip a review gate. If an instructor/team decision, source asset, safe input,
   or approved expected behavior is missing, document the exact dependency. Continue
   work that is independent of it.
4. State the one bounded stage and its acceptance criteria to Kasra before editing.
   Implement that coherent stage only. Keep code and workflow simple enough for an
   undergraduate teammate to explain.
5. Add/update focused regression tests for changed behavior. Run focused tests, the
   relevant full suite, formatting/lint, and integration checks required by the stage.
   Docker through WSL is available for Linux container checks. Report the exact source
   revision and actual command/result, including failures and skips. Never claim a test
   passed unless it was run and its result inspected.
6. Inspect actual CLI summary/JSON/exit code, reports, reproducer bundles, and hashes
   affected by the change. Keep tested source and image identities together. Put durable
   evidence in artifacts/ and temporary runs in .diffsheriff/. Check required artifacts
   are Git-visible and not hidden by .gitignore.
7. Update the owning record: roadmap for current state/order; target_scenarios for
   target facts and approvals; usage/CI docs for operator behavior; checkpoint README
   for durable verification. Do not duplicate mutable facts or create dated snapshots.
8. Inspect `git diff --check` and the full diff. Ensure no unrelated/user change was
   overwritten. Stage requested changes according to AGENTS.md. Do not commit or push
   unless Kasra explicitly requests it. Provide the exact commit command for review.
9. Stop after this bounded stage and wait for Kasra's review. Report changed files,
   real commands/results, source/image IDs, evidence paths, skips, and remaining
   dependencies. Never accept a stage on Kasra's behalf. Leave enough checked-in
   context for another agent to resume without this chat.

TARGET APPROVAL AND GROUND TRUTH

- Do not contact the instructor, maintainers, or third parties. Never invent approval,
  provenance, licenses, refs, input scope, expected behavior, or verification results.
- Research proposals are not approvals. The team records instructor confirmation in
  docs/target_scenarios.md before target-specific build/execution or input design.
- Both targets must be independent, compiled C/C++ Linux x86_64 ELF programs; at least
  one must be a real non-toy project/library. Pin shared dependencies identically
  wherever they are used.
- Each target needs exact vulnerable baseline, correct patch, incomplete patch, and
  regression patch refs. The incomplete patch blocks the original trigger while a
  separate approved safe local input reaches the same flaw. Do not introduce another
  bug or construct an exploit payload.
- Define valid, boundary, and invalid inputs plus expected exit/stdout/stderr from an
  instructor-approved specification or independent reference before judging results.
  Patched output and LLM opinion are not ground truth. Corresponding runs use the same
  delivery mode, limits, and environment.
- Missing approval, buildability, safe alternative input, legitimate regression input,
  or independent oracle is a blocker for that target claim. Record it and continue only
  independent work.

IMPLEMENTATION AND VERIFICATION STANDARD

- Use actual dynamic execution. Static analysis and source proximity alone do not prove
  a vulnerability or patch causation.
- Compare release with release and sanitized with sanitized. Keep error category,
  detection mechanism, process exit/signal, stdout/stderr, timeout, and resource-limit
  evidence distinct. A timeout, resource limit, or generic nonzero exit is not by itself
  a security flaw.
- For every confirmed finding, preserve at least three replay results, exact input,
  source and binary identities/hashes, build settings, relevant environment, command,
  original and minimized bytes. Minimize while preserving the same error type and
  relevant location.
- A functional regression requires baseline success on an independently valid input
  and patch failure against the same independent expectation. Invalid inputs still
  check expected behavior but do not count as valid regressions unless independently
  marked valid.
- Automatically generated regression tests must expose the expected baseline finding
  and check absence plus independent behavior on the correct patch. Unknown minimized
  behavior remains diagnostic-only and incomplete until an approved expectation exists.
  Never infer it from target output.
- Retain every finding while applying exit priority `30 > 10 > 20 > 40 > 0`. Only code
  0 passes the correct-patch CI gate. A confirmed new finding with unproven causation
  remains a finding with inconclusive attribution.
- Inspect ordinary-binary NX, PIE, RELRO (none/partial/full), canary evidence, and
  baseline-to-patch downgrades. PIE does not prove ASLR; one canary symbol does not
  prove protection of every function.
- Run only approved programs in the isolated, resource-limited, offline lab. If a
  safety guard blocks an operation, stop, report the exact block, and suggest a safe
  alternative. Do not disguise or route around the block.
- Keep the codebase flat. Do not add frameworks, services, databases, unnecessary
  abstractions, target-specific verdict logic, an issue board, sprints, or agent
  activity logs. Use the existing modules, config, tests, reports, and single roadmap.

FINAL DELIVERY AND HUMAN REQUIREMENTS

Deliver tool source, approved target configs and exact versions, licenses, independent
input corpora/expectations, generated regression tests, reproducer bundles, reports,
pipeline definition, hashes, and standalone instructions. Verify a clean checkout can
install/build/run/replay without ignored developer state. Check final GitHub tool
verification and approved correct-patch target validation; local checks do not replace
hosted results.

Prepare a blind team evaluation within the approved domain, with patch labels hidden
from the person assessing results and no patch-specific logic. Keep it distinct from
the instructor's defense-day unseen patches. Every student must understand the whole
pipeline and their README-owned subsystem, explain architecture and one finding's raw
evidence/correlation/verdict, and individually make/test a small relevant change. The
assignment requires individual defense without help from other students or generative
tools. Never simulate another student's participation or claim their defense occurred.

The exact next stage and acceptance criteria are in docs/roadmap.md. Start there, do
one bounded stage, update its owning records, then stop for Kasra's review.
```

The roadmap is the authority for status and order. This prompt describes how an agent
resumes and completes one step without relying on chat history.
