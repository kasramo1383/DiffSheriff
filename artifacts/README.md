# Retained evidence

These are retained verification records. Current acceptance and remaining work belong
in [the roadmap](../docs/roadmap.md). The current `artifacts/evaluation/matrix.tsv` has
two rows, both marked `inconclusive_report`: Target 1 correct (exit 40) and incomplete
(exit 10). The correct report points to `evaluation/target1/correct/runs/run-76j2clt5/`;
`run-gx6_3cwa/` is an earlier, separate historical attempt. The incomplete report points
to `evaluation/target1/incomplete/runs/run-y7lh43z5/`. Neither report has
`analysis_complete: true`.

Target 1 regression has a retained console log and partial run directory, but no
finalized report or matrix row. All three Target 2 variants have no report, log, or
matrix row. Thus only two of six comparisons have report rows, one more attempt is
partial, and three variants have not been run. See F09 in the roadmap for exact
report statuses and unresolved reasons. The historical run JSONs preserve their
recorded configuration snapshots; current configs separately record the course team's
approval waiver. Generated regressions under `evaluation/` do not replace the matrix.

| Record | Purpose |
| --- | --- |
| [F03 corpus review](checkpoints/f03-corpus-review/README.md) | Selected-input/expectation review and the zlib invalid-input resolution. |
| [Build and hardening](checkpoints/build-hardening/README.md) | Selected-version builds, ELF NX/PIE/RELRO/canary observations and downgrade reporting. |
| [PNG contract](checkpoints/png-contract/README.md) | Decode-error handling, updated source versions, reviewed fixtures and native scenario checks. |
| [Zlib contract and CI setup](checkpoints/zlib-contract-ci/README.md) | Bounded zlib status/validity, native cases and fresh source-bundle setup. |
| [Correlation and priority](checkpoints/correlation-priority/README.md) | Ambiguous attribution repair and all 16 mixed-outcome CLI checks; [rebuilt-runtime retry](checkpoints/correlation-priority/retry/README.md). |
| [Reduction limits](checkpoints/reduction-limits/README.md) | Explicit reduction limits, stop reasons and synthetic/pipeline checks. |
| [Code audit](checkpoints/code-audit/README.md) | Five repaired generic input/build/replay defects, test results and a harmless native run. |
| [Evidence integrity](checkpoints/evidence-integrity/README.md) | Retained artifact hash checks and repairs. |
| [CI formatting](checkpoints/ci-format/README.md) | Formatting configuration and historical hosted generic CI results. |
| [Minimized results](checkpoints/minimized-results/README.md) | Synthetic minimized-finding classification and deduplication evidence. |
| [Cache imports](checkpoints/cache-import/README.md) | Synthetic stale/conflicting regression transfer and independent-expectation checks. |
| [Clean checkout verification](checkpoints/clean-checkout/README.md) | Fresh Python setup, harmless runtime check, standalone wheel and local CI gate. |
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
