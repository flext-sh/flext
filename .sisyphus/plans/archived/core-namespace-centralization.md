# ARCHIVED — Subsumed by modernization-reorg-execution.md

# Centralize Scattered Types/Protocols/Models/Utilities in flext_core

## TL;DR

> **Quick Summary**: Move all scattered type aliases, Protocol classes, Pydantic models, and utility functions in `flext_core` to their proper namespace homes (`t.*`, `p.*`, `m.*`, `u.*`). Same MRO pattern established for constants (`c.Infra.*`).
> 
> **Deliverables**:
> - All type aliases centralized in `typings.py` → `t.*`
> - All Protocol classes centralized in `protocols.py` → `p.*`
> - All Pydantic models centralized in `_models/` → `m.*`
> - All utility functions centralized in `_utilities/` → `u.*`
> - flext-ldif updated from private `_models` imports to public `m.*` facade
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 4 waves
> **Critical Path**: Phase 0 → Phase 1 (Types) → Phase 2 (Protocols) → Phase 3 (Models) → Phase 4 (Utilities) → Phase 5 (Cross-project) → FINAL

---

## Context

### Original Request
"voce tem que aplicar esse mesmo conceito e estrutura de constants para typings, protocols, models e utilities"

### Interview Summary
**Key Discussions**:
- User wants identical namespace centralization pattern from constants (`c.Infra.*`) applied to `t.*`, `p.*`, `m.*`, `u.*`
- ALL scattered items move — both public and private
- Pure refactoring: zero behavior change, full test suite (5471 tests) as verification

**Research Findings**:
- **Types scattered**: 9 type aliases/statements in `_utilities/` and `context.py`
- **Protocols scattered**: 5 Protocol classes in `dispatcher.py`, `_utilities/collection.py`, `typings.py`
- **Models scattered**: ~8 BaseModel/RootModel subclasses in `typings.py`, `_runtime_metadata.py`, `_utilities/conversion.py`
- **Utilities scattered**: 6 helper functions in `_models/container.py`, `_models/domain_event.py`, `result.py`, `handlers.py`
- **External consumers**: flext-ldif imports from `flext_core._models.base`, `_models.collections`, `_models.entity`

### Metis Review
**Identified Gaps** (addressed):
- Backward compat for private items: NOT needed (`_` prefix = internal API)
- `_Predicate` naming: only ONE exists in collection.py (mapper.py has `_MapperCallable`, not `_Predicate`)
- `_RootDictModel` in typings.py: moves to `_models/` — MRO verified post-move
- flext-ldif cross-project coordination: included as Phase 5
- `__qualname__` / `patch()` targets: included as verification steps per task

---

## Work Objectives

### Core Objective
Centralize ALL scattered type aliases, Protocol classes, Pydantic models, and utility functions from random files into their designated namespace facades, following the exact MRO pattern established for constants.

### Concrete Deliverables
- `typings.py` / `FlextTypes` has ALL type aliases → `t.*`
- `protocols.py` / `FlextProtocols` has ALL protocols → `p.*`
- `_models/` + `models.py` / `FlextModels` has ALL models → `m.*`
- `_utilities/` + `utilities.py` / `FlextUtilities` has ALL utilities → `u.*`
- flext-ldif uses `m.*` facade instead of `flext_core._models.*`

### Definition of Done
- [ ] `python -m pytest tests/ -q` → 5471+ pass, 0 failures
- [ ] `python -c "from flext_core import c, m, p, t, u, r"` → exit 0, no circular imports
- [ ] Zero scattered type/protocol/model/utility definitions outside their homes (verified by grep)

### Must Have
- Every move is a pure relocation — no behavior changes, no renames, no signature changes
- Full test suite passes after EACH task, not just at the end
- Private items keep their underscore prefix in the new home
- Duplicate TypeVars replaced with canonical ones from `typings.py`

### Must NOT Have (Guardrails)
- ❌ NO renaming items while moving — if a name conflict exists, resolve it BEFORE moving
- ❌ NO modifying function bodies, signatures, or docstrings during moves
- ❌ NO reorganizing facade class structure — only ADD items to existing structure
- ❌ NO removing existing `__init__.py` exports — only ADD new lazy import entries
- ❌ NO `# type: ignore`, `Any`, `cast()`, inline imports
- ❌ NO "improvements" — pure structural refactoring ONLY

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: Tests-after (run existing suite, no new tests needed for pure moves)
- **Framework**: pytest (5471 tests baseline)

### QA Policy
Every task runs the full test suite + circular import check after completion.
Evidence saved to `.sisyphus/evidence/task-{N}-*.txt`.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Phase 0 — Baseline):
├── Task 1: Baseline verification [quick]

Wave 2 (Phases 1-2 — Types + Protocols, SEQUENTIAL within, parallel between waves):
├── Task 2: Centralize type aliases from _utilities/ → t.* [deep]
├── Task 3: Centralize type alias from context.py → t.* [quick]
├── Task 4: Deduplicate TypeVars (remove dupes, use canonical from typings.py) [deep]
├── Task 5: Centralize dispatcher protocols → p.Dispatch.* [deep]
├── Task 6: Centralize _Predicate + _RootDictProtocol → p.* [quick]

