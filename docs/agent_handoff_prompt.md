# DiffSheriff Implementation and Verification Handoff

Use a fresh Strix session for the open and pending roadmap items below. The
[roadmap](roadmap.md) owns course acceptance status. This session addresses the
symbolizer and baseline signature diagnosis, target configuration hardening, the
real-target evaluation matrix (F09), later-run regression enrollment (F07), CI/CD
workflow verification (F10), and standalone delivery preparation (F12).

## Start the session

Paste this in an interactive WSL Ubuntu terminal:

```bash
handoff='/mnt/f/KasraFolder/دانشگاه صنعتی آریامهر/ترم 7/امنیت داده و شبکه/Project/docs/agent_handoff_prompt.md'
launcher=$(awk '{sub(/\r$/, "")} /^<!-- STRIX LAUNCHER BEGIN -->$/{on=1;next} /^<!-- STRIX LAUNCHER END -->$/{exit} on && !/^```/{print}' "$handoff") &&
  test -n "$launcher" && bash -c "$launcher"
```

The launcher extracts the committed codebase from `HEAD` into a disposable workspace packet.
It includes all `diffsheriff/` modules, full unit/integration test suites, target configs and
manifests under `evaluation/`, CI workflow definitions, and relevant documentation. It extracts
the diagnostic context from the historical `target1/correct` attempt (`exit_code: 40`), detailing
why the baseline signature was unestablished and why the reproducer replay was marked unstable.

The session runs in Strix, requests `openrouter/deepseek/deepseek-v4.1-flash-1017`, uses the
WSL default gateway proxy on port 10808, and operates within a $5 budget.

Expected outputs under `~/strix-runs/diffsheriff-remaining-*/`:

| Path | Contents |
| --- | --- |
| `evidence/audit-output/verification-report.md` | Outcomes, test evidence, diagnosis, and verification commands |
| `evidence/audit-output/proposed.patch` | Clean unified diff against repository HEAD for review |
| `evidence/audit-output/checkpoint.md` | Incremental progress recorded after each task |
| `strix_runs/<run-id>/` | Native Strix session execution records and logs |

The launcher does not apply the patch directly to the repository. The operator reviews, tests,
and applies the proposed patch before executing the final containerized target matrix.

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

def copy_file(rel_path, ref=revision):
    try:
        data = subprocess.check_output(["git", "-C", project, "show", f"{ref}:{rel_path}"])
        destination = root / rel_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    except Exception:
        src = Path(project) / rel_path
        if src.is_file():
            destination = root / rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(src.read_bytes())

# 1. Core package files
for name in (
    "diffsheriff/__init__.py", "diffsheriff/builder.py", "diffsheriff/cli.py",
    "diffsheriff/config.py", "diffsheriff/correlator.py", "diffsheriff/hardening.py",
    "diffsheriff/minimizer.py", "diffsheriff/pipeline.py", "diffsheriff/regressions.py",
    "diffsheriff/reporter.py", "diffsheriff/reproduce.py", "diffsheriff/runner.py",
    "diffsheriff/triage.py",
):
    copy_file(name)

# 2. Test suite
for name in (
    "tests/__init__.py", "tests/test_artifacts.py", "tests/test_builder.py",
    "tests/test_cli.py", "tests/test_config.py", "tests/test_container.py",
    "tests/test_container_integration.py", "tests/test_correlator.py",
    "tests/test_hardening.py", "tests/test_minimizer.py", "tests/test_pipeline.py",
    "tests/test_regressions.py", "tests/test_reporter.py", "tests/test_runner.py",
    "tests/test_sources.py", "tests/test_split_commits.py",
    "tests/test_target_assets.py", "tests/test_triage.py",
):
    copy_file(name)

# 3. Configurations and evaluation assets
for name in (
    "configs/example_target.yaml",
    "evaluation/target1/correct.yaml", "evaluation/target1/incomplete.yaml",
    "evaluation/target1/regression.yaml", "evaluation/target1/reference.py",
    "evaluation/target1/suites/expected.json",
    "evaluation/target2/correct.yaml", "evaluation/target2/incomplete.yaml",
    "evaluation/target2/regression.yaml", "evaluation/target2/reference.py",
    "evaluation/target2/suites/expected.json",
):
    copy_file(name)

# Copy target1 generated regressions
for name in (
    "evaluation/target1/generated-regressions/533609f36db8336c36255e0f4a97624621afe93ebba4349c80a3c650f518d139.json",
    "evaluation/target1/generated-regressions/5e2c902ef2a14d55f97fa26acaa8b0d84f6cb4eab96430809f77ba3fa0045831.json",
    "evaluation/target1/generated-regressions/7c2328b634e431ba1384cf482081177cbf34eab62de1952b1c2893808309b404.json",
    "evaluation/target1/generated-regressions/f58e94adc1e87425523cb461f0f50088f7677390c2e766c51416788b0684d0dc.json",
):
    copy_file(name)

# 4. CI Workflows and documentation
for name in (
    ".github/workflows/validate_target.yml", ".github/workflows/verify_patch.yml",
    "docs/roadmap.md", "docs/target_scenarios.md", "docs/evaluation.md",
    "docs/ci.md", "docs/specification.md", "docs/architecture.md",
    "docs/defense_guide.md", "docs/usage.md",
    "docker/Dockerfile", "docker/docker-compose.yml",
    "pyproject.toml", "README.md", "verify.sh",
):
    copy_file(name)

# 5. Diagnostic Context
write("context/revision.txt", revision + "\n")
hist_report_raw = read("artifacts/evaluation/target1/correct/report.json", historical)
hist_report = json.loads(hist_report_raw)
summary = {k: hist_report[k] for k in (
    "target_name", "schema_version", "exit_code", "verdict", "analysis_complete",
    "security_status", "functional_status", "total_tests_run",
    "functional_passed", "functional_failed", "notes",
)}
summary["runtime_image"] = hist_report["evidence"]["execution_settings"].get("image")
summary["baseline_identity_modes"] = hist_report["evidence"].get("baseline_identity_modes")
summary["baseline_signature_expected"] = hist_report["evidence"]["configuration"]["baseline_signature"]
summary["historical_revision"] = historical
write("context/historical-report.json", json.dumps(summary, indent=2) + "\n")

diagnosis = {
    "historical_exit_code": 40,
    "historical_verdict": "INCONCLUSIVE",
    "observed_error": "trees.c:1092:20: runtime error: index 734 out of bounds for type 'const uch[512]'",
    "sanitizer_warning": "==5684==WARNING: invalid path to external symbolizer!\n==5684==WARNING: Failed to use and restart external symbolizer!",
    "parsed_function": "unknown",
    "expected_function": "compress_block",
    "root_cause": (
        "ASan/UBSan external symbolizer missing in execution environment caused function name to resolve "
        "as 'unknown', mismatching baseline_signature ('compress_block') and triggering "
        "baseline_identity_unestablished (exit 40) and false reproducer_unstable."
    ),
    "remedy": (
        "Add external_symbolizer_path=/usr/bin/llvm-symbolizer to ASAN_OPTIONS and UBSAN_OPTIONS in "
        "target configurations, and ensure triage.py / runner.py robustly handle and default symbolizer paths."
    )
}
write("context/symbolizer-diagnosis.json", json.dumps(diagnosis, indent=2) + "\n")
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
You are working in `/workspace/evidence` on resolving the open and pending items in the
DiffSheriff patch-validation framework.

Read `context/revision.txt`, `context/historical-report.json`, `context/symbolizer-diagnosis.json`,
`docs/roadmap.md`, and `docs/evaluation.md`.

### Context & Operating Principles
DiffSheriff validates C/C++ patches by executing baseline and patch builds in isolated Docker
containers under release and sanitized modes. It prioritizes exit codes:
`30 (Build/Config error) > 10 (Vuln remains / New issue) > 20 (Func regression) > 40 (Inconclusive) > 0 (Pass)`.

Ground truth is defined strictly by independent specifications and reviewed manifests, never
inferred from patch output. A crash is not assumed to be a vulnerability without matching runtime
evidence and correlation. Maintain exact code standards: do not weaken assertions, bypass checks,
or simulate test passes.

---

### Task 1: Fix Symbolizer Configuration & Triage Robustness (F09 Precondition)
**Problem:** In the retained `target1/correct` attempt (`context/historical-report.json`), the run
returned exit code 40 (INCONCLUSIVE) with notes:
`"Designated baseline flaw was not reproduced with stable source evidence"` and
`"Unstable reproducer: regression/7c2328b634e431ba1384cf482081177cbf34eab62de1952b1c2893808309b404 sanitized base"`.
As diagnosed in `context/symbolizer-diagnosis.json`, Clang's ASan/UBSan lacked an explicit path to
`llvm-symbolizer`. The runtime emitted:
`==5684==WARNING: invalid path to external symbolizer!`
Because stack addresses could not be symbolized, `triage.py` parsed the function as `"unknown"`
instead of `"compress_block"`. This signature mismatch caused `baseline_identity_unestablished`
and falsely marked the reproducer unstable on replay.

**Action:**
1. Update `evaluation/target1/{correct,incomplete,regression}.yaml`,
   `evaluation/target2/{correct,incomplete,regression}.yaml`, and `configs/example_target.yaml`:
   Set `ASAN_OPTIONS: detect_leaks=0:abort_on_error=1:symbolize=1:external_symbolizer_path=/usr/bin/llvm-symbolizer`
   and `UBSAN_OPTIONS: print_stacktrace=1:halt_on_error=1:external_symbolizer_path=/usr/bin/llvm-symbolizer`.
2. Inspect `diffsheriff/triage.py`:
   Ensure `triage_execution_result` and frame parser handle UBSan reports with symbolizer warnings
   or trailing function names cleanly. If a stack frame contains `#0 0x... in <function> <file>:<line>`,
   extract the function accurately.
