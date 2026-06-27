"""Command registry discovery from `scripts/cmd/<verb>/<what>.py|.sh`."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from scripts.lib.parsing import (
    DEFAULT_COMMAND,
    Command,
    Param,
    RegistryError,
    TomlTable,
    param_value,
    parse_aliases,
    parse_params,
    parse_string_list,
    require_bool,
    require_string,
    validate_all_choices,
    validate_command_contract,
    validate_invocation,
)

__all__ = [
    "COMMAND_SUFFIXES",
    "DEFAULT_COMMAND",
    "HEADER_END",
    "HEADER_START",
    "IGNORED_DIRS",
    "ROOT",
    "SCRIPTS_DIR",
    "Command",
    "Param",
    "Registry",
    "RegistryError",
    "discover",
    "header_data",
    "load_command",
    "param_value",
    "validate_invocation",
]

HEADER_START = "/// flext-command"
HEADER_END = "///"
COMMAND_SUFFIXES = frozenset({".sh", ".py"})
IGNORED_DIRS = frozenset({
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "lib",
    "maintenance",
    "github",
})

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts" / "cmd"


class Registry:
    """Discovered command registry from `scripts/cmd/<verb>/<what>.py|.sh`."""

    def __init__(self) -> None:
        self._commands: dict[str, dict[str, Command]] = {}
        self._aliases: dict[str, str] = {}

    def add(self, command: Command) -> None:
        by_what = self._commands.setdefault(command.verb, {})
        if command.what in by_what:
            raise RegistryError(
                f"comando duplicado: {command.verb} WHAT={command.what}"
            )
        by_what[command.what] = command
        for alias in command.aliases:
            previous = self._aliases.get(alias)
            if previous and previous != command.verb:
                raise RegistryError(
                    f"alias duplicado: {alias} aponta para {previous} e {command.verb}"
                )
            self._aliases[alias] = command.verb

    def validate(self) -> None:
        if not self._commands:
            raise RegistryError(
                "nenhum comando encontrado em scripts/cmd/<verbo>/<what>"
            )
        for verb, commands in sorted(self._commands.items()):
            if DEFAULT_COMMAND not in commands:
                raise RegistryError(f"verbo '{verb}' sem WHAT={DEFAULT_COMMAND}")
            domains = {command.domain for command in commands.values()}
            if len(domains) != 1:
                valid = ", ".join(sorted(domains))
                raise RegistryError(
                    f"verbo '{verb}' declara mais de um domain: {valid}"
                )
            for command in commands.values():
                if command.what != DEFAULT_COMMAND and command.aliases:
                    raise RegistryError(
                        f"{command.path}: aliases podem ser declarados apenas em WHAT={DEFAULT_COMMAND}"
                    )
                validate_command_contract(command)
            validate_all_choices(verb, commands)

    def verbs(self) -> list[str]:
        return sorted(self._commands)

    def resolve_verb(self, verb: str) -> str:
        resolved = self._aliases.get(verb, verb)
        if resolved not in self._commands:
            raise RegistryError(f"verbo '{verb}' desconhecido")
        return resolved

    def commands(self, verb: str) -> Mapping[str, Command]:
        return self._commands[self.resolve_verb(verb)]

    def command(self, verb: str, what: str) -> Command:
        commands = self.commands(verb)
        if what not in commands:
            valid = " ".join(sorted(commands))
            raise RegistryError(f"WHAT='{what}' invalido para {verb}. Validos: {valid}")
        return commands[what]

    def aliases_for(self, verb: str) -> list[str]:
        return sorted(
            alias for alias, target in self._aliases.items() if target == verb
        )


def discover() -> Registry:
    registry = Registry()
    if not SCRIPTS_DIR.exists():
        raise RegistryError("diretorio scripts/cmd ausente")
    for verb_dir in sorted(SCRIPTS_DIR.iterdir(), key=lambda item: item.name):
        if not verb_dir.is_dir() or verb_dir.name in IGNORED_DIRS:
            continue
        for path in sorted(verb_dir.iterdir(), key=lambda item: item.name):
            if path.name == "__pycache__":
                continue
            if path.is_dir():
                raise RegistryError(
                    f"{path}: diretorio publico nao pode estar aninhado"
                )
            if path.suffix not in COMMAND_SUFFIXES:
                raise RegistryError(f"{path}: arquivo publico deve ser .sh ou .py")
            registry.add(load_command(path, verb_dir.name))
    registry.validate()
    return registry


def load_command(path: Path, expected_verb: str) -> Command:
    data = header_data(path)
    verb = require_string(data, "verb", path)
    what = require_string(data, "what", path)
    if verb != expected_verb:
        raise RegistryError(
            f"{path}: header verb={verb} diverge do diretorio {expected_verb}"
        )
    if what != path.stem:
        raise RegistryError(
            f"{path}: header what={what} diverge do arquivo {path.stem}"
        )
    return Command(
        verb=verb,
        what=what,
        domain=require_string(data, "domain", path),
        summary=require_string(data, "summary", path),
        description=require_string(data, "description", path),
        example=require_string(data, "example", path),
        path=path,
        mutates=require_bool(data, "mutates", path),
        aliases=parse_aliases(data.get("aliases"), path),
        params=parse_params(data.get("params"), path),
        rules=parse_string_list(data, "rules", path),
    )


def header_data(path: Path) -> TomlTable:
    lines = path.read_text(encoding="utf-8").splitlines()[:220]
    in_header = False
    payload: list[str] = []
    for raw in lines:
        stripped = raw.strip()
        content = stripped[1:].strip() if stripped.startswith("#") else stripped
        if content == HEADER_START:
            in_header = True
            continue
        if in_header and content == HEADER_END:
            break
        if in_header:
            payload.append(content)
    if not payload:
        raise RegistryError(f"{path}: sem header flext-command")
    try:
        return cast("TomlTable", tomllib.loads("\n".join(payload)))
    except tomllib.TOMLDecodeError as exc:
        raise RegistryError(f"{path}: header TOML invalido: {exc}") from exc
