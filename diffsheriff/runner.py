"""Process execution; pipeline calls use fresh resource-limited Docker containers."""

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time
import uuid


@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    output_limited: bool = False
    resource_limited: bool = False
    command: list[str] = field(default_factory=list)
    container_state: dict = field(default_factory=dict)


def capture_command(args, timeout, payload=None, env=None, cwd=None, limit=1048576):
    """Bound memory while draining both streams, and kill the process on limits."""
    output = [bytearray(), bytearray()]
    overflow = threading.Event()
    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=cwd,
        start_new_session=os.name == "posix",
    )

    def drain(stream, buffer):
        with stream:
            while chunk := stream.read(4096):
                remaining = limit - len(buffer)
                buffer.extend(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()

    def feed():
        try:
            proc.stdin.write(payload)
            proc.stdin.flush()
        except (BrokenPipeError, OSError):
            pass
        finally:
            proc.stdin.close()

    readers = [
        threading.Thread(target=drain, args=(stream, buffer), daemon=True)
        for stream, buffer in zip((proc.stdout, proc.stderr), output)
    ]
    for thread in readers:
        thread.start()
    writer = None
    if payload is not None:
        writer = threading.Thread(target=feed, daemon=True)
        writer.start()
    deadline = time.monotonic() + timeout
    timed_out = False
    try:
        while proc.poll() is None:
            if overflow.is_set() or time.monotonic() >= deadline:
                timed_out = not overflow.is_set()
                break
            time.sleep(0.01)
    finally:
        # Also close inherited pipes held by descendants after their parent exits.
        if os.name == "posix":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif proc.poll() is None:
            proc.kill()
        proc.wait()
        for thread in readers:
            thread.join(timeout=1)
        if writer:
            writer.join(timeout=1)
    return ExecutionResult(
        proc.returncode,
        output[0].decode("latin1"),
        output[1].decode("latin1"),
        timed_out,
        overflow.is_set(),
        command=list(args),
    )


def execute_target(
    binary_path,
    input_payload,
    input_method="file",
    file_flag="--file",
    fixed_args=None,
    env_vars=None,
    timeout_sec=5.0,
):
    """Local primitive for trusted tests; the validation pipeline uses Docker."""
    args = [str(binary_path), *(fixed_args or [])]
    env = os.environ.copy()
    env.update(env_vars or {})
    with tempfile.TemporaryDirectory() as directory:
        stdin = None
        if input_method == "stdin":
            stdin = input_payload
        elif input_method == "argv":
            # UTF-8 is explicit; arbitrary binary payloads require stdin or file.
            args.append(input_payload.decode("utf-8"))
        elif input_method == "file":
            path = Path(directory) / "input"
            path.write_bytes(input_payload)
            args.extend(([file_flag] if file_flag else []) + [str(path)])
        else:
            raise ValueError(f"Unsupported input method: {input_method}")
        return capture_command(args, timeout_sec, stdin, env=env)


def resolve_image(image):
    proc = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    info = json.loads(proc.stdout)[0]
    if info["Os"] != "linux" or info["Architecture"] != "amd64":
        raise ValueError("execution.image must be a local Linux amd64 image")
    return info["Id"]


def run_container(
    source,
    command,
    settings,
    *,
    timeout=None,
    payload=None,
    input_file=None,
    writable=False,
    output_limit=None,
):
    """Expose only the target snapshot and one optional input, never the repository."""
    name = "diffsheriff-" + uuid.uuid4().hex
    source = Path(source).resolve()
    if "," in str(source):
        raise ValueError("Docker mount paths cannot contain commas")
    mount = f"type=bind,src={source},dst=/src" + ("" if writable else ",readonly")
    uid = str(os.getuid()) if hasattr(os, "getuid") else "1000"
    args = [
        "docker",
        "run",
        "--name",
        name,
        "--pull=never",
        "--platform=linux/amd64",
        "--network=none",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--read-only",
        "--user",
        uid if writable else "65534:65534",
        "--memory",
        f"{settings.memory_mb}m",
        "--memory-swap",
        f"{settings.memory_mb}m",
        "--cpus",
        str(settings.cpus),
        "--pids-limit",
        str(settings.pids_limit),
        "--ulimit",
        "core=0",
        "--tmpfs",
        "/tmp:rw,nosuid,size=256m,mode=1777",
        "--mount",
        mount,
        "--workdir",
        "/src",
        "--log-driver=none",
    ]
    if input_file:
        input_file = Path(input_file).resolve()
        if "," in str(input_file):
            raise ValueError("Docker mount paths cannot contain commas")
        args.extend(["--mount", f"type=bind,src={input_file},dst=/input,readonly"])
    for key, value in sorted(settings.environment_variables.items()):
        args.extend(["--env", f"{key}={value}"])
    if payload is not None:
        args.append("-i")
    args.extend(["--entrypoint", command[0], settings.image, *command[1:]])
    try:
        result = capture_command(
            args,
            timeout or settings.timeout_seconds,
            payload,
            limit=output_limit or settings.output_limit_bytes,
        )
        if not result.timed_out and not result.output_limited:
            inspected = subprocess.run(
                ["docker", "inspect", "--format", "{{json .State}}", name],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            state = json.loads(inspected.stdout)
            result.container_state = state
            if state.get("Error"):
                raise RuntimeError(f"Container operation failed: {state['Error']}")
            if result.exit_code != state["ExitCode"]:
                raise RuntimeError(f"Docker client failed: {result.stderr}")
            result.resource_limited = bool(state.get("OOMKilled"))
        return result
    finally:
        cleanup = subprocess.run(
            ["docker", "rm", "--force", name],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if cleanup.returncode and "No such container" not in cleanup.stderr:
            raise RuntimeError(f"Container cleanup failed: {cleanup.stderr}")


def execute_container(source, binary, payload, settings):
    args = ["/src/" + binary, *settings.fixed_arguments]
    with tempfile.TemporaryDirectory() as directory:
        input_file = None
        stdin = None
        if settings.input_method == "stdin":
            stdin = payload
        elif settings.input_method == "argv":
            value = payload.decode("utf-8")
            if "\0" in value:
                raise ValueError("argv payload contains NUL; use file or stdin")
            args.append(value)
        else:
            input_file = Path(directory) / "input"
            input_file.write_bytes(payload)
            input_file.chmod(0o644)
            if settings.file_argument_flag:
                args.append(settings.file_argument_flag)
            args.append("/input")
        # The trusted supervisor preserves negative signal return codes, unlike
        # Docker's ambiguous 128+signal process status convention.
        wrapped = [
            "python3",
            "-I",
            "-m",
            "diffsheriff.runner",
            str(settings.timeout_seconds),
            str(settings.output_limit_bytes),
            *args,
        ]
        result = run_container(
            source,
            wrapped,
            settings,
            payload=stdin,
            input_file=input_file,
            timeout=settings.timeout_seconds + 15,
            output_limit=settings.output_limit_bytes * 12 + 65536,
        )
        if result.timed_out or result.resource_limited or result.output_limited:
            return result
        if result.exit_code:
            raise RuntimeError(f"Execution supervisor failed: {result.stderr}")
        child = ExecutionResult(**json.loads(result.stdout))
        child.container_state = result.container_state
        return child


if __name__ == "__main__":
    from dataclasses import asdict
    import sys

    outcome = capture_command(
        sys.argv[3:],
        float(sys.argv[1]),
        sys.stdin.buffer.read(),
        limit=int(sys.argv[2]),
    )
    print(json.dumps(asdict(outcome)))
