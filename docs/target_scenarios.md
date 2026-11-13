# Target selection and scenario record

## Current status

No course target, vulnerability, patch set, functional oracle, or expected-result
corpus is recorded as instructor-approved. `configs/example_target.yaml` is only a
schema example. `tests/fixtures/harmless/main.c` is an engineering smoke fixture,
not a course target: it safely echoes bytes and contains no vulnerability or exploit.
Synthetic sanitizer logs in unit/integration tests verify report logic only.

DiffSheriff must not grow into exploit tooling or be run against unapproved systems.
The assignment's incomplete-patch case still requires a distinct alternative test input
for an approved local target. Keep that input within the authorized lab corpus and
document its provenance and expected behavior. The approval table below must remain
pending until the team supplies real target facts and instructor confirmation.

This document becomes the authoritative project record for target facts once the team and instructor establish them. Do not duplicate mutable target facts in the README or roadmap; link here instead.

## Approval record

Complete this section only from primary upstream sources and instructor confirmation.

| Field | Target 1 | Target 2 |
| --- | --- | --- |
| Name and role | Pending | Pending |
| Real non-toy project/library? | Pending | Pending |
| Upstream source URL | Pending | Pending |
| License | Pending | Pending |
| Vulnerability identifier/source | Pending | Pending |
| Vulnerable source ref | Pending | Pending |
| Correct upstream patch ref | Pending | Pending |
| Input interface | Pending | Pending |
| Independent functional specification/tests | Pending | Pending |
| Instructor approval evidence/date | Pending | Pending |

At least one target must be a real, non-toy project or library. Both must be C/C++, buildable from source as Linux x86_64 ELF executables, and configurable without target-specific logic in DiffSheriff.

## Candidate proposals — unapproved (2026-11-13)

These are public-source research proposals for the team and instructor to review,
not approved targets or completed scenarios. No target was built or executed. The
baseline candidates below are the immediate parents of the selected upstream fixes;
their local buildability, fault reproduction, and suitability for all four scenarios
remain unverified. The approval table above intentionally remains pending.

The [source record](../artifacts/target-candidates/2026-11-13-source-records.json)
retains four verified upstream commit identities and hashes of eight inspected files.
Its [evidence notes](../artifacts/target-candidates/README.md) explain the limits.
Full commit hashes identify development snapshots, not release tags.

### Candidate 1: zlib / CVE-2018-25032

