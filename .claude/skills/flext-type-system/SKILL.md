---
name: flext-type-system
description: Canonical FLEXT type-system map for aliases, generics, result interplay, and settings contracts. Use when changing shared typing primitives.
---

# Flext Type System

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

## Instructions
- Use existing type var definitions before introducing new generic parameters.
- Prefer `FlextTypes` aliases (`GeneralValueType`, maps, scalar groups) for public contracts.
- Ensure downstream users (`result.py`, `settings.py`, `protocols.py`) still type-check.

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
- `rg -n "TypeVar\(|type GeneralValueType|class FlextTypes|JsonPrimitive" flext-core/src/flext_core/typings.py`
- `rg -n "class FlextResult|type .*=" flext-core/src/flext_core/result.py`
- `rg -n "T_Settings|BaseSettings" flext-core/src/flext_core/settings.py flext-core/src/flext_core/typings.py`
