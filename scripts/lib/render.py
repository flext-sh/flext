"""Rendering boundary for promoted Make command help."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import m, u
from scripts.lib.registry import CommandRegistry

if TYPE_CHECKING:
    from collections.abc import Iterable


class CommandRenderer:
    """Render dispatcher help through the canonical flext-tests helpers."""

    @staticmethod
    def global_help(registry: m.Tests.MakeRegistry) -> str:
        """Render top-level dispatcher help."""
        rendered: str = u.Tests.make_render_global_help(registry)
        return rendered

    @staticmethod
    def verb_help(registry: m.Tests.MakeRegistry, requested_verb: str) -> str:
        """Render help for one promoted verb."""
        result = u.Tests.make_render_verb_help(registry, requested_verb)
        if result.failure:
            raise CommandRegistry.Error(result.error or "verb help render failed")
        return result.value

    @staticmethod
    def command_help(
        registry: m.Tests.MakeRegistry, requested_verb: str, what: str
    ) -> str:
        """Render help for one promoted command."""
        result = u.Tests.make_render_command_help(registry, requested_verb, what)
        if result.failure:
            raise CommandRegistry.Error(result.error or "command help render failed")
        return result.value

    @staticmethod
    def dry_run(command: m.Tests.MakeCommand, requested_verb: str, what: str) -> str:
        """Render dry-run output for one mutating command."""
        rendered: str = u.Tests.make_render_dry_run(
            command, requested_verb, what, u.Cli.process_env()
        )
        return rendered

    @staticmethod
    def format_params_inline(params: Iterable[m.Tests.MakeParam]) -> str:
        """Render command params in one compact inline form."""
        rendered: str = u.Tests.make_format_params_inline(params)
        return rendered

    @staticmethod
    def example_for(command: m.Tests.MakeCommand, requested_verb: str) -> str:
        """Return the example adjusted for an alias-preserving verb."""
        rendered: str = u.Tests.make_example_for(command, requested_verb)
        return rendered


__all__: list[str] = ["CommandRenderer"]
