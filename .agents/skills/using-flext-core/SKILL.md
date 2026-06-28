---
name: using-flext-core
description: 'Use when working with flext-core: result flow, settings, container, dispatcher,
  and canonical aliases. Provides quick examples and good/bad practices for the base
  package. DO NOT USE FOR: questions unrelated to flext-core or creating projects/architecture
  from scratch.'
license: MIT
metadata:
  version: 1.0.0
---
# Using flext-core

**UTILITY SKILL**

Quick-reference for using `flext_core` in FLEXT projects.

## USE FOR

- Using `flext_core` aliases, result flow, settings, container, or dispatcher.
- Choosing the canonical pattern for base concerns.

## DO NOT USE FOR

- Questions unrelated to `flext_core`.
- Creating projects or architecture from scratch.

## Workflow

1. Identify the concern (result, settings, container, dispatcher).
2. Use the canonical alias and example below.
3. Validate with `ruff check <file>` and `pyrefly check <file>`.

## Critical rules

- Import via root aliases: `from flext_core import c, m, p, r, t, u`.
- Use `r[T]` for fallible paths.
- Reset singletons in tests with `FlextSettings.reset_for_testing()`.

## Aliases

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `m` | models / Pydantic helpers |
| `p` | protocols |
| `r` | result (`returns`) |
| `t` | typings |
| `u` | utilities |

## Result flow

```python
from __future__ import annotations
from flext_core import p, r

def safe_divide(a: float, b: float) -> p.Result[float]:
    if b == 0:
        return r[float].fail("division_by_zero")
    return r[float].ok(a / b)
```

## Settings

```python
from flext_core import FlextSettings

settings = FlextSettings.fetch_global()
```

## Container

```python
from flext_core import FlextContainer

container = FlextContainer()
container.bind("service", "ready")
resolved = container.resolve("service")
```

## Good

```python
from flext_core import c, m, r, t, u
```

## Bad

```python
from flext_core._models.base import SomeModel  # bypass facade
```

## Validation

```bash
ruff check <file>
pyrefly check <file>
```

## References

- `docs/guides/using-flext-core.md`
- `.agents/skills/coding-standards/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
