#!/usr/bin/env bash
# Execute the six approved baseline/patch comparisons and verify their evidence.
#
# Required before running (see docs/evaluation.md):
#   * development dependencies installed and the runtime image built
#   * both source bundles cloned into evaluation/<target>/repository
#   * a Docker daemon reachable by the current user
#
# Each comparison keeps its console log, JSON report and run bundles under
# artifacts/evaluation/<target>/<variant>/. Exit codes are compared with the
# justified scenario table; they are never forced.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 30

PYTHON="${PYTHON:-python3}"
IMAGE="${DIFFSHERIFF_TEST_IMAGE:-diffsheriff:local}"
ARTIFACTS="${MATRIX_ARTIFACTS:-artifacts/evaluation}"
SYMBOLIZER="${MATRIX_SYMBOLIZER_PATH:-/usr/bin/llvm-symbolizer}"

# target:variant:expected-exit-code, in the order the assignment lists them.
ROWS=(
  "target1:correct:0"
  "target1:incomplete:10"
  "target1:regression:20"
  "target2:correct:0"
  "target2:incomplete:10"
  "target2:regression:20"
)

usage() {
  cat <<'EOF'
Usage: bash scripts/run_matrix.sh [--list]

Runs the six target comparisons defined in docs/evaluation.md and verifies:
  * the validator exit code matches the justified scenario outcome
  * the retained JSON report parses and records the same exit code
  * every retained reproducer bundle has its metadata and both inputs

Environment:
  PYTHON                  Python with DiffSheriff installed (default: python3)
  DIFFSHERIFF_TEST_IMAGE  Local runtime image (default: diffsheriff:local)
  MATRIX_ARTIFACTS        Output root (default: artifacts/evaluation)
  MATRIX_SYMBOLIZER_PATH  Symbolizer expected inside the image
                          (default: /usr/bin/llvm-symbolizer)
EOF
}

if [ "${1:-}" = "--list" ]; then
  printf '%s\n' "${ROWS[@]}"
  exit 0
fi
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

errors=()
report_error() {
  errors+=("$1")
  printf 'FAIL %s\n' "$1" >&2
}

# ---------------------------------------------------------------- preflight
command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "Missing prerequisite: $PYTHON" >&2
  exit 30
}
"$PYTHON" -c 'import diffsheriff.config, yaml' >/dev/null 2>&1 || {
  echo "DiffSheriff is not importable; run: python -m pip install -e '.[dev]'" >&2
  exit 30
}
command -v docker >/dev/null 2>&1 || {
  echo "Missing prerequisite: docker" >&2
  exit 30
}
docker info >/dev/null 2>&1 || {
  echo "The Docker daemon is not reachable by this user." >&2
  exit 30
}
docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "Runtime image $IMAGE is missing; build it first:" >&2
  echo "  docker build --platform linux/amd64 -t $IMAGE -f docker/Dockerfile ." >&2
  exit 30
}
# Stack frames must symbolize, or the designated signature cannot be matched.
if ! docker run --rm --entrypoint /bin/sh "$IMAGE" -c \
  "test -x '$SYMBOLIZER'" >/dev/null 2>&1; then
  echo "The runtime image has no executable symbolizer at $SYMBOLIZER." >&2
  echo "Install LLVM in the image and set external_symbolizer_path in the config." >&2
  exit 30
fi

for target in target1 target2; do
  repository="evaluation/$target/repository"
  if [ ! -d "$repository" ]; then
    report_error "missing source checkout: $repository (run the Prepare target sources step)"
  fi
  for variant in correct incomplete regression; do
    config="evaluation/$target/$variant.yaml"
    if [ ! -f "$config" ]; then
      report_error "missing configuration: $config"
    fi
  done
done
if [ "${#errors[@]}" -ne 0 ]; then
  printf 'Preflight failed; nothing was executed.\n' >&2
  exit 30
fi

for target in target1 target2; do
  repository="evaluation/$target/repository"
  for ref in $(
    "$PYTHON" - "evaluation/$target/correct.yaml" <<'PY'
import sys, yaml
target = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["target"]
print(target["base_ref"], target["patch_ref"])
PY
  ); do
    git -C "$repository" cat-file -e "$ref^{commit}" 2>/dev/null ||
      report_error "$repository does not contain configured commit $ref"
  done
done
if [ "${#errors[@]}" -ne 0 ]; then
  printf 'Preflight failed; nothing was executed.\n' >&2
  exit 30
fi

mkdir -p "$ARTIFACTS"
summary="$ARTIFACTS/matrix.tsv"
printf 'target\tvariant\texpected\tactual\tverdict\n' >"$summary"

# ---------------------------------------------------------------- execution
for row in "${ROWS[@]}"; do
  target="${row%%:*}"
  rest="${row#*:}"
  variant="${rest%%:*}"
  expected="${rest##*:}"
  config="evaluation/$target/$variant.yaml"
  out="$ARTIFACTS/$target/$variant"
  mkdir -p "$out"
  printf '\n=== %s/%s (expected exit %s) ===\n' "$target" "$variant" "$expected"

  actual=0
  "$PYTHON" -m diffsheriff.cli --config "$config" \
    --output-json "$out/report.json" \
    --artifacts "$out/runs" \
    >"$out/console.log" 2>&1 || actual=$?

  if [ "$actual" -ne "$expected" ]; then
    report_error "$target/$variant exited $actual, expected $expected"
  fi

  "$PYTHON" scripts/verify_matrix_run.py "$out" --target "$target" \
    --variant "$variant" --actual "$actual" --expected "$expected"
  verify=$?
  if [ "$verify" -ne 0 ]; then
    report_error "$target/$variant retained evidence is incomplete"
  fi

  printf '%s\t%s\t%s\t%s\t%s\n' \
    "$target" "$variant" "$expected" "$actual" \
    "$([ "$actual" -eq "$expected" ] && echo verified || echo mismatch)" \
    >>"$summary"
done

# ---------------------------------------------------------------- summary
printf '\nComparison summary (%s):\n' "$summary"
cat "$summary"
if [ "${#errors[@]}" -ne 0 ]; then
  printf '\nMATRIX FAILED\n' >&2
  printf '  %s\n' "${errors[@]}" >&2
  exit 1
fi
printf '\nMATRIX PASSED: six comparisons produced the justified exit codes.\n'
printf 'Replay a baseline finding with:\n'
printf '  python -m diffsheriff.reproduce <run>/reproducers/<bundle> --check-regression\n'