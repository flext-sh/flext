"""Validation boundary for the promoted Make command surface."""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from typing import ClassVar

from flext_tests import c, m, t, u
from scripts.lib.exec import CommandExecution
from scripts.lib.registry import CommandRegistry
from scripts.lib.surface_probes import SurfaceProbeRunner


class SurfaceValidator:
    """Validate Makefile cases and command metadata."""

    MAKE_CASE_RE: ClassVar[re.Pattern[str]] = re.compile(r"^\s*([^)]*?)\)\s")

    @staticmethod
    def validate(dispatch_main: Callable[[tuple[str, ...]], int]) -> int:
        """Validate every promoted verb/WHAT route and return a shell exit code."""
        registry = CommandRegistry.discover()
        failures = [
            *SurfaceValidator.validate_static(registry),
            *SurfaceProbeRunner.run(SurfaceProbeRunner.build(registry), dispatch_main),
        ]
        if failures:
            print("surface validation failed:", file=sys.stderr)
            for failure in failures:
                print(f"  - {failure}", file=sys.stderr)
            return 1
        command_count = sum(
            len(SurfaceValidator.registry_commands(registry, verb))
            for verb in u.Tests.make_registry_verbs(registry)
        )
        verb_count = len(u.Tests.make_registry_verbs(registry))
        print(f"surface validation ok: {verb_count} verbs, {command_count} WHATs")
        return 0

    @staticmethod
    def validate_static(registry: m.Tests.MakeRegistry) -> t.StrSequence:
        """Validate registry metadata against the root Makefile surface."""
        failures: list[str] = []
        targets = CommandExecution.make_targets()
        cases = SurfaceValidator.make_dispatch_cases()
        for verb in u.Tests.make_registry_verbs(registry):
            commands = SurfaceValidator.registry_commands(registry, verb)
            if verb not in targets:
                failures.append(f"make target ausente para verbo publico: {verb}")
            failures.extend(SurfaceValidator.validate_verb_cases(verb, commands, cases))
            for command in commands.values():
                failures.extend(SurfaceValidator.validate_command(command, targets))
        return tuple(failures)

    @staticmethod
    def validate_verb_cases(
        verb: str,
        commands: t.MappingKV[str, m.Tests.MakeCommand],
        cases: t.MappingKV[str, frozenset[str]],
    ) -> t.StrSequence:
        """Validate one Makefile case block against registry WHAT values."""
        if verb not in cases:
            if len(commands) > 1 or verb not in c.Tests.MAKE_PUBLIC_VERBS_WITHOUT_CASE:
                return (f"make {verb}: sem dispatcher WHAT explicito",)
            return ()
        case_values = cases[verb]
        expected = frozenset(commands)
        missing = sorted(expected - case_values)
        extra = sorted(case_values - expected - {""})
        failures: list[str] = []
        if missing:
            failures.append(f"make {verb}: WHAT ausente: {', '.join(missing)}")
        if extra:
            failures.append(f"make {verb}: WHAT sem registry: {', '.join(extra)}")
        return tuple(failures)

    @staticmethod
    def validate_command(
        command: m.Tests.MakeCommand,
        targets: frozenset[str],
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
    def make_dispatch_cases() -> t.MappingKV[str, frozenset[str]]:
        """Return public Make WHAT cases keyed by verb."""
        lines = (
            (CommandRegistry.ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
        )
        cases: t.MutableMappingKV[str, frozenset[str]] = {}
        for index, line in enumerate(lines):
            if not line or line.startswith(("\t", " ", "_", ".", "#")):
                continue
            head, marker, _tail = line.partition(":")
            if marker != ":" or not head:
                continue
            parsed = SurfaceValidator.parse_case_values(lines[index + 1 :])
            if parsed:
                cases[head] = parsed
        return cases

    @staticmethod
    def parse_case_values(lines: t.StrSequence) -> frozenset[str]:
        """Parse WHAT labels from one Make case statement body."""
        values: set[str] = set()
        in_case = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("$(Q)case "):
                in_case = True
                continue
            if not in_case:
                if stripped or line.startswith("\t"):
                    continue
                return frozenset(values)
            if stripped == "esac":
                return frozenset(values)
            match = SurfaceValidator.MAKE_CASE_RE.match(stripped)
            if match is None:
                continue
            labels = match.group(1).replace('"', "")
            for label in labels.split("|"):
                value = label.strip()
                if value != "*":
                    values.add(value)
        return frozenset(values)

    @staticmethod
    def registry_commands(
        registry: m.Tests.MakeRegistry,
        verb: str,
    ) -> t.MappingKV[str, m.Tests.MakeCommand]:
        """Return registry commands through the canonical flext-tests facade."""
        result = u.Tests.make_registry_commands(registry, verb)
        if result.failure:
            raise CommandRegistry.Error(result.error or "registry lookup failed")
        return result.value


__all__: list[str] = ["SurfaceValidator"]
