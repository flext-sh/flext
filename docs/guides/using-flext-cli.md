# Using flext-cli

`flext_cli` provides a unified Typer abstraction for model-driven CLI applications.

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

**Important:** `s` is the service/runtime alias. `config` and `settings` are
validated package-root singleton exports, not short aliases.

## Purpose

- Define CLI commands as Pydantic models.
- Let `FlextCliCli` convert model fields into Typer options.
- Keep output formatting, prompts, and runtime consistent across FLEXT CLI tools.

## Settings

Import the existing validated singletons from the package root; do not
redefine, instantiate, or privately import their classes:

```python
from flext_cli import config, settings
```

## Model-driven command

```python
from __future__ import annotations

from flext_cli import m, t
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

**Common mistakes to avoid:**

- `FlextCliCli.build_model_command(...)` does not exist; use `FlextCliCli.model_command(...)`.
- `m.CliInput` / `m.CliOutput` do not exist; use plain `m.BaseModel` subclasses.

## Testing a command

```python
from typer.testing import CliRunner

runner = CliRunner()
result = runner.invoke(app, ["greet", "--name", "Ada"])
assert result.exit_code == 0
```

## Good practices

- Use plain `m.BaseModel` subclasses for command input.
- Read configuration only through package-root `config` and `settings`; `s` is
  the service/runtime alias.
- Avoid ad-hoc Typer functions and direct `print()`/`sys.exit()` in commands.

## Bad practices

```python
import typer


def main(name: str):  # ad-hoc command, no model
    print(f"Hello, {name}")
```

## Related

- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`
- `.agents/skills/using-flext-cli/SKILL.md`
- `.agents/skills/coding-standards/SKILL.md`
- `flext-cli/src/flext_cli/services/cli.py`
