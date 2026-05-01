## Python Version & Core Requirements

- **Python 3.13+** — Verified in `pyproject.toml` (`requires-python = ">=3.13"`)
  and `ruff-shared.toml` (`target-version = "py313"`)
- **Pydantic v2** — Required for all models (`pydantic>=2.0`)
- **`from **future** import annotations

from collections.abc import Mapping, Sequence`** in every file

## FLEXT Mapping-First Policy (Contract Layer)

- **Default contract type**: `Mapping[K, V]` for read-only boundaries.
- **Explicit mutable contract**: `MutableMapping[K, V]` only when mutation is part of the contract.
- **Bare `dict`, `list`, `set`, `tuple` are FORBIDDEN as type annotations** — use `collections.abc` abstractions exclusively.
- **Schema-bearing payloads**: prefer `TypedDict` or Pydantic models instead of plain map contracts.
- **Runtime checks**: prefer protocol/Mapping checks over `isinstance(x, dict)` unless dict-only behavior is required.

### Collections.abc Migration Rules

| Bare Type       | Read-Only            | Mutated                        |
| --------------- | -------------------- | ------------------------------ |
| `dict[K, V]`    | `Mapping[K, V]`      | `MutableMapping[K, V]`         |
| `list[X]`       | `Sequence[X]`        | `MutableSequence[X]`           |
| `set[X]`        | `AbstractSet[X]`     | Keep `set[X]` (see exceptions) |
| `tuple[X, ...]` | Keep `tuple[X, ...]` | N/A (immutable)                |

### Keep Concrete — Exceptions (CRITICAL)

These patterns MUST keep concrete `dict`/`list`/`set` types:

| Pattern                                   | Reason                                                          |
| ----------------------------------------- | --------------------------------------------------------------- |
| `r[list[X]]`, `r[dict[K,V]]`              | **r[T] is INVARIANT** — `r[Sequence[X]]` ≠ `r[list[X]]`         |
| `dict[str, list[X]]` from u.PrivateAttr | **Nested invariance** — return type must match concrete backing |
| `__all__: list[str]`                      | Python convention                                               |
| `u.Field(default_factory=list)`           | Pydantic internals require concrete                             |
| `u.PrivateAttr(default_factory=dict)`   | Pydantic internals require concrete                             |
| `ClassVar[list[...]]`                     | Class variable convention                                       |
| PEP 695 `type X = dict[...]`              | Type alias definitions                                          |
| Singer SDK method overrides               | Framework requires concrete `dict`/`list`                       |
| `isinstance(x, dict)`                     | Runtime check requires concrete type                            |
| `TypeAdapter(dict[...])`                  | Pydantic validation requires concrete                           |
| `set[X]` with `.update()`/`.discard()`    | `MutableSet` lacks these methods                                |

### Simplification Patterns

```python
# ❌ Unnecessary intermediate variable with append loop
results: MutableSequence[str] = []
for item in items:
    if item.is_valid:
        results.append(item.name)
return results

# ✅ Comprehension with Sequence (when not mutated after)
results: t.StrSequence = [item.name for item in items if item.is_valid]
return results

# ✅ match/case instead of isinstance chains (Python 3.13)
match value:
    case str():
        return value.upper()
    case int():
        return str(value)
    case _:
        return repr(value)
```

### Validation Command

```bash
ruff check --select=F821,F401,F811  # Verify no undefined names or unused imports
```

---

## Rule 1: NEVER Use `Any` or `object` (AXIOMATIC — Zero Tolerance)

### Replace with the appropriate type from the `FlextTypes` hierarchy

| Instead of              | Use                                          | When                                                           |       |         |        |           |
| ----------------------- | -------------------------------------------- | -------------------------------------------------------------- | ----- | ------- | ------ | --------- |
| `Any` / `object`        | Specific Pydantic Model                      | **MANDATORY**: For ALL domain entities and value objects       |       |         |        |           |
| `Any` / `object`        | `t.Scalar`                                   | Primitives: `str \                                             | int \ | float \ | bool \ | datetime` |
| `Mapping[*, *]`         | `FlextModels.Dict` / Model                   | Replaced by `RootModel` or specialized Pydantic models         |       |         |        |           |
| `Mapping[*, *]`         | `FlextModels.Dict` / Model                   | Replaced by `RootModel` or specialized Pydantic models         |       |         |        |           |
| Broad container aliases | `m.<Domain>.*Model` / `p.<Domain>.*Protocol` | Replace permissive contracts with explicit models/protocols    |       |         |        |           |
| `m.Dict`                | `FlextModels.Dict`                           | **Transitioning**: Prefer specialized models over generic dict |       |         |        |           |
| `Sequence[Any]`         | `Sequence[SpecificModel]`                    | Generic lists are forbidden                                    |       |         |        |           |
| `Sequence[Any]`         | `Sequence[SpecificModel]`                    | Read-only batch contracts                                      |       |         |        |           |

