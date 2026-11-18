# Running DiffSheriff

For the short, ordered assessment procedure, see [evaluation.md](evaluation.md).

## Install and prepare the runtime

Use Python 3.10 or newer, Git, and Docker with Linux amd64 containers. The Docker
image must contain DiffSheriff and the compilers/libraries needed by the target.
Invoke the validator on the host; do not expose the Docker socket to target containers.
If Docker runs in WSL, run DiffSheriff inside the same WSL distribution. Prefer a
Linux filesystem checkout when Windows directory permissions obstruct bind mounts
or Docker build-context inspection.

```sh
python -m pip install -e '.[dev]'
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
python -m pytest -q
```

The supplied native fixture echoes bytes safely. It contains no vulnerability,
exploit, or bypass. Run the real container check separately:

```sh
# POSIX shell
DIFFSHERIFF_DOCKER_TESTS=1 python -m pytest -q tests/test_container_integration.py
```

```powershell
$env:DIFFSHERIFF_DOCKER_TESTS = '1'
python -m pytest -q tests/test_container_integration.py
```

It builds two source revisions in both modes, checks hardening and all input
interfaces, and expects `40`: a harmless program cannot establish a baseline flaw.
Set `DIFFSHERIFF_TEST_IMAGE` to test a different locally built runtime image without
replacing `diffsheriff:local`.
The other integration tests simulate diagnostic output to exercise verdicts; they
are not security-target acceptance evidence.

For one-command tool verification on Linux/WSL after installing the development
dependencies and building the runtime image:

```sh
bash verify.sh
```

This checks prerequisites, Black, standard Flake8 checks, the complete test suite
including the harmless native matrix, and wheel construction. It fails on any failed
step and retains results in a fresh `.diffsheriff/verification.*` directory without
deleting earlier evidence. `PYTHON` selects the Python executable;
`DIFFSHERIFF_TEST_IMAGE` selects an already-built image. Copy accepted results into
`artifacts/` with source/image identities when retaining a checkpoint. This command
does not claim the approved-target matrices or clean-room delivery are complete.

## Configure an authorized target

Copy `configs/example_target.yaml` beside independently maintained test assets.
Schema version `2.0` replaces the original scaffold schema; old files fail with code
30 instead of silently running a partial analysis.

- `target.repository_path` is a local Git repository. `base_ref` and `patch_ref` must
  be full commit hashes. The checkout, including uncommitted files, is untouched.
- `target.baseline_signature` specifies `error_type`, repository-relative `file`,
  `function`, and baseline `line`. Match the actual symbolized diagnostic. Compile
  diagnostic builds with `-g -fno-omit-frame-pointer` and sanitizer support, and give
  the sanitizer runtime an external symbolizer:
  `ASAN_OPTIONS=...:symbolize=1:external_symbolizer_path=/usr/bin/llvm-symbolizer` and
  `UBSAN_OPTIONS=...:external_symbolizer_path=/usr/bin/llvm-symbolizer`. Every shipped
  configuration sets both. The runner appends that path when sanitizer options omit
  it (so replaying an older reproducer bundle still resolves functions), but an
  explicit value is preferred because it is recorded with the run. Without a
  symbolizer, Clang prints `WARNING: invalid path to external symbolizer!`, frames
  stay as `module+offset`, the parsed function is `unknown`, and no function-level
  signature can be established. The retained triage record exposes
  `symbolizer_failed` and `unsymbolized_frames` so this cause is visible in the JSON
  instead of appearing as an unexplained inconclusive result.
- Build commands are trusted shell commands executed inside disposable containers.
  Paths are relative to the source root. Dependencies must already be in the image
  or vendored: builds have no network. Symlinks/submodules are rejected.
- All configuration paths are relative to the YAML file. Suite paths and binary
  paths cannot traverse outside their designated roots.
- `valid_directory`, `boundary_directory`, and `malicious_directory` must each
  contain at least one existing input. The historical `malicious_directory` key also
  accepts ordinary invalid-input tests. DiffSheriff does not generate exploits.
- `stdin` and `file` carry arbitrary bytes; `argv` carries one UTF-8 argument and
  cannot represent NUL. Set `fixed_arguments` and optional `file_argument_flag` as
  needed. Equivalent versions always use the same settings.
- Hardening minima are optional operator policy, not mandatory all-enabled course
  requirements. The example config is stricter than the six selected target configs,
  whose absolute minima are neutral. ELF inspection and downgrade warnings always run.
  An explicitly enabled missing minimum or a detected downgrade still prevents PASS
  under the current conservative verdict policy.

