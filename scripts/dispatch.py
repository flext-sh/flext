"""Command dispatch framework for FLEXT Makefile verbs."""

from __future__ import annotations

from typing import ClassVar

from scripts.lib.cli import CommandCli
from scripts.lib.exec import CommandExecution
from scripts.lib.registry import CommandRegistry
from scripts.lib.render import CommandRenderer


class Dispatch:
    """Public namespace for promoted Make command scripts."""

    DEFAULT_COMMAND: ClassVar[str] = CommandRegistry.DEFAULT_COMMAND
    Command = CommandRegistry.Command
    Param = CommandRegistry.Param
    Registry = CommandRegistry.Registry
    RegistryError = CommandRegistry.Error

    main = staticmethod(CommandCli.main)
    discover = staticmethod(CommandRegistry.discover)
    command_env = staticmethod(CommandExecution.command_env)
    env_enabled = staticmethod(CommandExecution.env_enabled)
    env_value = staticmethod(CommandExecution.env_value)
    promoted_main = staticmethod(CommandExecution.promoted_main)
    render_global_help = staticmethod(CommandRenderer.global_help)
    require_dispatched = staticmethod(CommandExecution.require_dispatched)
    run_make = staticmethod(CommandExecution.run_make)
    run_shell = staticmethod(CommandExecution.run_shell)
    surface_validation_enabled = staticmethod(
        CommandExecution.surface_validation_enabled
    )


__all__: list[str] = ["Dispatch"]


if __name__ == "__main__":
    raise SystemExit(Dispatch.main())