### The Type Hierarchy (from `typings.py` lines 153-176)

```text
Scalar-like contracts -> `t.Scalar` + domain value models (`m.<Domain>.ValueModel`)
Mapping contracts     -> domain mapping models (`m.<Domain>.ConfigModel`, `m.<Domain>.ServiceRegistryModel`)
Container contracts   -> explicit sequence/resource models (`m.<Domain>.BatchModel`, `m.<Domain>.ResourceModel`)
Fallibility contract  -> `r[T]`
```

## Verification

```bash
make val PROJECT=<name>
make val PROJECT=<name> FIX=1
make val PROJECTS="proj-a proj-b"
```

Custom checks for this skill must live in `.agents/skills/flext-strict-typing/` and emit `{"violation_count": N}` when using `type: custom`.

### Special RootModel Containers (from `typings.py` lines 357-462)

```python
m.Dict  # Transitional only — migrate to explicit domain dict models
m.Domain.ConfigModel  # Canonical strict settings contract
p.ServiceMap  # Transitional only — migrate to explicit service registry models
t.ErrorMap  # RootModel[Mapping[str, int | str | t.IntMapping]] — error types
t.JsonList  # Transitional only — migrate to t.SequenceOf[m.<Domain>.ItemModel]
t.FactoryMap  # RootModel[Mapping[str, FactoryRegistrationCallable]]
t.ResourceMap  # RootModel[Mapping[str, ResourceCallable]]
t.u.FieldValidatorMap  # RootModel[Mapping[str, Callable[[GVT], GVT]]]
```

---

## Rule 2: TypeAlias Declaration — PEP 695 Canonical

### `typings.py` aliases follow AGENTS.md: use `type X = ...` and keep runtime narrowing out of alias syntax

PEP 695 is the canonical alias syntax in `typings.py`. These aliases are annotation-only and MUST NOT be used in `isinstance()`, subclass clauses, or other runtime type-checking contexts.

```python
# Canonical alias style in typings.py
type JsonPrimitive = str | int | float | bool | None

type GeneralValueType = (
    Scalar
    | BaseModel
    | Path
    | t.SequenceOf[FlextTypes.GeneralValueType]
    | t.MappingKV[str, FlextTypes.GeneralValueType]
)
```

### Runtime narrowing — Use canonical `u.is_*()` helpers

When runtime narrowing is required, use the public guard utilities exposed through `u`, as required by AGENTS.md.

### FORBIDDEN PATTERNS

```python
# ❌ FORBIDDEN — runtime checks against alias syntax
isinstance(val, t.Primitives)
isinstance(val, t.Scalar)
isinstance(val, t.JsonValue)


# ❌ FORBIDDEN — subclassing a type alias
class Foo(t.JsonValue): ...
```

### CORRECT PATTERNS

```python
# ✅ CORRECT — alias syntax stays in typings.py
type Container = t.t.JsonValue

# ✅ CORRECT — runtime narrowing uses public guards
from flext_core import u

if u.is_scalar(val):
    ...
if u.is_container(val):
    ...
```

---

## Rule 3: TypeVars — Module-Level Only

All TypeVars are declared at module level in `typings.py`, not inside classes:

```python
# Module-level TypeVars (from typings.py lines 44-93)
T = TypeVar("T")  # Generic
T_co = TypeVar("T_co", covariant=True)  # Read-only
T_contra = TypeVar("T_contra", contravariant=True)  # Write-only
E = TypeVar("E")  # Element type
U = TypeVar("U")  # Utility type
R = TypeVar("R")  # Return type
P = ParamSpec("P")  # Decorator patterns

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
from flext_core import T, T_co, U, P, R, T_Model, T_Settings
```

---

## Rule 4: Modern Python Typing (Python 3.13+)

