"""Probe runner for the promoted Make command surface."""

from __future__ import annotations

import os
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from typing import TYPE_CHECKING

from flext_tests import c, m, t, u
from scripts.lib.registry import CommandRegistry

if TYPE_CHECKING:
    from collections.abc import Callable


class SurfaceProbeRunner:
    """Build and execute in-process dispatcher probes."""

    @staticmethod
    def build(registry: m.Tests.MakeRegistry) -> t.SequenceOf[m.Tests.MakeSurfaceProbe]:
        """Build command-line probes for every promoted verb and WHAT."""
        probes: list[m.Tests.MakeSurfaceProbe] = [
            m.Tests.MakeSurfaceProbe(
                name="global help", argv=("help",), expected_output=("flext - make",)
            )
        ]
        for verb in u.Tests.make_registry_verbs(registry):
            probes.append(
                m.Tests.MakeSurfaceProbe(
                    name=f"{verb} verb help",
                    argv=(verb,),
                    env={c.Tests.MAKE_WHAT_PARAM: "help"},
                    expected_output=(f"make {verb} WHAT=<WHAT>",),
                )
            )
            commands_result = u.Tests.make_registry_commands(registry, verb)
            if commands_result.failure:
                raise CommandRegistry.Error(
                    commands_result.error or "registry lookup failed"
                )
            for command in sorted(
                commands_result.value.values(), key=lambda item: item.what
            ):
                probes.extend(SurfaceProbeRunner.command_probes(command))
        probes.extend((
            m.Tests.MakeSurfaceProbe(
                name="unknown verb",
                argv=("unknown-surface-verb",),
                expected_output=("ERRO:",),
            ),
            m.Tests.MakeSurfaceProbe(
                name="unknown WHAT",
                argv=("check",),
                env={c.Tests.MAKE_WHAT_PARAM: "unknown"},
                expected_output=("ERRO:",),
            ),
            m.Tests.MakeSurfaceProbe(
                name="invalid choice",
                argv=("build",),
                env={c.Tests.MAKE_WHAT_PARAM: "docs", "DOCS_PHASE": "bad"},
                expected_output=("ERRO:",),
            ),
        ))
        return tuple(probes)

    @staticmethod
    def command_probes(
        command: m.Tests.MakeCommand,
    ) -> t.SequenceOf[m.Tests.MakeSurfaceProbe]:
        """Build help, dry-run, and execution-route probes for one command."""
        env = SurfaceProbeRunner.command_env(command)
        probes: list[m.Tests.MakeSurfaceProbe] = [
            m.Tests.MakeSurfaceProbe(
                name=f"{command.verb}/{command.what} help",
                argv=(command.verb,),
                env={**env, c.Tests.MAKE_HELP_PARAM: "1"},
                expected_output=(f"make {command.verb} WHAT={command.what}",),
            )
        ]
        if command.mutates or command.mutates_when:
            mutation_env = SurfaceProbeRunner.mutation_env(command, env)
            probes.extend((
                m.Tests.MakeSurfaceProbe(
                    name=f"{command.verb}/{command.what} dry-run",
                    argv=(command.verb,),
                    env={
                        **mutation_env,
                        c.Tests.MAKE_SURFACE_VALIDATE_ENV: (
                            c.Tests.MAKE_DISPATCH_ENV_VALUE
                        ),
                    },
                    expected_output=("DRY-RUN: nenhuma mutacao executada.",),
                ),
                m.Tests.MakeSurfaceProbe(
                    name=f"{command.verb}/{command.what} apply route",
                    argv=(command.verb,),
                    env={
                        **mutation_env,
                        c.Tests.MAKE_APPLY_PARAM: c.Tests.MAKE_DISPATCH_ENV_VALUE,
                        c.Tests.MAKE_SURFACE_VALIDATE_ENV: (
                            c.Tests.MAKE_DISPATCH_ENV_VALUE
                        ),
                    },
                    expected_output=("SURFACE-VALIDATE:",),
                ),
            ))
            return tuple(probes)
        probes.append(
            m.Tests.MakeSurfaceProbe(
                name=f"{command.verb}/{command.what} route",
                argv=(command.verb,),
                env={
                    **env,
                    c.Tests.MAKE_SURFACE_VALIDATE_ENV: (
                        c.Tests.MAKE_DISPATCH_ENV_VALUE
                    ),
                },
            )
        )
        return tuple(probes)

    @staticmethod
    def command_env(command: m.Tests.MakeCommand) -> t.StrMapping:
        """Return safe parameter values for one command probe."""
        env: t.MutableStrMapping = {c.Tests.MAKE_WHAT_PARAM: command.what}
        for param in command.params:
            if param.name == c.Tests.MAKE_WHAT_PARAM:
                continue
            env[param.name] = c.Tests.MAKE_SAFE_PROBE_VALUES.get(
                param.name, param.default
            )
        return env

    @staticmethod
    def mutation_env(
        command: m.Tests.MakeCommand, env: t.MappingKV[str, str]
    ) -> t.StrMapping:
        """Return probe environment values that activate mutation conditions."""
        resolved: t.MutableStrMapping = dict(env)
        for condition in command.mutates_when:
            resolved[condition.name] = condition.values[0]
        return resolved

    @staticmethod
    def run(
        probes: t.SequenceOf[m.Tests.MakeSurfaceProbe],
        dispatch_main: Callable[[tuple[str, ...]], int],
    ) -> t.StrSequence:
        """Run all surface probes and return failure messages."""
        failures: list[str] = []
        for probe in probes:
            result = SurfaceProbeRunner.run_one(probe, dispatch_main)
            output = f"{result.stdout}\n{result.stderr}"
            expect_failure = probe.name.startswith(("unknown", "invalid"))
            if expect_failure:
                if result.returncode == 0:
                    failures.append(f"{probe.name}: expected failure, got exit 0")
                elif not all(fragment in output for fragment in probe.expected_output):
                    failures.append(f"{probe.name}: missing expected error output")
                continue
            if result.returncode != 0:
                failures.append(
                    f"{probe.name}: exit {result.returncode}: {output.strip()}"
                )
                continue
            missing = [
                fragment for fragment in probe.expected_output if fragment not in output
            ]
            if missing:
                failures.append(f"{probe.name}: missing output: {', '.join(missing)}")
        return tuple(failures)

    @staticmethod
    def run_one(
        probe: m.Tests.MakeSurfaceProbe, dispatch_main: Callable[[tuple[str, ...]], int]
    ) -> m.Tests.MakeSurfaceProbeResult:
        """Run one dispatcher probe in-process with an isolated environment."""
        return SurfaceProbeRunner.with_environment(
            probe.env,
            lambda: SurfaceProbeRunner.capture(dispatch_main, tuple(probe.argv)),
        )

    @staticmethod
    def with_environment(
        env: t.MappingKV[str, str], action: Callable[[], m.Tests.MakeSurfaceProbeResult]
    ) -> m.Tests.MakeSurfaceProbeResult:
        """Run an action with probe environment values, then restore environment."""
        original = os.environ.copy()
        try:
            os.environ.clear()
            os.environ.update(original)
            os.environ.update(env)
            os.environ[c.Tests.MAKE_PYTHONPATH_ENV] = str(CommandRegistry.ROOT)
            return action()
        finally:
            os.environ.clear()
            os.environ.update(original)

    @staticmethod
    def capture(
        dispatch_main: Callable[[tuple[str, ...]], int], argv: tuple[str, ...]
    ) -> m.Tests.MakeSurfaceProbeResult:
        """Capture stdout/stderr from one dispatcher invocation."""
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = dispatch_main(argv)
            except SystemExit as exc:
                code = exc.code if isinstance(exc.code, int) else 1
        return m.Tests.MakeSurfaceProbeResult(
            returncode=code, stdout=stdout.getvalue(), stderr=stderr.getvalue()
        )


__all__: list[str] = ["SurfaceProbeRunner"]
