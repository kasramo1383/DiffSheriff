# Candidate upstream source snapshots

These archives are convenience copies of the exact upstream baseline/fix commits already
recorded in `docs/target_scenarios.md`. They are inputs to Stage 3 feasibility work, not
selected targets or evidence that either vulnerability reproduces locally.

| Archive | Upstream source | SHA-256 |
| --- | --- | --- |
| `zlib-baseline-e99813dbfe9a.tar.gz` | `https://codeload.github.com/madler/zlib/tar.gz/e99813dbfe9a09e33d42e8da9e550a0c4b7ff734` | `7f38a0e6ff155ecd4b7e985cacea20c868930cbddc4180165671def2ae1b3f6e` |
| `zlib-fix-5c44459c3b28.tar.gz` | `https://codeload.github.com/madler/zlib/tar.gz/5c44459c3b28a9bd3283aaceab7c615f8020c531` | `c1de01363bc62242a6819486dd52fe2b37cd995a6642d09142ca3c82458d2894` |
| `libpng-baseline-8439534daa1d.tar.gz` | `https://codeload.github.com/pnggroup/libpng/tar.gz/8439534daa1d3a5705ba92e653eda9251246dd61` | `c73af438385b725238443ed9c23065b3ed614e04b24cd4b9560f1a587ce7f20f` |
| `libpng-fix-9c0d5c77bf5b.tar.gz` | `https://codeload.github.com/pnggroup/libpng/tar.gz/9c0d5c77bf5bf2d7c1e11f388de40a70e0191550` | `154c4a2a32c187d9ff3e578408c1b12b9e35620d8ce85aa1ec6e3983fa45fd5d` |

The current machine also has disposable extracted copies under
`.diffsheriff/candidate-sources/`; that directory is ignored and must not be used as
delivery evidence. If a candidate is selected, package only the required source form,
license notices, local patches/drivers, and reproducibility metadata described by the
roadmap. Remove rejected or redundant candidate archives before final delivery.
