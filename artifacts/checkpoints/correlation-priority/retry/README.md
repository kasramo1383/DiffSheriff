# Runtime rebuild retry and verification

The ordinary rebuild at revision `d68f152` again failed fetching the anonymous Docker
Hub token with HTTP 403. The same token endpoint returned HTTP 200 through the local
Windows HTTP proxy on port 10808, from both Windows and WSL. No response tokens were
retained. WSL reached the proxy at its Windows default gateway, not WSL localhost.

`build-direct.log` preserves the failed direct retry. `build-proxy.log` records a
successful build with proxy variables scoped to that process and predefined Docker
build arguments. The OS/dependency layers were cached; this is not a clean dependency
acquisition check. No daemon configuration or persistent proxy environment was changed.

`verification.json` records the new exact runtime image, installed correlator hash,
source identity, commands, actual test counts and package checks. The installed code
was checked against the workspace, and the image environment contained no proxy
variables. Verification ran with proxy variables removed and the runtime pinned by ID.

`verify-linux.log` and `full-linux.xml` retain the full generic verification, including
formatting, lint, the harmless native Docker matrix and package creation. `package/`
contains the resulting wheel, installed and invoked outside source. The original
pre-fix failure tests and overlong test strings are covered by the successful full
suite; historical failed logs remain unchanged in the parent checkpoint.

`source-sha256.json` uses CRLF-to-LF normalization. `artifact-sha256.json` hashes these
retained bytes, excluding itself. A temporary snapshot of staged files matched the
tested source hashes and was removed after verified copies of the results were kept.

This run resolves the earlier reliance on an older runtime for generic verification.
It establishes no selected-target functional correctness, F04 dependency pinning,
instructor approval or individual defense. See [the roadmap](../../../../docs/roadmap.md)
for the owning acceptance state and [usage](../../../../docs/usage.md#retrying-docker-hub-access-from-wsl)
for the build command if the direct networking problem recurs.
