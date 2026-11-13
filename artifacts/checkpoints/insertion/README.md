# Insertion attribution and final defensive verification

Based on `bafe4eb` plus this checkpoint's commit. `source-sha256.json` records the
exact final Python sources, with CRLF normalized to LF, tested in Linux and installed
in the verification image. The source checkout, installed image package, and packaged
wheel were compared byte-for-byte after that normalization.

## Behavior and evidence

An insertion can now relate to a baseline runtime finding without an old edited line.
Git's hunk context must contain a simple, unambiguous function declaration matching
the exact observed function and source path, before its recorded stack location.
There must be exactly one candidate hunk, and all three baseline observations must
agree. Stable corresponding patch runs must meet independent expectations before
the finding becomes Fixed. File proximity or disappearance alone is insufficient.

The reported relation is `Insertion in observed function`, not a claim that a branch
was executed or proof of causation. Complex/overloaded declarations, absent context,
multiple candidate insertions, and changing caller evidence remain inconclusive.
Confirmed new patch diagnostics keep their separate attribution status. Existing
edited-line matches still work. Relative paths no longer alias a same-named file
in another source directory.

`red.xml` records the pre-fix checkpoint: the positive CLI insertion case and two
direct/caller correlation cases failed; 15 negative/other cases passed. `focused.xml`
records the next focused run: 76 passing pipeline and correlation cases. The final
suite additionally exercises security minimization through the real CLI/report
entry point with mocked target execution, with and without a functional reference.

- `full-windows.xml`: 133 passed, one native Docker test skipped, Python 3.13.
- `full-linux.xml`: **134 passed, no skips**, Python 3.12.3 in Ubuntu WSL. This includes
  actual Git diff generation and the actual harmless C/container fixture.
- Black: all 26 Python files passed in Linux. Windows Flake8 passed; Linux's standard
  Flake8 checks (`E,F,W,C90`) passed. Additional host-installed lint plugins initially
  reported unrelated style policies; they are not project dependencies.
- Wheel construction passed; the wheel is retained in `package/`.

The Windows run preceded only line-wrapping changes to long test strings. The Linux
run tests the exact final source hashes. Production sources did not change afterward.
The synthetic CLI matrix covers fixed, incomplete, new, functional regression,
inconclusive, unstable, hardening failure, and tool failure outcomes. It also checks
replay and loading generated regressions on a second run. Native execution is
infrastructure evidence: the echo fixture contains no vulnerability or exploit.

## Retained native run

`native/run/` contains the complete native run, with four source ZIPs and built trees,
inputs, patch diff, and JSON report. `native/config.yaml` and `native/expected.json`
retain the independently supplied fixture settings and expectations. Original run
paths and source commit IDs are preserved as provenance. Recorded input, archive,
and binary hashes were verified after copying. The report records 36 suite
executions, functional PASS, and overall INCONCLUSIVE (40), because this harmless
program cannot establish the designated security flaw.

The final image is
`sha256:ec88e772250a0af68a300f5b17eaccc37f401a6b024d2b14add921a3c071c482`.
`native/runtime-source-sha256.json` verifies its installed Python sources.
`native/build.log` retains the successful offline overlay build. The overlay in
`native/runtime.Dockerfile` reuses the previous pinned native compiler/runtime image:
`sha256:55d389e754d88b310bbbda5b12c72225ff4e0d37d4749a4be79679671ccc4e00`.
These runtime images remain external dependencies. The first fresh base-image build
could not install apt packages with networking disabled, so the existing dependency
image was reused and the current project was reinstalled without network access.

## Verification commands

The final Linux source snapshot ran from `/var/tmp/diffsheriff-final.jfUACq`, with
the workspace's cached pure-Python tools on `PYTHONPATH`. The executed test command
was equivalent to the following from a Linux checkout with project/dev dependencies:

```sh
docker tag sha256:55d389e754d88b310bbbda5b12c72225ff4e0d37d4749a4be79679671ccc4e00 diffsheriff:verification-base
docker build --network=none -t diffsheriff:verification -f artifacts/checkpoints/insertion/native/runtime.Dockerfile .
DIFFSHERIFF_DOCKER_TESTS=1 DIFFSHERIFF_TEST_IMAGE=diffsheriff:verification python3 -m pytest -q tests --basetemp=.diffsheriff/final-tests --junitxml=artifacts/checkpoints/insertion/full-linux.xml
python3 -m black --check diffsheriff tests
python3 -m flake8 --select=E,F,W,C90 diffsheriff tests
```

The actual Linux test base directory was the snapshot's `test-work/`; the XML output
was written directly to this artifact directory. To build a new runtime when the
retained base image is unavailable, use the normal `docker/Dockerfile` with package
network access during image construction. Target builds and executions remain offline.

The focused and Windows commands were:

```powershell
$env:PYTHONPATH = (Resolve-Path .diffsheriff/deps).Path
python -m pytest -q tests/test_pipeline.py tests/test_correlator.py -k insertion --basetemp=.diffsheriff/tests-insertion-red --junitxml=artifacts/checkpoints/insertion/red.xml
python -m pytest -q tests/test_pipeline.py tests/test_correlator.py --basetemp=.diffsheriff/tests-insertion-focused-final --junitxml=artifacts/checkpoints/insertion/focused.xml
python -m pytest -q tests --basetemp=.diffsheriff/tests-insertion-full --junitxml=artifacts/checkpoints/insertion/full-windows.xml
python -m flake8 --jobs=1 diffsheriff tests
$env:TEMP = (Resolve-Path .diffsheriff/tmp).Path
$env:TMP = $env:TEMP
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/insertion/package
```

The first command describes the red checkpoint; the final version now passes all
selected cases. The cached dependency and temp paths are workspace conveniences;
a clean environment can install the project dev dependencies normally.

Remaining work is approved real-target scenarios, their acceptance tests/evidence,
and the team's human defense/delivery review. This checkpoint makes no instructor
approval or real-vulnerability validation claim and includes no exploit tooling.
