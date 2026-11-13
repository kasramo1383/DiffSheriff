# Agent handoff prompt

Copy this prompt when assigning the next project step to an AI coding agent.

```text
You are helping complete the DiffSheriff course project. Read these project files
before acting:

1. docs/course_assignment.pdf. It is the authoritative requirement source.
2. docs/specification.md. It is an English digest and yields to the PDF.
3. docs/roadmap.md. It records implementation status and remaining work.
4. docs/target_scenarios.md. It is the sole record for target facts and approval.
5. AGENTS.md and artifacts/README.md. They define repository and evidence handling.

Current scope

Use the roadmap's workflow and pipeline section to choose the next code change.
The current checkpoint names the next task. See the target record for work that
depends on instructor approval.

Work one bounded stage at a time. Begin with the next action in the roadmap checkpoint.
For the next step only, inspect the relevant source, make a small focused change or
prepare the requested evidence, and verify that step. Do not start a later step in the
same assignment. Leave the repository in a clear, reviewable state and report what
changed, commands run, exact results, skips, and unresolved dependencies. Then stop
for Kasra's review. Do not mark the step accepted on the user's behalf. Another agent
must be able to continue from the roadmap, target record, and checked-in files without
chat history.

Targets, approval, and test inputs

Do not invent instructor approval, source provenance, licenses, commit references,
functional ground truth, or validation results. Do not contact the instructor or
third parties. Public-source research may produce clearly labeled candidate targets
and citations for the team to review, but candidates remain unapproved until the team
records instructor confirmation in docs/target_scenarios.md. If approval or assets are
missing, document the specific dependency and work only on independent tasks that do
not assume it.

Keep security work defensive and local. Use only explicitly approved source snapshots
and safe lab inputs. Do not create exploit tooling, weaponized payloads, or tests for
unapproved systems. The assignment's incomplete-patch case requires a distinct,
authorized local test input that still reaches the same underlying flaw. Handle that
case only within the approved target corpus and document the input's provenance and
expected behavior. If a safety system blocks a narrowly defensive operation, stop that
operation, report the exact block, and propose a safe substitute without obscuring or
routing around the block.

Verification and evidence

Read the relevant checkpoint instructions before repeating checks. Do not claim tests
were run unless they were run. Use WSL when Linux containers are needed if Windows
Docker integration is unavailable. Retain durable reports, source snapshots, inputs,
and packages under artifacts/ when they are useful for handoff. Keep temporary output
and dependency caches out of Git. Check recorded hashes and ensure generated files are
visible to Git before reporting an artifact as retained. Never combine evidence from
different source revisions or runtime images.

Project constraints

Keep DiffSheriff understandable and flat. Avoid frameworks, services, databases,
unnecessary abstractions, target-name or patch-specific verdict logic, and unrelated
cleanup. Follow the existing Python style and test conventions. Preserve user changes.
Do not commit or push unless Kasra explicitly requests it. Do not modify durable
global instructions. Update the relevant project record after the user accepts a
completed stage.

Start by stating the single roadmap step you are taking and its acceptance criteria.
Then do only that step.
```

The roadmap remains the source for current status and stage order. This prompt records
how an agent should pick up and complete one stage.
