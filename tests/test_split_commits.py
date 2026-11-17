"""Exercise the commit helper only in disposable Git repositories."""

from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    (tmp_path / "baseline").write_text("keep")
    git(tmp_path, "add", "baseline")
    git(tmp_path, "commit", "-m", "baseline")
    shutil.copyfile(ROOT / "split_commits.py", tmp_path / "split_commits.py")
    for name in [
        "evaluation/target1/reference.py",
        ".github/workflows/validate_target.yml",
        "docs/roadmap.md",
        "artifacts/checkpoints/zlib-contract-ci/binary",
    ]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\0\xffbinary" if name.endswith("binary") else b"new\n")
    git(tmp_path, "add", "--all")
    return tmp_path


def run(repo, *args):
    return subprocess.run(
        [sys.executable, str(repo / "split_commits.py"), *args],
        capture_output=True,
        text=True,
    )


def test_preview_preserves_history_and_staging(repo):
    head = git(repo, "rev-parse", "HEAD").stdout
    index = git(repo, "write-tree").stdout
    result = run(repo)
    assert result.returncode == 0 and "Preview only" in result.stdout
    assert git(repo, "rev-parse", "HEAD").stdout == head
    assert git(repo, "write-tree").stdout == index


@pytest.mark.parametrize("count", [2, 3])
def test_apply_groups_all_bytes_without_push_or_identity_changes(repo, count):
    original = git(repo, "write-tree").stdout
    result = run(repo, "--commits", str(count), "--apply")
    assert result.returncode == 0, result.stderr
    assert int(git(repo, "rev-list", "--count", "HEAD").stdout) == count + 1
    assert git(repo, "rev-parse", "HEAD^{tree}").stdout == original
    assert not git(repo, "status", "--porcelain").stdout
    assert git(repo, "config", "user.name").stdout.strip() == "Fixture"
    assert (
        git(repo, "log", "-1", "--format=%ae").stdout.strip()
        == "fixture@example.invalid"
    )
    assert "Nothing pushed" in result.stdout
    assert "No pending changes" in run(repo, "--apply").stdout


@pytest.mark.parametrize("problem", ["unknown", "partial", "identity"])
def test_preflight_failure_preserves_staging_and_history(repo, problem):
    if problem == "unknown":
        (repo / "unrelated").write_text("keep")
    elif problem == "partial":
        (repo / "docs/roadmap.md").write_text("unstaged work")
    else:
        git(repo, "config", "user.name", "")
        git(repo, "config", "user.email", "")
    head = git(repo, "rev-parse", "HEAD").stdout
    index = git(repo, "write-tree").stdout
    assert run(repo, "--apply").returncode != 0
    assert git(repo, "rev-parse", "HEAD").stdout == head
    assert git(repo, "write-tree").stdout == index


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX commit hook")
def test_failed_commit_hook_keeps_work_and_can_resume(repo):
    hook = repo / ".git/hooks/pre-commit"
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    head = git(repo, "rev-parse", "HEAD").stdout
    assert run(repo, "--apply").returncode != 0
    assert git(repo, "rev-parse", "HEAD").stdout == head
    assert (repo / "docs/roadmap.md").read_text() == "new\n"
    hook.unlink()
    assert run(repo, "--apply").returncode == 0


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX commit hook")
def test_later_failure_preserves_completed_commit_and_resumes(repo):
    hook = repo / ".git/hooks/pre-commit"
    hook.write_text('#!/bin/sh\n[ "$(git rev-list --count HEAD)" -ne 2 ]\n')
    hook.chmod(0o755)
    assert run(repo, "--apply").returncode != 0
    assert int(git(repo, "rev-list", "--count", "HEAD").stdout) == 2
    assert (repo / "docs/roadmap.md").read_text() == "new\n"
    hook.unlink()
    assert run(repo, "--apply").returncode == 0
    assert int(git(repo, "rev-list", "--count", "HEAD").stdout) == 4
    assert not git(repo, "status", "--porcelain").stdout
