# Development Standards

Quick-reference for daily development in the FLEXT monorepo. For the root
engineering law, see `AGENTS.md`. For automated enforcement details, see
`.agents/skills/coding-standards/SKILL.md` and child skills.

## Required file header

Every Python file must start with:

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
```

`ruff` enforces this via `I002`.

## Config and settings are the SSOT (P0)

All configuration and runtime settings come from `from <ns> import config, settings`
and are consumed through `config.<Ns>.*` and `settings.<Ns>.*`. No code, test, or
script may embed a value that the SSOT owns.

- Tests must be able to validate any change to config or settings without being
  rewritten. Expectations come from the config/settings objects, not from
  hardcoded literals copied from today's files.
- A test that fails only because a config value changed is a test defect; fix
  the test to read from the SSOT.
- This rule applies to every tier: unit, integration, and e2e tests, plus
  markdown examples and docstring snippets validated by the pytest plugin.

See `docs/standards/testing.md` for the test-side enforcement of this rule.

## Canonical aliases

Use the facade aliases exposed by `flext_core` and project facades:

|Alias|Purpose|
|-------|---------|
|`c`|constants / constants namespace|
|`d`|decorators|
|`e`|errors / exceptions|
|`h`|handlers|
|`m`|models|
|`p`|protocols|
|`r`|result (`FlextResult`)|
|`s`|service / runtime|
|`t`|typings|
|`u`|utilities|
|`x`|mixins / execution|

**Important:** `s` is the service/runtime alias. Settings classes (`FlextSettings`,
`FlextCliSettings`, `FlextTestsSettings`) have no short alias.

Facade owner modules that compose an upstream FLEXT facade by MRO use the
upstream short alias as the base class and then publish the local alias at the
bottom:

```python
from flext_cli import m, u
from flext_plugin import c, p, r, t


class FlextPluginModels(m): ...


m = FlextPluginModels
```

This applies to `c`, `t`, `p`, `m`, and `u` facades. Pylance's
`reportGeneralTypeIssues` workspace diagnostic is disabled because it flags this
canonical self-rebound facade pattern; `pyright`, `pyrefly`, and `mypy` gates
remain authoritative.

`base.py` and `api.py` follow the same owner-facade rule:

```python
from flext_core import s
from flext_db_oracle._utilities.db_oracle import FlextDbOracleUtilitiesDbOracle


class FlextDbOracleServiceBase(s, FlextDbOracleUtilitiesDbOracle): ...


s = FlextDbOracleServiceBase
```

```python
from flext_db_oracle.services.api_runtime import FlextDbOracleApiRuntime


class FlextDbOracleApi(FlextDbOracleApiRuntime): ...


db_oracle = FlextDbOracleApi
```

Example:

```python
from flext_core import c, m, r, t, u


def load(user_id: int) -> r[m.User]:
    return u.http_get(f"{c.API_BASE}/users/{user_id}")
```

## Imports

- Absolute imports only in `src/`.
- No wildcard imports.
- No relative imports.
- No legacy typing imports (`typing.Dict`, `typing.List`, etc.).
- No direct imports of abstracted frameworks (pydantic, structlog, typer, returns)
  in consumer projects; use the project facade.

Order:

1. `from __future__ import annotations`
2. `from collections.abc import Mapping, Sequence`
3. stdlib
4. third-party
5. first-party (`flext_core`, `flext_*`)
6. local package

## Typing

- Use `Mapping` / `MutableMapping` for contracts instead of `dict`.
- Use `t.JsonValue` for unknown JSON instead of `Any`.
- Use Pydantic v2 `BaseModel` for schema-bearing payloads.
- Avoid `typing.Any`, bare `object`, and `# type: ignore`.

```python
from collections.abc import Mapping
from flext_core import t


def normalize(data: Mapping[str, t.JsonValue]) -> t.JsonValue: ...
```

## Result flow

Fallible paths return `r[T]` (`FlextResult`) annotated as `p.Result[T]`. Construct with `r[T].ok` / `r[T].fail`; convert with `from_result` / `from_failure`. Do not use ad-hoc error dicts or raw exceptions for control flow.

```python
from flext_core import r


def parse(value: str) -> r[int]:
    try:
        return r.ok(int(value))
    except ValueError as exc:
        return r[int].fail("invalid_integer", exception=exc)
```

## Logging

Use `u.fetch_logger(__name__)`. No `u.Cli.print()` in library code.

```python
from flext_core import u

logger = u.fetch_logger(__name__)
logger.info("event.name", key=value)
```

## Error handling

Catch specific exceptions. No bare `except:`. No empty `except/pass` blocks.

```python
try:
    value = int(raw)
except ValueError as exc:
    raise e.ValidationError("invalid integer") from exc
```

## Models and settings

Use Pydantic v2 `BaseModel` and `m.SettingsConfigDict` for settings branches.

```python
from flext_core import FlextSettings, m


class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")
```

## Anti-patterns

|Anti-pattern|Fix|
|--------------|-----|
|`from typing import Any`|use a concrete type or `t.JsonValue`|
|`isinstance(x, dict)`|`isinstance(x, Mapping)`|
|`default_factory=dict`|explicit factory or Pydantic model|
|`sys.exit()` in library code|raise an exception|
|`breakpoint()` / `import pdb`|remove before committing|
|`TODO/FIXME/HACK` comments|resolve or create a bead|
|`# type: ignore` / `# noqa`|fix root cause|
|relative imports|absolute imports|
|wildcard imports|explicit imports|
|`s` used for settings|`s` is service/runtime; use `FlextSettings` by name|

## Local validation

```bash
make check PROJECT=<proj> CHECK_GATES=lint,format,pyrefly
make check PROJECT=<proj> CHECK_GATES=pyright,mypy
make test PROJECT=<proj> MATCH=<expr>
```

Scope with `PROJECT=` / `CHECK_GATES=` / `FILE=` / `MATCH=` — never bare ruff/pyrefly/mypy.

## Related

- `AGENTS.md` — root engineering law
- `.agents/skills/flext-law/SKILL.md` — FLEXT domain law
- `~/.agents/skills/inviolable-rules/SKILL.md` — gate commands
- `~/.agents/skills/make-check/SKILL.md` — canonical Make verbs
- `AGENTS.md` Learned Workspace Facts — CI policy and `make gen APPLY=Y` workflow regeneration
