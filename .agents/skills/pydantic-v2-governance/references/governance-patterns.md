## Instructions

### 1. u.Field() → Annotated Pattern

**Pattern**: For nullable fields, use `Annotated[T | None, u.Field(...)]` NOT `Annotated[T, u.Field(...)] | None`.

**Canonical Example** (`flext-core/src/flext_core/models/cqrs.py:91-99`):

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, u.Field


class Pagination(m.BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Pagination",
            "description": "Pagination model for query results with computed fields",
        }
    )
    page: Annotated[
        int,
        u.Field(
            default=c.DEFAULT_PAGE_NUMBER,
            ge=c.RETRY_COUNT_MIN,
            description="Page number (1-based indexing)",
            examples=[1, 2, 10, 100],
        ),
    ] = c.DEFAULT_PAGE_NUMBER
```

**Why**: The union MUST be inside `Annotated[]`, not outside. This ensures u.Field constraints apply to the entire union.

**Anti-pattern**:

```python
# ✗ WRONG — u.Field constraints don't apply to None
field: Annotated[str, u.Field(min_length=1)] | None = None
```

**Correct**:

```python
# ✓ CORRECT — u.Field constraints apply to entire union
field: Annotated[str | None, u.Field(min_length=1)] = None
```

**Repository anchors**:

- `flext-core/src/flext_core/models/cqrs.py:91-99`
- `flext-core/src/flext_core/models/base.py` (multiple examples)

### 2. default_factory for Mutable Defaults

**Pattern**: ALWAYS use `default_factory` for mutable defaults (list, dict, set). NEVER use `default=[]`.

**Canonical Example**:

```python
from pydantic import BaseModel, u.Field


class RetryConfiguration(m.BaseModel):
    retry_on_status_codes: Sequence[int] = u.Field(default_factory=list)
    metadata: t.StrMapping = u.Field(default_factory=dict)
    tags: set[str] = u.Field(default_factory=set)
```

**Why**: `default=[]` creates a SHARED mutable t.JsonValue across all instances (Python gotcha). `default_factory=list` creates a NEW list per instance.

**Anti-pattern**:

```python
# ✗ WRONG — Shared mutable default
class Config(m.BaseModel):
    items: t.StrSequence = u.Field(default=[])  # BUG: all instances share same list
```

**Correct**:

```python
# ✓ CORRECT — New list per instance
class Config(m.BaseModel):
    items: t.StrSequence = u.Field(default_factory=list)
```

**Repository anchors**:

- `flext-core/src/flext_core/models/settings.py` (multiple examples)
- `flext-core/src/flext_core/models/base.py` (multiple examples)

### 3. TypeAdapter Caching

**Pattern**: Cache `TypeAdapter` instances as `ClassVar` to avoid repeated instantiation in loops.

**Canonical Example** (`flext-core/src/flext_core/models/base.py:53-102`):

```python
from typing import Annotated, ClassVar
from pydantic import BaseModel, u.Field, TypeAdapter