### Always use modern syntax (with Mapping-first contracts)

| Old (FORBIDDEN)         | New (REQUIRED)                                                    | Ruff Rule            |       |
| ----------------------- | ----------------------------------------------------------------- | -------------------- | ----- |
| `typing.List[X]`        | `Sequence[X]`                                                     | UP006                |       |
| `typing.Dict[str, X]`   | `Mapping[str, X]` (contract) / `Mapping[str, X]` (local mutation) | UP006 + FLEXT policy |       |
| `typing.Tuple[X, ...]`  | `tuple[X, ...]`                                                   | UP006                |       |
| `typing.Optional[X]`    | `X \                                                              | None`                | UP007 |
| `typing.Union[X, Y]`    | `X \                                                              | Y`                   | UP007 |
| `typing.Sequence`       | `collections.abc.Sequence`                                        | UP035                |       |
| `typing.Mapping`        | `collections.abc.Mapping`                                         | UP035                |       |
| `typing.Callable`       | `collections.abc.Callable`                                        | UP035                |       |
| `isinstance(x, (A, B))` | `isinstance(x, A \                                                | B)`                  | UP038 |

### Use `typing.Self` for return self patterns

```python
from typing import Self


class MyModel(m.BaseModel):
    def configure(self, x: int) -> Self:
        ...
        return self
```

---

## Rule 5: Pydantic v2 Model Typing (AXIOMATIC)

ALL code MUST follow "Pydantic v2 way" EXTENSIVELY across ALL 33 projects (`src/`, `tests/`, `examples/`). Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO — USE, USE, USE Pydantic v2 features to their fullest; if not using a feature, REVIEW and USE it; if not needed, use a simpler base and USE it fully.

**u.Field Declarations**: `u.Field()` for ALL field declarations with `description`, `title`, `examples`, `json_schema_extra` documenting business rules. u.Fields are self-documenting contracts, not bare attributes. `SecretStr`/`SecretBytes` for ALL sensitive values. Internal/private state MUST use `u.PrivateAttr()` — never bare `self._x = ...` assignments.

**Model Configuration**: `model_config = ConfigDict(...)` for ALL model configuration. Standalone `*Config` classes are TOTALLY FORBIDDEN — use `BaseSettings` or `ConfigDict` instead. Configuration values from `settings.py` (`s.*`).

**Validation**: Custom `@u.field_validator`/`@u.model_validator` MUST be minimized — prefer Pydantic v2 built-in constraints (`u.Field(ge=0, le=100)`, `Annotated[str, StringConstraints()]`, `Literal`, `constr`, `conint`, pattern constraints) before writing custom validators. Ad-hoc validation functions outside models are FORBIDDEN.

**FORBIDDEN Inside Model Classes**: Initialization helpers (`def setup()`, `def initialize()`), unnecessary `@property`, simple getters/setters, line-reduction wrappers, pass-through methods. If Pydantic v2 has a built-in mechanism (`@u.computed_field`, `model_post_init`, `__init_subclass__`, `u.PrivateAttr`), USE IT.

**Centralization**: `Enum`, `Mapping`, and `Literal` values MUST come from `constants.py` (`c.*`) — never defined inline. JSON via `model_dump_json()`, `model_validate_json()`, `model_dump()`, `TypeAdapter` — never raw `json.loads()`/`json.dumps()`.

**Scope**: Nested facade classes in modules MAY contain business logic methods beyond validation, but ALL their internal properties MUST use `u.Field()` and `u.PrivateAttr`. `models.py`/`models/` directories are for model definitions ONLY — remove business logic, utility functions, and orchestration code. Compatibility wrappers, legacy code, and non-business validation fallbacks are TOTALLY FORBIDDEN. Tests follow these exact same rules.

**AXIOMATIC — Integral Validation**: Every typing or model change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. ALL impacted references across ALL 33 projects MUST be immediately updated via ast-grep (`sg`) search-and-replace. Linter suppression comments (`# type: ignore`, `# noqa`, `# pyright: ignore`, `# pyrefly: ignore`, `# mypy: ignore`) are FORBIDDEN without: (1) real, verifiable internet citations, (2) explicit business necessity in the comment, (3) per-line only — never global. Fix the code, never silence the linter.

### ConfigDict (not inner `class Config`)