## Independent expectations

The `expectations` JSON maps each `suite/relative-filename` to the expected exit code,
stdout, and stderr. An optional `valid_input` boolean records whether the independent
specification designates that input as valid:

```json
{
  "valid/hello.input": {"exit_code": 0, "stdout": "hello\n", "stderr": ""},
  "boundary/empty.input": {"exit_code": 0, "stdout": "", "stderr": "", "valid_input": true},
  "malicious/invalid.input": {"exit_code": 2, "stdout": "", "stderr": "invalid\n"}
}
```

Keys must match the discovered corpus exactly. Outputs use a lossless Latin-1 byte
mapping, so byte `ff` is JSON `"\u00ff"`. JSON Unicode text must represent the exact
expected output bytes. `provenance` records the independent specification/test source;
it is not evidence of instructor approval by itself.

`valid_input` defaults to true in the `valid` suite and false in other suites.
Mark independently valid boundary cases true so baseline-passing, patch-failing
behavior is counted as a functional regression (exit 20, subject to exit priority).
Invalid or unspecified boundary cases still check expected behavior and can prevent
PASS, but a mismatch alone is not labeled a valid-input regression. The flag must
be a JSON boolean; strings, numbers, and null are rejected. Generated regressions
preserve this designation. Existing manifests without the flag retain their defaults.

Security-input reduction preserves the classified error and source location across
three executions, even without an independent functional reference. Timeouts,
resource/output limits, different locations, and generic nonzero exits do not match.
Functional-input reduction still requires known independent expectations. To obtain
expectations for new reduced inputs, supply an independent reference executable as
an argv list, for example `["python3", "/src/reference.py"]`.
It receives candidate bytes on stdin and must emit one JSON object with `exit_code`,
`stdout`, and `stderr`, exiting 0. It runs in a restricted container with the config
directory at `/src`, read-only, and never receives target observations. Its logic
must come from the approved independent specification. Failure or malformed output
is code 30. The resulting expectation is retained in the generated regression.

The reference may also supply a boolean `valid_input` for those exact candidate
bytes. Without it, newly reduced bytes have unknown validity and are not credited
as valid-input functional checks. A known corpus designation is reused for identical
bytes; the parent input's validity is never inherited by different reduced bytes.
Stable minimized replays enter the same finding and exit-priority rules as ordinary
cases. New results identify their minimized input and parent case in the report;
results already represented by that parent are deduplicated. This comparison reuses
recorded observations and never recursively minimizes the reduced case.

Reference output is a UTF-8 JSON document. Expected stdout/stderr strings inside that
document still represent output bytes with the Latin-1 mapping described above.
For argv delivery, reduction skips byte slices that are not valid UTF-8 or contain
NUL, instead of treating an unrepresentable candidate as a validator failure.

## Reduction limits and retained outcomes

The optional top-level `minimization` configuration bounds each reproducer's search:

```yaml
minimization:
  max_granularity: 16
  max_oracle_calls: 256
```

These are the defaults for existing configurations. Granularity must be an integer
at least 2; oracle calls must be an integer at least 1. `null` disables an individual
limit. Disabling both permits the complete delta-debugging search, which can be costly
for large inputs. An oracle call evaluates one candidate and may run several reference
and target processes; it is not a count of child-process executions. Initial input and
empty-input checks consume this budget. The final three baseline and three patch
replays run separately and are not skipped when the search limit is reached.

`reproducer.json` retains a `minimization` record; report JSON includes the same summary
under `evidence.minimizations`, with case/mode/side and a relative reproducer path.
Records include original/reduced byte sizes, whether shrinking occurred, both limits,
oracle-call count and the stop reason:

| Stop reason | Meaning |
| --- | --- |
| `granularity_limit` | Finer partitions were not attempted beyond the configured cap. |
| `oracle_call_limit` | The candidate-evaluation budget was consumed. |
| `search_exhausted` | All chunks and complements at single-byte granularity were rejected for the retained input. |
| `empty_reproducer` | Empty input preserves the finding. |
| `single_byte_reproducer` | One byte remains after empty input was rejected. |
| `initial_not_reproduced` | The initial reduction check failed; original bytes are retained and reproduction is incomplete. |

