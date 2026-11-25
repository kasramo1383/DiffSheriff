# Engineer 1 presentation guide

**Owner:** Mohammadreza Izadi (402110916)

**Topic:** Build, execution isolation, and ELF hardening.

This guide starts from zero. Your job is to explain how the same approved source
snapshot becomes two trustworthy binaries and how every run is bounded. You do
not need to explain sanitizer parsing or target scenarios in detail; point to
Engineers 2–4 for those parts.

## 1. The story to tell

DiffSheriff first exports an exact Git commit. It then builds a normal **release**
binary and a **sanitized** binary from separate clean directories. The release
binary represents ordinary user behavior. The sanitized binary is for useful
diagnostic output such as AddressSanitizer. If both modes were built in one dirty
directory, old object files could make the comparison untrustworthy.

At execution time, the target is placed in a fresh Linux amd64 Docker container:
no network, no Linux capabilities, no new privileges, read-only root filesystem,
non-root user when possible, bounded memory/CPU/processes/output, and a timeout.
The source snapshot and one input are the only mounts. This is containment and
repeatability, not an exploit mechanism.

Finally, `hardening.py` inspects the produced ELF for NX, PIE, RELRO, stack
canary indicators, and sanitizer/FORTIFY symbols. It compares base and patch
release binaries and records any degradation.

## 2. Files and exact code to know

### `diffsheriff/builder.py`

`prepare_sources` proves that the requested ref resolves to the same full commit,
rejects submodules/symlinks, and extracts a Git archive. The key check is:

```python
resolved = subprocess.run(
    ["git", "-C", str(repository), "rev-parse", "--verify", commit + "^{commit}"],
    check=True,
).stdout.strip()
if resolved != commit:
    raise ValueError("Source ref did not resolve to the requested exact commit")
```

`build_isolated_matrix` loops over `("release", "sanitized")`, calls
`run_container` for clean/build commands, retains command output, and hashes the
resulting binary. The important safety check is that the binary is a regular
file contained inside the snapshot:

```python
if not binary.is_file() or binary.is_symlink() \
        or not binary.resolve().is_relative_to(source.resolve()):
    raise ValueError("Build did not produce a regular contained binary")
```

Changing `release_command`, `sanitized_command`, or a binary path in a target
YAML changes what is built and can cause exit 30 if the command/path is wrong.
Changing the commit ref changes the source identity and is forbidden unless the
new full hash is instructor-approved.

### `diffsheriff/runner.py`

The container command is assembled in `run_container`:

```python
"--pull=never", "--platform=linux/amd64", "--network=none",
"--cap-drop=ALL", "--security-opt=no-new-privileges", "--read-only",
"--memory", f"{settings.memory_mb}m", "--cpus", str(settings.cpus),
"--pids-limit", str(settings.pids_limit), "--ulimit", "core=0",
```

The source is mounted at `/src`; an optional input is mounted read-only at
`/input`. The Docker image must already be local (`--pull=never`), so a network
failure cannot silently change the run. `capture_command` drains stdout and
stderr while enforcing the timeout/output limit.

Behavior knobs live in `TargetExecutionSection` (`diffsheriff/config.py:65-76`):

| Setting | If lowered too far |
| --- | --- |
| `timeout_seconds` | `timed_out=True`, usually exit 40/inconclusive. |
| `memory_mb`, `cpus`, `pids_limit` | Resource limit or OOM evidence; not a security finding. |
| `output_limit_bytes` | `output_limited=True`; triage reports an output limit. |
| `environment_variables` | Sanitizer symbolization and program behavior can change. |

Safe defense demo: copy a harmless config, set `execution.timeout_seconds: 0.01`,
run one fixture, show the timeout note, then restore the value. Do not use a
malicious input and do not commit this temporary change.

### `diffsheriff/hardening.py`

`inspect_elf_hardening` reads program headers and symbol tables. The result is a
small record:

```python
HardeningResult(nx, pie, relro, bool(canary_symbols), indicators)
```

`compare_hardening` warns when patch loses NX, PIE, canary, or RELRO level. A
warning is retained in the report and can make analysis incomplete; it is not
automatically proof that the patch is functionally wrong.

## 3. How to run your part

```bash
python -m pip install -e ".[dev]"
docker build --platform linux/amd64 -t diffsheriff:local -f docker/Dockerfile .
python -m pytest -q tests/test_builder.py tests/test_runner.py tests/test_hardening.py
```

For the whole matrix, use `bash scripts/run_matrix.sh`; do not manually replace
the image or force an exit code. If Docker Hub is blocked, pull the approved
mirror image once, tag it locally as needed, or build with the prepared WSL/Docker
environment. The repository must record the image name and evidence honestly;
do not hard-code a private mirror into source.

## 4. Three sentences to memorize

1. “Release and sanitized builds come from separate exact snapshots, so stale
   objects cannot mix modes.”
2. “The container is intentionally offline and resource-bounded; a timeout or
   OOM is incomplete evidence, not a vulnerability verdict.”
3. “ELF inspection is evidence about protection state; `compare_hardening` reports
   a downgrade instead of pretending the binary is secure.”

