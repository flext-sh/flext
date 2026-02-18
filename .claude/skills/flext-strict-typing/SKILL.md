---
name: flext-strict-typing
description: Verified type system rules, type hierarchy, and enforcement policies for the FLEXT ecosystem
---

# FLEXT Strict Typing Rules

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


> **Source of truth**: Extracted from `flext-core/src/flext_core/typings.py` (534 lines)
> and cross-referenced with `models.py`, `protocols.py`, and `ruff-shared.toml`.

## Python Version & Core Requirements

- **Python 3.13+** — Verified in `pyproject.toml` (`requires-python = ">=3.13"`)
  and `ruff-shared.toml` (`target-version = "py313"`)
- **Pydantic v2** — Required for all models (`pydantic>=2.0`)
- **`from __future__ import annotations`** in every file

## FLEXT Mapping-First Policy (Contract Layer)

- **Default contract type**: `Mapping[K, V]` for read-only boundaries.
- **Explicit mutable contract**: `MutableMapping[K, V]` only when mutation is part of the contract.
- **`dict[K, V]` is almost-banned in annotations**: keep `dict` primarily for local mutation hotspots and short-lived intermediate states.
- **Schema-bearing payloads**: prefer `TypedDict` or Pydantic models instead of plain map contracts.
- **Runtime checks**: prefer protocol/Mapping checks over `isinstance(x, dict)` unless dict-only behavior is required.

---

## Rule 1: NEVER Use `Any` or `object`

### Replace with the appropriate type from the `FlextTypes` hierarchy

| Instead of | Use | When |
| --- | --- | --- |
| `Any` | `t.GeneralValueType` | General-purpose value containers |
| `Any` | `t.ScalarValue` | Primitives: `str \| int \| float \| bool \| datetime \| None` |
| `Any` | `t.MetadataScalarValue` | Metadata: `str \| int \| float \| bool \| None` |
| `Any` | `t.JsonPrimitive` | JSON primitives: `str \| int \| float \| bool \| None` |
| `Any` | `t.JsonValue` | Full JSON values |
| `object` | `t.GeneralValueType` | Method params that accept "anything" |
| `dict[str, Any]` | `t.ConfigMap` | Configuration dictionaries |
| `dict[str, Any]` | `t.Dict` | General dictionaries |
| `dict[str, Any]` | `t.ServiceMap` | Service registry mappings |
| `list[Any]` | `list[t.GeneralValueType]` | Generic lists |
| `Sequence[Any]` | `t.ObjectList` | RootModel for batch operations |

### The Type Hierarchy (from `typings.py` lines 153-176)

```

## Verification

```bash
python3 scripts/core/skill_validate.py --skill flext-strict-typing --mode baseline
```

### Special RootModel Containers (from `typings.py` lines 357-462)

```python
t.Dict              # RootModel[dict[str, GeneralValueType]] — general dict
t.ConfigMap          # RootModel[dict[str, GeneralValueType]] — config dicts
t.ServiceMap         # RootModel[dict[str, GeneralValueType]] — service registry
t.ErrorMap           # RootModel[dict[str, int | str | dict[str, int]]] — error types
t.ObjectList         # RootModel[list[GeneralValueType]] — batch operations
t.FactoryMap         # RootModel[dict[str, FactoryRegistrationCallable]]
t.ResourceMap        # RootModel[dict[str, ResourceCallable]]
t.FieldValidatorMap  # RootModel[dict[str, Callable[[GVT], GVT]]]
```

---

## Rule 2: TypeAlias Declaration Format

### Within the `FlextTypes` class — use `TypeAlias` annotation

```python
# ✅ CORRECT — TypeAlias inside FlextTypes class
ScalarValue: TypeAlias = str | int | float | bool | datetime | None

# ❌ WRONG — PEP 695 `type` statement inside class (basedpyright incompatible)
# type ScalarValue = ...  # Don't use inside FlextTypes class
```

### At module level — use PEP 695 `type` statement (required for recursive types)

```python
# ✅ CORRECT — Module-level recursive type (PEP 695 required for Pydantic compat)
type GeneralValueType = (
    str | int | float | bool | datetime | None
    | BaseModel | Path
    | Sequence[GeneralValueType]
    | Mapping[str, GeneralValueType]
)

# ✅ CORRECT — Module-level simple types
type JsonPrimitive = str | int | float | bool | None
type ServiceInstanceType = GeneralValueType
type FactoryCallable = Callable[[], GeneralValueType]
```

---

## Rule 3: TypeVars — Module-Level Only

All TypeVars are declared at module level in `typings.py`, not inside classes:

```python
# Module-level TypeVars (from typings.py lines 44-93)
T = TypeVar("T")                                    # Generic
T_co = TypeVar("T_co", covariant=True)               # Read-only
T_contra = TypeVar("T_contra", contravariant=True)    # Write-only
E = TypeVar("E")                                     # Element type
U = TypeVar("U")                                     # Utility type
R = TypeVar("R")                                     # Return type
P = ParamSpec("P")                                   # Decorator patterns

