<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
  - [1. Field() → Annotated Pattern](#1-field--annotated-pattern)
  - [2. default_factory for Mutable Defaults](#2-defaultfactory-for-mutable-defaults)
  - [3. TypeAdapter Caching](#3-typeadapter-caching)
  - [4. Protocol vs ABC](#4-protocol-vs-abc)
  - [5. issubclass() Safety](#5-issubclass-safety)
  - [6. ConfigDict](#6-configdict)
  - [7. Validation Boundaries](#7-validation-boundaries)
  - [8. Anti-Patterns](#8-anti-patterns)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: pydantic-v2-governance
description: Internal Pydantic v2 governance patterns for FLEXT 33-project monorepo. Use when creating models, validators, or working with Pydantic v2 features across the codebase.

---

# Pydantic v2 Governance

**Reviewed**: 2026-02-22 | **Scope**: Canonical Pydantic v2 patterns from FLEXT codebase

## Scope

- `.claude/skills/pydantic-v2-governance/`
- All 33 FLEXT projects (`src/`, `tests/`, `examples/`)
- Codifies ACTUAL codebase patterns, not theoretical best practices

## References

- `AGENTS.md` §3.1-§3.3 — Code Law (canonical governance)
- `.claude/skills/lib-pydantic-v2/SKILL.md` — Pydantic v2 API rules
- `.claude/skills/pydantic-v2-patterns/SKILL.md` — Advanced patterns
- `flext-core/src/flext_core/_models/cqrs.py:82-101` — Annotated pattern
- `flext-core/src/flext_core/_models/base.py:53-102` — TypeAdapter caching
- `flext-core/src/flext_core/protocols.py:1-100` — Protocol patterns
- `flext-core/src/flext_core/typings.py:1-150` — Type system foundation
- `flext-core/AGENTS.md` — Project-level pointer

## Rules

- **Policy Authority**: `AGENTS.md` §3.1-§3.3 is supreme law. This skill documents IMPLEMENTATION patterns.
- **Codebase Evidence**: Every pattern MUST reference actual codebase files.
- **No Contradiction**: This skill extends `lib-pydantic-v2` and `pydantic-v2-patterns`, never contradicts them.
- **Mandatory Pydantic v2 Mastery**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY — USE, USE, USE Pydantic v2 features to their fullest across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class extends `BaseModel` (or FLEXT base models) via MRO.
- **Field() for ALL declarations**: Use `Field()` with `description`, `title`, `examples`, `json_schema_extra` documenting business rules — fields are self-documenting contracts.
- **Secrets**: Use `SecretStr`/`SecretBytes` for secrets.
- **ConfigDict**: Use `model_config = ConfigDict(...)` for config — standalone `*Config` classes TOTALLY FORBIDDEN (use `BaseSettings`/`ConfigDict`).
- **Minimize custom validators**: Prefer built-in constraints (`Field(ge=0)`, `StringConstraints()`, `Literal`, `constr`, `conint`).
- **FORBIDDEN in models**: initialization helpers, unnecessary `@property`, simple getters/setters, line-reduction wrappers, pass-through methods — USE Pydantic built-ins (`@computed_field`, `model_post_init`, `PrivateAttr`).
- **Enums/Mappings/Literals**: From `constants.py` (`c.*`), config from `settings.py` (`s.*`).
- **JSON**: Via `model_dump_json()`, `model_validate_json()`, `TypeAdapter`.
- **Internal state**: Via `PrivateAttr` — never bare `self._x`.
- **Nested classes**: MAY have business methods but ALL properties use `Field()`/`PrivateAttr`.
- **models.py/_models/**: For model definitions ONLY.

## Instructions

### 1. Field() → Annotated Pattern

**Pattern**: For nullable fields, use `Annotated[T | None, Field(...)]` NOT `Annotated[T, Field(...)] | None`.

**Canonical Example** (`flext-core/src/flext_core/_models/cqrs.py:91-99`):

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "Pagination",
            "description": "Pagination model for query results with computed fields",
        }
    )
    page: Annotated[
        int,
        Field(
            default=c.Pagination.DEFAULT_PAGE_NUMBER,
            ge=c.Reliability.RETRY_COUNT_MIN,
            description="Page number (1-based indexing)",
            examples=[1, 2, 10, 100],
        ),
    ] = c.Pagination.DEFAULT_PAGE_NUMBER
```

**Why**: The union MUST be inside `Annotated[]`, not outside. This ensures Field constraints apply to the entire union.

**Anti-pattern**:

```python
# ✗ WRONG — Field constraints don't apply to None
field: Annotated[str, Field(min_length=1)] | None = None
```

**Correct**:

```python
# ✓ CORRECT — Field constraints apply to entire union
field: Annotated[str | None, Field(min_length=1)] = None
```

**Repository anchors**:
- `flext-core/src/flext_core/_models/cqrs.py:91-99`
- `flext-core/src/flext_core/_models/base.py` (multiple examples)

### 2. default_factory for Mutable Defaults

**Pattern**: ALWAYS use `default_factory` for mutable defaults (list, dict, set). NEVER use `default=[]`.

**Canonical Example**:

```python
from pydantic import BaseModel, Field


class RetryConfiguration(BaseModel):
    retry_on_status_codes: list[int] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    tags: set[str] = Field(default_factory=set)
```

**Why**: `default=[]` creates a SHARED mutable object across all instances (Python gotcha). `default_factory=list` creates a NEW list per instance.

**Anti-pattern**:

```python
# ✗ WRONG — Shared mutable default
class Config(BaseModel):
    items: list[str] = Field(default=[])  # BUG: all instances share same list
```

**Correct**:

```python
# ✓ CORRECT — New list per instance
class Config(BaseModel):
    items: list[str] = Field(default_factory=list)
```

**Repository anchors**:
- `flext-core/src/flext_core/_models/settings.py` (multiple examples)
- `flext-core/src/flext_core/_models/base.py` (multiple examples)

### 3. TypeAdapter Caching

**Pattern**: Cache `TypeAdapter` instances as `ClassVar` to avoid repeated instantiation in loops.

**Canonical Example** (`flext-core/src/flext_core/_models/base.py:53-102`):

```python
from typing import Annotated, ClassVar
from pydantic import BaseModel, Field, TypeAdapter


class ValidationHelpers(BaseModel):
    _tags_adapter: ClassVar[TypeAdapter[list[str]] | None] = None
    _list_adapter: ClassVar[TypeAdapter[list[t.Container]] | None] = None
    _strict_string_adapter: ClassVar[
        TypeAdapter[Annotated[str, Field(strict=True)]] | None
    ] = None
    _metadata_map_adapter: ClassVar[
        TypeAdapter[Mapping[str, t.MetadataValue]] | None
    ] = None
    _config_adapter: ClassVar[TypeAdapter[Mapping[str, t.Container]] | None] = None
    _dict_container_adapter: ClassVar[TypeAdapter[dict[str, t.Container]] | None] = None
    _list_container_adapter: ClassVar[TypeAdapter[list[t.Container]] | None] = None
    _tuple_container_adapter: ClassVar[TypeAdapter[tuple[t.Container, ...]] | None] = (
        None
    )
    _primitives_adapter: ClassVar[TypeAdapter[t.Primitives] | None] = None
    _dict_str_metadata_adapter: ClassVar[
        TypeAdapter[dict[str, t.MetadataValue | None]] | None
    ] = None
    _list_serializable_adapter: ClassVar[TypeAdapter[list[t.Serializable]] | None] = (
        None
    )
    _tuple_serializable_adapter: ClassVar[
        TypeAdapter[tuple[t.Serializable, ...]] | None
    ] = None
    _set_container_adapter: ClassVar[TypeAdapter[set[t.Container]] | None] = None
    _set_str_adapter: ClassVar[TypeAdapter[set[str]] | None] = None
    _set_scalar_adapter: ClassVar[TypeAdapter[set[t.Scalar]] | None] = None
    _sortable_dict_adapter: ClassVar[
        TypeAdapter[dict[t.SortableObjectType, t.Serializable | None]] | None
    ] = None
    _strict_json_list_adapter: ClassVar[TypeAdapter[list[t.StrictValue]] | None] = None
    _strict_json_scalar_adapter: ClassVar[TypeAdapter[t.Scalar] | None] = None
    _scalar_adapter: ClassVar[TypeAdapter[t.Scalar] | None] = None
    _float_adapter: ClassVar[TypeAdapter[float] | None] = None
    _str_adapter: ClassVar[TypeAdapter[str] | None] = None
    _str_list_adapter: ClassVar[TypeAdapter[list[str]] | None] = None
    _str_or_bytes_adapter: ClassVar[TypeAdapter[str | bytes] | None] = None
    _enum_type_adapter: ClassVar[TypeAdapter[type[StrEnum]] | None] = None
    _serializable_adapter: ClassVar[TypeAdapter[t.Serializable] | None] = None
    _metadata_json_dict_adapter: ClassVar[
        TypeAdapter[dict[str, t.Primitives]] | None
    ] = None
    _flat_metadata_dict_adapter: ClassVar[
        TypeAdapter[dict[str, t.Primitives]] | None
    ] = None

    @classmethod
    def get_tags_adapter(cls) -> TypeAdapter[list[str]]:
        if cls._tags_adapter is None:
            cls._tags_adapter = TypeAdapter(list[str])
        return cls._tags_adapter
```

**Why**: `TypeAdapter` instantiation is expensive. Caching as `ClassVar` ensures one instance per class, not per method call.

**Anti-pattern**:

```python
# ✗ WRONG — Creates new TypeAdapter on every call
def validate_tags(self, tags) -> list[str]:
    adapter = TypeAdapter(list[str])  # EXPENSIVE
    return adapter.validate_python(tags)
```

**Correct**:

```python
# ✓ CORRECT — Cached TypeAdapter
_tags_adapter: ClassVar[TypeAdapter[list[str]] | None] = None


@classmethod
def get_tags_adapter(cls) -> TypeAdapter[list[str]]:
    if cls._tags_adapter is None:
        cls._tags_adapter = TypeAdapter(list[str])
    return cls._tags_adapter


def validate_tags(self, tags) -> list[str]:
    return self.get_tags_adapter().validate_python(tags)
```

**Repository anchors**:
- `flext-core/src/flext_core/_models/base.py:53-102`
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

    def dispatch(self, command: BaseModel) -> r[BaseModel]: ...


# ABC — inheritance contract
class BaseHandler(ABC):
    """Abstract base for handlers with shared implementation."""

    @abstractmethod
    def handle(self, message: BaseModel) -> r[BaseModel]:
        """Subclasses MUST implement."""
        ...

    def validate(self, message: BaseModel) -> r[bool]:
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
        instance: FlextProtocols.Base | t.Container,
        protocol: type,
    ) -> bool:
        """Check if an instance implements a protocol."""
        registered_protocols = cls.get_class_protocols(instance.__class__)
        if protocol in registered_protocols:
            return True
        protocol_annotations: Mapping[str, object] = (
            protocol.__annotations__ if hasattr(protocol, "__annotations__") else {}
        )
        raw_attrs_candidate = getattr(protocol, "__protocol_attrs__", ())
        raw_attrs: set[str] = set[str]()
        iterable_attrs: Sequence[str] = ()
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
from pydantic import BaseModel, ConfigDict, Field


class StrictBoundaryModel(BaseModel):
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
    name: str = Field(..., description="Entity name")
    value: int = Field(..., ge=0, description="Non-negative value")
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
class MyModel(BaseModel):
    class Config:
        extra = "forbid"
```

**Correct**:

```python
# ✓ CORRECT — Pydantic v2 style
class MyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
```

**Repository anchors**:
- `flext-core/src/flext_core/_models/base.py` (`FrozenStrictModel`)
- `flext-core/src/flext_core/_models/cqrs.py:85-90`
- `flext-core/src/flext_core/settings.py`

### 7. Validation Boundaries

**Pattern**: Configurable validation depth via `FLEXT_METACLASS_STRICT` environment variable.

**Canonical Example**:

```python
import os
from pydantic import BaseModel, ConfigDict

# Read from environment
STRICT_MODE = os.getenv("FLEXT_METACLASS_STRICT", "false").lower() == "true"


class BoundaryModel(BaseModel):
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

```python
# ✗ WRONG — Any is forbidden
from typing import Any

data = ...  # FORBIDDEN
```

**Correct**: Use `t.*` contracts:

```python
# ✓ CORRECT — Use t.* contracts
from flext_core import t

data: t.Container = ...
metadata: t.MetadataValue = ...
config: t.ConfigMap = ...
```

#### 8.3 object — FORBIDDEN

```python
# ✗ WRONG — bare object is forbidden
data = ...  # FORBIDDEN
```

**Correct**: Use `t.*` contracts:

```python
# ✓ CORRECT — Use t.* contracts
from flext_core import t

data: t.Container = ...
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

#### 8.5 Double Field() assignment — FORBIDDEN

```python
# ✗ WRONG — Double Field() assignment
from typing import Annotated
from pydantic import BaseModel, Field


class Model(BaseModel):
    x: Annotated[str, Field(min_length=1)] = Field(default="")  # REDUNDANT
```

**Correct**: Field() ONLY in Annotated OR as default, not both:

```python
# ✓ CORRECT — Field() in Annotated
class Model(BaseModel):
    x: Annotated[str, Field(min_length=1, default="")] = ""


# ✓ CORRECT — Field() as default
class Model(BaseModel):
    x: str = Field(default="", min_length=1)
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

## Workflow

1. Read `AGENTS.md` §3.1-§3.3 for supreme law
2. Read `lib-pydantic-v2` for API rules
3. Read `pydantic-v2-patterns` for advanced patterns
4. Locate nearest codebase example for the pattern you need
5. Copy structure from real implementation
6. Adapt names/types while preserving validation semantics
7. Run `make validate PROJECT=<name>` to verify
8. Run `make validate PROJECT=<name> FIX=1` to auto-fix

## Examples

Good:

```python
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        json_schema_extra={
            "title": "User",
            "description": "User entity with strict validation",
        },
    )

    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="User full name",
            examples=["Alice Smith", "Bob Jones"],
        ),
    ]
    email: Annotated[
        str,
        Field(
            pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            description="User email address",
            examples=["alice@example.com"],
        ),
    ]
    tags: list[str] = Field(
        default_factory=list,
        description="User tags",
    )
```

Why good: Uses `Annotated` correctly, `Field()` with full metadata, `default_factory` for mutable default, `ConfigDict` for config.

Bad:

```python
from pydantic import BaseModel


class User(BaseModel):
    class Config:  # ✗ v1 style
        extra = "forbid"

    name: str  # ✗ No Field() metadata
    email: str  # ✗ No validation
    tags: list[str] = []  # ✗ Mutable default bug
```

Why bad: v1 `Config` class, no `Field()` metadata, mutable default bug.

## Verification

```bash
# Confirm skill exists
ls -1 .claude/skills/pydantic-v2-governance/SKILL.md

# Confirm frontmatter
rg -n "^name:|^description:" .claude/skills/pydantic-v2-governance/SKILL.md

# Confirm sections
for s in "## Scope" "## References" "## Rules" "## Instructions" "## Workflow" "## Examples" "## Verification"; do grep -q "$s" .claude/skills/pydantic-v2-governance/SKILL.md || echo "MISSING $s"; done

# Confirm no v1 patterns in codebase
rg -n "@validator\(" --glob "**/*.py" flext-core/src/ flext-grpc/src/
rg -n "\.dict\(\)|\.json\(\)" --glob "**/*.py" flext-core/src/
rg -n "class Config:" --glob "**/*.py" flext-core/src/

# Confirm no model_rebuild
rg -n "model_rebuild\(" --glob "**/*.py" flext-core/src/ flext-core/tests/

# Confirm TypeAdapter caching pattern
rg -n "ClassVar\[TypeAdapter" flext-core/src/flext_core/_models/base.py

# Confirm Annotated pattern
rg -n "Annotated\[.*\|.*None.*Field" flext-core/src/flext_core/_models/cqrs.py

# Run validation
make validate PROJECT=flext-core
make validate PROJECT=flext-core FIX=1
```
