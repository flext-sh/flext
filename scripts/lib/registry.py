"""Command registry boundary for promoted Make verbs."""

from __future__ import annotations

from pathlib import Path

from flext_tests import c, m, p, t, u


class CommandRegistry:
    """Thin CLI boundary over the canonical flext-tests Make registry."""

    class Error(ValueError):
        """Raised when command metadata or invocation cannot be resolved."""

    Command = m.Tests.MakeCommand
    Param = m.Tests.MakeParam
    Registry = m.Tests.MakeRegistry

    DEFAULT_COMMAND = c.Tests.MAKE_DEFAULT_COMMAND
    ROOT = Path(__file__).resolve().parent.parent.parent
    SCRIPTS_DIR = ROOT / "scripts" / "cmd"

    @staticmethod
    def discover() -> p.Tests.MakeRegistry:
        """Discover and validate the promoted command registry."""
        result = u.Tests.make_discover(CommandRegistry.SCRIPTS_DIR)
        if result.failure:
            raise CommandRegistry.Error(result.error or "registry discovery failed")
        value = result.value
        if not value:
            msg = "registry discovery returned invalid model"
            raise CommandRegistry.Error(msg)
        return value

    @staticmethod
    def load_command(path: Path, expected_verb: str) -> p.Tests.MakeCommand:
        """Load one promoted command from its flext-command header."""
        result = u.Tests.make_load_command(path, expected_verb)
        if result.failure:
            raise CommandRegistry.Error(result.error or "command load failed")
        value = result.value
        if not value:
            msg = "command load returned invalid model"
            raise CommandRegistry.Error(msg)
        return value

    @staticmethod
    def header_data(path: Path) -> t.Tests.MakeTomlTable:
        """Return parsed TOML metadata from one command header."""
        result = u.Tests.make_header_data(path)
        if result.failure:
            raise CommandRegistry.Error(result.error or "header load failed")
        try:
            table: t.Tests.MakeTomlTable = (
                t.Tests.MAKE_TOML_TABLE_ADAPTER.validate_python(result.value)
            )
        except (TypeError, ValueError) as exc:
            msg = "header load returned invalid TOML table"
            raise CommandRegistry.Error(msg) from exc
        return table

    @staticmethod
    def validate_invocation(
        command: p.Tests.MakeCommand, *, require_required: bool = True
    ) -> None:
        """Validate environment-backed parameter values for one invocation."""
        result = u.Tests.make_validate_invocation(
            command, u.Cli.process_env(), require_required=require_required
        )
        if result.failure:
            raise CommandRegistry.Error(result.error or "invocation validation failed")

    @staticmethod
    def param_value(param: p.Tests.MakeParam, command: p.Tests.MakeCommand) -> str:
        """Return the current value for one promoted-command parameter."""
        value: str = u.Tests.make_param_value(param, command, u.Cli.process_env())
        return value


__all__: list[str] = ["CommandRegistry"]
