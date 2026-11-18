# Clean checkout verification

Verified the generic delivery path on WSL Ubuntu x86_64 with Python 3.12.3
and Docker Engine 29.5.3. The checkout began at the pushed source revision in
[verification.json](verification.json), without a copied virtual environment,
prepared target repository, or run state. Only the development dependency
change recorded there was applied before the successful repeat.

## Setup result

A fresh environment installed by `python -m pip install -e '.[dev]'` exposed
a missing prerequisite: `verify.sh` imports `setuptools` and uses it to build
a wheel without build isolation, but it was previously declared only for
isolated builds. On Python 3.12 the script failed before testing. Adding it
to the development extra fixed the documented setup.

Docker Hub returned HTTP 403 on the direct build. The
[documented proxy retry](../../../docs/usage.md#retrying-docker-hub-access-from-wsl)
built the test image. It reused cached Ubuntu package layers and rebuilt the
project installation layer. This run does not prove cache-free acquisition
of OS packages.

## Checks

- From the second clean checkout and newly installed virtual environment, ran
  `bash verify.sh` with `PYTHON` pointing to the new virtual environment and
  `DIFFSHERIFF_TEST_IMAGE` set to the rebuilt image tag. Black, Flake8, the full
  pytest suite, and wheel construction passed. The suite checked the delivered
  source bundle refs. The harmless container test used real release and sanitized
  builds and all three input interfaces. Its expected inconclusive security
  result does not establish target acceptance.
- Installed the retained wheel into a separate virtual environment outside
  the checkout. `diffsheriff --help` succeeded and a nonexistent config
  produced exit 30 with structured JSON.
- Ran the existing CI validation shell block in temporary directories against
  a CLI stub returning each documented exit code. The shell preserved each
  code and the JSON remained at the workflow output path. This verifies the
  local shell gate. Hosted artifact upload was outside the check.

## Actual CLI in the local CI shell

A separate [functional round trip](harmless-ci-roundtrip.json) used the
installed wheel and the exact `Run patch validation` shell block. The source
fixture was the harmless echo program with one ordinary output byte changed
from `x` to `X`. Its independent expectation was byte-for-byte echo. The first
run returned 20 and exported two functional manifests. A second checkout with
ordinary echo restored imported both manifests, replayed them three times per
version in both build modes, and passed all functional comparisons. Export
preserved the cache bytes. The combined result stayed 40: a harmless program
has no designated security finding, and the fixture flags omitted a required
stack canary. An absent configuration returned 30 and retained its JSON.
This exercises the real local shell gate for those outcomes.

Course target comparisons and later-run acceptance with the delivered targets
remain open in the [roadmap](../../../docs/roadmap.md).