```python
# ✅ CORRECT — Pydantic v2 style
class MyModel(m.BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=True,
    )


# ❌ WRONG — Pydantic v1 style
class MyModel(m.BaseModel):
    class Config:
        validate_assignment = True
```

### u.Field declarations

```python
# ✅ CORRECT — Annotated with u.Field
name: str = u.Field(default="", description="Name")
items: t.StrSequence = u.Field(default_factory=list)
created_at: datetime = u.Field(default_factory=lambda: datetime.now(UTC))

# ❌ WRONG — No default_factory for mutable defaults
items: t.StrSequence = []  # Mutable default, use u.Field(default_factory=list)
```

### Validators use `@u.field_validator` and `@u.model_validator`

```python
from pydantic import u.field_validator, u.model_validator


class MyModel(m.BaseModel):
    name: str

    @u.field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @u.model_validator(mode="after")
    def validate_model(self) -> Self:
        ...
        return self
```

---

## Rule 6: Annotated Validation Types

Use `t.*` validation types for constrained scalar fields:

```python
from flext_core import t


class ServerConfig(m.BaseModel):
    port: t.PortNumber  # Annotated[int, Ge(1), Le(65535)]
    timeout: t.PositiveTimeout  # Annotated[float, Gt(0.0), Le(300.0)]
    retries: t.RetryCount  # Annotated[int, Ge(0), Le(10)]
    workers: t.WorkerCount  # Annotated[int, Ge(1), Le(100)]
```

---

## Rule 7: protocols.py — Structural Typing

All protocols in `protocols.py` are `@runtime_checkable` and use structural
typing (duck typing — no inheritance required for compliance):

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class SerializableRecord(Protocol):
    def to_dict(self) -> m.Domain.SerializedModel: ...
    def u.to_json(self) -> str: ...
```

- Protocols go in `protocols.py`, organized inside the `FlextProtocols` class
- Subprojects EXTEND protocols: `class FlextAuthProtocols(FlextProtocols): ...`

---

## Rule 8: Enum Typing — StrEnum Only

All enums use `StrEnum` (never `Enum`, `IntEnum`, or raw strings):

```python
from enum import StrEnum, unique


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
    DEFAULTS: Final[t.IntMapping] = MappingProxyType({"x": 1, "y": 2})
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
def process(self, data: m.Domain.ProcessInputModel) -> p.Result[bool]: ...


def validate(self, value: str) -> str: ...


# ✅ Use r[T] for operations that can fail
def load_config(self) -> p.Result[m.Domain.ConfigModel]: ...


# ❌ WRONG — Missing return type
def process(self, data): ...
```

---

## Rule 11: Callable Typing

Use specific callable types from `FlextTypes`:

```python
# Specific callable types from typings.py
p.HandlerCallable  # Prefer Callable[[m.<Domain>.InputModel], m.<Domain>.OutputModel]
t.ConditionCallable  # Prefer Callable[[m.<Domain>.InputModel], bool]
p.FactoryCallable  # Callable[[], t.RegisterableService]
p.ResourceCallable  # Prefer Callable[[], m.<Domain>.ResourceModel]
t.DecoratorType  # Callable[[HandlerCallable], HandlerCallable]

# For custom signatures, use import from collections.abc:
from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence

callback: Callable[[str, int], bool]
```

---

## Ruff Rules That Enforce Typing (from ruff-shared.toml)

Key rules in `[lint.select]`:

- `ANN` — All annotation rules (requires type hints everywhere)
- `UP` — pyupgrade (modern syntax enforcement)
- `TCH` — Type checking imports
- `PYI` — Stub file rules
- `RUF013` — Implicit `Optional` forbidden (use `X | None` explicitly)

Key rules in `[lint.ignore]`:

- `ANN101` — Missing `self` annotation (ignored, obvious)
- `ANN102` — Missing `cls` annotation (ignored, obvious)
- `ANN401` — `Any` usage (**AXIOMATIC**: MUST be enforced — `Any` is totally forbidden; use `t.*` contracts from `typings.py`)

## Zero Tolerance for Hacks (Mandatory)

1. **`model_rebuild()`** — PROHIBITED in all code. Resolve at definition time.
2. **`cast()`** — PROHIBITED in project code. Use `isinstance` or `TypeGuard`. (Exception: Only allowed in core `result.py`).
3. **`eval()` / `exec()`** — PROHIBITED.
4. **`inline imports`** — PROHIBITED.

---

## Rule 14: NEVER Use `str | None` When Default Is `""` — `| None` is INLINE-ONLY

If a Pydantic field has a string default (including `""`), `None` MUST NOT be in
the type unless `None` carries **distinct domain semantics** (e.g., "not yet configured"
vs "explicitly empty").

**AXIOMATIC**: `| None` MUST NEVER be baked into type alias definitions in `typings.py`.
Type aliases are ALWAYS non-nullable. Consumers add `| None` inline at the usage site
when business requires it. If a type needs nullable semantics, the developer writes
`t.Scalar | None` at the field/parameter declaration, NOT by defining a
`NullableScalarValue` alias in `typings.py`.

```python
# ❌ WRONG — None is semantically meaningless when default is ""
backup_path: str | None = u.Field(default="", description="Backup path.")
target_dn: str | None = u.Field(default="", description="Target DN.")