Wave 3 (Phase 3-4 — Models + Utilities):
├── Task 7: Move RootModel subclasses from typings.py → _models/ [deep]
├── Task 8: Move _StrictJsonScalarModel + _runtime Metadata → _models/ [quick]
├── Task 9: Move utility functions from _models/ → _utilities/ [deep]
├── Task 10: Move is_success_result/is_failure_result → u.* [quick]
├── Task 11: Move _handler_type_to_literal → u.* [quick]

Wave 4 (Phase 5 — Cross-project + Final):
├── Task 12: Update flext-ldif private imports → m.* facade [quick]
├── Task 13: Final grep sweep — verify zero scattered definitions [deep]

Wave FINAL (Verification):
├── Task F1: Plan compliance audit [oracle]
├── Task F2: Code quality review [unspecified-high]
├── Task F3: Real QA — full test suite + cross-project [unspecified-high]
├── Task F4: Scope fidelity check [deep]

Critical Path: T1 → T2 → T5 → T7 → T9 → T12 → T13 → F1-F4
Max Concurrent: 4 (Wave 2 tasks can overlap if they don't touch same files)
```

### Dependency Matrix
| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 2-6 |
| 2-4 | 1 | 7-8 |
| 5-6 | 1 | 7-8 |
| 7-8 | 2-6 | 9-11 |
| 9-11 | 7-8 | 12-13 |
| 12-13 | 9-11 | F1-F4 |

### Agent Dispatch Summary
- **Wave 1**: 1 task → `quick`
- **Wave 2**: 5 tasks → 3× `deep`, 2× `quick`
- **Wave 3**: 5 tasks → 2× `deep`, 3× `quick`
- **Wave 4**: 2 tasks → `quick` + `deep`
- **FINAL**: 4 tasks → `oracle` + 2× `unspecified-high` + `deep`

---

## TODOs

- [ ] 1. Baseline Verification

  **What to do**:
  - Run full test suite: `python -m pytest tests/ -q` → confirm 5471+ pass, 0 failures
  - Run circular import check: `python -c "from flext_core import c, m, p, t, u, r"` → exit 0
  - Run external consumer scan: `grep -rn "from flext_core\._" flext-*/src/ --include="*.py" | grep -v flext-core`
  - Record baseline numbers for regression comparison

  **Must NOT do**:
  - Modify any files

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Blocked By**: None
  - **Blocks**: Tasks 2-6

  **References**:
  - `src/flext_core/__init__.py` — public API exports
  - `tests/` — full test suite

  **Acceptance Criteria**:
  - [ ] Tests: 5471+ pass, 0 failures
  - [ ] Circular import check: exit 0
  - [ ] External consumers documented (expected: only flext-ldif hits)

  **QA Scenarios**:
  ```
  Scenario: Baseline test suite
    Tool: Bash
    Steps:
      1. cd /home/marlonsc/flext/flext-core && python -m pytest tests/ -q
      2. Assert output contains "passed" and "0 failed"
    Expected Result: 5471+ passed, 0 failures
    Evidence: .sisyphus/evidence/task-1-baseline.txt
  ```

  **Commit**: NO

- [ ] 2. Centralize Type Aliases from _utilities/ → FlextTypes

  **What to do**:
  - Move `type StrictJsonScalar` and `type StrictJsonValue` from `_utilities/conversion.py` → `typings.py` as `FlextTypes` class attributes
  - Move `type _MapperCallable` from `_utilities/mapper.py` → `typings.py` as `FlextTypes` class attribute
  - Update consumer files to use `t.StrictJsonScalar`, `t.StrictJsonValue`, `t._MapperCallable`
  - Use `lsp_find_references` on each type BEFORE moving to map ALL consumers
  - Search for `patch()` targets referencing old paths: `grep -rn "patch.*conversion\|patch.*mapper" tests/`

  **Must NOT do**:
  - Change type definitions (no simplification, no expansion)
  - Remove imports that are still needed for other things in the source file

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`]
    - `flext-strict-typing`: type system rules for FlextTypes pattern
    - `flext-import-rules`: import organization rules

  **Parallelization**:
  - **Blocked By**: Task 1
  - **Blocks**: Tasks 7-8

  **References**:
  - `src/flext_core/typings.py:81` — `FlextTypes` class definition (add new type aliases here)
  - `src/flext_core/_utilities/conversion.py:17-20` — `StrictJsonScalar`, `StrictJsonValue` definitions
  - `src/flext_core/_utilities/mapper.py:30` — `_MapperCallable` definition
  - `src/flext_infra/_constants_modules.py` — reference pattern for how standalone items were centralized

  **Acceptance Criteria**:
  - [ ] `StrictJsonScalar`, `StrictJsonValue` exist as `t.StrictJsonScalar`, `t.StrictJsonValue`
  - [ ] `_MapperCallable` exists as `t._MapperCallable`
  - [ ] No `type StrictJsonScalar` or `type StrictJsonValue` in `_utilities/conversion.py`
  - [ ] No `type _MapperCallable` in `_utilities/mapper.py`
  - [ ] `python -m pytest tests/ -q` → all pass
  - [ ] `python -c "from flext_core import t; print(t.StrictJsonScalar)"` → works

  **QA Scenarios**:
  ```
  Scenario: Type alias access via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import t; print(t.StrictJsonScalar); print(t.StrictJsonValue)"
      2. Assert both print successfully without ImportError
    Expected Result: Both types accessible, no errors
    Evidence: .sisyphus/evidence/task-2-types-access.txt

  Scenario: No scattered type aliases remain in _utilities/
    Tool: Bash
    Steps:
      1. grep -rn "^type " src/flext_core/_utilities/ --include="*.py"
      2. Assert 0 matches
    Expected Result: No type statements in _utilities/
    Evidence: .sisyphus/evidence/task-2-grep-clean.txt
  ```

  **Commit**: YES (groups with T3, T4)
  - Message: `refactor(core): centralize scattered type aliases into FlextTypes`

