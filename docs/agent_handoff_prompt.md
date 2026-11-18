# DiffSheriff recovery audit handoff

Use this handoff for a read-only review of the current committed project and the
recovery evidence recorded at `1d0910d`. The [roadmap](roadmap.md) owns acceptance
status and remaining work.

## Operator instructions

Paste the full block below into an interactive WSL Ubuntu terminal. It creates a
fresh run directory and supplies the original assignment, requirements digest,
architecture, roadmap, target provenance, CI policy, checkpoint summaries, and report
metadata. An inventory lists the implementation, configuration, and test paths at the
audited commit. The launcher gives Strix a documentation workspace and a writable
report folder. The checkout, source bundles, inputs, and binaries stay outside it.

The launcher uses the existing private Strix configuration, pins DeepSeek Flash 1017,
and supplies an empty MCP configuration. It applies the Windows proxy on port 10808
through the current WSL gateway.

The launcher prints the exact paths at startup. Outputs live under
`~/strix-runs/diffsheriff-audit-*/` in WSL:

- `evidence/audit-output/audit-report.md` is the completed project audit.
- `evidence/audit-output/audit-checkpoint.md` records progress if the run is interrupted.
- `strix_runs/<run-id>/` holds native Strix artifacts such as `run.json`,
  `strix.log`, and any coverage, SARIF, or native final report.

```bash
(
  set -euo pipefail
  project='/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project'
  revision=$(git -C "$project" rev-parse --verify HEAD)
  recovery=1d0910d0f8eb25e3122a1600bddff2c1287d713a
  model=openrouter/deepseek/deepseek-v4.1-flash-1017
  git -C "$project" cat-file -e "${recovery}^{commit}"

  mkdir -p "$HOME/strix-runs"
  run_dir=$(mktemp -d "$HOME/strix-runs/diffsheriff-audit-XXXXXX")
  packet="$run_dir/evidence"
  output="$packet/audit-output"
  mkdir -p "$output"

  copy_doc() {
    local path="$1"
    mkdir -p "$packet/$(dirname "$path")"
    git -C "$project" show "$revision:$path" > "$packet/$path"
  }
  for path in AGENTS.md docs/course_assignment.pdf docs/specification.md \
    docs/architecture.md docs/roadmap.md artifacts/README.md; do
    copy_doc "$path"
  done
  while IFS= read -r path; do
    case "$path" in
      */README.md) copy_doc "$path" ;;
    esac
  done < <(git -C "$project" ls-tree -r --name-only "$revision" -- artifacts/checkpoints)

  git -C "$project" show "$revision:docs/target_scenarios.md" |
    awk '/^## Driver and patch scope/ { exit } { print }' > "$packet/docs/target-provenance.md"
  git -C "$project" show "$revision:docs/ci.md" |
    awk '/^```/ { fence=!fence; next } !fence' > "$packet/docs/ci.md"
  {
    printf 'Project snapshot\n'
    git -C "$project" show -s --format='%H %s' "$revision"
    printf '\nRecovered evidence revision\n'
    git -C "$project" show -s --format='%H %s' "$recovery"
    printf '\nTracked implementation, configuration, and test paths (inventory only)\n'
    git -C "$project" ls-tree -r --name-only "$revision" -- diffsheriff tests .github/workflows evaluation targets
  } > "$packet/revision.txt"
  git -C "$project" show "$recovery:artifacts/evaluation/target1/correct/report.json" |
    python3 -c '
import json
import sys

