# Typing Consolidation Plan 0.12.1

**Goal**: Centralize Pydantic v2 JSON typing natively in flext-core, eliminate all recursion, zero type narrowing bloat

**Status**: In Progress | **Baseline**: flext-core/cli/infra = 0 pyrefly errors

## Phase 1: Centralized JSON Type Hierarchy (Core-First)

### 1.1 Native Pydantic v2 RootModel-based JSON types in `flext-core/_typings/base.py`

**Current**: Multiple JSON aliases scattered (`t.JsonValue`, `t.JsonValue`, `t.Scalar`)
**Target**: Single canonical RootModel-based JSON contract

```python
# Canonical Pydantic v2 JSON types (native serialization)
class JsonLiteral(RootModel[str | int | float | bool | None]):
    """Atomic JSON value."""


class JsonValue(RootModel[JsonLiteral | dict[str, "JsonValue"] | list["JsonValue"]]):
    """Full recursive JSON (Pydantic native)."""


class ConfigMap(RootModel[t.JsonMapping]):
    """Configuration mapping (Pydantic native)."""


# Deduplication: all former t.JsonValue, t.Scalar, t.Primitives vanish
```

### 1.2 Complete Container elimination in favor of JSON hierarchy

- Remove `t.JsonValue` alias (replaced by `JsonValue`)
- Remove `t.Scalar` (replaced by `JsonLiteral`)
- Remove `t.Primitives` (replaced by inline `str | int | float | bool | None`)
- Remove `t.RuntimeData` composition

### 1.3 TypeAdapter consolidation for all JSON validation

```python
# Single canonical validators per type
JSON_ADAPTER: ClassVar[TypeAdapter[JsonValue]] = TypeAdapter(JsonValue)
CONFIG_MAP_ADAPTER: ClassVar[TypeAdapter[ConfigMap]] = TypeAdapter(ConfigMap)
```

## Phase 2: Cascade Adoption (cli → infra → all projects)

### 2.1 flext-cli: Replace all `t.JsonPayload` with native `JsonValue`

### 2.2 flext-infra: Replace all `t.InfraValue` with native `JsonValue`

### 2.3 All 34 projects: Update type signatures from scattered `t.*` to canonical aliases

## Phase 3: Result/Error/Model Alignment

### 3.1 Result[T] where T ∈ {JsonValue, ConfigMap, BaseModel, Scalar}

### 3.2 Error carriers: All use `error_data: JsonValue | None`

### 3.3 Settings: All use `ConfigMap` for nested config

## Evidence Checklist

- [ ] Phase 1.1: RootModel JSON types created + TypeAdapter validators cached
- [ ] Phase 1.2: All Container/Scalar/Primitives removed from typings.py
- [ ] Phase 1.3: All 34 projects pass pyrefly with 0 errors
- [ ] Phase 2, 2.1-2.3: cli/infra/all adopt new hierarchy
- [ ] Phase 3: Result/Settings/Error all aligned
- [ ] Workspace validation: No import cycles, 0 pyrefly errors

---

**Implementation Start**: Now
**Current User**: Principal Software Engineer Mode
