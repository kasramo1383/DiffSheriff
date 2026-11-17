# Bounded zlib contract and CI source preparation

This checkpoint addresses F01's selected zlib completion/status contract and the
source-preparation part of F10. The [target record](../../../docs/target_scenarios.md#bounded-zlib-functional-contract)
owns the contract and its independent API-documentation basis. No project or target
source commits were created for this work; existing bundle identities are unchanged.

All selected zlib bytes within 0 through 65,536 bytes are valid compression input.
The reference now predicts successful API completion with valid_input true in that
scope and explicitly refuses larger input. Suite and generated labels agree. This
checks the declared driver status contract, not byte-for-byte compressed output or
all library functionality. Independent system-zlib round trips support payload validity;
no expected value is copied from the patched program. Instructor approval is pending.

The workflow now clones the two delivered bundles before validation, stops on a missing
bundle and refuses existing destinations. Tests run that exact shell step in a fresh
directory and verify every configured source commit. Existing CLI tests cover real
exit gating. Successful selected-target CI comparisons still depend on F09/F02 work.
No additional service, cache strategy or provider workflow was added.

## Retained evidence

- `focused.xml`: target assets and existing pipeline checks, including generated
  functional eligibility, reference scope, independent payload round trips and fresh
  workflow setup/refusal behavior.
- `clang-build-failed.json`: failed Clang build without HAVE_UNISTD_H. The old custom
  Makefile omitted that platform definition, so gzip sources lacked unistd declarations.
- `native.json`: exact source/runtime/build identities and actual native results for
  baseline/correct/regression, both modes, selected inputs and three runs per case.
- `native/`: the corresponding six executables, with hashes in native.json. Inputs are
  the exact delivered files named and hashed there; they were not duplicated here.
- `full-linux.xml`, `verify-linux.log`, `verification.json`: full generic verification
  and package installation from a staged-source snapshot with matching source hashes.
- `package/`: wheel built in that verification.
- `source-sha256.json`: source/test/target-asset identities with CRLF normalized to LF.
- `artifact-sha256.json`: retained checkpoint bytes, excluding the manifest itself.

The native check uses the actual configured commands with Clang and HAVE_UNISTD_H in
both modes. All five chosen inputs finish successfully on baseline and correct. The
regression variant intentionally fails the large valid text and its existing reduced
case in both modes; other chosen inputs pass. The ordinary baseline security trigger
and incomplete-patch bypass matrix are not evaluated by this smoke check.

The PDF still requires the full selected-target matrices, security reproducers and
later-run checks. PNG reference/driver work, meaningful invalid-interface coverage
for zlib, actual hosted CI and instructor approval are not established by this record.
Prior generic checkpoint results remain associated with their original source/image.
