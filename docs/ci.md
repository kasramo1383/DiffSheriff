# Patch validation in CI

The [target workflow](../.github/workflows/validate_target.yml) runs the real CLI.
Its config must already identify an authorized local target, independently defined
expectations, and full baseline/patch Git commit hashes. The example schema is not
a runnable course target. See [target_scenarios.md](target_scenarios.md) for target
provenance and the status of instructor approval.

Run **Validate target patch** manually in GitHub Actions with the config's path,
or set the repository variable `DIFFSHERIFF_TARGET_CONFIG` to enable it on the
verification workflow's main-branch pushes and manual runs. It is also callable
from another workflow using `workflow_call`. The checkout includes full history and
submodules; `target.repository_path` must resolve to the checked-out target repository
with both source commits available. The runtime image is built from this checkout.

The `Prepare target sources` step preflights both bundle paths
(`targets/<target>/source.bundle`) and both destinations
(`evaluation/<target>/repository`) before it clones either bundle. A missing
bundle, a file that `git bundle list-heads` cannot read, or an existing or symlinked
destination stops the step before it creates a checkout. Only then does the step
clone the two bundles in the existing order. Fresh-runner tests verify every
configured commit is available, and synthetic bundles verify that an unreadable
second bundle leaves the first destination untouched. If a clone itself fails after a
successful preflight, the first checkout may already exist; retry from a fresh
checkout or clean runner rather than reusing the partial workspace, because the step
refuses an existing destination and never deletes one.
See the [evaluation guide](evaluation.md) for standalone setup. Target acceptance
results remain separate from source setup verification.

After the runtime image is built, the job verifies the external symbolizer inside it:

```sh
docker run --rm --entrypoint /bin/sh diffsheriff:local \
  -c 'test -x /usr/bin/llvm-symbolizer'
```

This is a target-acceptance precondition, not a convenience check. Clang's ASan/UBSan
runtime must invoke `llvm-symbolizer` to turn a stack address into
`function file:line`. Without it the runtime prints
`WARNING: invalid path to external symbolizer!`, frames stay as `module+offset`,
triage reports the function as `unknown`, the designated `baseline_signature` cannot
be established, and the comparison returns 40 (INCONCLUSIVE) with
`baseline_identity_unestablished`. All six shipped configs set
`external_symbolizer_path=/usr/bin/llvm-symbolizer` in `ASAN_OPTIONS` and
`UBSAN_OPTIONS`, and the job fails before validation if the image cannot honor it.
The runner also supplies that default for sanitizer options that omit the path, which
keeps replays of bundles recorded before this option existed usable.

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

## Reproduce the job from a clean checkout

Every command below uses only committed files. No absolute path, ignored directory,
local regression cache, or uncommitted edit is required.

```sh
git clone REPOSITORY_URL diffsheriff-clean
cd diffsheriff-clean
git rev-parse HEAD                        # record the evaluated revision

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

for target in target1 target2; do
  test -f "targets/$target/source.bundle"
  test ! -e "evaluation/$target/repository"
  git bundle list-heads "targets/$target/source.bundle" >/dev/null
done
git clone -- targets/target1/source.bundle evaluation/target1/repository
git clone -- targets/target2/source.bundle evaluation/target2/repository

docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
docker run --rm --entrypoint /bin/sh diffsheriff:local \
  -c 'test -x /usr/bin/llvm-symbolizer'

mkdir -p .diffsheriff/ci .diffsheriff/retained-regressions
diffsheriff --config evaluation/target1/correct.yaml \
  --regressions-from .diffsheriff/retained-regressions \
  --export-regressions .diffsheriff/retained-regressions \
  --output-json .diffsheriff/ci/report.json \
  --artifacts .diffsheriff/ci/runs
echo "exit code: $?"
```

The last command's exit code is the validation result; keep
`.diffsheriff/ci/report.json` and `.diffsheriff/ci/runs/` with it. To run all six
comparisons with the same evidence checks, use
`bash scripts/run_matrix.sh` as described in [evaluation.md](evaluation.md).
`bash scripts/run_matrix.sh` refuses to start when the bundles, the cloned
repositories, the image, or the symbolizer are missing, so a partial checkout cannot
be mistaken for a failed patch.

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
import preserves independently reviewed local assets. A full cached expectation with
no matching local manifest is accepted only when a pre-import local corpus or reviewed
regression has exactly the same input bytes, expected behavior, and validity flag.
Cache content alone cannot establish ground truth. Keep approved expectations in the
local corpus or checked-in regression directory, including expectations previously
established by a reference command.

## Reduced inputs with unknown functional behavior

Security minimization may produce bytes with no independent expected output. Such a
manifest has `check: diagnostic`, `expected: null`, and `valid_input: false`. It is
loaded and replayed in its recorded build mode on later runs. The original case and
its independent expectation are retained separately. Diagnostic reproduction alone
cannot complete the full regression check: missing expected behavior makes analysis
inconclusive, including on the first run that creates the reduced case.

To complete that check, supply an approved independent reference command or replace
the null expectation with an independently established `exit_code`, `stdout`, and
`stderr` mapping in the local manifest, set `check: full`, and explicitly review its
boolean `valid_input`. Do not copy the patched program's output.

An incoming diagnostic null expectation now yields to a matching local full check.
Identity includes the exact baseline, verified input hash and bytes, input filename,
build mode, both signatures, finding side, kind, and all other metadata except
`expected`, `check`, and `valid_input`. The local manifest and input remain byte-for-byte
unchanged. Equal metadata also preserves local formatting, and repeated imports are
idempotent. Different non-null expectations, identity differences, invalid metadata,
corrupt inputs, traversal, and symlinks fail closed before transfer writes. Export
refreshes the caller-owned output snapshot for the configured baseline, even
when there are no generated regressions. It retires stale manifests and unreferenced
payloads from that baseline. Other baselines and unrelated files are preserved.
Invalid destination manifests and conflicting files are rejected before any writes.

For an untrusted cache expectation without independent local evidence, import reports
`BUILD_OR_CONFIG_ERROR` (30). Omit `--regressions-from` for a fresh local run, or establish
and check in the reviewed local expectation before importing again. Do not copy cache
output into the local corpus just to bypass the check. CI operators can retire an
incompatible cache and run from the reviewed checkout. See the
[Stage 2 checkpoint](../artifacts/checkpoints/cache-import/README.md) for verification.
A known expected result for the same input bytes can also be reused from the independent
corpus.

Workflow mechanics follow GitHub's documentation for
[reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)
and [dependency caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows).
