"""Validation boundary for the promoted Make command surface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import m, t, u
from scripts.lib.exec import CommandExecution
from scripts.lib.registry import CommandRegistry
from scripts.lib.surface_probes import SurfaceProbeRunner

if TYPE_CHECKING:
    from collections.abc import Callable


class SurfaceValidator:
    """Validate Makefile dispatcher wrappers and command metadata."""

    @staticmethod
    def validate(dispatch_main: Callable[[tuple[str, ...]], int]) -> int:
        """Validate every promoted verb/WHAT route and return a shell exit code."""
        registry = CommandRegistry.discover()
        failures = [
            *SurfaceValidator.validate_static(registry),
            *SurfaceProbeRunner.run(SurfaceProbeRunner.build(registry), dispatch_main),
        ]
        if failures:
            for failure in failures:
                print(f"ERRO: {failure}")
            return 1
        command_count = sum(
            len(SurfaceValidator.registry_commands(registry, verb))
            for verb in u.Tests.make_registry_verbs(registry)
        )
        verb_count = len(u.Tests.make_registry_verbs(registry))
        print(
            f"Surface validated: {verb_count} verbs, {command_count} commands"
        )
        return 0

    @staticmethod
    def validate_static(registry: m.Tests.MakeRegistry) -> t.StrSequence:
        """Validate registry metadata against the root Makefile surface."""
        failures: list[str] = []
        targets = CommandExecution.make_targets()
        wrappers = SurfaceValidator.make_dispatch_wrappers()
        for verb in u.Tests.make_registry_verbs(registry):
            commands = SurfaceValidator.registry_commands(registry, verb)
            if verb not in targets:
                failures.append(f"make target ausente para verbo publico: {verb}")
            if verb not in wrappers:
                failures.append(f"make {verb}: wrapper dispatcher ausente")
            for command in commands.values():
                failures.extend(SurfaceValidator.validate_command(command, targets))
        return tuple(failures)

    @staticmethod
    def validate_command(
        command: m.Tests.MakeCommand, targets: frozenset[str]
    ) -> t.StrSequence:
        """Validate one command's static contract."""
        failures: list[str] = []
        if command.target and command.target not in targets:
            failures.append(
                f"{command.verb} WHAT={command.what}: target ausente {command.target}"
            )
        if not command.example.startswith(f"make {command.verb} "):
            failures.append(
                f"{command.verb} WHAT={command.what}: exemplo nao usa make canonico"
            )
        return tuple(failures)

    @staticmethod
    def make_dispatch_wrappers() -> frozenset[str]:
        """Return public Make targets delegated to the registry dispatcher."""
        lines = (
            (CommandRegistry.ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
        )
        wrappers: set[str] = set()
        current_target = ""
        for line in lines:
            if line and not line.startswith(("\t", " ", "#")):
                head, marker, _tail = line.partition(":")
                is_public_target = (
                    marker == ":" and head and not head.startswith(("_", "."))
                )
                current_target = head if is_public_target else ""
                continue
            if not current_target or not line.startswith("\t"):
                continue
            stripped = line.strip()
            if stripped == f"$(Q)$(FLEXT_MAKE_DISPATCH) {current_target}":
                wrappers.add(current_target)
        return frozenset(wrappers)

    @staticmethod
    def registry_commands(
        registry: m.Tests.MakeRegistry, verb: str
    ) -> t.MappingKV[str, m.Tests.MakeCommand]:
        """Return registry commands through the canonical flext-tests facade."""
        result = u.Tests.make_registry_commands(registry, verb)
        if result.failure:
            raise CommandRegistry.Error(result.error or "registry lookup failed")
        return result.value


__all__: list[str] = ["SurfaceValidator"]
