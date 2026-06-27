"""Command metadata: contracts, parsing, and validation helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from flext_cli import u

TomlValue = str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"]
TomlTable = dict[str, TomlValue]

DEFAULT_COMMAND = "all"


@dataclass(frozen=True, slots=True)
class Param:
    """One promoted-command parameter declared in the header TOML."""

    name: str
    help: str
    required: bool = False
    default: str = ""
    choices: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Command:
    """One promoted command discovered from `scripts/cmd/<verb>/<what>.py`."""

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
    target: str = ""
    target_env: tuple[tuple[str, str], ...] = ()


class RegistryError(Exception):
    """Raised for invalid command metadata or invalid CLI invocation."""


def require_string(data: Mapping[str, TomlValue], key: str, path: Path) -> str:
    """Return one required non-empty string field from header TOML."""
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        msg = f"{path}: campo obrigatorio ausente: {key}"
        raise RegistryError(msg)
    return value.strip()


def require_optional_string(data: Mapping[str, TomlValue], key: str, path: Path) -> str:
    """Return one optional string field from header TOML."""
    value = data.get(key, "")
    if not isinstance(value, str):
        msg = f"{path}: campo opcional {key} deve ser string"
        raise RegistryError(msg)
    return value.strip()


def require_bool(data: Mapping[str, TomlValue], key: str, path: Path) -> bool:
    """Return one required boolean field from header TOML."""
    value = data.get(key)
    if not isinstance(value, bool):
        msg = f"{path}: campo booleano obrigatorio ausente: {key}"
        raise RegistryError(msg)
    return value


def parse_aliases(value: TomlValue | None, path: Path) -> tuple[str, ...]:
    """Parse optional command aliases from header TOML."""
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = f"{path}: aliases deve ser lista de strings"
        raise RegistryError(msg)
    aliases: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            msg = f"{path}: aliases invalido"
            raise RegistryError(msg)
        aliases.append(item.strip())
    return tuple(aliases)


def parse_string_list(
    data: Mapping[str, TomlValue] | TomlValue, field: str, path: Path
) -> tuple[str, ...]:
    """Parse one optional string-list field from header TOML."""
    value: TomlValue | None
    if isinstance(data, dict):
        value = data.get(field)
    else:
        msg = f"{path}: campo {field} deve ser lista de strings"
        raise RegistryError(msg)
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = f"{path}: {field} deve ser lista de strings"
        raise RegistryError(msg)
    values: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            msg = f"{path}: {field} invalido"
            raise RegistryError(msg)
        values.append(item.strip())
    return tuple(values)


def parse_params(value: TomlValue | None, path: Path) -> tuple[Param, ...]:
    """Parse promoted-command parameter declarations from header TOML."""
    if value is None:
        return ()
    if not isinstance(value, list):
        msg = f"{path}: params deve conter lista"
        raise RegistryError(msg)
    params: list[Param] = []
    for item in value:
        if not isinstance(item, dict):
            msg = f"{path}: params deve conter objetos TOML"
            raise RegistryError(msg)
        params.append(parse_param(item, path))
    return tuple(params)


def parse_string_map(
    value: TomlValue | None, path: Path
) -> tuple[tuple[str, str], ...]:
    """Parse an optional string-to-string mapping from header TOML."""
    if value is None:
        return ()
    if not isinstance(value, dict):
        msg = f"{path}: target_env deve ser objeto TOML"
        raise RegistryError(msg)
    items: list[tuple[str, str]] = []
    for key, item in sorted(value.items()):
        if not isinstance(key, str) or not key.strip():
            msg = f"{path}: target_env possui chave invalida"
            raise RegistryError(msg)
        if not isinstance(item, str):
            msg = f"{path}: target_env.{key} deve ser string"
            raise RegistryError(msg)
        items.append((key.strip(), item))
    return tuple(items)


def parse_param(data: Mapping[str, TomlValue], path: Path) -> Param:
    """Parse one parameter object from header TOML."""
    name = require_string(data, "name", path)
    help_text = require_string(data, "help", path)
    required_raw = data.get("required", False)
    default_raw = data.get("default", "")
    if not isinstance(required_raw, bool):
        msg = f"{path}: params.required deve ser booleano"
        raise RegistryError(msg)
    if not isinstance(default_raw, str):
        msg = f"{path}: params.default deve ser string"
        raise RegistryError(msg)
    return Param(
        name=name,
        help=help_text,
        required=required_raw,
        default=default_raw,
        choices=parse_string_list(data, "choices", path),
    )


def validate_invocation(command: Command, *, require_required: bool = True) -> None:
    """Validate environment-backed parameter values for one invocation."""
    for param in command.params:
        value = param_value(param, command)
        if require_required and param.required and not value:
            msg = (
                f"{command.verb} WHAT={command.what}: parametro obrigatorio ausente: "
                f"{param.name}; exemplo: {command.example}"
            )
            raise RegistryError(msg)
        if value and param.choices and value not in param.choices:
            valid = "|".join(param.choices)
            msg = f"{command.verb} WHAT={command.what}: {param.name}={value!r} invalido; validos: {valid}"
            raise RegistryError(msg)


def validate_command_contract(command: Command) -> None:
    """Validate one discovered command against the dispatcher contract."""
    if command.mutates and not any(param.name == "APPLY" for param in command.params):
        msg = f"{command.path}: comandos mutadores devem declarar param APPLY com validacao de mudanca"
        raise RegistryError(msg)
    if command.path.name != f"{command.what}.py" and command.path.suffix != ".sh":
        msg = f"{command.path}: comando deve usar extensão .py ou .sh"
        raise RegistryError(msg)
    if not command.summary.strip():
        msg = f"{command.path}: campo summary não pode estar vazio"
        raise RegistryError(msg)
    if command.target and command.path.suffix != ".py":
        msg = f"{command.path}: target header-only deve usar arquivo .py"
        raise RegistryError(msg)
    if command.target_env and not command.target:
        msg = f"{command.path}: target_env exige target"
        raise RegistryError(msg)


def validate_all_choices(verb: str, commands: Mapping[str, Command]) -> None:
    """Validate WHAT choices declared by the verb default command."""
    all_command = commands[DEFAULT_COMMAND]
    what_param = next(
        (param for param in all_command.params if param.name == "WHAT"), None
    )
    if what_param is None or not what_param.choices:
        return
    declared = tuple(sorted(what_param.choices))
    actual = tuple(sorted(commands))
    if declared != actual:
        msg = (
            f"{all_command.path}: choices de WHAT divergem dos comandos promovidos para {verb}: "
            f"declared={','.join(declared)} actual={','.join(actual)}"
        )
        raise RegistryError(msg)


def param_value(param: Param, command: Command) -> str:
    """Return the current value for one promoted-command parameter."""
    if param.name == "WHAT":
        return command.what
    return u.Cli.process_env().get(param.name, param.default).strip()
