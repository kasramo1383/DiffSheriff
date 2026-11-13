# Preparing to explain DiffSheriff

Use this guide for study before the individual defense. It records no attendance,
authorship, instructor approval, or completed defense. The four named owners and
student IDs are maintained only in [README](../README.md#contributors-and-engineering-ownership).
Current delivery gates are in [the roadmap](roadmap.md).

Start with [architecture](architecture.md), run the [verification command](usage.md),
then trace one retained report from inputs and source hashes through observations,
findings, priority, and replay. Distinguish synthetic diagnostic fixtures from native
execution evidence and approved-target evidence. Do not describe a harmless native
code-40 result as a successful security fix.

| Role | Read and trace | Relevant checks | Practice task before defense |
| --- | --- | --- | --- |
| Engineer 1: build/execution | `builder.py`, `runner.py`, `hardening.py`; source archives, four build records, image identity | `test_builder.py`, `test_sources.py`, `test_runner.py`, `test_container.py`, `test_hardening.py`, native integration | Explain a timeout/output limit versus a crash, and how equivalent limits and pristine builds avoid misleading comparisons. Make a small limits/config validation change and exercise its failure path. |
| Engineer 2: triage/correlation | `triage.py`, `correlator.py`, `compare_case`; stack, exact diff edits, signatures | `test_triage.py`, `test_correlator.py`, correlation cases in `test_pipeline.py` | Trace a changed-caller finding and an inconclusive relation. Explain why a new observation is not automatically caused by the patch. Add one synthetic parser edge case with a test. |
| Engineer 3: replay/regression | `minimizer.py`, `reproduce.py`, `regressions.py`, `record_reproducer`; original/reduced bytes and logs | `test_minimizer.py`, `test_regressions.py`, replay/minimization cases in `test_pipeline.py` | Explain the reduction invariant, three-run stability, unknown expectations, and stale-cache precedence. Exercise a hash mismatch without modifying retained evidence. |
| Engineer 4: integration/targets | `config.py`, `pipeline.py`, `cli.py`, `reporter.py`, workflows; config-to-exit flow | `test_config.py`, `test_cli.py`, `test_reporter.py`, `test_pipeline.py` | Explain mixed outcomes and priority while retaining independent statuses. Trace how an approved config reaches the target workflow and why a skipped target job is not acceptance. |

For a finding, locate its case index, mode, input hash, source/binary identities,
observations, detection mechanism, actual termination, correlation, and reason. Check
whether its minimized input has an independent expectation. Explain both what the
evidence supports and what remains unknown. Keep the entire run directory together
when demonstrating replay; synthetic bundles with placeholder images are not native
replay demonstrations.

The actual defense and live change are each student's independent work without other
students or generative assistance. Practice changes are preparation, not evidence
that the person has already passed or contributed a particular implementation.
