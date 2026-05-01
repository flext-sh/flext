## Instructions

### Validators

#### Pattern A: Reusable Annotated aliases

Use `Annotated` aliases to avoid duplicating validation logic across models.

```python
from typing import Annotated
from pydantic import AfterValidator, m.BeforeValidator, PlainValidator


def strip_whitespace(v: str) -> str:
    return v.strip()


def validate_non_empty(v: str) -> str:
    cleaned = v.strip()
    if not cleaned:
        raise ValueError("String cannot be empty or whitespace")
    return cleaned


def normalize_to_list(v) -> t.JsonList:
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
NormalizedList = Annotated[t.JsonList, m.BeforeValidator(normalize_to_list)]
UUIDStr = Annotated[str, PlainValidator(validate_uuid_string)]
```

Repository anchor:

- `flext-core/src/flext_core/models/base.py` (`StrippedString`, `ValidatedString`, `NormalizedList`, `UUIDStr`)

Use when:

- The same domain constraint appears in multiple models.
- You need consistent behavior across subprojects.

#### Pattern B: Pre-normalization field validator

Normalize broad input forms before typed validation.

```python
from collections.abc import Mapping
from pydantic import BaseModel, u.Field, u.field_validator


class Metadata(m.BaseModel):
    attributes: t.JsonMapping = u.Field(default_factory=dict)

    @u.field_validator("attributes", mode="before")
    @classmethod
    def normalize_attributes(cls, value) -> t.JsonMapping:
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

- `flext-core/src/flext_core/models/base.py` (`Metadata._validate_attributes`)

Use when:

- Input source may provide dict-like structures, custom mappings, or nested models.

#### Pattern C: Typed post-validation field validator

Validate business semantics after Pydantic has typed the field.

```python
from pydantic import BaseModel, u.Field, u.field_validator


class RetryConfiguration(m.BaseModel):
    retry_on_status_codes: t.SequenceOf[int] = u.Field(default_factory=list)

    @u.field_validator("retry_on_status_codes", mode="after")
    @classmethod
    def validate_status_codes(cls, values: t.SequenceOf[int]) -> t.SequenceOf[int]:
        for code in values:
            if code < 100 or code > 599:
                raise ValueError(f"Invalid HTTP status code: {code}")
        return values
```

Repository anchor:

- `flext-core/src/flext_core/models/settings.py` (`validate_backoff_strategy`)

Use when:

- u.Field is already typed and the next step is domain-level acceptance/rejection.

#### Pattern D: Cross-field model validator

Enforce invariants involving more than one field.

```python
from typing import Self
from pydantic import BaseModel, u.Field, u.model_validator


class RetryWindow(m.BaseModel):
    initial_delay_seconds: float = u.Field(gt=0)
    max_delay_seconds: float = u.Field(gt=0)

    @u.model_validator(mode="after")
    def validate_window(self) -> Self:
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError("max_delay_seconds must be >= initial_delay_seconds")
        return self
```

Repository anchors:

- `flext-core/src/flext_core/models/settings.py` (`validate_delay_consistency`, `validate_batch`)
- `flext-core/src/flext_core/models/base.py` (audit/timestamp/id consistency validators)

Use when:

- One field’s validity depends on another field.

---

### Computed u.Fields

#### Pattern A: Derived status/value properties

Use computed fields for values derived from stored fields.

```python
from datetime import UTC, datetime
from pydantic import BaseModel, u.Field, u.computed_field


class TimestampedModel(m.BaseModel):
    created_at: datetime = u.Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    @u.computed_field
    def is_modified(self) -> bool:
        return self.updated_at is not None

    @u.computed_field
    @property
    def age_seconds(self) -> float:
        return (datetime.now(UTC) - self.created_at).total_seconds()

    @u.computed_field
    @property
    def is_recent(self) -> bool:
        return self.age_seconds <= 3600
```

Repository anchor:

- `flext-core/src/flext_core/models/base.py` (`TimestampableMixin`)

#### Pattern B: Registry/service summaries

Use multiple small computed fields to keep state reporting explicit.

```python
from pydantic import BaseModel, u.Field, u.computed_field


class RegistrationSummary(m.BaseModel):
    registered: t.StrSequence = u.Field(default_factory=list)
    errors: t.StrSequence = u.Field(default_factory=list)

    @u.computed_field
    def success(self) -> bool:
        return not self.errors

    @u.computed_field
    def successful_registrations(self) -> int:
        return len(self.registered)

    @u.computed_field
    def failed_registrations(self) -> int:
        return len(self.errors)
```

Repository anchor:

- `flext-core/src/flext_core/registry.py`

#### Pattern C: Runtime facade computed field

Expose internal runtime composition as a stable read-only surface.

```python
from pydantic import u.computed_field


