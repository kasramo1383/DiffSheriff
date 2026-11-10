"""
Process execution runner with timeout watchdog and multi-modal I/O dispatch.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Dict, List, Optional


@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool


def execute_target(
    binary_path: Path,
    input_payload: bytes,
    input_method: str = "file",  # "stdin", "argv", "file"
    file_flag: Optional[str] = "--file",
    fixed_args: Optional[List[str]] = None,
    env_vars: Optional[Dict[str, str]] = None,
    timeout_sec: float = 5.0,
) -> ExecutionResult:
    """
    Executes a target binary with payload via stdin, argv, or a temporary file.
    """
    args = [str(binary_path)]
    if fixed_args:
        args.extend(fixed_args)

    temp_file_obj = None
    stdin_data = None

    try:
        if input_method == "stdin":
            stdin_data = input_payload
        elif input_method == "argv":
            payload_str = input_payload.decode("latin1", errors="replace")
            args.append(payload_str)
        elif input_method == "file":
            temp_file_obj = tempfile.NamedTemporaryFile(delete=False)
            temp_file_obj.write(input_payload)
            temp_file_obj.flush()
            temp_file_obj.close()
            if file_flag:
                args.extend([file_flag, temp_file_obj.name])
            else:
                args.append(temp_file_obj.name)
        else:
            raise ValueError(f"Unsupported input method: {input_method}")

        process_env = os.environ.copy()
        if env_vars:
            process_env.update(env_vars)

        proc = subprocess.run(
            args,
            input=stdin_data,
            capture_output=True,
            timeout=timeout_sec,
            env=process_env,
        )

        return ExecutionResult(
            exit_code=proc.returncode,
            stdout=proc.stdout.decode("latin1", errors="replace"),
            stderr=proc.stderr.decode("latin1", errors="replace"),
            timed_out=False,
        )

    except subprocess.TimeoutExpired as e:
        return ExecutionResult(
            exit_code=-1,
            stdout=(e.stdout or b"").decode("latin1", errors="replace"),
            stderr=(e.stderr or b"").decode("latin1", errors="replace"),
            timed_out=True,
        )
    finally:
        if temp_file_obj and Path(temp_file_obj.name).exists():
            try:
                Path(temp_file_obj.name).unlink()
            except OSError:
                pass
