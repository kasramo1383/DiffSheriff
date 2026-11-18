# Build and hardening evidence

F04/F05 evidence for the selected target versions.

**Scope.** Confirm that every selected version builds in corresponding ordinary and
instrumented modes, record the actual toolchain, build commands, dependencies, source
identities and release-binary hardening (NX/PIE/RELRO/canary), and verify the configured
hardening downgrade reporting. No packaging change is made unless a version cannot be
built or the refs/bundles/configs disagree.

**Environment.** No container runtime was available (the environment lacks
`CAP_SYS_ADMIN`), so the delivered bundles were built and inspected natively on Linux
x86_64. Toolchain: Debian clang 14.0.6, GNU make 4.3, gcc 15.3.0; Target 2 links the
system zlib (`libz.so.1.3.2`) via `-lz`, as the target record documents.

**Builds.** All eight versions (baseline/correct/incomplete/regression × release/sanitized)
for both targets compiled without error. Commands and identities are in `build.txt`.

**Hardening (release binaries).** Every target/version reports NX=True, PIE=True,
RELRO=partial, canary=False. The bundled Makefiles provide no explicit canary or
full-RELRO flags and the six selected configs impose no absolute all-enabled minimum, so
these observations are expected and do not fail the run.

**Downgrade reporting.** Baseline→correct reports no degradation; a deliberately weakened
build (`-no-pie -z norelro -z execstack -fno-stack-protector`) reports NX, PIE and RELRO
downgrades. `tests/test_hardening.py` passes (7).

**Source/bundle agreement.** `git bundle list-heads` shows all four configured commits in
both bundles, matching the six configs. No ref/bundle/config disagreement was found, so no
packaging change was required.

See `build.txt` for the raw transcript.