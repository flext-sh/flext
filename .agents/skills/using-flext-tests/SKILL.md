---
name: using-flext-tests
description: 'Use when writing FLEXT tests. Covers fixtures, singleton reset, test runtime aliases, and asserting result flows. DO NOT USE FOR: questions unrelated to flext-tests or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.1.0
---

# Using flext-tests

**UTILITY SKILL**

Quick-reference for using the `flext_tests` toolkit.

## USE FOR

- Writing tests for FLEXT projects.
- Using shared fixtures, matchers, or file helpers.
- Resetting singletons between tests.

## DO NOT USE FOR

- Questions unrelated to `flext_tests`.
- Creating projects or architecture from scratch.

## Workflow

1. Import test aliases and fixtures from `flext_tests`.
2. Write the test with public API assertions.
3. Validate with `make test PROJECT=<proj> MATCH=<expr>`.

## Critical rules

- Rely on `reset_settings` and `test_runtime` autouse fixtures.
- Assert public behavior, not private internals.
- Assert result state via `.success`, `.failure`, and `.unwrap()` on `r[T]` instances.
- Reset singletons manually only when fixtures are not enough.

## Aliases

```python
from flext_tests import c, e, m, p, r, s, t, u
```

`flext_tests` reexports `d`, `e`, `h`, `r`, `x` from `flext_infra` and exposes `tk`, `td`, `tf`, `tv`, `tm` for domain helpers.

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `e` | errors / exceptions (reexported) |
| `m` | models |
| `p` | protocols |
| `r` | result (reexported) |
| `s` | service / test runtime (`FlextTestsServiceBase`) |
| `t` | typings |
| `u` | utilities |

Settings are accessed via `FlextTestsSettings` or project-specific settings classes (no short alias).

## Essential fixtures

| Fixture | Purpose |
|---------|---------|
| `reset_settings` | Resets `FlextSettings`, `FlextTestsSettings`, and `FlextContainer` singletons between tests (autouse). |
| `test_runtime` | Binds aliases and `service`/`settings`/`logger` on class instances (autouse). |
| `settings` | Clean `FlextTestsSettings(debug=True, trace=False)`. |
| `settings_factory` | Creates project-specific settings instances. |
| `temp_dir` / `temp_file` | Temporary paths isolated per test. |

```python
from __future__ import annotations

from flext_core import FlextSettings
from flext_tests import FlextTestsSettings


def test_settings_isolation(settings: FlextTestsSettings) -> None:
    settings.debug = True
    # Next test receives a fresh singleton via reset_settings
    assert FlextSettings.fetch_global() is not settings
```

## Asserting results

```python
from __future__ import annotations

from flext_core import r


def safe_divide(a: float, b: float) -> r[float]:
    if b == 0:
        return r.from_failure(ValueError("division by zero"))
    return r.from_value(a / b)


def test_safe_divide() -> None:
    result = safe_divide(10, 2)
    assert result.success
    assert result.unwrap() == 5.0

    failure = safe_divide(10, 0)
    assert failure.failure
```

## Manual singleton reset

When a fixture is not enough:

```python
from __future__ import annotations

from flext_core import FlextContainer, FlextSettings
from flext_tests import FlextTestsSettings

FlextSettings.reset_for_testing()
FlextTestsSettings.reset_for_testing()
FlextContainer.reset_for_testing()
```

## Good

```python
from __future__ import annotations

from flext_tests import settings_factory


def test_create_user(settings_factory) -> None:
    from flext_api.settings import FlextApiSettings

    settings = settings_factory(FlextApiSettings, base_url="http://test")
    assert settings.base_url == "http://test"
```

## Bad

```python notest
# Illustrative anti-pattern: mutating global singleton without resetting.
FlextSettings.fetch_global().debug = True
```

## Validation

```bash
make test PROJECT=<proj> MATCH=<expr>
```

## References

- `docs/guides/using-flext-tests.md`
- `.agents/skills/coding-standards/SKILL.md`
- `.agents/skills/flext-quality-gates/SKILL.md`
