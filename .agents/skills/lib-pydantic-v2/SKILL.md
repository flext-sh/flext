---
name: lib-pydantic-v2
description: Pydantic v2 model, validation, and serialization patterns used across FLEXT. Use when creating models, adding validators, using ConfigDict, TypeAdapter, or model_validate/model_dump.

---

# Lib Pydantic V2 — Models, Validators, and Adapters

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `flext-core/src/flext_core/settings.py` — FlextSettings (BaseSettings + ConfigDict)
- `flext-core/src/flext_core/models/settings.py` — nested settings models with u.field_validator/u.model_validator
- `flext-core/src/flext_core/_utilities/validation.py` — TypeAdapter utilities, validation helpers
- `flext-core/src/flext_core/typings.py` — RootModel containers (Dict, ConfigMap, etc.)
- `flext-grpc/src/flext_grpc/models.py` — gRPC domain models with u.computed_field
- All subproject `settings.py` files

## References

- `AGENTS.md` — canonical governance source
- <https://docs.pydantic.dev/latest/> — official Pydantic v2 docs
- `flext-core/pyproject.toml` — pins `pydantic>=2.12.3`, `pydantic-core>=2.41.4`

## Rules

- **Consume Pydantic base classes via `m` facade**: `m.ArbitraryTypesModel`, `m.Value`, `m.Command`, `m.Query`, `m.StrictModel`, etc. are flat on `m`.
- **Pydantic decorators and utilities** are accessed via flext_core aliases: `u.Field`, `m.ConfigDict`, `u.field_validator`, `u.model_validator`, `u.computed_field`.
- **Only v2 API**: `model_validate`, `model_dump`, `model_dump_json`, `ConfigDict`, `u.field_validator`, `u.model_validator`, `u.computed_field`.
- **Never** use v1 API: `@validator`, `.dict()`, `.json()`, `class Config:`, `from_orm`, `orm_mode`.
- **Critical violation**: never use `model_rebuild(...)` to patch unresolved annotations.
- Models must resolve all references at definition time via explicit imports/type aliases and stable declaration order.
- Use `make val` as enforcement gate (with `PROJECT`/`PROJECTS` selectors). Auto-fix path is `make val FIX=1`.
- Use `TypeAdapter` from pydantic for validating non-model types — never ad-hoc casting with `isinstance` chains.
- Set `ConfigDict(extra="forbid")` on strict boundary models, `extra="ignore"` on flexible internal models.
- Use `u.Field(description=...)` with explicit `description=` on all public model fields.
- All model classes defined as nested classes within MRO facade hierarchy (e.g., `FlextProjectModels.Domain.ModelName`).

## Instructions

### Core Model Patterns

**Model with ConfigDict** (base class from `m`, config from `c`, decorators from `u`):

```python
from __future__ import annotations

from typing import Annotated

from flext_core import c, m, t, u


class FlextProcessingModels(m):
    """One facade per module with nested domain classes."""

    class Processing:
        """Domain namespace — nested models here."""

        class Request(m.ArbitraryTypesModel):
            """Request model with strict boundary config."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                validate_assignment=True,
                use_enum_values=True,
                extra="forbid",
            )

            name: Annotated[t.NonEmptyStr, u.Field(description="Request name")]
            timeout: Annotated[
                int, u.Field(default=30, ge=1, le=300, description="Timeout seconds")
            ]
```

**u.field_validator** (from `u`, mode="before" or "after"):

```python
from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence
from typing import Annotated

from flext_core import m, u


class FlextValidationModels(m):
    """Facade with field-level validation example."""

    class Validation:
        """Validation domain namespace."""

        class RetryConfig(m.ArbitraryTypesModel):
            """Retry configuration with status code filter."""

            codes: Annotated[
                t.SequenceOf[int],
                u.Field(default_factory=list, description="HTTP status codes to retry"),
            ]

            @u.field_validator("codes", mode="after")
            @classmethod
            def filter_codes(cls, v: t.SequenceOf[int]) -> t.SequenceOf[int]:
                """Keep only 4xx/5xx codes."""
                return [code for code in v if 400 <= code < 600]
```

**u.model_validator** (from `u`, mode="after"):

