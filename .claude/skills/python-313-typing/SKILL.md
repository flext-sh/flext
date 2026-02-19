<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [PEP 696 — Type Parameter Defaults](#pep-696-type-parameter-defaults)
  - [PEP 702 — @deprecated](#pep-702-deprecated)
  - [PEP 705 — ReadOnly TypedDict](#pep-705-readonly-typeddict)
  - [PEP 742 — TypeIs](#pep-742-typeis)
  - [Other 3.13 Improvements](#other-313-improvements)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---
name: python-313-typing
description: Comprehensive Python 3.13 typing PEPs reference — PEP 696 (type defaults), PEP 702 (@deprecated), PEP 705 (ReadOnly), PEP 742 (TypeIs). Use when working with Python 3.13+ type features.
---

# Python 3.13 Typing

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival — consolidates 7 disabled skills

## Scope

- Python 3.13+ typing features across all FLEXT subprojects
- `flext-core/src/flext_core/typings.py` — central type definitions
- `flext-core/src/flext_core/result.py` — typed result patterns

## References

- <https://docs.python.org/3.13/whatsnew/3.13.html>
- <https://peps.python.org/pep-0696/> — Type Parameter Defaults
- <https://peps.python.org/pep-0702/> — @deprecated
- <https://peps.python.org/pep-0705/> — ReadOnly TypedDict
- <https://peps.python.org/pep-0742/> — TypeIs
- `.claude/skills/python-modern-type-syntax/SKILL.md` — 3.10+ syntax
- `.claude/skills/flext-strict-typing/SKILL.md` — FLEXT type rules

## Rules

- Use PEP 696 type defaults to reduce boilerplate in generic classes.
- Use `@deprecated` (PEP 702) instead of docstring-only deprecation notices.
- Use `ReadOnly` (PEP 705) for immutable TypedDict fields — not for all fields.
- Prefer `TypeIs` (PEP 742) over `TypeGuard` — it narrows both branches.

## Instructions

### PEP 696 — Type Parameter Defaults

```python
class Container[T = str]:
    def __init__(self, value: T) -> None:
        self.value = value

c1 = Container("hello")     # Container[str] — default
c2 = Container[int](42)     # Container[int] — explicit

class Result[T, E = str]:
    ...  # E defaults to str if not specified

type Callback[T = None] = Callable[[T], None]
```

**Multiple defaults** — defaults must trail non-defaulted params:

```python
class Map[K, V = str, M = dict[K, V]]:
    ...
```

**NoDefault sentinel**:

```python
from typing import TypeVar, NoDefault
T = TypeVar("T")
print(T.__default__ is NoDefault)  # True — no default set
```

### PEP 702 — @deprecated

```python
from warnings import deprecated

@deprecated("Use new_function() instead")
def old_function() -> None:
    ...

@deprecated("Use NewClass instead, removed in 4.0")
class OldClass:
    ...
```

Type checkers emit warnings at call sites. Runtime emits `DeprecationWarning`.

**Deprecate specific overload**:

```python
from typing import overload
from warnings import deprecated

@overload
@deprecated("Pass keyword args instead")
def connect(host: str, port: int) -> Connection: ...

@overload
def connect(*, url: str) -> Connection: ...
```

### PEP 705 — ReadOnly TypedDict

```python
from typing import ReadOnly, TypedDict

class Config(TypedDict):
    name: ReadOnly[str]       # immutable after creation
    debug: bool               # mutable

cfg: Config = {"name": "app", "debug": True}
cfg["debug"] = False  # OK
cfg["name"] = "new"   # type error: ReadOnly
```

**With Required/NotRequired**:

```python
class Settings(TypedDict):
    host: ReadOnly[Required[str]]
    port: ReadOnly[NotRequired[int]]
    timeout: int  # mutable, required
```

**Inheritance** — ReadOnly is preserved through inheritance:

```python
class Base(TypedDict):
    version: ReadOnly[str]

class Extended(Base):
    extra: str  # version remains ReadOnly
```

### PEP 742 — TypeIs

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(data: list[object]) -> None:
    if is_str_list(data):
        print(data[0].upper())  # narrowed: list[str]
    else:
        print(len(data))  # narrowed: list[object] (BOTH branches!)
```

**TypeIs vs TypeGuard**:

| Feature | TypeIs (PEP 742) | TypeGuard (PEP 647) |
|---|---|---|
| Narrows positive branch | Yes | Yes |
| Narrows negative branch | Yes | No |
| Requires subtype relationship | Yes | No |
| Use for | Exact type checks | Structural/duck-type checks |

**FLEXT pattern**:

```python
from typing import TypeIs
from flext_core import FlextResult

def is_success[T](result: FlextResult[T]) -> TypeIs[FlextResult[T]]:
    return result.is_success
```

### Other 3.13 Improvements

**Improved `locals()` semantics (PEP 667)**:

```python
def example():
    x = 1
    loc = locals()
    x = 2
    # In 3.13: locals() returns a snapshot, not a live view
    assert loc["x"] == 1  # snapshot at time of call
```

## Workflow

1. Check that project targets Python 3.13+ before using these features.
2. Use type defaults (PEP 696) to simplify generic class APIs.
3. Mark deprecated APIs with `@deprecated` for type checker and runtime warnings.
4. Use `ReadOnly` selectively on TypedDict fields that must be immutable.
5. Prefer `TypeIs` over `TypeGuard` for type narrowing guards.

## Examples

Good:

```python
class Cache[K = str, V = bytes]:
    def get(self, key: K) -> V | None: ...

cache = Cache()          # Cache[str, bytes]
cache = Cache[int, str]() # Cache[int, str]
```

Why good: PEP 696 defaults reduce boilerplate — callers don't need to specify common type args.

Bad:

```python
# Deprecating via docstring only
def old_func():
    """Deprecated: use new_func() instead."""
    ...
```

Why bad: type checkers can't warn callers. Use `@deprecated("use new_func()")` instead.

## Verification

```bash
rg -n "TypeIs\[|ReadOnly\[|@deprecated|NoDefault" --glob "**/*.py" flext-core/src/
python -c "from typing import TypeIs, ReadOnly; print('3.13 typing available')" 2>/dev/null || echo "Python < 3.13"
```
