# Real-target matrix checkpoint

Run date: 2026-11-19. The delivered six-row matrix was executed from an
isolated WSL Ubuntu checkout with Docker and the checked-in source bundles.
The focused pipeline/correlation tests passed (`140 passed`) before the run.

| Target | Correct | Incomplete | Regression |
| --- | ---: | ---: | ---: |
| target1 (zlib) | 0 / PASS | 10 / VULN_REMAINS_OR_NEW_ISSUE | 20 / FUNC_REGRESSION |
| target2 (libpng) | 0 / PASS | 10 / VULN_REMAINS_OR_NEW_ISSUE | 20 / FUNC_REGRESSION |

The retained reports and run bundles are under
`artifacts/evaluation/<target>/<variant>/`; `matrix.tsv` records the exact
exit-code agreement. Each row passed `scripts/verify_matrix_run.py`, including
baseline identity, original/minimized inputs, hashes and at least three
baseline replays for every retained reproducer.

The cached local runtime image was missing the zlib development headers even
though `docker/Dockerfile` declares `zlib1g-dev`. Target2 was rerun with a
local derived image containing those declared headers and linker symlink; this
changes no target source or project code. A fresh Docker Hub rebuild was not
available in this environment (HTTP 403), so hosted CI must still rebuild the
checked-in Dockerfile normally.

The incomplete and regression reports intentionally retain
`analysis_complete: false` where an independent expectation is not available
for every minimized diagnostic. Their scenario exit codes and required
security/functional findings are still explicit; unknown expectations remain
inconclusive rather than being invented.

## Clean-checkout CI gate

A disposable clean-room checkout cloned both source bundles, resolved all four
configured commits, passed the symbolizer/runtime preflight, and ran the exact
`validate_target.yml` CLI block for both correct configs. Both local gates
returned exit `0` with `PASS` reports. Their JSON reports and exported manifests
are retained under `ci/target1/` and `ci/target2/` here. This is a local
workflow-equivalent check; GitHub-hosted image rebuild and artifact upload were
not claimed as executed.