```python
from __future__ import annotations

from typing import Annotated, Self

from flext_core import m, u


class FlextBatchModels(m):
    """Facade with cross-field model validation."""

    class Batch:
        """Batch processing namespace."""

        class Config(m.ArbitraryTypesModel):
            """Batch processing configuration."""

            batch_size: Annotated[
                int, u.Field(default=100, description="Items per batch")
            ]
            max_workers: Annotated[
                int, u.Field(default=4, description="Parallel workers")
            ]

            @u.model_validator(mode="after")
            def validate_batch(self) -> Self:
                """batch_size must be >= max_workers."""
                if self.batch_size < self.max_workers:
                    msg = "batch_size must be >= max_workers"
                    raise ValueError(msg)
                return self
```

**u.computed_field** (from `u`):

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, t, u


class FlextGrpcModels(m):
    """Facade with computed field example."""

    class Grpc:
        """gRPC domain namespace."""

        class Server(m.BaseModel):
            """gRPC server config with computed endpoint."""

            host: Annotated[t.NonEmptyStr, u.Field(description="Server host")]
            port: Annotated[int, u.Field(description="Server port")]

            @u.computed_field
            def endpoint(self) -> str:
                """Computed endpoint from host:port."""
                return f"{self.host}:{self.port}"
```

### TypeAdapter for Non-Model Validation

From `flext-core/src/flext_core/_utilities/validation.py`:

```python
from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence

from flext_core import m

adapter = m.TypeAdapter(Sequence[int])
validated = adapter.validate_python([1, 2, 3])
```

The `FlextUtilitiesValidation` class centralizes TypeAdapter usage for dynamic type normalization, network validators, and string/numeric validators.

### RootModel Containers (from `typings.py`)

```python
from __future__ import annotations

from collections.abc import Mapping

from flext_core import m


class StringMap(m.RootModel[t.StrMapping]):
    """RootModel container for string-to-string mappings."""

    root: t.StrMapping


class IntMap(m.RootModel[t.IntMapping]):
    """RootModel container for string-to-int mappings."""

    root: t.IntMapping
```

Used via explicit domain models and facade exports (`m.*`) rather than broad container aliases.

### Forward Reference Discipline (no model_rebuild)

- `model_rebuild()` is a critical architecture violation — FORBIDDEN.
- Import referenced symbols before model declaration.
- Keep type aliases and model dependencies declared before use.
- Use postponed annotations (`from __future__ import annotations`) and real symbols in scope.
- If a circular dependency seems to require `model_rebuild`, use Protocol-based decoupling or move models to a lower tier.

### Serialization Patterns

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, t, u


class DemoModel(m.ArbitraryTypesModel):
    """Model for serialization examples."""

    name: Annotated[t.NonEmptyStr, u.Field(description="Name")]


# v2 serialization
model = DemoModel(name="test")
data = model.model_dump()
json_str = model.model_dump_json()
schema = DemoModel.model_json_schema()

# v2 deserialization
instance = DemoModel.model_validate({"name": "test"})
instance_json = DemoModel.model_validate_json(b'{"name": "test"}')
```

## Workflow

1. Find nearest existing model in the same subproject for pattern reference
2. Use `ConfigDict` (never `class Config:`) with explicit `extra=` and `validate_assignment=`
3. Add `u.Field(description=...)` on all public fields
4. Use `@u.field_validator` (not `@validator`) with `mode=` parameter
5. Use `@u.model_validator(mode="after")` for cross-field validation
6. Run `rg "@validator\(" --glob "**/*.py"` to verify no v1 validators
7. Run `rg "model_rebuild\(" --glob "**/*.py"` and keep zero hits in production and tests
8. Run standardized validation automation:

```bash
make val PROJECT=flext-core
make val PROJECT=flext-core FIX=1
```

## Examples

### Good: Model consumed via `m` base class with MRO nesting

```python
from __future__ import annotations

from typing import Annotated

from flext_core import c, m, t, u


class FlextProcessingWorkflow(m):
    """One facade per module with nested domain namespace."""

    class Processing:
        """Workflow domain namespace."""

        class Config(m.ArbitraryTypesModel):
            """Workflow config with ConfigDict and u.field_validator."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                extra="forbid",
                validate_assignment=True,
            )

            name: Annotated[t.NonEmptyStr, u.Field(description="Workflow name")]
            max_retries: Annotated[
                int, u.Field(default=3, ge=0, description="Max retries")
            ]

            @u.field_validator("name", mode="before")
            @classmethod
            def strip_name(cls, v: str) -> str:
                """Normalize whitespace before validation."""
                return v.strip()
```

