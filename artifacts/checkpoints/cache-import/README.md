# Stage 2: reconcile trusted regression-cache imports

Based on `c0b5eb7d71aa27218fd47c747e871c4b9b71a569` plus this checkpoint's changes.
`source-sha256.json` identifies the tested sources, tests, fixtures, and package
configuration, with CRLF normalized to LF. This checkpoint records implementation
and generic verification of the cache-import behavior. It is not target-acceptance
evidence; current project status and remaining work are maintained in
[`docs/roadmap.md`](../../../docs/roadmap.md).

## Behavior and trust boundary

The shared transfer helper validates manifests and input hashes before planning any
writes. Identity includes every field except `expected`, `check`, and `valid_input`:
the exact baseline, input filename and verified bytes/hash, build mode, baseline and
originating finding signatures, finding side, kind, and any additional metadata.
This includes patch-coordinate signatures with `side: patch`.

A matching incoming diagnostic null expectation yields to a local full expectation.
The local manifest and payload remain byte-for-byte unchanged. Semantically equal
metadata also preserves local formatting. Different non-null expectations, invalid
metadata, conflicting identities/bytes, corrupt hashes, traversal, and symlinks fail
closed. An unrelated baseline is filtered only when it does not collide with a local
manifest. A cache cannot upgrade an existing local diagnostic manifest to a full check.

Before CLI import, discovery snapshots independent local corpus/reviewed regression
expectations. A new full cached manifest is accepted only if its exact payload,
expected exit/stdout/stderr, and validity match that snapshot. Import does not turn
newly copied cache entries into evidence for other entries. The local checkout is the
operator's trust boundary; this does not authenticate who reviewed a local expectation.

Export still refreshes an explicitly selected caller-owned snapshot. Conflicts are
validated for the entire transfer before writes start. This is not a filesystem
transaction against concurrent writers or an I/O failure during the final writes.
Do not share the destination with an untrusted concurrent writer.

An incompatible/untrusted cache returns operational code 30, with incomplete analysis.
Omit `--regressions-from` for a fresh local run, or establish and check in independent
local expectations. No extra bypass switch, workflow change, or dependency was added.
See [CI/operator guidance](../../../docs/ci.md).

## Verification

- `red.xml`: 12 passed, 3 failed before implementation. It reproduced stale diagnostic
  conflict, cache-only ground-truth acceptance, and silent baseline-collision filtering.
- `focused.xml`: 35 passed, 6 Windows symlink skips, 74 deselected. Covers helper
  transfers and CLI stale/conflict/cache-only/restore behavior.
- `full-windows.xml`: **192 passed, 7 skipped** on Python 3.13. The skips are the six
  symlink cases (host lacks link-creation permission) and Linux native-container test.
- `full-linux.xml`: **199 passed, no skips**, Python 3.12.3 in Ubuntu WSL, including
  all symlink cases and the harmless native container test.
- Black 26.10.1: all 28 Python files unchanged after formatting, with project config.
- Flake8's standard E/F/W/C90 checks passed on Windows and Linux. Unfiltered local
  Flake8 also loads unrelated cached docstring/quote/import plugins and reports their
  existing violations; those plugins are not installed by the project's CI dependencies.
- Offline wheel construction succeeded. Every packaged Python source and installed
  runtime source matched the tested checkout after newline normalization.
- Git whitespace checks passed outside the raw pre-fix `red.xml` traceback, whose
  original trailing space is preserved as test evidence.

Commands, from the checkout (or its identical Linux snapshot):

```text
python -m pytest -q tests/test_regressions.py --basetemp=.diffsheriff/cache-red --junitxml=artifacts/checkpoints/cache-import/red.xml
python -m pytest -q tests/test_regressions.py tests/test_pipeline.py -k "not test_pipeline or cli_cache_respects or cli_exports_and_restores" --basetemp=.diffsheriff/cache-final-focus --junitxml=artifacts/checkpoints/cache-import/focused.xml
python -m pytest -q tests/ --basetemp=.diffsheriff/cache-full --junitxml=artifacts/checkpoints/cache-import/full-windows.xml
python3 -m black --check --workers 1 diffsheriff tests
python3 -m flake8 --jobs=1 --select=E,F,W,C90 diffsheriff tests
DIFFSHERIFF_DOCKER_TESTS=1 DIFFSHERIFF_TEST_IMAGE=diffsheriff:cache-import python3 -m pytest -q tests/ --basetemp="$snapshot/results" --junitxml="$repo/artifacts/checkpoints/cache-import/full-linux.xml"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/cache-import/package
```

Dependencies came from `.diffsheriff/deps` on `PYTHONPATH`. Windows wheel TEMP/TMP
pointed to `.diffsheriff/tmp`. The Linux snapshot path is in `verification.json`.
Black was run in WSL after the Windows multiprocess invocation stalled and was stopped.

## Retained evidence

`synthetic/` contains helper source/destination files showing stale-null versus local
reviewed behavior, plus three CLI test directories with their actual configs, inputs,
reports, generated manifests, and run bundles. The CLI stale-cache case passes with
exit 0 and refreshed export matching the unchanged local files. Conflicting and
cache-only expectations return 30 before target execution. `observed-results.json`
records these outcomes and local manifest hashes. The helper case separately proves
that a local reviewed `valid_input: true` survives an incoming diagnostic false flag.

These are mocked diagnostics and placeholder build/image identities, not executable
course-target evidence. They are retained to inspect transfer semantics and reports.

`native/` retains the harmless C fixture, config/corpus, native source archives,
binaries, reports, runtime source hashes, and image build log. It verifies ordinary
native execution remains intact: 36 suite executions, functional PASS, exit 40 because
the harmless fixture has no designated baseline flaw. All four binary and archive
hashes and six recorded case-input hashes were verified against its report.

Runtime image: `sha256:00fe036fddd0c2e52dda09dce51e963f30345faeefec01cabf564776f710a5c9`.
It was built offline by overlaying this source onto `diffsheriff:minimized-results`
(`sha256:dca15002993f7f4997c27d10e4abd5b7ebbddfa0ca632b28cf9968820ada1189`):

```dockerfile
FROM diffsheriff:cache-import-base
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
```

The old image was tagged as `diffsheriff:cache-import-base`; construction used
`docker build --network=none -t diffsheriff:cache-import .`. Runtime image availability
is external to the retained files. Original temporary paths in reports are provenance,
not portable replay paths. `artifact-sha256.json` hashes every retained file except
itself; `verification.json` records checked source/runtime/package identities.

No Stage 2 commit, push, or hosted rerun was performed. Stage 3 remains a team/instructor
approval dependency. No proposed course targets, real exploits, or aggressive inputs
were built, executed, or created.
