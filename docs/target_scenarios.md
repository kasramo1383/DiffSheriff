# Target source and scenario record

[The roadmap](roadmap.md) owns acceptance status and requirement gaps. This record
owns target identities, construction and input locations. Instructor approval evidence
has not been supplied. The bounded zlib completion/status contract is documented
below; the native-format PNG completion/rejection contract is recorded at the end.
Neither is instructor-approved.

## Source identities

Upstream snapshots are retained in `targets/candidates/upstream/`, with original URLs
and checksums in its README. [The original provenance record](../artifacts/target-candidates/README.md)
documents upstream commit/parent research. Local bundles contain newly created snapshot
history, rather than the original upstream commit graph. Do not substitute one set of refs
for the other.

| Source | zlib / CVE-2018-25032 | libpng / CVE-2019-7317 |
| --- | --- | --- |
| Upstream baseline | `e99813dbfe9a09e33d42e8da9e550a0c4b7ff734` | `8439534daa1d3a5705ba92e653eda9251246dd61` |
| Upstream fix | `5c44459c3b28a9bd3283aaceab7c615f8020c531` | `9c0d5c77bf5bf2d7c1e11f388de40a70e0191550` |
| License | zlib license, bundled README/headers | PNG Reference Library License v2, bundled LICENSE |

### Target 1 packaged versions

Bundle: `targets/target1/source.bundle`. SHA-256:
`79ae2dde02dd807b3215cefe360e0e2276ce96dd1495e4e97f3e1feb8b784074`.

| Version | Exact local commit |
| --- | --- |
| baseline | `88fb854d151473d88294f56da390408c61be23a8` |
| correct | `29abcf1b7d99287ec85e5babd4d4234f60d1fff7` |
| incomplete | `3798818fa44dc59e2bc21fdf7112cc72103b04c2` |
| regression | `73baa13a5ce13ab49e2b6eb85d2269148b283185` |

Configurations and the sole editable test corpus are under `evaluation/target1/`.
Clone the bundle as described in [evaluation.md](evaluation.md); the disposable
`repository/` checkout is ignored. Driver and Makefile source belong to the exact
bundled commits, rather than a second independently editable copy under `targets/`.

### Target 2 packaged versions

Bundle: `targets/target2/source.bundle`. SHA-256:
`dff58e37fd39e005163ed3a6b0e422317a46d661c41ef8476ee4bd5576c31fd0`.

| Version | Exact local commit |
| --- | --- |
| baseline | `b1bd9ad4088a429292111a831247a26bbe06b350` |
| correct | `d57c4e247776fe92f3128cb4e71410bb86edb907` |
| incomplete | `e11572a245295b26d8874fe3a8084801762f898f` |
| regression | `426e4f9baa9b35ed6635423b50f3c7e43fd6c8b0` |

Configurations and the sole editable test corpus are under `evaluation/target2/`.
Clone the bundle as described in [evaluation.md](evaluation.md); the disposable
`repository/` checkout is ignored. Driver and Makefile source belong to the exact
bundled commits, rather than a second independently editable copy under `targets/`.

## Driver and patch scope

zlib uses bundled `driver/zlib_driver.c`, file input via `--file`, `Z_FIXED` and
`memLevel=1`. It checks for stream completion but discards compressed bytes. The
incomplete variant adds a flush condition in `deflate.h` depending on input count and
buffer occupancy. The regression variant changes the driver to reject streams longer
than 1,000 bytes beginning with the literal `Antigravity`. These are deliberately
constructed local scenarios. Their definitions do not establish observed outcomes.

libpng uses bundled `driver/png_driver.c` and the simplified read API. Its driver
checks begin/finish-read and allocation failures and discards decoded pixels. The incomplete variant changes
`png_image_free` to apply the safe cleanup only for widths at most 100, retaining the
old path for larger widths. Its regression variant changes the driver to reject heights
above 50. libpng links system zlib with `-lz`, separately from Target 1; neither the
Dockerfile nor package instructions pin that dependency version. Record the actual
version/image used for comparison and replay; universal package pinning is optional.

Bundled Makefiles offer `release`, `sanitized` and `clean`. Their default flags lack
explicit stack-canary and full-RELRO options; `CC ?= clang` does not override GNU make's
built-in `CC=cc`. Record actual build commands and ELF results instead of assuming
the configuration hardening policy was satisfied. The selected configs now impose no
absolute all-enabled minimum: the PDF requires inspection and downgrade warnings, not
forcing protections absent from the baseline.

## Input and expectation ownership

Each `evaluation/targetN/suites/` owns valid, boundary and invalid directories plus
`expected.json`. Its sibling `reference.py` and `generated-regressions/` own reference
logic and generated cases. Matching corpus copies formerly under `targets/` were
removed after byte comparison. Driver copies matched bundled baseline source after
CRLF normalization and were also removed.

The selected upstream baseline archives were compared with bundled baseline files.
All original upstream paths are present. After CRLF normalization, Target 1 differs
in its replaced Makefile; Target 2 preserves all original file contents. Both add local
driver/build assets. Keep the original upstream archives: they preserve provenance
and original line endings/build material independently of the local snapshot history.

