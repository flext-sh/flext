# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Strong Typing Overhaul — flext-core

## TL;DR

> **Quick Summary**: Close the flext-core type system triad (t ↔ p ↔ m). Tighten all loose types, expand `RegisterableService` with Protocol types, replace `HandlerType`, remove `t.Any` and dead aliases, bound TypeVars, standardize model field types, and resolve all 45 mypy errors.
>
> **Deliverables**:
> - Closed type system triad: types (t) feed protocols (p) and models (m), no gaps
> - Zero loose types (`object`, `Any`, `Callable[..., Any]`) in src/flext_core/
> - Dead aliases removed from typings.py (LaxStr, ScalarAlias, FlexibleValue, etc.)
> - All 45 mypy errors resolved
> - `make check` and `make test` pass
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves + final verification (3 parallel reviewers)
> **Critical Path**: Task 1 → Task 2+3 (parallel) → Task 4 → Task 5 → F1+F2+F3

---

## Context

### Original Request
User wants to tighten ALL types in flext-core using modern Python 3.13 PEPs, accepting ONLY what's actually used. No backward compatibility. Mandatory namespaced classes (c, t, p, m, u).

### Current State
- 45 mypy errors in src/flext_core/ (down from 88)
- Root cause of ~10 errors: `RegisterableService` too narrow (missing Protocol types Config, Context, CommandBus)
- Root cause of ~5 errors: `t.HandlerType = Callable[..., Any] | object` — absurdly loose
- Root cause of ~3 errors: `t.Any` alias wrapping `typing.Any`
- Remaining ~27 errors: various type mismatches (args.py, runtime.py, mapper.py, etc.)

### Research Findings (Complete)
- Full Protocol hierarchy mapped (30+ Protocols in protocols.py)
- All register() call sites traced — actual types: Config, Context, CommandBus, Logger, BaseModel subclasses
- HandlerType used in dispatcher: handlers are BaseModel instances OR callables, never raw `object`
- `t.Any` only in 3 context.py validators — receives raw Pydantic input before validation

---

## Work Objectives

### Core Objective
Tighten every type alias in flext-core to accept exactly what's used, using Python 3.13 PEP 695 syntax.

### Concrete Deliverables
- Expanded `p.RegisterableService` with exact Protocol types
- Replaced `t.HandlerType` with tight `Callable[..., _ContainerValue | None]` (no BaseModel, no object)
- Removed `t.Any` alias, replaced usages in validators with `object` (Pydantic mandate)
- All `t.RegisterableService` usages migrated to `p.RegisterableService`
- 0 mypy errors in `src/flext_core/`

### Definition of Done
- [ ] `python -m mypy src/flext_core/ --config-file=pyproject.toml` → 0 errors
- [ ] `make check` passes (or error count decreases)
- [ ] `make test` passes

### Must Have
- Types accept ONLY what's actually used — no broader
- PEP 695 `type` syntax for all type aliases
- Namespaced classes (c, t, p, m, u) — no divergence
- All Protocol types from protocols.py used where appropriate

### Must NOT Have (Guardrails)
- ❌ `object` as parameter type (except `__eq__` and TypeGuard inputs — Python mandates)
- ❌ `typing.Any` or `t.Any` anywhere
- ❌ `Callable[..., Any]` — must specify return type
- ❌ Backward compatibility shims
- ❌ Changes to `__eq__(self, other: object)` — Python protocol requirement
- ❌ Changes to TypeGuard function inputs from `object` — that IS their purpose
- ❌ Bounding covariant/contravariant TypeVars (T_co, T_contra, MessageT_contra)
- ❌ `# type: ignore`, `cast()`, root aliases
- ❌ Changes to Pydantic `mode="before"` validator inputs — they MUST accept `object` (Pydantic mandate)
- ❌ Adding BaseModel to HandlerLike without verifying dispatcher handles it (use Callable union only)

### Metis Review (Critical Corrections)
1. **HandlerLike must NOT include BaseModel** — dispatcher `_execute_handler` has isinstance checks for (DispatchMessageProtocol, HandleProtocol, ExecuteProtocol, callable). A bare BaseModel without handle/execute hits the `else` failure path. Correct HandlerLike: `Callable[..., _ContainerValue | None]` only. Model-based handlers implement HandleProtocol structurally.
2. **`_is_registerable_service()` guard must be updated** — currently accepts `hasattr(value, '__dict__')` (any object). Must be updated to match the expanded `p.RegisterableService` static type. Both changes must be atomic.
3. **Pydantic `mode='before'` validators use `object`, not `t.GuardInputValue`** — The 3 uses of `t.Any` in `_models/context.py` receive pre-validation input of arbitrary type from Pydantic internals. Replace with `object` (Python-mandated, like `__eq__`), NOT the narrower `t.GuardInputValue`.

### Protocol Standardization Rules (Python 3.13 + Pydantic v2 + SOLID)

Research findings from Python 3.13 typing docs, PEP 544/695, Pydantic v2 internals, and production patterns:

**1. Metaclass Resolution (ALREADY CORRECT)**
flext-core's `_CombinedModelMeta = type("_CombinedModelMeta", (type(BaseModel), type(Protocol)), {})` is the canonical
pattern for resolving Protocol + Pydantic metaclass conflict. `ProtocolModelMeta(_CombinedModelMeta)` correctly separates
Protocol bases from model bases. NO CHANGES NEEDED here — this is production-grade.

