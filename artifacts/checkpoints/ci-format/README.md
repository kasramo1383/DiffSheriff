# CI formatting correction

The [GitHub run for d319a10](https://github.com/kasramo1383/DiffSheriff/actions/runs/43415419073)
passed the unit tests on Python 3.10 and 3.12, but failed the Black formatting step.
The native-container job passed. The target-patch job was skipped by its configuration
condition. GitHub job metadata confirmed these steps; authenticated raw logs were
unavailable. The formatting failure was independently reproduced in the checkout.

Black 26.10.1 required a trailing comma after `bind_now=False` in
`tests/test_hardening.py`. Earlier local checks used a standalone snapshot without
`.git` or a `[tool.black]` section. Black therefore did not discover its project
configuration and Python-version requirement, unlike in the CI Git checkout. Earlier
snapshot formatting results do not establish that the CI formatting step passed.

The correction adds that comma and explicitly sets Black's target to Python 3.10
in `pyproject.toml`, making configuration discoverable in both environments. No
production behavior or workflow gating changed.

Verification on Python 3.12.3 with Black 26.10.1:

- `python3 -m black --check --workers 1 diffsheriff tests`: all 28 files unchanged
  in both the actual Git checkout and a fresh standalone Linux snapshot.
- `python3 -m pytest -q tests/ --junitxml=.../unit-linux.xml`: 163 passed, one native
  Docker test skipped. The retained XML is from the fresh snapshot.
- `python3 -m flake8 --select=E,F,W,C90 diffsheriff tests`: passed.

The snapshot contained the current source, tests, `pyproject.toml`, README, and Flake8
configuration; dev dependencies came from the workspace cache on `PYTHONPATH`.
GitHub has not been rerun for this fix, and no commit or push was performed by the
agent. Target approval and Stage 2 dependencies remain.
