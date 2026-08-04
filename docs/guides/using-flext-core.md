# Using flext-core

`flext_core` is the base package for result flow, settings, container wiring, logging, and service runtime.

## Aliases

Import canonical aliases from the package root:

```python
from flext_core import c, d, e, h, m, p, r, s, t, u, x
```

| Alias | Purpose |
| ------- | --------- |
| `c` | constants / constants namespace |
| `d` | decorators |
| `e` | errors / exceptions |
| `h` | handlers |
| `m` | models / Pydantic helpers |
| `p` | protocols |
| `r` | result factory (`FlextResult`); annotate returns as `p.Result[T]` |
| `s` | service / runtime (`FlextService`) |
| `t` | typings |
| `u` | utilities |
| `x` | mixins / execution |

**Important:** `s` is the service/runtime alias. Settings classes (`FlextSettings`, `FlextCliSettings`,
`FlextTestsSettings`) have no short alias.

## Result flow

Fallible paths return `r[T]`. Avoid raw exceptions or ad-hoc error dicts for control flow.

```python
from __future__ import annotations

from flext_core import p, r


def safe_divide(a: float, b: float) -> p.Result[float]:
    if b == 0:
        return r[float].fail("division_by_zero")
    return r[float].ok(a / b)


assert safe_divide(10, 2).success
assert safe_divide(10, 2).value == 5.0
assert safe_divide(10, 0).failure
```


## Result DIP (`p.Result` + `r`)

- Annotate fallible returns as `p.Result[T]` (protocol).
- Construct with the `r` / `FlextResult` facade: `r[T].ok`, `r[T].fail`, `fail_op`, `from_validation`, `create_from_callable`.
- Convert between result-like values with `r.from_result` / `r[T].from_failure` / `r.copy_from_result`.
- Empty failures (`fail(None)` / `fail("")`) remain failed railway values; exception-derived `error_data` redacts
  `c.SENSITIVE_ERROR_DATA_KEYS`.
- Do not import `FlextResult` lazily inside `_result/` factories, and do not use the retired `returns` mypy plugin.

## Settings

```python
from flext_core import FlextSettings

settings = FlextSettings.fetch_global()
assert isinstance(settings.model_dump(), dict)
```

Subprojects extend `FlextSettings` with their own `env_prefix`:

```python
from flext_core import FlextSettings, m


class FlextCliSettings(FlextSettings):
    model_config = m.SettingsConfigDict(env_prefix="FLEXT_CLI_", extra="ignore")
```

## Container

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

settings = FlextSettings.fetch_global()
runtime = s(settings=settings)
```

## Good practices

- Use aliases instead of importing nested modules directly.
- Use `r[T]` for fallible paths.
- Reset singletons in tests with `FlextSettings.reset_for_testing()` and `FlextContainer.reset_for_testing()`.
- Remember: `s` = service/runtime, never settings.

## Bad practices

```python notest
from flext_core._models.base import SomeModel  # bypass facade
from flext_core.result import ok, fail  # bypass r alias
from flext_core import s as settings  # wrong: s is service/runtime
```

## Related

- `.agents/skills/flext-law/SKILL.md`
- `${config.AiHub.paths.agents_home}/skills/make-check/SKILL.md`
- `${config.AiHub.paths.agents_home}/skills/inviolable-rules/SKILL.md`
- `flext-core/src/flext_core/README.md`
