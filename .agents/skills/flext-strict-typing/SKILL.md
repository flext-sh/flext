---
name: flext-strict-typing
description: 'Defines and enforces the FLEXT type hierarchy: t.* contracts, PEP 695
  type aliases, r[T] result containers, and isinstance/TypeGuard narrowing. Use when
  writing type annotations, fixing pyrefly or pyright errors, working with t.JsonValue
  or t.Scalar, enforcing no-Any. DO NOT USE FOR: questions unrelated to flext-strict-typing
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# FLEXT Strict Typing Rules

**UTILITY SKILL**

Defines and enforces the FLEXT type hierarchy.

## USE FOR

- Writing or fixing type annotations.
- Resolving `pyrefly` / `pyright` errors.
- Choosing between `Mapping`, concrete `m.*` Pydantic models (data contracts), and `t.JsonValue` (`TypedDict` is not a data contract — ADR-011).
- Enforcing no-`Any` policies.

## DO NOT USE FOR

- Questions unrelated to FLEXT typing.
- Creating projects or architecture from scratch.

## Workflow

1. Detect typing violations from gates or structural search.
2. Map each violation to canonical `t.*` and `r[T]` patterns.
3. Apply fixes in shared-core-first order when contracts are reused.

## Critical rules

- No `typing.Any` in contracts.
- Use `Mapping` / `MutableMapping` for mapping contracts; use `dict` only for mutation hotspots.
- Use `t.JsonValue` for unknown JSON payloads.
- Use `r[T]` for fallible application paths.
- Narrow with `isinstance` + `TypeGuard`; avoid `type()`.

## Good examples

```python
from __future__ import annotations

from collections.abc import Mapping
from flext_core import r, t


def parse(data: Mapping[str, t.JsonValue]) -> r[int]: ...
```

```python notest
# Illustrative TypeGuard pattern — runtime narrowing requires an unconstrained input.
from typing import TypeGuard


class User:
    pass


def is_user(value: object) -> TypeGuard[User]:
    return isinstance(value, User)
```

## Bad examples

```python notest
# Illustrative anti-pattern: legacy typing and bare Any.
from typing import Any, Dict


def parse(data: Dict[str, Any]) -> Any: ...
```

```python notest
# Illustrative anti-pattern: bare object/dict instead of typed contracts.
def parse(data: dict[str, object]) -> dict[str, object]: ...
```

## Mapping contract guide

| Intent | Type |
|--------|------|
| read-only contract | `Mapping[str, t.JsonValue]` |
| mutating contract | `MutableMapping[str, t.JsonValue]` |
| schema payload / data contract | concrete `m.*` (`BaseModel` / `RootModel`) — never `TypedDict` (ADR-011) |
| mutation hotspot | `dict[str, t.JsonValue]` (rare) |

## Result containers

Fallible paths return `r[T]` from `returns`:

```python
from __future__ import annotations

from flext_core import r


def load(user_id: int) -> r[str]: ...
```

## Suppression comments

Do not use `# type: ignore`, `# noqa`, `# pylint: disable`, or `# mypy: ignore`. Fix the root cause.

## Validation

```bash
pyrefly check <file>
pyright <file>
ruff check <file>
```

## References

- [references/type-rules-detail.md](references/type-rules-detail.md)
- `.agents/skills/coding-standards/SKILL.md` — general coding standards quick-reference
