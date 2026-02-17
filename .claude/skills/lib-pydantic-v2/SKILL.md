---
name: lib-pydantic-v2
description: Pydantic v2 model, validation, and serialization patterns used across FLEXT. Use when creating models, adding validators, using ConfigDict, TypeAdapter, or model_validate/model_dump.
---

# Lib Pydantic V2 — Models, Validators, and Adapters

## Scope

- `flext-core/src/flext_core/settings.py` — FlextSettings (BaseSettings + SettingsConfigDict)
- `flext-core/src/flext_core/_models/settings.py` — nested config models with field_validator/model_validator
- `flext-core/src/flext_core/_utilities/validation.py` — TypeAdapter utilities, validation helpers
- `flext-core/src/flext_core/typings.py` — RootModel containers (Dict, ConfigMap, etc.)
- `flext-grpc/src/flext_grpc/models.py` — gRPC domain models with computed_field
- All subproject `settings.py` files

## References

- <https://docs.pydantic.dev/latest/> — official Pydantic v2 docs
- `flext-core/pyproject.toml` — pins `pydantic>=2.12.3`, `pydantic-core>=2.41.4`

## Rules

- **Only v2 API**: `model_validate`, `model_dump`, `model_dump_json`, `ConfigDict`, `field_validator`, `model_validator`, `computed_field`.
- **Never** use v1 API: `@validator`, `.dict()`, `.json()`, `class Config:`, `from_orm`, `orm_mode`.
- **Critical violation**: never use `model_rebuild(...)` to patch unresolved annotations.
- Models must resolve all references at definition time via explicit imports/type aliases and stable declaration order.
- Use `scripts/validation/enforce_pydantic_v2_skill.sh` as enforcement gate and `scripts/validation/fix_pydantic_v2_violations.sh` for safe codemod fixes.
- Use `TypeAdapter` for validating non-model types — never ad-hoc casting with `isinstance` chains.
- Set `ConfigDict(extra="forbid")` on strict boundary models, `extra="ignore"` on flexible internal models.
- Use `Field(...)` with explicit `description=` on all public model fields.

## Instructions

### Core Model Patterns

**BaseModel with ConfigDict** (every model in FLEXT):

```python
from pydantic import BaseModel, ConfigDict, Field

class ProcessingRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",            # strict at boundaries
    )
    name: str = Field(..., description="Request name")
    timeout: int = Field(default=30, ge=1, le=300)
```

**field_validator** (mode="before" or "after"):

```python
from pydantic import field_validator

class RetryConfiguration(BaseModel):
    retry_on_status_codes: list[int] = Field(default_factory=list)

    @field_validator("retry_on_status_codes", mode="after")
    @classmethod
    def validate_status_codes(cls, v: list[int]) -> list[int]:
        return [c for c in v if 400 <= c < 600]
```

**model_validator** (mode="after" for cross-field validation):

```python
from pydantic import model_validator

class BatchProcessingConfig(BaseModel):
    batch_size: int = Field(default=100)
    max_workers: int = Field(default=4)

    @model_validator(mode="after")
    def validate_batch_config(self) -> Self:
        if self.batch_size < self.max_workers:
            msg = "batch_size must be >= max_workers"
            raise ValueError(msg)
        return self
```

**computed_field** (derived read-only properties):

```python
from pydantic import computed_field

class GrpcModel(BaseModel):
    host: str
    port: int

    @computed_field
    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"
```

### TypeAdapter for Non-Model Validation

From `flext-core/src/flext_core/_utilities/validation.py`:

```python
from pydantic import TypeAdapter as PydanticTypeAdapter

# Validate arbitrary values at runtime without a full model
adapter = PydanticTypeAdapter(list[int])
validated = adapter.validate_python([1, 2, 3])
```

The `FlextUtilitiesValidation` class centralizes TypeAdapter usage for:

- `_normalize_pydantic_value()` — dynamic type normalization
- Network validators (`validate_uri`, `validate_port_number`, `validate_hostname`)
- String/Numeric validators in nested `Validation` groups

### RootModel Containers (from `typings.py`)

```python
class Dict(RootModel[dict[str, GeneralValueType]]):
    root: dict[str, GeneralValueType]

class ConfigMap(RootModel[dict[str, GeneralValueType]]):
    root: dict[str, GeneralValueType]

class ServiceMap(RootModel[dict[str, GeneralValueType]]):
    root: dict[str, GeneralValueType]
```

Used via `t.ConfigMap`, `t.ServiceMap`, `t.ErrorMap`, `t.FactoryMap`, `t.ResourceMap`.

### Forward Reference Discipline (no model_rebuild)

- Import referenced symbols before model declaration.
- Keep type aliases and model dependencies declared before use.
- Use postponed annotations (`from __future__ import annotations`) and real symbols in scope.
- Do not rely on `_types_namespace` patching.

### Serialization Patterns

```python
# ✓ v2 serialization
data = model.model_dump()                        # → dict
json_str = model.model_dump_json()               # → JSON string
schema = Model.model_json_schema()               # → JSON Schema dict

# ✓ v2 deserialization
instance = Model.model_validate(raw_dict)        # from dict
instance = Model.model_validate_json(json_bytes) # from JSON
```

## Workflow