**2. PEP 695 Generic Syntax (MODERNIZE)**
Python 3.13 canonical: `class Handler[MessageT, ResultT](Protocol):` (square-bracket syntax).
Old: `Handler(Protocol[MessageT_contra, ResultT])` is legacy for 3.13+.
Variance is now INFERRED by default — explicit `covariant=True` mostly unnecessary.
ACTION: Evaluate which Protocols use old-style generics and modernize to PEP 695 in a FUTURE task
(not in this plan — scope is type alias tightening, not Protocol syntax modernization).

**3. @runtime_checkable Performance (AUDIT NEEDED — FUTURE)**
`isinstance()` against `@runtime_checkable` Protocols has O(n) complexity per member, NOT cached.
ALL 30+ Protocols in flext-core are `@runtime_checkable`. This is a performance concern for hot paths.
RECOMMENDATION: In a future pass, audit which Protocols NEED runtime checks vs static-only.
For THIS plan: leave all as `@runtime_checkable` (changing would break runtime isinstance checks in container/guards).

**4. ISP Compliance (ALREADY GOOD)**
flext-core already follows Interface Segregation well:
- Small atomic Protocols: `BaseProtocol` (1 method), `Routable` (3 properties), `HasModelDump` (1 method)
- Composition via multiple inheritance: `Config(HasModelDump, BaseProtocol, Protocol)`, `DI(Configurable, Protocol)`
- Fat interfaces split: `Result[T]` (25+ methods) is the only large Protocol, justified by railway-oriented pattern.
NO CHANGES NEEDED — architecture is SOLID-compliant.

**5. DIP via Protocol-Based DI (VALIDATE)**
The `p.DI` Protocol defines the container contract with typed methods (`register`, `get`, `get_typed[T]`).
Expanding `p.RegisterableService` to include Protocol types (Config, Context, etc.) strengthens DIP
by ensuring the container formally accepts its own abstract contracts as services.
ACTION: Task 1 expands RegisterableService — this IS the DIP improvement.

**6. Structural Subtyping Pitfalls (APPLY IN TASK 4)**
- **Attribute invariance**: Protocol attributes must match EXACTLY (not subtype). `attr: float` requires `float`, not `int`.
- **Parameter name matching**: Method parameter names in implementations MUST match Protocol definitions.
- **mypy strictness**: mypy requires explicit member definitions; `__getattr__` won't satisfy Protocol.
ACTION: Task 4 must check that all Protocol implementations match parameter names and attribute types exactly.

**7. Protocol vs ABC Decision (RULE)**
- Use **Protocols** for: service contracts, DI boundaries, structural typing (3rd-party compatible).
- Use **ABC** for: internal hierarchies with shared implementation logic (e.g., `FlextService` base class).
- NEVER mix: a class should not inherit both a Protocol and an ABC for the same concern.
flext-core currently uses Protocols correctly for contracts and ABC (via FlextService) for shared logic.

---

### Type System Triad Architecture (t ↔ p ↔ m)