- [ ] 3. Centralize ContextValue Type Alias → FlextTypes

  **What to do**:
  - Move `type ContextValue = t.ConfigMapValue` from `context.py` → `typings.py` as `FlextTypes.ContextValue`
  - Update `context.py` to use `t.ContextValue`
  - Use `lsp_find_references` on `ContextValue` to find all consumers

  **Must NOT do**:
  - Touch anything else in context.py

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Blocked By**: Task 1
  - **Blocks**: Tasks 7-8

  **References**:
  - `src/flext_core/context.py:28` — `type ContextValue = t.ConfigMapValue`
  - `src/flext_core/typings.py:81` — `FlextTypes` class

  **Acceptance Criteria**:
  - [ ] `t.ContextValue` accessible
  - [ ] No `type ContextValue` in `context.py`
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: ContextValue via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import t; print(t.ContextValue)"
    Expected Result: Type prints, no error
    Evidence: .sisyphus/evidence/task-3-context-value.txt
  ```

  **Commit**: YES (groups with T2, T4)

- [ ] 4. Deduplicate TypeVars — Replace Dupes with Canonical from typings.py

  **What to do**:
  - `_utilities/result_helpers.py:10` has `T = TypeVar("T")` — DUPLICATE of `typings.py:24`. Remove, import `T` from `flext_core.typings`
  - `_utilities/model.py:19` has `T_Model = TypeVar("T_Model", bound=BaseModel)` — DUPLICATE of `typings.py:44`. Remove, import from typings
  - For LOCAL-ONLY TypeVars that are NOT duplicates (e.g., `_PredicateT_contra`, `EnumT`, `_ValidatedReturn`, `_ValidatedParams`): LEAVE IN PLACE — they are type parameters scoped to their module, not types to centralize
  - Use `lsp_find_references` on each TypeVar to verify scope before removing

  **Must NOT do**:
  - Move local-only TypeVars that serve as module-scoped type parameters
  - Change TypeVar bounds, variance, or names

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `python-modern-type-syntax`]

  **Parallelization**:
  - **Blocked By**: Task 1
  - **Blocks**: Tasks 7-8

  **References**:
  - `src/flext_core/typings.py:24` — canonical `T = TypeVar("T")`
  - `src/flext_core/typings.py:44` — canonical `T_Model = TypeVar("T_Model", bound=BaseModel)`
  - `src/flext_core/_utilities/result_helpers.py:10` — duplicate `T`
  - `src/flext_core/_utilities/model.py:19` — duplicate `T_Model`

  **Acceptance Criteria**:
  - [ ] Zero duplicate TypeVar definitions across codebase
  - [ ] All non-duplicate local TypeVars remain in their module
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: No duplicate TypeVars
    Tool: Bash
    Steps:
      1. grep -rn 'T = TypeVar' src/flext_core/ --include='*.py' | grep -v typings.py | grep -v __pycache__
      2. Assert only local-scoped TypeVars remain (not T or T_Model)
    Expected Result: Zero matches for T or T_Model outside typings.py
    Evidence: .sisyphus/evidence/task-4-typevar-dedup.txt
  ```

  **Commit**: YES (groups with T2, T3)
  - Message: `refactor(core): centralize scattered type aliases into FlextTypes`

- [ ] 5. Centralize Dispatcher Protocols → FlextProtocols

  **What to do**:
  - Move `DispatchMessageProtocol`, `HandleProtocol`, `ExecuteProtocol` from `dispatcher.py` → `protocols.py`
  - Add as nested class under `FlextProtocols.Dispatch`: `p.Dispatch.Message`, `p.Dispatch.Handle`, `p.Dispatch.Execute`
  - Update `dispatcher.py` to import from `p.Dispatch.*`
  - Verify `isinstance()` checks still work after move (dispatcher uses these for runtime type checking)
  - Search for `patch()` targets: `grep -rn "patch.*DispatchMessage\|patch.*HandleProtocol\|patch.*ExecuteProtocol" tests/`

  **Must NOT do**:
  - Change protocol method signatures
  - Rename the protocols (keep original names as the nested class names)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`]

  **Parallelization**:
  - **Blocked By**: Task 1
  - **Blocks**: Tasks 7-8

  **References**:
  - `src/flext_core/dispatcher.py:21-47` — three Protocol classes
  - `src/flext_core/protocols.py` — `FlextProtocols` class (add `Dispatch` nested class here)
  - `src/flext_core/dispatcher.py:_execute_handler` — where isinstance checks happen

  **Acceptance Criteria**:
  - [ ] `p.Dispatch.Message`, `p.Dispatch.Handle`, `p.Dispatch.Execute` accessible
  - [ ] No Protocol definitions in `dispatcher.py`
  - [ ] `isinstance()` checks in dispatcher still pass
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: Dispatcher protocols via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import p; print(p.Dispatch.Message, p.Dispatch.Handle, p.Dispatch.Execute)"
      2. Assert all three print without error
    Expected Result: All protocols accessible
    Evidence: .sisyphus/evidence/task-5-dispatch-protocols.txt

  Scenario: isinstance checks still work
    Tool: Bash
    Steps:
      1. python -m pytest tests/ -k dispatch -q
      2. Assert all dispatch-related tests pass
    Expected Result: All pass
    Evidence: .sisyphus/evidence/task-5-isinstance.txt
  ```

  **Commit**: YES (groups with T6)
  - Message: `refactor(core): centralize scattered protocols into FlextProtocols`

