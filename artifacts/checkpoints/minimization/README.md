# Security minimization checkpoint

Tested on Windows with Python 3.13, based on revision `5bb5472` plus the source
changes in this checkpoint's commit. `source-sha256.json` identifies the exact
Python sources after normalizing CRLF to LF. This is synthetic diagnostic coverage;
target execution, builds, image resolution, and hardening are mocked in pipeline
tests. No course-target acceptance is claimed.

The new no-reference case failed before the fix because `diagnostic` was not reduced
to `d`. Six negative cases also failed because unknown candidates were never run.
The reference-enabled case already passed. `red.xml` retains those results (7 failed,
1 passed). `focused.xml` records 34 passing pipeline/minimizer checks after the fix.
`full.xml` records 97 passed and one native Docker test skipped.

Commands, from the repository root:

```powershell
# Use the installed project/dev dependencies; this workspace used its cached tools.
$env:PYTHONPATH = (Resolve-Path .diffsheriff/deps).Path
python -m pytest -q tests/test_pipeline.py -k security_minimization --basetemp=.diffsheriff/tests-minimization-red --junitxml=artifacts/checkpoints/minimization/red.xml
python -m pytest -q tests/test_pipeline.py tests/test_minimizer.py --basetemp=.diffsheriff/tests-minimization-green --junitxml=artifacts/checkpoints/minimization/focused.xml
python -m pytest -q tests --basetemp=.diffsheriff/tests-minimization-full-deps --junitxml=artifacts/checkpoints/minimization/full.xml
python -m flake8 --jobs=1 diffsheriff tests
Get-ChildItem diffsheriff,tests -Recurse -Filter *.py | ForEach-Object { python -m black --check $_.FullName }
$env:TEMP = (Resolve-Path .diffsheriff/tmp).Path
$env:TMP = $env:TEMP
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir artifacts/checkpoints/minimization/package
```

The first command describes the pre-fix run; on the fixed revision all eight cases
pass. Formatting was checked sequentially with Black's `format_file_contents` API
using `fast=False` and line length 88 for all 26 Python files; the per-file CLI above
is equivalent. Black's multi-file CLI blocks on a local socket in this sandbox.
Flake8 and wheel construction passed. The first wheel attempt hit Windows temporary
path limits; rebuilding with the shorter workspace temp path succeeded. An initial
full-suite invocation without cached dependencies failed two ELF tests because
`pyelftools` was absent; the recorded full run supplies that dependency and passes.

The wheel contains this checkpoint's implementation and is separate from the older
retained `07914aa` wheel. Reproducer tests verify three-run stability, unchanged
error/location, rejection of limits/signals/instability, diagnostic-only replay,
original-input regression fallback, and loading those regressions on a second run.
Unknown reduced behavior is recorded as `expected: null`, never inferred from the
patch. Existing functional reduction still requires independent expectations.

Not run: the native Docker test (no Docker executable available on this host).
Remaining implementation gaps: boundary regression classification and insertion-only
patch attribution. Human acceptance and real-target evidence remain outstanding.
