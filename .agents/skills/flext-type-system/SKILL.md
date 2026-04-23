---
name: flext-type-system
description: Canonical FLEXT type-system map for aliases, generics, result interplay, and settings contracts. Use when changing shared typing primitives.

---

# Flext Type System

**Reviewed**: 2026-04-20 | **Scope**: Type-system map — aliases, generics, result interplay, settings contracts, p.* protocols mandatory at public boundaries

## Scope

- Type-system source of truth:
  - `flext-core/src/flext_core/typings.py`
- Type consumers:
  - `flext-core/src/flext_core/result.py`
  - `flext-core/src/flext_core/settings.py`
  - `flext-core/src/flext_core/protocols.py`

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_core/typings.py` (type vars + aliases + `FlextTypes`)
- `flext-core/src/flext_core/result.py` (`r[T_co]` and alias `r`)
- `flext-core/src/flext_core/settings.py` (`T_Settings` bound usage)
- `flext-core/src/flext_core/__init__.py` (exported aliases)

## Rules

- Add shared aliases in `typings.py` rather than re-declaring in feature modules. Type aliases MUST be non-nullable — `| None` is added inline at usage sites only.
- Structural protocols live in `protocols.py` (consumed via `p.*`); reusable composed aliases live in `typings.py` (consumed via `t.*`); domain carriers live in `models.py` (consumed via `m.*`). Never annotate with a concrete class when an inherited `p.*`/`t.*` already expresses the contract.
- Keep `t.JsonValue` canonical: it is only the `pydantic.JsonValue` re-export (`tp.JsonValue` / `t.JsonValue`). Never widen that alias with `Path`, `BaseModel`, `JsonList`, `JsonMapping`, or any other union members.
- Preserve generic covariance/contravariance semantics where defined.
- Keep exported short aliases (`t`, `r`) stable across refactors.
- Canonical governance (see `AGENTS.md`):
  - §3.2 — `Any`, `object`, and `Mapping[str, Any]` are forbidden; `| None` inline-only.
  - §3.3 — `r[T]` is the sole fallibility contract; no `T | None` returns in business logic.
  - §3.1 — single nested-class hierarchy per module via MRO from Pydantic v2 `BaseModel`.
  - §3.5 — every type change passes all 4 linters and updates impacted references via `ast-grep`.
- **Cross-project namespace inheritance**: downstream projects MUST inherit parent facade classes (e.g., `FlextMeltanoModels`, not `FlextModels`) so namespaces cascade via MRO. Applies to `m`, `c`, `t`, `u`, `p`. See the Cross-Project section below.
- **Protocols mandatory at public boundaries**: every public parameter/return that accepts or exposes a dispatcher, handler, service, container, settings, or model MUST be typed as a `p.*` protocol — never as a concrete `m.*` class or a concrete service class. Concrete classes appear only inside their own implementation body and at wire boundaries (factory output, fixture bootstrap). Missing protocols MUST be added under the owning project's `p.*` namespace first. Verification: `rg -n "-> (Flext|m)\.[A-Z][A-Za-z]+\." --type py src/ --glob '!**/factory*.py' --glob '!**/fixtures/**'` — every hit must be justified as a wire boundary.
- See `.agents/skills/flext-strict-typing/SKILL.md` for PEP 695 aliases/generics, `TypeIs`/`TypeGuard` narrowing, structural `match/case`, `@override` and `@final` usage — those rules compose with everything in this skill.

## TypeAliasType Runtime Boundary (CRITICAL — Python 3.12+)

PEP 695 `type X = ...` creates `TypeAliasType`. In FLEXT, that syntax is canonical in `typings.py`, and those aliases are annotation-only.

**Rules:**

1. Use `type X = ...` for aliases in `typings.py`, following AGENTS.md.
2. Never use `isinstance(val, t.SomeAlias)`.
3. Never subclass a type alias.
4. Runtime narrowing MUST use the canonical `u.is_*()` helpers.
5. `TypeAdapter` is validation infrastructure, not a replacement for runtime narrowing.

**Quick reference:**

| Pattern                     | Status               |             |
| --------------------------- | -------------------- | ----------- |
| `type X = str \             | int` in `typings.py` | ✅ canonical |
| `isinstance(val, t.Scalar)` | ❌ forbidden          |             |
| `u.is_scalar(val)`          | ✅ canonical          |             |

## Cross-Project Namespace Inheritance (m, c, t, u, p)

Each downstream project inherits its parent project's facade, gaining all parent namespaces via MRO:

```python
# flext-target-oracle/models.py
from flext_meltano import FlextMeltanoModels


class FlextTargetOracleModels(FlextMeltanoModels):  # NOT FlextModels
    class TargetOracle:
        class MyModel(FlextMeltanoModels.ArbitraryTypesModel): ...


