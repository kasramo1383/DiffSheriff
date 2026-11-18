# Strix implementation handoff

Use this as the single live handoff for Strix or another coding agent. The [roadmap](roadmap.md) owns requirement interpretation and acceptance status; this file turns the remaining work into an execution order. The [original assignment](course_assignment.pdf) is authoritative.

```text
Continue DiffSheriff from the current repository state. Read AGENTS.md,
docs/course_assignment.pdf, docs/roadmap.md, docs/target_scenarios.md,
docs/evaluation.md, and artifacts/README.md before changing anything.

Starting point recorded for this handoff: branch main at 3fb8372
(fix: report PNG decode failures and refresh packaged scenarios). Preserve all current
uncommitted work: edits to `artifacts/README.md`, `docs/agent_handoff_prompt.md`,
`docs/roadmap.md`, and `docs/target_scenarios.md`; the new F03 and build-hardening
checkpoints; and the partial `artifacts/evaluation/target1/correct/` run. Inspect Git
state before acting and preserve unrelated changes and existing evidence.

The interrupted Strix run `project_d0e5` used the unpinned model
`openrouter/deepseek/deepseek-v4.1-flash`. Its state file still says `running`, but no
Strix process remains; treat it as orphaned and do not resume it. The operator's WSL
Strix config is now pinned to `openrouter/deepseek/deepseek-v4.1-flash-1017`. Confirm
the first request in a fresh Strix log names that exact model before proceeding. The
retained target1/correct DiffSheriff report returned exit 40 (INCONCLUSIVE); diagnose
its unstable baseline reproducer before counting or rerunning that comparison.

Network route already tested by the operator on 2026-11-17: Windows has a listener on
port 10808; WSL gateway `172.22.224.1` can connect to it. A direct request to
`https://auth.docker.io/token?service=registry.docker.io` returned HTTP 403; the same
request through `http://172.22.224.1:10808` returned HTTP 200. Do not repeat proxy
discovery. In WSL, derive the current gateway (it may change after restart), then set
the process-scoped proxy before Strix/provider requests and dependency/image fetches:

```bash
gateway="$(ip -4 route show default | awk '{print $3; exit}')"
proxy="http://${gateway}:10808"
export HTTP_PROXY="$proxy" HTTPS_PROXY="$proxy" ALL_PROXY="$proxy"
export http_proxy="$proxy" https_proxy="$proxy" all_proxy="$proxy"
export NO_PROXY="localhost,127.0.0.1,::1" no_proxy="localhost,127.0.0.1,::1"
```

