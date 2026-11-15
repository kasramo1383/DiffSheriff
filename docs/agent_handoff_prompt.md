# Agent handoff prompt

Use this prompt when another coding agent takes over the repository. Mutable status and
acceptance criteria belong in [`roadmap.md`](roadmap.md); target facts belong in
[`target_scenarios.md`](target_scenarios.md). Do not copy those facts into this file.

```text
Finish every repository-implementable requirement of the DiffSheriff assignment.

Read AGENTS.md, docs/course_assignment.pdf, docs/roadmap.md,
docs/target_scenarios.md, and the records linked by the current unfinished roadmap
stage before editing. The PDF is the requirements authority. Source, tests, hashes,
run artifacts, and CI results are the verification authority.

There is no team/instructor target-selection loop. Determine the target pair and
bounded test scope from the PDF, primary upstream evidence, and isolated local
feasibility tests. Record the decision honestly as a project selection, never as
instructor approval. Then continue through every remaining roadmap stage: package all
eight scenario versions, freeze independent corpora and expectations, run and repair
both real-target matrices, complete final local and available hosted verification,
perform the clean-room delivery audit, and prepare blind-evaluation and defense-study
materials. Do not stop after planning, feasibility analysis, one target, or one
successful scenario.

Work in coherent verified checkpoints and update the owning record after each. Preserve
existing user changes and retained evidence. Keep the project flat and understandable;
do not add target-specific verdict logic, unnecessary frameworks/services, issue boards,
sprints, or agent-activity records. Execute only selected historical C/C++ targets in
an isolated, resource-limited local Linux/Docker lab. Never contact deployed systems,
create exploit tooling, fabricate evidence, or turn a timeout/nonzero exit into a
security finding.

Run focused checks after each change and the full relevant verification before final
handoff. Inspect actual JSON, readable reports, exit codes, replays, minimized inputs,
hashes, and manifests. Preserve failures and skips honestly. Do not commit, push, pull,
or discard work. Do not edit README for personal notes.

Finish only when the PDF-to-evidence audit finds no locally actionable gap. Actual
student defenses, an independent human blind exercise, instructor approval, and an
instructor-only unseen-patch event are external facts: prepare the repository materials
but never claim those events occurred. Report changed files, exact commands/results,
final target matrices, clean-room outcome, genuine external remainder, and final Git
status.
```

For a Strix run, use the more detailed execution contract in
[`strix_completion_instructions.md`](strix_completion_instructions.md).
For the large Antigravity preparation chunk that completes Roadmap Stages 3–5 before
the final Strix matrices, send [`antigravity_preparation_instructions.md`](antigravity_preparation_instructions.md)
as the complete prompt.
