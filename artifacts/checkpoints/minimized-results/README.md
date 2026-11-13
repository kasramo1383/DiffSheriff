# Stage 1: classify minimized replay results

Based on `8d6455cda831378f8c6ffb261edb36849fe9d385` plus this checkpoint's changes.
`source-sha256.json` identifies the tested production sources, tests, and package
configuration, with CRLF normalized to LF. Stage 1 is ready for review, not recorded
as accepted. Stage 2 regression-cache reconciliation has not been implemented here.

## Behavior

Stable minimized observations now enter the existing case comparison and final
verdict-priority logic. The pipeline reuses the three retained baseline and patch
observations without launching another minimization. New findings identify their
minimized input, original case, build mode, expectation, and report case index.

Results already represented by the same parent case and mode are deduplicated using
status, diagnostic signature, correlation, and explanation. Runtime addresses do not
create new identities. Newly established baseline identity can reclassify earlier
findings, followed by deduplication. A later reproducer error preserves already
collected minimized findings while operational code 30 retains priority.

Unknown expectations remain diagnostic-only and incomplete. Validity of different
reduced bytes is not inherited from the parent input: it must come from the independent
corpus or an explicit boolean `valid_input` in the independent reference result.
The existing three-field reference response remains supported; omitted validity does
not designate new bytes as a valid functional test. Invalid flag types fail closed.
See [usage](../../../docs/usage.md) for the reference contract.

## Results and scope

- `red.xml`: two pre-fix diagnostic cases returned 40 instead of 10; the new explicit
  reference-validity contract was rejected; the unchanged-result case passed.
  This is 3 failures and 1 pass before the implementation.
- `focused.xml`: 9 final focused minimized-result cases passed.
- `full-windows.xml`: **163 passed, one native Docker test skipped**, Python 3.13.
- `full-linux.xml`: **164 passed, no skips**, Python 3.12.3 in Ubuntu WSL.
- Black and Flake8 passed. Wheel construction succeeded; every packaged Python source
  matches the checkout after newline normalization.
- All final Linux test/source files match the checkout. Installed runtime sources
  match as well; `verification.json` and `native/runtime-source-sha256.json` retain
  the identities and wheel hash.

The focused cases cover remaining and distinct minimized patch diagnostics, explicit
validity versus false/omitted validity, runtime-address deduplication, baseline-identity
reclassification, and retaining minimized results after a later operational failure.
The full suite also preserves ordinary code-20 regression behavior and all existing
exit priorities, replay, generated-regression, and container checks.

## Retained evidence

`synthetic/` contains five inspected report/run bundles, test configs and inputs, and
generated manifests from the final focused run. Its `observed-results.json` records:

| Case | Exit | Evidence |
| --- | ---: | --- |
| Remaining diagnostic | 10 | Minimized incomplete-fix finding; missing expectation stays inconclusive |
| Distinct diagnostic | 10 | Minimized new finding; missing expectation stays inconclusive |
| Functional regression | 10 | Functional FAIL and security FAIL; security retains priority |
| Unchanged result | 0 | One Fixed finding and no duplicate minimized case record |
| Later reproducer failure | 30 | Minimized security finding retained; operational error retains priority |

These are synthetic diagnostics and fake build files produced by mocked tests, not
executable target evidence. Their placeholder image/source identities cannot be used
to replay them outside the test harness. Both original/minimized bytes, observation
logs, expectations, validity flags, and case-index references were inspected.

`native/` separately retains the actual harmless CLI run, four source archives and
binaries, original inputs, configuration, expectations, and fixture Git history in
`source.bundle`. Its report has 36 suite executions, functional PASS, and exit 40
because the echo fixture has no security flaw. Archive, binary, and input hashes match
the report. Original temporary paths are retained for provenance, not portability.

The native image is
`sha256:dca15002993f7f4997c27d10e4abd5b7ebbddfa0ca632b28cf9968820ada1189`.
The offline overlay in `native/runtime.Dockerfile` uses the preceding workflow image
`sha256:e8c4e3dd4d497a15b4973a0cd575b246538490fc80909990eb4c0411581372b5`.
Images are external dependencies. A fresh machine can build `docker/Dockerfile` as
`diffsheriff:minimized-results` with network access for package installation. For the
retained native fixture, copy its config, expectations, input tests, and source bundle
to a fresh directory, clone the bundle into `repository/`, and run the CLI on that
config. The expected harmless verdict remains 40.

## Commands

Windows used cached dev dependencies on `PYTHONPATH` and short workspace temp paths:

```powershell
python -m pytest -q tests/test_pipeline.py -k 'minimized_patch_diagnostic or minimized_known_valid or minimized_unchanged' --basetemp=.diffsheriff/min-results-red --junitxml=artifacts/checkpoints/minimized-results/red.xml
python -m pytest -q tests/test_pipeline.py -k minimized --basetemp=.diffsheriff/min-results-final-focused --junitxml=artifacts/checkpoints/minimized-results/focused.xml
python -m pytest -q tests --basetemp=.diffsheriff/min-results-final-windows --junitxml=artifacts/checkpoints/minimized-results/full-windows.xml
python -m flake8 --jobs=1 diffsheriff tests
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/minimized-results/package
```

The red command describes the pre-fix checkpoint. Linux used the final snapshot path
recorded in `verification.json`, with dependencies available through `PYTHONPATH`:

```sh
DIFFSHERIFF_DOCKER_TESTS=1 DIFFSHERIFF_TEST_IMAGE=diffsheriff:minimized-results python3 -m pytest -q tests --basetemp=test-work --junitxml="$task_repo/artifacts/checkpoints/minimized-results/full-linux.xml"
python3 -m black --check --workers 1 diffsheriff tests
python3 -m flake8 --select=E,F,W,C90 diffsheriff tests
```

`task_repo` was the original repository path. No hosted CI or approved real-target
acceptance was run. The [roadmap](../../../docs/roadmap.md) requires review of this
stage before Stage 2; target approval and target-dependent delivery remain separate.
