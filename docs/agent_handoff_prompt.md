# DiffSheriff reporting verification and implementation handoff

Use a fresh interactive Strix session to verify the reporting change from
`fa6ee16` and fill the remaining direct reporter test coverage. The course
acceptance state lives in the [roadmap](roadmap.md). This session verifies
reporting and does not provide target evaluation evidence for F09.

## Start the session

Paste this command in an interactive WSL Ubuntu terminal. It reads the launcher
and prompt from this file in the working tree. It supplies the relevant source,
tests, and report contract from the same committed revision. The previous native
run is represented by a small historical metadata extract for the legacy JSON
check. The Strix workspace is a writable copy; it does not contain the repository,
real target sources, inputs, binaries, build/replay code, or credentials.

```bash
handoff='/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project/docs/agent_handoff_prompt.md'
launcher=$(awk '{sub(/\r$/, "")} /^<!-- STRIX LAUNCHER BEGIN -->$/{on=1;next} /^<!-- STRIX LAUNCHER END -->$/{exit} on && !/^```/{print}' "$handoff") &&
  test -n "$launcher" && bash -c "$launcher"
```

The launcher uses the configured Strix/OpenRouter credentials, requests DeepSeek
Flash 1017, and uses the Windows proxy at the current WSL gateway on port 10808.
It passes an empty MCP configuration, sets the Strix budget to $5, and uses a
finite ceiling of one million turns per agent (the installed CLI needs a positive
integer). It starts the TUI without a non-interactive flag.

Share the printed run directory after the session. Under
`~/strix-runs/diffsheriff-reporting-*/`, look for:

| Path | Contents |
| --- | --- |
| `evidence/audit-output/verification-report.md` | Outcome, exact commands, test counts, and any remaining limitations |
| `evidence/audit-output/proposed.patch` | Patch for the reporter test file and, only if needed, the reporter itself |
| `evidence/audit-output/checkpoint.md` | Latest progress if interrupted |
| `strix_runs/<run-id>/` | Native Strix session artifacts, including the LLM log |

Check the first `llm_request` entry for `provider=openrouter` and
`model=deepseek/deepseek-v4.1-flash-1017`. Codex can review the saved report and
patch and verify the proposed edits in the repository. The launcher does not
apply the patch.

<!-- STRIX LAUNCHER BEGIN -->
```bash
set -euo pipefail
project='/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project'
handoff="$project/docs/agent_handoff_prompt.md"
config="$HOME/.strix/cli-config.json"
model=openrouter/deepseek/deepseek-v4.1-flash-1017
historical=1d0910d0f8eb25e3122a1600bddff2c1287d713a

command -v strix >/dev/null
test -r "$config" || { printf 'Cannot read Strix config: %s\n' "$config" >&2; exit 1; }
revision=$(git -C "$project" rev-parse --verify HEAD)
git -C "$project" merge-base --is-ancestor fa6ee16 "$revision" ||
  { printf 'HEAD does not contain the reporting fix fa6ee16.\n' >&2; exit 1; }

gateway=$(ip -4 route show default | awk 'NR == 1 {print $3}')
: "${gateway:?WSL IPv4 default gateway is missing}"
proxy="http://$gateway:10808"
export HTTP_PROXY="$proxy" HTTPS_PROXY="$proxy" ALL_PROXY="$proxy"
export http_proxy="$proxy" https_proxy="$proxy" all_proxy="$proxy"
export NO_PROXY='localhost,127.0.0.1,::1' no_proxy='localhost,127.0.0.1,::1'

mkdir -p "$HOME/strix-runs"
run_dir=$(mktemp -d "$HOME/strix-runs/diffsheriff-reporting-XXXXXX")
packet="$run_dir/evidence"
output="$packet/audit-output"
mkdir -p "$packet/diffsheriff" "$packet/tests" "$packet/context" "$output"

for path in diffsheriff/__init__.py diffsheriff/reporter.py tests/__init__.py tests/test_reporter.py; do
  git -C "$project" show "$revision:$path" > "$packet/$path"
done
git -C "$project" show -s --format='%H %s' "$revision" > "$packet/context/revision.txt"
git -C "$project" show "$revision:docs/usage.md" |
  awk '/^Codes are /{copy=1} /^An insertion-only patch /{copy=0} copy' \
    > "$packet/context/report-contract.md"
test -s "$packet/context/report-contract.md"
git -C "$project" show "$historical:artifacts/evaluation/target1/correct/report.json" |
  python3 -c '
