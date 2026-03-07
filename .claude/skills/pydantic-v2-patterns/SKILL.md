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

---

name: pydantic-v2-patterns
description: Deep-dive patterns companion to lib-pydantic-v2 for advanced Pydantic v2 implementation in FLEXT.

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
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO. `Field()` for ALL declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts. `SecretStr`/`SecretBytes` for secrets. `ConfigDict(...)` for config — standalone `*Config` classes TOTALLY FORBIDDEN (use `BaseSettings`/`ConfigDict`). Minimize custom `@field_validator`/`@model_validator` — prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`). FORBIDDEN in models: initialization helpers, unnecessary `@property`, simple getters/setters, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`). Enums/Mappings/Literals from `constants.py` (`c.*`), config from `settings.py` (`s.*`). JSON via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`. Internal state via `PrivateAttr` — never bare `self._x`. Nested classes MAY have business methods but ALL properties use `Field()`/`PrivateAttr`. `models.py`/`_models/` for model definitions ONLY. If not using a Pydantic v2 feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models like `FlextModels.ArbitraryTypesModel`, `FlextModels.FrozenModel`). Loose functions, standalone classes without MRO lineage, and modules without nested class facades are FORBIDDEN.
- **AXIOMATIC**: Compatibility wrappers, non-business validation fallbacks, legacy code of ANY kind, and compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED on contact.

## Instructions

### Validators

#### Pattern A: Reusable Annotated aliases

Use `Annotated` aliases to avoid duplicating validation logic across models.

```python
from typing import Annotated
from pydantic import AfterValidator, BeforeValidator, PlainValidator

def strip_whitespace(v: str) -> str:
    return v.strip()

def validate_non_empty(v: str) -> str:
    cleaned = v.strip()
    if not cleaned:
        raise ValueError("String cannot be empty or whitespace")
    return cleaned

def normalize_to_list(v: t.GeneralValueType) -> list[t.GeneralValueType]:
    if isinstance(v, list):
        return v
    if isinstance(v, (tuple, set)):
        return list(v)
    return [v]

def validate_uuid_string(v: str) -> str:
    import uuid

    try:
        uuid.UUID(v)
        return v
    except Exception as exc:
        raise ValueError("Invalid UUID format") from exc

StrippedString = Annotated[str, AfterValidator(strip_whitespace)]
ValidatedString = Annotated[str, AfterValidator(validate_non_empty)]
NormalizedList = Annotated[list[object], BeforeValidator(normalize_to_list)]
UUIDStr = Annotated[str, PlainValidator(validate_uuid_string)]
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`StrippedString`, `ValidatedString`, `NormalizedList`, `UUIDStr`)

Use when:

- The same domain constraint appears in multiple models.
- You need consistent behavior across subprojects.

#### Pattern B: Pre-normalization field validator

Normalize broad input forms before typed validation.

```python
from collections.abc import Mapping
from pydantic import BaseModel, Field, field_validator

class Metadata(BaseModel):
    attributes: dict[str, t.GeneralValueType] = Field(default_factory=dict)

    @field_validator("attributes", mode="before")
    @classmethod
    def normalize_attributes(cls, value: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
        if value is None:
            return {}
        if isinstance(value, BaseModel):
            dumped = value.model_dump()
            if isinstance(dumped, Mapping):
                return {str(k): v for k, v in dumped.items()}
            raise TypeError("attributes BaseModel must dump to mapping")
        if isinstance(value, Mapping):
            return {str(k): v for k, v in value.items()}
        raise TypeError(f"attributes must be dict-like, got {type(value).__name__}")
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`Metadata._validate_attributes`)

Use when:

- Input source may provide dict-like structures, custom mappings, or nested models.

#### Pattern C: Typed post-validation field validator

Validate business semantics after Pydantic has typed the field.

```python
from pydantic import BaseModel, Field, field_validator

class RetryConfiguration(BaseModel):
    retry_on_status_codes: list[int] = Field(default_factory=list)

    @field_validator("retry_on_status_codes", mode="after")
    @classmethod
    def validate_status_codes(cls, values: list[int]) -> list[int]:
        for code in values:
            if code < 100 or code > 599:
                raise ValueError(f"Invalid HTTP status code: {code}")
        return values