class ValidationHelpers(m.BaseModel):
    _tags_adapter: ClassVar[m.TypeAdapter[t.StrSequence] | None] = None
    _list_adapter: ClassVar[m.TypeAdapter[t.JsonList] | None] = None
    _strict_string_adapter: ClassVar[
        m.TypeAdapter[Annotated[str, u.Field(strict=True)]] | None
    ] = None
    _metadata_map_adapter: ClassVar[
        m.TypeAdapter[Mapping[str, t.JsonValue]] | None
    ] = None
    _config_adapter: ClassVar[m.TypeAdapter[t.JsonMapping] | None] = None
    _dict_container_adapter: ClassVar[
        m.TypeAdapter[t.JsonMapping] | None
    ] = None
    _list_container_adapter: ClassVar[m.TypeAdapter[t.JsonList] | None] = None
    _tuple_container_adapter: ClassVar[
        m.TypeAdapter[tuple[t.JsonValue, ...]] | None
    ] = None
    _primitives_adapter: ClassVar[m.TypeAdapter[t.Primitives] | None] = None
    _dict_str_metadata_adapter: ClassVar[
        m.TypeAdapter[Mapping[str, t.JsonValue | None]] | None
    ] = None
    _list_serializable_adapter: ClassVar[
        m.TypeAdapter[Sequence[t.JsonValue]] | None
    ] = None
    _tuple_serializable_adapter: ClassVar[
        m.TypeAdapter[tuple[t.JsonValue, ...]] | None
    ] = None
    _set_container_adapter: ClassVar[m.TypeAdapter[set[t.JsonValue]] | None] = None
    _set_str_adapter: ClassVar[m.TypeAdapter[set[str]] | None] = None
    _set_scalar_adapter: ClassVar[m.TypeAdapter[set[t.Scalar]] | None] = None
    _sortable_dict_adapter: ClassVar[
        m.TypeAdapter[Mapping[t.SortableObjectType, t.JsonValue | None]] | None
    ] = None
    _strict_json_list_adapter: ClassVar[
        m.TypeAdapter[Sequence[t.StrictValue]] | None
    ] = None
    _strict_json_scalar_adapter: ClassVar[m.TypeAdapter[t.Scalar] | None] = None
    _scalar_adapter: ClassVar[m.TypeAdapter[t.Scalar] | None] = None
    _float_adapter: ClassVar[m.TypeAdapter[float] | None] = None
    _str_adapter: ClassVar[m.TypeAdapter[str] | None] = None
    _str_list_adapter: ClassVar[m.TypeAdapter[t.StrSequence] | None] = None
    _str_or_bytes_adapter: ClassVar[m.TypeAdapter[str | bytes] | None] = None
    _enum_type_adapter: ClassVar[m.TypeAdapter[type[StrEnum]] | None] = None
    _serializable_adapter: ClassVar[m.TypeAdapter[t.JsonValue] | None] = None
    _metadata_json_dict_adapter: ClassVar[
        m.TypeAdapter[Mapping[str, t.Primitives]] | None
    ] = None
    _flat_metadata_dict_adapter: ClassVar[
        m.TypeAdapter[Mapping[str, t.Primitives]] | None
    ] = None

    @classmethod
    def get_tags_adapter(cls) -> m.TypeAdapter[t.StrSequence]:
        if cls._tags_adapter is None:
            cls._tags_adapter = TypeAdapter(t.StrSequence)
        return cls._tags_adapter
```

**Why**: `TypeAdapter` instantiation is expensive. Caching as `ClassVar` ensures one instance per class, not per method call.

**Anti-pattern**:

```python
# ✗ WRONG — Creates new TypeAdapter on every call
def validate_tags(self, tags) -> t.StrSequence:
    adapter = TypeAdapter(t.StrSequence)  # EXPENSIVE
    return adapter.validate_python(tags)
```

**Correct**:

```python
# ✓ CORRECT — Cached TypeAdapter
_tags_adapter: ClassVar[m.TypeAdapter[t.StrSequence] | None] = None


@classmethod
def get_tags_adapter(cls) -> m.TypeAdapter[t.StrSequence]:
    if cls._tags_adapter is None:
        cls._tags_adapter = TypeAdapter(t.StrSequence)
    return cls._tags_adapter


def validate_tags(self, tags) -> t.StrSequence:
    return self.get_tags_adapter().validate_python(tags)
```

**Repository anchors**:

- `flext-core/src/flext_core/models/base.py:53-102`
- `flext-core/src/flext_core/_utilities/validation.py`

### 4. Protocol vs ABC

**Pattern**: Use `Protocol` for structural typing (duck typing), `ABC` for explicit inheritance contracts.

**When to use Protocol**:

- Interface contracts across unrelated classes
- Structural typing (if it walks like a duck...)
- No shared implementation needed
- MUST use `@runtime_checkable` for `isinstance()` checks

**When to use ABC**:

- Shared implementation via inheritance
- Explicit "is-a" relationships
- Template method pattern
- Enforced method implementation

**Canonical Example** (`flext-core/src/flext_core/protocols.py:39-100`):

```python
from typing import Protocol, runtime_checkable
from abc import ABC, abstractmethod


# Protocol — structural typing
@runtime_checkable
class CommandBus(Protocol):
    """Structural interface for command dispatching."""

    def dispatch(self, command: BaseModel) -> p.Result[BaseModel]: ...


# ABC — inheritance contract
class BaseHandler(ABC):
    """Abstract base for handlers with shared implementation."""

    @abstractmethod
    def handle(self, message: BaseModel) -> p.Result[BaseModel]:
        """Subclasses MUST implement."""
        ...

    def validate(self, message: BaseModel) -> p.Result[bool]:
        """Shared implementation."""
        return r[bool].ok(True)
