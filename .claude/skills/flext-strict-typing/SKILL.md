<!-- TOC START -->
- [Python Version & Core Requirements](#python-version-core-requirements)
- [FLEXT Mapping-First Policy (Contract Layer)](#flext-mapping-first-policy-contract-layer)
- [Rule 1: NEVER Use `Any` or `object`](#rule-1-never-use-any-or-object)
  - [Replace with the appropriate type from the `FlextTypes` hierarchy](#replace-with-the-appropriate-type-from-the-flexttypes-hierarchy)
  - [The Type Hierarchy (from `typings.py` lines 153-176)](#the-type-hierarchy-from-typingspy-lines-153-176)
- [Verification](#verification)
  - [Special RootModel Containers (from `typings.py` lines 357-462)](#special-rootmodel-containers-from-typingspy-lines-357-462)
- [Rule 2: TypeAlias Declaration Format](#rule-2-typealias-declaration-format)
  - [Within the `FlextTypes` class — use `TypeAlias` annotation](#within-the-flexttypes-class-use-typealias-annotation)
  - [At module level — use PEP 695 `type` statement (required for recursive types)](#at-module-level-use-pep-695-type-statement-required-for-recursive-types)
- [Rule 3: TypeVars — Module-Level Only](#rule-3-typevars-module-level-only)
- [Rule 4: Modern Python Typing (Python 3.13+)](#rule-4-modern-python-typing-python-313)
  - [Always use modern syntax (with Mapping-first contracts)](#always-use-modern-syntax-with-mapping-first-contracts)
  - [Use `typing.Self` for return self patterns](#use-typingself-for-return-self-patterns)
- [Rule 5: Pydantic v2 Model Typing](#rule-5-pydantic-v2-model-typing)
  - [ConfigDict (not inner `class Config`)](#configdict-not-inner-class-config)
  - [Field declarations](#field-declarations)
  - [Validators use `@field_validator` and `@model_validator`](#validators-use-fieldvalidator-and-modelvalidator)
- [Rule 6: Annotated Validation Types](#rule-6-annotated-validation-types)
- [Rule 7: protocols.py — Structural Typing](#rule-7-protocolspy-structural-typing)
- [Rule 8: Enum Typing — StrEnum Only](#rule-8-enum-typing-strenum-only)
- [Rule 9: Constants Typing — Final + Immutable Collections](#rule-9-constants-typing-final-immutable-collections)
- [Rule 13: Advanced Fix Strategy (No Simplistic Rewrites)](#rule-13-advanced-fix-strategy-no-simplistic-rewrites)
- [Rule 10: Return Types — ALWAYS Explicit](#rule-10-return-types-always-explicit)
- [Rule 11: Callable Typing](#rule-11-callable-typing)
- [Ruff Rules That Enforce Typing (from ruff-shared.toml)](#ruff-rules-that-enforce-typing-from-ruff-sharedtoml)
- [Rule 14: NEVER Use `str | None` When Default Is `""`](#rule-14-never-use-str--none-when-default-is-)
- [Rule 15: Pydantic Models Over Plain Helper Classes](#rule-15-pydantic-models-over-plain-helper-classes)
- [Rule 16: Result Protocol for `is_success` Pattern](#rule-16-result-protocol-for-is_success-pattern)
- [Rule 17: Type Narrowing and Polymorphic Contracts (Mandatory)](#rule-17-type-narrowing-and-polymorphic-contracts-mandatory)
- [Rule 12: FlextResult Factory Method Typing](#rule-12-flextresult-factory-method-typing)
  - [`r` Alias — Universal Import Pattern](#r-alias-universal-import-pattern)
  - [`ok()` vs `fail()` — Asymmetric Generics](#ok-vs-fail-asymmetric-generics)
  - [Internal Implementation Pattern (in `result.py`)](#internal-implementation-pattern-in-resultpy)
  - [Why `cast` Is Required](#why-cast-is-required)
  - [Usage Examples](#usage-examples)
<!-- TOC END -->

---
name: flext-strict-typing
description: Verified type system rules, type hierarchy, and enforcement policies for the FLEXT ecosystem
---

# FLEXT Strict Typing Rules

**Reviewed**: 2026-02-21 | **Scope**: Added Rules 14-16 (str|None ban, helper class policy, is_success protocol)


> **Source of truth**: Extracted from `flext-core/src/flext_core/typings.py` (534 lines)
> and cross-referenced with `models.py`, `protocols.py`, and `ruff-shared.toml`.

> **Rule**: See `CLAUDE.md` §3 Code Law for canonical `FlextResult` and typing requirements.

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
make validate PROJECT=<name>
make validate PROJECT=<name> FIX=1
make validate PROJECTS="proj-a proj-b"
```

Custom checks for this skill must live in `.claude/skills/flext-strict-typing/` and emit `{"violation_count": N}` when using `type: custom`.

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

## Rule 14: NEVER Use `str | None` When Default Is `""`

If a Pydantic field has a string default (including `""`), `None` MUST NOT be in
the type unless `None` carries **distinct domain semantics** (e.g., "not yet configured"
vs "explicitly empty").

```python
# ❌ WRONG — None is semantically meaningless when default is ""
backup_path: str | None = Field(default="", description="Backup path.")
target_dn: str | None = Field(default="", description="Target DN.")

# ✅ CORRECT — just str with empty default
backup_path: str = Field(default="", description="Backup path.")
target_dn: str = Field(default="", description="Target DN.")

# ✅ CORRECT — None has distinct meaning ("not configured at all")
config_file: str | None = Field(default=None, description="Optional config override.")
```

**Decision tree**:
1. Is `None` a valid domain state distinct from `""`? → Use `str | None = Field(default=None)`
2. Is the field always a string, just sometimes empty? → Use `str = Field(default="")`
3. Is the field required? → Use `str` (no default)

---

## Rule 15: Pydantic Models Over Plain Helper Classes

Plain Python classes with `dict`/`MutableMapping` storage are **banned** for
domain state. Use Pydantic models instead, even for mutable processing helpers.

```python
# ❌ WRONG — plain class with dict storage
class PhaseResults:
    def __init__(self) -> None:
        self.results: MutableMapping[int, OperationStats] = {}

# ✅ CORRECT — Pydantic model with proper typing
class PhaseResults(BaseModel):
    results: Mapping[int, OperationStats] = Field(default_factory=dict)

    def with_result(self, phase: int, stats: OperationStats) -> PhaseResults:
        """Immutable update — returns new instance with added result."""
        updated = dict(self.results)
        updated[phase] = stats
        return self.model_copy(update={"results": updated})
```

**When plain classes ARE acceptable**:
- Pure utility/helper functions with no state
- Namespace classes (like `FlextModels`) that only organize nested types
- Protocol classes (structural typing contracts)

Everything else that holds state → Pydantic model.

---

## Rule 16: Result Protocol for `is_success` Pattern

Result models that expose an `is_success` property MUST implement
`FlextProtocols.SuccessCheckable` (or the project-level equivalent) instead
of duplicating the property in every model.

```python
# In protocols.py:
@runtime_checkable
class SuccessCheckable(Protocol):
    @property
    def is_success(self) -> bool: ...

# In models.py — base for all result models:
class ResultBase(BaseModel):
    """Base for result models with success tracking."""
    success: bool = Field(default=False, description="Operation succeeded.")
    message: str = Field(default="", description="Human-readable result.")

    @property
    def is_success(self) -> bool:
        return self.success
```

This eliminates duplication across `MigrationResult`, `SyncResult`,
`CleanResult`, `AclResult`, `ValidationResult`, etc.

---

## Rule 17: Type Narrowing and Polymorphic Contracts (Mandatory)

**Type narrowing**  
Use correct typing so the type checker can narrow. Do NOT use `type(x) is T` or `type(x) == T` for narrowing; use `isinstance(x, T)` or a `TypeGuard`. **Replacing `isinstance` with `type()` is FORBIDDEN** — it does not provide type narrowing and violates this rule.

```python
# ❌ FORBIDDEN — type() does not narrow for type checkers
if type(obj) is str:
    use(obj)  # type checker may not narrow

# ✅ CORRECT — isinstance narrows
if isinstance(obj, str):
    use(obj)  # str

# ✅ CORRECT — TypeGuard for custom predicates
def is_config_map(val: t.ConfigMapValue) -> TypeGuard[t.ConfigMap]:
    return isinstance(val, t.ConfigMap)
```

**Polymorphic code → centralized Pydantic models**  
Dismantle polymorphic functions: replace multiple branches on type/union with a single contract. Use centralized Pydantic v2 models with validation (discriminated unions, `Field`, `model_validator`, `field_validator`). Prefer overloads or discriminated unions over loose `Union` handling in function bodies.

```python
# ❌ AVOID — many branches on type in one function
def process(data: str | dict | list | BaseModel) -> Result:
    if isinstance(data, str): ...
    elif isinstance(data, dict): ...
    elif isinstance(data, list): ...

# ✅ PREFER — single model with validation
class ProcessInput(BaseModel):
    kind: Literal["str", "dict", "list"]
    value: str | dict[str, t.ConfigMapValue] | list[t.ConfigMapValue]
    @model_validator(mode="after")
    def check_kind_match(self): ...

def process(data: ProcessInput) -> Result: ...
```

---

## Mandatory Agent Instructions (Exigent)

Agents MUST apply the following when editing FLEXT code. No exceptions without explicit operator approval.

1. **Runtime aliases only**  
   Simple assignments only in package __init__: c = FlextConstants, m = FlextModels, etc. Never use FlextRuntime.Aliases or any alias registry. Access via project runtime alias only; no subdivision; MRO protocol only; direct methods.

2. **No type() for type narrowing**  
   Never use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or a `TypeGuard` so the type checker narrows correctly. Swapping `isinstance` for `type()` is forbidden.

3. **Dismantle polymorphic code**  
   Replace functions/methods that branch on multiple types (str | dict | list | BaseModel, etc.) with a single contract: centralized Pydantic v2 models, discriminated unions, `Field`, `@field_validator`, `@model_validator`. One entry point, validation in the model.

4. **No non-runtime aliases**  
   Remove compatibility or duplicate aliases (e.g. `LegacyX = NewX`, extra module-level aliases that mirror facades). Keep only the canonical runtime alias per facade (e.g. one `m`, one `c`, one `t` at package/project root).

5. **Direct methods only**  
   Remove loose wrappers and pass-through functions; call the canonical implementation directly. Prefer methods on the owning class over free functions that only delegate.

---

## Rule 12: FlextResult Factory Method Typing

This section keeps detailed generic behavior and edge cases; normative enforcement lives in `CLAUDE.md` §3 Code Law.

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