3. In `tests/test_triage.py` and `tests/test_config.py`:
   Add test coverage reproducing the exact raw stderr from `context/symbolizer-diagnosis.json`.
   Verify that function names are resolved and that configs validate the updated environment options.

---

### Task 2: Real-Target Matrix Automation and Verification (F09)
The assignment requires demonstrating two real/independent targets across 4 versions each,
amounting to 6 baseline-vs-patch comparisons.

**Targets:**
- Target 1: `zlib` (CVE-2018-25032, heap buffer overflow in `deflate.c`).
  - `evaluation/target1/correct.yaml` -> Expected code: **0** (`PASS`)
  - `evaluation/target1/incomplete.yaml` -> Expected code: **10** (`VULN_REMAINS`)
  - `evaluation/target1/regression.yaml` -> Expected code: **20** (`FUNC_REGRESSION`)
- Target 2: `libpng` (CVE-2019-7317, use-after-free in `png_image_free`).
  - `evaluation/target2/correct.yaml` -> Expected code: **0** (`PASS`)
  - `evaluation/target2/incomplete.yaml` -> Expected code: **10** (`VULN_REMAINS`)
  - `evaluation/target2/regression.yaml` -> Expected code: **20** (`FUNC_REGRESSION`)

**Action:**
1. Verify that the 6 configuration files adhere strictly to schema version 2.0:
   - Within each target, only `target.patch_ref` changes between variants.
   - `base_ref`, `patch_ref`, and `baseline_signature` match `docs/target_scenarios.md`.
