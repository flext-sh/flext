---
name: using-flext-cli
description: 'Use when building or testing FLEXT CLI commands. Covers the model-driven Typer abstraction, CLI settings, output formatting, and CliRunner testing. DO NOT USE FOR: questions unrelated to flext-cli or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.1.0
---

# Using flext-cli

**UTILITY SKILL**

Quick-reference for building CLI commands with `flext_cli`.

## USE FOR

- Writing or testing FLEXT CLI commands.
- Using the model-driven Typer abstraction.
- Configuring CLI settings.

## DO NOT USE FOR

- Questions unrelated to `flext_cli`.
- Creating projects or architecture from scratch.

## Workflow

1. Define a Pydantic input model (`m.BaseModel`).
2. Register a handler and build a Typer command with `FlextCliCli.model_command`.
3. Test with `CliRunner` from `typer.testing`.

## Critical rules

- Model-driven commands only; avoid ad-hoc Typer functions.
- **ADR-005:** use `u.Cli.render_template` (Jinja2), `u.Cli.config_load`/`config_load_dir`, and `u.Cli.yaml_validate_schema` for all template/config/schema work; `flext-cli` is the SSOT owner. See `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Consume configuration only from the package-root singletons:
  `from flext_cli import config, settings`. Consumers never import the private
  settings module, instantiate the settings class, or call `fetch_global()`;
  `s` is the service/runtime alias, not settings.
- Command input models are plain `m.BaseModel` subclasses (`m.CliInput`/`m.CliOutput` do not exist).
- `FlextCliCli.build_model_command` does not exist; the canonical method is `FlextCliCli.model_command(...)`.

## Aliases

```python
from flext_cli import c, config, m, p, r, s, settings, t, u
```

`flext_cli` reexports `d`, `e`, `h`, `r`, `x` from `flext_core`.

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `m` | models |
| `p` | protocols |
| `r` | result (reexported from `flext_core`) |
| `s` | service / runtime (`FlextCliServiceBase`) |
| `t` | typings |
| `u` | utilities |

`config` and `settings` are validated package-root singleton exports, not short
aliases.

## Model-driven command

```python
from __future__ import annotations

from flext_cli import m, p, t
from flext_cli.services.cli import FlextCliCli


class GreetInput(m.BaseModel):
    name: str
    shout: bool = False


def greet_handler(model: GreetInput) -> t.JsonValue:
    message = f"Hello, {model.name}!"
    if model.shout:
        message = message.upper()
    return {"message": message}


command = FlextCliCli.model_command(
    model_cls=GreetInput,
    handler=greet_handler,
)
```

## Settings

Import and use the existing validated singletons from the package root; do not
redefine, instantiate, or privately import their classes:

```python
from flext_cli import config, settings
```

## Testing

```python notest
# Illustrative test sketch — real CLI tests require a Typer app, command group,
# and runner assembled via FlextCliCli.create_app_with_common_params/create_group/
# register_command/add_group/create_cli_runner.
from flext_cli import m, p, t, u
from flext_cli.services.cli import FlextCliCli


class GreetInput(m.BaseModel):
    name: str


def greet_handler(model: GreetInput) -> t.JsonValue:
    return {"message": f"Hello, {model.name}!"}


command = FlextCliCli.model_command(
    model_cls=GreetInput,
    handler=greet_handler,
)
_ = command
```

## Good

```python
from __future__ import annotations

from flext_cli import m


class GreetInput(m.BaseModel):
    name: str
```

## Bad

```python notest
# Illustrative anti-pattern: ad-hoc typer function instead of model-driven command.
import typer


def main(name: str):
    print(f"Hello, {name}")
```

## Validation

```bash
ruff check <file>
pyrefly check <file>
make test PROJECT=flext-cli MATCH=cli
```

## References

- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`
- `docs/guides/using-flext-cli.md`
- `.agents/skills/coding-standards/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
