# Generic code audit before target evaluation

This audit starts from `5d15a831ed6c29486628f00bf30dd6f5c3be1bde` plus the staged
reference-parity work and the fixes identified in `source-sha256.json`. Hashes normalize
CRLF to LF. The user requested that known generic code defects be fixed and that
target evaluation be left to the team with precise instructions.

The code review covered configuration, source/build preparation, process/container
execution, triage, diff/signature correlation, pipeline comparison, reduction,
generated-regression transfer, replay, hardening/reporting, CLI, and target workflow
setup. Existing tests cover corresponding build modes, independent expectations,
status/exit priority, incomplete analysis, limits, evidence, and path/hash failures.
The comparison repository was not used as the correctness oracle for this audit.

## Reproduced and repaired defects

1. Byte-oriented reduction could split a UTF-8 code point in argv mode, then abort
   the entire evaluation with code 30. Unrepresentable candidates are now rejected
   before reference/target execution; the original representable input is retained.
2. Reference-command output is captured losslessly as Latin-1 bytes, but its JSON
   document must be decoded as UTF-8. Non-ASCII JSON now preserves the intended
   independently specified output bytes rather than inventing a different expectation.
3. A configured release build containing observed sanitizer symbols could be treated
   as ordinary release evidence. It now fails as a build/configuration contradiction
   before suite execution, while retaining the observed ELF record. Missing symbols
   alone are still not used as proof of instrumentation absence.
4. A security reproducer with a missing signature could claim clean executions as
   reproduction of `null`. Replay now requires a nonempty security identity, a valid
   kind, both artifacts and a valid finding side, and valid expected-result shape.
5. An existing `replay.json` symlink could overwrite another file. Replay rejects
   symlink bundles/outputs and uses contained-file checks for metadata and patch diff.

These repairs reuse the existing byte representation, reduction oracle, ELF inspection,
expectation validator, and path checks. No new dependency or target-specific logic was
introduced. Trusted operator configuration/reproducer metadata and a non-concurrently
modified evidence directory remain assumptions; this is not a hostile-writer filesystem
transaction or a cryptographic provenance system.

## Verification

- `red-windows.xml`: four reproduced failures; output-symlink case skipped because
  this Windows host lacks symlink permission.
- `red-linux.xml`: all **five regression tests failed** before the fixes, including
  the output-symlink case.
- `focused-windows.xml`: **131 passed, 7 symlink skips** for pipeline, cache transfer,
  and configuration checks after the fixes.
- `full-windows.xml`: **200 passed, 8 skipped**, Python 3.13.1. Skips are seven symlink
  cases and the native Linux container check.
- `full-linux.xml`: **208 passed, zero skips**, Python 3.12.3. This includes the five
  repaired cases and the existing harmless native fixture, not approved course targets.
- `verify-linux.log`: new verifier passed Black (28 files), standard Flake8 E/F/W/C90,
  the complete suite, and offline wheel construction. Docker host blkio/cgroup notices
  are retained as emitted; they did not fail the checks.
- Tested Linux source/tests, installed runtime source, and wheel Python source match
  the checkout after newline normalization. The retained artifact hashes are exact bytes.

Commands used with cached dependencies on `PYTHONPATH`:

```text
python -m pytest -q tests/test_pipeline.py -k 'reference_json_decodes or argv_reduction or instrumented_release or missing_security_identity or output_symlink' --basetemp=.diffsheriff/audit-red --junitxml=artifacts/checkpoints/code-audit/red-windows.xml
python3 -m pytest -q tests/test_pipeline.py -k 'reference_json_decodes or argv_reduction or instrumented_release or missing_security_identity or output_symlink' --basetemp=/var/tmp/diffsheriff-audit-red --junitxml=artifacts/checkpoints/code-audit/red-linux.xml
python -m pytest -q tests/test_pipeline.py tests/test_regressions.py tests/test_config.py --basetemp=.diffsheriff/audit-focused --junitxml=artifacts/checkpoints/code-audit/focused-windows.xml
python -m pytest -q tests/ --basetemp=.diffsheriff/audit-full --junitxml=artifacts/checkpoints/code-audit/full-windows.xml
DIFFSHERIFF_TEST_IMAGE=diffsheriff:code-audit bash verify.sh
```

The last command ran in the fresh Linux source snapshot recorded in `verification.json`.
Cached development dependencies were used; this does not replace final clean-room
delivery verification. The wheel is retained in `package/`.

Raw failing-test XML preserves pytest's original whitespace. Git whitespace checks
exclude `red-linux.xml`, `red-windows.xml`, and the preceding checkpoint's `red.xml`;
all other staged files pass the check.

## Retained evidence and remaining work

`synthetic/utf8-argv/` retains the harmless UTF-8 input, expectation/config, mock build
files, run/reproducer data, and generated regression from the successful regression
test. Synthetic sanitizer text and placeholder image identities are explicitly not
real-target findings. `synthetic/reference-decoding.json` records input JSON bytes
and the matching independently expected/decoded result.

`native/` retains the harmless echo fixture, configuration/corpus, four source archives,
four binaries, report, runtime source hashes, and image-build log. Its result is code
40 with functional PASS and 36 suite executions, since it has no designated security
flaw. All four source/binary hashes and six case-input hashes match the report.

Runtime image: `sha256:a82a5b7e8a58caea82cc8fa066b656fc96c9b4ec4f4b8a9f4fe11d080e8f65c1`.
It overlays these sources onto `diffsheriff:reference-parity`
(`sha256:b5bbef31e8ab12df9a99d0b446a0edf5f19294fbc66a43e13aca1b49742a0ab6`), tagged
`diffsheriff:code-audit-base`, with the same offline COPY/pip-install Dockerfile shown
in the preceding checkpoint and `docker build --network=none -t diffsheriff:code-audit .`.
`verification.json` identifies the snapshot and wheel; `artifact-sha256.json` hashes
all checkpoint files except itself. Paths embedded in reports are original provenance.

No known generic implementation defect found by this bounded review is deferred.
That is not a guarantee of zero bugs or full marks on unseen targets. No course-target
scenario, target CI run, unseen evaluation, clean-room delivery, or defense was run.
The team's exact remaining preparation and execution steps are in
[evaluation.md](../../../docs/evaluation.md); live review/approval gates remain in
[the roadmap](../../../docs/roadmap.md). No commit or push was performed by the agent.
