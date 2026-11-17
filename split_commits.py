#!/usr/bin/env python3
"""Split the prepared DiffSheriff changes. Preview by default; never push.

    python split_commits.py
    python split_commits.py --apply          # three commits
    python split_commits.py --commits 2 --apply

Uses the caller's configured Git identity and ordinary commit hooks. If a commit
fails, earlier commits stay intact and remaining file changes are preserved.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args])


def paths(root, *args):
    return {os.fsdecode(p) for p in git(root, *args).split(b"\0") if p}


def category(path):
    if path.startswith("evaluation/target1/"):
        return 0
    if path in {
        ".github/workflows/validate_target.yml",
        "tests/test_target_assets.py",
    } or path.startswith("evaluation/target2/"):
        return 1
    if path.startswith(
        ("docs/", "artifacts/checkpoints/zlib-contract-ci/")
    ) or path in {
        "artifacts/README.md",
        "split_commits.py",
        "tests/test_split_commits.py",
    }:
        return 2
    raise ValueError(f"Unassigned change; review before splitting: {path}")


def plan(root, count):
    if paths(root, "diff", "--name-only", "--diff-filter=U", "-z"):
        raise ValueError("Resolve merge conflicts before splitting commits")
    staged = paths(root, "diff", "--cached", "--name-only", "--no-renames", "-z")
    unstaged = paths(root, "diff", "--name-only", "--no-renames", "-z")
    if staged & unstaged:
        raise ValueError(
            "Partially staged files: stage or unstage each file " "completely first"
        )
    pending = (
        staged
        | unstaged
        | paths(root, "ls-files", "--others", "--exclude-standard", "-z")
    )
    groups = [[], [], []]
    for path in sorted(pending):
        groups[category(path)].append(path)
    if count == 2:
        return [
            (
                "fix: define bounded zlib expectations and prepare CI sources",
                groups[0] + groups[1],
            ),
            ("chore: document scope and retain verified handoff", groups[2]),
        ]
    return [
        ("fix: define bounded zlib contract and build settings", groups[0]),
        ("ci: prepare delivered target sources and test assets", groups[1]),
        ("chore: document scope and retain verified handoff", groups[2]),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--commits", type=int, choices=(2, 3), default=3)
    parser.add_argument(
        "--apply", action="store_true", help="create commits; default is preview only"
    )
    args = parser.parse_args(argv)
    try:
        root = Path(
            git(Path(__file__).resolve().parent, "rev-parse", "--show-toplevel")
            .decode()
            .strip()
        )
        if root != Path(__file__).resolve().parent:
            raise ValueError("Run this helper from the DiffSheriff repository root")
        git(root, "rev-parse", "--verify", "HEAD")
        groups = [
            (message, files) for message, files in plan(root, args.commits) if files
        ]
        if not groups:
            print("No pending changes.")
            return 0
        for number, (message, files) in enumerate(groups, 1):
            print(f"{number}. {message} ({len(files)} files)", flush=True)
        if not args.apply:
            print(
                "Preview only. Add --apply to create these commits. "
                "Nothing will be pushed."
            )
            return 0
        author = git(root, "var", "GIT_AUTHOR_IDENT").decode().strip()
        git(root, "var", "GIT_COMMITTER_IDENT")
        print(f"Using configured author: {author}", flush=True)
        # Unstage the known changes only; working-tree contents remain untouched.
        subprocess.run(
            ["git", "-C", str(root), "reset", "--quiet", "HEAD", "--"], check=True
        )
        for message, files in groups:
            subprocess.run(
                [
                    "git",
                    "--literal-pathspecs",
                    "-C",
                    str(root),
                    "add",
                    "-A",
                    "--",
                    *files,
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-m", message], check=True
            )
        remaining = git(root, "status", "--short")
        if remaining:
            print(remaining.decode(errors="replace"), file=sys.stderr)
            raise ValueError(
                "Changes remain after committing; inspect them before proceeding"
            )
        print("Commits created. Nothing pushed.")
        return 0
    except (ValueError, subprocess.CalledProcessError) as error:
        print(
            f"Stopped: {error}. No reset of committed history was performed.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