```

**Why**: Protocols enable loose coupling without inheritance. ABCs enforce explicit contracts with shared behavior.

**Repository anchors**:

- `flext-core/src/flext_core/protocols.py:1-100`
- `flext-core/src/flext_core/handlers.py`

### 5. issubclass() Safety

**Pattern**: NEVER use bare `issubclass()` with Protocols. Use `_ProtocolIntrospection.check_implements_protocol()` or `isinstance()` with `@runtime_checkable`.

**Canonical Example** (`flext-core/src/flext_core/protocols.py:39-76`):

```python
from typing import Protocol, runtime_checkable


class _ProtocolIntrospection:
    """Internal helpers for protocol detection and compliance checks."""

    @classmethod
    def check_implements_protocol(
        cls,
        instance: FlextProtocols.Base | t.JsonValue,
        protocol: type,
    ) -> bool:
        """Check if an instance implements a protocol."""
        registered_protocols = cls.get_class_protocols(instance.__class__)
        if protocol in registered_protocols:
            return True
        protocol_annotations: t.JsonMapping = (
            protocol.__annotations__ if hasattr(protocol, "__annotations__") else {}
        )
        raw_attrs_candidate = getattr(protocol, "__protocol_attrs__", ())
        raw_attrs: set[str] = set[str]()
        iterable_attrs: t.StrSequence = ()
        try:
            iterable_attrs = tuple(raw_attrs_candidate)
        except TypeError:
            iterable_attrs = ()
        raw_attrs = set(iterable_attrs)
        protocol_methods: set[str] = set()
        protocol_methods.update(raw_attrs)
        required_members: set[str] = set(protocol_annotations.keys())
        required_members.update(protocol_methods)
        required_members = {
            m
            for m in required_members
            if not m.startswith("_")
            or m.startswith("__")
            or (m in {"metadata_extra", "sealed"})
        }
        if not required_members:
            return False
        return all(hasattr(instance, member) for member in required_members)
```

**Why**: `issubclass(SomeClass, SomeProtocol)` can raise `TypeError` if the Protocol isn't properly decorated. Use structural checks or `isinstance()` with `@runtime_checkable`.

**Anti-pattern**:

```python
# ✗ WRONG — Can raise TypeError
if issubclass(MyClass, SomeProtocol):  # UNSAFE
    ...
```

**Correct**:

```python
# ✓ CORRECT — Safe structural check
if _ProtocolIntrospection.check_implements_protocol(instance, SomeProtocol):
    ...


# ✓ CORRECT — isinstance with @runtime_checkable
@runtime_checkable
class SomeProtocol(Protocol): ...


if isinstance(instance, SomeProtocol):
    ...
```

**Repository anchors**:

- `flext-core/src/flext_core/protocols.py:39-100`

### 6. ConfigDict

**Pattern**: Use `model_config = ConfigDict(...)` for ALL model configuration. Standalone `*Config` classes are FORBIDDEN.

**Canonical Example**:

```python
from pydantic import BaseModel, ConfigDict, u.Field


class StrictBoundaryModel(m.BaseModel):
    model_config = ConfigDict(
        strict=True,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "title": "Strict Boundary Model",
            "description": "Immutable contract with strict validation",
        },
    )
    name: str = u.Field(..., description="Entity name")
    value: int = u.Field(..., ge=0, description="Non-negative value")
```

**Common ConfigDict options**:

- `strict=True` — No coercion (boundary models)
- `validate_assignment=True` — Validate on field assignment
- `validate_default=True` — Validate default values
- `extra="forbid"` — Reject unknown fields (strict boundaries)
- `extra="ignore"` — Ignore unknown fields (flexible internal models)
- `frozen=True` — Immutable model
- `str_strip_whitespace=True` — Auto-strip strings
- `json_schema_extra={}` — OpenAPI/JSON Schema metadata

**Anti-pattern**:

```python
# ✗ WRONG — Pydantic v1 style
class MyModel(m.BaseModel):
    class Config:
        extra = "forbid"
```

**Correct**:

```python
# ✓ CORRECT — Pydantic v2 style
class MyModel(m.BaseModel):
    model_config = ConfigDict(extra="forbid")
