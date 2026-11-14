# Retained project artifacts

These artifacts are deliberately versioned. Generated and synthetic evidence is
relevant project output; dependency caches and temporary work directories are not.
Git preserves artifact bytes without line-ending conversion so recorded hashes
remain meaningful across Windows and Linux checkouts.

The [evidence-integrity checkpoint](checkpoints/evidence-integrity/README.md) records
the repair of three stale checkpoint README hashes and adds a test that validates all
retained checkpoint manifests against exact delivered bytes.

## Native verification

- `native/native-tests.xml`: retained Linux test results, 91 tests and zero failures,
  errors, or skips. This includes the harmless native Docker smoke test.
- `native/native-validation-report.json`: the native fixture's report from that
  verification snapshot. It records 36 suite executions, functional PASS, and exit
  40 because no baseline security flaw exists in the harmless program.
- `native/cli-run/`: a separate earlier standalone CLI invocation, including its own
  `report.json`, patch diff, original source ZIPs, four built binaries/source trees,
  and input files. Its commit IDs and runtime image ID intentionally differ from
  the later verification report. Do not combine their identities or hashes.

The reports preserve the original execution paths and image IDs as provenance.
Those temporary paths need not exist on another machine, and Docker runtime images
are external dependencies. Source archives and binaries for the earlier CLI run
are retained under `native/cli-run/`. The four binaries and four archives match
the SHA-256 values in that run's report. The three retained inputs also match the
report's input hashes.

## Retaining evidence for a checkpoint

Place durable evidence under `artifacts/` and keep temporary run directories under
`.diffsheriff/`. Include the tested DiffSheriff revision, exact command, and result
with each retained test report. For a run bundle, keep the report with its own
inputs, source and build artifacts, and any reproducers it references. Record the
runtime image needed to replay it. Check that the files are visible to Git and that
recorded hashes match before handing off the checkpoint. Link the evidence from
the [roadmap](../docs/roadmap.md) once the checkpoint is accepted.

## Package

The latest verified implementation and wheel are in the
[code-audit checkpoint](checkpoints/code-audit/README.md), which fixes five reproduced
input/build-mode/replay defects and links the team's exact evaluation procedure.
The [reference-parity checkpoint](checkpoints/reference-parity/README.md) retains
per-build ELF indicators, richer console evidence, one-command verification, and a
UBSan termination fix following comparison with DNS-P1.
The [cache-import checkpoint](checkpoints/cache-import/README.md) reconciles stale
diagnostic caches against reviewed local expectations and retains CLI transfer evidence.
The [minimized-results checkpoint](checkpoints/minimized-results/README.md) adds
classification of stable minimized observations and focused synthetic reports.
The preceding [workflow checkpoint](checkpoints/workflow/README.md) covers CI integration,
regression transfer, cross-input identity, raw hardening evidence, and a retained
native CLI run. Earlier checkpoints are
[insertion correlation](checkpoints/insertion/README.md),
[minimization](checkpoints/minimization/README.md), and
[boundary classification](checkpoints/boundary/README.md). Each records its own
source hashes, commands, results, and scope; do not combine evidence from different
checkpoints.

`package/diffsheriff-0.1.0-py3-none-any.whl` is the earlier distribution built from
commit `07914aa`. The current verified implementation wheel is retained in the
[minimized-results checkpoint](checkpoints/minimized-results/README.md). The [roadmap](../docs/roadmap.md)
records what the implementation checks establish and what course work remains.
