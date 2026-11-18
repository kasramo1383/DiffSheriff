# Evaluation: what the team must do

Use this procedure after resolving the acceptance gaps in [the roadmap](roadmap.md).
The assessment needs **two independent C/C++ targets**, at least one a real non-toy
project/library. Instructor approval was waived by the course team. Each target
needs a baseline and three patch versions: correct, incomplete, and functional regression.
That is **six comparisons**, not one demonstration. Use only the documented local input
scope; no exploit tooling is needed. The waiver and source facts belong in
[target_scenarios.md](target_scenarios.md).

## 1. Prepare the assets once

For each `target1` and `target2`:

- Record source/license provenance, four full Git commit hashes, and independently
  justified expected behavior. No approval-pending requirement belongs in active target
  records. An incomplete patch must leave the same flaw reachable through a different
  in-scope input; a regression patch must break a valid input that the baseline passes.
  No invented outcomes or patched-output oracle.
- Preserve the source history in `targets/targetN/source.bundle` using
  `git -C PATH_TO_TARGET_REPO bundle create ABSOLUTE_OUTPUT_PATH --all`.
  Include required license notices. Make sure all four commits have refs in that
  repository before bundling. The source commits must contain any required drivers
  and regular vendored dependencies; unsupported symlinks/submodules must be resolved
  as documented in usage, without changing provenance silently.
- Create `evaluation/targetN/{correct,incomplete,regression}.yaml` from
  `configs/example_target.yaml`. Within a target, change **only `target.patch_ref`**
  between those three configs. Use `repository_path: repository`, the full baseline
  hash, its designated observed sanitizer signature, build commands/binary paths,
  and the documented input interface/settings.
- Put the same valid/boundary/invalid input files, `expected.json`, provenance, and
  shared `regression_directory` beside those configs. Define expected exit/stdout/
  stderr and validity independently. A reviewed fixed manifest can suffice. Use an
  optional reference command or establish expectations for the actual reduced inputs;
  no general-purpose reference implementation is required.
  `expected: null` deliberately leaves analysis incomplete.

All example placeholders must be replaced. If identifying the baseline signature,
inspect the actual approved finding under `evidence.cases[].runs.base[].signature`
from an initial run; record that finding's error/file/function/line. Do not choose an
unrelated signature merely to obtain a pass. Preserve that initial report too.

## 2. Install and run the six comparisons (Linux/WSL)

From the project root, with the required assets available:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
git clone targets/target1/source.bundle evaluation/target1/repository
git clone targets/target2/source.bundle evaluation/target2/repository
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
docker run --rm --entrypoint /bin/sh diffsheriff:local \
  -c 'test -x /usr/bin/llvm-symbolizer'
bash verify.sh
```

Use an image with the selected targets' declared build dependencies. The PDF requires
release hardening inspection and downgrade warnings, not every protection enabled.
The selected configs use neutral absolute minima; retain their actual observations. Clone the source
bundles into a fresh checkout; do not overwrite existing source worktrees. Keep the
bundles in Git, not unmanaged nested `.git` directories.

The `docker run` line is a required preflight: the sanitizer runtime needs an external
symbolizer to turn a stack address into `function file:line`. Without it Clang prints
`WARNING: invalid path to external symbolizer!`, triage resolves the function as
`unknown`, the designated baseline signature cannot be established, and the comparison
is inconclusive (40). All six configs therefore set
`external_symbolizer_path=/usr/bin/llvm-symbolizer` in `ASAN_OPTIONS` and
`UBSAN_OPTIONS`; the runtime image already installs LLVM. If the preflight fails,
install LLVM in the image rather than lowering the expectation.

Then run the six comparisons:

```bash
bash scripts/run_matrix.sh
```

The runner executes each comparison separately, saves its console output, retains the
JSON report and run bundles under `artifacts/evaluation/<target>/<variant>/`, compares
the process exit code with the justified outcome, and then verifies the retained
evidence through `scripts/verify_matrix_run.py`. It preflights Docker, the image, the
symbolizer, both configurations, both cloned repositories and every configured commit
before it executes anything, and it never rewrites an exit code. `--list` prints the
six rows; `MATRIX_ARTIFACTS` relocates the output root.

The rows are:

| Target | Variant | Config | Expected |
| --- | --- | --- | ---: |
| target1 | correct | `evaluation/target1/correct.yaml` | 0 |
| target1 | incomplete | `evaluation/target1/incomplete.yaml` | 10 |
| target1 | regression | `evaluation/target1/regression.yaml` | 20 |
| target2 | correct | `evaluation/target2/correct.yaml` | 0 |
| target2 | incomplete | `evaluation/target2/incomplete.yaml` | 10 |
| target2 | regression | `evaluation/target2/regression.yaml` | 20 |

Each row is one `diffsheriff --config … --output-json … --artifacts …` invocation; the
equivalent manual loop for one comparison is:

```bash
out="artifacts/evaluation/target1/correct"
mkdir -p "$out"
actual=0
diffsheriff --config evaluation/target1/correct.yaml \
  --output-json "$out/report.json" --artifacts "$out/runs" \
  > "$out/console.log" 2>&1 || actual=$?