The flext-core type system is a closed triad of three namespaced pillars.
ALL code in flext-core and consumer projects MUST use these pillars — no raw types.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLEXT TYPE SYSTEM TRIAD                         │
│                                                                     │
│   t (FlextTypes/typings.py)     p (FlextProtocols/protocols.py)    │
│   ┌───────────────────┐         ┌─────────────────────────┐        │
│   │ Type Aliases       │────────>│ Protocol Contracts      │        │
│   │ - _ContainerValue  │         │ - RegisterableService   │        │
│   │ - ScalarValue      │         │ - Config, Context, DI   │        │
│   │ - GuardInputValue  │         │ - Handler, CommandBus   │        │
│   │ - HandlerLike      │         │ - Result, ResultLike    │        │
│   │ - ConfigMapValue   │         │ - Service, Repository   │        │
│   └───────────┬───────┘         └────────────┬────────────┘        │
│               │                               │                     │
│               └───────────┐   ┌───────────────┘                     │
│                           ▼   ▼                                     │
│                 m (FlextModels/_models/)                            │
│                 ┌───────────────────────┐                           │
│                 │ Pydantic Models        │                          │
│                 │ - ServiceRegistration  │                          │
│                 │ - ContextData          │                          │
│                 │ - ServiceRuntime       │                          │
│                 │ - Entity, Value, Agg.  │                          │
│                 └───────────────────────┘                           │
│                                                                     │
│  RULES:                                                            │
│  1. Types (t) define WHAT values look like (unions, scalars)        │
│  2. Protocols (p) define WHAT behavior is expected (contracts)      │
│  3. Models (m) IMPLEMENT protocols using types as field annotations │
│  4. t feeds into p (method signatures) and m (field types)          │
│  5. p feeds into m (base classes, Protocol compliance)              │
│  6. m NEVER feeds back into t or p (no circular dependency)         │
└─────────────────────────────────────────────────────────────────────┘
```

**Type Flow Rules (ENFORCE IN ALL CODE):**
1. Model fields MUST use `t.*` aliases (e.g., `t.GuardInputValue`) — never raw `str | int | float`
2. Protocol method signatures MUST use `t.*` aliases — never `typing.Any` or bare `object`
3. DI-connected models MUST declare Protocol compliance via field types from `p.*`
4. `m.ServiceRuntime(config: p.Config, context: p.Context, container: p.DI)` is the canonical pattern
5. Container operations MUST accept `p.RegisterableService` — the single source of truth
6. Dead type aliases MUST be removed — only aliases actively used in p or m survive

**Identified Dead Aliases (to remove from typings.py):**
- `t.Any` — PROHIBITED, wraps `typing.Any`
- `t.LaxStr` — unused in any Protocol or Model
- `t.ScalarAlias` — redundant, identical to `t.ScalarValue`
- `t.FlexibleValue` — redundant, identical to `t.GuardInputValue` and `t.ConfigMapValue`
- `t.AcceptableMessageType` — unused in Protocols
- `t.ConditionCallable` — unused in Protocols
- `t.HandlerType` — REPLACED by `t.HandlerLike`

**Identified Unbound TypeVar (to fix):**
- `TModel` (line 50) — unbound, should be `TypeVar('TModel', bound=BaseModel)`

**Model ↔ Protocol Gaps (to close):**
- `ServiceRegistration.service` uses `t.RegisterableService` → must use `p.RegisterableService`
- `validate_service_type()` accepts `object` + `hasattr(v, '__dict__')` → must match `p.RegisterableService`
- `_models/context.py` uses `t.Any` in 3 validators → must use `object` (Pydantic mandate)


## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after (verify no regressions)
- **Framework**: pytest (via `make test`)

### QA Policy
Every task verified by running mypy and tests. Evidence: error counts before/after.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — type definitions + cleanup):
├── Task 1: Expand p.RegisterableService + fix HandlerType + remove t.Any + dead aliases [deep]

Wave 2 (Propagation — use new types, MAX PARALLEL):
├── Task 2: Migrate t.RegisterableService → p.RegisterableService + fix model types [quick]
├── Task 3: Migrate t.HandlerType → t.HandlerLike + fix t.Any in validators [quick]

Wave 3 (Remaining errors + model standardization):
├── Task 4: Fix remaining mypy errors + enforce triad type rules [deep]
├── Task 5: Final verification — make check + make test [quick]

Wave FINAL (Verification — 4 parallel):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Dead alias + triad compliance check [quick]
```

### Dependency Matrix
- **1**: None — start immediately
- **2**: Depends on 1 (needs expanded p.RegisterableService)
- **3**: Depends on 1 (needs t.HandlerLike definition)
- **4**: Depends on 2, 3 (needs all type migrations done)
- **5**: Depends on 4

---

## TODOs

