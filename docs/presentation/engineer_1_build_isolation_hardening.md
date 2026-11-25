# Eng 1 presentation guide

**Presenter:** Eng 1

**Topic:** Configuration validation, build, execution isolation, and ELF hardening.

This guide starts from zero. Your job is to explain how the same approved source
snapshot becomes two trustworthy binaries and how every run is bounded. You do
not need to explain sanitizer parsing or target scenarios in detail; point to
Engineers 2–4 for those parts. Your share includes the configuration validator
previously listed under Engineer 4. The additional breadth balances the denser
algorithms in Engineers 2 and 3's parts.

Your handoff: accept a YAML configuration, validate it, and supply exact build
records and bounded execution results. Engineer 2 interprets those results;
Engineer 4 makes the final comparison decisions. Follow the shared 8-minute
rehearsal structure: 3 minutes code, 2 evidence, 2 change, 1 question.

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

### `diffsheriff/config.py`: validate the request first

YAML is the readable settings file. A Git commit hash identifies one saved source
snapshot; a branch name such as `main` can move. `DiffSheriffConfig.from_yaml`
therefore requires a full commit hash for both sides. This is the actual check:

```python
for key in ("base_ref", "patch_ref"):
    value = _string(target.get(key), f"target.{key}")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
        raise ConfigError(f"target.{key} must be a full Git commit hash")
    refs[key] = value
```

`relative_path` rejects absolute or escaping paths; `from_yaml` also rejects
invalid limits and unsupported input methods. A path such as `build/program`
stays inside the source snapshot. `../program` could escape it and is rejected.
Engineer 4 consumes the validated settings; you explain these validation rules.

For your change demonstration, run `python` from the repository root to open
Python's interactive prompt, paste this block, then press Enter on a blank line:

```python
from diffsheriff.config import ConfigError, relative_path

for value in ("build/program", "../program"):
    try:
        print(value, "-> ACCEPT:", relative_path(value, "binary_path"))
    except ConfigError as error:
        print(value, "-> REJECT:", error)

```

The first path is accepted and the second is rejected. The change is the path
value passed into the same function. Explain the condition that caused the
change. This is a configuration-validation exercise; it does not build a target.
Use `exit()` to leave Python. For an instructor-requested implementation change,
locate the corresponding condition in `relative_path` and its test in
`tests/test_config.py::test_binary_path_cannot_escape` before editing.

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
python -m pytest -q tests/test_config.py
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

For your evidence slot, show a retained build's commit, binary SHA-256, and ELF
protection fields. Explain that SHA-256 is a fingerprint of the actual bytes.
Be ready to answer: “Why reject `main` and `../program` before building?”

