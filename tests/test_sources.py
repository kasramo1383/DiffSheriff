"""Archive isolation and exact source handling without external targets."""

from pathlib import Path
import subprocess
import zipfile

import pytest
from diffsheriff.builder import prepare_sources


def test_export_keeps_checkout_and_retains_archive(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
        ).stdout.strip()

    git("init")
    (repo / "source.c").write_text("original")
    git("add", "source.c")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "fixture",
    )
    commit = git("rev-parse", "HEAD")
    (repo / "source.c").write_text("uncommitted user work")
    destination = tmp_path / "snapshot"
    archive = prepare_sources(repo, commit, destination)
    assert (destination / "source.c").read_text() == "original"
    assert (repo / "source.c").read_text() == "uncommitted user work"
    assert archive.is_file()
    assert not (destination / ".git").exists()


@pytest.mark.parametrize(
    "filename,mode",
    [("../escape", 0o100644), ("link", 0o120777), (".git/config", 0o100644)],
)
def test_unsafe_archives_are_rejected(tmp_path, monkeypatch, filename, mode):
    commit = "a" * 40

    def git(args, **kwargs):
        if "rev-parse" in args:
            return subprocess.CompletedProcess(args, 0, commit, "")
        if "ls-tree" in args:
            return subprocess.CompletedProcess(args, 0, "", "")
        output = Path(args[args.index("--output") + 1])
        with zipfile.ZipFile(output, "w") as archive:
            info = zipfile.ZipInfo(filename)
            info.external_attr = mode << 16
            archive.writestr(info, "payload")
        return subprocess.CompletedProcess(args, 0, b"", b"")

    monkeypatch.setattr("diffsheriff.builder.subprocess.run", git)
    with pytest.raises(ValueError):
        prepare_sources(tmp_path, commit, tmp_path / "snapshot")
    assert not (tmp_path / "escape").exists()
