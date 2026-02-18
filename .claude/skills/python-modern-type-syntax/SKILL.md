---
name: python-modern-type-syntax
description: Modern Python type annotation patterns for 3.10+ including union syntax, type aliases, generics, Self, ParamSpec, and TypeVarTuple. Use when writing or modernizing type annotations.
---

# Python Modern Type Syntax

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- Type annotations across all FLEXT Python subprojects
- `flext-core/src/flext_core/typings.py` — central type definitions
- `flext-core/src/flext_core/protocols.py` — protocol definitions

## References

- <https://docs.python.org/3.13/library/typing.html>
- `.claude/skills/flext-strict-typing/SKILL.md` — FLEXT-specific type rules
- `.claude/skills/python-313-typing/SKILL.md` — Python 3.13 typing PEPs

## Rules

- Use `X | Y` union syntax (3.10+) instead of `Union[X, Y]`.
- Use `type` statement for type aliases (3.12+) instead of `TypeAlias`.
- Use new generic syntax `class Foo[T]:` (3.12+) instead of `Generic[T]`.
- Use `Self` (3.11+) for return type of methods returning own class.
- Follow FLEXT namespace alias conventions (`t.*`, `p.*`) for project types.

## Instructions

### Union Syntax (3.10+)

```python
# Modern
def process(value: str | int | None) -> str: ...

# Avoid
from typing import Union, Optional
def process(value: Union[str, int, Optional[str]]) -> str: ...
```

### Type Alias Syntax (3.12+)

```python
# Modern
type UserID = str | int
type Callback[T] = Callable[[T], None]

# Avoid
from typing import TypeAlias
UserID: TypeAlias = str | int
```

### Generic Class Syntax (3.12+)

```python
# Modern
class Container[T]:
    def __init__(self, value: T) -> None:
        self.value = value

# With bounds
class NumberBox[T: (int, float)]:
    def __init__(self, value: T) -> None:
        self.value = value

# With defaults (3.13+, PEP 696)
class Result[T, E = str]:
    ...
```

### Generic Function Syntax (3.12+)

```python
# Modern
def first[T](items: Sequence[T]) -> T:
    return items[0]

# Multiple type parameters
def zip_with[T, U, V](a: T, b: U, func: Callable[[T, U], V]) -> V:
    return func(a, b)
```

### Self Type (3.11+)

```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self
```

### ParamSpec (3.10+)

```python
from typing import ParamSpec, Callable

type P = ParamSpec("P")

def decorator[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
    return wrapper
```

### TypeVarTuple (3.11+)

```python
def apply[*Ts](funcs: tuple[Callable[[], *Ts]]) -> tuple[*Ts]:
    return tuple(f() for f in funcs)
```

### Never and NoReturn (3.11+)

```python
from typing import Never, NoReturn, assert_never

def handle_status(status: str) -> Never:
    raise ValueError(f"unexpected: {status}")
```

### Required/NotRequired (3.11+)

```python
from typing import TypedDict, Required, NotRequired

class Config(TypedDict):
    host: Required[str]
    port: NotRequired[int]
```

## Workflow

1. Check project's minimum Python version to determine available syntax.
2. Use modern syntax for new code — match the newest available features.
3. When modernizing existing code, update one module at a time.
4. Verify with type checker after each migration batch.

## Examples

Good:

```python
def fetch(id: str | int) -> User | None:
    ...
```

Why good: uses 3.10+ union syntax — concise and readable.

Bad:

```python
from typing import Union, Optional
def fetch(id: Union[str, int]) -> Optional[User]:
    ...
```

Why bad: verbose legacy syntax — `Union` and `Optional` are unnecessary with `|`.

## Verification

```bash
rg -n "Union\[|Optional\[" --glob "**/*.py" flext-core/src/ | head -20
rg -n "type \w+ =" --glob "**/*.py" flext-core/src/
rg -n "class \w+\[" --glob "**/*.py" flext-core/src/
```
