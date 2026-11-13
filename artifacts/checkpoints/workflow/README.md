# Workflow and pipeline completion checkpoint

Based on `a6ecc3f5749b8f1beedc50cbbe6d9109375351ee` plus the changes in this checkpoint.
`source-sha256.json` identifies the exact Python sources, tests, workflows, and package
configuration with CRLF normalized to LF. This records implementation verification,
not team acceptance, instructor approval, or real-target vulnerability validation.

## Changed behavior

- The target CI job invokes the CLI with exact refs from its config, preserves the
  actual exit code, restores/exports regression inputs, and retains available reports
  and run bundles after either a pass or a failure. Conflicting local regression
  files and corrupt imports fail with code 30.
- Reduced security inputs without independent expectations are enrolled as diagnostic
  regressions, while the original cases keep their own expectations. Missing reduced
  expectations make analysis incomplete on the first run and subsequent runs. An
  independent reference or supplied expectation can complete the full check.
- Confirmed baseline identities are shared across inputs in the same build mode,
  independently of input order. Different modes, unstable baselines, and different
  signatures do not establish an incomplete fix. A late execution error preserves
  findings from completed cases while returning code 30.
- Hardening JSON retains the inspected flags and symbol names. A shared object's
  `ET_DYN` type alone no longer qualifies it as PIE. Dynamic flags are read through
  program headers, including in sectionless ELF fixtures.

## Verification results

- `full-windows.xml`: **151 passed, one native Docker test skipped**, Python 3.13.
- `full-linux.xml`: **152 passed, no skips**, Python 3.12.3 in Ubuntu WSL.
- Black and Flake8 passed. Both GitHub workflows passed Actionlint v1.7.12.
  `actionlint-source.json` records the official release URL and checksum verified
  before execution; the downloaded executable is a temporary tool, not a deliverable.
- The wheel in `package/` built successfully. Every packaged Python source matches
  the checkout after newline normalization; its hash is in `verification.json`.
- The installed runtime sources match both the Linux test snapshot and checkout.
  `native/runtime-source-sha256.json` and `native-verification.json` retain identities.

The tests include synthetic diagnostics through the CLI, all priority exit codes,
diagnostic regression enrollment and later expectation completion, regression transfer,
corrupt/conflicting imports, cross-input identity with mode/stability exclusions,
late runtime failures, and actual harmless C builds and execution. Synthetic cases
do not contain working vulnerabilities or establish target acceptance.

## Native evidence

`native/run/` retains the complete harmless run: four exact source archives and built
trees, inputs, diff, settings, build logs, and report. The CLI report, config, independent
echo expectations, input suites, and exact fixture Git history (`source.bundle`) are
also retained in `native/`. All four archive hashes, four binary hashes, and six case
input references were checked against the report. Original temporary execution paths
are preserved for provenance; they are not portable paths.

This run records 36 suite executions, functional PASS, and overall INCONCLUSIVE (40),
because a harmless echo fixture cannot reproduce a baseline security flaw. Both
release builds retain NX, PIE, full RELRO, canary indicators, and the raw marker data.

The final image is
`sha256:e8c4e3dd4d497a15b4973a0cd575b246538490fc80909990eb4c0411581372b5`.
`native/build.log` and `native/runtime.Dockerfile` describe the offline overlay using
the earlier compiler/runtime image
`sha256:ec88e772250a0af68a300f5b17eaccc37f401a6b024d2b14add921a3c071c482`.
Images are external dependencies. A fresh machine can build `docker/Dockerfile` as
`diffsheriff:workflow` with network access for package installation; subsequent target
builds and executions are offline.

To repeat the retained fixture, copy `native/config.yaml`, `native/expected.json`,
`native/tests/`, and `native/source.bundle` to a fresh working directory. Clone the
bundle into that directory's `repository/`, then run the CLI on the copied config.
It pins the two source commits and uses the `diffsheriff:workflow` image. Expect code
40, not a passing security verdict.

## Commands

The Windows run used the workspace's cached dev dependencies on `PYTHONPATH`, with
a short temporary path to avoid Windows path-length errors:

```powershell
python -m pytest -q tests --basetemp=.diffsheriff/gaps-windows-complete --junitxml=artifacts/checkpoints/workflow/full-windows.xml
python -m flake8 --jobs=1 diffsheriff tests
.diffsheriff/tools/actionlint.exe -color=false .github/workflows/verify_patch.yml .github/workflows/validate_target.yml
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/workflow/package
```

The Linux snapshot path is recorded in `native-verification.json`. From that snapshot,
with dependencies installed or the workspace cache on `PYTHONPATH`, verification ran:

```sh
DIFFSHERIFF_DOCKER_TESTS=1 DIFFSHERIFF_TEST_IMAGE=diffsheriff:workflow python3 -m pytest -q tests --basetemp=test-work --junitxml="$task_repo/artifacts/checkpoints/workflow/full-linux.xml"
python3 -m black --check --workers 1 diffsheriff tests
python3 -m flake8 --select=E,F,W,C90 diffsheriff tests
```

`task_repo` was the original repository path. The source identity and native image
were compared before delivery. GitHub-hosted cache/artifact service execution was
not run; workflow validation is static plus local CLI/native coverage. Approved
target matrices, hosted acceptance evidence, unseen patches, and human defense remain
as recorded in the [roadmap](../../../docs/roadmap.md).
