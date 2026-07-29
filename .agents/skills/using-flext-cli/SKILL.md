---
name: using-flext-cli
description: 'Guidance for building or testing FLEXT CLI commands. Covers the model-driven Typer abstraction, CLI settings, output formatting, and CliRunner testing.'
license: MIT
metadata:
  version: 1.1.0
---
# Using flext-cli

Quick-reference for building CLI commands with `flext_cli`.

## Workflow

1. Define a Pydantic input model (`m.BaseModel`).
2. Register a handler and build a Typer command with `FlextCliCli.model_command`.
3. Test with `CliRunner` from `typer.testing`.

## Critical rules

- Model-driven commands only; avoid ad-hoc Typer functions.
- Use `FlextCliSettings.fetch_global()` for configuration; `s` is the service/runtime alias, not settings.
- Command input models are plain `m.BaseModel` subclasses (`m.CliInput`/`m.CliOutput` do not exist).
- `FlextCliCli.build_model_command` does not exist; the canonical method is `FlextCliCli.model_command(...)`.

## Aliases

```python
from flext_cli import c, m, p, r, s, t, u
```

`flext_cli` may still expose migration-era operational names in the live API. Do not add new dependencies on `h` or `x`; target the v0.13 owners when refactoring.

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `m` | models |
| `p` | protocols |
| `r` | result (reexported from `flext_core`) |
| `s` | service / runtime (`FlextCliServiceBase`) |
| `t` | typings |
| `u` | utilities |

Settings are accessed via `FlextCliSettings` (no short alias).

## Model-driven command

```python
from __future__ import annotations

from flext_cli import m, t
from flext_cli.services.cli import FlextCliCli
from flext_cli.settings import FlextCliSettings

class GreetInput(m.BaseModel):
    name: str
    shout: bool = False

def greet_handler(model: GreetInput) -> t.JsonValue:
    message = f"Hello, {model.name}!"
    if model.shout:
        message = message.upper()
    return {"message": message}

settings = FlextCliSettings.fetch_global()
command = FlextCliCli.model_command(
    model_cls=GreetInput,
    handler=greet_handler,
    settings=settings,
)
```

## Settings

Import and use the existing settings class; do not redefine it:

```python
from flext_cli.settings import FlextCliSettings

settings = FlextCliSettings.fetch_global()
```

## Testing

```python notest
# Illustrative test sketch — real CLI tests require a Typer app, command group,
# and runner assembled via FlextCliCli.create_app_with_common_params/create_group/
# register_command/add_group/create_cli_runner.
from flext_cli import m, t, u
from flext_cli.services.cli import FlextCliCli
from flext_cli.settings import FlextCliSettings

class GreetInput(m.BaseModel):
    name: str

def greet_handler(model: GreetInput) -> t.JsonValue:
    return {"message": f"Hello, {model.name}!"}

settings = FlextCliSettings.fetch_global()
command = FlextCliCli.model_command(
    model_cls=GreetInput,
    handler=greet_handler,
    settings=settings,
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

- `docs/guides/using-flext-cli.md`
- `.agents/skills/coding-standards/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
