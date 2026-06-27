"""Command metadata: contracts, parsing, and validation helpers."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

TomlValue = str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"]
TomlTable = dict[str, TomlValue]

DEFAULT_COMMAND = "all"


@dataclass(frozen=True, slots=True)
class Param:
    name: str
    help: str
    required: bool = False
    default: str = ""
    choices: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Command:
    verb: str
    what: str
    domain: str
    summary: str
    description: str
    example: str
    path: Path
    mutates: bool
    aliases: tuple[str, ...]
    params: tuple[Param, ...]
    rules: tuple[str, ...]


class RegistryError(Exception):
    """Raised for invalid command metadata or invalid CLI invocation."""


def require_string(data: Mapping[str, TomlValue], key: str, path: Path) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{path}: campo obrigatorio ausente: {key}")
    return value.strip()


def require_bool(data: Mapping[str, TomlValue], key: str, path: Path) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise RegistryError(f"{path}: campo booleano obrigatorio ausente: {key}")
    return value


def parse_aliases(value: TomlValue | None, path: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise RegistryError(f"{path}: aliases deve ser lista de strings")
    aliases: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RegistryError(f"{path}: aliases invalido")
        aliases.append(item.strip())
    return tuple(aliases)


def parse_string_list(
    data: Mapping[str, TomlValue] | TomlValue, field: str, path: Path
) -> tuple[str, ...]:
    value: TomlValue | None
    if isinstance(data, dict):
        value = data.get(field)
    else:
        raise RegistryError(f"{path}: campo {field} deve ser lista de strings")
    if value is None:
        return ()
    if not isinstance(value, list):
        raise RegistryError(f"{path}: {field} deve ser lista de strings")
    values: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise RegistryError(f"{path}: {field} invalido")
        values.append(item.strip())
    return tuple(values)


def parse_params(value: TomlValue | None, path: Path) -> tuple[Param, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise RegistryError(f"{path}: params deve conter lista")
    params: list[Param] = []
    for item in value:
        if not isinstance(item, dict):
            raise RegistryError(f"{path}: params deve conter objetos TOML")
        params.append(parse_param(item, path))
    return tuple(params)


def parse_param(data: Mapping[str, TomlValue], path: Path) -> Param:
    name = require_string(data, "name", path)
    help_text = require_string(data, "help", path)
    required_raw = data.get("required", False)
    default_raw = data.get("default", "")
    if not isinstance(required_raw, bool):
        raise RegistryError(f"{path}: params.required deve ser booleano")
    if not isinstance(default_raw, str):
        raise RegistryError(f"{path}: params.default deve ser string")
    return Param(
        name=name,
        help=help_text,
        required=required_raw,
        default=default_raw,
        choices=parse_string_list(data, "choices", path),
    )


def validate_invocation(command: Command, *, require_required: bool = True) -> None:
    for param in command.params:
        value = param_value(param, command)
        if require_required and param.required and not value:
            raise RegistryError(
                f"{command.verb} WHAT={command.what}: parametro obrigatorio ausente: {param.name}; exemplo: {command.example}"
            )
        if value and param.choices and value not in param.choices:
            valid = "|".join(param.choices)
            raise RegistryError(
                f"{command.verb} WHAT={command.what}: {param.name}={value!r} invalido; validos: {valid}"
            )


def validate_command_contract(command: Command) -> None:
    if command.mutates and not any(param.name == "APPLY" for param in command.params):
        raise RegistryError(
            f"{command.path}: comandos mutadores devem declarar param APPLY com validacao de mudanca"
        )
    if command.path.name != f"{command.what}.py" and command.path.suffix != ".sh":
        raise RegistryError(f"{command.path}: comando deve usar extensão .py ou .sh")
    if not command.summary.strip():
        raise RegistryError(f"{command.path}: campo summary não pode estar vazio")


def validate_all_choices(verb: str, commands: Mapping[str, Command]) -> None:
    all_command = commands[DEFAULT_COMMAND]
    what_param = next(
        (param for param in all_command.params if param.name == "WHAT"), None
    )
    if what_param is None or not what_param.choices:
        return
    declared = tuple(sorted(what_param.choices))
    actual = tuple(sorted(commands))
    if declared != actual:
        raise RegistryError(
            f"{all_command.path}: choices de WHAT divergem dos comandos promovidos para {verb}: "
            f"declared={','.join(declared)} actual={','.join(actual)}"
        )


def param_value(param: Param, command: Command) -> str:
    if param.name == "WHAT":
        return command.what
    return os.environ.get(param.name, param.default).strip()
