# Retained evidence

This index describes the current retained evidence. The [roadmap](../docs/roadmap.md)
owns requirement status, and the [target-matrix checkpoint](checkpoints/target-matrix/README.md)
owns the six target runs, their detailed outcomes, and environment caveats.

`evaluation/matrix.tsv` contains all six expected rows. Each process exit code matches
its configured scenario outcome, and each row passed `scripts/verify_matrix_run.py`.
That verifier checks report/run structure and selected evidence invariants; it does not
prove that every finding is conclusive. The correct variants are complete `PASS` reports.
The incomplete and regression variants have the following retained report states:

| Report | Exit / verdict | Analysis | Remaining diagnostic |
| --- | --- | --- | --- |
| target1 / incomplete | 10 / `VULN_REMAINS_OR_NEW_ISSUE` | Incomplete | `fix_evidence_insufficient`; `patch_attribution_unestablished` |
| target2 / incomplete | 10 / `VULN_REMAINS_OR_NEW_ISSUE` | Incomplete | `functional_expectation_missing` |
| target2 / regression | 20 / `FUNC_REGRESSION` | Incomplete | `fix_evidence_insufficient`; `functional_expectation_unmet_on_patch`; `functional_expectation_missing` |

These are scenario-level outcomes, not a claim that every finding was classified.
Keep inconclusive findings and their independent-expectation gaps visible. The earlier
Target 1 correct reports with exit 40 remain under their original run directories as
historical attempts; the current root report is exit 0 / `PASS`.

| Record | Purpose |
| --- | --- |
| [F03 corpus review](checkpoints/f03-corpus-review/README.md) | Selected-input/expectation review and the zlib invalid-input resolution. |
| [Build and hardening](checkpoints/build-hardening/README.md) | Selected-version builds, ELF NX/PIE/RELRO/canary observations and downgrade reporting. |
| [PNG contract](checkpoints/png-contract/README.md) | Decode-error handling, updated source versions, reviewed fixtures and native scenario checks. |
| [Zlib contract and CI setup](checkpoints/zlib-contract-ci/README.md) | Bounded zlib status/validity, native cases and fresh source-bundle setup. |
| [Correlation and priority](checkpoints/correlation-priority/README.md) | Attribution limits and all 16 mixed-outcome CLI checks; [rebuilt-runtime retry](checkpoints/correlation-priority/retry/README.md). |
| [Reduction limits](checkpoints/reduction-limits/README.md) | Explicit reduction limits, stop reasons and synthetic/pipeline checks. |
| [Code audit](checkpoints/code-audit/README.md) | Repaired generic input/build/replay defects, test results and a harmless native run. |
| [Evidence integrity](checkpoints/evidence-integrity/README.md) | Retained artifact hash checks and repairs. |
| [CI formatting](checkpoints/ci-format/README.md) | Formatting configuration and historical hosted generic CI results. |
| [Minimized results](checkpoints/minimized-results/README.md) | Synthetic minimized-finding classification and deduplication evidence. |
| [Cache imports](checkpoints/cache-import/README.md) | Synthetic stale/conflicting regression transfer and independent-expectation checks. |
| [Clean checkout verification](checkpoints/clean-checkout/README.md) | Fresh Python setup, harmless runtime check, standalone wheel and local CI gate. |
| [Reference parity](checkpoints/reference-parity/README.md) | ELF symbol observations, UBSan termination and generic verification. |
| [Target matrix](checkpoints/target-matrix/README.md) | Six real-target comparisons and local clean-checkout CI-equivalent results. |
| [Upstream provenance](target-candidates/README.md) | Original public source/parent/license research; not target acceptance. |

Each checkpoint owns its commands, source hashes, run identities, limits and manifests.
Its wheel represents that historical source, not necessarily the current implementation.
Keep separate runs separate; temporary paths in reports identify their original machine.
Replaying a complete run requires its recorded Docker image and matching tool version.

Earlier boundary, minimization, insertion and workflow checkpoints, the first native
smoke run and the top-level obsolete wheel were superseded by later records and removed
from the delivery tree. Their committed versions remain in Git history. Current
source/tests retain their behavior; distinct later synthetic cases, failed attempts and
complete native bundles remain with their own manifests.

Accepted target runs live under `artifacts/evaluation/targetN/VARIANT/`, as described
in [evaluation.md](../docs/evaluation.md). Each includes console output, report,
source/build artifacts, inputs and reproducers. Verify hashes before claiming acceptance.
