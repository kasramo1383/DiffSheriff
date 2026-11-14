# DNS-P1 feature comparison

This review compares [DNS-P1 / PatchGuard at
`41173bab54a3b1aa0318564799a299e6d35573ea`](https://github.com/Kiarash-Sanei/DNS-P1/tree/41173bab54a3b1aa0318564799a299e6d35573ea)
with DiffSheriff starting at `5d15a83` and the reference-parity changes linked below.
The reference was inspected as source; its scripts, samples, and tests were not run.
No third-party implementation or target assets were copied into this project.

This comparison is supplementary analysis of optional generic features. It is not an
assignment requirement, target approval, or project-status authority. The assignment
PDF remains authoritative; another repository's checklist is a comparison aid only.
Live completion status belongs only in [the roadmap](roadmap.md). Verification of the
changes from this review is in the
[reference-parity checkpoint](../artifacts/checkpoints/reference-parity/README.md).

## Required capabilities

| Capability in the reference | DiffSheriff implementation/evidence | Assessment |
| --- | --- | --- |
| Configurable C/C++ Linux x86_64 executables | `config.py`, `builder.py`, `hardening.py`; config/source/ELF tests | Implemented; ELF architecture validated. |
| Baseline/patch and Git diff | Exact source archives and hashes; `pipeline.py`, `correlator.py` | Implemented; mutable refs and plain directories intentionally excluded. |
| Separate ordinary/instrumented builds | Four pristine build trees; corresponding-mode comparisons | Implemented; ELF observations now retained for every build, not only release hardening. |
| stdin, file, argv input | `runner.py`; native test exercises all three | Implemented with DiffSheriff's fixed-argument/file-flag contract. |
| Resource-limited execution | Offline containers, read-only execution mounts, CPU/RAM/PID/output/time bounds | Implemented; retain container isolation instead of copying host-process execution. |
| Valid, boundary, invalid corpora | Exact file discovery and independent expectations; `discover_cases` | Implemented; actual approved-target corpora remain a delivery dependency. |
| Independent functional ground truth | Exact exit/stdout/stderr plus explicit validity; optional reference command | Implemented; no patched-output oracle. |
| Category, mechanism, termination | `triage.py`, raw execution records | Implemented; this review fixes UBSan's missing actual signal. Bare signals stay inconclusive. |
| Fault-site and caller-chain correlation | Actual changed lines, caller frames, conservative insertion evidence | Implemented and tested; ambiguous relations remain inconclusive. |
| Fixed / incomplete / new / regression / inconclusive | `compare_case`, tests across outcomes and priority combinations | Implemented; simulated verdict tests do not replace target matrices. |
| At least three replays and stability | Suite observations and reproducer logs | Implemented in both modes, with unstable outcomes retained. |
| Error/location-preserving reduction | `minimizer.py`, `record_reproducer` | Implemented; original and minimized inputs retained. |
| Reproducer with identity and build/run environment | Run archives, binaries, hashes, settings, logs; `reproduce.py` | Implemented; transfer the entire run and provide the pinned runtime image. |
| Automatically loaded regression tests | Generated manifests, discovery, cache transfer | Implemented; unknown reduced expectations cannot become a full passing check. |
| NX, PIE, RELRO levels, canary and downgrades | ELF parser plus comparison; native and unit checks | Implemented with raw indicators and explicit limitations. |
| Human summary, JSON, CI exit priority | `cli.py`, `reporter.py`; `30 > 10 > 20 > 40 > 0` | Implemented; console now exposes more existing evidence. |
| Hosted tool and target gates | `.github/workflows/verify_patch.yml`, `validate_target.yml` | Implemented workflow mechanics; approved-target hosted acceptance remains pending. |
| Two independent targets and scenario versions | Roadmap Stages 3-6; `target_scenarios.md` | Not delivered. Reference samples do not confer approval for this repository. |
| Unseen-patch evaluation | Generic config/evidence pipeline; roadmap Stage 9 | Capability is not proof of an actual blind evaluation; that remains pending. |
| Standalone delivery and individual defense | Usage/CI/architecture docs, wheel, evidence; roadmap Stages 8-9 | Generic material exists; final target delivery and each person's defense remain external work. |

## Additional features and intentional differences

The reference's [verification driver](https://github.com/Kiarash-Sanei/DNS-P1/blob/41173bab54a3b1aa0318564799a299e6d35573ea/verify.sh)
and [scenario driver](https://github.com/Kiarash-Sanei/DNS-P1/blob/41173bab54a3b1aa0318564799a299e6d35573ea/run_all.sh)
combine checks into a convenient entry point. DiffSheriff now provides `bash verify.sh`
for formatting, standard lint, the full suite including the harmless native matrix,
and wheel construction. It explicitly reports tool verification, not project
completion. A two-target decision table still belongs with approved scenario assets;
there is no fake target matrix or target-specific verdict branch.

The reference adds [FORTIFY/stripping metadata](https://github.com/Kiarash-Sanei/DNS-P1/blob/41173bab54a3b1aa0318564799a299e6d35573ea/patchguard/hardening.py)
and [sanitizer-symbol inspection](https://github.com/Kiarash-Sanei/DNS-P1/blob/41173bab54a3b1aa0318564799a299e6d35573ea/patchguard/buildinfo.py).
DiffSheriff now retains conventional FORTIFY symbol candidates, observed sanitizer
families/symbols, and available `.symtab`/`.dynsym` tables in every build's ELF record.
It does not infer compile flags, per-function protection, or runtime ASLR from those
indicators. Symbol loss alone does not prove a hardening downgrade: calls can be
optimized out or their symbol tables removed. The required NX/PIE/RELRO/canary
comparison keeps its existing behavior. See [glibc fortification](https://sourceware.org/glibc/manual/latest/html_node/Source-Fortification.html)
and [GCC instrumentation](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html)
for why compile-time transformations and observed symbols are different evidence.

The [reference console renderer](https://github.com/Kiarash-Sanei/DNS-P1/blob/41173bab54a3b1aa0318564799a299e6d35573ea/patchguard/report.py)
shows richer details. DiffSheriff now prints release hardening, build symbol summaries,
finding detection/correlation/stability/reason, minimized-input paths, and the retained
evidence directory. JSON remains the complete machine-readable record. Separate
`--quiet`/`--json` switches are not required for this functionality: JSON already has
an explicit output file, independent of console output.

Other representation choices do not require duplicate implementations: byte files
and exact expectations replace the reference's inline/base64/generated-input JSON;
full refs in target configuration replace branch overrides; `python -m
diffsheriff.reproduce` replaces generated shell replay scripts. Both support the
underlying tasks, with DiffSheriff's own identity and path checks.

The reference's ASLR-disabling option and host ASLR probe were not adopted. A host
sysctl is not a measurement of the target container, and changing execution security
settings merely to resemble the reference is outside this comparison's agreed scope.
Allocator text without source evidence remains a raw diagnostic/inconclusive signal,
not an inferred specific memory-error location or patch cause.

Its three-person role split and commit-author generation script were not adopted.
DiffSheriff retains the four owners in README and real contribution history. The
[study guide](defense_guide.md) provides preparation paths without asserting completed
participation or supplying live-defense answers.

## Limits of the reference's completion claim

At the inspected commit, `git ls-tree` contains no `pg_out/` reports/bundles despite
the README listing that directory as pre-generated output. The setup scripts create
local sample repositories and branches; their presence is not retained execution
evidence. We did not verify that their scenario scripts pass.

The source includes two deliberately prepared samples, but this review found no
recorded instructor approval or independently approved functional oracle for adopting
them here. A README's description of a sample as non-toy does not establish that
the instructor accepts it as the required real project/library. No repository-level
license file was found in the inspected tree; none of its code was imported.

Source inspection also shows behaviors DiffSheriff should not inherit: host-process
limits do not provide its current filesystem/network isolation; a generic clean
termination or missing symbol does not prove a security fix. The reference's generated
regression uses a no-crash expectation, whereas DiffSheriff requires independent
expected behavior for full regression acceptance. Coverage claims were therefore
mapped to actual contracts and evidence, rather than copied as completed requirements.

## Second guide review: dynAn / TEMP

The team also supplied [ta-tahmasebi/TEMP at
`e3dc7fc74e99d3f31e9d1ba206c6fd64dc57c139`](https://github.com/ta-tahmasebi/TEMP/tree/e3dc7fc74e99d3f31e9d1ba206c6fd64dc57c139).
Its own requirements matrix records one purpose-built target, no real-world target,
no demonstrated unseen-patch evaluation, and no instructor approval. Those are the
same external target-authoring and approval gaps recorded in DiffSheriff's roadmap;
copying its `confparse` fixture would not satisfy the two-target requirement.

The guide's core required behavior—dual builds, isolated execution, independent
expectations, diff correlation, replay/minimization, generated regressions, hardening,
structured reports, and exit priority—is already implemented and verified here. Its
web UI, environment doctor, optional LLM advisor, and optional fuzzing are outside the
assignment requirements and do not supply missing target evidence. No source, target,
test, or optional framework code was copied from this guide.