class ServiceRuntimeHolder:
    _runtime

    @u.computed_field
    def runtime(self):
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


class CommandMessage(m.BaseModel):
    message_type: Literal["command"] = "command"
    command_type: str


class QueryMessage(m.BaseModel):
    message_type: Literal["query"] = "query"
    query_type: str


class EventMessage(m.BaseModel):
    message_type: Literal["event"] = "event"
    event_type: str


MessageUnion = Annotated[
    CommandMessage | QueryMessage | EventMessage,
    Discriminator("message_type"),
]
```

Repository anchors:

- `flext-core/src/flext_core/models/base.py` (`MessageUnion`)
- `flext-core/src/flext_core/models.py` (`MessageUnion` alias)

#### Pattern B: Result unions for explicit branching

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Discriminator


class SuccessResult(m.BaseModel):
    result_type: Literal["success"] = "success"
    value


class FailureResult(m.BaseModel):
    result_type: Literal["failure"] = "failure"
    error: str


class PartialResult(m.BaseModel):
    result_type: Literal["partial"] = "partial"
    value
    warnings: t.StrSequence


OperationResult = Annotated[
    SuccessResult | FailureResult | PartialResult,
    Discriminator("result_type"),
]
```

Repository anchor:

- `flext-core/src/flext_core/models/base.py` (`OperationResult`, `ValidationOutcome`)

Guidance:

- Discriminator field name must exist in every variant.
- Literal values are wire-level contracts; change only with migration planning.
- Keep each union family domain-scoped (messages vs results vs outcomes).

---

### Serializers

#### Pattern A: JSON-specific field serializer

```python
from datetime import datetime
from pydantic import BaseModel, u.field_serializer


class AuditModel(m.BaseModel):
    created_at: datetime

    @u.field_serializer("created_at", when_used="json")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()
```

Repository anchors:

- `flext-core/src/flext_core/models/base.py` (datetime serializers)
- `flext-db-oracle/src/flext_db_oracle/models.py` (execution and time serializers)

#### Pattern B: Multi-field serializer for coherent formatting

```python
from datetime import datetime
from pydantic import BaseModel, u.field_serializer


class TimestampPair(m.BaseModel):
    created_at: datetime | None
    updated_at: datetime | None

    @u.field_serializer("created_at", "updated_at", when_used="json")
    def serialize_timestamps(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
```

Repository anchor:

- `flext-core/src/flext_core/models/base.py` (`serialize_timestamps`, `serialize_audit_timestamps`)

#### Pattern C: Wildcard serializer for envelope enrichment

```python
from datetime import UTC, datetime
from pydantic import BaseModel, u.field_serializer
from pydantic_core.core_schema import u.FieldSerializationInfo


class EnvelopeModel(m.BaseModel):
    include_metadata: bool = True

    @u.field_serializer("*", when_used="json")
    def serialize_with_metadata(self, value, _info: u.FieldSerializationInfo):
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


class ContractModel(m.BaseModel):
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

- `flext-core/src/flext_core/models/base.py` (`ContractModel`)

Guidance:

- Use strict mode on boundaries to prevent silent coercion.
- Add `extra="ignore"` only when interoperability requires forward compatibility.
- Pair strict mode with explicit validators for domain invariants.

---

### TypeAdapter

#### Pattern A: Runtime validate wrapper

```python
from pydantic import TypeAdapter, ValidationError


def validate_runtime(data, type_: type[t.JsonValue]) -> tuple[bool, t.JsonValue | str]:
    adapter = TypeAdapter(type_)
    try:
        return True, adapter.validate_python(data)
    except c.ValidationError as exc:
        errors = "; ".join(f"{e['loc']}: {e['msg']}" for e in exc.errors())
        return False, f"Validation failed: {errors}"
```

Repository anchor:

- `flext-core/src/flext_core/_utilities/validation.py` (`TypeAdapter.validate`)

#### Pattern B: Runtime serialization wrapper

```python
from pydantic import TypeAdapter


def serialize_runtime(value, type_: type[t.JsonValue]) -> t.JsonMapping:
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


def parse_json_runtime(
    json_str: str, type_: type[t.JsonValue]
) -> tuple[bool, t.JsonValue | str]:
    adapter = TypeAdapter(type_)
    try:
        return True, adapter.validate_json(json_str)
    except c.ValidationError as exc:
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


def load_fixture(path: Path) -> t.JsonMapping:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)
    adapter = TypeAdapter(t.JsonMapping)
    return adapter.validate_python(payload)
```

Repository anchor:

- `flext-cli/tests/conftest.py` (`load_fixture_config`, `load_fixture_data`)

Guidance:

- Keep TypeAdapter in utilities and fixture loaders.
- Do not replace rich domain models with TypeAdapter where model semantics are required.
- Use adapter wrappers when runtime type is generic or dynamic.

---
