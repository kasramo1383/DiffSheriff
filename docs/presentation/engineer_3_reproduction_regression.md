# Engineer 3 presentation guide

**Owner:** Mohammadreza Javadi (402105868)

**Topic:** Stability replay, bounded minimization, reproducer bundles, generated
regression tests, and replay verification.

Your part answers: “How do we know this result is repeatable, and how can another
person verify it later?” The answer is retained bytes plus hashes, not memory or
a screenshot.

## 1. The story to tell

For each supplied input and build mode, the pipeline runs the base and patch
three times. `stable_observations` requires the same signature (or the same
execution fields when there is no signature) and rejects limit events. Only a
stable observation is eligible for a finding.

If a supplied input already reproduces a reviewed finding, `minimize` tries
smaller chunks and complements. It asks an oracle whether the same error type
and crash function remain. It never invents a new trigger and records why it
stopped. The input is not called globally minimal unless the evidence supports
that claim.

The retained bundle contains `original.input`, `minimized.input`,
`reproducer.json`, hashes, base/patch artifact identities, and replay records.
`reproduce.py` verifies the minimized-input hash and binary hashes, executes both
sides three times, and can check baseline-fail/patch-pass behavior.

Generated regression manifests are copied only when their base commit, payload,
signature, validity, and independent expectation agree. Conflicting files are
refused rather than silently overwritten.

## 2. Exact code to know

### `diffsheriff/minimizer.py`

The invariant is explicit:

```python
@dataclass
class FailureInvariant:
    expected_error_type: str
    expected_crash_function: str
```

The oracle refuses to count a candidate unless it preserves that invariant:

```python
crashed, error_type, func_name = oracle(candidate)
return crashed and error_type == invariant.expected_error_type and (
    not invariant.expected_crash_function
    or func_name == invariant.expected_crash_function
)
```

The result includes `stop_reason`, `oracle_calls`, original/minimized sizes, and
limits. `max_oracle_calls` and `max_granularity` are honest bounds, not cosmetic
settings.

Safe defense demo: change a copied config from `max_oracle_calls: 256` to `1`.
The result should stop with `oracle_call_limit`. Restore the value afterward and
explain that one call cannot establish a minimum.

### `diffsheriff/reproduce.py`

Before executing, it checks the bundle and input:

```python
if compute_sha256(payload_path) != metadata["minimized_sha256"]:
    raise ValueError("Reproducer input hash mismatch")
```

It verifies both base and patch binary hashes, gathers three observations for each
side, computes `reproduced` and `stable`, and returns exit 0 only when the
requested replay check succeeds. Replay errors use exit 30; an unsuccessful or
unstable replay uses exit 40.

### `diffsheriff/regressions.py`

`read_regression` validates the manifest schema, kind, mode, signature, expected
result, validity, flat input path, and SHA-256. `copy_regressions` then checks
same-baseline identity and refuses conflicting files. This protects the
regression cache from becoming an unreviewed source of truth.

## 3. Where pipeline evidence is created

`pipeline.record_reproducer` has the important boundary:

```python
"""Reduce supplied cases only; never generate a new trigger or bypass."""
```

`run_pipeline` writes the input hash, patch diff, build records, observations,
minimizations, and reproducer paths into the run directory under the configured
artifact root. The matrix verifier checks report schema/exit-code agreement,
baseline identity, at least three baseline replays, both input files, and the
minimized-input hash.

## 4. How to run your part

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_minimizer.py tests/test_regressions.py
python -m pytest -q tests/test_pipeline.py -k "reproduc or minimiz or replay"
python -m diffsheriff.reproduce <bundle> --check-regression
```

Use a bundle produced by the matrix. Do not edit `reproducer.json` by hand; a
modified hash should fail loudly. When explaining a report, show original and
minimized sizes, `stop_reason`, replay count, and SHA-256.

## 5. Three sentences to memorize

1. “Three consistent observations turn a one-off process result into stable
   evidence.”
2. “Minimization preserves the reviewed error type/function; it does not search
   for or generate an exploit.”
3. “Hashes bind the retained bytes to the build and report, so replay is
   independently checkable.”

