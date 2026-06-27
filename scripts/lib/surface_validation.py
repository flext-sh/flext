"""Exhaustive validation for the promoted scripts command surface."""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable, Mapping
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO

from scripts.lib.exec import make_targets
from scripts.lib.registry import ROOT, Command, Registry, discover

MAKE_CASE_RE = re.compile(r"^\s*([^)]*?)\)\s")
PUBLIC_VERBS_WITHOUT_CASE = frozenset({"clean", "test"})


@dataclass(frozen=True, slots=True)
class Probe:
    """One command-line probe for the promoted scripts surface."""

    name: str
    argv: tuple[str, ...]
    env: Mapping[str, str]
    expected_output: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """Captured result from one in-process dispatcher probe."""

    returncode: int
    stdout: str
    stderr: str


DispatchMain = Callable[[tuple[str, ...]], int]


def validate_surface(dispatch_main: DispatchMain) -> int:
    """Validate every promoted verb/WHAT route and return a shell exit code."""
    registry = discover()
    failures = [
        *validate_static_surface(registry),
        *run_probes(build_surface_probes(registry), dispatch_main),
    ]
    if failures:
        print("surface validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    command_count = sum(len(registry.commands(verb)) for verb in registry.verbs())
    print(
        f"surface validation ok: {len(registry.verbs())} verbs, {command_count} WHATs"
    )
    return 0


def validate_static_surface(registry: Registry) -> list[str]:
    """Validate registry metadata against the root Makefile surface."""
    failures: list[str] = []
    targets = make_targets()
    cases = make_dispatch_cases()
    for verb in registry.verbs():
        commands = registry.commands(verb)
        if verb not in targets:
            failures.append(f"make target ausente para verbo publico: {verb}")
        if verb in cases:
            case_values = cases[verb]
            expected = set(commands)
            missing = sorted(expected - case_values)
            extra = sorted(case_values - expected - {""})
            if missing:
                failures.append(f"make {verb}: WHAT ausente: {', '.join(missing)}")
            if extra:
                failures.append(f"make {verb}: WHAT sem registry: {', '.join(extra)}")
        elif len(commands) > 1 or verb not in PUBLIC_VERBS_WITHOUT_CASE:
            failures.append(f"make {verb}: sem dispatcher WHAT explicito")
        for command in commands.values():
            failures.extend(validate_command_static(command, targets))
    return failures


def validate_command_static(command: Command, targets: frozenset[str]) -> list[str]:
    """Validate one command's static contract."""
    failures: list[str] = []
    if command.target and command.target not in targets:
        failures.append(
            f"{command.verb} WHAT={command.what}: target ausente {command.target}"
        )
    text = f"{command.summary} {command.description} {command.example}".lower()
    if "legacy" in text:
        failures.append(
            f"{command.verb} WHAT={command.what}: texto ainda menciona legacy"
        )
    if not command.example.startswith(f"make {command.verb} "):
        failures.append(
            f"{command.verb} WHAT={command.what}: exemplo nao usa make canonico"
        )
    return failures


def build_surface_probes(registry: Registry) -> list[Probe]:
    """Build command-line probes for every promoted verb and WHAT."""
    probes = [
        Probe(
            name="global help",
            argv=("help",),
            env={},
            expected_output=("flext - make",),
        ),
    ]
    for verb in registry.verbs():
        probes.append(
            Probe(
                name=f"{verb} verb help",
                argv=(verb,),
                env={"WHAT": "help"},
                expected_output=(f"make {verb} WHAT=<WHAT>",),
            )
        )
        for command in sorted(
            registry.commands(verb).values(), key=lambda item: item.what
        ):
            probes.extend(command_probes(command))
    probes.extend((
        Probe("unknown verb", ("unknown-surface-verb",), {}, ("ERRO:",)),
        Probe("unknown WHAT", ("check",), {"WHAT": "unknown"}, ("ERRO:",)),
        Probe(
            "invalid choice",
            ("build",),
            {"WHAT": "docs", "DOCS_PHASE": "bad"},
            ("ERRO:",),
        ),
    ))
    return probes


def command_probes(command: Command) -> list[Probe]:
    """Build help, dry-run, and execution-route probes for one command."""
    env = command_env(command)
    probes = [
        Probe(
            name=f"{command.verb}/{command.what} help",
            argv=(command.verb,),
            env={**env, "HELP": "1"},
            expected_output=(f"make {command.verb} WHAT={command.what}",),
        )
    ]
    if command.mutates:
        probes.extend((
            Probe(
                name=f"{command.verb}/{command.what} dry-run",
                argv=(command.verb,),
                env=env,
                expected_output=("DRY-RUN: nenhuma mutacao executada.",),
            ),
            Probe(
                name=f"{command.verb}/{command.what} apply route",
                argv=(command.verb,),
                env={**env, "APPLY": "Y", "FLEXT_SURFACE_VALIDATE": "Y"},
                expected_output=("SURFACE-VALIDATE:",),
            ),
        ))
        return probes
    probes.append(
        Probe(
            name=f"{command.verb}/{command.what} route",
            argv=(command.verb,),
            env={**env, "FLEXT_SURFACE_VALIDATE": "Y"},
        )
    )
    return probes


def command_env(command: Command) -> dict[str, str]:
    """Return safe parameter values for one command probe."""
    env = {"WHAT": command.what}
    for param in command.params:
        if param.name == "WHAT":
            continue
        env[param.name] = safe_param_value(param.name, param.default)
    return env


def safe_param_value(name: str, default: str) -> str:
    """Return a safe validation value for one command parameter."""
    values = {
        "APPLY": "N",
        "CHECK_GATES": "lint",
        "DEPS_REPORT": "0",
        "DOCS_PHASE": "validate",
        "DRY_RUN": "1",
        "MESSAGE": "chore: surface validation",
        "PYTEST_ARGS": "-q",
        "TAG": "surface-validation",
        "VALIDATE_SCOPE": "project",
    }
    return values.get(name, default)


def run_probes(probes: list[Probe], dispatch_main: DispatchMain) -> list[str]:
    """Run all surface probes and return failure messages."""
    failures: list[str] = []
    for probe in probes:
        result = run_probe(probe, dispatch_main)
        output = f"{result.stdout}\n{result.stderr}"
        expect_failure = probe.name.startswith(("unknown", "invalid"))
        if expect_failure:
            if result.returncode == 0:
                failures.append(f"{probe.name}: expected failure, got exit 0")
            elif not all(fragment in output for fragment in probe.expected_output):
                failures.append(f"{probe.name}: missing expected error output")
            continue
        if result.returncode != 0:
            failures.append(f"{probe.name}: exit {result.returncode}: {output.strip()}")
            continue
        missing = [
            fragment for fragment in probe.expected_output if fragment not in output
        ]
        if missing:
            failures.append(f"{probe.name}: missing output: {', '.join(missing)}")
    return failures


def run_probe(probe: Probe, dispatch_main: DispatchMain) -> ProbeResult:
    """Run one dispatcher probe in-process with an isolated environment."""
    return with_probe_environment(
        probe.env,
        lambda: capture_dispatch(dispatch_main, probe.argv),
    )


def with_probe_environment(
    env: Mapping[str, str], action: Callable[[], ProbeResult]
) -> ProbeResult:
    """Run an action with probe environment values, then restore environment."""
    original = os.environ.copy()
    try:
        os.environ.clear()
        os.environ.update(original)
        os.environ.update(env)
        os.environ["PYTHONPATH"] = str(ROOT)
        return action()
    finally:
        os.environ.clear()
        os.environ.update(original)


def capture_dispatch(dispatch_main: DispatchMain, argv: tuple[str, ...]) -> ProbeResult:
    """Capture stdout/stderr from one dispatcher invocation."""
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            code = dispatch_main(argv)
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    return ProbeResult(
        returncode=code,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
    )


def make_dispatch_cases() -> dict[str, set[str]]:
    """Return public Make WHAT cases keyed by verb."""
    lines = (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
    cases: dict[str, set[str]] = {}
    for index, line in enumerate(lines):
        if not line or line.startswith(("\t", " ", "_", ".", "#")):
            continue
        head, marker, _tail = line.partition(":")
        if marker != ":" or not head:
            continue
        parsed = parse_case_values(lines[index + 1 :])
        if parsed:
            cases[head] = parsed
    return cases


def parse_case_values(lines: list[str]) -> set[str]:
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
            return values
        if stripped == "esac":
            return values
        match = MAKE_CASE_RE.match(stripped)
        if not match:
            continue
        labels = match.group(1).replace('"', "")
        for label in labels.split("|"):
            value = label.strip()
            if value != "*":
                values.add(value)
    return values
