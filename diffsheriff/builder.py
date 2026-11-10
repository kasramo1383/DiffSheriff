"""
Dual-build orchestrator: builds target binaries in Release and Sanitized modes.
"""

from dataclasses import dataclass
import hashlib
from pathlib import Path
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
    # 1. Clean
    if clean_cmd:
        run_command(clean_cmd, repo_dir)

    # 2. Release Build
    code, out, err = run_command(release_cmd, repo_dir)
    rel_path = repo_dir / release_bin_relpath
    if code != 0 or not rel_path.exists():
        return False, None, f"Release build failed (code {code}):\n{err}\n{out}"
    rel_hash = compute_sha256(rel_path)

    # 3. Clean before sanitized build
    if clean_cmd:
        run_command(clean_cmd, repo_dir)

    # 4. Sanitized Build
    code, out, err = run_command(sanitized_cmd, repo_dir)
    san_path = repo_dir / sanitized_bin_relpath
    if code != 0 or not san_path.exists():
        return False, None, f"Sanitized build failed (code {code}):\n{err}\n{out}"
    san_hash = compute_sha256(san_path)

    artifacts = BuildArtifacts(
        release_binary=rel_path,
        release_sha256=rel_hash,
        sanitized_binary=san_path,
        sanitized_sha256=san_hash,
    )
    return True, artifacts, ""
