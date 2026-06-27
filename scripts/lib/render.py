"""Help and dry-run text rendering for the dispatch framework."""

from __future__ import annotations

from collections.abc import Iterable

from scripts.lib.registry import (
    DEFAULT_COMMAND,
    Command,
    Param,
    Registry,
    param_value,
)


def render_global_help(registry: Registry) -> str:
    """Render top-level dispatcher help."""
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
    """Render help for one promoted verb."""
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
        lines.extend(f"  - {rule}" for rule in rules)
    examples = sorted({
        example_for(command, requested_verb) for command in commands.values()
    })
    if examples:
        lines.extend(["", "Exemplos:"])
        lines.extend(f"  {example}" for example in examples)
    return "\n".join(lines)


def render_command_help(registry: Registry, requested_verb: str, what: str) -> str:
    """Render help for one promoted command."""
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
        lines.extend(f"  - {rule}" for rule in command.rules)
    lines.extend(["", "Exemplo:", f"  {example_for(command, requested_verb)}"])
    return "\n".join(lines)


def render_dry_run(command: Command, requested_verb: str, what: str) -> str:
    """Render dry-run output for one mutating command."""
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
            shown = value or "<ausente>"
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
    """Render command params in one compact inline form."""
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
    """Return the example adjusted for an alias-preserving verb."""
    canonical = f"make {command.verb}"
    requested = f"make {requested_verb}"
    if command.example.startswith(canonical):
        return requested + command.example[len(canonical) :]
    return command.example
