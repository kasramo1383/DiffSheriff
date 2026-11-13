# Architecture

The pipeline is explicit and flat:

```text
CLI -> validated config -> independent suite + expected results
    -> exact source snapshots -> base/patch x release/sanitized builds
    -> ELF checks -> isolated executions + three replays
    -> triage + source signatures + actual diff edits
    -> corresponding-mode comparison -> reduction + retained reproducers
    -> generated regressions -> JSON + readable summary + prioritized exit
```

Requirements come from `course_assignment.pdf` and its working English digest in
`specification.md`. Implementation progress and verification limits are maintained
only in `roadmap.md`.

| Module | Responsibility |
| --- | --- |
| `config.py` | Version 2 schema and path/type/ref validation |
| `builder.py` | Exact Git archives, pristine build trees, logs, and binary hashes |
| `runner.py` | Bounded process capture, restricted Docker lifecycle, input delivery, and signal-preserving supervisor |
| `pipeline.py` | Independent expectations, discovery, corresponding-mode comparison, replay/minimization, and regression insertion |
| `triage.py` | Detection mechanisms, categories, real signal status, and runtime frames |
| `correlator.py` | Old/new changed lines, insertion-to-runtime-function evidence, caller evidence, and normalized source signatures |
| `minimizer.py` | Delta debugging against a strict caller-supplied invariant |
| `hardening.py` | x86_64 ELF validation, NX/PIE/RELRO/canary comparison, and per-build symbol evidence |
| `reproduce.py` | Re-execution of retained cases, including hash verification |
| `regressions.py` | Baseline-filtered regression import/export with hash and conflict checks |
| `reporter.py` | Independent statuses, JSON evidence, atomic report replacement, and exit priority |
| `cli.py` | Configuration, pipeline invocation, developer summary, and operation errors |

## Invariants

1. A passing verdict requires the designated baseline signature, stable replays,
   expected patched behavior, sufficient correlation, and completed mandatory checks.
2. Release is compared only to release; sanitized only to sanitized. Source versions
   have separate build directories, and every mode starts from a fresh archive.
3. All corresponding executions share inputs, pinned image identity, environment,
   input delivery, timeout, and resource limits. Targets cannot modify suite files.
4. Expectations come from the independently supplied JSON manifest or optional
   reference command, never from baseline or patched output.
5. Nonzero exits and bare signals are not confirmed security identities. Generic or
   source-less diagnostics remain inconclusive. Source lines are normalized across
   unchanged diff ranges; ambiguous mappings retain their patch coordinate.
6. Actual changed-line intersection, outer runtime frames, and unambiguous insertions
   in observed baseline functions are evidence of relation, not proof of causation.
   Insertion matches must agree across baseline replays before a fixed verdict.
   Unattributed confirmed patch diagnostics retain code 10 while analysis completeness
   remains false.
7. Input reduction preserves the same diagnostic/location or independent functional
   mismatch and checks three executions. Unknown reduced-input behavior is not inferred.
8. Build/config/runtime/tool failure takes precedence over other exit conditions;
   already collected independent evidence remains in JSON.

## Isolation and artifacts

DiffSheriff runs on the host and launches a new Docker container for each build step,
execution, or reference invocation. Only a disposable snapshot is writable during
builds; target execution mounts it read-only. Network, capabilities, and privilege
gain are disabled. Containers have CPU, RAM, PID, temporary-storage, and output
bounds. The container supervisor records actual child signals and kills its process
group on a timeout; the host removes the container even after a client failure.
Configured commands and the selected image are trusted operator inputs.

Each `.diffsheriff/runs/run-*` directory contains original source archives, four
built source trees, inputs, diff, report, and per-finding reproducer records. Keep the
whole directory together: reproducer records refer to shared artifacts using relative
paths. The runtime image is pinned by its inspected ID and must remain available.
Generated regression inputs/manifests live at the configured regression directory
and are consumed only for the matching exact baseline. They are derived evidence,
not new functional ground truth.

See `usage.md` for the configuration and replay contract. Target-specific behavior
belongs in target assets and configuration, never branches in the validator.