python3 scripts/verify_matrix_run.py "$out" --target target1 --variant correct \
  --actual "$actual" --expected 0
```

Inspect every JSON: corresponding build modes, baseline identity, independent statuses,
hardening, correlation, three replay observations, and original/minimized inputs.
Code 30 means a build/config/tool problem; 40 means insufficient evidence. Diagnose
the recorded reason; never override those codes to match the table.

The verifier checks retained report and reproducer structure, process/report/expected
exit-code agreement, baseline identity, and replay evidence. Its matrix verdict is not
proof that `analysis_complete` is true or that every finding is correctly attributed;
review each report's analysis status and incomplete reasons before accepting a target.
The verifier fails a comparison that lacks a retained report, whose report exit code
differs from the process exit code, whose `evidence.baseline_identity_modes` is empty,
or whose reproducer bundles lack `reproducer.json`, `original.input`,
`minimized.input`, a matching minimized-input hash, or three baseline replays. Fix the
underlying cause and rerun; do not relax the check. A failing run keeps its
`console.log`, so the recorded `analysis_incomplete_reasons` and notes explain the
outcome.

## 3. Demonstrate replay, regression enrollment, and CI

- For each target, take a **baseline finding bundle from its correct-patch run**:
  `python -m diffsheriff.reproduce FULL_BUNDLE_PATH --check-regression` must return 0.
  Use the report's run directory plus one of its `evidence.reproducers` paths. Keep
  the entire run together and make its pinned Docker image ID available.
- Run each correct config again after the matrix. Require code 0 and verify the new
  report contains `regression/` cases. Establish independent expectations for any
  newly reduced inputs before considering this check complete.
- Commit the approved bundles/configs/corpora/generated regressions and evidence.
  The `Prepare target sources` step in `.github/workflows/validate_target.yml`
  already clones both bundles on a fresh runner and refuses existing destinations.
- Verify the existing target workflow from a fresh source environment. A hosted
  **Validate target patch** run is one convenient demonstration if available; the PDF
  does not prescribe GitHub or require separate hosted runs for both targets. Retain
  actual results and JSON. Correct patches should pass; incomplete/regression variants
  must fail the gate with their actual nonzero code. Do not add another CI system.

## 4. Finish delivery and the defense

In a clean Linux checkout without ignored developer state, repeat setup, both correct
runs, and replay. Keep source/image identities, versions, hashes, commands/results,
licenses, and runtime image availability instructions with the delivery. Combine this
check with the matrix/CI work when practical instead of repeating a full campaign.
An unseen-patch rehearsal is optional; no hidden-label package, answer key or worksheet
is required for repository completion. The actual defense-day unseen evaluation remains
required. Each student then
prepares and completes their own defense using [the study guide](defense_guide.md).

This procedure supplies evidence for the rubric; it cannot guarantee the instructor's
score or replace unseen evaluation, genuine participation, or individual defense.
Instructor approval was waived by the course team. The validator audit and tests are
recorded in the
[code-audit checkpoint](../artifacts/checkpoints/code-audit/README.md).
