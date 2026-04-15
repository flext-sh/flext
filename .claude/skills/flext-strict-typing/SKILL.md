---

name: flext-strict-typing
description: Defines and enforces the FLEXT type hierarchy: t.* contracts, PEP 695 type aliases, r[T] result containers, and isinstance/TypeGuard narrowing. Use when writing type annotations, fixing pyrefly or pyright errors, working with t.Container or t.Scalar, enforcing no-Any strictness, or deciding how to narrow a discriminated union in src/ code.
triggers:
  - writing type annotations in src/ code
  - fixing pyrefly or pyright type errors
  - working with t.* contracts (t.Container, t.Scalar, t.ConfigMap)
  - deciding how to narrow a discriminated union
  - replacing Any or bare dict with typed contracts
  - defining a new type alias in typings.py
  - using isinstance or TypeGuard for narrowing
  - reviewing r[T] return types
  - ensuring no-Any strictness across a module

---

<!-- TOC START -->

- [Python Version & Core Requirements](#python-version-core-requirements)
- [FLEXT Mapping-First Policy (Contract Layer)](#flext-mapping-first-policy-contract-layer)
- [Rule 1: NEVER Use `Any` or `t.RecursiveContainer`](#rule-1-never-use-any-or-t.RecursiveContainer)
  - [Replace with the appropriate type from the `FlextTypes` hierarchy](#replace-with-the-appropriate-type-from-the-flexttypes-hierarchy)
  - [The Type Hierarchy (from `typings.py` lines 153-176)](#the-type-hierarchy-from-typingspy-lines-153-176)
- [Verification](#verification)
  - [Special RootModel Containers (from `typings.py` lines 357-462)](#special-rootmodel-containers-from-typingspy-lines-357-462)
- [Rule 2: TypeAlias Declaration Format](#rule-2-typealias-declaration-format)
  - [Within the `FlextTypes` class — use `TypeAlias` annotation](#within-the-flexttypes-class-use-typealias-annotation)
  - [At module level — use PEP 695 `type` statement (required for recursive types)](#at-module-level-use-pep-695-type-statement-required-for-recursive-types)
- [Rule 3: TypeVars — Module-Level Only](#rule-3-typevars-module-level-only)
- [Rule 4: Modern Python Typing (Python 3.13+)](#rule-4-modern-python-typing-python-313)
  - [Always use modern syntax (with Mapping-first contracts)](#always-use-modern-syntax-with-mapping-first-contracts)
  - [Use `typing.Self` for return self patterns](#use-typingself-for-return-self-patterns)
- [Rule 5: Pydantic v2 Model Typing](#rule-5-pydantic-v2-model-typing)
  - [ConfigDict (not inner `class Config`)](#configdict-not-inner-class-settings)
  - [Field declarations](#field-declarations)
  - [Validators use `@field_validator` and `@model_validator`](#validators-use-fieldvalidator-and-modelvalidator)
- [Rule 6: Annotated Validation Types](#rule-6-annotated-validation-types)
- [Rule 7: protocols.py — Structural Typing](#rule-7-protocolspy-structural-typing)
- [Rule 8: Enum Typing — StrEnum Only](#rule-8-enum-typing-strenum-only)
- [Rule 9: Constants Typing — Final + Immutable Collections](#rule-9-constants-typing-final-immutable-collections)
- [Rule 13: Advanced Fix Strategy (No Simplistic Rewrites)](#rule-13-advanced-fix-strategy-no-simplistic-rewrites)
- [Rule 10: Return Types — ALWAYS Explicit](#rule-10-return-types-always-explicit)
- [Rule 11: Callable Typing](#rule-11-callable-typing)
- [Ruff Rules That Enforce Typing (from ruff-shared.toml)](#ruff-rules-that-enforce-typing-from-ruff-sharedtoml)
- [Rule 14: NEVER Use `str | None` When Default Is `""`](#rule-14-never-use-str--none-when-default-is-)
- [Rule 15: Pydantic Models Over Plain Helper Classes](#rule-15-pydantic-models-over-plain-helper-classes)
- [Rule 16: Result Protocol for `is_success` Pattern](#rule-16-result-protocol-for-is_success-pattern)
- [Rule 17: Type Narrowing and Polymorphic Contracts (Mandatory)](#rule-17-type-narrowing-and-polymorphic-contracts-mandatory)
- [Rule 12: r Factory Method Typing](#rule-12-flextresult-factory-method-typing)
  - [`r` Alias — Universal Import Pattern](#r-alias-universal-import-pattern)
  - [`ok()` vs `fail()` — Asymmetric Generics](#ok-vs-fail-asymmetric-generics)
  - [Internal Implementation Pattern (in `result.py`)](#internal-implementation-pattern-in-resultpy)
  - [Why `cast` Is Required](#why-cast-is-required)
  - [Usage Examples](#usage-examples)
  <!-- TOC END -->

# FLEXT Strict Typing Rules

**Reviewed**: 2026-03-03 | **Scope**: AXIOMATIC — `Any`/`t.RecursiveContainer` absolute prohibition, `None` only for business semantics, type narrowing only when business-required

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
from flext_core import p, r


def parse_payload(payload: p.MappingLikePayload) -> p.Result[str]:
    return r[str].ok("ok")
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
