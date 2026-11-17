# Evaluation: what the team must do

Use this procedure after resolving the acceptance gaps in [the roadmap](roadmap.md).
The assessment needs **two approved independent C/C++ targets**, at
least one a real non-toy project/library. Each needs a baseline and three patch
versions: correct, incomplete, and functional regression. That is **six comparisons**,
not one demonstration. Use only the approved local input scope; no exploit tooling is
needed. Approval and source facts belong in [target_scenarios.md](target_scenarios.md).

## 1. Prepare the assets once

For each `target1` and `target2`:

- Record instructor approval, source/license provenance, four full Git commit hashes,
  and independent expected behavior. An incomplete patch must leave the same flaw
  reachable through a different approved input; a regression patch must break a valid
  input that the baseline passes. No invented outcomes or patched-output oracle.
- Preserve the source history in `targets/targetN/source.bundle` using
  `git -C PATH_TO_APPROVED_REPO bundle create ABSOLUTE_OUTPUT_PATH --all`.
  Include required license notices. Make sure all four commits have refs in that
  repository before bundling. The source commits must contain any required drivers
  and regular vendored dependencies; unsupported symlinks/submodules must be resolved
  as documented in usage, without changing provenance silently.
- Create `evaluation/targetN/{correct,incomplete,regression}.yaml` from
  `configs/example_target.yaml`. Within a target, change **only `target.patch_ref`**
  between those three configs. Use `repository_path: repository`, the full baseline
  hash, its designated observed sanitizer signature, build commands/binary paths,
  and the approved input interface/settings.
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
bash verify.sh
```

Use an image with the approved targets' declared build dependencies. The PDF requires
release hardening inspection and downgrade warnings, not every protection enabled.
The selected configs use neutral absolute minima; retain their actual observations. Clone the source
bundles into a fresh checkout; do not overwrite existing source worktrees. Keep the
bundles in Git, not unmanaged nested `.git` directories.

Then run this matrix. Each invocation creates a separate retained run; console output
and the latest report are saved beside it. The table compares expected outcomes without
changing the validator's verdict:

```bash
failed=0
for target in target1 target2; do
  for pair in correct:0 incomplete:10 regression:20; do
    variant=${pair%:*}; expected=${pair#*:}
    out="artifacts/evaluation/$target/$variant"
    mkdir -p "$out"
    actual=0
    diffsheriff --config "evaluation/$target/$variant.yaml" \
      --output-json "$out/report.json" --artifacts "$out/runs" \
      > "$out/console.log" 2>&1 || actual=$?
    printf '%s/%s expected=%s actual=%s\n' "$target" "$variant" "$expected" "$actual"
    [ "$actual" -eq "$expected" ] || failed=1
  done
done
[ "$failed" -eq 0 ]
```

Inspect every JSON: corresponding build modes, baseline identity, independent statuses,
hardening, correlation, three replay observations, and original/minimized inputs.
Code 30 means a build/config/tool problem; 40 means insufficient evidence. Diagnose
the recorded reason; never override those codes to match the table.

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
score or replace approval, unseen evaluation, genuine participation, or individual
defense. The validator audit and tests are recorded in the
[code-audit checkpoint](../artifacts/checkpoints/code-audit/README.md).
