---
name: pydantic-v2-patterns
description: Advanced Pydantic v2 implementation patterns for FLEXT: discriminated unions, computed_field, PrivateAttr, validators, model_config, and ConfigDict governance across 33 projects. Use when implementing complex model hierarchies, chaining validators, resolving pydantic v1-to-v2 migration errors, or writing FLEXT-compliant models.

---

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
class FlextPattern(m):
    class Domain:
        class Window(m.Value):
            start: int = u.Field(default=0, ge=0)
            end: int = u.Field(default=0, ge=0)
            label: t.NonEmptyStr

            @u.field_validator("label", mode="before")
            @classmethod
            def normalize_label(cls, value: t.RuntimeData) -> str:
                if not isinstance(value, str):
                    raise TypeError("label must be str")
                cleaned = value.strip()
                if not cleaned:
                    raise ValueError("label cannot be empty")
                return cleaned

            @u.model_validator(mode="after")
            def validate_window(self) -> Self:
                if self.end < self.start:
                    raise ValueError("end must be >= start")
                return self

        class ServiceBase(s[t.Dict]):
            pass

        class Service(ServiceBase):
            def validate(self, window: "FlextPattern.Domain.Window") -> p.Result[int]:
                return r[int].ok(window.end - window.start)
- Reuse repository-proven patterns before inventing new abstractions.
- Prefer alias-first consumption (`c`, `p`, `t`, `m`, `u`, and `s`) throughout — never mix direct pydantic imports.
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
- **Rule**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO. `Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for settings — standalone `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@field_validator`/`@model_validator` — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), settings from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `PrivateAttr` — never bare `self._x`. Nested classes MAY have business methods but ALL properties use `Field()`/`PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. Boolean/status fields use canonical names such as `success`, `failure`, `expired`, `healthy`, or `configured`. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **Rule**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **Rule**: Compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and compatibility aliases are FORBIDDEN. Legacy code is DELETED on contact.


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

### Good: Pydantic via `m` facade with MRO-nested validators

```python
from __future__ import annotations

from typing import Self

from flext_core import m, p, r, s, t, c


class FlextPatternModels(m):
    """Models inherit from m via MRO — all Pydantic via facade."""
    
    class Domain:
        class Window(m.BaseModel):
            """Window with validation phases separated."""
            model_config = m.ConfigDict(extra=c.EXTRA_FORBID)
            start: int = m.Field(default=0, ge=0, description="Window start")
            end: int = m.Field(default=0, ge=0, description="Window end")
            label: t.NonEmptyStr = m.Field(..., description="Label")

            # Phase 1: Normalize input before type coercion
            @m.field_validator("label", mode="before")
            @classmethod
            def normalize_label(cls, value: t.RuntimeData) -> str:
                if not isinstance(value, str):
                    raise TypeError("label must be str")
                return value.strip()

            # Phase 2: Cross-field validation after all fields coerced
            @m.model_validator(mode="after")
            def validate_window(self) -> Self:
                if self.end < self.start:
                    raise ValueError("end must be >= start")
                return self

            # Computed property (immutable derivation)
            @m.computed_field
            @property
            def width(self) -> int:
                return self.end - self.start


class FlextPatternServiceBase(s[t.Dict]):
    """Service base with DI support."""
    pass


class FlextPatternService(FlextPatternServiceBase):
    """Service consuming models via MRO paths."""
    
    def validate(self, window: FlextPatternModels.Domain.Window) -> p.Result[int]:
        """Validate and return window width."""
        return r[int].ok(window.width)  # Uses computed_field
```

Why good:
- ✅ **All Pydantic via `m`** — `m.BaseModel`, `m.Field`, `m.ConfigDict`, `m.field_validator`, `m.model_validator`, `m.computed_field`
- ✅ **MRO inheritance** — `FlextPatternModels(m)` → Domain.Window inherits Pydantic via facade
- ✅ **Validator phases separated** — normalize (before) → coerce → validate cross-fields (after)
- ✅ **Nested domain namespace** — `m.Domain.Window` preserved, not flattened
- ✅ **Service boundary** — receives typed models, returns result via `r[T]`

### Bad: Direct pydantic imports instead of via `m` facade

```python
# ✗ WRONG — importing from pydantic directly
from pydantic import BaseModel, field_validator, Field

class Window(BaseModel):
    start: int = Field(default=0)
    end: int = Field(default=0)

    @field_validator("start", mode="before")
    @classmethod
    def mixed_logic(cls, value):
        return int(value)
```

Why bad:
- Bypasses `m` facade — no centralized Pydantic governance
- Loses MRO composition — cannot inherit parent facades
- Prevents cross-field validation, computed fields through abstraction
- Breaks with architectural isolation (c/p/t/m/u contracts)

### Bad: Cross-field logic in field validator

```python
# ✗ WRONG — validator with side effects and unrelated logic
@m.field_validator("start", mode="before")
@classmethod
def mixed_logic(cls, value):
    # Coercion + side effects + hidden invariant checks all in one
    import logging
    logging.info(f"Validating {value}")  # Side effect!
    return int(value)
```

Why bad: side effects and cross-field logic in field validator makes behavior brittle and hard to test.

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
