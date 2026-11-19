# Real-target matrix checkpoint

Run date: 2026-11-19. The delivered six-row matrix was executed from an
isolated WSL Ubuntu checkout with Docker and the checked-in source bundles.
The focused pipeline/correlation tests passed (`140 passed`) before the run.

| Target | Correct | Incomplete | Regression |
| --- | ---: | ---: | ---: |
| target1 (zlib) | 0 / PASS | 10 / VULN_REMAINS_OR_NEW_ISSUE | 20 / FUNC_REGRESSION |
| target2 (libpng) | 0 / PASS | 10 / VULN_REMAINS_OR_NEW_ISSUE | 20 / FUNC_REGRESSION |

## Current report analysis status

The root reports under each target/variant directory are the current reports. Earlier
reports remain under their `runs/` directories as historical attempts. Current report
summaries:

| Variant | Tests | Analysis | Security | Functional | Findings | Incomplete reason(s) |
| --- | ---: | --- | --- | --- | --- | --- |
| target1 / correct | 144 | Complete | PASS | PASS | Fixed: 6 | None |
| target1 / incomplete | 144 | Incomplete | FAIL | INCONCLUSIVE | Incomplete Fix: 2; Inconclusive: 8 | `fix_evidence_insufficient`; `patch_attribution_unestablished` |
| target1 / regression | 144 | Complete | PASS | FAIL | Functional Regression: 6; Fixed: 6 | None |
| target2 / correct | 48 | Complete | PASS | PASS | Fixed: 4 | None |
| target2 / incomplete | 60 | Incomplete | FAIL | PASS | Fixed: 5; Incomplete Fix: 1; Inconclusive: 1 | `functional_expectation_missing` |
| target2 / regression | 78 | Incomplete | INCONCLUSIVE | FAIL | Functional Regression: 1; Fixed: 7; Inconclusive: 2 | `fix_evidence_insufficient`; `functional_expectation_unmet_on_patch`; `functional_expectation_missing` |

The matrix TSV and structural verifier establish process/report exit agreement and
required evidence structure; they do not establish that every finding has a conclusive
classification. Target 1 incomplete has two `Incomplete Fix` findings but eight
inconclusive findings because patch attribution is not established. Target 2 incomplete
has one inconclusive minimized input (`minimized/0727fdc603dd5477790e`) derived from the
bypass PNG and no independent functional expectation. Target 2 regression has one
confirmed functional regression, two inconclusive findings, and a reduced input without
an independent expectation
(`regression/aa623b9c6c003303387bbd289e02da44fa7ee81b3be80d11a312c7bd9b16874f`).
These remain disclosed analytical limitations. Do not convert unknown expectations into
inferred pass/fail results.

The retained reports and run bundles are under
`artifacts/evaluation/<target>/<variant>/`; `matrix.tsv` records the exact
exit-code agreement. Each row passed `scripts/verify_matrix_run.py`, including
baseline identity, original/minimized inputs, hashes and at least three
baseline replays for every retained reproducer.

The cached local runtime image was missing the zlib development headers even
though `docker/Dockerfile` declares `zlib1g-dev`. Target2 was rerun with a
local derived image containing those declared headers and linker symlink; this
changes no target source or project code. A fresh Docker Hub rebuild was not
available in this environment (HTTP 403). A hosted run may additionally verify the
checked-in Dockerfile rebuild and normal artifact upload; that optional external check
has not been represented as completed.

Some incomplete and regression reports retain `analysis_complete: false` due to the
specific reasons in the table above. Their scenario-level process exits match the
expected codes; this does not imply all security/functional findings are conclusive.

## Clean-checkout CI gate

A disposable clean-room checkout cloned both source bundles, resolved all four
configured commits, passed the symbolizer/runtime preflight, and ran the exact
`validate_target.yml` CLI block for both correct configs. Both local gates
returned exit `0` with `PASS` reports. Their JSON reports and exported manifests
are retained under `ci/target1/` and `ci/target2/` here. This is a local
workflow-equivalent check; GitHub-hosted image rebuild and artifact upload were
not claimed as executed.
