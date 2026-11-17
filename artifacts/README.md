# Retained evidence

These are historical verification records. Current acceptance and all remaining work
belong in [the roadmap](../docs/roadmap.md). No selected-target matrix run bundle is
currently delivered here. Generated regressions under `evaluation/` do not replace one.

| Record | Purpose |
| --- | --- |
| [PNG contract](checkpoints/png-contract/README.md) | Decode-error handling, updated source versions, reviewed fixtures and native scenario checks. |
| [Zlib contract and CI setup](checkpoints/zlib-contract-ci/README.md) | Bounded zlib status/validity, native cases and fresh source-bundle setup. |
| [Correlation and priority](checkpoints/correlation-priority/README.md) | Ambiguous attribution repair and all 16 mixed-outcome CLI checks; [rebuilt-runtime retry](checkpoints/correlation-priority/retry/README.md). |
| [Reduction limits](checkpoints/reduction-limits/README.md) | Explicit reduction limits, stop reasons and synthetic/pipeline checks. |
| [Code audit](checkpoints/code-audit/README.md) | Five repaired generic input/build/replay defects, test results and a harmless native run. |
| [Evidence integrity](checkpoints/evidence-integrity/README.md) | Retained artifact hash checks and repairs. |
| [CI formatting](checkpoints/ci-format/README.md) | Formatting configuration and historical hosted generic CI results. |
| [Minimized results](checkpoints/minimized-results/README.md) | Synthetic minimized-finding classification and deduplication evidence. |
| [Cache imports](checkpoints/cache-import/README.md) | Synthetic stale/conflicting regression transfer and independent-expectation checks. |
| [Reference parity](checkpoints/reference-parity/README.md) | ELF symbol observations, UBSan termination and generic verification. |
| [Upstream provenance](target-candidates/README.md) | Original public source/parent/license research; not target acceptance. |

Each checkpoint owns its commands, source hashes, run identities, limits and manifests.
Its wheel represents that historical source, not necessarily the current implementation.
Keep separate runs separate; temporary paths in reports identify their original machine.
Replaying a complete run requires its recorded Docker image and matching tool version.

Earlier boundary, minimization, insertion and workflow checkpoints, the first native
smoke run and the top-level obsolete wheel were superseded by these later generic
records and removed from the delivery tree. Their committed versions remain in Git
history. Current source/tests retain their behavior; distinct later synthetic cases,
failed attempts and complete native bundles remain with their own manifests.

Place accepted target runs under `artifacts/evaluation/targetN/VARIANT/`, as described
in [evaluation.md](../docs/evaluation.md). Include console output, report, source/build
artifacts, inputs and reproducers together. Verify hashes before claiming acceptance.
