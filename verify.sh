#!/usr/bin/env bash
# Verify the generic tool and harmless native fixture; no course targets are run.
set -eu
cd "$(dirname "$0")"
python="${PYTHON:-python3}"
image="${DIFFSHERIFF_TEST_IMAGE:-diffsheriff:local}"
for tool in "$python" git docker; do
    command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 1; }
done
"$python" -c 'import pytest, black, flake8, setuptools, wheel, elftools, yaml, click'
docker info >/dev/null
docker image inspect "$image" >/dev/null || {
    echo "Build the runtime image first; see docs/usage.md ($image)." >&2
    exit 1
}
mkdir -p .diffsheriff
work="$(mktemp -d "$PWD/.diffsheriff/verification.XXXXXX")"
echo "Verification evidence: $work"
"$python" -m black --check --workers 1 diffsheriff tests
"$python" -m flake8 --jobs=1 --select=E,F,W,C90 diffsheriff tests
DIFFSHERIFF_DOCKER_TESTS=1 DIFFSHERIFF_TEST_IMAGE="$image" \
    "$python" -m pytest -q tests/ --basetemp="$work/tests" --junitxml="$work/tests.xml"
"$python" -m pip wheel . --no-deps --no-build-isolation --wheel-dir "$work/package"
echo "TOOL VERIFICATION PASSED (synthetic tests and harmless native fixture)."
echo "Approved-target matrices, clean-room delivery, and individual defenses remain separate gates."
