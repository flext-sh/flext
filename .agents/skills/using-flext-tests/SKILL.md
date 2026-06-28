---
name: using-flext-tests
description: 'Use when writing FLEXT tests. Covers fixtures, singleton reset, test runtime
  aliases, and asserting result flows. DO NOT USE FOR: questions unrelated to flext-tests
  or creating projects/architecture from scratch.'
license: MIT
metadata:
  version: 1.0.0
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

1. Import test aliases and fixtures.
2. Write the test with public API assertions.
3. Validate with `make test PROJECT=<proj> MATCH=<expr>`.

## Critical rules

- Rely on `reset_settings` and `test_runtime` autouse fixtures.
- Assert public behavior, not private internals.
- Reset singletons manually only when fixtures are not enough.

## Aliases

```python
from flext_tests import c, e, m, p, r, s, t, u
```

## Essential fixtures

| Fixture | Purpose |
|---------|---------|
| `reset_settings` | Resets `FlextSettings`, `FlextTestsSettings`, and `FlextContainer` between tests. |
| `test_runtime` | Binds aliases and `service`/`settings`/`logger` on class instances. |
| `settings` | Clean `FlextTestsSettings(debug=True, trace=False)`. |
| `settings_factory` | Creates project-specific settings instances. |

```python
from __future__ import annotations
from flext_core import FlextSettings, FlextTestsSettings

def test_settings_isolation(settings: FlextTestsSettings) -> None:
    settings.debug = True
    assert FlextSettings.fetch_global() is not settings
```

## Asserting results

```python
from returns.result import Success

def test_safe_divide() -> None:
    result = safe_divide(10, 2)
    assert isinstance(result, Success)
    assert result.unwrap() == 5.0
```

## Manual singleton reset

```python
from flext_core import FlextContainer, FlextSettings
from flext_tests.settings import FlextTestsSettings

FlextSettings.reset_for_testing()
FlextTestsSettings.reset_for_testing()
FlextContainer.reset_for_testing()
```

## Good

```python
def test_create_user(settings_factory) -> None:
    settings = settings_factory(FlextApiSettings, base_url="http://test")
    assert settings.base_url == "http://test"
```

## Bad

```python
# Mutating global singleton without resetting
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
