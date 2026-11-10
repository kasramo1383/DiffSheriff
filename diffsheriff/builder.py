"""
Dual-build orchestrator: builds target binaries in Release and Sanitized modes.
"""

from dataclasses import dataclass
import hashlib
from pathlib import Path
import shutil
import subprocess
from typing import Optional, Tuple


@dataclass
class BuildArtifacts:
    release_binary: Path
    release_sha256: str
    sanitized_binary: Path
    sanitized_sha256: str


def compute_sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_command(command: str, cwd: Path) -> Tuple[int, str, str]:
    proc = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def build_dual_matrix(
    repo_dir: Path,
    clean_cmd: str,
    release_cmd: str,
    release_bin_relpath: str,
    sanitized_cmd: str,
    sanitized_bin_relpath: str,
) -> Tuple[bool, Optional[BuildArtifacts], str]:
    """
    Builds both Release and Sanitized variants independently.
    Returns (success, artifacts, error_message).
    """
    artifact_dir = repo_dir / ".diffsheriff" / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # 1. Clean
    if clean_cmd:
        code, out, err = run_command(clean_cmd, repo_dir)
        if code != 0:
            return False, None, f"Pre-release clean failed (code {code}):\n{err}\n{out}"

    # 2. Release Build
    code, out, err = run_command(release_cmd, repo_dir)
    rel_path = repo_dir / release_bin_relpath
    if code != 0 or not rel_path.exists():
        return False, None, f"Release build failed (code {code}):\n{err}\n{out}"
    release_copy = artifact_dir / f"release-{rel_path.name}"
    shutil.copy2(rel_path, release_copy)
    rel_hash = compute_sha256(release_copy)

    # 3. Clean before sanitized build
    if clean_cmd:
        code, out, err = run_command(clean_cmd, repo_dir)
        if code != 0:
            return (
                False,
                None,
                f"Pre-sanitized clean failed (code {code}):\n{err}\n{out}",
            )

    # 4. Sanitized Build
    code, out, err = run_command(sanitized_cmd, repo_dir)
    san_path = repo_dir / sanitized_bin_relpath
    if code != 0 or not san_path.exists():
        return False, None, f"Sanitized build failed (code {code}):\n{err}\n{out}"
    sanitized_copy = artifact_dir / f"sanitized-{san_path.name}"
    shutil.copy2(san_path, sanitized_copy)
    san_hash = compute_sha256(sanitized_copy)

    artifacts = BuildArtifacts(
        release_binary=release_copy,
        release_sha256=rel_hash,
        sanitized_binary=sanitized_copy,
        sanitized_sha256=san_hash,
    )
    return True, artifacts, ""


def prepare_sources(repository, commit, destination):
    """Export a commit without changing the user's checkout or running Git hooks."""
    import stat
    import zipfile
    from diffsheriff.config import relative_path

    destination.mkdir(parents=True, exist_ok=False)
    resolved = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--verify", commit + "^{commit}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.strip()
    if resolved != commit:
        raise ValueError("Source ref did not resolve to the requested exact commit")
    tree = subprocess.run(
        ["git", "-C", str(repository), "ls-tree", "-r", commit],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    if any(line.startswith("160000 ") for line in tree.splitlines()):
        raise ValueError("Submodules must be vendored into the target snapshot")
    archive = destination.parent / (destination.name + ".zip")
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "archive",
            "--format=zip",
            "--output",
            str(archive),
            commit,
        ],
        capture_output=True,
        check=True,
        timeout=60,
    )
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            relative_path(entry.filename.rstrip("/"), "source archive path")
            mode = entry.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(
                    "Source symlinks are not supported; vendor regular files"
                )
            output = destination / entry.filename
            if entry.is_dir():
                output.mkdir(parents=True, exist_ok=True)
            else:
                output.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(entry) as src, output.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                output.chmod(0o755 if mode & 0o111 else 0o644)
    return archive


def build_isolated_matrix(repository, commit, destination, build, execution, records):
    """Build each mode from a pristine snapshot and keep logs even on failure."""
    from dataclasses import asdict
    from diffsheriff.runner import run_container

    artifacts = {}
    for mode in ("release", "sanitized"):
        source = destination / mode
        archive = prepare_sources(repository, commit, source)
        record = {
            "commit": commit,
            "source_archive": str(archive),
            "source_archive_sha256": compute_sha256(archive),
            "commands": [],
        }
        records[mode] = record
        for command in (build.clean_command, getattr(build, mode + "_command")):
            if not command:
                continue
            result = run_container(
                source,
                ["/bin/sh", "-c", command],
                execution,
                timeout=build.timeout_seconds,
                writable=True,
            )
            record["commands"].append(asdict(result))
            if (
                result.exit_code
                or result.timed_out
                or result.output_limited
                or result.resource_limited
            ):
                raise RuntimeError(f"{mode} build failed; see retained command output")
        relative = getattr(build, mode + "_binary_path")
        binary = source / relative
        if (
            not binary.is_file()
            or binary.is_symlink()
            or not binary.resolve().is_relative_to(source.resolve())
        ):
            raise ValueError(
                f"Build did not produce a regular contained binary: {relative}"
            )
        binary.chmod(0o755)
        record.update(
            binary=relative, sha256=compute_sha256(binary), source=str(source)
        )
        artifacts[mode] = (source, relative)
    return artifacts
