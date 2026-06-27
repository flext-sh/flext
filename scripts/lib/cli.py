"""CLI orchestration: argument handling, help routing, and dispatch."""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence

from scripts.lib.exec import env_enabled, run
from scripts.lib.registry import (
    DEFAULT_COMMAND,
    Registry,
    RegistryError,
    discover,
    validate_invocation,
)
from scripts.lib.render import (
    render_command_help,
    render_dry_run,
    render_global_help,
    render_verb_help,
)


def main(argv: Sequence[str] | None = None) -> int:
    args = tuple(_apply_env_from_args(sys.argv[1:] if argv is None else argv))
    try:
        if args and args[0] in {"help", "--help", "-h"}:
            return _print_help("")
        if not args:
            return _print_help(os.environ.get("WHAT", "").strip())
        if args[0] == "--validate":
            return 0
        return dispatch(args[0])
    except RegistryError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


def _apply_env_from_args(raw_args: Sequence[str]) -> list[str]:
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
    return command_args


def _print_help(requested: str) -> int:
    registry = discover()
    if requested and "/" in requested:
        verb, what = requested.split("/", 1)
        return print_command_or_verb_help(registry, verb, what)
    if requested:
        return print_verb_help(registry, requested)
    print(render_global_help(registry))
    return 0


def print_command_or_verb_help(registry: Registry, verb: str, what: str) -> int:
    print(render_command_help(registry, verb, what))
    return 0


def print_verb_help(registry: Registry, requested_verb: str) -> int:
    print(render_verb_help(registry, requested_verb))
    return 0


def dispatch(requested_verb: str) -> int:
    registry = discover()
    verb = registry.resolve_verb(requested_verb)
    requested = os.environ.get("WHAT", "").strip() or DEFAULT_COMMAND
    what_values = _normalize_what(requested)

    if requested == "help":
        print(render_verb_help(registry, requested_verb))
        return 0
    if env_enabled("HELP") or env_enabled("OPTIONS"):
        if len(what_values) == 1:
            return print_command_or_verb_help(registry, requested_verb, what_values[0])
        print_verbosity_help(registry, requested_verb, what_values)
        return 0
    code = 0
    for what in what_values:
        command = registry.command(verb, what)
        is_dry_run = command.mutates and os.environ.get("APPLY", "N").upper() != "Y"
        validate_invocation(command, require_required=not is_dry_run)
        if is_dry_run:
            print(render_dry_run(command, requested_verb, what))
            continue
        child_code = run(command)
        if child_code != 0:
            return child_code
        code = child_code
    return code


def _normalize_what(raw: str) -> tuple[str, ...]:
    items: list[str] = []
    for raw_item in raw.split(","):
        item = raw_item.strip()
        if not item:
            continue
        if "/" in item:
            item = item.rsplit("/", 1)[-1].strip()
        if not item:
            continue
        items.append(item)
    if not items:
        return (DEFAULT_COMMAND,)
    return tuple(dict.fromkeys(items))


def print_verbosity_help(
    registry: Registry, requested_verb: str, what_values: tuple[str, ...]
) -> None:
    if len(what_values) != 1:
        print(render_verb_help(registry, requested_verb))
        return
    print(render_command_help(registry, requested_verb, what_values[0]))
