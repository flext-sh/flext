"""Execution boundary for promoted Make commands."""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from flext_cli import u
from flext_tests import c, m, t
from scripts.lib.registry import CommandRegistry

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


class CommandExecution:
    """Run promoted commands through flext-cli process utilities."""

    @staticmethod
    def run(command: m.Tests.MakeCommand) -> int:
        """Run one promoted command through the canonical execution path."""
        if command.target:
            return CommandExecution.run_make(
                command.target, extra_env=dict(command.target_env)
            )
        env = CommandExecution.command_env(command)
        if command.path.suffix == ".py":
            if CommandExecution.surface_validation_enabled():
                return CommandExecution.run_python_probe(command, env)
            return CommandExecution.run_python(command, env)
        return CommandExecution.run_process(("bash", str(command.path)), extra_env=env)

    @staticmethod
    def run_make(
        target: str,
        *,
        make_args: Sequence[str] = (),
        extra_env: t.MappingKV[str, str] | None = None,
    ) -> int:
        """Run a Makefile target and return the process exit code."""
        if CommandExecution.surface_validation_enabled():
            if not CommandExecution.make_target_exists(target):
                return 2
            rendered = " ".join((
                "make",
                target,
                *make_args,
                *CommandExecution.make_variable_args(extra_env),
            ))
            u.Cli.emit_raw(f"SURFACE-VALIDATE: {rendered}\n")
            return 0
        return CommandExecution.run_process((
            "make",
            target,
            *make_args,
            *CommandExecution.make_variable_args(extra_env),
        ))

    @staticmethod
    def run_shell(
        command: Sequence[str], *, extra_env: t.MappingKV[str, str] | None = None
    ) -> int:
        """Run a command and return its process exit code."""
        if CommandExecution.surface_validation_enabled():
            return 0
        return CommandExecution.run_process(command, extra_env=extra_env)

    @staticmethod
    def run_python(command: m.Tests.MakeCommand, env: t.MappingKV[str, str]) -> int:
        """Execute a promoted Python command under canonical dispatch env."""
        return CommandExecution.run_process(
            (
                sys.executable,
                "-c",
                "import runpy, sys; runpy.run_path(sys.argv[1], run_name='__main__')",
                str(command.path),
            ),
            extra_env=env,
        )

    @staticmethod
    def run_python_probe(
        command: m.Tests.MakeCommand, env: t.MappingKV[str, str]
    ) -> int:
        """Run one Python command safely in-process for surface validation."""
        previous = os.environ.copy()
        try:
            os.environ.update(env)
            try:
                runpy.run_path(str(command.path), run_name="__main__")
            except SystemExit as exc:
                return exc.code if isinstance(exc.code, int) else 1
        finally:
            os.environ.clear()
            os.environ.update(previous)
        return 0

    @staticmethod
    def run_process(
        command: Sequence[str], *, extra_env: t.MappingKV[str, str] | None = None
    ) -> int:
        """Run one process through flext-cli and mirror captured output."""
        result = u.Cli.run_raw(command, cwd=CommandRegistry.ROOT, env=extra_env)
        if result.failure:
            if result.error:
                sys.stderr.write(f"{result.error}\n")
            return 1
        output = result.value
        if output.stdout:
            sys.stdout.write(output.stdout)
        if output.stderr:
            sys.stderr.write(output.stderr)
        exit_code: int = output.exit_code
        return exit_code

    @staticmethod
    def make_variable_args(values: t.MappingKV[str, str] | None) -> t.StrSequence:
        """Return Make command-line variable assignments for override precedence."""
        if not values:
            return ()
        return tuple(f"{name}={value}" for name, value in values.items())

    @staticmethod
    def command_env(command: m.Tests.MakeCommand) -> t.StrMapping:
        """Return canonical environment for a promoted command."""
        return u.Cli.process_env(
            overrides={
                c.Tests.MAKE_WHAT_PARAM: command.what,
                c.Tests.MAKE_DISPATCH_ENV: c.Tests.MAKE_DISPATCH_ENV_VALUE,
                c.Tests.MAKE_DISPATCH_VERB_ENV: command.verb,
                c.Tests.MAKE_DISPATCH_WHAT_ENV: command.what,
                c.Tests.MAKE_DISPATCH_PATH_ENV: str(command.path.resolve()),
                c.Tests.MAKE_PYTHONPATH_ENV: str(CommandRegistry.ROOT),
            }
        )

    @staticmethod
    def require_dispatched(path: Path) -> None:
        """Fail if a promoted Python command is run outside the dispatcher."""
        expected = str(path.resolve())
        if (
            os.environ.get(c.Tests.MAKE_DISPATCH_ENV) == c.Tests.MAKE_DISPATCH_ENV_VALUE
            and os.environ.get(c.Tests.MAKE_DISPATCH_PATH_ENV) == expected
        ):
            return
        raise SystemExit(2)

    @staticmethod
    def promoted_main(script_file: str | Path, handler: Callable[[], int]) -> NoReturn:
        """Run a promoted Python command through the dispatch guard."""
        CommandExecution.require_dispatched(Path(script_file))
        raise SystemExit(handler())

    @staticmethod
    def env_enabled(name: str) -> bool:
        """Return whether an environment flag is truthy."""
        return u.Cli.process_env().get(name, "N").upper() in c.Tests.MAKE_TRUE_VALUES

    @staticmethod
    def env_value(name: str, default: str = "") -> str:
        """Return one environment value through the canonical CLI env resolver."""
        value: str = u.Cli.process_env().get(name, default)
        return value.strip()

    @staticmethod
    def surface_validation_enabled() -> bool:
        """Return whether Make execution should only validate command routing."""
        return (
            os.environ.get(c.Tests.MAKE_SURFACE_VALIDATE_ENV, "N").upper()
            in c.Tests.MAKE_TRUE_VALUES
        )

    @staticmethod
    def make_targets() -> frozenset[str]:
        """Return target names declared in the root Makefile."""
        targets: set[str] = set()
        makefile = CommandRegistry.ROOT / "Makefile"
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

    @staticmethod
    def make_target_exists(target: str) -> bool:
        """Return whether one Make target exists in the root Makefile."""
        return target in CommandExecution.make_targets()


__all__: list[str] = ["CommandExecution"]