- [ ] 6. Centralize ALL Remaining Scattered Protocols → FlextProtocols

  **What to do**:
  - Move `_Predicate` protocol from `_utilities/collection.py:25` → `protocols.py` as `FlextProtocols.Collection._Predicate`
  - Move `_Predicate[T]` protocol from `_utilities/mapper.py:22` → `protocols.py` as `FlextProtocols.Mapper._Predicate`
    - NOTE: these are TWO DIFFERENT `_Predicate` protocols — collection uses `_PredicateT_contra`, mapper uses `T`. They MUST get distinct namespace paths
  - Move `_RootDictProtocol` from `typings.py:165` → `protocols.py` as `FlextProtocols._RootDictProtocol`
  - Move `_HasModelDump` from `_models/context.py:34` → `protocols.py` as `FlextProtocols._HasModelDump`
    - It's `@runtime_checkable` — preserve that decorator after move
  - Move `MetadataProtocol` from `exceptions.py:28` → `protocols.py` as `FlextProtocols.MetadataProtocol`
  - Update all source files to import from `p.*` instead of local definitions
  - If `_RootDictProtocol` is unused, consider removing it entirely (verify with `lsp_find_references`)
  - Also move the `_PredicateT_contra` TypeVar with the collection `_Predicate` (they're a unit)

  **Must NOT do**:
  - Rename the protocols
  - Merge different protocols with similar names

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Blocked By**: Task 1
  - **Blocks**: Tasks 7-8

  **References**:
  - `src/flext_core/_utilities/collection.py:21-28` — `_PredicateT_contra` + `_Predicate` (collection variant)
  - `src/flext_core/_utilities/mapper.py:22-27` — `_Predicate[T]` (mapper variant, DIFFERENT protocol)
  - `src/flext_core/typings.py:164-166` — `_RootDictProtocol`
  - `src/flext_core/_models/context.py:33-35` — `@runtime_checkable class _HasModelDump(Protocol)`
  - `src/flext_core/exceptions.py:28-30` — `class MetadataProtocol(Protocol)`
  - `src/flext_core/protocols.py` — FlextProtocols class (target home)

  **Acceptance Criteria**:
  - [ ] No Protocol definitions in `_utilities/collection.py`, `_utilities/mapper.py`, `typings.py`, `_models/context.py`, or `exceptions.py`
  - [ ] `p.Collection._Predicate` and `p.Mapper._Predicate` both accessible (distinct protocols)
  - [ ] `p._HasModelDump` is `@runtime_checkable` (preserved after move)
  - [ ] `p.MetadataProtocol` accessible
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: No scattered protocols
    Tool: Bash
    Steps:
      1. grep -rn "class.*Protocol" src/flext_core/ --include="*.py" | grep -v protocols.py | grep -v __pycache__
      2. Assert 0 matches
    Expected Result: Zero protocol definitions outside protocols.py
    Evidence: .sisyphus/evidence/task-6-grep-clean.txt
  ```

  **Commit**: YES (groups with T5)
  - Message: `refactor(core): centralize scattered protocols into FlextProtocols`

- [ ] 7. Move RootModel Subclasses from typings.py → _models/

  **What to do**:
  - Move `ObjectList`, `_RootDictModel`, `Dict`, `ConfigMap`, `ServiceMap`, `ErrorMap`, `FactoryMap`, `ResourceMap`, `BatchResultDict` from `typings.py` → new file `_models/containers.py`
  - Create `FlextModelsContainers` class in `_models/containers.py` containing all moved models
  - Import into `models.py` facade: add MRO class `class Containers(FlextModelsContainers):`
  - Update `models.py` aliases that currently reference `t.Dict`, `t.ConfigMap`, etc. to reference `FlextModelsContainers.*`
  - Verify MRO chain: `python -c "from flext_core import m; print(m.Dict.__mro__)"` — must resolve correctly
  - Update ALL consumers (use `lsp_find_references` for each model class)

  **Must NOT do**:
  - Change model fields, validators, or config
  - Change MRO hierarchy (only move, don't restructure)
  - Touch `_RootDictProtocol` (already handled in T6)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`, `flext-import-rules`]
    - `lib-pydantic-v2`: Pydantic model patterns for safe moves

  **Parallelization**:
  - **Blocked By**: Tasks 2-6
  - **Blocks**: Tasks 9-11

  **References**:
  - `src/flext_core/typings.py:124-200` — ObjectList, _RootDictModel, Dict/ConfigMap/etc.
  - `src/flext_core/models.py:96-106` — current facade aliases (`m.Dict = t.Dict` etc.)
  - `src/flext_core/_models/` — existing model subpackage (create `containers.py` here)

  **Acceptance Criteria**:
  - [ ] `m.Dict`, `m.ConfigMap`, `m.ServiceMap`, `m.ErrorMap` all accessible
  - [ ] No RootModel/BaseModel subclasses in `typings.py`
  - [ ] MRO chain intact for all container models
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: Container models via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import m; d = m.Dict(root={'a': 'b'}); print(d['a']); print(m.Dict.__mro__)"
      2. Assert 'b' printed and MRO chain resolves
    Expected Result: Model works, MRO intact
    Evidence: .sisyphus/evidence/task-7-container-models.txt

  Scenario: No model classes in typings.py
    Tool: Bash
    Steps:
      1. grep -n "class.*RootModel\|class.*BaseModel" src/flext_core/typings.py
      2. Assert 0 matches
    Expected Result: Zero model definitions in typings.py
    Evidence: .sisyphus/evidence/task-7-typings-clean.txt
  ```

  **Commit**: YES (groups with T8)
  - Message: `refactor(core): centralize scattered models into FlextModels`

- [ ] 8. Move _StrictJsonScalarModel + _RuntimeMetadata → _models/

  **What to do**:
  - Move `_StrictJsonScalarModel` from `_utilities/conversion.py` → `_models/containers.py` (created in T7)
  - Move `Metadata` model from `_runtime_metadata.py` → appropriate `_models/*.py` file
  - Update `_runtime_metadata.py` and `_utilities/conversion.py` to import from new locations
  - Expose through `FlextModels` facade if public, keep `_` prefix if private

  **Must NOT do**:
  - Change model fields or behavior

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`lib-pydantic-v2`]

  **Parallelization**:
  - **Blocked By**: Tasks 2-6
  - **Blocks**: Tasks 9-11

  **References**:
  - `src/flext_core/_utilities/conversion.py` — `_StrictJsonScalarModel`
  - `src/flext_core/_runtime_metadata.py` — `Metadata` model
  - `src/flext_core/_models/containers.py` — created in T7

  **Acceptance Criteria**:
  - [ ] No BaseModel subclasses in `_utilities/conversion.py` or `_runtime_metadata.py`
  - [ ] Tests pass

  **QA Scenarios**:
  ```
  Scenario: No scattered models
    Tool: Bash
    Steps:
      1. grep -rn "class.*BaseModel\|class.*RootModel" src/flext_core/ --include="*.py" | grep -v _models/ | grep -v models.py | grep -v __pycache__ | grep -v typings.py
      2. Assert 0 matches (typings.py cleaned in T7)
    Expected Result: Zero model definitions outside _models/
    Evidence: .sisyphus/evidence/task-8-models-clean.txt
  ```

  **Commit**: YES (groups with T7)
  - Message: `refactor(core): centralize scattered models into FlextModels`

- [ ] 9. Move Utility Functions from _models/ → _utilities/

  **What to do**:
  - Move `_is_metadata_instance` (TypeGuard) and `_normalize_metadata` from `_models/container.py` → `_utilities/model.py` (add to `FlextUtilitiesModel`)
  - Move `_MetadataInput` type alias alongside the functions (they're a unit)
  - Move `_normalize_event_data` from `_models/domain_event.py` → `_utilities/model.py`
  - Update `_models/container.py` to import from `_utilities/model.py`
  - Update `_models/domain_event.py` to import from `_utilities/model.py`
  - Expose through `u.Model._is_metadata_instance`, `u.Model._normalize_metadata`, `u.Model._normalize_event_data`
  - Import chain is verified safe: `_models/container.py` → `_utilities/model.py` → `_models/base.py` (no cycle — `_utilities/model.py` already imports `FlextModelFoundation` at line 17)
  - Use `lsp_find_references` on each function BEFORE moving to map ALL consumers
  - Note: `_normalize_metadata` in `exceptions.py` is a DIFFERENT function (method on BaseError) — do NOT touch it
  - Note: `_normalize_metadata_before` in `_models/context.py` is a DIFFERENT function — do NOT touch it

  **Must NOT do**:
  - Touch `_normalize_metadata` in `exceptions.py` (different function, same name)
  - Touch `_normalize_metadata_before` in `_models/context.py` (different function)
  - Change function bodies, signatures, or return types
  - Move `_ComparableConfigMap` class (it's a model, stays in `_models/domain_event.py`)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`, `lib-pydantic-v2`]
    - `flext-strict-typing`: type system rules for TypeGuard/TypeIs patterns
    - `flext-import-rules`: import organization and circular import detection
    - `lib-pydantic-v2`: Pydantic BeforeValidator patterns

  **Parallelization**:
  - **Blocked By**: Tasks 7-8
  - **Blocks**: Tasks 12-13

  **References**:
  - `src/flext_core/_models/container.py:25-59` — `_MetadataInput`, `_is_metadata_instance`, `_normalize_metadata` definitions
  - `src/flext_core/_models/container.py:112,196,233` — internal call sites (field validators using `_normalize_metadata`)
  - `src/flext_core/_models/domain_event.py:36-60` — `_normalize_event_data` definition
  - `src/flext_core/_utilities/model.py` — target home (`FlextUtilitiesModel` class)
  - `src/flext_core/utilities.py:95-96` — `u.Model` facade class
  - `src/flext_core/exceptions.py:434,499` — DIFFERENT `_normalize_metadata` (DO NOT TOUCH)
  - `src/flext_core/_models/context.py:65` — DIFFERENT `_normalize_metadata_before` (DO NOT TOUCH)

  **Acceptance Criteria**:
  - [ ] `_is_metadata_instance` and `_normalize_metadata` NOT in `_models/container.py` (as standalone functions)
  - [ ] `_normalize_event_data` NOT in `_models/domain_event.py` (as standalone function)
  - [ ] Both accessible via `u.Model._is_metadata_instance`, `u.Model._normalize_metadata`
  - [ ] `python -c "from flext_core import c, m, p, t, u, r"` → exit 0 (no circular imports)
  - [ ] `python -m pytest tests/ -q` → all pass

  **QA Scenarios**:
  ```
  Scenario: Moved utility functions accessible via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import u; print(u.Model._normalize_metadata)"
      2. Assert prints function reference without ImportError
    Expected Result: Function accessible via u.Model namespace
    Evidence: .sisyphus/evidence/task-9-utilities-access.txt

  Scenario: No standalone utility functions in _models/ (only methods on classes)
    Tool: Bash
    Steps:
      1. grep -n "^def _is_metadata_instance\|^def _normalize_metadata\b\|^def _normalize_event_data" src/flext_core/_models/*.py
      2. Assert 0 matches
    Expected Result: Zero standalone utility function definitions in _models/
    Evidence: .sisyphus/evidence/task-9-grep-clean.txt

  Scenario: No circular imports introduced
    Tool: Bash
    Steps:
      1. python -c "from flext_core import c, m, p, t, u, r; print('OK')"
      2. Assert 'OK' printed
    Expected Result: Clean import, no ImportError or circular dependency
    Evidence: .sisyphus/evidence/task-9-no-circular.txt
  ```

  **Commit**: YES (groups with T10, T11)
  - Message: `refactor(core): centralize scattered utilities into FlextUtilities`

- [ ] 10. Move is_success_result / is_failure_result → FlextUtilities

  **What to do**:
  - Move `is_success_result` (TypeIs) and `is_failure_result` (TypeIs) from `result.py:770-777` → `_utilities/result_helpers.py` (add to `ResultHelpers` class)
  - These are **exported** functions (in `__all__`), so they MUST remain accessible from `result.py` via re-export
  - Update `result.py` to import from `_utilities/result_helpers.py` and re-export in `__all__`
  - Expose through `u.ResultHelpers.is_success_result`, `u.ResultHelpers.is_failure_result`
  - Also add flat aliases: `u.is_success_result`, `u.is_failure_result` (staticmethod on FlextUtilities)
  - Use `lsp_find_references` on both functions to map ALL consumers before moving
  - Note: these functions reference `FlextRuntime.RuntimeResult` — verify import chain is clean

  **Must NOT do**:
  - Remove from `result.py` `__all__` — keep re-export for backward compat
  - Change TypeIs return type or function signature
  - Change `FlextResult` reference (it's the TypeIs target type)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Blocked By**: Tasks 7-8
  - **Blocks**: Tasks 12-13

  **References**:
  - `src/flext_core/result.py:770-780` — `is_success_result`, `is_failure_result` definitions + `__all__`
  - `src/flext_core/_utilities/result_helpers.py` — target home (`ResultHelpers` class)
  - `src/flext_core/utilities.py:33-35` — `FlextUtilitiesResultHelpers` import and facade registration

  **Acceptance Criteria**:
  - [ ] `u.is_success_result` and `u.is_failure_result` accessible
  - [ ] `from flext_core.result import is_success_result` still works (re-export)
  - [ ] `python -m pytest tests/ -q` → all pass

  **QA Scenarios**:
  ```
  Scenario: Result helpers via facade
    Tool: Bash
    Steps:
      1. python -c "from flext_core import u; print(u.is_success_result); print(u.is_failure_result)"
      2. Assert both print function references
    Expected Result: Both accessible via u.* namespace
    Evidence: .sisyphus/evidence/task-10-result-helpers.txt

  Scenario: Backward-compatible import still works
    Tool: Bash
    Steps:
      1. python -c "from flext_core.result import is_success_result, is_failure_result; print('OK')"
      2. Assert 'OK' printed
    Expected Result: Old import path still works via re-export
    Evidence: .sisyphus/evidence/task-10-backward-compat.txt
  ```

  **Commit**: YES (groups with T9, T11)

- [ ] 11. Move _handler_type_to_literal (module-level) → FlextUtilities

  **What to do**:
  - Move the MODULE-LEVEL `_handler_type_to_literal` function from `handlers.py:914-929` → `_utilities/` (new or existing file)
  - IMPORTANT: There are TWO functions named `_handler_type_to_literal`:
    - `FlextHandlers._handler_type_to_literal` (staticmethod at line 123) — uses dict lookup — **DO NOT TOUCH**
    - Module-level `_handler_type_to_literal` (line 914) — uses match/case — **THIS ONE MOVES**
  - The module-level function is in `__all__` — keep re-export from `handlers.py`
  - Update `handlers.py` to import from new location and re-export
  - Expose through `u.*` facade
  - Update test file: `tests/unit/test_handlers_full_coverage.py:43-48` references `handlers_module._handler_type_to_literal` — verify this still works via re-export

  **Must NOT do**:
  - Touch `FlextHandlers._handler_type_to_literal` (the class staticmethod at line 123)
  - Merge the two implementations (they have different approaches: dict vs match)
  - Change match/case logic or handler type mapping

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-import-rules`]

  **Parallelization**:
  - **Blocked By**: Tasks 7-8
  - **Blocks**: Tasks 12-13

  **References**:
  - `src/flext_core/handlers.py:914-932` — module-level `_handler_type_to_literal` + `__all__`
  - `src/flext_core/handlers.py:123-131` — class staticmethod (DO NOT TOUCH)
  - `tests/unit/test_handlers_full_coverage.py:43-48` — test for module-level function

  **Acceptance Criteria**:
  - [ ] Module-level `_handler_type_to_literal` NOT defined in `handlers.py` (only re-exported)
  - [ ] `FlextHandlers._handler_type_to_literal` (class staticmethod) unchanged
  - [ ] `from flext_core.handlers import _handler_type_to_literal` still works
  - [ ] `python -m pytest tests/ -q` → all pass

  **QA Scenarios**:
  ```
  Scenario: Handler utility accessible and re-export works
    Tool: Bash
    Steps:
      1. python -c "from flext_core.handlers import _handler_type_to_literal; from flext_core import c; print(_handler_type_to_literal(c.Cqrs.HandlerType.COMMAND))"
      2. Assert 'command' printed
    Expected Result: Function works via re-export
    Evidence: .sisyphus/evidence/task-11-handler-reexport.txt

  Scenario: Class staticmethod unchanged
    Tool: Bash
    Steps:
      1. python -c "from flext_core import h, c; print(h._handler_type_to_literal(c.Cqrs.HandlerType.QUERY))"
      2. Assert 'query' printed
    Expected Result: Class method still works independently
    Evidence: .sisyphus/evidence/task-11-class-method.txt
  ```

  **Commit**: YES (groups with T9, T10)
  - Message: `refactor(core): centralize scattered utilities into FlextUtilities`

- [ ] 12. Update flext-ldif Private Imports → m.* Facade

  **What to do**:
  - Update 3 private imports in flext-ldif to use the public `m.*` facade:
    1. `flext-ldif/src/flext_ldif/_models/metadata.py:8` — `from flext_core._models.base import FlextModelFoundation` → `from flext_core import m` then use `m.Base` (which is `FlextModelFoundation`)
    2. `flext-ldif/src/flext_ldif/_models/results.py:6` — `from flext_core._models.collections import FlextModelsCollections` → `from flext_core import m` then use `m.Collections` (already aliased)
    3. `flext-ldif/src/flext_ldif/_models/results.py:7` — `from flext_core._models.entity import FlextModelsEntity` → use `m.EntityModels` (already aliased)
  - Use `lsp_find_references` in the flext-ldif files to confirm which attributes are accessed from each import
  - Verify the `m.*` aliases exist by checking `models.py` facade:
    - `m.Base = FlextModelFoundation` (line 112)
    - `m.Collections` — verify this alias exists or add it
    - `m.EntityModels = FlextModelsEntity` (line 115)
  - Run flext-ldif tests: `cd /home/marlonsc/flext/flext-ldif && python -m pytest tests/ -q`

  **Must NOT do**:
  - Change any flext-ldif logic, only import paths
  - Add new model classes to flext-core (only use existing facade aliases)
  - Break flext-ldif test suite

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-import-rules`]

  **Parallelization**:
  - **Blocked By**: Tasks 9-11
  - **Blocks**: Task 13

  **References**:
  - `flext-ldif/src/flext_ldif/_models/metadata.py:8` — current private import
  - `flext-ldif/src/flext_ldif/_models/results.py:6-7` — current private imports
  - `src/flext_core/models.py:112-120` — facade namespace aliases (m.Base, m.EntityModels, etc.)

  **Acceptance Criteria**:
  - [ ] Zero `from flext_core._models` imports in flext-ldif
  - [ ] `grep -rn "from flext_core\._models" flext-ldif/src/ --include="*.py"` → 0 matches
  - [ ] `cd /home/marlonsc/flext/flext-ldif && python -m pytest tests/ -q` → all pass

  **QA Scenarios**:
  ```
  Scenario: No private _models imports in flext-ldif
    Tool: Bash
    Steps:
      1. grep -rn "from flext_core\._models" flext-ldif/src/ --include="*.py"
      2. Assert 0 matches
    Expected Result: Zero private imports from flext_core._models
    Evidence: .sisyphus/evidence/task-12-ldif-clean.txt

  Scenario: flext-ldif test suite passes
    Tool: Bash
    Steps:
      1. cd /home/marlonsc/flext/flext-ldif && python -m pytest tests/ -q
      2. Assert all pass, 0 failures
    Expected Result: Full flext-ldif test suite green
    Evidence: .sisyphus/evidence/task-12-ldif-tests.txt
  ```

  **Commit**: YES
  - Message: `refactor(ldif): use m.* facade instead of private _models imports`
  - Files: `flext-ldif/src/flext_ldif/_models/metadata.py`, `flext-ldif/src/flext_ldif/_models/results.py`

- [ ] 13. Final Grep Sweep — Verify Zero Scattered Definitions

  **What to do**:
  - Run comprehensive grep sweep to verify EVERY scattered definition has been moved:
  - **Types check**: `grep -rn "^type " src/flext_core/ --include="*.py" | grep -v typings.py | grep -v __pycache__`
    - Expected: 0 matches (all type aliases in typings.py)
  - **Protocols check**: `grep -rn "class.*Protocol" src/flext_core/ --include="*.py" | grep -v protocols.py | grep -v __pycache__ | grep -v TYPE_CHECKING`
    - Expected: 0 matches outside protocols.py
  - **Models check**: `grep -rn "class.*(BaseModel)\|class.*(RootModel)" src/flext_core/ --include="*.py" | grep -v _models/ | grep -v models.py | grep -v __pycache__`
    - Expected: 0 matches outside _models/
  - **TypeVar dedup check**: `grep -rn "T = TypeVar\|T_Model = TypeVar" src/flext_core/ --include="*.py" | grep -v typings.py | grep -v __pycache__`
    - Expected: 0 matches for duplicated T and T_Model
  - **Cross-project private import check**: `grep -rn "from flext_core\._" flext-*/src/ --include="*.py" | grep -v flext-core`
    - Expected: 0 matches (all external consumers use facade)
  - **Circular import check**: `python -c "from flext_core import c, m, p, t, u, r"`
    - Expected: exit 0
  - **Full test suite**: `python -m pytest tests/ -q`
    - Expected: 5471+ pass, 0 failures
  - Document any remaining items as KNOWN EXCEPTIONS with justification (e.g., `_ComparableConfigMap` stays in `_models/domain_event.py` because it's a model class, not a type alias)

  **Must NOT do**:
  - Make any code changes (verification only)
  - Move items discovered here without a plan amendment

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`]

  **Parallelization**:
  - **Blocked By**: Tasks 9-12
  - **Blocks**: F1-F4

  **References**:
  - All source files in `src/flext_core/`
  - `flext-ldif/src/flext_ldif/` (external consumer)

  **Acceptance Criteria**:
  - [ ] Zero scattered type aliases outside `typings.py`
  - [ ] Zero scattered Protocol classes outside `protocols.py`
  - [ ] Zero scattered BaseModel/RootModel outside `_models/` (except `_ComparableConfigMap`)
  - [ ] Zero duplicate TypeVars (T, T_Model)
  - [ ] Zero private `_models` imports from external projects
  - [ ] Circular import check passes
  - [ ] Full test suite passes

  **QA Scenarios**:
  ```
  Scenario: Comprehensive grep sweep
    Tool: Bash
    Steps:
      1. Run all grep commands listed above
      2. Collect results into single report
      3. Assert ALL checks return 0 unexpected matches
    Expected Result: Zero scattered definitions remain
    Evidence: .sisyphus/evidence/task-13-grep-sweep.txt

  Scenario: Full test suite final run
    Tool: Bash
    Steps:
      1. cd /home/marlonsc/flext/flext-core && python -m pytest tests/ -q
      2. cd /home/marlonsc/flext/flext-ldif && python -m pytest tests/ -q
      3. Assert both pass
    Expected Result: 5471+ tests pass (core), all pass (ldif)
    Evidence: .sisyphus/evidence/task-13-final-tests.txt
  ```

  **Commit**: NO (verification only)