report = json.load(sys.stdin)
fields = (
    "exit_code", "verdict", "analysis_complete", "total_tests_run",
    "functional_passed", "functional_failed", "security_status", "functional_status",
)
summary = {key: report[key] for key in fields}
summary["runtime_image"] = report["evidence"]["execution_settings"]["image"]
summary["baseline_identity_modes"] = report["evidence"]["baseline_identity_modes"]
print(json.dumps(summary, indent=2))
' > "$packet/target1-correct-summary.json"

  awk '/^<!-- STRIX PROMPT BEGIN -->$/{copy=1;next} /^<!-- STRIX PROMPT END -->$/{exit} copy' \
    < <(tr -d '\r' < "$project/docs/agent_handoff_prompt.md") > "$run_dir/instructions.md"
  test -s "$run_dir/instructions.md"
  printf '[]\n' > "$run_dir/mcp.json"

  gateway=$(ip -4 route show default | awk 'NR == 1 {print $3}')
  : "${gateway:?WSL IPv4 default gateway is missing}"
  proxy="http://$gateway:10808"
  export HTTP_PROXY="$proxy" HTTPS_PROXY="$proxy" ALL_PROXY="$proxy"
  export http_proxy="$proxy" https_proxy="$proxy" all_proxy="$proxy"
  export NO_PROXY='localhost,127.0.0.1,::1' no_proxy='localhost,127.0.0.1,::1'

  printf 'Run directory: %s\nAudit report: %s/audit-report.md\nRequested model: %s\n' \
    "$run_dir" "$output" "$model"
  cd "$run_dir"
  strix_status=0
  STRIX_LLM="$model" strix \
    --config "$HOME/.strix/cli-config.json" \
    --mcp-config "$run_dir/mcp.json" \
    --target "$packet" \
    --instruction-file "$run_dir/instructions.md" \
    --scan-mode quick --scope-mode full --max-budget 5 --max-turns 1000000 || strix_status=$?

  if [[ -s "$output/audit-report.md" ]]; then
    printf 'Saved audit report: %s/audit-report.md\n' "$output"
  else
    printf 'No completed audit report. Review %s and %s/strix_runs/ for partial output.\n' \
      "$output" "$run_dir" >&2
    (( strix_status != 0 )) || strix_status=1
  fi
  exit "$strix_status"
)
```

Check the first `llm_request` entry in the fresh `strix.log` for
`provider=openrouter model=deepseek/deepseek-v4.1-flash-1017`. The million-turn
value is a finite per-agent ceiling. Share the printed run directory after the
session so the report and logs can be read directly.

## Audit prompt

<!-- STRIX PROMPT BEGIN -->
You are reviewing a local packet of DiffSheriff course-project documents and
recorded result metadata. Start with revision.txt, docs/specification.md,
docs/architecture.md, and docs/roadmap.md. Treat docs/course_assignment.pdf as the
authority. If PDF extraction is unavailable, use the digest and record that
limitation. Audit the evidence within the supplied packet. Keep the input files
unchanged and write only inside audit-output/. Do not scan systems or networks,
run project code or builds, generate inputs, reproduce vulnerabilities, or delegate
those activities.

1. Reconcile `revision.txt`, `docs/roadmap.md`, and `artifacts/README.md`. Identify stale
   status statements, contradictory claims, and evidence gaps introduced by the
   interrupted recovery. Files outside the packet are unavailable for this review.
2. Assess F03 against the assignment and the F03 corpus-review checkpoint. Separate the
   recorded test and input counts from the interpretation of per-target invalid
   payload coverage, which is pending instructor approval.
3. Assess F04/F05 using the build-hardening checkpoint and target provenance. Separate native build and
   ELF evidence from the required delivery-environment and CI acceptance checks.
4. Review `target1-correct-summary.json`. Check that the roadmap and index treat
   exit 40 and incomplete analysis as an inconclusive attempt. Flag conclusions
   that cannot be drawn from the recorded counts and runtime metadata.
5. Save a progress note in audit-output/audit-checkpoint.md and update it as each
   review area is completed. Label it partial.
6. Save the final Markdown report in audit-output/audit-report.md within the mounted
   packet. Write it to a temporary file in the same directory and rename it into
   place once complete. Verify it exists before finishing. Start with the audited
   revision and scope. For each issue give the file and section, the conflicting
   evidence or missing record, and the smallest correction. End with the remaining
   deliverables in order and one next defensive engineering task. Tag decisions
   that require instructor input. Print the report location and a brief summary in
   the TUI, then finish.
<!-- STRIX PROMPT END -->