For Docker builds, also pass `--build-arg HTTP_PROXY="$proxy" --build-arg
HTTPS_PROXY="$proxy"` as shown in [usage.md](usage.md#retrying-docker-hub-access-from-wsl).
Do not persist these settings or include credentials in evidence. If an actual request
still fails, retain its exact command and error and continue independent local work;
do not turn proxy discovery into a prerequisite again.

Work in the following order. For each item, inspect, implement the smallest needed
change, run its acceptance checks yourself in the available Linux/WSL environment,
inspect the results, retain durable evidence, and update the owning roadmap row before
continuing. Do not stop after presenting commands for the user to run. Use the verified
proxy setup above for network-dependent requests. If a real environment blocker remains
after using that setup, record the exact command/error and continue independent work.
Never claim verification from prepared or unexecuted commands. Ask the user only for
information or external decisions that cannot be established from the repository or
available environment, such as instructor approval; continue technical work meanwhile.

1. F03 — Review the selected inputs and expected results. Compare the files in both
   target evaluation directories with their documented contracts in
   docs/target_scenarios.md. Check validity labels, expected exit/output behavior,
   representative valid/boundary/invalid coverage, and equivalent inputs/settings
   across versions and modes. Correct only demonstrably stale or unsupported claims;
   unknown minimized bytes must remain inconclusive unless independently justified.
   Important: the `65537 -> exit 2` test currently exercises only `reference.py`; it
   does not prove the target driver rejects that input. Resolve the roadmap's open
   invalid-interface question against the actual target interface and assignment. Add
   only the smallest genuine invalid case if needed and if its expected result is
   independently supported; otherwise document why the selected compressor contract
   has no invalid payload within its declared scope and how the assignment's invalid
   input category is satisfied. Do not treat a reference-only test as target coverage
   or waive a required category merely to avoid adding one case. The asset suite has
   already passed (`python -m pytest -q tests/test_target_assets.py`: 11 passed), and
   all six manifests loaded: target1 has 10 cases per variant with 0 invalid; target2
   has 4 cases per variant with 3 invalid. These results are recorded in the roadmap;
   do not repeat unchanged checks. Run only a targeted native/interface check needed to
   settle the F03 question. Do not add corpus-size or exhaustive-format requirements.

2. F04/F05 — Confirm source builds and release hardening on the actual selected
   versions. Use the delivered source bundles and the environment in docs/evaluation.md.
   Record compiler/toolchain, build commands, dependencies/runtime, source refs/hashes,
   and observed NX/PIE/RELRO/canary states for release binaries. Make a build or
   packaging change only if a required version cannot be built/replayed or the four
   refs/bundles/configs disagree. Run the corresponding ordinary and sanitized builds;
   retain inspection output and verify configured hardening downgrade reporting. Do
   not require every mitigation to be enabled.

3. F09 — Run the six real-target comparisons exactly as documented in
   docs/evaluation.md: correct/incomplete/regression for target1 and target2. Use
   equivalent inputs and settings within each target. Preserve separate run identities,
   reports, console logs, source/build identities, original and minimized inputs,
   correlation evidence, termination details, and three replays. Compare actual exit
   codes to 0/10/20; never force outcomes. Investigate 30/40 from their report evidence.
   Inspect all six JSON reports and verify the assignment's distinctions and evidence.
   Retain the actual matrix under artifacts/evaluation/targetN/VARIANT/. Do not call a
   native smoke or generic test suite a full matrix.

4. F06 — During F09, verify automatic reduction on actual findings. Keep the original
   and minimized input and at least three replay results. If an input cannot shrink,
   report the actual stopping reason; do not claim reduction. The generic minimizer
   itself is already verified, so add no minimizer features without a concrete failure.

5. F07 — After correct-patch matrix runs have generated current baseline cases, review
   each case against its bytes and the independently established contract. Run each
   correct config again so the generated cases are loaded. Check that the original
   baseline problem reproduces and is absent on the correct patch, and that functional
   cases remain eligible for regression checks. Keep unknown expectations inconclusive.
   Retain the later-run reports and regression inputs/manifests. Do not revive the
   retired PNG legacy cases as current evidence.

6. F10/F12 — Verify the existing CI and standalone delivery using delivered bundles,
   configs, fixtures, and declared prerequisites in a fresh checkout/location. Make
   only the setup changes needed to run the existing workflow. Verify a correct-patch
   gate passes and incomplete/regression results fail with their actual codes; retain
   workflow output and JSON. Build/install, run a correct comparison, and replay a
   representative finding without relying on ignored local state or chat history. No
   hosted provider is mandatory, and no second CI system is wanted.

Constraints:
- Treat docs/roadmap.md as the sole status and requirement-gap list. Update it as work
  is completed; do not create another checklist or parallel handoff.
- F01/F02 are implemented for the selected documented contracts; F05 PNG packaging,
  F06 generic reduction, F08 generic correlation, F10 source preparation, and F11
  generic exit/verification work already have checkpoint evidence. Recheck them only
  where a selected-target result exposes a real defect.
- The assignment does not require exhaustive library validation, universal package
  locking, all protections enabled, branch tracing, a general-purpose decoder,
  arbitrary-input expectations, hosted CI, or rehearsal packaging. Do not add these
  as completion criteria. Preserve the distinction between instructor approval and
  technical evidence; never fabricate approval, participation, or defenses.
- Keep provenance/licenses intact. Do not relabel old runs after source changes.
  Keep each evidence bundle self-describing and tied to its exact source/runtime.
- For changed code, run existing focused tests and relevant final verification yourself.
  Do not add tests or repeat accepted unchanged suites without need.
- Review the complete diff and repository status. Remove only temporary material
  created by this task. Follow AGENTS.md for staging/commit behavior and report exact
  completed fix IDs, commands/results, retained evidence, limitations, and the first
  unfinished action.
```
