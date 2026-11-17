# Target source and scenario record

[The roadmap](roadmap.md) owns acceptance status and requirement gaps. This record
owns target identities, construction and input locations. Instructor approval evidence
has not been supplied. The bounded zlib completion/status contract is documented
below; PNG contract/reference review remains pending. Neither is instructor-approved.

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
`64caa34d8dc8d72f116d9d563979bbb12d3d77704f64965811b3df524459032a`.

| Version | Exact local commit |
| --- | --- |
| baseline | `c9ceee6f648dd8f7e6bfa336bc00a4dd6174046f` |
| correct | `c27a4c54b68bc966025b8bfb79b01f0fd70a6106` |
| incomplete | `75682381b55f07b6c86ce5d120745c63311854c0` |
| regression | `7e8cbfdb88229e21c64dcc65be4a8fe4a6ee29f7` |

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
ignores read failures and discards decoded pixels. The incomplete variant changes
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

The existing constant reference scripts provide no input-specific validation. Constant
expected outputs can be legitimate for a documented bounded contract, but the blanket
false validity and success for new reduced inputs need independent justification.
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
a separate F03 review item. PNG validity/reference work is unchanged and remains open.

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
