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

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope
- Type-system source of truth:
  - `flext-core/src/flext_core/typings.py`
- Type consumers:
  - `flext-core/src/flext_core/result.py`
  - `flext-core/src/flext_core/settings.py`
  - `flext-core/src/flext_core/protocols.py`

## References
- `flext-core/src/flext_core/typings.py` (type vars + aliases + `FlextTypes`)
- `flext-core/src/flext_core/result.py` (`FlextResult[T_co]` and alias `r`)
- `flext-core/src/flext_core/settings.py` (`T_Settings` bound usage)
- `flext-core/src/flext_core/__init__.py` (exported aliases)

## Rules
- Add shared aliases in `typings.py` rather than re-declaring in feature modules.
- Keep recursive/general value aliases compatible with existing boundaries.
- Preserve generic covariance/contravariance semantics where defined.
- Keep exported short aliases (`t`, `r`) stable across refactors.
- **Cross-project namespace inheritance**: downstream projects MUST inherit parent facade classes (e.g., `FlextMeltanoModels`, not `FlextModels`) so namespaces cascade via MRO. This applies to `m`, `c`, `t`, `u`, `p`.

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

| Approach | Problem |
|----------|---------|
| `Meltano = FlextMeltanoModels.Meltano` (assignment) | mypy `name-defined` error with `from __future__ import annotations` |
| Per-type subclasses inside `class Meltano:` | Invariance errors: `list[SubType]` ≠ `list[ParentType]` |
| `from flext_meltano import m as m_meltano` | Anti-pattern: duplicates namespace surface, adds unnecessary aliases |
| Top-level inheritance (`class Models(Parent):`) | ✅ Clean MRO, zero duplication, exact same types |

**Anti-patterns (NEVER):**
- `from flext_meltano import FlextMeltanoModels as m_meltano` — duplicate alias
- `class Meltano: SingerSchemaMessage = FlextMeltanoModels.Meltano.SingerSchemaMessage` — not valid as type
- Inheriting `FlextModels` directly when parent project namespaces are needed

## Instructions
- Use existing type var definitions before introducing new generic parameters.
- Prefer `FlextTypes` aliases (`GeneralValueType`, maps, scalar groups) for public contracts.
- Ensure downstream users (`result.py`, `settings.py`, `protocols.py`) still type-check.
- When creating a new project that depends on another FLEXT project's types, ALWAYS inherit the parent facade class in your models/protocols/etc.

```python
T = TypeVar("T")
T_Settings = TypeVar("T_Settings", bound=BaseSettings)

type GeneralValueType = str | int | float | bool | datetime | None | BaseModel | Path | Sequence[GeneralValueType] | Mapping[str, GeneralValueType]
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

Why good: focused alias with clear semantic purpose.

Bad:

```python
JsonPrimitive = object
```

Why bad: overly broad type erases constraints and degrades static analysis.

## Verification

Make gates:

- `make check PROJECT=flext-core CHECK_GATES=type` — type-check validates type system contracts
- `make check PROJECT=flext-core` — full lint + type + format + security
- `make test PROJECT=flext-core` — type contracts exercised by test suite

Pattern checks:

- `rg -n "TypeVar\(|type GeneralValueType|class FlextTypes|JsonPrimitive" flext-core/src/flext_core/typings.py`
- `rg -n "class FlextResult|type .*=" flext-core/src/flext_core/result.py`
- `rg -n "T_Settings|BaseSettings" flext-core/src/flext_core/settings.py flext-core/src/flext_core/typings.py`
