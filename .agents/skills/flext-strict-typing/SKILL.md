---
name: flext-strict-typing
description: Defines and enforces the FLEXT type hierarchy: t.* contracts, PEP 695 type aliases, r[T] result containers, and isinstance/TypeGuard narrowing. Use when writing type annotations, fixing pyrefly or pyright errors, working with t.Container or t.Scalar, enforcing no-Any strictness, or deciding how to narrow a discriminated union in src/ code.

---

# FLEXT Strict Typing Rules

**Reviewed**: 2026-03-03 | **Scope**: Type hierarchy, PEP 695 aliases, r[T] containers, isinstance/TypeGuard narrowing

> **Source of truth**: Extracted from `flext-core/src/flext_core/typings.py` (534 lines)
> and cross-referenced with `models.py`, `protocols.py`, and `ruff-shared.toml`.
>
> **Rule**: See `AGENTS.md` §3 Code Law for canonical `r` and typing requirements.

## Scope

- Strict typing law across all projects, including `src/`, `tests/`, and `examples/`.
- Type contracts, narrowing discipline, alias safety, and Pydantic v2 typing patterns.

## References

- `AGENTS.md`
- `flext-core/src/flext_core/typings.py`
- `flext-core/src/flext_core/result.py`
- `flext-core/src/flext_core/protocols.py`

## Rules

- Use `t.*` contracts from `typings.py` instead of ad-hoc inline unions.
- Keep ownership explicit: structural protocols in `p.*`, composed aliases in `t.*`, domain models in `m.*`.
- Never annotate with a concrete class when an inherited `p.*` protocol or `t.*` alias already expresses the contract.
- Use `r[T]` for fallible returns and avoid nullable fallibility patterns.
- Use `isinstance`/TypeGuard for narrowing; avoid `type(...) is ...` narrowing.
- Keep typing changes integral: verify ruff, mypy, pyright, and pyrefly.

## Instructions

- Start by classifying each type issue (annotation, alias, narrowing, result flow).
- If a failure comes from a missing shared contract, add or refine the canonical contract in `protocols.py` or `typings.py` before patching consumers.
- Apply minimally invasive, architecture-safe fixes that preserve MRO contracts.
- Re-run targeted and project gates after each fix group.

## Workflow

1. Detect typing violations from gates and structural search.
2. Map each violation to canonical `t.*` and `r` patterns.
3. Apply fixes in shared-core-first order when contracts are reused.
4. Validate and confirm no regression in dependent projects.

## Examples

Good:

```python
from __future__ import annotations

from flext_core import p, r, t


def parse_payload(payload: m.ConfigMap) -> p.Result[str]:
    """Use m.ConfigMap for Mapping[str, str] parameters, p.Result[T] as return type."""
    value = payload.get("key", "")
    if not value:
        return r[str].fail("key is missing")
    return r[str].ok(str(value))
```

Why good: the example uses a public contract and keeps fallibility on `r[T]`.

Bad:

```python
from flext_core import FlextRegistry


def parse_payload(payload: FlextRegistry) -> str | None:
    return None
```

Why bad: it couples the signature to a concrete implementation and reintroduces nullable fallibility instead of the canonical public contract.

## Detailed Type Rules

Full type enforcement rules are in [references/type-rules-detail.md](references/type-rules-detail.md). Load it when you need rule-level detail on:

- `Any` prohibition and allowed exceptions
- PEP 695 `type X = ...` alias syntax and runtime restrictions
- TypeVar, TypeVarTuple, ParamSpec patterns
- Pydantic v2 typing integration and model field rules
- Protocol patterns and structural subtyping
- Enum/Literal patterns in `constants.py`
- Return type policies by code path
- Advanced pyrefly/pyright error fix strategies
