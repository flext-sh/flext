"""Process execution and dispatch-guard layer for promoted commands."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import NoReturn

from flext_cli import u
from scripts.lib.registry import ROOT, Command


def run(command: Command) -> int:
    """Run one promoted command through the canonical execution path."""
    if command.target:
        return run_make(command.target, extra_env=dict(command.target_env))
    env = command_env(command)
    if command.path.suffix == ".py":
        return run_python(command, env)
    return run_streaming(("bash", str(command.path)), env=env)


def run_make(
    target: str,
    *,
    make_args: Sequence[str] = (),
    extra_env: Mapping[str, str] | None = None,
) -> int:
    """Run a Makefile target and return the process exit code."""
    if surface_validation_enabled():
        if not make_target_exists(target):
            print(f"ERRO: Make target ausente: {target}", file=sys.stderr)
            return 2
        rendered = " ".join(("make", target, *make_args))
        print(f"SURFACE-VALIDATE: {rendered}")
        return 0
    command = ("make", target, *make_args)
    return run_streaming(command, env=extra_env)


def run_shell(
    command: Sequence[str], *, extra_env: Mapping[str, str] | None = None
) -> int:
    """Run a generic shell command and return the process exit code."""
    if surface_validation_enabled():
        print(f"SURFACE-VALIDATE: {' '.join(command)}")
        return 0
    result = u.Cli.run_raw(command, cwd=ROOT, env=extra_env)
    if result.failure:
        print(result.error or "command execution failed", file=sys.stderr)
        return 1
    output = result.value
    if output.stdout:
        print(output.stdout, end="")
    if output.stderr:
        print(output.stderr, file=sys.stderr, end="")
    return output.exit_code


def run_python(command: Command, env: Mapping[str, str]) -> int:
    """Execute a promoted Python command under canonical dispatch env."""
    return run_streaming(
        (
            sys.executable,
            "-c",
            "import runpy, sys; runpy.run_path(sys.argv[1], run_name='__main__')",
            str(command.path),
        ),
        env=env,
    )


def run_streaming(command: Sequence[str], env: Mapping[str, str] | None = None) -> int:
    """Run a command that must stream output directly to the terminal."""
    return subprocess.run(
        list(command),
        cwd=str(ROOT),
        env=u.Cli.process_env(overrides=env),
        check=False,
    ).returncode


def command_env(command: Command) -> dict[str, str]:
    """Return canonical environment for a promoted command."""
    return u.Cli.process_env(
        overrides={
            "WHAT": command.what,
            "FLEXT_COMMAND_DISPATCHED": "Y",
            "FLEXT_COMMAND_VERB": command.verb,
            "FLEXT_COMMAND_WHAT": command.what,
            "FLEXT_COMMAND_PATH": str(command.path.resolve()),
            "PYTHONPATH": str(ROOT),
        }
    )


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
    """Return whether an environment flag is truthy."""
    return u.Cli.process_env().get(name, "N").upper() in {"1", "Y", "YES", "TRUE"}


def env_value(name: str, default: str = "") -> str:
    """Return one environment value through the canonical CLI env resolver."""
    return u.Cli.process_env().get(name, default).strip()


def surface_validation_enabled() -> bool:
    """Return whether Make execution should only validate command routing."""
    return os.environ.get("FLEXT_SURFACE_VALIDATE", "N").upper() in {
        "1",
        "Y",
        "YES",
        "TRUE",
    }


def make_targets() -> frozenset[str]:
    """Return target names declared in the root Makefile."""
    targets: set[str] = set()
    makefile = ROOT / "Makefile"
    for raw_line in makefile.read_text(encoding="utf-8").splitlines():
        if not raw_line or raw_line.startswith(("\t", " ", "#", ".")):
            continue
        head, marker, _tail = raw_line.partition(":")
        if marker != ":" or not head:
            continue
        for target in head.split():
            if target and all(char not in target for char in "$(){}"):
                targets.add(target)
    return frozenset(targets)


def make_target_exists(target: str) -> bool:
    """Return whether one Make target exists in the root Makefile."""
    return target in make_targets()