- [ ] 1. Tighten type definitions in protocols.py + typings.py

  **What to do**:

  **1a. Expand `p.RegisterableService` in protocols.py (line 1531-1533)**

  Current:
  ```python
      type RegisterableService = (
          t.GeneralValueType | BindableLogger | Callable[..., t.GeneralValueType]
      )
  ```

  Replace with:
  ```python
      type RegisterableService = (
          t.GeneralValueType
          | BindableLogger
          | Callable[..., t.GeneralValueType]
          | Config
          | Context
          | DI
          | Service
          | CommandBus
          | Registrable
      )
  ```

  These are nested classes in FlextProtocols — accessible by short name in the class body.
  PEP 695 `type` statements evaluate lazily with class namespace access.

  **1b. Replace `t.HandlerType` in typings.py (line 169)**

  Current:
  ```python
      type HandlerType = Callable[..., Any] | object
  ```

  Replace with — rename to `HandlerLike` for clarity (METIS CORRECTION: no BaseModel, callables only):
  ```python
      type HandlerLike = Callable[..., _ContainerValue | None]
  ```

  Why (Metis correction): Dispatcher `_execute_handler` uses isinstance checks for
  DispatchMessageProtocol, HandleProtocol, ExecuteProtocol, then callable.
  A bare BaseModel without handle/execute hits the `else` failure path.
  Model-based handlers (FlextHandlers) implement HandleProtocol structurally,
  so they match as callables or protocol instances — BaseModel in the union is wrong.

  **1c. Remove `t.Any` alias in typings.py (line 94)**

  Current:
  ```python
      Any: TypeAlias = typing.Any
  ```

  DELETE this line entirely.
  METIS CORRECTION: Replace usages in `_models/context.py` with `object` (NOT `t.GuardInputValue`).
  Pydantic `mode='before'` validators receive arbitrary pre-validation input — `object` is mandated.
  This is the same exemption as `__eq__(self, other: object)` — a Python/Pydantic requirement.

  **1d. Add HandlerLike as TypeAlias in FlextTypes class (after removing HandlerType)**

  Add near line 166 (after HandlerCallable):
  ```python
      HandlerLike: TypeAlias = HandlerLike  # PEP 695 module-level → class alias
  ```

  Wait — since line 169 is INSIDE FlextTypes class (4-space indent), the PEP 695 `type HandlerLike` is already a class-level name. No extra TypeAlias needed. Just rename the `type` statement.

  **1e. Remove dead aliases from typings.py (Type Triad cleanup)**

  DELETE the following dead/redundant aliases from FlextTypes class:
  ```python
  # LINE 94 — t.Any (already handled in 1c)
  Any: TypeAlias = typing.Any  # DELETE

  # LINE ~94 — t.LaxStr (unused in any Protocol or Model)
  LaxStr: TypeAlias = str | bytes | bytearray  # DELETE

  # LINE ~99 — t.ScalarAlias (redundant, identical to ScalarValue)
  ScalarAlias: TypeAlias = ScalarValue  # DELETE

  # LINE ~109 — t.FlexibleValue (redundant, identical to GuardInputValue/ConfigMapValue)
  FlexibleValue: TypeAlias = _ContainerValue  # DELETE

  # LINE ~169 — t.AcceptableMessageType (unused in Protocols)
  AcceptableMessageType: TypeAlias = ScalarValue | BaseModel | Sequence[ScalarValue]  # DELETE

  # LINE ~170 — t.ConditionCallable (unused in Protocols)
  ConditionCallable: TypeAlias = Callable[[ScalarValue], bool]  # DELETE

  # LINE 171 — t.HandlerType (already handled in 1b — replaced by HandlerLike)
  ```

  IMPORTANT: Before deleting, grep each alias across the FULL workspace:
  ```bash
  grep -rn 't\.LaxStr\|t\.ScalarAlias\|t\.FlexibleValue\|t\.AcceptableMessageType\|t\.ConditionCallable' --include='*.py' /home/marlonsc/flext/*/src/
  ```
  If ANY external project uses the alias, keep it but mark as `@deprecated` in docstring.
  If no usages, delete.

  **1f. Bound unbound TModel TypeVar (line 50)**

  Current:
  ```python
  TModel = TypeVar('TModel')
  ```

  Replace with:
  ```python
  TModel = TypeVar('TModel', bound=BaseModel)
  ```

  This TypeVar is used for generic model operations — it MUST be bounded to BaseModel
  to prevent passing arbitrary types where Pydantic models are expected.
  **Must NOT do**:
  - Do NOT change `__eq__(self, other: object)` signatures anywhere
  - Do NOT change TypeGuard function inputs from `object`
  - Do NOT bound T_co, T_contra, MessageT_contra

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (foundation task)
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None

  **References**:
  - `src/flext_core/protocols.py:1531-1533` — Current RegisterableService definition to expand
  - `src/flext_core/protocols.py:826` — Handler Protocol (used in expansion)
  - `src/flext_core/protocols.py:350-700` — Config, Context, DI, Service, CommandBus Protocol definitions
  - `src/flext_core/typings.py:169` — Current HandlerType to replace
  - `src/flext_core/typings.py:94` — t.Any to remove
  - `src/flext_core/typings.py:52-63` — _ContainerValue definition (used in HandlerLike)
  - `src/flext_core/typings.py:105` — t.GuardInputValue (replacement for t.Any)

  **Acceptance Criteria**:
  - [ ] `p.RegisterableService` includes Config, Context, DI, Service, CommandBus, Registrable
  - [ ] `t.HandlerLike` = `Callable[..., _ContainerValue | None]` (no `Any`, no `object`, no BaseModel — Metis correction)
  - [ ] `t.Any` line deleted from typings.py
  - [ ] `python -m mypy src/flext_core/typings.py --config-file=pyproject.toml` → 0 errors
  - [ ] `python -m mypy src/flext_core/protocols.py --config-file=pyproject.toml` → ≤4 errors (attr-defined are pre-existing)

  **QA Scenarios**:
  ```
  Scenario: RegisterableService accepts Protocol types
    Tool: Bash
    Steps:
      1. python -m mypy src/flext_core/protocols.py --config-file=pyproject.toml 2>&1 | grep "RegisterableService"
    Expected Result: No errors mentioning RegisterableService
    Evidence: .sisyphus/evidence/task-1-registerable-service.txt

  Scenario: HandlerLike rejects object and Any
    Tool: Bash
    Steps:
      1. grep -n "Callable\[\.\.\..*Any\]\|: object" src/flext_core/typings.py
    Expected Result: No matches (no Any in callable return, no bare object)
    Evidence: .sisyphus/evidence/task-1-handler-like.txt
  ```

  **Commit**: YES
  - Message: `fix(types): tighten RegisterableService with Protocol types, replace HandlerType, remove t.Any`
  - Files: `src/flext_core/protocols.py`, `src/flext_core/typings.py`
  - Pre-commit: `python -m mypy src/flext_core/typings.py src/flext_core/protocols.py --config-file=pyproject.toml`

---

