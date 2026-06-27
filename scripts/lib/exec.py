"""Process execution and dispatch-guard layer for promoted commands."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import NoReturn

from scripts.lib.registry import ROOT, Command


def run(command: Command) -> int:
    env = command_env(command)
    if command.path.suffix == ".py":
        return run_python(command, env)
    return subprocess.run(
        ["bash", str(command.path)], cwd=str(ROOT), env=env, check=False
    ).returncode


def run_make(
    target: str,
    *,
    make_args: Sequence[str] = (),
    extra_env: Mapping[str, str] | None = None,
) -> int:
    """Run a Makefile target and return the process exit code."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    command = ("make", target, *make_args)
    result = subprocess.run(list(command), cwd=str(ROOT), env=env, check=False)
    return result.returncode


def run_shell(
    command: Sequence[str], *, extra_env: Mapping[str, str] | None = None
) -> int:
    """Run a generic shell command and return the process exit code."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(list(command), cwd=str(ROOT), env=env, check=False)
    return result.returncode


def run_python(command: Command, env: Mapping[str, str]) -> int:
    """Execute a promoted Python command under canonical dispatch env."""
    return subprocess.run(
        [sys.executable, str(command.path)], cwd=str(ROOT), env=dict(env), check=False
    ).returncode


def command_env(command: Command) -> dict[str, str]:
    """Return canonical environment for a promoted command."""
    env = os.environ.copy()
    env["WHAT"] = command.what
    env["FLEXT_COMMAND_DISPATCHED"] = "Y"
    env["FLEXT_COMMAND_VERB"] = command.verb
    env["FLEXT_COMMAND_WHAT"] = command.what
    env["FLEXT_COMMAND_PATH"] = str(command.path.resolve())
    env["PYTHONPATH"] = str(ROOT)
    return env


def require_dispatched(path: Path) -> None:
    """Fail if a promoted Python command is run outside `scripts/dispatch.py`."""
    expected = str(path.resolve())
    if (
        os.environ.get("FLEXT_COMMAND_DISPATCHED") == "Y"
        and os.environ.get("FLEXT_COMMAND_PATH") == expected
    ):
        return
    print(
        "ERRO: comandos publicos devem ser executados via make <verbo> WHAT=<acao>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def promoted_main(script_file: str | Path, handler: Callable[[], int]) -> NoReturn:
    """Run a promoted Python command through the dispatch guard."""
    require_dispatched(Path(script_file))
    raise SystemExit(handler())


def env_enabled(name: str) -> bool:
    return os.environ.get(name, "N").upper() in {"1", "Y", "YES", "TRUE"}
