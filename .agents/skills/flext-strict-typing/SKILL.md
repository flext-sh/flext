---
name: flext-strict-typing
description: Defines and enforces the FLEXT type hierarchy: t.* contracts, PEP 695 type aliases, r[T] result containers, and isinstance/TypeGuard narrowing. Use when writing type annotations, fixing pyrefly or pyright errors, working with t.JsonValue or t.Scalar, enforcing no-Any strictness, or deciding how to narrow a discriminated union in src/ code.

---

# FLEXT Strict Typing Rules

**Reviewed**: 2026-04-20 | **Scope**: Type hierarchy, PEP 695 aliases/generics, r[T] containers, TypeIs/TypeGuard narrowing, match/case dispatch, @override/@final/Self

## Hard Start Card (mandatory)

1. No `Any`, no loose unions rebuilt at call sites.
2. Reuse canonical `c.*`, `t.*`, `p.*`, `m.*`, `u.*`, `h.*`, `r[T]` first.
3. Prefer `TypeIs`, `Self`, `@override`, `match/case`, PEP 695 aliases/generics.
4. Replace nullable fallibility with `r[T]`.
5. Delete unnecessary polymorphic helper code when typing primitives or Pydantic contracts already express the contract.
6. Finish only with all typing gates green.

## Typing Kill-Switches (mandatory)

1. If you write `Any`, stop and replace with `t.*` contract.
2. If you write `T | None` for fallibility, stop and replace with `r[T]`.
3. If you write a custom polymorphic helper, stop and try `TypeIs` / discriminated union / `match`.
4. If you cannot name the exact shared alias/protocol being reused, stop and search first.

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
- Before creating a new alias/helper, check whether the concern already belongs to `c.*`, `t.*`, `p.*`, `m.*`, `u.*`, or `h.*`. Reuse the owner first.
- Keep ownership explicit: structural protocols in `p.*`, composed aliases in `t.*`, domain models in `m.*`.
- Never annotate with a concrete class when an inherited `p.*` protocol or `t.*` alias already expresses the contract.
- Use `r[T]` for fallible returns and avoid nullable fallibility patterns.
- Use `isinstance`/TypeGuard for narrowing; avoid `type(...) is ...` narrowing.
- Keep typing changes integral: verify ruff, mypy, pyright, and pyrefly.
- Prefer central `t.*` aliases at the lowest stable layer when the same type composition appears more than once; do not keep rebuilding equivalent unions at call sites.
- Ad-hoc polymorphic helpers that only re-express an existing protocol, typed union, discriminated union, or result contract are deletion targets.
- Prefer existing `t.JsonValue` and CLI/Core JSON-capable contracts over new recursive or transport-shape aliases.
- **PEP 695 only** for new/touched code: `type X = ...` aliases (no `typing.TypeAlias`), `class Foo[T]` generics, `def f[T](x: T) -> T` (no `typing.TypeVar`/`Generic`).
- **Narrowing**: prefer `TypeIs[T]` (bidirectional narrowing) over `TypeGuard[T]` (one-way) for every `is_*` helper. Bare `bool` returns from is-helpers at public boundaries are forbidden.
- **Structural pattern matching** (`match/case`) mandatory for multi-branch dispatch on discriminated unions or subtypes. Rewrite `isinstance` ladders of three or more branches.
- **`@override`** on every overriding method (prevents drift after parent signature changes).
- **`@final`** on leaf classes that must not be subclassed.
- **`Self`** return type for fluent/copy methods and classmethod factories that return the current class.
- **Builtin generics** only: `list`, `dict`, `tuple`, `set`, `frozenset`. `typing.List/Dict/Tuple/Set/FrozenSet` forbidden.
- **`T | None`** / **`A | B`** only; `typing.Optional` and `typing.Union` are forbidden in new or touched code.
- **Protocols at boundaries**: see `.agents/skills/flext-type-system/SKILL.md` for the mandatory use of `p.*` protocols at every public API boundary that accepts a concrete class.

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

from flext_core import m, p, r


def parse_payload(payload: m.ConfigMap) -> p.Result[str]:
    """Use m.ConfigMap for mapping parameters, p.Result[T] as return type."""
    value = payload.root.get("key", "")
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

## Verification

- `rg -n "typing\.(TypeVar|TypeAlias|Generic|Optional|Union|List|Dict|Tuple|Set|FrozenSet)" --type py --glob '!**/.venv/**'` — expect zero hits in new/touched code.
- `rg -n "\bObject\b|\bAny\b" flext-core/src/flext_core --type py` — audit every hit for §3.2 compliance.
- `rg -n "Optional\[|Union\[" --type py --glob '!**/.venv/**'` — expect zero hits.
- `rg -n "def is_[a-z_]+\([^)]*\)\s*->\s*bool:" --type py --glob '!**/.venv/**'` — audit for `TypeIs`/`TypeGuard` migration.
- `rg -n "@override\b" --type py src/ | head -20` — spot-check decorator usage on overrides.
- `ruff check src/ tests/` — 0.
- `pyrefly check src/` — 0.
- `pyright src/` — 0.
