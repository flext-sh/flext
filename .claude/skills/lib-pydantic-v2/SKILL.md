<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [Core Model Patterns](#core-model-patterns)
  - [TypeAdapter for Non-Model Validation](#typeadapter-for-non-model-validation)
  - [RootModel Containers (from `typings.py`)](#rootmodel-containers-from-typingspy)
  - [Forward Reference Discipline (no model_rebuild)](#forward-reference-discipline-no-modelrebuild)
  - [Serialization Patterns](#serialization-patterns)
- [Workflow](#workflow)
- [Examples](#examples)
  - [Good: FlextSettings model_config](#good-flextsettings-modelconfig)
  - [Good: r.from_validation integration](#good-flextresultfromvalidation-integration)
  - [Bad: v1-style validator](#bad-v1-style-validator)
  - [Bad: .dict() / .json()](#bad-dict-json)
  - [Bad: class Config instead of ConfigDict](#bad-class-config-instead-of-configdict)
  - [Bad: model_rebuild patching](#bad-modelrebuild-patching)
  - [Good: all references defined before model declaration](#good-all-references-defined-before-model-declaration)
- [Subproject Usage Map](#subproject-usage-map)
- [Verification](#verification)
<!-- TOC END -->

---

name: lib-pydantic-v2
description: Pydantic v2 model, validation, and serialization patterns used across FLEXT. Use when creating models, adding validators, using ConfigDict, TypeAdapter, or model_validate/model_dump.

---

# Lib Pydantic V2 — Models, Validators, and Adapters

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `flext-core/src/flext_core/settings.py` — FlextSettings (BaseSettings + SettingsConfigDict)
- `flext-core/src/flext_core/_models/settings.py` — nested config models with field_validator/model_validator
- `flext-core/src/flext_core/_utilities/validation.py` — TypeAdapter utilities, validation helpers
- `flext-core/src/flext_core/typings.py` — RootModel containers (Dict, ConfigMap, etc.)
- `flext-grpc/src/flext_grpc/models.py` — gRPC domain models with computed_field
- All subproject `settings.py` files

## References

- `AGENTS.md` — canonical governance source
- <https://docs.pydantic.dev/latest/> — official Pydantic v2 docs
- `flext-core/pyproject.toml` — pins `pydantic>=2.12.3`, `pydantic-core>=2.41.4`

## Rules

- **Only v2 API**: `model_validate`, `model_dump`, `model_dump_json`, `ConfigDict`, `field_validator`, `model_validator`, `computed_field`.
- **Never** use v1 API: `@validator`, `.dict()`, `.json()`, `class Config:`, `from_orm`, `orm_mode`.
- **Critical violation**: never use `model_rebuild(...)` to patch unresolved annotations.
- Models must resolve all references at definition time via explicit imports/type aliases and stable declaration order.
- Use `make validate` as enforcement gate (with `PROJECT`/`PROJECTS` selectors). Auto-fix path is `make validate FIX=1`.
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
        extra="forbid",  # strict at boundaries
    )
    name: str = Field(..., description="Request name")
    timeout: int = Field(default=30, ge=1, le=300)
```

**field_validator** (mode="before" or "after"):

```python
from pydantic import field_validator


class RetryConfiguration(BaseModel):
    retry_on_status_codes: Sequence[int] = Field(default_factory=list)

    @field_validator("retry_on_status_codes", mode="after")
    @classmethod
    def validate_status_codes(cls, v: Sequence[int]) -> Sequence[int]:
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
adapter = PydanticTypeAdapter(Sequence[int])
validated = adapter.validate_python([1, 2, 3])
```

The `FlextUtilitiesValidation` class centralizes TypeAdapter usage for:

- `_normalize_pydantic_value()` — dynamic type normalization
- Network validators (`validate_uri`, `validate_port_number`, `validate_hostname`)
- String/Numeric validators in nested `Validation` groups

### RootModel Containers (from `typings.py`)

```python
from flext_core import m


class Dict(RootModel[Mapping[str, m.Core.ValueModel]]):
    root: Mapping[str, m.Core.ValueModel]


class ConfigMap(RootModel[Mapping[str, m.Core.ConfigEntryModel]]):
    root: Mapping[str, m.Core.ConfigEntryModel]


class ServiceMap(RootModel[Mapping[str, m.Core.ServiceEntryModel]]):
    root: Mapping[str, m.Core.ServiceEntryModel]
```

Used via explicit domain models and facade exports (`m.*`) rather than broad container aliases.

### Forward Reference Discipline (no model_rebuild)

- **ABSOLUTELY FORBIDDEN**: `model_rebuild()` is a critical architecture violation.
- Import referenced symbols before model declaration.
- Keep type aliases and model dependencies declared before use.
- Use postponed annotations (`from **future** import annotations

from collections.abc import Mapping, Sequence`) and real symbols in scope.
- Do not rely on `_types_namespace` patching or post-definition rebuild.
- If a circular dependency seems to require `model_rebuild`, you MUST use **Protocol-based decoupling** or move the models to a lower foundation tier.

### Serialization Patterns

```python
# ✓ v2 serialization
data = model.model_dump()  # → dict
json_str = model.model_dump_json()  # → JSON string
schema = Model.model_json_schema()  # → JSON Schema dict

# ✓ v2 deserialization
instance = Model(raw_dict)  # from dict
instance = Model.model_validate_json(json_bytes)  # from JSON
```

## Workflow

1. Find nearest existing model in the same subproject for pattern reference
2. Use `ConfigDict` (never `class Config:`) with explicit `extra=` and `validate_assignment=`
3. Add `Field(description=...)` on all public fields
4. Use `@field_validator` (not `@validator`) with `mode=` parameter
5. Use `@model_validator(mode="after")` for cross-field validation
6. Run `rg "@validator\(" --glob "**/*.py"` to verify no v1 validators
7. Run `rg "model_rebuild\(" --glob "**/*.py"` and keep zero hits in production and tests
8. Run standardized validation automation:

```bash
make validate PROJECT=<name>
make validate PROJECT=<name> FIX=1
```

## Examples

### Good: FlextSettings model_config

```python
model_config = SettingsConfigDict(
    env_prefix=c.ENV_PREFIX,  # "FLEXT_"
    env_nested_delimiter=c.ENV_NESTED_DELIMITER,
    env_file=u.resolve_env_file(),
    env_file_encoding=c.DEFAULT_ENCODING,
    case_sensitive=False,
    extra=c.EXTRA_IGNORE,
    validate_assignment=True,
)
```

### Good: r.from_validation integration

```python
result = r.from_validation(raw_data, UserModel)
# Uses model(y → r[UserModel]
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
data = model.dict()  # → use model.model_dump()
text = model.json()  # → use model.model_dump_json()
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
MyModel.model_rebuild(
    _types_namespace=_types_namespace
)  # ❌ CRITICAL VIOLATION - BANNED
```

**Why banned**: `model_rebuild()` hides invalid declaration order and unresolved annotations. It is forbidden in all production, test, and script code. Fix the model graph so all referenced symbols exist at definition time or use structural typing (Protocols).

### Good: all references defined before model declaration

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_core import t


class QueryModel(m.Query):
    filters: t.Dict
```

**Why good**: referenced types are available in module scope; no post-definition rebuild step is required.

## Subproject Usage Map

| Subproject                      | Key Files                                          | Pattern                                                                     |
| ------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------- |
| `flext-core`                    | `settings.py`, `_models/settings.py`, `typings.py` | SettingsConfigDict, ConfigDict, field_validator, model_validator, RootModel |
| `flext-grpc`                    | `models.py`, `settings.py`                         | BaseModel + computed_field, SettingsConfigDict                              |
| `flext-auth`                    | `settings.py`, `models.py`                         | SettingsConfigDict, ConfigDict                                              |
| `flext-cli`                     | `settings.py`, `file_tools.py`                     | SettingsConfigDict, yaml → model validation                                 |
| `flext-ldif`                    | `settings.py`, `_models/settings.py`               | SettingsConfigDict, ConfigDict                                              |
| `flext-api`                     | `settings.py`                                      | SettingsConfigDict                                                          |
| `flext-web`                     | `settings.py`                                      | SettingsConfigDict                                                          |
| `flext-meltano`                 | `project_service.py`                               | yaml.safe_dump + BaseModel patterns                                         |
| `flext-quality`                 | `utilities.py`, `rules/loader.py`                  | yaml + model validation                                                     |
| `flext-tap-*`, `flext-target-*` | `settings.py`                                      | SettingsConfigDict                                                          |

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

# Skill automation gate
make validate PROJECT=<name>
make validate PROJECT=<name> FIX=1

# Confirm dependency version
rg "pydantic>=" flext-core/pyproject.toml
```

<!-- AUTOMATION: Managed by scripts/core/skill_validate.py via .claude/skills/lib-pydantic-v2/rules.yml -->
