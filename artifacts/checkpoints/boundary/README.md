# Boundary functional-regression checkpoint

Tested on Windows with Python 3.13, based on `c5345b1` plus this checkpoint's
changes. `source-sha256.json` identifies the exact tested Python sources with CRLF
normalized to LF. Pipeline tests mock builds, container execution, image resolution,
and hardening; this is synthetic validator coverage, not real-target acceptance.

`red.xml` records 8 failures and 1 pass before the change. The direct comparison
test shows the original bug: an independently valid boundary case is not marked
as a regression. CLI cases also show the old schema rejects explicit validity.
`focused.xml` records 47 passing pipeline/report tests; `full.xml` records 110 passed
and one native Docker test skipped. Subsequent added cases cover a failing baseline
and coexistence with an outstanding security finding (exit 10 has priority).

Commands from the repository root (with project/dev dependencies installed):

```powershell
$env:PYTHONPATH = (Resolve-Path .diffsheriff/deps).Path
python -m pytest -q tests/test_pipeline.py -k 'boundary or input_validity' --basetemp=.diffsheriff/tests-boundary-red-complete --junitxml=artifacts/checkpoints/boundary/red.xml
python -m pytest -q tests/test_pipeline.py tests/test_reporter.py --basetemp=.diffsheriff/tests-boundary-focused-final --junitxml=artifacts/checkpoints/boundary/focused.xml
python -m pytest -q tests --basetemp=.diffsheriff/tests-boundary-full --junitxml=artifacts/checkpoints/boundary/full.xml
python -m flake8 --jobs=1 diffsheriff tests
Get-ChildItem diffsheriff,tests -Recurse -Filter *.py | ForEach-Object { python -m black --check $_.FullName }
$env:TEMP = (Resolve-Path .diffsheriff/tmp).Path
$env:TMP = $env:TEMP
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/boundary/package
```

The first command is the pre-fix checkpoint; the final source adds parameter cases
and all selected tests now pass. Flake8, sequential Black API checks (`fast=False`,
line length 88, all 26 Python files), and wheel construction passed. The wheel's
Python source was checked against the source checkout.

`valid_input` is optional in independent expectation entries, defaults true only for
the valid suite, and must be a boolean. Explicitly valid boundary cases contribute
to functional totals, produce regression bundles, and retain their designation on
subsequent runs. False or unspecified boundary validity never turns a mismatch into
a functional regression. Existing expectation manifests remain compatible.

Not run: native Docker verification, because no Docker executable is available on
this host. Insertion-only patch attribution and human/target acceptance remain open.
