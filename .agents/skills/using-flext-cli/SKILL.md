---
name: using-flext-cli
description: 'Use when building or testing FLEXT CLI commands. Covers the model-driven
  Typer abstraction, CLI settings, output formatting, and CliRunner testing. DO NOT
  USE FOR: questions unrelated to flext-cli or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.0.0
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

1. Define a Pydantic input model.
2. Register a handler and build a Typer command with `FlextCliCli`.
3. Test with `CliRunner`.

## Critical rules

- Model-driven commands only; avoid ad-hoc Typer functions.
- Use `FlextCliSettings` / `s.fetch_global()` for configuration.
- Use `u.Cli` helpers for annotations and defaults.

## Aliases

```python
from flext_cli import c, m, p, r, s, t, u
```

## Model-driven command

```python
from __future__ import annotations
from flext_cli import m, s, t
from flext_cli.services.cli import FlextCliCli

class GreetInput(m.CliInput):
    name: str
    shout: bool = False

def greet_handler(model: GreetInput) -> t.JsonValue:
    message = f"Hello, {model.name}!"
    if model.shout:
        message = message.upper()
    return {"message": message}

command = FlextCliCli.build_model_command(
    model_cls=GreetInput,
    handler=greet_handler,
    settings=s.fetch_global(),
)
```

## Settings

```python
from flext_cli import c
from flext_core import FlextSettings, m

class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")
```

## Testing

```python
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["greet", "--name", "Ada"])
assert result.exit_code == 0
```

## Good

```python
class GreetInput(m.CliInput):
    name: str
```

## Bad

```python
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
