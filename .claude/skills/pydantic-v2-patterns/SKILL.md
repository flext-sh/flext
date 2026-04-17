---
name: pydantic-v2-patterns
description: Advanced Pydantic v2 implementation patterns for FLEXT: discriminated unions, u.computed_field, u.PrivateAttr, validators, model_config, and ConfigDict governance across 33 projects. Use when implementing complex model hierarchies, chaining validators, resolving pydantic v1-to-v2 migration errors, or writing FLEXT-compliant models.

---

# Pydantic v2 Patterns

**Reviewed**: 2026-02-17 | **Scope**: Implementation patterns that complement `lib-pydantic-v2`

## Scope

- Pattern-level guidance for advanced Pydantic v2 usage in FLEXT.
- Companion to `lib-pydantic-v2` (rules/API policy); this skill focuses on implementation depth.
- Feature families covered:
  - Validators
  - Computed u.Fields
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
  - `u.field_validator(..., mode="before")` for normalization/coercion.
  - `u.field_validator(..., mode="after")` for typed semantic checks.
  - `u.model_validator(mode="after")` for cross-field invariants.
- Keep computed fields pure and deterministic.
- Keep serializers explicit and scope-limited.
- Use discriminated unions for runtime polymorphism; always include literal tags.
- Use strict models for boundaries and contracts; use lenient models only where dynamic inputs are expected.
- Use TypeAdapter for non-model types and dynamic/runtime payload validation.
- Keep error messages stable enough for tests and operations.
- Avoid repeating v1 migration anti-pattern content already documented in `lib-pydantic-v2`.
- **Rule**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO. `u.Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for settings — standalone `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@u.field_validator`/`@u.model_validator` — prefer built-in constraints (`u.Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@u.computed_field`, `model_post_init`, `u.PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), settings from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `u.PrivateAttr` — never bare `self._x`. Nested classes MAY have business methods but ALL properties use `u.Field()`/`u.PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. Boolean/status fields use canonical names such as `success`, `failure`, `expired`, `healthy`, or `configured`. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **Rule**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **Rule**: Compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and compatibility aliases are FORBIDDEN. Legacy code is DELETED on contact.

## Instructions

> Advanced patterns are documented in [references/patterns-detail.md](references/patterns-detail.md). Load it for the full pattern library.

Pattern families available in references:

- **Validators**: `@u.field_validator`, `@u.model_validator`, reusable `Annotated` aliases with constraints
- **Computed fields**: `@u.computed_field` with `cached_property` semantics and FLEXT examples
- **Discriminated unions**: `Discriminator()` with Literal tags for polymorphic parsing
- **Serializers**: `@u.field_serializer`, `@u.model_serializer`, `model_dump()` control
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

from typing import Annotated, Self

from flext_core import c, m, p, r, t, u


class FlextExampleModels(m):
    """Model facade — validators, computed fields, ConfigDict via c/m/u."""

    class Example:
        class Window(m.Value):
            """Window with validation phases separated."""

            model_config = m.ConfigDict(extra="forbid")
            start: Annotated[
                t.NonNegativeInt,
                u.Field(
                    default=0,
                    description="Window start",
                    validate_default=True,
                ),
            ]
            end: Annotated[
                t.NonNegativeInt,
                u.Field(
                    default=0,
                    description="Window end",
                    validate_default=True,
                ),
            ]
            label: Annotated[t.NonEmptyStr, u.Field(description="Label")]

            @u.field_validator("label", mode="before")
            @classmethod
            def normalize_label(cls, value: t.RuntimeData) -> str:
                if not isinstance(value, str):
                    msg = "label must be str"
                    raise TypeError(msg)
                return value.strip()

            @u.model_validator(mode="after")
            def validate_window(self) -> Self:
                if self.end < self.start:
                    msg = "end must be >= start"
                    raise ValueError(msg)
                return self


def demo_window() -> p.Result[int]:
    """Create a Window and compute width."""
    w = FlextExampleModels.Example.Window(start=1, end=4, label="ok")
    return r[int].ok(w.end - w.start)
```

Why good:

- ✅ **All Pydantic via `m`** — `m.BaseModel`, `u.Field`, `m.ConfigDict`, `u.field_validator`, `u.model_validator`, `u.computed_field`
- ✅ **One-facade module + MRO** — `FlextPattern(FlextPatternValidateMixin, s[t.Dict])`
- ✅ **Validator phases separated** — normalize (before) → coerce → validate cross-fields (after)
- ✅ **Nested domain namespace** — `FlextPattern.Domain.Window` preserved, not flattened
- ✅ **Service boundary** — receives typed models, returns result via `r[T]`

### Bad: Direct pydantic imports instead of via `m` facade

```python
# ✗ WRONG — importing from pydantic directly (use flext_core c/m/u)
# from pydantic import BaseModel, u.Field, u.field_validator  # BANNED
from flext_core import m, u


class Window(m.BaseModel):
    start: int = 0
    end: int = 0

    @u.field_validator("start", mode="before")
    @classmethod
    def mixed_logic(cls, value: str) -> int:
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
from __future__ import annotations

from flext_core import u


@u.field_validator("start", mode="before")
@classmethod
def mixed_logic(cls, value: str) -> int:
    # Coercion + side effects + hidden invariant checks all in one
    logger = u.create_module_logger(__name__)
    logger.info("validating", value=value)  # Side effect in validator!
    return int(value)
```

Why bad: side effects and cross-field logic in field validator makes behavior brittle and hard to test.

Good:

```python
from typing import Annotated, Literal

from pydantic import Discriminator

from flext_core import m


class Ok(m.BaseModel):
    kind: Literal["ok"] = "ok"
    value: int


class Err(m.BaseModel):
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
- `rg -n "u.field_validator\(|u.model_validator\(|u.computed_field|u.field_serializer|Discriminator\(|TypeAdapter|strict=True" flext-core/src/flext_core/_models/base.py flext-core/src/flext_core/_models/settings.py flext-core/src/flext_core/_utilities/validation.py flext-core/src/flext_core/models.py flext-core/src/flext_core/service.py flext-core/src/flext_core/registry.py flext-ldif/src/flext_ldif/_models/base.py flext-cli/tests/conftest.py flext-tap-oracle-oic/src/flext_tap_oracle_oic/models.py`
