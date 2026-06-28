# Development Standards

Quick-reference for daily development in the FLEXT monorepo. For the root engineering law, see `AGENTS.md`. For automated enforcement details, see `.agents/skills/coding-standards/SKILL.md` and child skills.

## Required file header

Every Python file must start with:

```python
from __future__ import annotations
from collections.abc import Mapping, Sequence
```

`ruff` enforces this via `I002`.

## Canonical aliases

Use the facade aliases exposed by `flext_core` and project facades:

| Alias | Purpose |
|-------|---------|
| `c` | constants / constants namespace |
| `m` | models |
| `p` | protocols |
| `t` | typings |
| `u` | utilities |
| `r` | result (`returns`-based) |
| `e` | errors / exceptions |
| `s` | settings |
| `x` | execution / dispatch |

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

def normalize(data: Mapping[str, t.JsonValue]) -> t.JsonValue:
    ...
```

## Result flow

Fallible paths return `r[T]` from `returns`. Do not use ad-hoc error dicts or raw exceptions for control flow.

```python
from flext_core import r

def parse(value: str) -> r[int]:
    ...
```

## Logging

Use `FlextLogger`. No `print()` in library code.

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

## Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| `from typing import Any` | use a concrete type or `t.JsonValue` |
| `isinstance(x, dict)` | `isinstance(x, Mapping)` |
| `default_factory=dict` | explicit factory or Pydantic model |
| `sys.exit()` in library code | raise an exception |
| `breakpoint()` / `import pdb` | remove before committing |
| `TODO/FIXME/HACK` comments | resolve or create a bead |
| `# type: ignore` / `# noqa` | fix root cause |
| relative imports | absolute imports |
| wildcard imports | explicit imports |

## Local validation

```bash
ruff check <file>
ruff format <file>
pyrefly check <file>
make test PROJECT=<proj> MATCH=<expr>
```

For several files:

```bash
make check CHANGED_ONLY=1
```

## Related

- `AGENTS.md` — root engineering law
- `.agents/skills/coding-standards/SKILL.md` — quick-reference skill
- `.agents/skills/flext-import-rules/SKILL.md` — import rules
- `.agents/skills/flext-strict-typing/SKILL.md` — typing rules
- `.agents/skills/flext-patterns/SKILL.md` — code patterns
- `.agents/skills/flext-quality-gates/SKILL.md` — gate commands
- `.agents/skills/flext-development-workflow/SKILL.md` — workflow
