# Patch validation in CI

The [target workflow](../.github/workflows/validate_target.yml) runs the real CLI.
Its config must already identify an authorized local target, independently defined
expectations, and full baseline/patch Git commit hashes. The example schema is not
a runnable course target. Target approval is recorded in
[target_scenarios.md](target_scenarios.md).

Run **Validate target patch** manually in GitHub Actions with the config's path,
or set the repository variable `DIFFSHERIFF_TARGET_CONFIG` to enable it on the
verification workflow's main-branch pushes and manual runs. It is also callable
from another workflow using `workflow_call`. The checkout includes full history and
submodules; `target.repository_path` must resolve to the checked-out target repository
with both source commits available. The runtime image is built from this checkout.

The job runs:

```sh
diffsheriff --config "$TARGET_CONFIG" \
  --regressions-from .diffsheriff/retained-regressions \
  --export-regressions .diffsheriff/retained-regressions \
  --output-json .diffsheriff/ci/report.json \
  --artifacts .diffsheriff/ci/runs
```

The CLI's exit code is the job's validation result. Only 0 passes; 10, 20, 30, and
40 fail the validation step. Expected scenario outcomes belong in a separate
demonstration, never an override that turns a vulnerable patch into a passing gate.
Target validation is not automatically run for pull requests. The unit and harmless
native jobs continue to run there.

## Regressions and retained evidence

The job restores the most recent accessible regression cache for the config path.
The CLI imports only manifests for the exact configured baseline, checks payload
hashes and contained paths, and rejects conflicts with checked-in files. If no cache
exists, the checked-in suite is used. Use a distinct config path per target.

Generated regressions are exported even when the pipeline returns a nonzero verdict.
The job attempts cache saving and artifact upload on both successful and failed runs.
`patch-validation` contains the CLI report, available source/build/run bundles, and
the exported regression suite. Setup failures before the CLI can run have workflow
logs but cannot have a target report. Caches can expire; the artifact is the retained
handoff copy, and important accepted regressions should also be committed to the
configured regression directory. GitHub artifacts also have a retention period, so
copy accepted evidence into `artifacts/` for durable project delivery.

For a local or clean CI checkout, copy the artifact's `retained-regressions` directory
and pass it through `--regressions-from`. Both transfer options accept directories;
neither changes a verdict into a pass. Export refreshes the specified output snapshot;
import refuses to overwrite different local assets. Existing unapproved expectations
must not be treated as ground truth merely because they came from an artifact.

## Reduced inputs with unknown functional behavior

Security minimization may produce bytes with no independent expected output. Such a
manifest has `check: diagnostic`, `expected: null`, and `valid_input: false`. It is
loaded and replayed in its recorded build mode on later runs. The original case and
its independent expectation are retained separately. Diagnostic reproduction alone
cannot complete the full regression check: missing expected behavior makes analysis
inconclusive, including on the first run that creates the reduced case.

To complete that check, supply an approved independent reference command or replace
the null expectation with an independently established `exit_code`, `stdout`, and
`stderr` mapping in the local manifest. Do not copy the patched program's output.
**Known limitation:** import currently rejects byte-different local and cached
manifests. In particular, a stale cache entry with `expected: null` can block a
matching checked-in manifest after its expectation has been independently approved.
Until this is fixed, review/retire that cache entry before importing it; never trust an
expectation merely because it came from the cache. The implementation work and required
conflict tests are tracked in [roadmap Stage 2](roadmap.md#stage-2--reconcile-trusted-regression-cache-manifests).
A known expected result for the same input bytes can also be reused from the independent
corpus.

Workflow mechanics follow GitHub's documentation for
[reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
and [dependency caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows).