- **Role and provenance:** real C compression library, maintained in
  [madler/zlib](https://github.com/madler/zlib). The
  [upstream issue](https://github.com/madler/zlib/issues/605) and
  [fix](https://github.com/madler/zlib/commit/5c44459c3b28a9bd3283aaceab7c615f8020c531)
  describe a deflate buffer-corruption problem associated with fixed Huffman coding.
- **Candidate baseline:** `e99813dbfe9a09e33d42e8da9e550a0c4b7ff734`.
- **Upstream fix:** `5c44459c3b28a9bd3283aaceab7c615f8020c531`; its sole parent
  is the baseline above. This selects one upstream correction, not a claim that the
  snapshot has no other flaws.
- **License:** zlib license notice in the pinned
  [README](https://raw.githubusercontent.com/madler/zlib/5c44459c3b28a9bd3283aaceab7c615f8020c531/README)
  and header; retain the notice and identify altered source when packaging.
- **Build/interface evidence:** the README describes source builds and tests;
  [CMakeLists.txt](https://raw.githubusercontent.com/madler/zlib/5c44459c3b28a9bd3283aaceab7c615f8020c531/CMakeLists.txt)
  defines C library and executable targets. The inspected
  [minigzip CLI](https://raw.githubusercontent.com/madler/zlib/5c44459c3b28a9bd3283aaceab7c615f8020c531/test/minigzip.c)
  does not expose a `Z_FIXED` option. A small, separately approved C driver may be
  necessary; stock minigzip is not established as a suitable vulnerability driver.
- **Proposed independent expectations:** use [RFC 1950](https://www.rfc-editor.org/rfc/rfc1950),
  [RFC 1951](https://www.rfc-editor.org/rfc/rfc1951), and the pinned
  [API contract](https://raw.githubusercontent.com/madler/zlib/5c44459c3b28a9bd3283aaceab7c615f8020c531/zlib.h)
  to specify valid behavior. Compressed bytes are not unique: an approved independent
  decoder and known original bytes could establish semantic correctness. Neither
  patched compressor output nor a round trip through the same target is independent
  ground truth. The decoder, driver contract, inputs, and expectations are not yet
  selected or approved.

### Candidate 2: libpng / CVE-2019-7317

- **Role and provenance:** real C PNG library, maintained in
  [pnggroup/libpng](https://github.com/pnggroup/libpng). The
  [maintainer's release notice](https://www.libpng.org/pub/png/libpng.html) and
  [upstream issue](https://github.com/pnggroup/libpng/issues/275) identify a
  use-after-free in the simplified read API.
- **Candidate baseline:** `8439534daa1d3a5705ba92e653eda9251246dd61`.
- **Upstream fix:**
  [`9c0d5c77bf5bf2d7c1e11f388de40a70e0191550`](https://github.com/pnggroup/libpng/commit/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550);
  its sole parent is the baseline above. The nearby commit
  `a627bd26a375f5c41d54f90a47c838157d1bec97` concerns an ARM palette regression
  and must not be substituted for this CVE fix.
- **License:** the pinned
  [LICENSE](https://raw.githubusercontent.com/pnggroup/libpng/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550/LICENSE)
  contains PNG Reference Library License version 2 and historical notices. Some
  contributed/generated files have separate terms; check the selected driver files
  and retain their notices before redistribution.
- **Build/interface evidence:** the pinned
  [README](https://raw.githubusercontent.com/pnggroup/libpng/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550/README)
  and [CMakeLists.txt](https://raw.githubusercontent.com/pnggroup/libpng/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550/CMakeLists.txt)
  describe C builds with a required zlib dependency. The upstream
  [pngstest.c](https://raw.githubusercontent.com/pnggroup/libpng/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550/contrib/libtests/pngstest.c)
  is a candidate simplified-API executable, but a deterministic single-input
  interface and actual fault reachability still need verification after approval.
- **Proposed independent expectations:** the
  [PNG specification](https://www.w3.org/TR/2003/REC-PNG-20031110/) can support
  independently specified image dimensions and pixel values. The approved driver
  must define color conversion and metadata handling so expected results do not
  depend on incidental encoding choices or copied patched output. No image corpus,
  expected outputs, or driver contract is approved yet.

### Selection decisions still required

1. The team and instructor must accept or replace both candidates and confirm their
   independence. libpng depends on zlib: its dependency must be a separately pinned,
   suitable version held constant across libpng scenarios, never the varying zlib
   candidate from target 1. This dependency pin has not been selected.
2. Confirm the exact source pairs, licensing/redistribution requirements, proposed
   input interfaces, independent specifications, and allowed local input scope.
   Record instructor confirmation and its date in the approval table; public
   upstream citations are not approval evidence.
3. After approval, verify Linux x86_64 builds and stable sanitizer observations before
   committing to either scenario matrix. Resource requirements, incomplete-patch
   feasibility, and a legitimate functional regression remain selection risks.
   No incomplete or regression patch refs, input corpus, or acceptance results have
   been created for these candidates.

The current stage ends with these proposals for review. Roadmap step 1 remains open
until instructor approval is recorded; scenario preparation is the next stage.

## Scenario contract for each target

| Version | Required behavior | Expected overall exit |
| --- | --- | ---: |
| Vulnerable baseline | At least one memory error is reproducible and described by stable evidence. | Not evaluated alone |
| Correct patch | Target error absent within the test scope; valid functional suite passes; no other confirmed security flaw; mandatory analysis complete. | 0 |
| Incomplete patch | Original trigger is blocked, but a distinct recorded input still reaches the same underlying flaw. | 10 |
| Regression patch | Target flaw is blocked, but at least one independently valid behavior that passed on baseline fails. | 20, unless code 10 or 30 also applies |

For every version, record an exact commit/ref and ensure the source is stored or reproducibly obtainable under the delivery rules. Do not select results by branch name, file name, commit ID, or patch hash.

## Per-target evidence checklist

### Provenance and builds

- Exact upstream source and license
- Exact four source refs
- Reproducible release and instrumented build commands
- Produced binary paths and SHA-256 hashes
- Linux x86_64 ELF confirmation
- NX, PIE, RELRO, and canary evidence for ordinary binaries

### Independent functional ground truth

- Authoritative specification or upstream tests
- Instructor-approved expected outputs and exit codes
- Valid input suite
- Boundary input suite
- Invalid/malicious input suite
- Identical corresponding execution settings across versions

### Vulnerability evidence

- Original trigger and at least one distinct bypass input for the incomplete patch
- Error category and detection mechanism
- Release and instrumented observations kept separate
- Relevant stack/execution-path evidence
- Patch diff and correlation evidence
- Original and minimized inputs
- Three or more replay results and stability classification

### Regression evidence

- Valid input that succeeds on baseline
- Independent expected behavior
- Patch result demonstrating the violation
- Evidence that the result is functional, not merely an unrelated build/config failure

## Selection risks to reject early

- The target is actually a script, service-only web application, or managed runtime.
- The historical version no longer builds reproducibly in the agreed environment.
- The alleged vulnerability or patch cannot be tied to a primary upstream source.
- The trigger is unreliable or requires prohibited external infrastructure.
- Functional correctness would be inferred from the patched binary itself.
- The proposed incomplete patch merely creates a different bug instead of leaving the same flaw reachable.
- The regression scenario lacks a legitimate valid input and independent expected result.
- Licensing or redistribution prevents inclusion or reproducible acquisition for delivery.

## Defense-day validation

Before delivery, have someone outside the implementing subsystem prepare unseen patches within the agreed target domain and interface. Retain only the input configuration and observed evidence; do not add patch-specific recognition logic.
