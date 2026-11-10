"""Unit tests for build artifact retention and failure handling."""

import shutil

from diffsheriff.builder import build_dual_matrix, compute_sha256


def test_dual_build_retains_release_across_second_clean(tmp_path, monkeypatch):
    bin_dir = tmp_path / "bin"

    def fake_run(command, cwd):
        if command == "clean":
            shutil.rmtree(bin_dir, ignore_errors=True)
        elif command == "release":
            bin_dir.mkdir()
            (bin_dir / "target").write_bytes(b"release")
        elif command == "sanitized":
            bin_dir.mkdir()
            (bin_dir / "target-asan").write_bytes(b"sanitized")
        return 0, "", ""

    monkeypatch.setattr("diffsheriff.builder.run_command", fake_run)

    success, artifacts, error = build_dual_matrix(
        repo_dir=tmp_path,
        clean_cmd="clean",
        release_cmd="release",
        release_bin_relpath="bin/target",
        sanitized_cmd="sanitized",
        sanitized_bin_relpath="bin/target-asan",
    )

    assert success is True
    assert error == ""
    assert artifacts is not None
    assert artifacts.release_binary.read_bytes() == b"release"
    assert artifacts.sanitized_binary.read_bytes() == b"sanitized"
    assert artifacts.release_sha256 == compute_sha256(artifacts.release_binary)
    assert artifacts.sanitized_sha256 == compute_sha256(artifacts.sanitized_binary)


def test_clean_failure_stops_build(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "diffsheriff.builder.run_command",
        lambda command, cwd: (2, "", "clean failed"),
    )

    success, artifacts, error = build_dual_matrix(
        repo_dir=tmp_path,
        clean_cmd="clean",
        release_cmd="release",
        release_bin_relpath="bin/target",
        sanitized_cmd="sanitized",
        sanitized_bin_relpath="bin/target-asan",
    )

    assert success is False
    assert artifacts is None
    assert "Pre-release clean failed" in error
