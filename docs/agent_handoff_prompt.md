# DiffSheriff implementation and verification handoff

Use a fresh Strix session for the open implementation work below. The
[roadmap](roadmap.md) owns course acceptance status. This session handles bounded
F07 and F10 fixes and the related F12 setup instructions. It also reviews the
historical F09 report metadata for missing evidence. Neither a synthetic test
pass nor the old native report completes a real target comparison.

## Start the session

Paste this in an interactive WSL Ubuntu terminal:

```bash
handoff='/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project/docs/agent_handoff_prompt.md'
launcher=$(awk '{sub(/\r$/, "")} /^<!-- STRIX LAUNCHER BEGIN -->$/{on=1;next} /^<!-- STRIX LAUNCHER END -->$/{exit} on && !/^```/{print}' "$handoff") &&
  test -n "$launcher" && bash -c "$launcher"
```

The launcher reads this handoff from the working tree and copies committed files
from `HEAD` into a disposable workspace. It includes the regression transfer
module and tests, pure validation helpers copied from the same revision, the CI
source setup step, and relevant documentation. It excludes real targets, configs,
inputs, credentials, and target build, execution, and replay code. The CI YAML
copy ends after the source setup step and the following unchanged line; it is
context for editing that step and is not a complete workflow.

The session opens the TUI, requests `openrouter/deepseek/deepseek-v4.1-flash-1017`,
uses the WSL default gateway proxy on port 10808, and loads no MCP connections.
Strix has a $5 budget and a finite ceiling of one million turns per agent. Check
the first `llm_request` entry in `strix.log` for the provider and model.

Share the printed run directory. Expected outputs under
`~/strix-runs/diffsheriff-remaining-*/`:

| Path | Contents |
| --- | --- |
| `evidence/audit-output/verification-report.md` | Outcomes and test evidence by roadmap item, plus remaining blockers |
| `evidence/audit-output/proposed.patch` | Proposed repository changes for review |
| `evidence/audit-output/checkpoint.md` | Progress after each task, including a partial run |
| `strix_runs/<run-id>/` | Native Strix session records and logs |

The launcher does not apply the patch. Review and test it in the real repository
before accepting any changes or updating the roadmap.

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
gateway=$(ip -4 route show default | awk 'NR == 1 {print $3}')
: "${gateway:?WSL IPv4 default gateway is missing}"
proxy="http://$gateway:10808"
export HTTP_PROXY="$proxy" HTTPS_PROXY="$proxy" ALL_PROXY="$proxy"
export http_proxy="$proxy" https_proxy="$proxy" all_proxy="$proxy"
export NO_PROXY='localhost,127.0.0.1,::1' no_proxy='localhost,127.0.0.1,::1'

mkdir -p "$HOME/strix-runs"
run_dir=$(mktemp -d "$HOME/strix-runs/diffsheriff-remaining-XXXXXX")
packet="$run_dir/evidence"
output="$packet/audit-output"
mkdir -p "$output"

python3 - "$project" "$revision" "$historical" "$packet" <<'PY'
import ast
import json
from pathlib import Path
import subprocess
import sys

project, revision, historical, packet = sys.argv[1:]
root = Path(packet)

def read(path, ref=revision):
    return subprocess.check_output(
        ["git", "-C", project, "show", f"{ref}:{path}"]
    ).decode("utf-8")

def write(path, content):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")

def helpers(path, imports, names):
    text = read(path)
    nodes = {
        node.name: node for node in ast.parse(text).body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    write(path, imports + "\n\n" + "\n\n\n".join(
        ast.get_source_segment(text, nodes[name]) for name in names
    ) + "\n")

for name in (
    "diffsheriff/__init__.py", "diffsheriff/regressions.py",
    "tests/__init__.py", "tests/test_regressions.py", "docs/ci.md",
):
    write(name, read(name))
helpers("diffsheriff/config.py", "from pathlib import PurePosixPath\n",
        ("ConfigError", "_string", "relative_path"))
helpers("diffsheriff/builder.py", "import hashlib\nfrom pathlib import Path\n",
        ("compute_sha256",))
helpers("diffsheriff/pipeline.py", "from diffsheriff.config import ConfigError, relative_path\n",
        ("expected_result", "contained_file"))

workflow = ".github/workflows/validate_target.yml"
prefix, end, _ = read(workflow).partition("      - run: python -m pip install .\n")
assert end and "      - name: Prepare target sources\n" in prefix
write(workflow, prefix + end)
write("context/revision.txt", revision + "\n")
report = json.loads(read("artifacts/evaluation/target1/correct/report.json", historical))
summary = {k: report[k] for k in (
    "schema_version", "exit_code", "verdict", "analysis_complete",
    "security_status", "functional_status", "total_tests_run",
    "functional_passed", "functional_failed",
)}
evidence = report["evidence"]
summary["runtime_image"] = evidence["execution_settings"].get("image")
summary["baseline_identity_modes"] = evidence.get("baseline_identity_modes")
summary["historical_revision"] = historical
write("context/historical-report.json", json.dumps(summary, indent=2) + "\n")
PY

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
Work in /workspace/evidence on the three items below. Read context/revision.txt
and docs/ci.md. The Python helper modules config.py, builder.py and pipeline.py
are exact excerpts for testing regression file transfer. They do not contain a
build or execution engine. The CI workflow copy is also an excerpt. Do not patch
these Python helper excerpts or add steps to the CI excerpt.

This is local software maintenance using harmless fixtures. Do not scan systems,
use the network, download dependencies, build or run course targets, generate
target inputs, reproduce vulnerabilities, run a hosted workflow, or delegate to
other agents. Do not commit, push, apply a patch to the live repository, change
historical evidence, or mark any course item accepted. If a prerequisite is
missing, record what failed and continue independent work. Stop any proposed
change that would require a weaker assertion or expanded access.

1. **F07: Fix stale files in a refreshed export.** `copy_regressions(...,
   replace_existing=True)` replaces matching files but leaves old manifests and
   inputs that no longer appear in the source snapshot. Docs call export a refresh.
   Baseline: `python3 -B -m pytest -q -p no:cacheprovider tests/test_regressions.py`.
   If pytest is absent, still add the repository test and verify the targeted
   before/after behavior with a standard-library script in a temporary directory;
   report the full suite as unrun. Add a regression test with harmless bytes
   and functional fixture metadata
   for an export that drops a previously exported case. Implement the smallest
   safe fix in diffsheriff/regressions.py and rerun that file. Plan and validate the
   transfer before mutating the destination. Keep unrelated files and payloads
   still referenced by a retained manifest; never follow symlinks or recursively
   clear the output path. If ownership is ambiguous, fail closed without changing
   files. Preserve import behavior, independent ground truth requirements,
   exact-baseline filtering and existing conflict handling. Verify refresh,
   unchanged unrelated files, and an invalid incoming transfer leaving the prior
   snapshot intact. Report any CLI behavior the packet cannot verify.

2. **F10: Preflight both CI sources before cloning either.** The current workflow
   checks and clones sequentially. A missing second bundle or an occupied second
   destination can leave the first checkout behind, causing a retry to fail on
   that new destination. Reproduce the partial setup with temporary local Git
   bundles containing ordinary text, then add a preflight for both bundle paths
   and both destination paths before the existing clone loop. Verify the exact
   step extracted from the YAML (use its known step boundaries if a YAML parser
   is unavailable): fresh setup resolves the two synthetic commits;
   a missing second bundle leaves the first destination absent; an existing or
   symlinked second destination is refused without changing it or creating the
   first. Keep local clone behavior and the workflow order. Do not add a new CI
   service, cleanup routine, runtime step or change the CLI gate. Distinguish path
   preflight from errors that happen during Git clone. Only that step may change.
   Include the executable synthetic check in the report under its own heading
   so a reviewer can repeat it without hosted CI.

3. **F12: Correct the shared setup instructions.** Update docs/ci.md to reflect
   the observed source preflight behavior and how to retry safely from a fresh
   checkout if a clone itself fails. Keep existing preparation instructions
   and limits concise; refer to the existing evaluation guide. Do not claim
   standalone delivery has passed. For F09, read context/historical-report.json
   and report why the retained native run cannot count as acceptance, what
   evidence remains absent, and which open checks belong to the course team.
   Keep this part read-only and do not produce target run or reproduction
   commands. Do not treat E01 approval or E02 defense as agent work.

Before edits, save the four candidate files temporarily so the patch is against
the supplied revision. Checkpoint after each work item in
audit-output/checkpoint.md. Write audit-output/proposed.patch as a unified diff
with a/ and b/ paths for only diffsheriff/regressions.py, tests/test_regressions.py,
.github/workflows/validate_target.yml and docs/ci.md. Use minimal context on the
workflow diff so it applies to the full file and does not delete anything outside
the source setup step. Remove temporary snapshots. Keep any unverified patch
clearly labeled. Verify the diff against the original packet files.

Write audit-output/verification-report.md with the source revision, per-item
status (implemented and verified, partial, or blocked), the exact verification
commands and observed results, changed files, and remaining prerequisites.
Distinguish local data handling and CI source setup evidence from hosted CI
gating, full later-run checks and course target acceptance. Write the report
through a temporary file and rename it into place, confirm it exists, print the
paths in the TUI, and conclude the session.
<!-- STRIX PROMPT END -->