# Handler TypeVars
MessageT_contra = TypeVar("MessageT_contra", contravariant=True)
ResultT = TypeVar("ResultT")

# Config/Model TypeVars
T_Model = TypeVar("T_Model", bound=BaseModel)
T_Namespace = TypeVar("T_Namespace")
T_Settings = TypeVar("T_Settings", bound=BaseSettings)
```

These are imported as:

```python
from flext_core.typings import T, T_co, U, P, R, T_Model, T_Settings
```

---

## Rule 4: Modern Python Typing (Python 3.13+)

### Always use modern syntax (with Mapping-first contracts)

| Old (FORBIDDEN) | New (REQUIRED) | Ruff Rule |
| --- | --- | --- |
| `typing.List[X]` | `list[X]` | UP006 |
| `typing.Dict[str, X]` | `Mapping[str, X]` (contract) / `dict[str, X]` (local mutation) | UP006 + FLEXT policy |
| `typing.Tuple[X, ...]` | `tuple[X, ...]` | UP006 |
| `typing.Optional[X]` | `X \| None` | UP007 |
| `typing.Union[X, Y]` | `X \| Y` | UP007 |
| `typing.Sequence` | `collections.abc.Sequence` | UP035 |
| `typing.Mapping` | `collections.abc.Mapping` | UP035 |
| `typing.Callable` | `collections.abc.Callable` | UP035 |
| `isinstance(x, (A, B))` | `isinstance(x, A \| B)` | UP038 |

### Use `typing.Self` for return self patterns

```python
from typing import Self

class MyModel(BaseModel):
    def configure(self, x: int) -> Self:
        ...
        return self
```

---

## Rule 5: Pydantic v2 Model Typing

### ConfigDict (not inner `class Config`)

```python
# ✅ CORRECT — Pydantic v2 style
class MyModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=True,
    )

# ❌ WRONG — Pydantic v1 style
class MyModel(BaseModel):
    class Config:
        validate_assignment = True
```

### Field declarations

```python
# ✅ CORRECT — Annotated with Field
name: str = Field(default="", description="Name")
items: list[str] = Field(default_factory=list)
created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

# ❌ WRONG — No default_factory for mutable defaults
items: list[str] = []  # Mutable default, use Field(default_factory=list)
```

### Validators use `@field_validator` and `@model_validator`

```python
from pydantic import field_validator, model_validator

