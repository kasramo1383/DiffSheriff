# Retained evidence integrity repair

Commit `ace8d1fdb9831f342f2c3e0fed8c7b0ab1548075` corrected status text in three
checkpoint READMEs but left their recorded SHA-256 values unchanged. That made the
delivered cache-import, minimized-results, and reference-parity manifests stale even
though their underlying run evidence was unchanged.

`red.xml` records the new integrity test failing on those three README entries before
the repair. The manifests now contain the hashes of the delivered README bytes.
`green.xml` records all five existing checkpoint manifests passing afterward, and
`full-windows.xml` records the complete suite on Windows with Python 3.13.1: 205 passed
and 8 platform-dependent symlink/native-Linux skips. The focused integrity test also
passed all five cases under Linux/WSL with Python 3.12.3. Black and the configured
Flake8 E/F/W/C90 checks passed under Linux for all 29 source and test files.

The new test discovers every `artifacts/checkpoints/*/artifact-sha256.json`, requires a
nonempty mapping, confines each named artifact to its checkpoint, requires the file to
exist, and compares its exact bytes to the recorded digest. It prevents later evidence
documentation edits from silently invalidating retained manifests.

`red.xml` preserves pytest's raw failing output, including its diagnostic whitespace.
The staged whitespace check excludes only that evidence file; all other changed files
pass the check.

The test changes no validator behavior and supplies no target-acceptance evidence.
Course-target execution remains gated by the approval and ground-truth records in
[`docs/target_scenarios.md`](../../../docs/target_scenarios.md).
