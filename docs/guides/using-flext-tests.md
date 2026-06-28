# Using flext-tests

`flext_tests` is the shared test toolkit. It provides fixtures, matchers, file helpers, and a test runtime that binds the canonical aliases.

## Aliases

```python
from flext_tests import c, e, m, p, r, s, t, u
```

`flext_tests` reexports `d`, `e`, `h`, `r`, `x` from `flext_infra` and exposes domain helpers (`tk`, `td`, `tf`, `tv`, `tm`).

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

**Important:** `s` is the service/test-runtime alias. Test settings are accessed via `FlextTestsSettings` (no short alias).

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

from flext_core import FlextSettings
from flext_tests import FlextTestsSettings


def test_settings_isolation(settings: FlextTestsSettings) -> None:
    settings.debug = True
    # Next test receives a fresh singleton via reset_settings
    assert FlextSettings.fetch_global() is not settings
```

## Resetting singletons manually

When a fixture is not enough:

```python
from flext_core import FlextContainer, FlextSettings
from flext_tests import FlextTestsSettings

FlextSettings.reset_for_testing()
FlextTestsSettings.reset_for_testing()
FlextContainer.reset_for_testing()
```

## Testing result flows

Use the `r` alias instead of importing from `returns` directly:

```python
from flext_core import r


def test_safe_divide() -> None:
    result = safe_divide(10, 2)
    assert result.success
    assert result.unwrap() == 5.0

    failure = safe_divide(10, 0)
    assert failure.failure
```

## Good practices

- Rely on `reset_settings` and `test_runtime` for isolation.
- Assert public API behavior, not private internals.
- Use `settings_factory` when a project-specific settings subclass is required.
- Assert result state via `.success`, `.failure`, and `.unwrap()` on `r[T]` instances.

## Generic Make Framework

`flext_tests` is also the shared library for registry-driven Make surfaces. A
workspace can promote commands by placing scripts under
`scripts/cmd/<verb>/<what>.py` with a `# /// flext-command` TOML header.

Use the public facades:

- `c.Tests.MAKE_*` for header names, environment keys, suffixes, and validation constants.
- `t.Tests.MakeTomlTable` / `t.Tests.MakeTomlValue` for parsed header payloads.
- `m.Tests.MakeCommand`, `m.Tests.MakeParam`, and `m.Tests.MakeRegistry` for command contracts.
- `u.Tests.make_discover`, `u.Tests.make_validate_invocation`, and `u.Tests.make_render_*` for discovery, validation, and help text.

The root dispatcher is only a CLI adapter. Promoted Python commands should
consume `scripts.dispatch.Dispatch`; they should not redefine command models,
parse TOML independently, or discover projects outside declared workspace
membership.

Inside `flext-tests`, the Make utility domain is split into parsing, contract,
registry, and rendering mixins. Consumers still call only `u.Tests.make_*`.

## Bad practices

```python
# Mutating global singleton without resetting
FlextSettings.fetch_global().debug = True

# Importing returns directly instead of using the r alias
from returns.result import Success

# Defining a parallel Make registry outside c/m/t/u.Tests
from dataclasses import dataclass
```

## Related

- `.agents/skills/using-flext-tests/SKILL.md`
- `.agents/skills/coding-standards/SKILL.md`
- `flext-tests/src/flext_tests/_fixtures/settings.py`
- `docs/architecture/adr/004-generic-make-framework-in-flext-tests.md`