1. Find nearest existing model in the same subproject for pattern reference
2. Use `ConfigDict` (never `class Config:`) with explicit `extra=` and `validate_assignment=`
3. Add `Field(description=...)` on all public fields
4. Use `@field_validator` (not `@validator`) with `mode=` parameter
5. Use `@model_validator(mode="after")` for cross-field validation
6. Run `rg "@validator\(" --glob "**/*.py"` to verify no v1 validators
7. Run `rg "model_rebuild\(" --glob "**/*.py"` and keep zero hits in production and tests
8. Run pydantic skill automation:

```bash
scripts/validation/fix_pydantic_v2_violations.sh --root . --dry-run
scripts/validation/enforce_pydantic_v2_skill.sh --mode baseline --root .
scripts/validation/enforce_pydantic_v2_skill.sh --mode strict --root .
```

## Examples

### Good: FlextSettings model_config

```python
model_config = SettingsConfigDict(
    env_prefix=c.Platform.ENV_PREFIX,          # "FLEXT_"
    env_nested_delimiter=c.Platform.ENV_NESTED_DELIMITER,
    env_file=u.resolve_env_file(),
    env_file_encoding=c.Utilities.DEFAULT_ENCODING,
    case_sensitive=False,
    extra=c.ModelConfig.EXTRA_IGNORE,
    validate_assignment=True,
)
```

### Good: FlextResult.from_validation integration

```python
result = FlextResult.from_validation(raw_data, UserModel)
# Uses model.model_validate(data) internally → r[UserModel]
```

### Bad: v1-style validator

```python
# ✗ WRONG — Pydantic v1 API
@validator("name", pre=True)
def validate_name(cls, v):
    return v.strip()
```

**Why bad**: `@validator` is deprecated in v2. Use `@field_validator("name", mode="before")` with `@classmethod`.

### Bad: .dict() / .json()

```python
# ✗ WRONG — v1 serialization
data = model.dict()     # → use model.model_dump()
text = model.json()     # → use model.model_dump_json()
```

### Bad: class Config instead of ConfigDict

```python
# ✗ WRONG — v1 configuration style
class MyModel(BaseModel):
    class Config:
        extra = "forbid"
```

**Why bad**: `class Config:` is v1 pattern. Use `model_config = ConfigDict(extra="forbid")`.

### Bad: model_rebuild patching

```python
_types_namespace = {"t": t}
MyModel.model_rebuild(_types_namespace=_types_namespace)
```

**Why bad**: this hides invalid declaration order and unresolved annotations. Fix the model graph so all referenced symbols exist at definition time.

### Good: all references defined before model declaration

```python
from __future__ import annotations

from flext_core import t

class QueryModel(m.Query):
    filters: t.Dict
```

**Why good**: referenced types are available in module scope; no post-definition rebuild step is required.

## Subproject Usage Map

| Subproject | Key Files | Pattern |
| ------------ | ----------- | --------- |
| `flext-core` | `settings.py`, `_models/settings.py`, `typings.py` | SettingsConfigDict, ConfigDict, field_validator, model_validator, RootModel |
| `flext-grpc` | `models.py`, `settings.py` | BaseModel + computed_field, SettingsConfigDict |
| `flext-auth` | `settings.py`, `models.py` | SettingsConfigDict, ConfigDict |
| `flext-cli` | `settings.py`, `file_tools.py` | SettingsConfigDict, yaml → model validation |
| `flext-ldif` | `settings.py`, `_models/settings.py` | SettingsConfigDict, ConfigDict |
| `flext-api` | `settings.py` | SettingsConfigDict |
| `flext-web` | `settings.py` | SettingsConfigDict |
| `flext-meltano` | `project_service.py` | yaml.safe_dump + BaseModel patterns |
| `flext-quality` | `utilities.py`, `rules/loader.py` | yaml + model validation |
| `flext-tap-*`, `flext-target-*` | `settings.py` | SettingsConfigDict |

## Verification

```bash
# Confirm v2 patterns in use
rg -n "ConfigDict|SettingsConfigDict|field_validator|model_validator|computed_field" --glob "**/*.py" flext-core flext-grpc flext-auth

# Confirm TypeAdapter usage
rg -n "TypeAdapter" --glob "**/*.py" flext-core/src/

# Detect v1 anti-patterns (should return zero hits in src/)
rg -n "@validator\(" --glob "**/*.py" flext-core/src/ flext-grpc/src/
rg -n "\.dict\(\)|\.json\(\)" --glob "**/*.py" flext-core/src/
rg -n "class Config:" --glob "**/*.py" flext-core/src/

# Detect critical rebuild anti-pattern (should return zero hits)
rg -n "model_rebuild\(" --glob "**/*.py" flext-core/src/ flext-core/tests/ flext-auth/src/ flext-api/src/ flext-cli/src/ flext-grpc/src/ flext-ldif/src/ flext-web/src/

# Skill automation gate + autofix
scripts/validation/fix_pydantic_v2_violations.sh --root . --dry-run
scripts/validation/enforce_pydantic_v2_skill.sh --mode baseline --root .

# Confirm dependency version
rg "pydantic>=" flext-core/pyproject.toml
```

<!-- AUTOMATION MARKERS (machine-readable, do not edit) -->
<!-- ASTGREP_SCAN_PACK: scripts/validation/ast-grep-pydantic-v2.yml -->
<!-- ASTGREP_FIX_PACK: scripts/validation/ast-grep-pydantic-v2.yml -->
<!-- AUTOFIX_MODE: safe -->