m = FlextTargetOracleModels
# m.Meltano.*       → inherited from FlextMeltanoModels
# m.TargetOracle.*  → defined locally
```

**Why this pattern is mandatory:**

| Approach                                            | Problem                                                              |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| `Meltano = FlextMeltanoModels.Meltano` (assignment) | mypy `name-defined` error with `from __future__ import annotations`  |
| Per-type subclasses inside `class Meltano:`         | Invariance errors: `Sequence[SubType]` ≠ `Sequence[ParentType]`      |
| `from flext_meltano import m`                       | Anti-pattern: duplicates namespace surface, adds unnecessary aliases |
| Top-level inheritance (`class Models(Parent):`)     | ✅ Clean MRO, zero duplication, exact same types                      |

**Anti-patterns (NEVER):**

- `from flext_meltano import m` — duplicate alias
- `class Meltano: SingerSchemaMessage = FlextMeltanoModels.Meltano.SingerSchemaMessage` — not valid as type
- Inheriting `FlextModels` directly when parent project namespaces are needed

## r[T] Container Invariance Rules

`r[T]` is **INVARIANT** — the type parameter `T` does not vary with subtyping.

**Rule:** Inside `r[T]`, use the **concrete** container type that matches the actual runtime value. Do NOT substitute abstract `Sequence`, `Mapping`, etc. as the type parameter — invariance makes that a type error.

| Return value | Correct annotation   | FORBIDDEN             |        |
| ------------ | -------------------- | --------------------- | ------ |
| `[1, 2, 3]`  | `r[list[int]]`       | `r[Sequence[int]]`    |        |
| `{"a": 1}`   | `r[dict[str, int]]`  | `r[t.IntMapping]`     |        |
| `{1, 2}`     | `r[set[int]]`        | `r[AbstractSet[int]]` |        |
| `(1, "x")`   | `r[tuple[int, str]]` | `r[Sequence[int \     | str]]` |

**Why:** `r[Sequence[int]]` and `r[list[int]]` are distinct types under invariance. Returning `r[list[int]]` where `r[Sequence[int]]` is declared is a type error.

**Parameter types** (function inputs) still use abstract covariant types (`Sequence`, `Mapping`) — invariance only applies inside `r[T]`.

```python
from __future__ import annotations

from flext_core import p, t


# CORRECT
def get_items() -> p.Result[list[str]]: ...


def get_config() -> p.Result[dict[str, int]]: ...


# FORBIDDEN — invariance violation: r[Sequence[int]] != r[list[int]]
# def get_items_bad() -> p.Result[t.StrSequence]: ...
# def get_config_bad() -> p.Result[t.IntMapping]: ...


# Parameters: abstract types OK (covariant position)
def process(items: t.StrSequence) -> p.Result[list[str]]: ...
```

## Instructions

- Use existing type var definitions before introducing new generic parameters.
- Prefer existing `FlextTypes` aliases and `p.*` protocols for public contracts; refine the canonical shared contract instead of inventing a local concrete annotation.
- Ensure downstream users (`result.py`, `settings.py`, `protocols.py`) still type-check.
- When creating a new project that depends on another FLEXT project's types, ALWAYS inherit the parent facade class in your models/protocols/etc.

```python
# Excerpt from flext-core/src/flext_core/typings.py — shown for reference only.
# The actual declarations live in typings.py and are accessed via t.* at call sites.

# TypeVar declarations (in typings.py):
# T = TypeVar("T")
# T_Settings = TypeVar("T_Settings", bound=BaseSettings)

# Canonical alias (in typings.py — NOT valid at call sites, annotation-only):
# type JsonValue = pydantic.JsonValue  # re-exported via tp.JsonValue / t.JsonValue
```

## Workflow

1. Locate existing alias/type-var nearest to intended change.
2. Extend or refine canonical alias in `typings.py`.
3. Validate impacted consumers in result/settings/protocol modules.
4. Re-run type checks for affected packages.

## Examples

Good:

```python
type JsonPrimitive = str | int | float | bool | None
```

Why good: focused annotation-only alias with clear semantic purpose.

Bad:

```python
from __future__ import annotations

from flext_core import t

# FORBIDDEN pattern — do NOT copy:
# JsonPrimitive = t.JsonValue  # erases all type constraints
# Use the explicit union or t.Scalar instead.

# Stub to satisfy linters in this documentation block:
JsonPrimitive = str | int | float | bool | None  # ← correct pattern
_ = t  # referenced above in the forbidden example comment
```

Why bad: `object` is forbidden in annotations (`AGENTS.md` §3.2) — it erases constraints and degrades static analysis. Use `t.Scalar` or the explicit union type.

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=type` — type-check validates type system contracts
- `make check PROJECT=flext-core` — full lint + type + format + security
- `make test PROJECT=flext-core` — type contracts exercised by test suite

Pattern checks:

- `rg -n "TypeVar\(|type t.JsonValue|class FlextTypes|JsonPrimitive" flext-core/src/flext_core/typings.py`
- `rg -n "class r|type .*=" flext-core/src/flext_core/result.py`
- `rg -n "T_Settings|BaseSettings" flext-core/src/flext_core/settings.py flext-core/src/flext_core/typings.py`