class MyModel(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        ...
        return self
```

---

## Rule 6: Annotated Validation Types

Use `t.Validation.*` for constrained scalar fields:

```python
from flext_core.typings import t

class ServerConfig(BaseModel):
    port: t.Validation.PortNumber         # Annotated[int, Field(ge=1, le=65535)]
    timeout: t.Validation.PositiveTimeout  # Annotated[float, Field(gt=0.0, le=300.0)]
    retries: t.Validation.RetryCount      # Annotated[int, Field(ge=0, le=10)]
    workers: t.Validation.WorkerCount     # Annotated[int, Field(ge=1, le=100)]
```

---

## Rule 7: protocols.py — Structural Typing

All protocols in `protocols.py` are `@runtime_checkable` and use structural
typing (duck typing — no inheritance required for compliance):

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, t.GeneralValueType]: ...
    def to_json(self) -> str: ...
```

- Protocols go in `protocols.py`, organized inside the `FlextProtocols` class
- Subprojects EXTEND protocols: `class FlextAuthProtocols(FlextProtocols): ...`

---

## Rule 8: Enum Typing — StrEnum Only

All enums use `StrEnum` (never `Enum`, `IntEnum`, or raw strings):

```python
from enum import StrEnum

class TokenTypes(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    BEARER = "bearer"
```

Benefits:

- Pydantic v2 auto-validates against StrEnum members
- No need for `Literal` types for validation
- No need for `frozenset` for validation
- Serializes as string automatically

---

## Rule 9: Constants Typing — Final + Immutable Collections

```python
from typing import Final
from types import MappingProxyType
from collections.abc import Mapping, Set as AbstractSet

class FlextConstants:
    # Scalar constants: use Final
    MAX_RETRIES: Final[int] = 3
    DEFAULT_TIMEOUT: Final[float] = 30.0

    # Immutable sets: use frozenset with AbstractSet type
    VALID_TYPES: Final[AbstractSet[str]] = frozenset({"a", "b", "c"})

    # Immutable maps: use MappingProxyType with Mapping type
    DEFAULTS: Final[Mapping[str, int]] = MappingProxyType({"x": 1, "y": 2})
```

---

## Rule 13: Advanced Fix Strategy (No Simplistic Rewrites)

When a typing rule is violated, prefer architecture-aware fixes over mechanical substitutions:

1. **Contract intent analysis**: determine whether the boundary is read-only (`Mapping`) or mutating (`MutableMapping`).
2. **Mutation path isolation**: keep mutation localized; materialize `dict(...)` only at mutation hotspots.
3. **Schema upgrade**: if map keys are known/stable, upgrade to `TypedDict` or Pydantic model.
4. **Runtime compatibility review**: replacing `isinstance(x, dict)` with `isinstance(x, Mapping)` is semantic and must be reviewed manually.
5. **Auto-fix scope**: allow auto-fix only for unambiguous syntactic migrations (`typing.Dict -> Mapping`), then run semantic validation.

---

## Rule 10: Return Types — ALWAYS Explicit

```python
# ✅ Every function/method MUST have explicit return type
def process(self, data: t.GeneralValueType) -> FlextResult[bool]:
    ...

def validate(self, value: str) -> str:
    ...

# ✅ Use FlextResult[T] for operations that can fail
def load_config(self) -> FlextResult[t.ConfigMap]:
    ...

# ❌ WRONG — Missing return type
def process(self, data):
    ...
```

---

## Rule 11: Callable Typing

Use specific callable types from `FlextTypes`:

```python
# Specific callable types from typings.py
t.HandlerCallable      # Callable[[GeneralValueType], GeneralValueType]
t.ConditionCallable     # Callable[[GeneralValueType], bool]
t.FactoryCallable       # Callable[[], GeneralValueType]
t.ResourceCallable      # Callable[[], GeneralValueType]
t.DecoratorType         # Callable[[HandlerCallable], HandlerCallable]

# For custom signatures, use import from collections.abc:
from collections.abc import Callable
callback: Callable[[str, int], bool]
```

---

## Ruff Rules That Enforce Typing (from ruff-shared.toml)

Key rules in `[lint.select]`:

- `ANN` — All annotation rules (requires type hints everywhere)
- `UP` — pyupgrade (modern syntax enforcement)
- `TCH` — Type checking imports (move type-only imports to `TYPE_CHECKING`)
- `PYI` — Stub file rules
- `RUF013` — Implicit `Optional` forbidden (use `X | None` explicitly)

Key rules in `[lint.ignore]`:

- `ANN101` — Missing `self` annotation (ignored, obvious)
- `ANN102` — Missing `cls` annotation (ignored, obvious)
- `ANN401` — `Any` usage (currently ignored but SHOULD be enforced)

---

## Rule 12: FlextResult Factory Method Typing

### `r` Alias — Universal Import Pattern

```python
from flext_core import FlextResult, r
# Use `r` everywhere:
#   r[T].ok(value)  — success (subscript sets T from value)
#   r.fail("msg")   — failure (no subscript, U inferred from return context)
```

### `ok()` vs `fail()` — Asymmetric Generics

| Factory | Call Pattern | Generic | Why |
| --- | --- | --- | --- |
| `ok` | `r[T].ok(value)` | Class-level `T` inferred from `value` | Type checker sees `value: T`, infers `T` |
| `fail` | `r.fail("error")` | Method-level `[U]` inferred from return context | No success value → `U` comes from function return type |

### Internal Implementation Pattern (in `result.py`)

```python
from typing import cast

class FlextResult[T_co](FlextRuntime.RuntimeResult[T_co]):
    @classmethod
    def ok[T](cls, value: T) -> FlextResult[T]:
        # T inferred from value — no cast needed
        return FlextResult[T](Success(value))

    @classmethod
    def fail[U](
        cls,
        error: str | None,
        error_code: str | None = None,
        error_data: t.ConfigMap | None = None,
    ) -> FlextResult[U]:
        error_msg = error if error is not None else ""
        result = Failure(error_msg)
        # cast() required: Failure → Result[Never, str] is invariant,
        # cannot widen to FlextResult[U] without explicit bridge
        return cast(
            "FlextResult[U]",
            FlextResult(result, error_code=error_code, error_data=error_data),
        )
```

### Why `cast` Is Required

`Failure(msg)` produces `Result[Never, str]`. Since `FlextResult` is **invariant** in
`T_co`, the type checker cannot widen `FlextResult[Never]` to `FlextResult[U]`.
`cast("FlextResult[U]", ...)` explicitly tells the checker the intended type without
any runtime cost. The quoted form `"FlextResult[U]"` avoids runtime evaluation of the
generic subscript (ruff RUF046).

### Usage Examples

```python
# Return-type annotation drives U inference for fail():
def load(self) -> r[float]:
    if not self._ready:
        return r.fail("Not ready")      # U inferred as float ✓
    return r[float].ok(self._value)      # T inferred from value ✓

# Chain composition:
def process(self) -> r[str]:
    return (
        self.load()
        .map(lambda v: f"Value: {v}")    # FlextResult[str]
    )
```