A limit stop retains the last input known to preserve the invariant; it does not imply
that the input shrank or is minimal. Final replay stability and independent functional
expectations still determine the verdict. An exhausted search also does not prove a
global minimum or establish input validity. The byte-returning `ddmin` helper remains
available for existing Python callers; the pipeline uses `minimize` and its structured
result to retain limits and outcomes.

## Validate and inspect

```sh
diffsheriff --config path/to/target.yaml --output-json validation_report.json \
  --artifacts .diffsheriff/runs
```

Codes are `0` PASS, `10` remaining/new confirmed diagnostic, `20` functional regression,
`30` build/config/tool failure, and `40` incomplete/unstable/insufficient evidence.
Priority is `30 > 10 > 20 > 40 > 0`. JSON retains all findings and independent security,
functional, and completeness statuses. A new diagnostic is not automatically proof
that the patch caused it. Correlation evidence and uncertainty are reported separately.

New reports include `analysis_incomplete_reasons`, a list of distinct reason tokens
in the order first recorded. It is empty for complete analysis and nonempty for
incomplete analysis, including when a higher priority outcome determines the exit
code. `notes` and finding evidence carry the details for individual failures.
The field is additive in schema `2.0`. If an older incomplete report lacks it,
read that as **cause not recorded** and continue to use `analysis_complete` for
completeness.

| Reason | Meaning |
| --- | --- |
| `setup_failed` | Configuration, inputs, runtime image resolution, or source preparation failed before the build. |
| `tool_failure` | An operational error interrupted the build or analysis. |
| `hardening_warning` | Release hardening degraded or did not meet a configured requirement. |
| `runtime_budget_exhausted` | An execution hit a time, resource, or output limit. |
| `replays_unstable`, `reproducer_unstable` | Suite observations or subsequent reproducer checks were unstable, respectively. |
| `baseline_identity_unestablished` | No stable source evidence confirmed the designated baseline signature. |
| `generated_baseline_signature_unconfirmed` | A generated case failed to confirm its expected baseline signature. |
| `source_signature_unconfirmed` | An abnormal termination lacked a confirmed source signature. |
| `patch_attribution_unestablished`, `fix_evidence_insufficient` | Evidence was insufficient to attribute a patch finding or classify a baseline finding as fixed, respectively. |
| `functional_expectation_missing` | An input lacked an independent functional expectation. |
| `functional_expectation_unmet_on_baseline`, `functional_expectation_unmet_on_patch` | Observed behavior on the indicated version did not meet the independent expectation and the comparison remained inconclusive. A confirmed designated baseline security signature is handled as the security scenario instead of adding the baseline functional-gap reason. |
| `report_write_failed`, `regression_export_failed` | The retained report could not be written or regression export failed, respectively. |

An insertion-only patch can be related to a baseline finding when one insertion hunk
has an unambiguous function declaration in Git's hunk context, and that exact function
and source path appear on the baseline runtime stack after the insertion point. All
three baseline observations must support the same hunk. The report labels this
`Insertion in observed function`; it is function-level evidence, not proof that an
inserted branch executed. A Fixed result also requires stable corresponding patch
runs satisfying independent expectations. Missing/complex function context, ambiguous
candidate insertions, and changing caller evidence remain inconclusive. Existing
edited-line correlation still applies to both versions, and a new patch diagnostic
does not acquire causal attribution from this baseline-only rule.

For a hunk that replaces existing lines, `Edit in observed function` requires one
matching hunk with an unambiguous function declaration and matching runtime file/function.
Several matching edit hunks are accepted as `Edits in observed function` when every
candidate belongs to the same observed function. When callers are also edited, the
top runtime frame may instead be reported as `Edited function on observed stack`.
Different-function candidates with no edited top frame remain inconclusive. A direct
edited-line runtime intersection takes precedence. Function- and stack-level evidence
do not prove branch execution or patch causation. A Fixed verdict still requires stable
corresponding baseline replays and independently expected behavior on the patch.

The report identifies its run directory. `total_tests_run` counts suite executions
(including their three repetitions); `functional_passed` and `functional_failed`
count comparisons for valid inputs by build mode. A failed comparison can be
inconclusive, for example when the baseline also misses the independent expectation.
Additional minimization and reproducer executions
are recorded in the corresponding replay logs. stdout/stderr are bounded per stream;
exceeding a bound prevents a passing result.

