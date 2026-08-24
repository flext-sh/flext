---
name: using-flext-core
description: 'Use when working with flext-core: canonical aliases, result flow, settings, container, logging, and service runtime. Provides quick examples and good/bad practices for the base package. DO NOT USE FOR: questions unrelated to flext-core or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.1.0
---

# Using flext-core

**UTILITY SKILL**

Quick-reference for using `flext_core` in FLEXT projects.

## USE FOR

- Using `flext_core` aliases, result flow, settings, container, logging, or service runtime.
- Choosing the canonical pattern for base concerns.

## DO NOT USE FOR

- Questions unrelated to `flext_core`.
- Creating projects or architecture from scratch.

## Workflow

1. Identify the concern (result, settings, container, logging, service).
2. Use the canonical alias and example below.
3. Validate with `ruff check <file>` and `pyrefly check <file>`.

## Critical rules

- Import via root aliases: `from flext_core import c, d, e, h, m, p, r, s, t, u, x`.
- `s` is the **service/runtime** alias (`FlextService`), never settings.
- Settings classes (`FlextSettings`, `FlextCliSettings`, `FlextTestsSettings`) have no short alias.
- **ADR-005:** `flext-core` is runtime-minimal for config — stdlib `tomllib` + `string.Template` + `u.config_*` only, **no Jinja2**, and it must **never import `flext-cli`/`flext-infra` at runtime**. Template/schema/multi-format loaders live in `flext-cli`. See `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Use `r[T]` for fallible paths; never raw exceptions or ad-hoc error dicts for control flow.
- Reset singletons in tests with `FlextSettings.reset_for_testing()` and `FlextContainer.reset_for_testing()`.

## Aliases

| Alias | Purpose |
|-------|---------|
| `c` | constants / constants namespace |
| `d` | decorators |
| `e` | errors / exceptions |
| `h` | handlers |
| `m` | models / Pydantic helpers |
| `p` | protocols |
| `r` | result (`FlextResult`) |
| `s` | service / runtime (`FlextService`) |
| `t` | typings |
| `u` | utilities |
| `x` | mixins / execution |

## Result flow

Fallible paths return `r[T]`. Prefer `r.ok(...)` when the type is inferred; use `r[float].ok(...)` only when disambiguation is needed.

```python
from __future__ import annotations

from flext_core import r


def safe_divide(a: float, b: float) -> r[float]:
    if b == 0:
        return r[float].fail("division_by_zero")
    return r.ok(a / b)


result = safe_divide(10, 2)
assert result.success
assert result.value == 5.0

failure = safe_divide(10, 0)
assert failure.failure
assert failure.error == "division_by_zero"
```

## Settings

```python
from flext_core import FlextSettings

assert isinstance(settings.model_dump(), dict)
```

Subprojects extend `FlextSettings` with their own `env_prefix`:

```python
from __future__ import annotations

from flext_core import FlextSettings
from flext_core import m


class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")
```

## Container

`FlextContainer` resolves services as results:

```python
from flext_core import FlextContainer, p

container = FlextContainer()
container.bind("service", "ready")
resolved: p.Result[str] = container.resolve("service", type_cls=str)
assert resolved.success
assert resolved.value == "ready"
```

## Logging

```python
from flext_core import u

logger = u.fetch_logger(__name__)
logger.info("user.created", user_id=42)
```

## Service runtime

```python
from flext_core import s, FlextSettings

runtime = s(runtime_settings=settings)
```

## Good

```python
from flext_core import c, m, r, p, t, u
```

## Bad

```python notest
# Illustrative anti-patterns — these imports bypass the canonical facade.
from flext_core._models.base import SomeModel  # bypass facade
from flext_core import ok, fail  # bypass r alias
from flext_core import s as settings  # s is service/runtime, not settings
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
