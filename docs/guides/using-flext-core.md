# Using flext-core

`flext_core` is the base package for result flow, settings, container wiring, and dispatcher-driven orchestration.

## Aliases

Import canonical aliases from the package root:

```python
from flext_core import c, d, e, h, m, p, r, s, t, u, x
```

| Alias | Purpose |
|-------|---------|
| `c` | constants |
| `d` | decorators |
| `e` | errors / exceptions |
| `h` | handlers |
| `m` | models / Pydantic helpers |
| `p` | protocols |
| `r` | result (`returns`) |
| `s` | service / runtime |
| `t` | typings |
| `u` | utilities |
| `x` | mixins |

Settings are accessed via `FlextSettings` (no short alias).

## Result flow

Fallible paths return `r[T]`. Avoid raw exceptions or ad-hoc error dicts for control flow.

```python
from __future__ import annotations

from flext_core import p, r


def safe_divide(a: float, b: float) -> p.Result[float]:
    if b == 0:
        return r.fail("division_by_zero")
    return r.ok(a / b)


assert safe_divide(10, 2).success
assert safe_divide(10, 0).failure
```

## Settings

```python
from flext_core import FlextSettings

settings = FlextSettings.fetch_global()
assert isinstance(settings.model_dump(), dict)
```

Subprojects extend `FlextSettings` with their own `env_prefix`:

```python
class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")
```

## Container

```python
from flext_core import FlextContainer

container = FlextContainer()
_ = container.bind("service", "ready")
resolved = container.resolve("service")

assert resolved.success
assert resolved.value == "ready"
```

## Dispatcher

See runnable examples in `examples/ex_04_flext_dispatcher.py`:

```python
from examples.ex_04_flext_dispatcher import Ex04DispatchDsl

result = Ex04DispatchDsl.run()
assert result.success
assert result.value == "pong:dispatcher-example"
```

## Good practices

- Use aliases instead of importing nested modules directly.
- Use `r[T]` for fallible paths.
- Reset singletons in tests with `FlextSettings.reset_for_testing()` and `FlextContainer.reset_for_testing()`.

## Bad practices

```python
from flext_core._models.base import SomeModel  # bypass facade
from flext_core.result import ok, fail        # bypass r alias
```

## Related

- `.agents/skills/using-flext-core/SKILL.md`
- `.agents/skills/coding-standards/SKILL.md`
- `flext-core/src/flext_core/README.md`
