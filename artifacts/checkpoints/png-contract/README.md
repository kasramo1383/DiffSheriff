# PNG completion/rejection contract and packaged versions

This checkpoint implements the selected F02 error/status contract and F05 packaging.
The [target record](../../../docs/target_scenarios.md#native-format-png-completionrejection-contract)
owns the independent png.h basis and exact source identities. Instructor approval
remains pending. No general PNG decoder or arbitrary-input oracle was added.

The driver returns 0 for successful native-format decode, 2 for read rejection, and
3 for allocation failure. Cleanup still runs, preserving the baseline flaw. Existing
regression behavior is retained. Unit harnesses compile the actual bundled driver
against controlled APIs to test begin/finish/allocation failure and cleanup directly.
The fixed reference recognizes reviewed fixture hashes only; unknown reduced behavior
is not inferred. The original RGBA fixture matches upstream pngtest.png byte-for-byte.

`source-mapping.json` maps old/current refs and bundle/driver hashes. The new bundle
preserves prior versions under legacy refs. `legacy-regressions/` retains the previous
three input/manifest pairs unchanged, outside the active test suite. The old reduced functional
case has no independent successful-decode justification. Old evidence
and source identities must not be relabelled as observations of the new versions.

`native.json` records source/build/runtime identities, actual ELF observations and
96 executions: four variants, two modes, four fixture inputs and three replays.
Every baseline sanitized input reproduces stack-use-after-return in png_safe_execute.
The correct version is clean and matches the selected completion/rejection expectations.
The incomplete version blocks the original trigger but its bypass retains the same
stable diagnostic. The regression version fails the valid image in both modes.
This is a native scenario/driver check, not the full generic F09 matrix with automatic
minimization, correlation and later-run regression enrollment.

`focused.xml` covers the target assets and generic pipeline. `full-linux.xml`,
`verify-linux.log` and `verification.json` record final generic verification and package
installation. `package/` holds its wheel. `source-sha256.json` normalizes CRLF to LF;
`artifact-sha256.json` covers exact retained evidence bytes, excluding itself.
Temporary source/build clones were removed after retaining the observations. Exact
source versions remain in the delivered bundle; native binary hashes are in the record.

Reproduce focused checks with declared development dependencies on Linux/WSL:

```sh
python3 -m pytest -q tests/test_target_assets.py tests/test_pipeline.py
bash verify.sh
```

F09 still needs full CLI matrices, complete security reproducer bundles, newly generated
regressions and later-run validation. This checkpoint does not claim those results,
hosted target CI, approval or defense. Unseen reduced inputs remain inconclusive.
