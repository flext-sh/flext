"""Command dispatch framework for FLEXT Makefile verbs."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, cast

TomlValue = str | int | float | bool | list["TomlValue"] | dict[str, "TomlValue"]
TomlTable = dict[str, TomlValue]

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
DEFAULT_COMMAND = "all"

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts" / "cmd"


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


def main(argv: Sequence[str] | None = None) -> int:
    args = tuple(_apply_env_from_args((sys.argv[1:] if argv is None else argv)))
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
    items = []
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


def run(command: Command) -> int:
    env = command_env(command)
    if command.path.suffix == ".py":
        return run_python(command, env)
    return subprocess.run(
        ["bash", str(command.path)], cwd=str(ROOT), env=env, check=False
    ).returncode


def run_make(
    target: str,
    *,
    make_args: Sequence[str] = (),
    extra_env: Mapping[str, str] | None = None,
) -> int:
    """Run a Makefile target and return the process exit code."""

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    command = ("make", target, *make_args)
    result = subprocess.run(list(command), cwd=str(ROOT), env=env, check=False)
    return result.returncode


def run_shell(
    command: Sequence[str], *, extra_env: Mapping[str, str] | None = None
) -> int:
    """Run a generic shell command and return the process exit code."""

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(list(command), cwd=str(ROOT), env=env, check=False)
    return result.returncode


def run_python(command: Command, env: Mapping[str, str]) -> int:
    """Execute a promoted Python command under canonical dispatch env."""

    return subprocess.run(
        [sys.executable, str(command.path)], cwd=str(ROOT), env=dict(env), check=False
    ).returncode


def command_env(command: Command) -> dict[str, str]:
    """Return canonical environment for a promoted command."""

    env = os.environ.copy()
    env["WHAT"] = command.what
    env["FLEXT_COMMAND_DISPATCHED"] = "Y"
    env["FLEXT_COMMAND_VERB"] = command.verb
    env["FLEXT_COMMAND_WHAT"] = command.what
    env["FLEXT_COMMAND_PATH"] = str(command.path.resolve())
    env["PYTHONPATH"] = str(ROOT)
    return env


def require_dispatched(path: Path) -> None:
    """Fail if a promoted Python command is run outside `scripts/dispatch.py`."""

    expected = str(path.resolve())
    if (
        os.environ.get("FLEXT_COMMAND_DISPATCHED") == "Y"
        and os.environ.get("FLEXT_COMMAND_PATH") == expected
    ):
        return
    print(
        "ERRO: comandos publicos devem ser executados via make <verbo> WHAT=<acao>",
        file=sys.stderr,
    )
    raise SystemExit(2)


def promoted_main(script_file: str | Path, handler: Callable[[], int]) -> NoReturn:
    """Run a promoted Python command through the dispatch guard."""

    require_dispatched(Path(script_file))
    raise SystemExit(handler())


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
        return cast(TomlTable, tomllib.loads("\n".join(payload)))
    except tomllib.TOMLDecodeError as exc:
        raise RegistryError(f"{path}: header TOML invalido: {exc}") from exc


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


def render_global_help(registry: Registry) -> str:
    lines = ["flext - make <verbo> WHAT=<acao> [PARAM=value ...]", ""]
    for verb in registry.verbs():
        command = registry.command(verb, DEFAULT_COMMAND)
        aliases = registry.aliases_for(verb)
        suffix = f" (alias: {', '.join(aliases)})" if aliases else ""
        lines.append(f"  {verb:14} [{command.domain:12}] {command.summary}{suffix}")
    lines.extend([
        "",
        "Use: make <verbo> para lista os WHAT disponiveis.",
        "Use: make <verbo> WHAT=<acao> para executar.",
        "Use: make <verbo> WHAT=<verbo>/<acao> para help da acao.",
        "Comandos mutadores exigem APPLY=Y.",
    ])
    return "\n".join(lines)


def render_verb_help(registry: Registry, requested_verb: str) -> str:
    verb = registry.resolve_verb(requested_verb)
    aliases = registry.aliases_for(verb)
    alias_suffix = f" (alias: {', '.join(aliases)})" if aliases else ""
    lines = [
        f"make {requested_verb} WHAT=<WHAT>{alias_suffix}",
        "",
        "WHAT disponiveis:",
    ]
    commands = registry.commands(verb)
    for what, command in sorted(commands.items()):
        marker = " [mutates]" if command.mutates else ""
        lines.append(f"  {what:20} [{command.domain:12}] {command.summary}{marker}")
    command_params = [
        (what, command) for what, command in sorted(commands.items()) if command.params
    ]
    if command_params:
        lines.extend(["", "Opcoes por WHAT:"])
        for what, command in command_params:
            lines.append(f"  {what:20} {format_params_inline(command.params)}")
        lines.extend([
            "",
            "Detalhe de uma acao:",
            f"  make {requested_verb} WHAT={requested_verb}/<WHAT>",
            f"  make {requested_verb} WHAT=<WHAT> OPTIONS=Y",
        ])
    rules = sorted({rule for command in commands.values() for rule in command.rules})
    if rules:
        lines.extend(["", "Regras:"])
        for rule in rules:
            lines.append(f"  - {rule}")
    examples = sorted({
        example_for(command, requested_verb) for command in commands.values()
    })
    if examples:
        lines.extend(["", "Exemplos:"])
        for example in examples:
            lines.append(f"  {example}")
    return "\n".join(lines)


def render_command_help(registry: Registry, requested_verb: str, what: str) -> str:
    command = registry.command(requested_verb, what)
    lines = [
        f"make {requested_verb} WHAT={what}",
        "",
        f"Dominio: {command.domain}",
        f"Mutacao: {'sim' if command.mutates else 'nao'}",
    ]
    if command.mutates:
        lines.append("Sem APPLY=Y a execucao fica em dry-run.")
    lines.extend(["", command.summary, command.description])
    if command.params:
        lines.extend(["", "Parametros:"])
        for param in command.params:
            required = " obrigatorio" if param.required else ""
            default = f" default={param.default}" if param.default else ""
            choices = f" choices={','.join(param.choices)}" if param.choices else ""
            lines.append(f"  {param.name:24} {param.help}{required}{default}{choices}")
    if command.rules:
        lines.extend(["", "Regras:"])
        for rule in command.rules:
            lines.append(f"  - {rule}")
    lines.extend(["", "Exemplo:", f"  {example_for(command, requested_verb)}"])
    return "\n".join(lines)


def render_dry_run(command: Command, requested_verb: str, what: str) -> str:
    lines = [
        "DRY-RUN: nenhuma mutacao executada.",
        f"Comando: make {requested_verb} WHAT={what}",
        f"Dominio: {command.domain}",
        f"Resumo: {command.summary}",
        "Regra: comando mutador exige APPLY=Y.",
    ]
    if command.params:
        lines.extend(["", "Parametros atuais:"])
        for param in command.params:
            value = param_value(param, command)
            shown = value if value else "<ausente>"
            required = "obrigatorio" if param.required else "opcional"
            choices = f" choices={','.join(param.choices)}" if param.choices else ""
            lines.append(
                f"  {param.name:24} {shown:20} {required}{choices} - {param.help}"
            )
    lines.extend([
        "",
        "Execucao canonica:",
        f"  {example_for(command, requested_verb)}",
    ])
    return "\n".join(lines)


def format_params_inline(params: Iterable[Param]) -> str:
    parts: list[str] = []
    for param in params:
        suffix = "*" if param.required else ""
        detail: list[str] = []
        if param.default:
            detail.append(f"default={param.default}")
        if param.choices:
            detail.append(f"choices={','.join(param.choices)}")
        rendered = f"{param.name}{suffix}"
        if detail:
            rendered = f"{rendered}({';'.join(detail)})"
        parts.append(rendered)
    return ", ".join(parts)


def example_for(command: Command, requested_verb: str) -> str:
    canonical = f"make {command.verb}"
    requested = f"make {requested_verb}"
    if command.example.startswith(canonical):
        return requested + command.example[len(canonical) :]
    return command.example


def env_enabled(name: str) -> bool:
    return os.environ.get(name, "N").upper() in {"1", "Y", "YES", "TRUE"}


if __name__ == "__main__":
    raise SystemExit(main())
