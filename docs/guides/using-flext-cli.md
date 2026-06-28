# Using flext-cli

`flext_cli` provides a unified Typer abstraction for model-driven CLI applications.

## Aliases

```python
from flext_cli import c, m, p, r, s, t, u
```

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `m` | models |
| `p` | protocols |
| `r` | result (reexported from `flext_core`) |
| `s` | service / runtime |
| `t` | typings |
| `u` | utilities |

Settings are accessed via `FlextCliSettings` (no short alias).

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

## Testing a command

```python
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["greet", "--name", "Ada"])
assert result.exit_code == 0
```

## Good practices

- Use plain `m.BaseModel` subclasses for command input.
- Read settings via `FlextCliSettings.fetch_global()`; `s` is the service/runtime alias.
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