---
## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `python -m pytest tests/ -q` + linter. Review all changed files for: `# type: ignore`, `Any`, `cast()`, empty catches, console.log. Check that no function bodies/signatures/docstrings were modified during moves.
  Output: `Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real QA** — `unspecified-high`
  Start from clean state. Run full test suite. Test cross-project (flext-ldif). Verify all namespace access works: `t.StrictJsonScalar`, `p.Dispatch.Message`, `m.Metadata`, `u.is_success_result`. Save evidence.
  Output: `Tests [N/N pass] | Namespaces [N/N] | Cross-Project [PASS/FAIL] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **T1**: no commit (verification only)
- **T2-T4**: `refactor(core): centralize scattered type aliases into FlextTypes` — typings.py, _utilities/*.py, context.py
- **T5-T6**: `refactor(core): centralize scattered protocols into FlextProtocols` — protocols.py, dispatcher.py, _utilities/collection.py, typings.py
- **T7-T8**: `refactor(core): centralize scattered models into FlextModels` — _models/*.py, typings.py, _runtime_metadata.py, _utilities/conversion.py
- **T9-T11**: `refactor(core): centralize scattered utilities into FlextUtilities` — _utilities/*.py, _models/*.py, result.py, handlers.py
- **T12**: `refactor(ldif): use m.* facade instead of private _models imports` — flext-ldif
- **T13**: no commit (verification only)

---

## Success Criteria

### Verification Commands
```bash
cd /home/marlonsc/flext/flext-core
python -m pytest tests/ -q  # Expected: 5471+ pass, 0 failures
python -c "from flext_core import c, m, p, t, u, r"  # Expected: exit 0
grep -rn "class.*Protocol" src/flext_core/ --include="*.py" | grep -v protocols.py | grep -v __pycache__  # Expected: 0 matches (except TYPE_CHECKING)
cd /home/marlonsc/flext/flext-ldif && python -m pytest tests/ -q  # Expected: all pass
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (flext-core + flext-ldif)
- [ ] Zero circular imports
- [ ] Zero scattered definitions outside homes
