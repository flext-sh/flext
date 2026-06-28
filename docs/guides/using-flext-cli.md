# Using flext-cli

`flext_cli` provides a unified Typer abstraction for model-driven CLI applications.

## Aliases

```python
from flext_cli import c, m, p, r, s, t, u
```

## Purpose

- Define CLI commands as Pydantic models.
- Let `FlextCliCli` convert model fields into Typer options.
- Keep output formatting, prompts, and runtime consistent across FLEXT CLI tools.

## Settings

CLI settings extend `FlextSettings` with `env_prefix="FLEXT_CLI_"`:

```python
from flext_cli import c
from flext_core import FlextSettings, m

class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")

    class CliSettings(m.SettingsValue):
        verbose: bool = c.Cli.CLI_DEFAULT_VERBOSE
        output_format: str = c.Cli.OUTPUT_DEFAULT_FORMAT_TYPE
```

## Model-driven command

```python
from __future__ import annotations

from flext_cli import c, m, p, r, s, t, u
from flext_cli.services.cli import FlextCliCli


class GreetInput(m.CliInput):
    name: str
    shout: bool = False


def greet_handler(model: GreetInput) -> t.JsonValue:
    message = f"Hello, {model.name}!"
    if model.shout:
        message = message.upper()
    return {"message": message}


# Build a Typer command from the model + handler
command = FlextCliCli.build_model_command(
    model_cls=GreetInput,
    handler=greet_handler,
    settings=s.fetch_global(),
)
```

## Testing a command

```python
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["greet", "--name", "Ada"])
assert result.exit_code == 0
```

## Good practices

- Use `m.CliInput` / `m.CliOutput` models for command I/O.
- Read settings via `s.fetch_global()` (the `FlextCliSettings` singleton).
- Use `u.Cli` helpers to resolve annotations and defaults.

## Bad practices

```python
import typer

def main(name: str):  # ad-hoc command, no model
    print(f"Hello, {name}")
```

## Related

- `.agents/skills/using-flext-cli/SKILL.md`
- `.agents/skills/coding-standards/SKILL.md`
- `flext-cli/src/flext_cli/services/cli.py`
