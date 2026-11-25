# Engineer 2 presentation guide

**Owner:** Mohammadmahdi Abedini (402106191)

**Topic:** Signals, sanitizer parsing, finding identity, Git-diff parsing, and
runtime-to-source correlation.

Start with the problem: a process exit code only says that something happened.
Your code turns noisy stderr and the real patch diff into explainable evidence.
It still refuses to overclaim when symbolization or correlation is missing.

## 1. The story to tell

1. `runner.py` returns exit code, stdout, stderr, and limit flags.
2. `triage.py` checks timeout/resource/output limits first. Those become a
   resource-limit category, not a crash finding.
3. It recognizes AddressSanitizer/UndefinedBehaviorSanitizer text, signal numbers,
   and source frames. If the sanitizer says it could not symbolize, the report
   records that fact.
4. `correlator.py` parses the actual unified diff between the two exact commits.
   It compares the frame's file/line with old lines for the base or new lines for
   the patch.
5. `finding_signature` keeps a stable tuple such as error type + file + function
   + line. Only unchanged patch coordinates are mapped back; changed lines stay
   conservative.

## 2. Exact code to know

### `diffsheriff/triage.py`

Signals are decoded instead of guessed from a generic non-zero exit:

```python
def _signal_from_return_code(exit_code, shell_status=False):
    if exit_code < 0:
        signal_number = -exit_code
    elif shell_status and exit_code >= 128:
        signal_number = exit_code - 128
    else:
        return None
    return SIGNALS.get(signal_number, f"SIGNAL_{signal_number}")
```

The first branch in `triage_execution_result` is deliberately conservative:

```python
if timed_out or resource_limited or output_limited:
    category = "timeout" if timed_out else \
        "resource-limit" if resource_limited else "output-limit"
    return CrashReport(False, category, "Resource Limit", ...)
```

For an AddressSanitizer line such as `ERROR: AddressSanitizer: heap-buffer-overflow`,
the parser stores `error_type="heap-buffer-overflow"`,
`detection_mechanism="AddressSanitizer"`, and source-level frames. The helper
`_source_frames` can synthesize the sanitizer's reported file/line when normal
frames are absent, but an unresolved function is never treated as a precise
source signature.

Changing the regex or unresolved-function list changes which stderr lines become
findings. Demonstrate this only with a unit fixture: add an assertion for one
known sanitizer summary, run `pytest tests/test_triage.py`, and revert it.

### `diffsheriff/correlator.py`

`parse_unified_diff` tracks old/new line numbers in a `DiffHunk`. Then:

```python
if _paths_match(frame.file, path) and frame.line in lines:
    return CorrelationVerdict(
        True,
        "Direct Match" if index == 0 else "Indirect (Caller/Callee)",
        path, frame.line, frame, hunk,
        "Runtime frame intersects an edited line; "
        "comparative evidence is required for attribution.",
    )
```

If no edited line or inserted function matches unambiguously, the verdict is
`Inconclusive`. That is a feature: a stack that merely crashes somewhere in the
same program is not enough to blame the patch.

`finding_signature` accepts only sanitizer mechanisms and useful error types,
rejects unknown/absolute paths, and preserves exact source locations. A changed
line cannot be mapped uniquely, so the code retains patch coordinates until
richer comparative evidence exists.

## 3. Pipeline connection

`pipeline.observe` combines execution, triage, signature, and correlation:

```python
result = execute_container(source, binary, payload, settings)
crash = triage_execution_result(result.exit_code, result.stdout, result.stderr, ...)
return {
    "execution": asdict(result),
    "triage": asdict(crash),
    "signature": finding_signature(crash, side, hunks),
    "correlation": asdict(correlate_stack_to_diff(crash.stack_trace, hunks, side)),
}
```

`compare_case` then compares corresponding base/patch modes and three stable
replays. A patch signature equal to the baseline is an incomplete fix; a
different confirmed patch signature can be a new issue; a base-pass/patch-fail
valid input is a functional regression.

## 4. How to run your part

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_triage.py tests/test_correlator.py
python -m pytest -q tests/test_pipeline.py -k "correlat or signature or stable"
```

Safe defense demo: in a temporary unit fixture, change one expected correlation
label from `Direct Match` to the intentionally conservative `Inconclusive`, run
the focused test to see the failure, then restore the test and implementation.
Never weaken the official target signature or manufacture a stack trace.

## 5. Three sentences to memorize

1. “A limit event is not a crash; it is incomplete evidence.”
2. “Correlation means the runtime frame intersects an actual changed line on the
   correct diff side, not merely that the program crashed.”
3. “An unknown or changed location stays inconclusive until comparative evidence
   supports attribution.”