The zlib reference covers its bounded completion contract. PNG uses reviewed fixed
fixture expectations and no general reduced-input reference. Unknown reduced behavior
remains diagnostic/inconclusive until independently established.
Fixed reviewed fixture expectations can suffice; no general decoder is required. zlib byte
streams are generally legitimate compression inputs even when labelled “invalid”
because they exercise a memory defect. PNG validity requires independent parsing.
RFC 1950/1951 and the PNG format specification are candidate authorities; merely naming
them does not establish that these tests implement their behavior. Review expected
outputs, valid boundaries, malformed-input behavior and reduced-input validity before
acceptance. The roadmap records the resulting requirements gaps.

## Required execution evidence

Use the six comparisons and later regression/replay steps in [evaluation.md](evaluation.md).
Retain observations against the exact local commit hashes above, source/binary/image
hashes, corresponding release/sanitized settings, raw diagnostics, correlation, at least
three replays, original/minimized bytes and independently checked expected behavior.
Target names, branch labels and expected exit tables are never verdict evidence.


## Bounded zlib functional contract

The selected driver accepts file byte streams of 0 through 65,536 bytes for this
assessment. All current suite and generated cases fit that range. Within it, ordinary
success means `deflateInit2` succeeds and `deflate(..., Z_FINISH)` reaches `Z_STREAM_END`;
the driver then returns 0 with empty stdout/stderr. File access, allocation, stream
initialization or failure to finish is not successful completion. This is an API
completion/status contract; it makes no claim to compare compressed output bytes.

The independent basis is the upstream `zlib.h` API documentation in both retained
upstream archives and the bundled baseline, especially the `deflate`/`Z_FINISH` and
`deflateBound` documentation: sufficient bound-sized output permits stream completion,
and `Z_STREAM_END` means all input was consumed and all output produced. The driver
uses that bound and checks completion. No expectation is copied from patched output.
The bounded size stays well below the driver's `uInt` input-size limit and uses the
same documented resource limits across variants.

The reference therefore reports all in-scope bytes as valid and predicts successful
completion, including the byte streams that expose the security defect. Unsupported
larger payloads fail the reference explicitly; this does not claim the driver enforces
that assessment bound. The existing `invalid/` directory is a legacy security-corpus
location, not proof of malformed compression data. Invalid-interface coverage remains
a separate F03 review item. PNG has its separate native-format contract below; general format decoding is outside this scope.

Tests independently compress/decompress the selected payloads with Python's system
zlib and verify that every manifest/reference validity agrees. This demonstrates that
the payloads are legitimate compression input; it does not inspect the target driver's
discarded compressed output. The two generated functional cases are now eligible for
functional-regression checks. Their bytes and source-version identities are unchanged.

For actual builds, all three zlib configs select Clang and define `HAVE_UNISTD_H` in
both modes. The custom bundled Makefile bypasses upstream configure; without that
normal platform feature definition, Clang rejects undeclared `read`, `write`, `close`
and `lseek` in the legacy gzip sources. No source or bundle commits were changed.
The [bounded native verification](../artifacts/checkpoints/zlib-contract-ci/README.md)
records successful completion on baseline/correct and failure of the documented
large-input regression, including the existing reduced case. It is not the full
security matrix and does not establish instructor approval.


## Native-format PNG completion/rejection contract

The driver keeps libpng's header-selected native format and supplies no colormap to
`png_image_finish_read`. The independent basis is the bundled/upstream `png.h`
simplified-read documentation: begin-read fills the header; finish-read completes
decoding and reports success/failure, and colormapped output requires a colormap.
The selected RGBA `valid.png` is byte-identical to upstream `pngtest.png` (verified
against the bundled source). Successful completion returns 0 with no output.
Begin/finish-read rejection returns 2 with no output. Allocation failure returns 3.
Cleanup runs on each of these paths, preserving the library flaw on the baseline.

The two existing indexed-color security fixtures request native palette output without
its required colormap, so the correct driver rejects them with 2. They are outside the
selected successful interface, even though the original trigger is a valid indexed
PNG file. Do not equate their directory name with global PNG-format invalidity.
Empty input rejects with 2. The deliberately constructed regression still rejects
height above 50 with code 1 and its existing diagnostic; the RGBA fixture has height 69.

`reference.py` recognizes only the four reviewed fixture hashes. Unknown bytes receive
no guessed expectation. The configs use the fixed expectation manifest and disable
the optional general reference command. Functional minimization may use known valid
fixtures; unknown reduced security behavior remains incomplete until reviewed.
No broader decoder or new dependency was introduced.

All four scenario driver versions were updated identically (preserving the deliberate
regression guard), and the configs now explicitly use Clang. Current refs are in the
table above; the bundle keeps the previous versions under `legacy/baseline`,
`legacy/correct`, `legacy/incomplete` and `legacy/regression`. The exact old-to-new map
is retained with the [PNG checkpoint](../artifacts/checkpoints/png-contract/README.md).
The three generated cases for the old baseline, including the truncated alleged
functional reproducer, were moved unchanged to that checkpoint's `legacy-regressions/`.
They are not current regression tests. Later pipeline runs must generate/review cases
for the new baseline rather than copying the former blanket success expectations.
