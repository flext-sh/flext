<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: flext-type-system
description: Canonical FLEXT type-system map for aliases, generics, result interplay, and settings contracts. Use when changing shared typing primitives.

---

# Flext Type System

**Reviewed**: 2026-03-03 | **Scope**: AXIOMATIC type purity — `Any`/`t.NormalizedValue` absolute prohibition enforced

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
- Keep recursive/general value aliases compatible with existing boundaries.
- Preserve generic covariance/contravariance semantics where defined.
- Keep exported short aliases (`t`, `r`) stable across refactors.
- **AXIOMATIC**: `Any`, `t.NormalizedValue`, and `dict[str, Any]` are TOTALLY FORBIDDEN in type annotations, function signatures, return types, and examples. Use `t.*` contracts from `typings.py` exclusively. Inline composed types are FORBIDDEN in all 33 projects — use `t.*` references only.
- **AXIOMATIC**: `| None` MUST NEVER appear in type alias definitions in `typings.py`. Type aliases are ALWAYS non-nullable. Consumers add `| None` inline at usage sites when business requires it (e.g., `field: t.Scalar | None`). No `NullableX` or `OptionalX` aliases.
- **AXIOMATIC**: Duplicating type definitions from the MRO chain is FORBIDDEN — even inside subproject `FlextTypes` nested classes. One definition, one source of truth. Compatibility aliases (`X = t.Y`) are FORBIDDEN.
- **AXIOMATIC**: `r` (`r`) is the SOLE mechanism for expressing fallibility. Functions that can fail MUST return `r[T]` — never `T | None`, never bare exceptions, never ad-hoc error dicts. The `r` alias (`from flext_core import r`) is MANDATORY at all usage sites. Composition operators (`map`, `flat_map`, `lash`, `value_or`) MUST replace `if result is None` / `try/except` chains. `r` eliminates `| None` return types from the business layer.
- **AXIOMATIC**: Compatibility wrappers (`def old(): return new()`), non-business validation fallbacks, legacy code maintenance, and `OldName = NewName` aliases are TOTALLY FORBIDDEN. Legacy code is deleted and replaced with canonical patterns. No grace period, no deprecation path.
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance. The most base class MUST inherit from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE Pydantic v2 features to their fullest. `Field()` with `description`/`title`/`examples`/`json_schema_extra` for ALL declarations. Minimize custom validators — prefer built-in constraints. `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). FORBIDDEN in models: init helpers, unnecessary `@property`, simple getters/setters, wrappers. USE: `@computed_field`, `model_post_init`, `PrivateAttr`. Enums/Literals from `c.*`, config from `s.*`. Internal state via `PrivateAttr`. Nested classes MAY have business methods but ALL properties use `Field()`/`PrivateAttr`. `models.py`/`_models/` for models ONLY.
- **AXIOMATIC**: Every type change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. ALL impacted references across ALL 33 projects MUST be updated via ast-grep (`sg`) search-and-replace immediately. Linter suppressions (`# type: ignore`, `# noqa`, etc.) are FORBIDDEN without real internet citations, business necessity in comments, and per-line only scope. Global suppressions are TOTALLY FORBIDDEN.
- **Cross-project namespace inheritance**: downstream projects MUST inherit parent facade classes (e.g., `FlextMeltanoModels`, not `FlextModels`) so namespaces cascade via MRO. This applies to `m`, `c`, `t`, `u`, `p`.

## TypeAliasType isinstance Incompatibility (CRITICAL — Python 3.12+)

PEP 695 `type X = ...` creates `TypeAliasType`, NOT `UnionType`. `isinstance(val, X)` FAILS at runtime.

**Rules:**
1. Non-recursive aliases (`Primitives`, `Scalar`, `Container`, `ConfigurationMapping`) → `X: TypeAlias = ...` (isinstance-safe)
2. Recursive aliases (`t.NormalizedValue`, `t.NormalizedValue`, `t.NormalizedValue`, `t.NormalizedValue`) → `type X = ...` (NEVER use with isinstance)
3. `TypeAliasType.__value__` is transitively poisoned — do NOT use as isinstance workaround
4. `TypeAdapter` is 4x slower than isinstance — do NOT use for type checking
5. Use `TypeGuard` functions from `_utilities/guards.py`: `is_primitive()`, `is_scalar()`, `is_flexible_value()`

**Quick reference:**

| Syntax | Runtime type | isinstance? |
|--------|-------------|-------------|
| `X: TypeAlias = str \| int` | `UnionType` | ✅ |
| `type X = str \| int` | `TypeAliasType` | ❌ |
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
| Per-type subclasses inside `class Meltano:`         | Invariance errors: `list[SubType]` ≠ `list[ParentType]`              |
| `from flext_meltano import m as m_meltano`          | Anti-pattern: duplicates namespace surface, adds unnecessary aliases |
| Top-level inheritance (`class Models(Parent):`)     | ✅ Clean MRO, zero duplication, exact same types                     |

**Anti-patterns (NEVER):**

- `from flext_meltano import FlextMeltanoModels as m_meltano` — duplicate alias
- `class Meltano: SingerSchemaMessage = FlextMeltanoModels.Meltano.SingerSchemaMessage` — not valid as type
- Inheriting `FlextModels` directly when parent project namespaces are needed

## Instructions

- Use existing type var definitions before introducing new generic parameters.
- Prefer `FlextTypes` aliases (`t.NormalizedValue`, maps, scalar groups) for public contracts.
- Ensure downstream users (`result.py`, `settings.py`, `protocols.py`) still type-check.
- When creating a new project that depends on another FLEXT project's types, ALWAYS inherit the parent facade class in your models/protocols/etc.

```python
T = TypeVar("T")
T_Settings = TypeVar("T_Settings", bound=BaseSettings)

type t.NormalizedValue = (
    str
    | int
    | float
    | bool
    | datetime
    | None
    | BaseModel
    | Path
    | Sequence[t.NormalizedValue]
    | Mapping[str, t.NormalizedValue]
)
```

## Workflow

1. Locate existing alias/type-var nearest to intended change.
2. Extend or refine canonical alias in `typings.py`.
3. Validate impacted consumers in result/settings/protocol modules.
4. Re-run type checks for affected packages.

## Examples

Good:

```python
type JsonPrimitive = t.Primitives | None
```

Why good: focused alias with clear semantic purpose.

Bad:

```python
JsonPrimitive = (
    t.NormalizedValue
)  # ← FORBIDDEN: `t.NormalizedValue` erases all type constraints
```

Why bad: `t.NormalizedValue` is AXIOMATIC FORBIDDEN — it erases constraints and degrades static analysis. Use `t.Scalar` or the explicit union type.

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=type` — type-check validates type system contracts
- `make check PROJECT=flext-core` — full lint + type + format + security
- `make test PROJECT=flext-core` — type contracts exercised by test suite

Pattern checks:

- `rg -n "TypeVar\(|type t.NormalizedValue|class FlextTypes|JsonPrimitive" flext-core/src/flext_core/typings.py`
- `rg -n "class r|type .*=" flext-core/src/flext_core/result.py`
- `rg -n "T_Settings|BaseSettings" flext-core/src/flext_core/settings.py flext-core/src/flext_core/typings.py`