# ✅ CORRECT — just str with empty default
backup_path: str = u.Field(default="", description="Backup path.")
target_dn: str = u.Field(default="", description="Target DN.")

# ✅ CORRECT — None has distinct meaning ("not configured at all")
config_file: str | None = u.Field(
    default=None, description="Optional settings override."
)
```

**Decision tree**:

1. Is `None` a valid domain state distinct from `""`? → Use `str | None = u.Field(default=None)`
2. Is the field always a string, just sometimes empty? → Use `str = u.Field(default="")`
3. Is the field required? → Use `str` (no default)

**`typings.py` definition rule**:

1. Does the type alias definition in `typings.py` include `| None`? → VIOLATION. Remove `| None` from the alias. Consumers add `| None` inline at usage sites.
2. Need a nullable variant? → Write `field: t.Scalar | None = u.Field(default=None)` at the usage site. NEVER create `NullableScalarValue` or `Scalar | None` aliases.

---

## Rule 15: Pydantic Models Over Plain Helper Classes

Plain Python classes with `dict`/`MutableMapping` storage are **banned** for
domain state. Use Pydantic models instead, even for mutable processing helpers.

```python
# ❌ WRONG — plain class with dict storage
class PhaseResults:
    def __init__(self) -> None:
        _ = self.results: MutableMapping[int, OperationStats] = {}

# ✅ CORRECT — Pydantic model with proper typing
class PhaseResults(m.BaseModel):
    results: t.MappingKV[int, OperationStats] = u.Field(default_factory=dict)

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

## Rule 16: Result Protocol for `success` Pattern

Result models that expose outcome state MUST implement
`FlextProtocols.SuccessCheckable` (or the project-level equivalent) instead
of duplicating the property in every model.

```python
# In protocols.py:
@runtime_checkable
class SuccessCheckable(Protocol):
    @property
    def success(self) -> bool: ...


# In models.py — base for all result models:
class ResultBase(m.BaseModel):
    """Base for result models with success tracking."""

    success: bool = u.Field(default=False, description="Operation succeeded.")
    message: str = u.Field(default="", description="Human-readable result.")

    @property
    def failure(self) -> bool:
        return not self.success
```

This eliminates duplication across `m.Infra.MigrationResult`, `SyncResult`,
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
def is_config_map(val: m.Domain.UnknownInputModel) -> TypeGuard[m.Domain.ConfigModel]:
    return u.is_config_map(val)
```

**Polymorphic code → centralized Pydantic models**  
Dismantle polymorphic functions: replace multiple branches on type/union with a single contract. Use centralized Pydantic v2 models with validation (discriminated unions, `u.Field`, `u.model_validator`, `u.field_validator`). Prefer overloads or discriminated unions over loose `Union` handling in function bodies.

```python
# ❌ AVOID — many branches on polymorphic input in one function
def process(data: m.Domain.ProcessInputModel) -> p.Result[str]: ...


# ✅ PREFER — single model with validation
class ProcessInput(m.BaseModel):
    kind: Literal["str", "dict", "list"]
    value: m.Domain.ProcessValueModel

    @u.model_validator(mode="after")
    def check_kind_match(self): ...


