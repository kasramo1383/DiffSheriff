# Explicit minimization limits and outcomes

This checkpoint implements roadmap F06 on parent revision `dde70b6`. It verifies the
generic minimizer and pipeline with synthetic cases and a harmless native fixture.
It is not selected-target acceptance; target references, corpora and matrices remain
subject to the other fixes in [the roadmap](../../../docs/roadmap.md).

## Behavior

`minimization.max_granularity` defaults to 16 and `max_oracle_calls` to 256. Each
accepts null to disable that limit. Configuration rejects unknown settings, booleans,
non-integers and values below the supported minimum. Existing configs use the defaults.
The granularity cap is respected even when it is not a power of two.

The structured `minimize` result retains original/reduced sizes, whether reduction
occurred, stop reason, candidate-evaluation count and both limits. The byte-returning
`ddmin` helper remains compatible. Reproducer metadata and report JSON preserve the
same summary. A limit stop keeps the last preserving payload. The final three replays
per version are separate from the search budget; an initial failed reduction check
retains original bytes and cannot establish stable reproduction. Unknown functional
expectations and changed error/location/limit outcomes retain their existing rules.

The [usage guide](../../../docs/usage.md#reduction-limits-and-retained-outcomes)
defines every stop reason and configuration option. No global-minimum claim is made.

## Evidence

- `synthetic-reduction.json`: exact 64-byte synthetic input and invariant. The default
  cap stops unchanged after 62 evaluations; expanded search removes the dispensable
  byte, reaching 63 bytes after 350 evaluations; a budget of three stops explicitly.
  This is a pure byte predicate, not a vulnerability or native-target experiment.
- `focused.xml`: minimizer/config/pipeline cases, including limits, exact completion
  on the final allowed evaluation, invalid settings, unchanged/empty outcomes, report
  and metadata consistency, instability, and final replay preservation.
- `full-linux.xml` and `verify-linux.log`: final generic verification, including the
  harmless native Docker matrix, formatting, lint and package creation.
- `build.log`: runtime rebuilt from the tested source.
- `package/`: wheel produced by verification; install/import checked outside the repo.
- `verification.json`: exact commands, results, runtime identities and package check.
- `source-sha256.json`: tested source/config/test hashes, normalized CRLF to LF.
- `artifact-sha256.json`: exact retained artifact bytes, excluding the manifest itself.

The initial focused run had 135 passes and one failed test assertion: a seven-call
budget finished successfully on call seven, while the test expected a limit stop.
The assertion was corrected and a separate exact-boundary completion test added.
The implementation correctly distinguishes completion from budget exhaustion.

Reproduce on Linux/WSL from the project root with declared development dependencies:

```sh
python3 -m pytest -q tests/test_minimizer.py tests/test_config.py tests/test_pipeline.py
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
bash verify.sh
```

Keep the recorded image/source identities when interpreting these observations.
Future source changes require their own verification; this checkpoint proves no
instructor approval, real-target functional correctness or student defense result.
