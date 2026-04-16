---
name: lib-returns
description: r railway composition built on dry-python/returns. Use when implementing result-flow operations, error recovery chains, or converting between container types.

---

# Lib Returns — r Railway Composition

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `flext-core/src/flext_core/result.py` — canonical r implementation (813 lines)
- `flext-core/src/flext_core/runtime.py` — RuntimeResult base class that r extends
- `flext-core/tests/unit/test_result_behaviors.py` — behavior test suite demonstrating correct usage
- `flext-core/tests/unit/test_result_coverage_100.py` — exhaustive coverage tests

## References

- `AGENTS.md` — canonical governance source
- <https://returns.readthedocs.io/en/latest/> — dry-python/returns official docs
- `flext-core/pyproject.toml` — pins `returns>=0.26.0`
- `flext-core/src/flext_core/protocols.py` — `p.Result` protocol that r satisfies

## Rules

- **Always** use `r[T].ok(value)` / `r[T].fail(error)` factory methods — never construct `r()` directly.
- **Never** pass `None` to `r[T].ok()` — it raises `ValueError`. Use `r[T].fail()` for absent values.
- Compose with `.map()` for pure transforms and `.flat_map()` for result-returning transforms.
- Use `.lash()` / `.recover()` for failure recovery — never imperative `if result.is_failure:` branching in composition chains.
- Keep `returns` library types (`IOResult`, `Maybe`, `Result`) inside `result.py` only — subprojects must use `r` / `r` exclusively.
## Instructions

### Public API Surface — `r[T_co]`

**Alias**: `r = r` — use `r` throughout application code.

**Import pattern** (all subprojects):

```python
from flext_core import r

_ = r[str].ok("example")
```

### Factory Methods

| Method                 | Signature                                                                                                                    | Purpose                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `r[T].ok(value)`       | `ok[T](cls, value: T) -> p.Result[T]`                                                                                     | Wrap success value (raises `ValueError` if `None`)      |
| `r[U].fail(error)`        | `fail[U](cls, error: str \| None, error_code: str \| None = None, error_data: m.Core.Tests.ResultErrorDataModel \| None = None) -> p.Result[U]` | Create failure with message, optional code and metadata |
| `r.safe`     | `safe[T](func: p.VariadicCallable[T]) -> p.VariadicCallable[r[T]]`                                                 | Decorator — catches exceptions, returns `.fail()`       |
| `create_from_callable` | `create_from_callable(cls, func: Callable[[], T_co], error_code: str \| None = None) -> p.Result[T_co]`                   | Execute callable, wrap result or exception              |

### Monadic Composition Chain

| Method            | Signature                                                                       | When to use                                  |
| ----------------- | ------------------------------------------------------------------------------- | -------------------------------------------- |
| `.map(func)`      | `map[U](self, func: Callable[[T_co], U]) -> p.Result[U]`                     | Transform success value with a pure function |
| `.flat_map(func)` | `flat_map[U](self, func: Callable[[T_co], RuntimeResult[U]]) -> p.Result[U]` | Chain operations returning `r`     |
| `.and_then(func)` | alias for `.flat_map()`                                                         | RFC-compliant name                           |
| `.filter(pred)`   | `filter(self, predicate: Callable[[T_co], bool]) -> p.Result[T_co]`          | Keep value if predicate passes, else fail    |

### Failure Recovery

| Method                            | Signature                                                                     | When to use                                    |
| --------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------- |
| `.recover(func)`                  | `recover(self, func: Callable[[str], T_co]) -> p.Result[T_co]`             | Replace failure with computed fallback value   |
| `.lash(func)`                     | `lash(self, func: Callable[[str], RuntimeResult[T_co]]) -> p.Result[T_co]` | Recover from failure by returning a new result |
| `.or_else(func)`                  | alias for `.lash()`                                                           | RFC-standard name                              |
| `.alt(func)` / `.map_error(func)` | `alt(self, func: Callable[[str], str]) -> p.Result[T_co]`                  | Transform error message without recovering     |

### Side Effects

| Method             | Signature                                                      | When to use                                  |
| ------------------ | -------------------------------------------------------------- | -------------------------------------------- |
| `.tap(func)`       | `tap(self, func: Callable[[T_co], None]) -> p.Result[T_co]` | Logging/metrics on success, result unchanged |
| `.tap_error(func)` | `tap_error(self, func: Callable[[str], None]) -> Self`         | Logging/metrics on failure, result unchanged |

### Value Extraction

| Method                          | Signature                                                                             | When to use                             |
| ------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------- |
| `.unwrap_or(default)`           | `unwrap_or(self, default: T_co) -> T_co`                                              | Get value or default                    |
| `.get_or_else(default)`         | alias for `.unwrap_or()`                                                              | Haskell/Scala naming                    |
| `.map_or(default, func)`        | `map_or[U](self, default: U, func: Callable[[T_co], U] \| None = None) -> U \| T_co`  | Transform + default in one call         |
| `.fold(on_failure, on_success)` | `fold[U](self, on_failure: Callable[[str], U], on_success: Callable[[T_co], U]) -> U` | Catamorphism — collapse to single value |

### Collection Operations

| Method                                    | Signature                                                                                                     | When to use                                |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `r.traverse(items, func)`       | `traverse[T, U](cls, items: Sequence[T], func: ..., *, fail_fast: bool = True) -> p.Result[Sequence[U]]`       | Map over sequence, fail-fast or accumulate |
| `r.accumulate_errors(*results)` | `accumulate_errors(cls, *results: p.Result[U]) -> p.Result[Sequence[U]]`                                    | Collect all successes, combine all errors  |
| `r.parallel_map(items, func)`   | `parallel_map[T, U2](cls, items: Sequence[T], func: ..., *, fail_fast: bool = True) -> p.Result[Sequence[U2]]` | Same semantics as traverse                 |