### Bad: v1-style validator

```text
from pydantic import validator

class _BadExample:
    @validator("name", pre=True)
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()
```

**Why bad**: `@validator` (v1) is deprecated. Use `@u.field_validator("name", mode="before")` with `@classmethod`.

### Bad: .dict() / .json()

```text
model = DemoModel(name="test")
data = model.dict()
text = model.json()
```

### Bad: class Config instead of ConfigDict

```text
class MyModel(m.BaseModel):
    class Config:
        extra = "forbid"
```

**Why bad**: `class Config:` is v1 pattern. Use `model_config = ConfigDict(extra="forbid")`.

### Bad: model_rebuild patching

```text
class MyModel(m.ArbitraryTypesModel):
    filters: Annotated[t.NonEmptyStr, u.Field(description="Query filter")]

MyModel.model_rebuild()
```

**Why banned**: `model_rebuild()` hides invalid declaration order. Fix the model graph so all symbols exist at definition time.

### Good: all references defined before model declaration

```python
from __future__ import annotations

from typing import Annotated

from flext_core import m, t, u


class QueryModel(m.ArbitraryTypesModel):
    """References resolved at definition time — no rebuild needed."""

    filters: Annotated[t.NonEmptyStr, u.Field(description="Query filter expression")]
```

**Why good**: referenced types are available in module scope; no post-definition rebuild step required.

## Subproject Usage Map

| Subproject                      | Key Files                                          | Pattern                                                                   |
| ------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------- |
| `flext-core`                    | `settings.py`, `models/settings.py`, `typings.py` | ConfigDict, ConfigDict, u.field_validator, u.model_validator, RootModel |
| `flext-grpc`                    | `models.py`, `settings.py`                         | BaseModel + u.computed_field, ConfigDict                                  |
| `flext-auth`                    | `settings.py`, `models.py`                         | ConfigDict, ConfigDict                                                    |
| `flext-cli`                     | `settings.py`, `file_tools.py`                     | ConfigDict, yaml → model validation                                       |
| `flext-ldif`                    | `settings.py`, `models/settings.py`               | ConfigDict, ConfigDict                                                    |
| `flext-api`                     | `settings.py`                                      | ConfigDict                                                                |
| `flext-web`                     | `settings.py`                                      | ConfigDict                                                                |
| `flext-meltano`                 | `project_service.py`                               | yaml.safe_dump + BaseModel patterns                                       |
| `flext-quality`                 | `utilities.py`, `rules/loader.py`                  | yaml + model validation                                                   |
| `flext-tap-*`, `flext-target-*` | `settings.py`                                      | ConfigDict                                                                |

## Verification

```bash
# Confirm v2 patterns in use
rg -n "ConfigDict|ConfigDict|u.field_validator|u.model_validator|u.computed_field" --glob "**/*.py" flext-core flext-grpc flext-auth

# Confirm TypeAdapter usage
rg -n "TypeAdapter" --glob "**/*.py" flext-core/src/

# Detect v1 anti-patterns (should return zero hits in src/)
rg -n "@validator\(" --glob "**/*.py" flext-core/src/ flext-grpc/src/
rg -n "\.dict\(\)|\.json\(\)" --glob "**/*.py" flext-core/src/
rg -n "class Config:" --glob "**/*.py" flext-core/src/

# Detect critical rebuild anti-pattern (should return zero hits)
rg -n "model_rebuild\(" --glob "**/*.py" flext-core/src/ flext-core/tests/ flext-auth/src/ flext-api/src/ flext-cli/src/ flext-grpc/src/ flext-ldif/src/ flext-web/src/

# Skill automation gate
make val PROJECT=flext-core
make val PROJECT=flext-core FIX=1

# Confirm dependency version
rg "pydantic>=" flext-core/pyproject.toml
```

<!-- AUTOMATION: Managed by scripts/core/skill_validate.py via .agents/skills/lib-pydantic-v2/rules.yml -->
