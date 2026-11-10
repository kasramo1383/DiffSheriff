"""Unit tests for process execution behavior."""

from pathlib import Path
import os
import sys

from diffsheriff.runner import execute_target


def test_custom_environment_does_not_remove_parent_environment():
    result = execute_target(
        Path(sys.executable),
        b"payload",
        input_method="argv",
        fixed_args=[
            "-c",
            "import os; "
            "print(os.environ['DIFFSHERIFF_TEST']); "
            "print(bool(os.environ.get('PATH')))",
        ],
        env_vars={"DIFFSHERIFF_TEST": "present"},
    )
    assert result.exit_code == 0
    assert result.stdout.splitlines() == ["present", "True"]
    assert os.environ.get("DIFFSHERIFF_TEST") is None
