"""CLI orchestration for promoted Make verbs."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

from flext_tests import c, t, u
from scripts.lib.exec import CommandExecution
from scripts.lib.registry import CommandRegistry
from scripts.lib.surface_validation import SurfaceValidator

if TYPE_CHECKING:
    from collections.abc import Sequence


class CommandCli:
    """Parse dispatcher arguments, render help, and execute commands."""

    @staticmethod
    def main(argv: Sequence[str] | None = None) -> int:
        """Run the FLEXT scripts dispatcher."""
        args = tuple(
            CommandCli.apply_env_from_args(sys.argv[1:] if argv is None else argv)
        )
        try:
            return CommandCli.route(args)
        except CommandRegistry.Error as exc:
            print(str(exc), file=sys.stderr)
            return 2

    @staticmethod
    def route(args: t.StrSequence) -> int:
        """Route normalized dispatcher arguments."""
        if args and args[0] in {"help", "--help", "-h"}:
            return CommandCli.print_help("")
        if not args:
            requested = u.Cli.process_env().get(c.Tests.MAKE_WHAT_PARAM, "").strip()
            return CommandCli.print_help(requested)
        if args[0] == "--validate":
            CommandRegistry.discover()
            return 0
        if args[0] == "--validate-surface":
            return SurfaceValidator.validate(CommandCli.main)
        return CommandCli.dispatch(args[0])

    @staticmethod
    def apply_env_from_args(raw_args: Sequence[str]) -> t.StrSequence:
        """Promote KEY=value argv items into the process environment."""
        command_args: list[str] = []
        for arg in raw_args:
            if "=" not in arg:
                command_args.append(arg)
                continue
            key, value = arg.split("=", 1)
            if key.isidentifier():
                os.environ[key] = value
                continue
            command_args.append(arg)
        return tuple(command_args)

    @staticmethod
    def print_help(requested: str) -> int:
        """Print global, verb, or command help."""
        registry = CommandRegistry.discover()
        if requested and "/" in requested:
            verb, what = requested.split("/", 1)
            return CommandCli.print_command_or_verb_help(registry, verb, what)
        if requested:
            return CommandCli.print_verb_help(registry, requested)
        return 0

    @staticmethod
    def print_command_or_verb_help(
        registry: CommandRegistry.Registry, verb: str, what: str
    ) -> int:
        """Print help for one command."""
        return 0

    @staticmethod
    def print_verb_help(registry: CommandRegistry.Registry, requested_verb: str) -> int:
        """Print help for one verb."""
        return 0

    @staticmethod
    def dispatch(requested_verb: str) -> int:
        """Dispatch one promoted verb from the current process environment."""
        registry = CommandRegistry.discover()
        verb_result = u.Tests.make_registry_resolve_verb(registry, requested_verb)
        if verb_result.failure:
            raise CommandRegistry.Error(verb_result.error or "verb unknown")
        verb = verb_result.value
        env = u.Cli.process_env()
        requested = (
            env.get(c.Tests.MAKE_WHAT_PARAM, "").strip() or c.Tests.MAKE_DEFAULT_COMMAND
        )
        what_values = CommandCli.normalize_what(requested)

        if requested == "help":
            return 0
        if CommandExecution.env_enabled(
            c.Tests.MAKE_HELP_PARAM
        ) or CommandExecution.env_enabled(c.Tests.MAKE_OPTIONS_PARAM):
            if len(what_values) == 1:
                return CommandCli.print_command_or_verb_help(
                    registry, requested_verb, what_values[0]
                )
            CommandCli.print_verbosity_help(registry, requested_verb, what_values)
            return 0

        code = 0
        for what in what_values:
            command_result = u.Tests.make_registry_command(registry, verb, what)
            if command_result.failure:
                raise CommandRegistry.Error(command_result.error or "command unknown")
            command = command_result.value
            is_dry_run = (
                command.mutates
                and env.get(c.Tests.MAKE_APPLY_PARAM, "N").upper()
                != c.Tests.MAKE_DISPATCH_ENV_VALUE
            )
            CommandRegistry.validate_invocation(
                command, require_required=not is_dry_run
            )
            if is_dry_run:
                continue
            child_code = CommandExecution.run(command)
            if child_code != 0:
                return child_code
            code = child_code
        return code

    @staticmethod
    def normalize_what(raw: str) -> tuple[str, ...]:
        """Normalize comma-separated WHAT values."""
        items: list[str] = []
        for raw_item in raw.split(","):
            item = raw_item.strip()
            if not item:
                continue
            if "/" in item:
                item = item.rsplit("/", 1)[-1].strip()
            if item:
                items.append(item)
        if not items:
            return (c.Tests.MAKE_DEFAULT_COMMAND,)
        return tuple(dict.fromkeys(items))

    @staticmethod
    def print_verbosity_help(
        registry: CommandRegistry.Registry,
        requested_verb: str,
        what_values: tuple[str, ...],
    ) -> None:
        """Print detailed help for one WHAT value or the parent verb."""
        if len(what_values) != 1:
            return


__all__: list[str] = ["CommandCli"]