The console also prints release hardening, per-build symbol observations, and finding
detection/correlation/stability/reason and minimized-input paths. Full details remain
in JSON. `evidence.builds.SIDE.MODE.elf` retains the ELF observations for each binary;
`evidence.hardening` remains the release-only comparison. Its indicators include
available symbol tables, conventional FORTIFY symbol candidates, and sanitizer
symbols by family. No observed symbols is not proof that a build lacks protection:
symbols or calls may have been stripped/optimized out. These observations do not
override the configured build mode, establish coverage, or measure runtime ASLR.
Observed sanitizer symbols in a configured release binary are a build-mode
contradiction and return code 30; supply separate ordinary and instrumented builds.
Missing symbols alone are not used to infer that a build is uninstrumented.

## Replay and generated regressions

Keep the entire run directory together. It includes source archives and hashes,
release/sanitized built trees, original suite inputs, patch diff, settings, build
logs, expected outcomes, and per-finding original/minimized cases and replay evidence.
Install the same DiffSheriff version and make the recorded runtime image ID available.
For transfer, use `docker image save --output runtime.tar IMAGE_ID` and
`docker image load --input runtime.tar` on the receiving host; the image is not
implicitly duplicated into every run directory.

```sh
python -m diffsheriff.reproduce .diffsheriff/runs/run-ID/reproducers/CASE-ID
python -m diffsheriff.reproduce .diffsheriff/runs/run-ID/reproducers/CASE-ID --check-regression
```

Normal replay returns 0 when the recorded finding repeats stably. `--check-regression`
returns 0 only when the security baseline reproduces and the patched counterpart
satisfies independent expected behavior. A still-broken functional-regression bundle
therefore does not pass that check. Errors return 30; unmatched/unstable evidence 40.
Results are written to `replay.json`; altered inputs or binaries are rejected by hash.
Replay rejects missing security identities, incomplete artifact pairs, and symlink
metadata/diff/output paths instead of reporting an empty identity as reproduced or
writing through an existing output link.
If a reduced security input has no independent expectation, its bundle records
`expected: null`. Diagnostic replay can succeed, but `--check-regression` returns 40
and `functional_expectation_available` is false. The original expectation is retained
separately; it is never applied to different reduced bytes.

Generated regression manifests and inputs are automatically inserted into the
configured regression directory. Later validator runs load those with the same
baseline commit, replay the expected baseline signature when applicable, and check
independent patched behavior. Keep these files if they are part of the delivered test
suite. Do not edit their expectations to copy patched output.
When a reduced input has no independent expectation, it is enrolled as a diagnostic
regression, and the original input keeps a separate full expectation. Missing reduced
expectations keep analysis incomplete, including on the run that creates the case.
The bundle's `regression_input` points to the minimized input; diagnostic reproduction
alone does not satisfy the full regression check. See [CI and regression handling](ci.md)
for supplying independent expectations and transferring suites between runs.

## Human delivery work

The target/provenance/approval record remains in `target_scenarios.md`. It must be
filled from actual source and instructor decisions. After real-target validation,
each contributor should explain one finding's observations, source correlation,
priority outcome, and replay, then make and test a small change in their owned
subsystem. This guide does not claim that the review has taken place.


## Retrying Docker Hub access from WSL

If the ordinary build fails at `auth.docker.io` with HTTP 403, first check direct
connectivity. A working local proxy can then be applied to that build process only.
For the Windows proxy on port 10808, WSL in NAT mode reaches the Windows host through
its default gateway, rather than WSL's own localhost:

```bash
gateway=$(ip -4 route show default | awk '{print $3; exit}')
proxy="http://$gateway:10808"
env HTTP_PROXY="$proxy" HTTPS_PROXY="$proxy" \
    http_proxy="$proxy" https_proxy="$proxy" \
    ALL_PROXY="$proxy" all_proxy="$proxy" \
    NO_PROXY=localhost,127.0.0.1,::1 no_proxy=localhost,127.0.0.1,::1 \
    docker build --progress=plain --platform linux/amd64 \
      --build-arg HTTP_PROXY="$proxy" --build-arg HTTPS_PROXY="$proxy" \
      -t diffsheriff:local -f docker/Dockerfile .
```

The proxy must already accept connections from WSL. This command does not configure
the Docker daemon or persist proxy variables in your shell. The target runner continues
to use restricted offline containers. The [retained retry](../artifacts/checkpoints/correlation-priority/retry/README.md)
records the direct HTTP 403, successful proxy-assisted build, cache use, image identity
and verification. A cached build does not establish fresh dependency acquisition.
