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
    parse_string_map,
    require_bool,
    require_optional_string,
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
        """Initialize an empty command registry."""
        self._commands: dict[str, dict[str, Command]] = {}
        self._aliases: dict[str, str] = {}

    def add(self, command: Command) -> None:
        """Add one command to the registry."""
        by_what = self._commands.setdefault(command.verb, {})
        if command.what in by_what:
            msg = f"comando duplicado: {command.verb} WHAT={command.what}"
            raise RegistryError(msg)
        by_what[command.what] = command
        for alias in command.aliases:
            previous = self._aliases.get(alias)
            if previous and previous != command.verb:
                msg = (
                    f"alias duplicado: {alias} aponta para {previous} e {command.verb}"
                )
                raise RegistryError(msg)
            self._aliases[alias] = command.verb

    def validate(self) -> None:
        """Validate the complete discovered command registry."""
        if not self._commands:
            msg = "nenhum comando encontrado em scripts/cmd/<verbo>/<what>"
            raise RegistryError(msg)
        for verb, commands in sorted(self._commands.items()):
            if DEFAULT_COMMAND not in commands:
                msg = f"verbo '{verb}' sem WHAT={DEFAULT_COMMAND}"
                raise RegistryError(msg)
            domains = {command.domain for command in commands.values()}
            if len(domains) != 1:
                valid = ", ".join(sorted(domains))
                msg = f"verbo '{verb}' declara mais de um domain: {valid}"
                raise RegistryError(msg)
            for command in commands.values():
                if command.what != DEFAULT_COMMAND and command.aliases:
                    msg = f"{command.path}: aliases podem ser declarados apenas em WHAT={DEFAULT_COMMAND}"
                    raise RegistryError(msg)
                validate_command_contract(command)
            validate_all_choices(verb, commands)

    def verbs(self) -> list[str]:
        """Return promoted verbs in display order."""
        return sorted(self._commands)

    def resolve_verb(self, verb: str) -> str:
        """Resolve one verb or alias to its canonical verb name."""
        resolved = self._aliases.get(verb, verb)
        if resolved not in self._commands:
            msg = f"verbo '{verb}' desconhecido"
            raise RegistryError(msg)
        return resolved

    def commands(self, verb: str) -> Mapping[str, Command]:
        """Return commands registered for one verb."""
        return self._commands[self.resolve_verb(verb)]

    def command(self, verb: str, what: str) -> Command:
        """Return one command by verb and WHAT value."""
        commands = self.commands(verb)
        if what not in commands:
            valid = " ".join(sorted(commands))
            msg = f"WHAT='{what}' invalido para {verb}. Validos: {valid}"
            raise RegistryError(msg)
        return commands[what]

    def aliases_for(self, verb: str) -> list[str]:
        """Return aliases that resolve to one canonical verb."""
        return sorted(
            alias for alias, target in self._aliases.items() if target == verb
        )


def discover() -> Registry:
    """Discover and validate the promoted command registry."""
    registry = Registry()
    if not SCRIPTS_DIR.exists():
        msg = "diretorio scripts/cmd ausente"
        raise RegistryError(msg)
    for verb_dir in sorted(SCRIPTS_DIR.iterdir(), key=lambda item: item.name):
        if not verb_dir.is_dir() or verb_dir.name in IGNORED_DIRS:
            continue
        for path in sorted(verb_dir.iterdir(), key=lambda item: item.name):
            if path.name == "__pycache__":
                continue
            if path.is_dir():
                msg = f"{path}: diretorio publico nao pode estar aninhado"
                raise RegistryError(msg)
            if path.suffix not in COMMAND_SUFFIXES:
                msg = f"{path}: arquivo publico deve ser .sh ou .py"
                raise RegistryError(msg)
            registry.add(load_command(path, verb_dir.name))
    registry.validate()
    return registry


def load_command(path: Path, expected_verb: str) -> Command:
    """Load one promoted command from its header TOML."""
    data = header_data(path)
    verb = require_string(data, "verb", path)
    what = require_string(data, "what", path)
    if verb != expected_verb:
        msg = f"{path}: header verb={verb} diverge do diretorio {expected_verb}"
        raise RegistryError(msg)
    if what != path.stem:
        msg = f"{path}: header what={what} diverge do arquivo {path.stem}"
        raise RegistryError(msg)
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
        target=require_optional_string(data, "target", path),
        target_env=parse_string_map(data.get("target_env"), path),
    )


def header_data(path: Path) -> TomlTable:
    """Return parsed TOML metadata from one command header."""
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
        msg = f"{path}: sem header flext-command"
        raise RegistryError(msg)
    try:
        return cast("TomlTable", tomllib.loads("\n".join(payload)))
    except tomllib.TOMLDecodeError as exc:
        msg = f"{path}: header TOML invalido: {exc}"
        raise RegistryError(msg) from exc