- [ ] 2. Migrate all `t.RegisterableService` → `p.RegisterableService`

  **What to do**:

  Replace ALL occurrences of `t.RegisterableService` with `p.RegisterableService` in the following files.
  The `p` import (FlextProtocols) is already available in all these files.

  **File-by-file changes** (exact line numbers from grep):

  **container.py** (18 occurrences):
  Lines: 229, 269, 302, 305, 743, 777, 826(x2), 850, 908, 919, 940, 943, 956, 959, 961, 969, 972, 974, 976, 987, 1204
  - Simple find/replace: `t.RegisterableService` → `p.RegisterableService`
  - Line 987 (`_is_registerable_service`): keep `TypeGuard[p.RegisterableService]`
  - Ensure `p` is imported (it IS — line 33 of container.py)

  **registry.py** (4 occurrences):
  Lines: 736, 750, 756, 760
  - Simple find/replace: `t.RegisterableService` → `p.RegisterableService`

  **service.py** (5 occurrences):
  Lines: 170, 290, 291, 296, 317
  - Simple find/replace: `t.RegisterableService` → `p.RegisterableService`
  - Verify `p` is imported (add `from flext_core import p` if missing)

  **mixins.py** (1 occurrence):
  Line: 457
  - `t.RegisterableService` → `p.RegisterableService`
  - Verify `p` is imported

  **runtime.py** (1 occurrence):
  Line: 810
  - `t.RegisterableService` → `p.RegisterableService`
  - Verify `p` is imported

  **_models/container.py** (2 occurrences):
  Lines: 87, 178
  - `t.RegisterableService` → `p.RegisterableService`
  - Verify `p` is imported (add if missing)

  **protocols.py** (7 occurrences — DI Protocol methods):
  Lines: 288, 624, 652, 668, 684
  - IMPORTANT: Inside FlextProtocols class, these are in nested Protocol classes
  - With `from __future__ import annotations`, annotations are strings
  - Change `t.RegisterableService` → `RegisterableService` (unqualified — resolves to the class-level type alias)
  - If mypy can't resolve unqualified name in nested class: keep `t.RegisterableService` (the narrow type is OK for Protocol definition — implementation can be wider)

  **Also**: Remove the now-dead `RegisterableService: TypeAlias = RegisterableService` from FlextTypes class (typings.py line 109) and the module-level `type RegisterableService` (typings.py lines 72-74). These are superseded by `p.RegisterableService`.
  WAIT — keep them if any external project imports `t.RegisterableService`. Check first:
  ```bash
  grep -rn "t\.RegisterableService" --include="*.py" /home/marlonsc/flext/*/src/ | grep -v flext-core
  ```
  If no external usages, remove. If external usages exist, keep as deprecated alias pointing to the narrow type (they'll be updated in consumer propagation phase).

  **Also**: Fix `_class_plugin_storage` type in registry.py line 109:
  ```python
  # Current:
  _class_plugin_storage: ClassVar[MutableMapping[str, t.RegistrablePlugin]] = {}
  # Fix to:
  _class_plugin_storage: ClassVar[MutableMapping[str, p.Registrable]] = {}
  ```

  **METIS CORRECTION**: Also update `_is_registerable_service()` runtime guard in container.py.
  Currently accepts `hasattr(value, '__dict__')` (any Python object).
  Must be updated to match the expanded `p.RegisterableService` static type.
  Both changes (static type + runtime guard) must be atomic to avoid divergence.
  The guard should check for Protocol types explicitly (isinstance checks for Config, Context, etc.).

  **Must NOT do**:
  - Do NOT change `t.RegisterableService` in test files or examples (separate task)
  - Do NOT remove `RegisterableService` from typings.py if external projects use it

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3)
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1

  **References**:
  - `src/flext_core/container.py` — Primary target, 18 occurrences
  - `src/flext_core/registry.py` — 4 occurrences + _class_plugin_storage fix
  - `src/flext_core/service.py` — 5 occurrences
  - `src/flext_core/mixins.py:457` — 1 occurrence
  - `src/flext_core/runtime.py:810` — 1 occurrence
  - `src/flext_core/_models/container.py:87,178` — 2 occurrences
  - `src/flext_core/protocols.py:288,624,652,668,684` — DI Protocol methods

  **Acceptance Criteria**:
  - [ ] `grep -rn "t\.RegisterableService" src/flext_core/` → 0 matches (or only in typings.py alias)
  - [ ] `python -m mypy src/flext_core/container.py --config-file=pyproject.toml` → no RegisterableService errors
  - [ ] container.py errors about Config/Context/FlextDispatcher → GONE

  **QA Scenarios**:
  ```
  Scenario: No t.RegisterableService remains in src code
    Tool: Bash
    Steps:
      1. grep -rn "t\.RegisterableService" src/flext_core/ | grep -v typings.py | grep -v __pycache__
    Expected Result: 0 matches
    Evidence: .sisyphus/evidence/task-2-no-t-registerable.txt

  Scenario: Container accepts Protocol types without error
    Tool: Bash
    Steps:
      1. python -m mypy src/flext_core/container.py --config-file=pyproject.toml 2>&1 | grep -c "error:"
    Expected Result: ≤3 errors (down from 7)
    Evidence: .sisyphus/evidence/task-2-container-mypy.txt
  ```

  **Commit**: YES
  - Message: `refactor(types): migrate t.RegisterableService → p.RegisterableService across flext-core`
  - Files: container.py, registry.py, service.py, mixins.py, runtime.py, _models/container.py, protocols.py
  - Pre-commit: `python -m mypy src/flext_core/ --config-file=pyproject.toml 2>&1 | tail -3`

---

