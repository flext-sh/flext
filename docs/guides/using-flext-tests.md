# Using flext-tests

`flext_tests` is the shared test toolkit. It provides fixtures, matchers, file helpers, and a test runtime that binds the canonical aliases.

## Aliases

```python
from flext_tests import c, e, m, p, r, s, t, u
```

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `e` | errors / exceptions (reexported) |
| `m` | models |
| `p` | protocols |
| `r` | result (reexported) |
| `s` | service / test runtime |
| `t` | typings |
| `u` | utilities |

Settings are accessed via `FlextTestsSettings` or project-specific settings classes (no short alias).

## Essential fixtures

Add `flext_tests` to your project test dependencies and use these fixtures in `conftest.py` or directly in tests:

| Fixture | Purpose |
|---------|---------|
| `reset_settings` | Resets `FlextSettings`, `FlextTestsSettings`, and `FlextContainer` singletons between tests (autouse). |
| `test_runtime` | Binds aliases (`c`, `e`, `m`, `p`, `r`, `s`, `t`, `u`) and `service`/`settings`/`logger` on class instances (autouse). |
| `settings` | Clean `FlextTestsSettings(debug=True, trace=False)`. |
| `settings_factory` | Factory for creating project-specific settings instances. |
| `temp_dir` / `temp_file` | Temporary paths isolated per test. |

```python
from __future__ import annotations

from flext_core import FlextSettings, FlextTestsSettings


def test_settings_isolation(settings: FlextTestsSettings) -> None:
    settings.debug = True
    # Next test receives a fresh singleton via reset_settings
    assert FlextSettings.fetch_global() is not settings
```

## Resetting singletons manually

When a fixture is not enough:

```python
FlextSettings.reset_for_testing()
FlextTestsSettings.reset_for_testing()
FlextContainer.reset_for_testing()
```

## Testing result flows

```python
from returns.result import Success

from flext_core import r


def test_safe_divide() -> None:
    result = safe_divide(10, 2)
    assert isinstance(result, Success)
    assert result.unwrap() == 5.0
```

## Good practices

- Rely on `reset_settings` and `test_runtime` for isolation.
- Assert public API behavior, not private internals.
- Use `settings_factory` when a project-specific settings subclass is required.

## Bad practices

```python
# Mutating global singleton without resetting
FlextSettings.fetch_global().debug = True
```

## Related

- `.agents/skills/using-flext-tests/SKILL.md`
- `.agents/skills/coding-standards/SKILL.md`
- `flext-tests/src/flext_tests/_fixtures/settings.py`
