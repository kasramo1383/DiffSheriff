# F03 corpus review

Retained evidence for the F03 review of the selected target inputs and expectations.

**Scope.** Confirm the validity labels, expected exit/output behavior and representative
valid/boundary/invalid coverage of both target evaluation directories against the
contracts in `docs/target_scenarios.md`, and resolve whether the assignment requires a
per-target invalid input for the zlib compressor.

**Environment.** The review environment had no container runtime, so the delivered
Target 1 bundle was built and executed directly on native Linux x86_64:

- `git clone targets/target1/source.bundle` (baseline `88fb854d…`, correct `29abcf1b…`)
- `make release CC=clang 'CFLAGS=-O2 -I. -DHAVE_UNISTD_H'`
- Toolchain: Debian clang 14.0.6, GNU make 4.3, gcc 15.3.0.

**Findings.**

- `python -m pytest -q tests/test_target_assets.py` -> 11 passed.
- All six configs load. target1: 10 cases per variant, 0 with `valid_input: false`
  (valid 4, boundary 2, malicious 2, regression 2). target2: 4 cases per variant, 3
  invalid (valid 1, boundary 1, malicious 2).
- The zlib release driver returns 0 for every suite and generated payload, for a
  65537-byte file, and for 77 randomized/edge inputs, on both baseline and correct. The
  only non-zero exits are interface-level: a missing or unreadable path, or a missing
  `--file` (both return 1 with a diagnostic). Those conditions are not expressible as a
  suite payload.
- The `65537 -> exit 2` behavior exists only in `evaluation/target1/reference.py`; the
  target driver itself exits 0 at 65537. It is not target coverage.

**Resolution.** The assignment (p. 2) requires the tool to run valid, boundary and
invalid input suites on both versions; it does not require a target whose declared
interface accepts every byte string to supply a distinct invalid payload. Target 1
therefore adds no invalid payload and keeps its `invalid/` triggers labelled valid. The
invalid category is exercised by the tool's mandatory valid/boundary/malicious suites and
supplied with genuine rejected payloads by Target 2 (`boundary/empty.png` and the two
indexed `malicious/*.png`, all exit 2). No corpus or config file was changed.

See `probe.txt` for the raw transcript.