```

Repository anchor:

- `flext-core/src/flext_core/_models/settings.py` (`validate_backoff_strategy`)

Use when:

- Field is already typed and the next step is domain-level acceptance/rejection.

#### Pattern D: Cross-field model validator

Enforce invariants involving more than one field.

```python
from typing import Self
from pydantic import BaseModel, Field, model_validator

class RetryWindow(BaseModel):
    initial_delay_seconds: float = Field(gt=0)
    max_delay_seconds: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError("max_delay_seconds must be >= initial_delay_seconds")
        return self
```

Repository anchors:

- `flext-core/src/flext_core/_models/settings.py` (`validate_delay_consistency`, `validate_batch`)
- `flext-core/src/flext_core/_models/base.py` (audit/timestamp/id consistency validators)

Use when:

- One field’s validity depends on another field.

---

### Computed Fields

#### Pattern A: Derived status/value properties

Use computed fields for values derived from stored fields.

```python
from datetime import UTC, datetime
from pydantic import BaseModel, Field, computed_field

class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    @computed_field
    def is_modified(self) -> bool:
        return self.updated_at is not None

    @computed_field
    @property
    def age_seconds(self) -> float:
        return (datetime.now(UTC) - self.created_at).total_seconds()

    @computed_field
    @property
    def is_recent(self) -> bool:
        return self.age_seconds <= 3600
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`TimestampableMixin`)

#### Pattern B: Registry/service summaries

Use multiple small computed fields to keep state reporting explicit.

```python
from pydantic import BaseModel, Field, computed_field

class RegistrationSummary(BaseModel):
    registered: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

    @computed_field
    def is_success(self) -> bool:
        return not self.errors

    @computed_field
    def successful_registrations(self) -> int:
        return len(self.registered)

    @computed_field
    def failed_registrations(self) -> int:
        return len(self.errors)
```

Repository anchor:

- `flext-core/src/flext_core/registry.py`

#### Pattern C: Runtime facade computed field

Expose internal runtime composition as a stable read-only surface.

```python
from pydantic import computed_field

class ServiceRuntimeHolder:
    _runtime: t.GeneralValueType

    @computed_field
    def runtime(self) -> t.GeneralValueType:
        return self._runtime
```

Repository anchor:

- `flext-core/src/flext_core/service.py` (`runtime`)

Guidance:

- Keep computed fields side-effect free.
- Avoid expensive I/O or mutation in computed field bodies.
- Use them for observability and derived metadata, not command execution.

---

### Discriminated Unions

#### Pattern A: Message unions with explicit discriminator

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Discriminator

class CommandMessage(BaseModel):
    message_type: Literal["command"] = "command"
    command_type: str

class QueryMessage(BaseModel):
    message_type: Literal["query"] = "query"
    query_type: str

class EventMessage(BaseModel):
    message_type: Literal["event"] = "event"
    event_type: str

MessageUnion = Annotated[
    CommandMessage | QueryMessage | EventMessage,
    Discriminator("message_type"),
]
```

Repository anchors:

- `flext-core/src/flext_core/_models/base.py` (`MessageUnion`)
- `flext-core/src/flext_core/models.py` (`MessageUnion` alias)

#### Pattern B: Result unions for explicit branching

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Discriminator

class SuccessResult(BaseModel):
    result_type: Literal["success"] = "success"
    value: object

class FailureResult(BaseModel):
    result_type: Literal["failure"] = "failure"
    error: str

class PartialResult(BaseModel):
    result_type: Literal["partial"] = "partial"
    value: object
    warnings: list[str]

OperationResult = Annotated[
    SuccessResult | FailureResult | PartialResult,
    Discriminator("result_type"),
]
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`OperationResult`, `ValidationOutcome`)

Guidance:

- Discriminator field name must exist in every variant.
- Literal values are wire-level contracts; change only with migration planning.
- Keep each union family domain-scoped (messages vs results vs outcomes).

---

### Serializers

#### Pattern A: JSON-specific field serializer

```python
from datetime import datetime
from pydantic import BaseModel, field_serializer

class AuditModel(BaseModel):
    created_at: datetime

    @field_serializer("created_at", when_used="json")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()
