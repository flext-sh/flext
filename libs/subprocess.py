from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


def run_checked(command: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, check=False)
    if result.returncode != 0:
        cmd = shlex.join(command)
        raise RuntimeError(f"command failed ({result.returncode}): {cmd}")


def run_capture(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        cmd = shlex.join(command)
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"command failed ({result.returncode}): {cmd}: {detail}")
    return result.stdout.strip()
