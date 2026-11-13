# Reference comparison and compatible feature completion

Based on `5d15a83` plus the sources identified in `source-sha256.json` (CRLF normalized
to LF). Kasra requested comparison with DNS-P1 and explicitly chose to retain exact
Git commits and instructor-approved targets while filling compatible gaps. This
checkpoint does not record acceptance of the preceding Stage 2 or of any target.

The [feature comparison](../../../docs/reference_comparison.md) maps the reference
at `41173bab54a3b1aa0318564799a299e6d35573ea` to DiffSheriff's contracts, tests, and
remaining delivery gates. `reference.json` preserves the inspected revision and file
hashes. Reference scripts, tests, and vulnerable samples were not executed or imported.

## Changes

- Retain available symbol tables, conventional FORTIFY symbol candidates, and
  sanitizer families/symbols. Each baseline/patch and release/sanitized build now has
  an `elf` record; required hardening comparison remains release-only.
- Show release hardening, per-build symbol summaries, finding detection/correlation/
  stability/reason, reduced input paths, and the evidence directory in the console.
- Preserve UBSan's actual termination signal using the same decoding as ASan, while
  keeping an ordinary exit 134 distinct from a signal unless shell semantics apply.
- Add `bash verify.sh`: prerequisite checks, Black, standard Flake8, the complete
  suite with harmless native execution, and wheel creation. It fails on failed steps,
  retains each run separately, and makes no target-acceptance claim. Development
  dependencies include `wheel` for the offline package step; shell files use LF.
- Add the comparison and four-role study guide; update usage, architecture, roadmap,
  and artifact index. Keep real contribution history and the existing target gate.

FORTIFY/sanitizer symbol names are observations, not proof of compile flags, executed
instrumentation, per-function protection, or runtime ASLR. Absence or removal can
reflect optimization/stripping. No new passing verdict or hardening failure is inferred
from these optional observations. Raw symbol tables are retained by name, rather than
asserting a binary is fully stripped solely because `.symtab` is missing.

## Verification

- `red.xml`: **3 failures, 5 passes** before metadata/console implementation.
- `signal-red.xml`: **2 failures, 1 pass** before the UBSan termination correction.
- `focused.xml`: **87 passes** for hardening, CLI, and pipeline changes. The later
  UBSan cases are included in both final full runs.
- `full-windows.xml`: **196 passed, 7 skipped**, Python 3.13.1. Skips: six symlink
  cases requiring link-creation permission and the Linux native-container test.
- `full-linux.xml`: **203 passed, no skips**, Python 3.12.3, run by the new verifier.
- `verify-linux.log`: actual one-command output, including Black (28 files), standard
  Flake8 E/F/W/C90 checks, full tests, and successful offline wheel construction.
- `verifier-failure-paths.json`: missing Python and missing image both exit nonzero
  without printing the success message.
- All tested Linux sources/tests/config match the checkout; installed container
  sources and packaged Python sources match after newline normalization.
- Git whitespace checks pass outside the original pre-fix `red.xml` traceback;
  its one whitespace-only diagnostic line is preserved as raw evidence.

Commands used, with `.diffsheriff/deps` supplied on `PYTHONPATH`:

```text
python -m pytest -q tests/test_hardening.py tests/test_pipeline.py::test_cli_exports_and_restores_generated_regressions --basetemp=.diffsheriff/parity-red --junitxml=artifacts/checkpoints/reference-parity/red.xml
python -m pytest -q tests/test_triage.py -k ubsan_preserves --basetemp=.diffsheriff/parity-signal-red --junitxml=artifacts/checkpoints/reference-parity/signal-red.xml
python -m pytest -q tests/test_hardening.py tests/test_pipeline.py tests/test_cli.py --basetemp=.diffsheriff/parity-focused --junitxml=artifacts/checkpoints/reference-parity/focused.xml
python -m pytest -q tests/ --basetemp=.diffsheriff/parity-full --junitxml=artifacts/checkpoints/reference-parity/full-windows.xml
bash -n verify.sh
DIFFSHERIFF_TEST_IMAGE=diffsheriff:reference-parity bash verify.sh
PYTHON=diffsheriff-nonexistent-python bash verify.sh
DIFFSHERIFF_TEST_IMAGE=diffsheriff:nonexistent-parity-image bash verify.sh
```

The last two commands are intentional failure checks. The full Linux command used a
fresh source snapshot at the path in `verification.json`; it used cached development
dependencies, so this is not the final clean-room delivery test. Docker reported host
blkio/cgroup deprecation notices, preserved in the log; they did not fail the checks.

## Evidence and package

`native/` contains the harmless fixture/corpus/config, report, four source archives,
four binaries, run data, runtime source hashes, and the offline image-build log. The
report returns 40, functional PASS, and 36 suite executions because no designated
baseline flaw exists in the harmless program. It observes ASan symbols in both
sanitized builds and none in the corresponding release builds. All four archive and
binary hashes and six case-input hashes were checked against the report.

`synthetic/symbol-fixture.elf` is a generated parser fixture, never executed. Its
inspection is in `symbol-evidence.json`; `ubsan-termination.json` records the parser's
three synthetic termination cases. These do not demonstrate a real vulnerability.

`package/` contains the verified wheel. `verification.json` records its SHA-256 and
the source/runtime identities. `artifact-sha256.json` hashes every checkpoint file
except itself. Original temporary paths in reports/logs are provenance; replay needs
the whole run directory and its recorded runtime image, as described in usage.

Runtime image: `sha256:b5bbef31e8ab12df9a99d0b446a0edf5f19294fbc66a43e13aca1b49742a0ab6`.
It was built with `docker build --network=none -t diffsheriff:reference-parity .`,
overlaying the tested source onto the preceding `diffsheriff:cache-import` image
(`sha256:00fe036fddd0c2e52dda09dce51e963f30345faeefec01cabf564776f710a5c9`), tagged
`diffsheriff:reference-parity-base`, using:

```dockerfile
FROM diffsheriff:reference-parity-base
WORKDIR /opt/diffsheriff
COPY pyproject.toml README.md ./
COPY diffsheriff/ diffsheriff/
RUN pip install --no-cache-dir --no-build-isolation --no-deps .
WORKDIR /src
```

No commit, push, hosted CI rerun, target acceptance, or individual defense was performed
by this review. The roadmap retains those dependencies and review decisions explicitly.
