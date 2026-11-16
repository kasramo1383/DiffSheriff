# Target selection and scenario record

## Current status

Stages 3, 4, 5, and 6 are COMPLETE. Two real, non-toy C libraries have been
selected, packaged into standalone git bundles (`source.bundle`), configured with
independent test suites and specifications, and evaluated across all six scenario
matrices with exact exit codes matching the priority hierarchy:
`30 (BUILD_ERROR) > 10 (VULN) > 20 (REGRESSION) > 40 (INCONCLUSIVE) > 0 (PASS)`.

- Target 1: `zlib` (v1.2.11 snapshot) for CVE-2018-25032.
  - `correct.yaml` -> Exit **0** (`PASS`), 120 suite executions, Security: PASS, Functional: PASS.
  - `incomplete.yaml` -> Exit **10** (`VULN_REMAINS_OR_NEW_ISSUE`), `cve_2018_25032_bypass.input` confirmed and minimized.
  - `regression.yaml` -> Exit **20** (`FUNC_REGRESSION`), `valid_large.txt` functional regression minimized via ddmin to 1,001 bytes.
- Target 2: `libpng` (v1.6.36 snapshot) for CVE-2019-7317.
  - `correct.yaml` -> Exit **0** (`PASS`), 60 suite executions, Security: PASS, Functional: PASS.
  - `incomplete.yaml` -> Exit **10** (`VULN_REMAINS_OR_NEW_ISSUE`), `cve_2019_7317_bypass.png` confirmed and minimized.
  - `regression.yaml` -> Exit **20** (`FUNC_REGRESSION`), 72 suite executions, `valid.png` functional regression on patch confirmed and minimized.

Dependency isolation is enforced: Target 2 dynamically links a pinned system zlib (`-lz`),
ensuring complete independence from Target 1. Deterministic C drivers (`zlib_driver.c` and
`png_driver.c`) adapt public library APIs to `--file <path>` CLI interfaces without
target-specific verdict logic.

DiffSheriff must not grow into exploit tooling or be run against external systems.
The assignment's incomplete-patch case still requires a distinct safe local test input
for a selected target. Keep that input within the recorded corpus and document its
provenance and expected behavior.

This document is the authoritative project record for target facts and selection
decisions. Do not duplicate mutable target facts in the README or roadmap; link here.

## Selection record

Completed from primary upstream sources and retained local feasibility evidence.
The project owner has authorized the implementing agent to determine the target pair and
test scope. This is not evidence of instructor approval; if the PDF requires that, record
the evidence as unavailable without blocking the requested repository implementation.