def process(data: ProcessInput) -> Result: ...
```

---

## Mandatory Agent Instructions (Exigent)

Agents MUST apply the following when editing FLEXT code. No exceptions without explicit operator approval.

1. **Runtime aliases only**  
   Simple assignments only in package **init**: c = FlextConstants, m = FlextModels, etc. Never use u.Aliases or any alias registry. Access via project runtime alias only; no subdivision; MRO protocol only; direct methods.

2. **No type() for type narrowing**  
   Never use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or a `TypeGuard` so the type checker narrows correctly. Swapping `isinstance` for `type()` is forbidden.

3. **Dismantle polymorphic code**  
   Replace functions/methods that branch on multiple types (str | dict | list | BaseModel, etc.) with a single contract: centralized Pydantic v2 models, discriminated unions, `u.Field`, `@u.field_validator`, `@u.model_validator`. One entry point, validation in the model.

4. **No non-runtime aliases**  
   Remove compatibility or duplicate aliases (e.g. `LegacyX = NewX`, extra module-level aliases that mirror facades). Keep only the canonical runtime alias per facade (e.g. one `m`, one `c`, one `t` at package/project root).

5. **Direct methods only**  
   Remove loose wrappers and pass-through functions; call the canonical implementation directly. Prefer methods on the owning class over free functions that only delegate.

---

## Rule 12: r — The Sole Fallibility Mechanism (AXIOMATIC)

`r` (`r`) is the **MANDATORY** mechanism for expressing fallibility across ALL 33 projects. Any function that can fail, raise, or return "not found" MUST return `r[T]` — never `T | None`, never a bare exception, never an ad-hoc error dict. `r` exists to **ELIMINATE** `| None` return types and manual `try/except` in the business layer. Composition operators (`map`, `flat_map`, `lash`, `value_or`) MUST replace imperative `if result is None` / `try/except` chains. The `r` alias is MANDATORY at all usage sites — never spell out `r`. Only pure predicates (`-> bool`), `__init__` constructors, and trivially infallible derived fields may deviate — each MUST be justified in a code comment. Result-like carriers expose `success`/`failure`, never `is_success`/`is_failure`. Detailed generic behavior and edge cases follow; normative enforcement lives in `AGENTS.md` §3 Code Law.

### `r` Alias — Universal Import Pattern

```python
from flext_core import r, p, r
# Use `r` everywhere:
#   r[T].ok(value)  — success (subscript sets T from value)
#   r.fail("msg")   — failure (no subscript, U inferred from return context)
```

### `ok()` vs `fail()` — Asymmetric Generics

| Factory | Call Pattern      | Generic                                         | Why                                                    |
| ------- | ----------------- | ----------------------------------------------- | ------------------------------------------------------ |
| `ok`    | `r[T].ok(value)`  | Class-level `T` inferred from `value`           | Type checker sees `value: T`, infers `T`               |
| `fail`  | `r.fail("error")` | Method-level `[U]` inferred from return context | No success value → `U` comes from function return type |

### Internal Implementation Pattern (in `result.py`)

```python
from typing import cast


class r[T_co](u.RuntimeResult[T_co]):
    @classmethod
    def ok[T](cls, value: T) -> p.Result[T]:
        # T inferred from value — no cast needed
        return r[T](Success(value))

    @classmethod
    def fail[U](
        cls,
        error: str | None,
        error_code: str | None = None,
        error_data: m.Tests.ResultErrorDataModel | None = None,
    ) -> p.Result[U]:
        error_msg = error if error is not None else ""
        result = Failure(error_msg)
        # cast() required: Failure → Result[Never, str] is invariant,
        # cannot widen to r[U] without explicit bridge
        return cast(
            "r[U]",
            r(result, error_code=error_code, error_data=error_data),
        )
```

### Why `cast` Is Required

`Failure(msg)` produces `Result[Never, str]`. Since `r` is **invariant** in
`T_co`, the type checker cannot widen `r[Never]` to `r[U]`.
`cast("r[U]", ...)` explicitly tells the checker the intended type without
any runtime cost. The quoted form `"r[U]"` avoids runtime evaluation of the
generic subscript (ruff RUF046).

### Usage Examples

```python
# Return-type annotation drives U inference for fail():
def load(self) -> p.Result[float]:
    if not self._ready:
        return r.fail("Not ready")  # U inferred as float ✓
    return r[float].ok(self.value)  # T inferred from value ✓


# Chain composition:
def process(self) -> p.Result[str]:
    return (
        self.load().map(lambda v: f"Value: {v}")  # r[str]
    )
```
