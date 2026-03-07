<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [Public API Surface — `FlextResult[T_co]`](#public-api-surface-flextresulttco)
  - [Factory Methods](#factory-methods)
  - [Monadic Composition Chain](#monadic-composition-chain)
  - [Failure Recovery](#failure-recovery)
  - [Side Effects](#side-effects)
  - [Value Extraction](#value-extraction)
  - [Collection Operations](#collection-operations)
  - [Pydantic Integration](#pydantic-integration)
  - [Returns Library Interop (inside `result.py` only)](#returns-library-interop-inside-resultpy-only)
  - [Resource Management](#resource-management)
  - [Type Guards](#type-guards)
- [Workflow](#workflow)
- [Examples](#examples)
  - [Good: Railway composition chain](#good-railway-composition-chain)
  - [Good: Batch processing with error accumulation](#good-batch-processing-with-error-accumulation)
  - [Good: Safe decorator for exception boundaries](#good-safe-decorator-for-exception-boundaries)
  - [Good: Fold to HTTP response](#good-fold-to-http-response)
  - [Bad: Imperative branching instead of composition](#bad-imperative-branching-instead-of-composition)
  - [Bad: Bare try/except bypassing FlextResult](#bad-bare-tryexcept-bypassing-flextresult)
  - [Bad: Constructing FlextResult directly](#bad-constructing-flextresult-directly)
- [Subproject Usage Map](#subproject-usage-map)
- [Verification](#verification)
<!-- TOC END -->

---

name: lib-returns
description: FlextResult railway composition built on dry-python/returns. Use when implementing result-flow operations, error recovery chains, or converting between container types.

---

# Lib Returns — FlextResult Railway Composition

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `flext-core/src/flext_core/result.py` — canonical FlextResult implementation (813 lines)
- `flext-core/src/flext_core/runtime.py` — RuntimeResult base class that FlextResult extends
- `flext-core/tests/unit/test_result_behaviors.py` — behavior test suite demonstrating correct usage
- `flext-core/tests/unit/test_result_coverage_100.py` — exhaustive coverage tests

## References

- `AGENTS.md` — canonical governance source
- <https://returns.readthedocs.io/en/latest/> — dry-python/returns official docs
- `flext-core/pyproject.toml` — pins `returns>=0.26.0`
- `flext-core/src/flext_core/protocols.py` — `p.ResultLike` protocol that FlextResult satisfies

## Rules

- **Always** use `r[T].ok(value)` / `r[T].fail(error)` factory methods — never construct `FlextResult()` directly.
- **Never** pass `None` to `r[T].ok()` — it raises `ValueError`. Use `r[T].fail()` for absent values.
- Compose with `.map()` for pure transforms and `.flat_map()` for result-returning transforms.
- Use `.lash()` / `.recover()` for failure recovery — never imperative `if result.is_failure:` branching in composition chains.
- Keep `returns` library types (`IOResult`, `Maybe`, `Result`) inside `result.py` only — subprojects must use `FlextResult` / `r` exclusively.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
## Instructions

### Public API Surface — `FlextResult[T_co]`

**Alias**: `r = FlextResult` — use `r` throughout application code.

**Import pattern** (all subprojects):

```python
from flext_core import FlextResult, r
# or via short alias:
from flext_core import r
```

### Factory Methods

| Method                 | Signature                                                                                                                    | Purpose                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `r[T].ok(value)`       | `ok[T](cls, value: T) -> FlextResult[T]`                                                                                     | Wrap success value (raises `ValueError` if `None`)      |
| `r.fail(error)`        | `fail[U](cls, error: str \| None, error_code: str \| None = None, error_data: t.ConfigMap \| None = None) -> FlextResult[U]` | Create failure with message, optional code and metadata |
| `FlextResult.safe`     | `safe[T](func: p.VariadicCallable[T]) -> p.VariadicCallable[FlextResult[T]]`                                                 | Decorator — catches exceptions, returns `.fail()`       |
| `create_from_callable` | `create_from_callable(cls, func: Callable[[], T_co], error_code: str \| None = None) -> FlextResult[T_co]`                   | Execute callable, wrap result or exception              |

### Monadic Composition Chain

| Method            | Signature                                                                       | When to use                                  |
| ----------------- | ------------------------------------------------------------------------------- | -------------------------------------------- |
| `.map(func)`      | `map[U](self, func: Callable[[T_co], U]) -> FlextResult[U]`                     | Transform success value with a pure function |
| `.flat_map(func)` | `flat_map[U](self, func: Callable[[T_co], RuntimeResult[U]]) -> FlextResult[U]` | Chain operations returning `FlextResult`     |
| `.and_then(func)` | alias for `.flat_map()`                                                         | RFC-compliant name                           |
| `.filter(pred)`   | `filter(self, predicate: Callable[[T_co], bool]) -> FlextResult[T_co]`          | Keep value if predicate passes, else fail    |

### Failure Recovery

| Method                            | Signature                                                                     | When to use                                    |
| --------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------- |
| `.recover(func)`                  | `recover(self, func: Callable[[str], T_co]) -> FlextResult[T_co]`             | Replace failure with computed fallback value   |
| `.lash(func)`                     | `lash(self, func: Callable[[str], RuntimeResult[T_co]]) -> FlextResult[T_co]` | Recover from failure by returning a new result |
| `.or_else(func)`                  | alias for `.lash()`                                                           | RFC-standard name                              |
| `.alt(func)` / `.map_error(func)` | `alt(self, func: Callable[[str], str]) -> FlextResult[T_co]`                  | Transform error message without recovering     |

### Side Effects

| Method             | Signature                                                      | When to use                                  |
| ------------------ | -------------------------------------------------------------- | -------------------------------------------- |
| `.tap(func)`       | `tap(self, func: Callable[[T_co], None]) -> FlextResult[T_co]` | Logging/metrics on success, result unchanged |
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
| `FlextResult.traverse(items, func)`       | `traverse[T, U](cls, items: Sequence[T], func: ..., *, fail_fast: bool = True) -> FlextResult[list[U]]`       | Map over sequence, fail-fast or accumulate |
| `FlextResult.accumulate_errors(*results)` | `accumulate_errors(cls, *results: FlextResult[U]) -> FlextResult[list[U]]`                                    | Collect all successes, combine all errors  |
| `FlextResult.parallel_map(items, func)`   | `parallel_map[T, U2](cls, items: Sequence[T], func: ..., *, fail_fast: bool = True) -> FlextResult[list[U2]]` | Same semantics as traverse                 |

### Pydantic Integration

| Method                          | Signature                                                                                      | When to use                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------- |
| `.from_validation(data, model)` | `from_validation(cls, data: t.GeneralValueType, model: type[T_Model]) -> FlextResult[T_Model]` | Validate data against Pydantic model    |
| `.to_model(model)`              | `to_model[U: BaseModel](self, model: type[U]) -> FlextResult[U]`                               | Convert success value to Pydantic model |

### Resource Management

```python
FlextResult.with_resource(
    factory=lambda: open("data.json"),
    op=lambda f: r[str].ok(f.read()),
    cleanup=lambda f: f.close(),
)
```

### Type Guards

```python
from flext_core import is_success_result, is_failure_result

if is_success_result(result):
    # TypeIs narrows: result.value is guaranteed non-None
    process(result.value)
```

## Workflow

1. Import `r` from `flext_core`
2. Create results via `r[T].ok(value)` or `r.fail("error")`
3. Compose with `.map()` → `.flat_map()` → `.lash()` chains
4. Extract at boundaries with `.fold()`, `.unwrap_or()`, or `.map_or()`
5. For batch operations use `FlextResult.traverse()` or `.accumulate_errors()`
6. Validate Pydantic input with `FlextResult.from_validation(data, Model)`

## Examples

### Good: Railway composition chain

```python
from flext_core import r

def process_user(user_id: str) -> r[UserResponse]:
    return (
        r[User].from_validation({"id": user_id}, User)
        .flat_map(lambda user: fetch_permissions(user))
        .map(lambda perms: UserResponse(permissions=perms))
        .tap(lambda resp: logger.info("processed", user_id=user_id))
        .lash(lambda err: r[UserResponse].fail(f"User processing failed: {err}"))
    )
```

### Good: Batch processing with error accumulation

```python
results = FlextResult.traverse(
    items=user_ids,
    func=lambda uid: r[User].from_validation({"id": uid}, User),
    fail_fast=False,  # collect ALL errors
)
```

### Good: Safe decorator for exception boundaries

```python
@FlextResult.safe
def parse_config(raw: str) -> dict:
    return json.loads(raw)  # exception → r.fail() automatically
```

### Good: Fold to HTTP response

```python
response = result.fold(
    on_failure=lambda err: {"status": 400, "error": err},
    on_success=lambda data: {"status": 200, "data": data},
)
```

### Bad: Imperative branching instead of composition

```python
# ✗ WRONG — breaks railway pattern
result = get_user(user_id)
if result.is_failure:
    return {"error": result.error}
perms = get_permissions(result.value)
if perms.is_failure:
    return {"error": perms.error}
return {"data": perms.value}
```

**Why bad**: Duplicated error handling at every step. Use `.flat_map()` chain instead.

### Bad: Bare try/except bypassing FlextResult

```python
# ✗ WRONG — exceptions bypass result flow
try:
    user = fetch_user(user_id)
    return {"data": user}
except Exception as e:
    return {"error": str(e)}
```

**Why bad**: Loses error_code/error_data metadata, breaks composition. Use `@FlextResult.safe` or explicit `r[T].fail()`.

### Bad: Constructing FlextResult directly

```python
# ✗ WRONG — internal constructor, not guaranteed stable
result = FlextResult(Success(value))
```

**Why bad**: Constructor has complex dual-mode logic (legacy vs new). Always use `r[T].ok()` / `r[T].fail()`.

## Subproject Usage Map

| Subproject       | Files                                                              | Pattern                                                  |
| ---------------- | ------------------------------------------------------------------ | -------------------------------------------------------- |
| `flext-auth`     | `provider_service.py`, `token_service.py`, `registry.py`, `api.py` | `from flext_core import r` — service results, auth flows |
| `flext-grpc`     | `api.py`                                                           | FlextResult for gRPC operation results                   |
| `flext-dbt-ldif` | `dbt_client.py`, `models.py`, `settings.py`                        | Business rule validation, DBT workflow results           |
| `flext-tap-ldif` | `utilities.py`                                                     | `from flext_core import FlextResult, t`                  |
| `flext-meltano`  | `dbt/service.py`                                                   | `from flext_core import r, FlextService`                 |
| `flext-cli`      | service modules                                                    | CLI operation results                                    |

## Verification

Make gates:

```bash
make check PROJECT=flext-core                  # lint + type gates for result.py
make check PROJECT=flext-core CHECK_GATES=type # type-check FlextResult composition
make test PROJECT=flext-core                   # railway composition tests
make validate PROJECT=flext-core               # complexity gates
```

Pattern checks:

```bash
# Confirm FlextResult declarations
rg -n "def ok|def fail|def map|def flat_map|def lash|def recover|def traverse|def fold|def tap" flext-core/src/flext_core/result.py

# Confirm r alias export
rg -n "^r = FlextResult" flext-core/src/flext_core/result.py

# Confirm subproject usage
rg -n "from flext_core import.*FlextResult|from flext_core import.*\br\b" --glob "**/*.py" flext-auth flext-grpc flext-meltano

# Verify no direct constructor usage (anti-pattern)
rg -n "FlextResult\(Success\|FlextResult\(Failure" --glob "**/*.py" flext-auth/src/ flext-grpc/src/

# Confirm returns library pinned
rg "returns>=" flext-core/pyproject.toml
```
