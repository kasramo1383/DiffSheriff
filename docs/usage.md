# Running DiffSheriff

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

## Configure an authorized target

Copy `configs/example_target.yaml` beside independently maintained test assets.
Schema version `2.0` replaces the original scaffold schema; old files fail with code
30 instead of silently running a partial analysis.

- `target.repository_path` is a local Git repository. `base_ref` and `patch_ref` must
  be full commit hashes. The checkout, including uncommitted files, is untouched.
- `target.baseline_signature` specifies `error_type`, repository-relative `file`,
  `function`, and baseline `line`. Match the actual symbolized diagnostic. Compile
  diagnostic builds with `-g -fno-omit-frame-pointer` and sanitizer support.
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
- Hardening minima are policy requirements. A missing minimum or a downgrade warns
  and prevents PASS, even when other checks succeed.

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

The report identifies its run directory. `total_tests_run` counts suite executions
(including their three repetitions); additional minimization and reproducer executions
are recorded in the corresponding replay logs. stdout/stderr are bounded per stream;
exceeding a bound prevents a passing result.

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