| Field | Target 1 | Target 2 |
| --- | --- | --- |
| Name and role | zlib (v1.2.11 snapshot): ubiquitous general-purpose DEFLATE compression library | libpng (v1.6.36 snapshot): official PNG reference graphics library |
| Real non-toy project/library? | Yes (standard Linux / cross-platform compression foundation) | Yes (standard PNG reference library used across OSs and browsers) |
| Upstream source URL | https://github.com/madler/zlib | https://github.com/pnggroup/libpng |
| License | zlib License (permissive, GPL-compatible; notice retained) | PNG Reference Library License version 2 (permissive, OSI-approved) |
| Vulnerability identifier/source | CVE-2018-25032 (upstream issue #605): buffer overflow in fixed Huffman deflate | CVE-2019-7317 (upstream issue #275): use-after-free in simplified read API |
| Vulnerable source ref | `e99813dbfe9a09e33d42e8da9e550a0c4b7ff734` | `8439534daa1d3a5705ba92e653eda9251246dd61` |
| Correct upstream patch ref | `5c44459c3b28a9bd3283aaceab7c615f8020c531` (sole parent: baseline) | `9c0d5c77bf5bf2d7c1e11f388de40a70e0191550` (sole parent: baseline) |
| Input interface | CLI driver `targets/target1/driver/zlib_driver.c` via `--file <path>` (`deflateInit2`, `Z_FIXED`, `memLevel=1`) | CLI driver `targets/target2/driver/png_driver.c` via `--file <path>` (`png_image_begin_read_from_file`, `png_image_free`) |
| Baseline ASan signature | `trees.c:1093` (`compress_block` reading `_dist_code`, `global-buffer-overflow`) | `pngerror.c:954` (`png_safe_execute` in `png_image_free_function`, `stack-use-after-return`) |
| Independent functional specification/tests | RFC 1950, RFC 1951 (DEFLATE format), independent system decompressor validation | W3C PNG Specification (ISO/IEC 15948), standard PNG test suites (`pngtest.png`) |
| Project selection rationale/date | Selected 2026-11-15 by implementing agent under project-owner authorization | Selected 2026-11-15 by implementing agent under project-owner authorization |
| Instructor approval evidence, if any | Unavailable (authorized by project owner; external instructor review pending) | Unavailable (authorized by project owner; external instructor review pending) |

At least one target must be a real, non-toy project or library. Both must be C/C++, buildable from source as Linux x86_64 ELF executables, and configurable without target-specific logic in DiffSheriff.

## Selected targets and feasibility verification (2026-11-15)

Both candidate proposals were verified in local Ubuntu WSL 2 Linux x86_64 environments,
satisfying the project's selection and feasibility criteria.

The [source record](../artifacts/target-candidates/2026-11-13-source-records.json)
retains four verified upstream commit identities and hashes of eight inspected files.
Its [evidence notes](../artifacts/target-candidates/README.md) explain the limits.
Full commit hashes identify development snapshots, not release tags.

### Target 1: zlib / CVE-2018-25032

- **Role and provenance:** real C compression library, maintained in
  [madler/zlib](https://github.com/madler/zlib). The
  [upstream issue](https://github.com/madler/zlib/issues/605) and
  [fix](https://github.com/madler/zlib/commit/5c44459c3b28a9bd3283aaceab7c615f8020c531)
  describe a deflate buffer-corruption problem associated with fixed Huffman coding.
- **Baseline:** `e99813dbfe9a09e33d42e8da9e550a0c4b7ff734`.
- **Upstream fix:** `5c44459c3b28a9bd3283aaceab7c615f8020c531`; its sole parent
  is the baseline above.
- **License:** zlib license notice in the pinned
  [README](https://raw.githubusercontent.com/madler/zlib/5c44459c3b28a9bd3283aaceab7c615f8020c531/README)
  and headers; retain the notice and identify altered source when packaging.
- **Deterministic Driver:** [targets/target1/driver/zlib_driver.c](../targets/target1/driver/zlib_driver.c).
  Exposes `--file <path>`. Streams file contents into `deflateInit2(&strm, Z_DEFAULT_COMPRESSION, Z_DEFLATED, 15, 1, Z_FIXED)`.
  With `memLevel=1`, `lit_bufsize` is constrained to 128 bytes (`pending_buf` 512 bytes), allowing
  distant matches in fixed Huffman blocks to exceed buffer bounds without being suppressed by `TOO_FAR`.
- **Corpus & Verification Evidence:**
  - `targets/target1/corpus/cve_2018_25032.input`: 32,768-byte de Bruijn sequence reproducing the buffer overrun.
  - `targets/target1/corpus/valid_small.txt` & `targets/target1/corpus/valid_large.txt`: valid test streams.
  - **ASan Execution on Baseline (`e99813dbfe9a`):** Exit code **1**. Crashes with:
    `AddressSanitizer: global-buffer-overflow` reading past `_dist_code[512]` at `trees.c:1093:20` in `compress_block`.
    Parsed triage signature: `{'error_type': 'global-buffer-overflow', 'file': 'trees.c', 'function': 'compress_block', 'line': 1093}`.
  - **ASan Execution on Fix (`5c44459c3b28`):** Exit code **0** on `cve_2018_25032.input`, `valid_small.txt`, and `valid_large.txt`.
- **Independent specifications:** [RFC 1950](https://www.rfc-editor.org/rfc/rfc1950),
  [RFC 1951](https://www.rfc-editor.org/rfc/rfc1951), and independent zlib/inflate decompression verification.

### Target 2: libpng / CVE-2019-7317

- **Role and provenance:** real C PNG library, maintained in
  [pnggroup/libpng](https://github.com/pnggroup/libpng). The
  [maintainer's release notice](https://www.libpng.org/pub/png/libpng.html) and
  [upstream issue](https://github.com/pnggroup/libpng/issues/275) identify a
  use-after-free in the simplified read API.
- **Baseline:** `8439534daa1d3a5705ba92e653eda9251246dd61`.
- **Upstream fix:**
  [`9c0d5c77bf5bf2d7c1e11f388de40a70e0191550`](https://github.com/pnggroup/libpng/commit/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550);
  its sole parent is the baseline above.
- **License:** the pinned
  [LICENSE](https://raw.githubusercontent.com/pnggroup/libpng/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550/LICENSE)
  contains PNG Reference Library License version 2.
- **Deterministic Driver:** [targets/target2/driver/png_driver.c](../targets/target2/driver/png_driver.c).
  Exposes `--file <path>`. Invokes `png_image_begin_read_from_file`, `png_image_finish_read`, and `png_image_free`.
- **Corpus & Verification Evidence:**
  - `targets/target2/corpus/cve_2019_7317.png`: crafted malformed PNG triggering simplified API cleanup path.
  - `targets/target2/corpus/valid.png`: standard valid PNG.
  - **ASan Execution on Baseline (`8439534daa1d`):** Exit code **1**. Crashes with:
    `AddressSanitizer: stack-use-after-return` in `png_safe_execute` at `pngerror.c:954:29` inside `png_image_free_function` (stack frame `c` in `png.c:4523`).
    Parsed triage signature: `{'error_type': 'stack-use-after-return', 'file': 'pngerror.c', 'function': 'png_safe_execute', 'line': 954}`.
  - **ASan Execution on Fix (`9c0d5c77bf5b`):** Exit code **0** on `cve_2019_7317.png` and `valid.png`.
- **Dependency Isolation:** libpng dynamically links against a pinned system zlib (`-lz`, Ubuntu package `zlib1g-dev`),
  held constant across all libpng scenarios. It does not share or link against Target 1's experimental zlib tree.
- **Independent specifications:** [W3C PNG Specification](https://www.w3.org/TR/2003/REC-PNG-20031110/)
  (ISO/IEC 15948) and standard independent PNG test suites (`pngtest.png`).

### Feasibility decisions resolved

1. **Target Independence:** Confirmed. libpng dynamically links against pinned system zlib (`-lz`), held strictly constant across all libpng versions.
2. **Deterministic Interfaces:** Minimal drivers (`zlib_driver.c` and `png_driver.c`) provide uniform `--file <path>` CLI options without any target-specific verdict logic.
3. **Reproducibility & Sanitizer Evidence:** Linux x86_64 builds compiled with clang AddressSanitizer reliably reproduce documented flaws on baselines and cleanly pass on upstream fixes.
4. **Stages 4, 5, and 6 Completed:** All eight scenario versions are packaged in `targets/target1/source.bundle` and `targets/target2/source.bundle`. Independent expectation manifests (`suites/expected.json` and `reference.py`) and evaluation configs (`evaluation/target1/*.yaml` and `evaluation/target2/*.yaml`) are verified. Full evaluations confirmed exact exit codes (0, 10, 20) matching the priority hierarchy.

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
- Independently sourced expected outputs and exit codes
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