import json
import sys

source = json.load(sys.stdin)
keys = ("schema_version", "analysis_complete", "exit_code", "verdict",
        "security_status", "functional_status", "analysis_incomplete_reasons")
json.dump({key: source[key] for key in keys if key in source}, sys.stdout, indent=2)
print()
' > "$packet/context/historical-report-extract.json"

awk '/^<!-- STRIX PROMPT BEGIN -->$/{copy=1;next} /^<!-- STRIX PROMPT END -->$/{exit} copy' \
  < <(tr -d '\r' < "$handoff") > "$run_dir/instructions.md"
test -s "$run_dir/instructions.md"
printf '[]\n' > "$run_dir/mcp.json"

printf 'Revision: %s\nRun directory: %s\nReport: %s/verification-report.md\nRequested model: %s\n' \
  "$revision" "$run_dir" "$output" "$model"
cd "$run_dir"
status=0
STRIX_LLM="$model" strix \
  --config "$config" \
  --mcp-config "$run_dir/mcp.json" \
  --target "$packet" \
  --instruction-file "$run_dir/instructions.md" \
  --scan-mode quick --max-budget 5 --max-turns 1000000 || status=$?

if [[ -s "$output/verification-report.md" ]]; then
  printf 'Saved report: %s/verification-report.md\n' "$output"
else
  printf 'No completed report. Check %s and %s/strix_runs/ for partial output.\n' \
    "$output" "$run_dir" >&2
  (( status != 0 )) || status=1
fi
if [[ -s "$output/proposed.patch" ]]; then
  printf 'Proposed patch: %s/proposed.patch\n' "$output"
fi
exit "$status"
```
<!-- STRIX LAUNCHER END -->

## Strix prompt

<!-- STRIX PROMPT BEGIN -->
This is a local Python reporting and unit test task. Work in /workspace/evidence.
Read context/revision.txt, context/report-contract.md, and
context/historical-report-extract.json first. The directory is the entire task
scope. Do not scan, use the network, install packages, build target programs,
generate test payloads, reproduce vulnerabilities, or delegate to other agents.
The exit code names are plain values to exercise in unit tests.

1. Run the baseline: from /workspace/evidence, use
   `python3 -B -m pytest -q -p no:cacheprovider tests/test_reporter.py`. If pytest
   is absent, use Python's standard library to import the module and call each
   plain `test_*` function, reporting that method explicitly. Do not use an
   expected result as a substitute for an observed result. Save progress to
   audit-output/checkpoint.md after the baseline.
2. Add focused tests to tests/test_reporter.py for the behavior that existing
   priority tests do not cover. Use small synthetic ValidationSummary instances
   and temporary directories. Check that a complete JSON report has `[]`;
   marking incomplete adds unique reasons in first-seen order across repeated
   calls; and writing an incomplete error report keeps schema `2.0`, its exit
   code, counters, notes and collected evidence. Keep tests callable without
   pytest fixtures so the standard-library fallback works. Separately load the
   historical extract and verify it is still incomplete with no recorded reason
   field. The extract is historical metadata; do not edit it or add a JSON reader.
3. Rerun the checks before proposing any production edit. If a new test fails,
   distinguish an unsupported test assumption or environment problem from a
   defect reachable through the existing reporter API. Correct the test or
   report the environment issue as appropriate. Change diffsheriff/reporter.py
   only if the failure demonstrates a violation of the documented report
   contract, and rerun the tests after that change. Preserve existing field
   types, exit codes and priority, and avoid broader refactoring. Stop and
   report a blocker if it would require another file, environment changes, or
   additional access. Do not commit or push.
4. Write audit-output/proposed.patch as a unified diff against the original
   snapshot, with `a/` and `b/` paths relative to the repository root. Before
   editing, keep the original text temporarily under audit-output/ for the diff;
   remove that copy afterward. Only diffsheriff/reporter.py and
   tests/test_reporter.py may appear in the patch. If you couldn't verify a patch,
   label it unverified in the report. Leave the context files untouched.
5. Write audit-output/verification-report.md with the source revision, outcome
   (verified, failed, or blocked), exact commands and observed results before
   and after edits, changed files and patch path (or why no patch), and limits.
   Distinguish serializer checks from CLI, pipeline and course acceptance,
   which are outside this session. Write to a temporary file in audit-output/
   and rename it to the final report when complete. Verify the report exists,
   print its path in the TUI, and conclude the session.
<!-- STRIX PROMPT END -->