### Pydantic Integration

| Method                          | Signature                                                                                      | When to use                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------- |
| `.from_validation(data, model)` | `from_validation(cls, data, model: type[T_Model]) -> p.Result[T_Model]` | Validate data against Pydantic model    |
| `.to_model(model)`              | `to_model[U: BaseModel](self, model: type[U]) -> p.Result[U]`                               | Convert success value to Pydantic model |

### Resource Management

```python
from flext_core import r

_ = r[str].ok("resource result")  # r.with_resource wraps lifecycle
```

### Type Guards

```python
from flext_core import p, r

result: p.Result[str] = r[str].ok("hello")
if result.success:
    _ = result.value  # narrowed: value is guaranteed non-None
```

## Workflow

1. Import `r` from `flext_core`
2. Create results via `r[T].ok(value)` or `r[T].fail("error")`
3. Compose with `.map()` → `.flat_map()` → `.lash()` chains
4. Extract at boundaries with `.fold()`, `.unwrap_or()`, or `.map_or()`
5. For batch operations use `r.traverse()` or `.accumulate_errors()`
6. Validate Pydantic input with `r.from_validation(data, Model)`

## Examples

### Good: Railway composition chain

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, r, t


class UserModel(m.ArbitraryTypesModel):
    """User domain model for railway example."""

    user_id: Annotated[t.NonEmptyStr, m.Field(description="User ID")]
    name: Annotated[t.NonEmptyStr, m.Field(description="User name")]


def fetch_user(user_id: str) -> r[UserModel]:
    """Fetch user by ID — returns r."""
    return r[UserModel].ok(UserModel(user_id=user_id, name="Alice"))


def process_user(user_id: str) -> r[str]:
    """Railway composition: fetch → map → tap."""
    return fetch_user(user_id).map(lambda user: user.name.upper()).tap(lambda _: None)
```

### Good: Safe decorator for exception boundaries

```python
from __future__ import annotations

import json

from flext_core import r


@r.safe
def parse_config(raw: str) -> str:
    """Exception → r.fail() automatically."""
    return json.loads(raw)
```

### Good: Fold to HTTP response

```python
from __future__ import annotations

from flext_core import r

result: r[str] = r[str].ok("data")
response = result.fold(
    on_failure=lambda err: f"error: {err}",
    on_success=lambda data: f"ok: {data}",
)
```

### Bad: Imperative branching instead of composition

```python
from __future__ import annotations

from flext_core import p, r


def bad_imperative(user_id: str) -> str:
    """Anti-pattern: imperative branching instead of .flat_map()."""
    result: p.Result[str] = r[str].ok(user_id)
    if not result.success:
        return f"error: {result.error}"
    return f"data: {result.value}"
```

**Why bad**: Duplicated error handling at every step. Use `.flat_map()` chain instead.

### Bad: Bare try/except bypassing r

```python
from __future__ import annotations


def bad_try_except(user_id: str) -> str:
    """Anti-pattern: exceptions bypass result flow."""
    try:
        return f"data: {user_id}"
    except Exception as exc:
        return f"error: {exc}"
```

**Why bad**: Loses error_code/error_data metadata, breaks composition. Use `@r.safe` or explicit `r[T].fail()`.

### Bad: Constructing r directly

```python
from __future__ import annotations

from flext_core import r

# WRONG — internal constructor, not guaranteed stable
# result = r(Success(value))
# Always use factory methods:
result = r[str].ok("value")
```

**Why bad**: Constructor has complex dual-mode logic (legacy vs new). Always use `r[T].ok()` / `r[T].fail()`.

## Subproject Usage Map

| Subproject       | Files                                                              | Pattern                                                  |
| ---------------- | ------------------------------------------------------------------ | -------------------------------------------------------- |
| `flext-auth`     | `provider_service.py`, `token_service.py`, `registry.py`, `api.py` | `from flext_core import r` — service results, auth flows |
| `flext-grpc`     | `api.py`                                                           | r for gRPC operation results                   |
| `flext-dbt-ldif` | `dbt_client.py`, `models.py`, `settings.py`                        | Business rule validation, DBT workflow results           |
| `flext-tap-ldif` | `utilities.py`                                                     | `from flext_core import r, p, t`                  |
| `flext-meltano`  | `dbt/service.py`                                                   | `from flext_core import r, p, s`                 |
| `flext-cli`      | service modules                                                    | CLI operation results                                    |

## Verification

Make gates:

```bash
make check PROJECT=flext-core                  # lint + type gates for result.py
make check PROJECT=flext-core CHECK_GATES=type # type-check r composition
make test PROJECT=flext-core                   # railway composition tests
make validate PROJECT=flext-core               # complexity gates
```

Pattern checks:

```bash
# Confirm r declarations
rg -n "def ok|def fail|def map|def flat_map|def lash|def recover|def traverse|def fold|def tap" flext-core/src/flext_core/result.py

# Confirm r alias export
rg -n "^r = r" flext-core/src/flext_core/result.py

# Confirm subproject usage
rg -n "from flext_core import.*r|from flext_core import.*\br\b" --glob "**/*.py" flext-auth flext-grpc flext-meltano

# Verify no direct constructor usage (anti-pattern)
rg -n "r\(Success\|r\(Failure" --glob "**/*.py" flext-auth/src/ flext-grpc/src/

# Confirm returns library pinned
rg "returns>=" flext-core/pyproject.toml
```