2. Implement a dedicated local verification runner script or entry point (`scripts/run_matrix.sh`
   or structured bash snippet in `docs/evaluation.md`) that executes the 6 comparisons, captures
   console logs, retains JSON reports, verifies exit codes, and checks reproducer bundles under
   `artifacts/evaluation/<target>/<variant>/`.
3. Add tests in `tests/test_target_assets.py` verifying that all 6 target configuration files load,
   resolve referenced suite files, have matching baseline signatures, and specify valid build and
   execution settings.

---

### Task 3: Later-Run Regression Enrollment & Replay Validation (F07 / F09)
**Action:**
1. Verify the regression export/import pipeline (`diffsheriff/regressions.py`):
   - Minimized failing inputs from the vulnerable baseline must be retained and automatically
     enrolled into regression suites for matching baselines.
   - When a regression case is replayed on the correct patch, it must verify the absence of the
     designated baseline failure and satisfy independent expected behavior.
2. In `tests/test_regressions.py`:
   - Verify that stale manifests for a baseline are retired upon export refresh.
   - Verify that invalid or unverified external manifests are rejected cleanly without corrupting
     the cache.
   - Test that `reproduce.py` succeeds with returncode 0 on valid reproducers across >= 3 replays.

---

### Task 4: CI Workflow and Standalone Delivery Preflight (F10 / F12)
**Action:**
1. Inspect `.github/workflows/validate_target.yml`:
   - Verify the `Prepare target sources` step: it must preflight both `targets/targetN/source.bundle`
     paths and ensure neither destination exists or is symlinked before cloning either.
   - Verify that the workflow correctly restores regressions, invokes `diffsheriff`, saves
     regressions, and uploads artifacts.
2. Update `docs/ci.md` and `docs/evaluation.md`:
   - Provide exact, reproducible steps for a clean-checkout run without reliance on local paths or
     uncommitted files.
   - Document the symbolizer fix so future evaluators understand the container requirements.

---

### Verification and Delivery Requirements

1. **Local Test Execution:**
   Run the pytest suite to verify all code and asset changes:
   ```bash
   python3 -m pytest -q tests/
   ```
   Ensure all tests pass with zero regressions.

2. **Incremental Checkpointing:**
   Record progress after each task into `audit-output/checkpoint.md`, noting verified functionality,
   commands executed, and observed results.

3. **Proposed Patch Generation:**
   Generate `audit-output/proposed.patch` containing clean unified diffs (`git diff` style with `a/`
   and `b/` prefixes) for all modified files:
   - `diffsheriff/triage.py` (if defensive parsing updated)
   - `diffsheriff/runner.py` (if symbolizer defaults updated)
   - `evaluation/target1/*.yaml`
   - `evaluation/target2/*.yaml`
   - `configs/example_target.yaml`
   - `tests/test_target_assets.py` / `tests/test_triage.py`
   - `docs/ci.md`, `docs/evaluation.md`, `docs/roadmap.md`

4. **Final Verification Report:**
   Write `audit-output/verification-report.md` detailing:
   - Evaluated repository revision
   - Itemized status for F07, F09, F10, and F12
   - Exact technical cause and remedy for the historical F09 failure
   - Test execution logs and verification evidence
   - Operator execution guide for running the containerized target matrix

Conclude by printing the paths of `verification-report.md` and `proposed.patch`.
<!-- STRIX PROMPT END -->
