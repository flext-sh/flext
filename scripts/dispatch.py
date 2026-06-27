"""Command dispatch framework for FLEXT Makefile verbs."""

from __future__ import annotations

from scripts.lib.cli import main
from scripts.lib.exec import (
    command_env,
    env_enabled,
    env_value,
    promoted_main,
    require_dispatched,
    run_make,
    run_shell,
)
from scripts.lib.registry import (
    DEFAULT_COMMAND,
    Command,
    Param,
    Registry,
    RegistryError,
    discover,
)
from scripts.lib.render import render_global_help

__all__ = [
    "DEFAULT_COMMAND",
    "Command",
    "Param",
    "Registry",
    "RegistryError",
    "command_env",
    "discover",
    "env_enabled",
    "env_value",
    "main",
    "promoted_main",
    "render_global_help",
    "require_dispatched",
    "run_make",
    "run_shell",
]


if __name__ == "__main__":
    raise SystemExit(main())