- [ ] 3. Migrate all `t.HandlerType` → `t.HandlerLike`

  **What to do**:

  Replace ALL `t.HandlerType` with `t.HandlerLike` across the codebase.

  **File-by-file changes**:

  **dispatcher.py** (6 occurrences):
  Lines: 59, 60, 61, 65, 197
  - `t.HandlerType` → `t.HandlerLike`

  **protocols.py** (1 occurrence):
  Line: 865 (CommandBus.register_handler)
  - `t.HandlerType` → `t.HandlerLike`

  **registry.py** (2 occurrences):
  Lines: 260, 261
  - `t.HandlerType` → `t.HandlerLike`

  **guards.py** (6 occurrences — TypeGuard):
  Lines: 177, 178, 180, 182, 189, 194
  - `t.HandlerType` → `t.HandlerLike` in TypeGuard return type and docstrings
  - The TypeGuard function `is_handler_type` checks if value is callable or BaseModel — update checks to match new type definition
  - Input parameter stays `object` (TypeGuard mandate)

  **Also**: Update `_models/context.py` — replace `t.Any` usages (METIS CORRECTION: use `object`):
  Lines: 31, 43, 53
  ```python
  # Line 31: def _normalize_to_mapping(v: t.Any) → change to:
  def _normalize_to_mapping(v: object) -> Mapping[str, t.GuardInputValue]:

  # Line 43: def _normalize_metadata_before(v: t.Any) -> t.Any → change to:
  def _normalize_metadata_before(v: object) -> object:

  # Line 53: def _normalize_statistics_before(v: t.Any) → change to:
  def _normalize_statistics_before(v: object) -> Mapping[str, t.GuardInputValue]:
  ```

  METIS CORRECTION: These are Pydantic `mode='before'` validators. They receive arbitrary
  pre-validation input from Pydantic internals — `object` is the correct type (same exemption
  as `__eq__`). Using `t.GuardInputValue` would be too narrow and cause runtime failures.

  **Must NOT do**:
  - Do NOT change `c.Cqrs.HandlerType` (StrEnum) — that's the VALID one
  - Do NOT remove the `is_handler_type` TypeGuard function (still useful for narrowing)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 2 (with Task 2)
  - **Blocks**: Task 4
  - **Blocked By**: Task 1

  **References**:
  - `src/flext_core/dispatcher.py:59-65,197` — Handler storage and registration
  - `src/flext_core/protocols.py:865` — CommandBus.register_handler Protocol
  - `src/flext_core/registry.py:260-261` — Handler conversion
  - `src/flext_core/_utilities/guards.py:177-194` — TypeGuard for handler type
  - `src/flext_core/_models/context.py:31,43,53` — t.Any usages to replace
  - `src/flext_core/constants.py:826` — c.Cqrs.HandlerType StrEnum (DO NOT TOUCH)

  **Acceptance Criteria**:
  - [ ] `grep -rn "t\.HandlerType" src/flext_core/` → 0 matches
  - [ ] `grep -rn "t\.Any[^a-zA-Z]" src/flext_core/` → 0 matches
  - [ ] `c.Cqrs.HandlerType` unchanged (still StrEnum)
  - [ ] `python -m mypy src/flext_core/dispatcher.py --config-file=pyproject.toml` → 0 errors

  **QA Scenarios**:
  ```
  Scenario: No t.HandlerType or t.Any remains
    Tool: Bash
    Steps:
      1. grep -rn "t\.HandlerType\|t\.Any[^a-zA-Z]" src/flext_core/ | grep -v __pycache__
    Expected Result: 0 matches
    Evidence: .sisyphus/evidence/task-3-no-handler-type.txt

  Scenario: c.Cqrs.HandlerType StrEnum preserved
    Tool: Bash
    Steps:
      1. grep -n "HandlerType" src/flext_core/constants.py
    Expected Result: StrEnum class definition present, unchanged
    Evidence: .sisyphus/evidence/task-3-cqrs-handler-preserved.txt
  ```

  **Commit**: YES
  - Message: `fix(types): replace loose HandlerType with tight HandlerLike, remove t.Any`
  - Files: dispatcher.py, protocols.py, registry.py, guards.py, _models/context.py, typings.py
  - Pre-commit: `python -m mypy src/flext_core/dispatcher.py --config-file=pyproject.toml`

---

