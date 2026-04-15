---

name: pydantic-v2-patterns
description: Advanced Pydantic v2 implementation patterns for FLEXT: discriminated unions, computed_field, PrivateAttr, validators, model_config, and ConfigDict governance across 33 projects. Use when implementing complex model hierarchies, chaining validators, resolving pydantic v1-to-v2 migration errors, or writing FLEXT-compliant models.
triggers:
  - implementing complex model hierarchies
  - chaining validators in a Pydantic v2 model
  - resolving Pydantic v1-to-v2 migration errors
  - writing FLEXT-compliant discriminated union models
  - using computed_field across multiple projects
  - implementing ConfigDict governance patterns
  - writing PrivateAttr or model_post_init logic
  - auditing 33-project Pydantic consistency

---

<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [Validators](#validators)
  - [Computed Fields](#computed-fields)
  - [Discriminated Unions](#discriminated-unions)
  - [Serializers](#serializers)
  - [Strict Mode](#strict-mode)
  - [TypeAdapter](#typeadapter)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

# Pydantic v2 Patterns

**Reviewed**: 2026-02-17 | **Scope**: Implementation patterns that complement `lib-pydantic-v2`

## Scope

- Pattern-level guidance for advanced Pydantic v2 usage in FLEXT.
- Companion to `lib-pydantic-v2` (rules/API policy); this skill focuses on implementation depth.
- Feature families covered:
  - Validators
  - Computed Fields
  - Discriminated Unions
  - Serializers
  - Strict Mode
  - TypeAdapter
- Repository anchors:
  - `flext-core/src/flext_core/_models/base.py`
  - `flext-core/src/flext_core/_models/settings.py`
  - `flext-core/src/flext_core/_utilities/validation.py`
  - `flext-core/src/flext_core/models.py`
  - `flext-core/src/flext_core/service.py`
  - `flext-core/src/flext_core/registry.py`
  - `flext-ldif/src/flext_ldif/_models/base.py`
  - `flext-cli/tests/conftest.py`
  - `flext-tap-oracle-oic/src/flext_tap_oracle_oic/models.py`

## References

- `AGENTS.md` — canonical governance source
- `.claude/skills/lib-pydantic-v2/SKILL.md`
- `.claude/skills/skill-format-universal/SKILL.md`
- `flext-core/src/flext_core/_models/base.py`
- `flext-core/src/flext_core/_models/settings.py`
- `flext-core/src/flext_core/_utilities/validation.py`
- `flext-core/src/flext_core/models.py`
- `flext-core/src/flext_core/service.py`
- `flext-core/src/flext_core/registry.py`
- `flext-ldif/src/flext_ldif/_models/base.py`
- `flext-cli/tests/conftest.py`
- `flext-tap-oracle-oic/src/flext_tap_oracle_oic/models.py`
- <https://docs.pydantic.dev/latest/concepts/validators/>
- <https://docs.pydantic.dev/latest/concepts/serialization/>
- <https://docs.pydantic.dev/latest/concepts/unions/>
- <https://docs.pydantic.dev/latest/concepts/strict_mode/>

## Rules

- Keep policy-level mandates in `lib-pydantic-v2`; keep procedural depth here.
- Reuse repository-proven patterns before inventing new abstractions.
- Keep validation phases explicit:
  - `field_validator(..., mode="before")` for normalization/coercion.
  - `field_validator(..., mode="after")` for typed semantic checks.
  - `model_validator(mode="after")` for cross-field invariants.
- Keep computed fields pure and deterministic.
- Keep serializers explicit and scope-limited.
- Use discriminated unions for runtime polymorphism; always include literal tags.
- Use strict models for boundaries and contracts; use lenient models only where dynamic inputs are expected.
- Use TypeAdapter for non-model types and dynamic/runtime payload validation.
- Keep error messages stable enough for tests and operations.
- Avoid repeating v1 migration anti-pattern content already documented in `lib-pydantic-v2`.
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO. `Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for settings — standalone `*Config` classes TOTALLY FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@field_validator`/`@model_validator` — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), settings from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `PrivateAttr` — never bare `self._x`. Nested classes MAY have business methods but ALL properties use `Field()`/`PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. Boolean/status fields use canonical names such as `success`, `failure`, `expired`, `healthy`, or `configured`. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **AXIOMATIC**: Compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED on contact.


## Instructions

> Advanced patterns are documented in [references/patterns-detail.md](references/patterns-detail.md). Load it for the full pattern library.

Pattern families available in references:
- **Validators**: `@field_validator`, `@model_validator`, reusable `Annotated` aliases with constraints
- **Computed fields**: `@computed_field` with `cached_property` semantics and FLEXT examples
- **Discriminated unions**: `Discriminator()` with Literal tags for polymorphic parsing
- **Serializers**: `@field_serializer`, `@model_serializer`, `model_dump()` control
- **Strict mode**: `model_config = ConfigDict(strict=True)` patterns
- **TypeAdapter**: caching strategy, `ClassVar[TypeAdapter]`, performance patterns

## Workflow

1. Read `lib-pydantic-v2` for policy constraints and banned patterns.
2. Select the needed family in this skill (validators, computed fields, unions, serializers, strict mode, TypeAdapter).
3. Locate nearest repository anchor and copy structure from real implementation.
4. Adapt names/types while preserving validation phase semantics.
5. Add focused tests for parse failures, invariant failures, computed outputs, and serializer output.
6. Run grep-based checks for consistency and forbidden drift.
7. Keep this skill and `lib-pydantic-v2` complementary.

## Examples

Good:

```python
from typing import Self
from pydantic import BaseModel, Field, field_validator, model_validator


class Window(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    label: str

    @field_validator("label", mode="before")
    @classmethod
    def normalize_label(cls, value) -> str:
        if not isinstance(value, str):
            raise TypeError("label must be str")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("label cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.end < self.start:
            raise ValueError("end must be >= start")
        return self
```

Why good: normalization and invariants are separated, deterministic, and easy to test.

Bad:

```python
from pydantic import BaseModel, field_validator


class Window(BaseModel):
    start: int
    end: int

    @field_validator("start", mode="before")
    @classmethod
    def mixed_logic(cls, value):
        # Coercion + unrelated global side effects + hidden invariant checks
        return int(value)
```

Why bad: cross-field and side-effect logic in a field validator makes behavior brittle.

Good:

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Discriminator


class Ok(BaseModel):
    kind: Literal["ok"] = "ok"
    value: int


class Err(BaseModel):
    kind: Literal["err"] = "err"
    error: str


Response = Annotated[Ok | Err, Discriminator("kind")]
```

Why good: explicit discriminator enables deterministic union parsing.

Bad:

```python
from pydantic import BaseModel


class MaybeResult(BaseModel):
    value: int | None = None
    error: str | None = None
```

Why bad: ambiguous shape with no explicit polymorphic contract.

## Verification

- `ls -1 .claude/skills/pydantic-v2-patterns/SKILL.md`
- `wc -l .claude/skills/pydantic-v2-patterns/SKILL.md`
- `rg -n "^name:|^description:" .claude/skills/pydantic-v2-patterns/SKILL.md`
- `for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .claude/skills/pydantic-v2-patterns/SKILL.md || echo "MISSING $s"; done`
- `rg -n "field_validator\(|model_validator\(|computed_field|field_serializer|Discriminator\(|TypeAdapter|strict=True" flext-core/src/flext_core/_models/base.py flext-core/src/flext_core/_models/settings.py flext-core/src/flext_core/_utilities/validation.py flext-core/src/flext_core/models.py flext-core/src/flext_core/service.py flext-core/src/flext_core/registry.py flext-ldif/src/flext_ldif/_models/base.py flext-cli/tests/conftest.py flext-tap-oracle-oic/src/flext_tap_oracle_oic/models.py`