```

**Repository anchors**:

- `flext-core/src/flext_core/models/base.py` (`ContractModel`)
- `flext-core/src/flext_core/models/cqrs.py:85-90`
- `flext-core/src/flext_core/settings.py`

### 7. Validation Boundaries

**Pattern**: Configurable validation depth via `FLEXT_METACLASS_STRICT` environment variable.

**Canonical Example**:

```python
import os
from pydantic import BaseModel, ConfigDict

# Read from environment
STRICT_MODE = os.getenv("FLEXT_METACLASS_STRICT", "false").lower() == "true"


class BoundaryModel(m.BaseModel):
    model_config = ConfigDict(
        strict=STRICT_MODE,
        validate_assignment=STRICT_MODE,
        extra="forbid" if STRICT_MODE else "ignore",
    )
```

**Why**: Allows runtime control of validation strictness without code changes. Useful for:

- Development (lenient) vs Production (strict)
- Testing with partial fixtures
- Gradual migration to stricter validation

**Repository anchors**:

- `flext-core/src/flext_core/protocols.py` (metaclass strict mode)
- `flext-core/src/flext_core/settings.py`

### 8. Anti-Patterns

**FORBIDDEN patterns** (see `AGENTS.md` §3.1-§3.3):

#### 8.1 cast() — FORBIDDEN

```python
# ✗ WRONG — cast() is forbidden outside flext-core result internals
from typing import cast

value = cast(str, some_value)  # FORBIDDEN
```

**Correct**: Use Pydantic validation or TypeGuard:

```python
# ✓ CORRECT — Pydantic validation
from pydantic import TypeAdapter

adapter = TypeAdapter(str)
value = adapter.validate_python(some_value)

# ✓ CORRECT — TypeGuard
from flext_core import u

if u.Guards.is_scalar(some_value):
    # some_value is now TypeGuard[Scalar]
    ...
```

#### 8.2 Any — FORBIDDEN

**FORBIDDEN**: `from typing import Any`. Use `t.*` contracts instead.

**Correct**:

```python
# ✓ CORRECT — Use t.* contracts
from flext_core import t

data: t.JsonValue = ...
metadata: t.JsonValue = ...
settings: m.ConfigMap = ...
```

#### 8.3 t.JsonValue — FORBIDDEN

```python
# ✗ WRONG — bare t.JsonValue is forbidden
data = ...  # FORBIDDEN
```

**Correct**: Use `t.*` contracts:

```python
# ✓ CORRECT — Use t.* contracts
from flext_core import t

data: t.JsonValue = ...
```

#### 8.4 type() for narrowing — FORBIDDEN

```python
# ✗ WRONG — type() for narrowing is forbidden
if type(value) is str:  # FORBIDDEN
    ...
if type(value) == str:  # FORBIDDEN
    ...
```

**Correct**: Use `isinstance()` or `TypeGuard`:

```python
# ✓ CORRECT — isinstance()
if isinstance(value, str):
    ...

# ✓ CORRECT — TypeGuard
from flext_core import u

if u.Guards.is_scalar(value):
    ...
```

#### 8.5 Double u.Field() assignment — FORBIDDEN

```python
# ✗ WRONG — Double u.Field() assignment
from typing import Annotated
from pydantic import BaseModel, u.Field


class Model(m.BaseModel):
    x: Annotated[str, u.Field(min_length=1)] = u.Field(default="")  # REDUNDANT
```

**Correct**: u.Field() ONLY in Annotated OR as default, not both:

```python
# ✓ CORRECT — u.Field() in Annotated
class Model(m.BaseModel):
    x: Annotated[str, u.Field(min_length=1, default="")] = ""


# ✓ CORRECT — u.Field() as default
class Model(m.BaseModel):
    x: str = u.Field(default="", min_length=1)
```

#### 8.6 Model(data) with dict — FORBIDDEN

```python
# ✗ WRONG — Direct instantiation with dict
model = MyModel({"key": "value"})  # FORBIDDEN
```

**Correct**: Use `model_validate()`:

```python
# ✓ CORRECT — model_validate()
model = MyModel.model_validate({"key": "value"})
```

**Repository anchors**:

- `AGENTS.md` §3.1-§3.3
- `flext-core/AGENTS.md` (Zero Tolerance Rules)