- [ ] 4. Fix remaining mypy errors by category

  **What to do**:

  After Tasks 1-3, re-run mypy to get updated error list. Fix remaining errors by category.
  Expected: many RegisterableService and HandlerType errors will be gone. Remaining errors:

  **Category A: settings.py (3 errors — structural)**
  - Line 27: metaclass conflict → This is a known Pydantic + Protocol metaclass issue. Use `ProtocolModelMeta` from protocols.py, OR suppress if truly unfixable.
  - Line 75: `resolve_env_file` has-type → Add explicit type annotation
  - Line 302: `_di_provider` no-redef → Restructure to avoid double definition (move to __init__ or use conditional)

  **Category B: protocols.py (4 errors — runtime-injected attrs)**
  - Lines 1611, 1767, 1776, 1782: `__protocols__`, `implements_protocol`, `get_protocols` → These are injected by ProtocolModelMeta at runtime. Fix with:
    ```python
    if TYPE_CHECKING:
        __protocols__: ClassVar[frozenset[type]]
        def implements_protocol(cls, protocol: type) -> bool: ...
        def get_protocols(cls) -> frozenset[type]: ...
    ```
    Or add them as abstract methods in the metaclass.

  **Category C: exceptions.py (4 errors — strict validator arg-type)**
  - Lines 168, 180, 192, 204: Strict value validators receive union types but expect specific types
  - Fix: Add proper type narrowing (isinstance checks) before passing to strict validators
  - Example for line 168: `if isinstance(value, str): return _StrictStringValue(value=value)`

  **Category D: runtime.py (5 errors)**
  - Line 88: `type` has no `Metadata` → `_LazyMetadata` class needs proper typing
  - Line 170: `_LazyMetadata` vs `type` assignment → Fix type annotation
  - Line 1208: `FilteringBoundLogger` vs `StructlogLogger` → Use `BindableLogger` (structlog base)
  - Line 1230: `_AsyncLogWriter` vs `TextIO` → Add Protocol or cast to TextIO (wrap in adapter)
  - Line 1245: `list[object]` → Type the processor list properly with structlog processor type

  **Category E: mapper.py (4 errors)**
  - Line 178: `StructlogLogger` vs `BoundLogger` → Use `BindableLogger` (common base)
  - Lines 1231, 2850: `object` → `_ContainerValue` in `_to_general_value_from_object` calls
    - The function name literally says "from_object" — it's designed to accept object
    - Fix: rename to `_to_general_value` and change input to `_ContainerValue`
    - OR add proper narrowing before the call
  - Line 1386: `T` vs `_ContainerValue` → Add isinstance narrowing

  **Category F: args.py (3 errors — return type)**
  - Lines 139, 181, 184: `FlextResult[Never]` vs `Result[V]`, dict vs Mapping
  - Fix: Ensure return types match. `FlextResult` should be compatible with `Result`.
  - Check if `FlextResult` inherits from `Result` or if there's a type alias mismatch.

  **Category G: guards.py (2 errors)**
  - Lines 773, 780: `T` vs `_ContainerValue` in `_guard_check_type`
  - Fix: The function expects `_ContainerValue` but receives generic `T`. Add type bound or isinstance narrowing.

  **Category H: Other (5 errors)**
  - configuration.py:389: `HasModelDump` vs `BaseModel` → Add `BaseModel` to the union or use `HasModelDump | BaseModel`
  - collection.py:432: `R | FlextResult[R]` vs `_ContainerValue` → Add narrowing
  - parser.py:1310: `type` vs `BaseModel | Mapping` → Add isinstance check
  - container.py:515,525,541: `type[Config]` union-attr → Add `is not None` narrowing
  - context.py:643: `Mapping` vs `dict` → Use `dict()` constructor or explicit cast
  - _models/context.py:178: return value type → Fix return type annotation

  **Approach**: Fix each category, run mypy after each, verify error count decreases.

  **Must NOT do**:
  - Do NOT add `# type: ignore` — fix the actual type
  - Do NOT use `cast()` — use isinstance narrowing
  - Do NOT change `__eq__` or TypeGuard input signatures

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`, `flext-pyrefly-typecheck-fix`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on Tasks 2, 3)
  - **Blocks**: Task 5
  - **Blocked By**: Tasks 2, 3

  **References**:
  - `src/flext_core/settings.py:27,75,302` — Metaclass, has-type, no-redef
  - `src/flext_core/protocols.py:1611,1767,1776,1782` — Runtime-injected attrs
  - `src/flext_core/exceptions.py:168,180,192,204` — Strict validators
  - `src/flext_core/runtime.py:88,170,1208,1230,1245` — Lazy metadata, structlog
  - `src/flext_core/_utilities/mapper.py:178,1231,1386,2850` — Structlog, object→value
  - `src/flext_core/_utilities/args.py:139,181,184` — Result return types
  - `src/flext_core/_utilities/guards.py:773,780` — TypeVar narrowing
  - `src/flext_core/_utilities/configuration.py:389` — HasModelDump
  - `src/flext_core/_utilities/collection.py:432` — FlextResult narrowing
  - `src/flext_core/_utilities/parser.py:1310` — type vs BaseModel
  - `src/flext_core/container.py:515,525,541` — Config union-attr
  - `src/flext_core/context.py:643` — Mapping vs dict
  - `src/flext_core/_models/context.py:178` — Return value type

  **Acceptance Criteria**:
  - [ ] `python -m mypy src/flext_core/ --config-file=pyproject.toml` → 0 errors
  - [ ] No `# type: ignore` added
  - [ ] No `cast()` added

  **QA Scenarios**:
  ```
  Scenario: Zero mypy errors in flext_core
    Tool: Bash
    Steps:
      1. python -m mypy src/flext_core/ --config-file=pyproject.toml 2>&1 | tail -3
    Expected Result: "Found 0 errors" or "Success: no issues found"
    Evidence: .sisyphus/evidence/task-4-zero-mypy.txt

  Scenario: No prohibited patterns
    Tool: Bash
    Steps:
      1. grep -rn "# type: ignore\|cast(" src/flext_core/ | grep -v __pycache__ | grep -v ".pyc"
    Expected Result: 0 matches
    Evidence: .sisyphus/evidence/task-4-no-prohibited.txt
  ```

  **Commit**: YES
  - Message: `fix(types): resolve all mypy errors in flext-core src/`
  - Files: All files with fixes
  - Pre-commit: `python -m mypy src/flext_core/ --config-file=pyproject.toml`

