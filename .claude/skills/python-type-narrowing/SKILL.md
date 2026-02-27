<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [isinstance Narrowing](#isinstance-narrowing)
  - [None Checks](#none-checks)
  - [TypeIs (Python 3.13+)](#typeis-python-313)
  - [TypeGuard (Python 3.10+)](#typeguard-python-310)
  - [assert_type (Python 3.11+)](#asserttype-python-311)
  - [Exhaustiveness Checking](#exhaustiveness-checking)
  - [Discriminated Union Narrowing](#discriminated-union-narrowing)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: python-type-narrowing
description: Type narrowing techniques including isinstance, TypeIs, TypeGuard, assert_type, and exhaustiveness checking. Use when writing conditional type logic or discriminated union handling.

---

# Python Type Narrowing

**Reviewed**: 2026-02-17 | **Scope**: Disabled skill revival

## Scope

- Type guard implementations across FLEXT subprojects
- `flext-core/src/flext_core/result.py` — `is_success_result`, `is_failure_result` guards
- `flext-core/src/flext_core/typings.py` — type definitions and guards

## References

- <https://docs.python.org/3.13/library/typing.html#typing.TypeIs>
- <https://docs.python.org/3.13/library/typing.html#typing.TypeGuard>
- `.claude/skills/python-313-typing/SKILL.md` — PEP 742 TypeIs details
- `.claude/skills/flext-strict-typing/SKILL.md` — FLEXT type rules

## Rules

- Prefer `TypeIs` (PEP 742, 3.13+) over `TypeGuard` — it narrows both branches.
- Use `isinstance` checks for simple type narrowing — no need for custom guards.
- Use `assert_never` for exhaustiveness checking in match/if-else chains.
- Never use `type()` comparison for narrowing — use `isinstance()` for type checks. (Except for AST identity where narrowing is not intended).
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, and architectural `getattr()`.

## Instructions

### isinstance Narrowing

```python
def process(value: str | int) -> str:
    if isinstance(value, str):
        return value.upper()
    return str(value)
```

### None Checks

```python
def get_name(user: User | None) -> str:
    if user is None:
        return "anonymous"
    return user.name  # narrowed to User
```

### TypeIs (Python 3.13+)

```python
from typing import TypeIs

def is_str_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(data: list[object]) -> None:
    if is_str_list(data):
        print(data[0].upper())  # narrowed: list[str]
    else:
        pass  # narrowed: list[object] (both branches!)
```

### TypeGuard (Python 3.10+)

```python
from typing import TypeGuard

def is_valid_user(obj: object) -> TypeGuard[User]:
    return isinstance(obj, dict) and "id" in obj

# Only narrows the positive branch (less precise than TypeIs)
```

### assert_type (Python 3.11+)

```python
from typing import assert_type

value: str | int = get_value()
if isinstance(value, str):
    assert_type(value, str)  # verify type checker agrees
```

### Exhaustiveness Checking

```python
from typing import assert_never

def handle(status: Literal["ok", "error", "pending"]) -> str:
    match status:
        case "ok": return "success"
        case "error": return "failed"
        case "pending": return "waiting"
        case _ as unreachable:
            assert_never(unreachable)  # compile-time error if cases missed
```

### Discriminated Union Narrowing

```python
class Dog:
    kind: Literal["dog"] = "dog"
class Cat:
    kind: Literal["cat"] = "cat"

type Pet = Dog | Cat

def feed(pet: Pet) -> str:
    match pet.kind:
        case "dog": return "bone"
        case "cat": return "fish"
```

## Workflow

1. Identify union types or optional values requiring conditional logic.
2. Use `isinstance` for simple type discrimination.
3. Use `TypeIs` for custom type guards that need both-branch narrowing.
4. Use `TypeGuard` only when `TypeIs` semantics don't apply (structural checks).
5. Add `assert_never` to match/if-else chains for exhaustiveness.

## Examples

Good:

```python
from typing import TypeIs

def is_success_result(r: FlextResult[T]) -> TypeIs[FlextResult[T]]:
    return r.is_success
```

Why good: TypeIs narrows both branches — caller gets precise types in if/else.

Bad:

```python
if type(value) == str:
    value.upper()
```

Why bad: `type()` comparison doesn't handle subclasses — use `isinstance(value, str)`.

## Verification

```bash
rg -n "TypeIs\[|TypeGuard\[|assert_never\|assert_type" --glob "**/*.py" flext-core/src/
rg -n "is_success_result|is_failure_result" flext-core/src/flext_core/result.py
```