```

Repository anchors:

- `flext-core/src/flext_core/_models/base.py` (datetime serializers)
- `flext-db-oracle/src/flext_db_oracle/models.py` (execution and time serializers)

#### Pattern B: Multi-field serializer for coherent formatting

```python
from datetime import datetime
from pydantic import BaseModel, field_serializer

class TimestampPair(BaseModel):
    created_at: datetime | None
    updated_at: datetime | None

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_timestamps(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`serialize_timestamps`, `serialize_audit_timestamps`)

#### Pattern C: Wildcard serializer for envelope enrichment

```python
from datetime import UTC, datetime
from pydantic import BaseModel, field_serializer
from pydantic_core.core_schema import FieldSerializationInfo

class EnvelopeModel(BaseModel):
    include_metadata: bool = True

    @field_serializer("*", when_used="json")
    def serialize_with_metadata(self, value: t.GeneralValueType, _info: FieldSerializationInfo) -> t.GeneralValueType:
        if not self.include_metadata:
            return value
        if isinstance(value, dict):
            return {
                **value,
                "_meta": {"serialized_at": datetime.now(UTC).isoformat()},
            }
        return value
```

Repository anchor:

- `flext-tap-oracle-oic/src/flext_tap_oracle_oic/models.py` (`serialize_with_oic_metadata`)

Guidance:

- Prefer specific field serializers first.
- Use wildcard serializers only for transport-level cross-cutting concerns.
- Keep payload shape changes explicit and documented.

---

### Strict Mode

#### Pattern A: Strict + frozen boundary contract

```python
from pydantic import BaseModel, ConfigDict

class FrozenStrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )
```

Repository anchor:

- `flext-core/src/flext_core/_models/base.py` (`FrozenStrictModel`)

Guidance:

- Use strict mode on boundaries to prevent silent coercion.
- Add `extra="ignore"` only when interoperability requires forward compatibility.
- Pair strict mode with explicit validators for domain invariants.

---

### TypeAdapter

#### Pattern A: Runtime validate wrapper

```python
from pydantic import TypeAdapter, ValidationError

def validate_runtime(data: t.GeneralValueType, type_: type[t.GeneralValueType]) -> tuple[bool, t.GeneralValueType | str]:
    adapter = TypeAdapter(type_)
    try:
        return True, adapter.validate_python(data)
    except ValidationError as exc:
        errors = "; ".join(f"{e['loc']}: {e['msg']}" for e in exc.errors())
        return False, f"Validation failed: {errors}"
```

Repository anchor:

- `flext-core/src/flext_core/_utilities/validation.py` (`TypeAdapter.validate`)

#### Pattern B: Runtime serialization wrapper

```python
from pydantic import TypeAdapter

def serialize_runtime(value: t.GeneralValueType, type_: type[t.GeneralValueType]) -> dict[str, t.GeneralValueType]:
    adapter = TypeAdapter(type_)
    dumped = adapter.dump_python(value, mode="json")
    if isinstance(dumped, dict):
        return dumped
    return {"value": dumped}
```

Repository anchor:

- `flext-core/src/flext_core/_utilities/validation.py` (`TypeAdapter.serialize`)

#### Pattern C: JSON parse to typed value

```python
from pydantic import TypeAdapter, ValidationError

def parse_json_runtime(json_str: str, type_: type[object]) -> tuple[bool, object | str]:
    adapter = TypeAdapter(type_)
    try:
        return True, adapter.validate_json(json_str)
    except ValidationError as exc:
        errors = "; ".join(f"{e['loc']}: {e['msg']}" for e in exc.errors())
        return False, f"JSON parsing failed: {errors}"
```

Repository anchor:

- `flext-core/src/flext_core/_utilities/validation.py` (`TypeAdapter.parse_json`)

#### Pattern D: Fixture contract validation in tests

```python
import json
from pathlib import Path
from pydantic import TypeAdapter

def load_fixture(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    adapter = TypeAdapter(dict[str, object])
    return adapter.validate_python(payload)
```

Repository anchor:

- `flext-cli/tests/conftest.py` (`load_fixture_config`, `load_fixture_data`)

Guidance:

- Keep TypeAdapter in utilities and fixture loaders.
- Do not replace rich domain models with TypeAdapter where model semantics are required.
- Use adapter wrappers when runtime type is generic or dynamic.

---

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
    def normalize_label(cls, value: t.GeneralValueType) -> str:
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