---

- [ ] 5. Final verification — make check + make test

  **What to do**:
  - Run `make test` in flext-core → all tests must pass
  - Run `make check` in flext-core → verify error reduction
  - Run `ruff check src/` → 0 lint errors
  - Run `ruff format --check src/` → 0 format errors

  If any test fails: fix the root cause (likely a type change broke runtime behavior). Do NOT revert types — fix the code.

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-quality-gates`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocks**: Final verification wave
  - **Blocked By**: Task 4

  **References**:
  - `flext-core/pyproject.toml` — Test and check configuration
  - `flext-core/Makefile` — Make targets

  **Acceptance Criteria**:
  - [ ] `make test` → PASS (0 failures)
  - [ ] `python -m mypy src/flext_core/ --config-file=pyproject.toml` → 0 errors
  - [ ] `ruff check src/` → 0 errors
  - [ ] `ruff format --check src/` → 0 errors

  **QA Scenarios**:
  ```
  Scenario: All tests pass
    Tool: Bash
    Steps:
      1. cd /home/marlonsc/flext/flext-core && make test 2>&1 | tail -10
    Expected Result: All tests pass, 0 failures
    Evidence: .sisyphus/evidence/task-5-make-test.txt

  Scenario: Mypy clean
    Tool: Bash
    Steps:
      1. python -m mypy src/flext_core/ --config-file=pyproject.toml 2>&1 | tail -3
    Expected Result: 0 errors
    Evidence: .sisyphus/evidence/task-5-mypy-clean.txt
  ```

  **Commit**: YES (if any fixes needed)
  - Message: `fix(types): resolve test/lint issues from strong typing overhaul`
  - Pre-commit: `make test`

---

## Final Verification Wave

> 3 review agents run in PARALLEL after all tasks complete. ALL must APPROVE.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Verify all Must Have / Must NOT Have criteria. Check: no `t.Any`, no `t.HandlerType`, no `object` params (except Python-mandated), `p.RegisterableService` includes all Protocol types.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run full quality gates. Check for: `# type: ignore`, `cast()`, `Any`, `object` parameter types, dead code from removed aliases.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | VERDICT`

- [ ] F3. **Type Triad Compliance Check** — `quick`
  Verify the t ↔ p ↔ m triad is closed:
  1. `grep -rn 't\.Any\|t\.LaxStr\|t\.ScalarAlias\|t\.FlexibleValue\|t\.AcceptableMessageType\|t\.ConditionCallable\|t\.HandlerType' src/flext_core/` → 0 matches (dead aliases removed)
  2. `grep -rn 'typing\.Any\|: Any\b' src/flext_core/ | grep -v __pycache__` → 0 matches (no raw Any)
  3. All model fields use `t.*` types, not raw Python types
  4. `ServiceRegistration.service` field type is `p.RegisterableService`
  5. `_is_registerable_service()` guard matches `p.RegisterableService` scope
  6. `TModel` TypeVar is bounded to `BaseModel`
  Output: `Dead Aliases [CLEAN/N found] | Raw Types [CLEAN/N found] | Triad [CLOSED/N gaps] | VERDICT`

---

## Commit Strategy

- **Task 1**: `fix(types): tighten RegisterableService, replace HandlerType, remove dead aliases, bound TModel`
- **Task 2**: `refactor(types): migrate t.RegisterableService → p.RegisterableService`
- **Task 3**: `fix(types): replace loose HandlerType → HandlerLike, remove t.Any from context validators`
- **Task 4**: `fix(types): resolve all remaining mypy errors in flext-core`
- **Task 5**: `fix(types): resolve test/lint issues from strong typing overhaul` (if needed)

---

## Success Criteria

### Verification Commands
```bash
cd /home/marlonsc/flext/flext-core
python -m mypy src/flext_core/ --config-file=pyproject.toml  # Expected: 0 errors
make test                                                      # Expected: PASS
ruff check src/                                                # Expected: 0 errors
grep -rn "t\.Any[^a-zA-Z]\|t\.HandlerType\|t\.LaxStr\|t\.ScalarAlias\|t\.FlexibleValue" src/flext_core/ | grep -v __pycache__  # Expected: 0 matches
grep -rn "typing\.Any" src/flext_core/ | grep -v __pycache__  # Expected: 0 matches
```

### Final Checklist
- [ ] `p.RegisterableService` expanded with Config, Context, DI, Service, CommandBus, Registrable
- [ ] `t.HandlerLike` = tight union (no Any, no object)
- [ ] `t.Any` alias removed
- [ ] All dead aliases removed (LaxStr, ScalarAlias, FlexibleValue, AcceptableMessageType, ConditionCallable)
- [ ] `TModel` TypeVar bounded to `BaseModel`
- [ ] `ServiceRegistration.service` uses `p.RegisterableService`
- [ ] `_is_registerable_service()` guard matches expanded `p.RegisterableService`
- [ ] 0 mypy errors in src/flext_core/
- [ ] All tests pass
- [ ] No `# type: ignore`, no `cast()`, no `typing.Any`
- [ ] Type System Triad closed: t feeds p+m, p feeds m, m never feeds back
