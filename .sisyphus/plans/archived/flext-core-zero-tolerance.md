# ARCHIVED — Subsumed by modernization-reorg-execution.md

# flext-core Zero Tolerance Compliance Fix

## TL;DR

> **Quick Summary**: Fix every CLAUDE.md and skills violation in flext-core with zero tolerance — eliminate all `cast()`, `Any`, `type()` narrowing, types outside `FlextTypes`, AND all custom JSON handling code (replaced with Pydantic v2 native JSON).
>
> **Deliverables**:
> - All `cast()` removed from source (5) and test files (719+)
> - All `Any` replaced with specific FlextTypes aliases
> - New `t.LazyExportType` and `t.AnnotationMap` type aliases created
> - Dead TypeVars (`T_Model`, `R2`) removed
> - `type()` narrowing in `_validator/tests.py` replaced with `isinstance`
> - Duplicate `RegistrablePlugin` in `registry.py` resolved
> - ALL custom JSON code eliminated — replaced with `pydantic.JsonValue`, `TypeAdapter`, `model_dump(mode='json')`
>
> **Estimated Effort**: XL (24 implementation tasks + 4 final verification)
> **Parallel Execution**: YES - 5 waves
> **Critical Path**: Task 1 (new types) → Tasks 4-14 (source+JSON fixes) → Tasks 15-23 (test fixes) → Task 24 (verification) → F1-F4

---

## Context

### Original Request
Fix flext-core applying CLAUDE.md and skills patterns correctly — zero tolerance for violations. Types must be inside `FlextTypes` class.

### Interview Summary
**Key Discussions**:
- User demands zero tolerance: ALL `Any`, `cast()`, `type()` narrowing must be fixed
- Test files ARE in scope (including 747+ cast() in pytest files)
- `__getattr__` `Any` → create new `t.LazyExportType` type alias
- Protocol introspection `Any` → create new `t.AnnotationMap` type alias

**Research Findings**:
- Architecture layers: CLEAN — no cross-layer violations
- Import rules: 100% COMPLIANT
- FlextRuntime.Aliases: CLEAN — zero usage
- Pydantic v2 patterns: COMPLIANT
- Facade staticmethod pass-throughs: CORRECT pattern

### Metis Review
**Identified Gaps** (addressed):
- `T_Model` (0 refs) should be REMOVED, `TModel` (20 refs) should be KEPT — inverted from initial analysis
- `type(x).__mro__` in matchers.py is NOT narrowing — only `type(x) is Y` in `_validator/tests.py` is a violation
- `StrictJsonValue` in conversion.py is RECURSIVE — MUST stay module-level per Rule 2
- `_MapperCallable` in mapper.py is PRIVATE — can stay module-level
- 747 cast() in 70 test files was a scope bomb — user confirmed ALL in scope
- Plan missed `_utilities/lazy.py`, `_dispatcher/__init__.py`, `_decorators/__init__.py` Any usages
- `RegistrablePlugin` in registry.py has semantic mismatch vs typings.py version — needs verification before replacing

---

## Work Objectives

### Core Objective
Achieve 100% compliance of flext-core with CLAUDE.md and all skills — zero `Any`, zero `cast()` (except result.py), zero `type()` narrowing, all types centralized in FlextTypes, and ALL custom JSON code replaced with Pydantic v2 native JSON support.

### Concrete Deliverables
- `typings.py`: 2 new type aliases (`LazyExportType`, `AnnotationMap`), 2 dead TypeVars removed
- `container.py`: 4 cast() eliminated
- `mixins.py`: 1 cast() eliminated
- `_models/context.py`: 3 `t.Any` → specific types
- `protocols.py`: 6+ `Any` → `t.AnnotationMap` or specific types
- `settings.py`: 3 `Any` → specific types
- `__init__.py`, `_decorators/__init__.py`, `_dispatcher/__init__.py`, `_utilities/lazy.py`: `Any` → `t.LazyExportType`
- `flext_tests/__init__.py`, `flext_tests/_validator/__init__.py`: `Any` → `t.LazyExportType`
- `_validator/tests.py`: 7 `type() is` → `isinstance()`
- `registry.py`: duplicate type removed
- `context.py`: module-level type moved or justified
- 70 test files: 747+ cast() eliminated
- `_utilities/mapper.py`: ALL custom JSON functions eliminated (`convert_to_json_value`, `convert_dict_to_json`, `convert_list_to_json`, `is_json_primitive`, `_apply_to_json`, `to_json` parameter threading)
- `_utilities/conversion.py`: `StrictJsonScalar`, `StrictJsonValue`, `_StrictJsonScalarModel`, custom JSON adapters eliminated
- `_utilities/parser.py`: `_to_json_value()` eliminated
- `_models/context.py`: `check_json_serializable()` eliminated
- `runtime.py`: `json.dumps`/`json.loads` replaced with Pydantic v2 `TypeAdapter`
- `utilities.py`: facade aliases for eliminated JSON methods removed
- `typings.py`: JSON type aliases reviewed — keep `JsonPrimitive`/`JsonValue`/`JsonDict` as they map to `pydantic.JsonValue`
- 6 test files: 35 JSON function references updated

### Definition of Done
- [ ] `grep -rn "cast(" flext-core/src/flext_core/ --include="*.py" | grep -v result.py` returns ZERO lines
- [ ] `grep -rn "cast(" flext-core/tests/ --include="*.py"` returns ZERO lines
- [ ] `grep -rn ": Any\b\|-> Any\b\|, Any\b" flext-core/src/ --include="*.py"` returns ZERO lines
- [ ] `make check PROJECT=flext-core` exits 0
- [ ] `make test PROJECT=flext-core` exits 0
- [ ] `grep -rn 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|_apply_to_json\|check_json_serializable' flext-core/src/ --include='*.py'` returns ZERO lines
- [ ] `grep -rn 'StrictJsonScalar\|StrictJsonValue\|_StrictJsonScalarModel' flext-core/src/ --include='*.py'` returns ZERO lines
- [ ] `grep -n 'import json' flext-core/src/flext_core/runtime.py` returns ZERO lines
- [ ] `grep -rn '__class__.*in {\|__class__.*not in {\|__class__ is \|__class__ ==' flext-core/src/flext_core/ --include='*.py'` returns ZERO lines

### Must Have
- Every `cast()` replaced with isinstance/TypeGuard/protocol pattern (except result.py)
- Every `Any` replaced with specific FlextTypes alias
- Dead TypeVars removed
- `type() is` and `__class__ is/in` narrowing replaced with `isinstance()` (7 + 28 instances)
- ALL custom JSON functions deleted from mapper.py, conversion.py, parser.py, context.py
- `json.dumps`/`json.loads` in runtime.py replaced with Pydantic v2 native APIs
- Facade aliases for deleted JSON functions removed from utilities.py

### Must NOT Have (Guardrails)
- **DO NOT** remove `JsonPrimitive`/`JsonValue`/`JsonDict` type aliases from typings.py — they are used across the codebase and map to `pydantic.JsonValue` semantics
- **DO NOT** remove `to_str()` or non-JSON conversion methods from conversion.py — only JSON-specific code
- **DO NOT** move private types (prefixed `_`) into FlextTypes — they're fine at module-level
- **DO NOT** touch `type(x).__mro__` patterns in matchers.py — these are NOT narrowing violations
- **DO NOT** change `result.py` cast() — explicitly allowed by CLAUDE.md
- **DO NOT** change behavior — all replacements must preserve runtime semantics
- **DO NOT** add `model_rebuild()`, inline imports, `eval()`, `exec()`
- **DO NOT** change facade staticmethod pass-throughs in `utilities.py` that are NOT JSON-related — they ARE the correct pattern
- **DO NOT** touch architecture layers or import order — they're already clean
- **DO NOT** touch `cast_generic` in utilities — it's safe runtime conversion, NOT `typing.cast()`
- **DO NOT** touch `__class__` access for introspection/logging — only identity comparison patterns

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES (pytest, pytest-asyncio, pytest-benchmark, pytest-cov)
- **Automated tests**: YES (tests-after) — run existing suite as regression check
- **Framework**: pytest via `make test PROJECT=flext-core`

### QA Policy
Every task MUST run agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Source code**: Use Bash — `grep` for violations, `make check`, `make test`
- **Type safety**: Use Bash — `make check PROJECT=flext-core CHECK_GATES=type`

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Foundation — new type aliases):
├── Task 1: Add LazyExportType + AnnotationMap to FlextTypes [quick]
├── Task 2: Remove dead TypeVars (T_Model, R2) from typings.py [quick]
└── Task 3: Resolve RegistrablePlugin duplicate in registry.py + ContextValue in context.py [quick]

Wave 2 (Source code + JSON elimination + __class__ fixes — MAX PARALLEL, 12 tasks):
├── Task 4: Fix cast() in container.py (4x) (depends: 1) [deep]
├── Task 5: Fix cast() in mixins.py (1x) (depends: 1) [quick]
├── Task 6: Fix Any in _models/context.py (3x t.Any) (depends: 1) [quick]
├── Task 7: Fix Any in protocols.py (6x) — use t.AnnotationMap (depends: 1) [deep]
├── Task 8: Fix Any in settings.py (3x) (depends: 1) [quick]
├── Task 9: Fix Any in __init__.py + lazy.py + _decorators/__init__ + _dispatcher/__init__ (depends: 1) [quick]
├── Task 10: Fix Any in flext_tests __init__ files (depends: 1) [quick]
├── Task 11: Fix type() narrowing in _validator/tests.py (7x) [quick]
├── Task 11b: Fix __class__ identity patterns across 8 source files (28x) [unspecified-high]
├── Task 12: Eliminate custom JSON from mapper.py (depends: 1) [deep]
├── Task 13: Eliminate custom JSON from conversion.py + parser.py (depends: 1) [deep]
└── Task 14: Eliminate custom JSON from context.py + runtime.py + utilities.py (depends: 1, 12, 13) [deep]

Wave 3 (Test file cast() remediation — MAX PARALLEL, 9 batches):
├── Task 15: Fix cast() in test_automated_*.py (31 casts) (depends: 4-8) [unspecified-high]
├── Task 16: Fix cast() in test_coverage_*.py + test_container*.py + test_context*.py (39 casts) (depends: 4-8) [unspecified-high]
├── Task 17: Fix cast() in test_dispatcher*.py + test_handlers*.py + test_decorators*.py (64 casts) (depends: 4-8) [unspecified-high]
├── Task 18: Fix cast() in test_service*.py + test_settings*.py (4 casts) (depends: 4-8) [quick]
├── Task 19: Fix cast() in test_utilities_mapper*.py (150+ casts) (depends: 12) [deep]
├── Task 20: Fix cast() in other test_utilities*.py + test_mixins*.py (175 casts) (depends: 4-8) [unspecified-high]
├── Task 21: Fix cast() in test_runtime*.py (74 casts) + update JSON test refs (35 calls) (depends: 14) [unspecified-high]
├── Task 22: Fix cast() in test_flext_tests/*.py + test_exceptions*.py + test_loggings*.py + remaining (150 casts) (depends: 4-8) [unspecified-high]
└── Task 23: Fix cast() in tests/integration/ + tests/benchmark/ (7 casts) (depends: 4-8) [quick]

Wave 4 (Verification):
└── Task 24: Full quality gate verification (depends: ALL) [deep]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real manual QA (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 → Task 12 → Task 14 → Task 19/21 → Task 24 → F1-F4
Parallel Speedup: ~80% faster than sequential
Max Concurrent: 11 (Wave 2)
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|-----------|--------|------|
| 1 | — | 4-14 | 1 |
| 2 | — | 24 | 1 |
| 3 | — | 24 | 1 |
| 4 | 1 | 15-23 | 2 |
| 5 | 1 | 15-23 | 2 |
| 6 | 1 | 15-23 | 2 |
| 7 | 1 | 15-23 | 2 |
| 8 | 1 | 15-23 | 2 |
| 9 | 1 | 24 | 2 |
| 10 | 1 | 24 | 2 |
| 11 | — | 24 | 2 |
| 12 | 1 | 14, 19 | 2 |
| 13 | 1 | 14 | 2 |
| 14 | 1, 12, 13 | 21 | 2 |
| 15-18 | 4-8 | 24 | 3 |
| 19 | 12 | 24 | 3 |
| 20 | 4-8 | 24 | 3 |
| 21 | 14 | 24 | 3 |
| 22-23 | 4-8 | 24 | 3 |
| 24 | ALL | F1-F4 | 4 |
| F1-F4 | 24 | — | FINAL |

### Agent Dispatch Summary

- **Wave 1**: 3 — T1-T3 → `quick`
- **Wave 2**: 11 — T4 → `deep`, T5-T6 → `quick`, T7 → `deep`, T8-T11 → `quick`, T12-T14 → `deep`
- **Wave 3**: 9 — T15-T17 → `unspecified-high`, T18 → `quick`, T19 → `deep`, T20-T22 → `unspecified-high`, T23 → `quick`
- **Wave 4**: 1 — T24 → `deep`
- **FINAL**: 4 — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [ ] 0. **PREREQUISITE**: Resolve dirty git state + verify test baseline

  **What to do**:
  - Commit or stash any uncommitted changes (`models.py`, `typings.py`, `containers.py`)
  - Resolve any ImportError in test suite (if `pytest --co` fails)
  - Run `make test PROJECT=flext-core` and record baseline test count/pass rate
  - This baseline is the regression benchmark — post-refactor test count must be ≥ baseline

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-development-workflow`]

  **Parallelization**:
  - **Blocks**: ALL other tasks (Wave 0 — must complete first)
  - **Blocked By**: None

  **Acceptance Criteria**:
  - [ ] `git status` shows clean working tree (or changes committed)
  - [ ] `make test PROJECT=flext-core` exits 0 and baseline recorded

  **Commit**: YES (if stashing/committing)
  - Message: `chore(flext-core): clean working tree for compliance refactor`

- [ ] 1. Add LazyExportType + AnnotationMap to FlextTypes class

  **What to do**:
  - Add `LazyExportType: TypeAlias` inside FlextTypes class in `typings.py` — union of `type | types.ModuleType | t.GeneralValueType` to cover all possible lazy-loaded exports (classes, TypeVars, modules, values)
  - Add `AnnotationMap: TypeAlias = dict[str, type | str | t.GeneralValueType]` inside FlextTypes class — covers Python `__annotations__` which can contain types, forward refs (strings), and values
  - Export both in FlextTypes docstring and `__all__`

  **Must NOT do**:
  - Do NOT use PEP 695 `type` statement inside FlextTypes class — use `TypeAlias` annotation per Rule 2
  - Do NOT add `Any` or `object` anywhere

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 2, 3)
  - **Blocks**: Tasks 4-10
  - **Blocked By**: None

  **References**:
  - `flext-core/src/flext_core/typings.py:81-356` — FlextTypes class where new aliases go
  - `flext-strict-typing` Rule 2 — TypeAlias inside class, PEP 695 only at module level
  - `flext-core/src/flext_core/_utilities/lazy.py:22` — current `-> Any` that will use LazyExportType
  - `flext-core/src/flext_core/protocols.py:57` — current `dict[str, Any]` that will use AnnotationMap

  **Acceptance Criteria**:
  - [ ] `grep -n 'LazyExportType.*TypeAlias' flext-core/src/flext_core/typings.py` finds the new alias inside FlextTypes
  - [ ] `grep -n 'AnnotationMap.*TypeAlias' flext-core/src/flext_core/typings.py` finds the new alias inside FlextTypes
  - [ ] `make check PROJECT=flext-core CHECK_GATES=type` exits 0

  **QA Scenarios:**
  ```
  Scenario: LazyExportType alias created correctly
    Tool: Bash
    Steps:
      1. grep -n 'LazyExportType.*TypeAlias' flext-core/src/flext_core/typings.py
      2. Assert line is inside class FlextTypes (between line 81 and end of class)
      3. Verify alias includes `type | ModuleType | GeneralValueType` or equivalent broad union
    Expected Result: Alias found inside FlextTypes, covers classes + modules + values
    Evidence: .sisyphus/evidence/task-1-lazy-export-type.txt

  Scenario: AnnotationMap alias created correctly
    Tool: Bash
    Steps:
      1. grep -n 'AnnotationMap.*TypeAlias' flext-core/src/flext_core/typings.py
      2. Assert line is inside class FlextTypes
      3. Verify alias includes `dict[str, type | str | GeneralValueType]` or equivalent
    Expected Result: Alias found inside FlextTypes, covers annotation dict patterns
    Evidence: .sisyphus/evidence/task-1-annotation-map.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `refactor(typings): add LazyExportType + AnnotationMap type aliases`
  - Files: `flext-core/src/flext_core/typings.py`
  - Pre-commit: `make check PROJECT=flext-core CHECK_GATES=type`

- [ ] 2. Remove dead TypeVars (T_Model, R2) from typings.py

  **What to do**:
  - Verify `T_Model` has 0 references using `lsp_find_references` (Metis confirmed 0 refs, only in `__all__`)
  - Verify `R2` has 0 references using `lsp_find_references`
  - Remove `T_Model = TypeVar("T_Model", bound=BaseModel)` line and its docstring
  - Remove `R2 = TypeVar("R2")` line
  - Remove `T_Model` from `__all__` in typings.py
  - Remove `T_Model` from `__init__.py` lazy imports AND `__all__` AND TYPE_CHECKING block
  - Keep `TModel = TypeVar("TModel", bound=BaseModel)` — it has 20 refs across 4 files

  **Must NOT do**:
  - Do NOT remove `TModel` — it is actively used (20 refs)
  - Do NOT remove any other TypeVar without verifying zero refs first

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 3)
  - **Blocks**: Task 19
  - **Blocked By**: None

  **References**:
  - `flext-core/src/flext_core/typings.py:44` — `T_Model` declaration (0 refs — REMOVE)
  - `flext-core/src/flext_core/typings.py:50` — `TModel` declaration (20 refs — KEEP)
  - `flext-core/src/flext_core/typings.py:51` — `R2` declaration (0 refs — REMOVE)
  - `flext-core/src/flext_core/__init__.py:52-53` — T_Model in TYPE_CHECKING + lazy imports

  **Acceptance Criteria**:
  - [ ] `grep -n 'T_Model\|^R2 ' flext-core/src/flext_core/typings.py` returns ZERO lines
  - [ ] `grep -n 'T_Model' flext-core/src/flext_core/__init__.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: Dead TypeVars removed without breaking refs
    Tool: Bash
    Steps:
      1. grep -rn 'T_Model' flext-core/src/ --include='*.py'
      2. grep -rn '\bR2\b' flext-core/src/flext_core/typings.py
      3. make check PROJECT=flext-core
    Expected Result: Zero T_Model refs, zero R2 refs, make check passes
    Evidence: .sisyphus/evidence/task-2-dead-typevars.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `refactor(typings): remove dead TypeVars T_Model and R2`
  - Files: `typings.py`, `__init__.py`

- [ ] 3. Resolve RegistrablePlugin duplicate in registry.py + ContextValue in context.py

  **What to do**:
  - `registry.py:32` — `type RegistrablePlugin = p.Registrable` duplicates `t.RegistrablePlugin`
    - FIRST: verify if `p.Registrable` protocol is structurally compatible with `t.RegistrablePlugin` union
    - If compatible: remove the module-level type, use `t.RegistrablePlugin` everywhere in registry.py
    - If NOT compatible: move this type INTO FlextTypes as a new alias
  - `registry.py:33` — `type RegistryBindingKey = str | type[object]` is file-local, used 2x
    - Move into FlextTypes class as `RegistryBindingKey: TypeAlias = str | type[object]`
  - `context.py:28` — `type ContextValue = t.ConfigMapValue` is a convenience alias used 30x
    - Move into FlextTypes class as `ContextValue: TypeAlias = ConfigMapValue`

  **Must NOT do**:
  - Do NOT change `RegistrablePlugin` semantics without verifying compatibility
  - Do NOT move recursive types

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-type-system`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1, 2)
  - **Blocks**: Task 19
  - **Blocked By**: None

  **References**:
  - `flext-core/src/flext_core/registry.py:32-33` — duplicate types to resolve
  - `flext-core/src/flext_core/context.py:28` — ContextValue alias to centralize
  - `flext-core/src/flext_core/typings.py:105` — existing `t.RegistrablePlugin` in FlextTypes
  - `flext-strict-typing` Rule 2 — TypeAlias inside FlextTypes class

  **Acceptance Criteria**:
  - [ ] `grep -n '^type ' flext-core/src/flext_core/registry.py` returns ZERO lines
  - [ ] `grep -n '^type ' flext-core/src/flext_core/context.py` returns ZERO lines
  - [ ] New types exist inside FlextTypes class in typings.py

  **QA Scenarios:**
  ```
  Scenario: Module-level types eliminated from registry.py and context.py
    Tool: Bash
    Steps:
      1. grep -n '^type ' flext-core/src/flext_core/registry.py
      2. grep -n '^type ' flext-core/src/flext_core/context.py
      3. make check PROJECT=flext-core
      4. make test PROJECT=flext-core
    Expected Result: Zero module-level type statements, all checks pass
    Evidence: .sisyphus/evidence/task-3-types-centralized.txt
  ```

  **Commit**: YES (groups with Wave 1)
  - Message: `refactor(typings): centralize RegistryBindingKey + ContextValue into FlextTypes`
  - Files: `typings.py`, `registry.py`, `context.py`

- [ ] 4. Fix cast() in container.py (4 instances)

  **What to do**:
  - Line 252: `cast("t.RegisterableService", raw_result)` — factory wrapper returns unknown type. Replace with isinstance check: `if not isinstance(raw_result, t.RegisterableService): raise TypeError(...)` then return directly
  - Line 633: `cast("t.RegisterableService", self._config)` — config is `p.Config | None`. Use isinstance: `if isinstance(self._config, BaseModel): self.register("config", self._config)`
  - Line 657: `cast("t.RegisterableService", self._context)` — context is `p.Context | None`. Same isinstance pattern
  - Line 667: `cast("t.RegisterableService", dispatcher)` — dispatcher is `FlextDispatcher`. Same isinstance pattern
  - For each: verify the ServiceRegistration model accepts the type WITHOUT cast
  - Consider if ServiceRegistration's `service` field type needs widening to accept protocols

  **Must NOT do**:
  - Do NOT add `# type: ignore` as a replacement for cast
  - Do NOT change ServiceRegistration model in a way that weakens type safety

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `rules-flext-core`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 5-11)
  - **Blocks**: Tasks 12-18
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/container.py:252,633,657,667` — cast() locations
  - `flext-core/src/flext_core/_models/container.py` — ServiceRegistration model definition
  - `flext-strict-typing` Rule: Zero Tolerance for Hacks — cast() PROHIBITED
  - `flext-core/src/flext_core/typings.py:72-74` — RegisterableService type definition

  **Acceptance Criteria**:
  - [ ] `grep -n 'cast(' flext-core/src/flext_core/container.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0
  - [ ] `make test PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: All cast() removed from container.py
    Tool: Bash
    Steps:
      1. grep -n 'cast(' flext-core/src/flext_core/container.py
      2. make check PROJECT=flext-core
      3. make test PROJECT=flext-core
    Expected Result: Zero cast lines, all checks and tests pass
    Evidence: .sisyphus/evidence/task-4-container-cast.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(container): eliminate cast() with isinstance patterns`
  - Files: `container.py`

- [ ] 5. Fix cast() in mixins.py (1 instance)

  **What to do**:
  - Line 444: `logger: FlextLogger = cast("FlextLogger", logger_result.value)` — logger_result is `r[t.RegisterableService]`
  - Replace with isinstance check: `if isinstance(logger_result.value, FlextLogger): logger = logger_result.value`
  - Or use `get_typed[FlextLogger]("logger", FlextLogger)` if container supports it

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 12-18
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/mixins.py:444` — cast() location

  **Acceptance Criteria**:
  - [ ] `grep -n 'cast(' flext-core/src/flext_core/mixins.py` returns ZERO lines

  **QA Scenarios:**
  ```
  Scenario: cast() removed from mixins.py
    Tool: Bash
    Steps:
      1. grep -n 'cast(' flext-core/src/flext_core/mixins.py
      2. make check PROJECT=flext-core
    Expected Result: Zero cast lines, checks pass
    Evidence: .sisyphus/evidence/task-5-mixins-cast.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(mixins): eliminate cast() with isinstance pattern`
  - Files: `mixins.py`

- [ ] 6. Fix Any in _models/context.py (3 instances of t.Any)

  **What to do**:
  - Line 31: `v: t.Any` → `v: t.GuardInputValue | BaseModel | None` (matches actual inputs: None, Mapping, model_dump objects)
  - Line 43: `v: t.Any` → `v: t.GuardInputValue | FlextModelFoundation.Metadata | None` and return `-> t.GuardInputValue | FlextModelFoundation.Metadata | None`
  - Line 53: `v: t.Any` → `v: t.GuardInputValue | BaseModel | None`
  - Verify `t.Any` is not a real attribute — it's likely accessing `typing.Any` through `t` namespace which is WRONG

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 12-18
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/_models/context.py:31,43,53` — t.Any locations
  - `flext-strict-typing` Rule 1 — NEVER Use Any or object

  **Acceptance Criteria**:
  - [ ] `grep -n 't\.Any' flext-core/src/flext_core/_models/context.py` returns ZERO lines

  **QA Scenarios:**
  ```
  Scenario: t.Any eliminated from context models
    Tool: Bash
    Steps:
      1. grep -n 't\.Any' flext-core/src/flext_core/_models/context.py
      2. make check PROJECT=flext-core CHECK_GATES=type
    Expected Result: Zero t.Any, type check passes
    Evidence: .sisyphus/evidence/task-6-context-any.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(models/context): replace t.Any with specific types`
  - Files: `_models/context.py`

- [ ] 7. Fix Any in protocols.py (6+ instances) using t.AnnotationMap

  **What to do**:
  - Lines 57, 88, 143: `dict[str, Any]` for `__annotations__` access → `t.AnnotationMap`
  - Line 186: `_CombinedModelMeta: Any` → `_CombinedModelMeta: type` (it's a dynamically-created metaclass type)
  - Line 594: `dict[str, Any] | None` in Config.model_copy → `dict[str, t.GeneralValueType] | None`
  - Line 14: Remove `Any` from imports if no longer needed
  - `_ProtocolIntrospection` methods use `dict[str, Any]` for `__annotations__` — replace all with `t.AnnotationMap`

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 12-18
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/protocols.py:14,57,88,143,186,594` — Any locations
  - Task 1 output — t.AnnotationMap definition to use

  **Acceptance Criteria**:
  - [ ] `grep -n '\bAny\b' flext-core/src/flext_core/protocols.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: All Any eliminated from protocols.py
    Tool: Bash
    Steps:
      1. grep -n '\bAny\b' flext-core/src/flext_core/protocols.py
      2. make check PROJECT=flext-core
    Expected Result: Zero Any usages, checks pass
    Evidence: .sisyphus/evidence/task-7-protocols-any.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(protocols): replace Any with t.AnnotationMap and specific types`
  - Files: `protocols.py`

- [ ] 8. Fix Any in settings.py (3 instances)

  **What to do**:
  - Line 19: Remove `Any` from typing imports
  - Line 220: `**_kwargs: Any` in `__new__` → `**_kwargs: t.GeneralValueType`
  - Line 257: `**kwargs: Any` in `__init__` → `**kwargs: t.GeneralValueType`
  - CRITICAL: Test that Pydantic v2 BaseSettings doesn't reject the signature change
  - If Pydantic rejects: use `**kwargs: t.ScalarValue | BaseModel | Mapping[str, t.ScalarValue]` instead

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Tasks 12-18
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/settings.py:19,220,257` — Any locations
  - `lib-pydantic-v2` skill — Pydantic v2 BaseSettings constructor patterns

  **Acceptance Criteria**:
  - [ ] `grep -n '\bAny\b' flext-core/src/flext_core/settings.py` returns ZERO lines
  - [ ] `make test PROJECT=flext-core` passes (Pydantic accepts new types)

  **QA Scenarios:**
  ```
  Scenario: Any eliminated from settings.py without breaking Pydantic
    Tool: Bash
    Steps:
      1. grep -n '\bAny\b' flext-core/src/flext_core/settings.py
      2. make test PROJECT=flext-core
    Expected Result: Zero Any, all settings tests pass
    Evidence: .sisyphus/evidence/task-8-settings-any.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(settings): replace Any with specific types`
  - Files: `settings.py`

- [ ] 9. Fix Any in **init**.py + lazy.py + _decorators/**init** +_dispatcher/**init** (PEP 562 pattern)

  **What to do**:
  - Replace `-> Any` with `-> t.LazyExportType` in ALL **getattr** PEP 562 functions:
    - `flext-core/src/flext_core/__init__.py:153`
    - `flext-core/src/flext_core/_utilities/lazy.py:22`
    - `flext-core/src/flext_core/_decorators/__init__.py:35`
    - `flext-core/src/flext_core/_dispatcher/__init__.py:51`
  - Remove `from typing import Any` from each file if no longer needed
  - Keep `# noqa: ANN401` only if ruff still requires it (may not after type change)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `flext-import-rules`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 19
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/__init__.py:153` — main **getattr**
  - `flext-core/src/flext_core/_utilities/lazy.py:14,20,22` — lazy_getattr helper
  - `flext-core/src/flext_core/_decorators/__init__.py:12,35`
  - `flext-core/src/flext_core/_dispatcher/__init__.py:13,51`

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_core/__init__.py flext-core/src/flext_core/_utilities/lazy.py flext-core/src/flext_core/_decorators/__init__.py flext-core/src/flext_core/_dispatcher/__init__.py` returns ZERO lines

  **QA Scenarios:**
  ```
  Scenario: Any replaced with LazyExportType in PEP 562 __getattr__
    Tool: Bash
    Steps:
      1. grep -rn '\bAny\b' flext-core/src/flext_core/__init__.py flext-core/src/flext_core/_utilities/lazy.py
      2. grep -n 'LazyExportType' flext-core/src/flext_core/__init__.py
      3. make check PROJECT=flext-core
    Expected Result: Zero Any, LazyExportType used, checks pass
    Evidence: .sisyphus/evidence/task-9-init-any.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(init): replace Any with t.LazyExportType in PEP 562 lazy loading`
  - Files: `__init__.py`, `_utilities/lazy.py`, `_decorators/__init__.py`, `_dispatcher/__init__.py`

- [ ] 10. Fix Any in flext_tests **init** files

  **What to do**:
  - `flext-core/src/flext_tests/__init__.py` — replace `Any` with `t.LazyExportType` in **getattr**
  - `flext-core/src/flext_tests/_validator/__init__.py` — same pattern

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 19
  - **Blocked By**: Task 1

  **Acceptance Criteria**:
  - [ ] `grep -rn '\bAny\b' flext-core/src/flext_tests/__init__.py flext-core/src/flext_tests/_validator/__init__.py` returns ZERO lines

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(flext_tests): replace Any with t.LazyExportType`
  - Files: `flext_tests/__init__.py`, `flext_tests/_validator/__init__.py`

- [ ] 11. Fix type() narrowing in _validator/tests.py (7 instances)

  **What to do**:
  - Replace all `type(decorator) is ast.Name` with `isinstance(decorator, ast.Name)` (7 locations around lines 215-237)
  - Same for `type(decorator.func) is ast.Attribute` and similar patterns
  - Do NOT touch `type(x).__mro__` patterns in matchers.py — those are NOT narrowing violations

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 19
  - **Blocked By**: None

  **References**:
  - `flext-core/src/flext_tests/_validator/tests.py:215-237` — type() narrowing locations
  - `flext-strict-typing` Rule 17 — isinstance for narrowing, NOT type()

  **Acceptance Criteria**:
  - [ ] `grep -n 'type(.*) is ' flext-core/src/flext_tests/_validator/tests.py` returns ZERO lines

  **QA Scenarios:**
  ```
  Scenario: type() narrowing replaced with isinstance()
    Tool: Bash
    Steps:
      1. grep -n 'type(.*) is ' flext-core/src/flext_tests/_validator/tests.py
      2. grep -n 'isinstance(' flext-core/src/flext_tests/_validator/tests.py | wc -l
      3. make check PROJECT=flext-core
    Expected Result: Zero type() is patterns, isinstance count increased, checks pass
    Evidence: .sisyphus/evidence/task-11-type-narrowing.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(flext_tests): replace type() narrowing with isinstance()`
  - Files: `flext_tests/_validator/tests.py`

- [ ] 11b. Fix `__class__` identity-comparison patterns across 8 source files (28 instances)

  **What to do**:
  - Replace all `__class__ in {list, tuple}`, `__class__ not in {list, tuple}`, `__class__ is X`, `__class__ == X` patterns with `isinstance()` equivalent
  - Files affected (28 total instances): `_models/collections.py` (9), `_utilities/domain.py` (4), `_utilities/parser.py` (3), `_utilities/mapper.py` (3), `_utilities/conversion.py` (3), `_utilities/guards.py` (2), `_utilities/collection.py` (2), `_models/entity.py` (2)
  - Pattern: `if value.__class__ in {str, int, float}:` → `if isinstance(value, (str, int, float)):`
  - Pattern: `if current.__class__ not in {list, tuple}:` → `if not isinstance(current, (list, tuple)):`

  **Must NOT do**:
  - Do NOT change `__class__` access for introspection/logging purposes (only identity comparison)
  - Do NOT change `type(x).__mro__` patterns — these are MRO introspection, not narrowing

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocks**: Task 24
  - **Blocked By**: None

  **References**:
  - 8 source files listed above with instance counts
  - `flext-strict-typing` Rule 17 — isinstance for narrowing, NOT type()/**class**

  **Acceptance Criteria**:
  - [ ] `grep -rn '__class__.*in {\|__class__.*not in {\|__class__ is \|__class__ ==' flext-core/src/flext_core/ --include='*.py'` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: __class__ identity patterns replaced with isinstance()
    Tool: Bash
    Steps:
      1. grep -rn '__class__.*in {\|__class__ is ' flext-core/src/flext_core/ --include='*.py'
      2. make check PROJECT=flext-core
      3. make test PROJECT=flext-core
    Expected Result: Zero __class__ identity patterns, checks and tests pass
    Evidence: .sisyphus/evidence/task-11b-class-narrowing.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(core): replace __class__ identity patterns with isinstance()`
  - Files: `_models/collections.py`, `_utilities/domain.py`, `_utilities/parser.py`, `_utilities/mapper.py`, `_utilities/conversion.py`, `_utilities/guards.py`, `_utilities/collection.py`, `_models/entity.py`

- [ ] 12. Eliminate custom JSON functions from mapper.py

  **What to do**:
  - DELETE `is_json_primitive()` (line 431) — replaced by Pydantic v2 `TypeAdapter(JsonValue).validate_python()`
  - DELETE `convert_to_json_value()` (line 441) — replaced by `TypeAdapter(JsonValue).dump_python(v, mode='json')`
  - DELETE `convert_dict_to_json()` (line 511) — replaced by `TypeAdapter(dict[str, JsonValue]).dump_python(d, mode='json')`
  - DELETE `convert_list_to_json()` (line 534) — replaced by `TypeAdapter(list[JsonValue]).dump_python(l, mode='json')`
  - DELETE `_apply_to_json()` (line 1788) — the entire `to_json` parameter threading pattern
  - REMOVE `to_json` parameter from `_transform_dict_mapping()` and all callers in mapper.py
  - REMOVE `to_json` from `transform_opts.get("to_json")` flow (line 1674)
  - For methods that used `to_json=True`: callers should use `model_dump(mode='json')` instead
  - Pydantic v2 API: `from pydantic import TypeAdapter, JsonValue`

  **Must NOT do**:
  - Do NOT delete non-JSON methods (`map_dict_keys`, `get`, `find_callable`, etc.) — only JSON-specific code
  - Do NOT change the class structure of FlextUtilitiesMapper
  - Do NOT change the `_MapperCallable` type alias (it's private and not JSON-related)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-11, 13)
  - **Blocks**: Tasks 14, 19
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/_utilities/mapper.py:431-554` — JSON functions to delete
  - `flext-core/src/flext_core/_utilities/mapper.py:1674-1895` — `to_json` parameter threading
  - `flext-core/src/flext_core/_utilities/mapper.py:2456-2491` — `to_json` in transform method
  - Pydantic v2 docs: `TypeAdapter.dump_python(v, mode='json')` for recursive JSON-safe conversion
  - Pydantic v2 docs: `from pydantic import JsonValue` — native JSON value type

  **Acceptance Criteria**:
  - [ ] `grep -n 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|_apply_to_json' flext-core/src/flext_core/_utilities/mapper.py` returns ZERO lines
  - [ ] `grep -n 'to_json' flext-core/src/flext_core/_utilities/mapper.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: All custom JSON functions deleted from mapper.py
    Tool: Bash
    Steps:
      1. grep -n 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|_apply_to_json' flext-core/src/flext_core/_utilities/mapper.py
      2. grep -n 'to_json' flext-core/src/flext_core/_utilities/mapper.py
      3. make check PROJECT=flext-core
    Expected Result: Zero matches for deleted functions, zero to_json references, checks pass
    Evidence: .sisyphus/evidence/task-12-mapper-json.txt

  Scenario: Non-JSON mapper methods still work
    Tool: Bash
    Steps:
      1. make test PROJECT=flext-core -- -k 'test_utilities_mapper' --ignore=tests/unit/test_utilities_mapper_full_coverage.py --ignore=tests/unit/test_utilities_mapper_coverage_100.py
      2. Verify tests that don't use deleted JSON functions still pass
    Expected Result: All non-JSON mapper tests pass
    Evidence: .sisyphus/evidence/task-12-mapper-non-json.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(mapper): eliminate custom JSON functions, use Pydantic v2 native JSON`
  - Files: `_utilities/mapper.py`

- [ ] 13. Eliminate custom JSON types from conversion.py + parser.py

  **What to do**:
  - **USER DECISION**: DELETE StrictJsonScalar/StrictJsonValue entirely. Use `pydantic.JsonValue` where JSON is intended. For methods that need `datetime` support, add `| datetime` explicitly to their parameter types.
  - STEP 1: DELETE `StrictJsonScalar` type alias (conversion.py:17) entirely
  - STEP 2: DELETE `StrictJsonValue` type alias (conversion.py:18-20) entirely
  - STEP 3: DELETE `_StrictJsonScalarModel` class (conversion.py:23-27)
  - STEP 4: DELETE `_strict_json_list_adapter` class attribute (conversion.py:43-45)
  - STEP 5: DELETE `_strict_json_scalar_adapter` class attribute (conversion.py:46-48)
  - STEP 6: Update 24 method signatures in conversion.py:
    - Methods handling pure JSON values: use `pydantic.JsonValue` or `t.JsonValue`
    - Methods that ALSO accept `datetime` (e.g. `to_str`, `to_str_list`): use `t.ConfigMapValue` or `pydantic.JsonValue | datetime`
    - Use `lsp_find_references` to trace each usage and determine correct replacement
  - STEP 7: DELETE `_to_json_value()` from parser.py (line 78) — replaced by `TypeAdapter(JsonValue).validate_python()`
  - STEP 8: Update parser.py line 1134 to use Pydantic v2 instead of calling `_to_json_value()`
  - Pydantic v2 API: `from pydantic import JsonValue, TypeAdapter`

  **Must NOT do**:
  - Do NOT delete non-JSON methods from conversion.py (`to_str`, `to_str_list`, etc.)
  - Do NOT delete `_float_adapter`, `_str_adapter`, `_str_list_adapter` — these are not JSON-related

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 4-12)
  - **Blocks**: Task 14
  - **Blocked By**: Task 1

  **References**:
  - `flext-core/src/flext_core/_utilities/conversion.py:17-48` — JSON types and adapters to delete
  - `flext-core/src/flext_core/_utilities/parser.py:78` — `_to_json_value()` to delete
  - `flext-core/src/flext_core/_utilities/parser.py:1134` — caller of `_to_json_value()` to update
  - Pydantic v2: `from pydantic import JsonValue` replaces StrictJsonScalar/StrictJsonValue

  **Acceptance Criteria**:
  - [ ] `grep -n 'StrictJsonScalar\|StrictJsonValue\|_StrictJsonScalarModel\|_strict_json_list_adapter\|_strict_json_scalar_adapter' flext-core/src/flext_core/_utilities/conversion.py` returns ZERO lines
  - [ ] `grep -n '_to_json_value' flext-core/src/flext_core/_utilities/parser.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: Custom JSON types eliminated from conversion.py and parser.py
    Tool: Bash
    Steps:
      1. grep -n 'StrictJsonScalar\|StrictJsonValue\|_StrictJsonScalarModel' flext-core/src/flext_core/_utilities/conversion.py
      2. grep -n '_to_json_value' flext-core/src/flext_core/_utilities/parser.py
      3. make check PROJECT=flext-core
    Expected Result: Zero JSON type remnants, checks pass
    Evidence: .sisyphus/evidence/task-13-conversion-json.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(conversion+parser): eliminate custom JSON types, use pydantic.JsonValue`
  - Files: `_utilities/conversion.py`, `_utilities/parser.py`

- [ ] 14. Eliminate custom JSON from context.py + runtime.py + utilities.py

  **What to do**:
  - `_models/context.py`: DELETE `check_json_serializable()` method (line 346) — replaced by `TypeAdapter(JsonValue).validate_python(value)`
  - `_models/context.py`: Update callers at lines 429 and 539 to use `TypeAdapter(pydantic.JsonValue).validate_python(working_value)` instead
  - `runtime.py:486`: Replace `json.dumps(normalized_mapping)` with `TypeAdapter(dict[str, t.ConfigMapValue]).dump_json(normalized_mapping).decode()` or `model_dump_json()`
  - `runtime.py:504-531`: Replace `is_valid_json()` — keep the TypeGuard signature, but replace `json.loads()` internals with `TypeAdapter(JsonValue).validate_json(value)` in try/except
  - `runtime.py:47`: Remove `import json` — no longer needed after above changes
  - `utilities.py:293-295,372`: DELETE facade aliases `convert_dict_to_json`, `convert_list_to_json`, `convert_to_json_value`, `is_json_primitive` — underlying functions no longer exist
  - VERIFY: `json_schema_extra` usage in `_models/cqrs.py`, `_models/handler.py`, `_models/settings.py`, `_models/base.py` — these are Pydantic v2 NATIVE and must be KEPT

  **Must NOT do**:
  - Do NOT remove `json_schema_extra` from any model — it's Pydantic v2 native
  - Do NOT change `is_valid_json()` signature — keep `TypeGuard[str]` return
  - Do NOT remove non-JSON facade aliases from utilities.py

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on 12+13 completing first — facade aliases reference deleted functions)
  - **Parallel Group**: Wave 2 (after Tasks 12, 13)
  - **Blocks**: Task 21
  - **Blocked By**: Tasks 1, 12, 13

  **References**:
  - `flext-core/src/flext_core/_models/context.py:346-369,429,539` — check_json_serializable + callers
  - `flext-core/src/flext_core/runtime.py:47,486,504-531` — import json, json.dumps, is_valid_json
  - `flext-core/src/flext_core/utilities.py:293-295,372` — facade aliases to delete
  - Pydantic v2: `TypeAdapter(JsonValue).validate_json(s)` for JSON string validation
  - Pydantic v2: `TypeAdapter(dict[str, T]).dump_json(d)` for dict → JSON bytes

  **Acceptance Criteria**:
  - [ ] `grep -n 'check_json_serializable' flext-core/src/flext_core/_models/context.py` returns ZERO lines
  - [ ] `grep -n 'import json' flext-core/src/flext_core/runtime.py` returns ZERO lines
  - [ ] `grep -n 'convert_dict_to_json\|convert_list_to_json\|convert_to_json_value\|is_json_primitive' flext-core/src/flext_core/utilities.py` returns ZERO lines
  - [ ] `make check PROJECT=flext-core` exits 0
  - [ ] `make test PROJECT=flext-core` exits 0

  **QA Scenarios:**
  ```
  Scenario: Custom JSON eliminated from context, runtime, utilities
    Tool: Bash
    Steps:
      1. grep -n 'check_json_serializable' flext-core/src/flext_core/_models/context.py
      2. grep -n 'import json' flext-core/src/flext_core/runtime.py
      3. grep -rn 'convert_dict_to_json\|convert_list_to_json\|convert_to_json_value\|is_json_primitive' flext-core/src/flext_core/utilities.py
      4. make check PROJECT=flext-core
      5. make test PROJECT=flext-core
    Expected Result: Zero custom JSON remnants, all checks and tests pass
    Evidence: .sisyphus/evidence/task-14-context-runtime-json.txt

  Scenario: is_valid_json still works with Pydantic v2 internals
    Tool: Bash
    Steps:
      1. grep -n 'is_valid_json' flext-core/src/flext_core/runtime.py
      2. grep -n 'TypeGuard' flext-core/src/flext_core/runtime.py
      3. make test PROJECT=flext-core -- -k 'test_runtime' -x
    Expected Result: is_valid_json exists with TypeGuard signature, runtime tests pass
    Evidence: .sisyphus/evidence/task-14-valid-json.txt
  ```

  **Commit**: YES (groups with Wave 2)
  - Message: `refactor(core): eliminate custom JSON from context/runtime/utilities, use Pydantic v2`
  - Files: `_models/context.py`, `runtime.py`, `utilities.py`

- [ ] 15. Fix cast() in test_automated_*.py (31 casts)

  **What to do**:
  - Remove all 31 `cast()` calls across 7 test files: `test_automated_container.py` (5), `test_automated_context.py` (2), `test_automated_decorators.py` (5), `test_automated_exceptions.py` (5), `test_automated_handlers.py` (1), `test_automated_loggings.py` (8), `test_automated_mixins.py` (5)
  - Most common pattern: `cast("str", obj)` — replace with `isinstance(obj, str)` assertions or direct variable typing
  - For each cast: determine the actual type being tested and replace with isinstance check, direct type annotation, or TypeGuard

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Tasks 16-23)
  - **Blocked By**: Tasks 4-8

  **References**:
  - `flext-core/tests/unit/test_automated_*.py` — 7 files with 31 cast() calls
  - `flext-strict-typing` — cast() PROHIBITED, use isinstance/TypeGuard instead

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_automated_*.py` returns ZERO lines
  - [ ] `make test PROJECT=flext-core -- -k 'test_automated'` passes

  **QA Scenarios:**
  ```
  Scenario: All cast() removed from automated tests
    Tool: Bash
    Steps:
      1. grep -rn 'cast(' flext-core/tests/unit/test_automated_*.py
      2. make test PROJECT=flext-core -- -k 'test_automated'
    Expected Result: Zero cast, all automated tests pass
    Evidence: .sisyphus/evidence/task-15-automated-cast.txt
  ```

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from test_automated files`

- [ ] 16. Fix cast() in test_coverage_*.py + test_container*.py + test_context*.py (39 casts)

  **What to do**:
  - Remove all 39 cast() calls across 6 files: `test_coverage_exceptions.py` (6), `test_coverage_utilities.py` (3), `test_container.py` (2), `test_container_full_coverage.py` (3), `test_context_full_coverage.py` (7), `test_models_context_full_coverage.py` (18)
  - Most common pattern: `cast("dict", obj)` — replace with isinstance + direct typing

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_coverage_*.py flext-core/tests/unit/test_container*.py flext-core/tests/unit/test_context*.py flext-core/tests/unit/test_models_context*.py` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from coverage/container/context tests`

- [ ] 17. Fix cast() in test_dispatcher*.py + test_handlers*.py + test_decorators*.py (64 casts)

  **What to do**:
  - Remove all 64 cast() calls across 5 files: `test_dispatcher_full_coverage.py` (11), `test_dispatcher_minimal.py` (16), `test_handlers.py` (20), `test_handlers_full_coverage.py` (4), `test_decorators_full_coverage.py` (13)
  - Most common pattern: `cast("Callable", obj)` — replace with Protocol-based type checking

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_dispatcher*.py flext-core/tests/unit/test_handlers*.py flext-core/tests/unit/test_decorators*.py` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from dispatcher/handlers/decorators tests`

- [ ] 18. Fix cast() in test_service*.py + test_settings*.py (4 casts)

  **What to do**:
  - Remove 4 cast() calls: `test_service_full_coverage.py` (4)
  - NOTE: test_result*.py files (28 casts) are EXCLUDED — cast() is ALLOWED in result.py and its tests

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_service*.py flext-core/tests/unit/test_settings*.py` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from service/settings tests`

- [ ] 19. Fix cast() in test_utilities_mapper*.py (150+ casts) + update JSON test refs

  **What to do**:
  - Remove 150+ cast() calls from `test_utilities_mapper_full_coverage.py` and `test_utilities_mapper_coverage_100.py`
  - ALSO update 24 references to deleted JSON functions (`convert_to_json_value`, `convert_dict_to_json`, `convert_list_to_json`, `is_json_primitive`, `_apply_to_json`, `to_json`)
  - DELETE or rewrite test cases that test deleted functions — these tests are no longer needed
  - Keep test cases for non-JSON mapper methods
  - Complex patterns: nested casts, casts in assertions — need case-by-case replacement

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Task 12 (mapper JSON functions must be deleted first)

  **References**:
  - `flext-core/tests/unit/test_utilities_mapper_full_coverage.py` — 12 JSON refs + many casts
  - `flext-core/tests/unit/test_utilities_mapper_coverage_100.py` — 12 JSON refs + many casts

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_utilities_mapper*.py` returns ZERO lines
  - [ ] `grep -rn 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|_apply_to_json' flext-core/tests/unit/test_utilities_mapper*.py` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() and JSON refs from mapper tests`

- [ ] 20. Fix cast() in other test_utilities*.py + test_mixins*.py (175 casts)

  **What to do**:
  - Remove ~175 cast() calls across remaining test_utilities files and `test_mixins_full_coverage.py` (22)
  - Excludes test_utilities_mapper*.py (handled in Task 19)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_utilities_[!m]*.py flext-core/tests/unit/test_mixins*.py` returns ZERO lines (excludes mapper files)

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from utilities/mixins tests`

- [ ] 21. Fix cast() in test_runtime*.py (74 casts) + update JSON test refs (11 calls)

  **What to do**:
  - Remove 74 cast() calls across `test_runtime.py` (20), `test_runtime_coverage_100.py` (12), `test_runtime_full_coverage.py` (42)
  - Update 6 references to `is_valid_json` and `json.dumps`/`json.loads` patterns that were changed in Task 14
  - DELETE or rewrite test cases that test old `json.loads()`/`json.dumps()` internals

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`, `lib-pydantic-v2`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Task 14 (runtime JSON must be replaced first)

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_runtime*.py` returns ZERO lines
  - [ ] `make test PROJECT=flext-core -- -k 'test_runtime'` passes

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() and update JSON refs in runtime tests`

- [ ] 22. Fix cast() in test_flext_tests/*.py + test_exceptions*.py + test_loggings*.py + remaining (150 casts)

  **What to do**:
  - Remove ~150 cast() calls across: `test_flext_tests/test_builders.py` (41), `test_flext_tests/test_factories.py` (43), `test_flext_tests/test_matchers.py` (4), `test_protocols_full_coverage.py` (7), `test_registry.py` (5), `test_registry_full_coverage.py` (5), `test_config.py` (1), `test_exceptions.py` (39), `test_loggings_full_coverage.py` (22), `test_di_services_access.py` (5), `test_final_75_percent_push.py` (1), `test_handler_decorator_discovery.py` (1)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_exceptions*.py flext-core/tests/unit/test_loggings*.py flext-core/tests/unit/test_protocols*.py flext-core/tests/unit/test_registry*.py` returns ZERO lines
  - [ ] `grep -rn 'cast(' flext-core/tests/unit/test_flext_tests/` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from remaining test files`

- [ ] 23. Fix cast() in tests/integration/ + tests/benchmark/ (1 verified cast)

  **What to do**:
  - Directory-driven: run `grep -rn 'cast(' flext-core/tests/integration/ flext-core/tests/benchmark/ --include='*.py'` and fix ALL matches found
  - Verified match: `flext-core/tests/integration/patterns/test_advanced_patterns.py:319` — `cast("FixtureCaseDict", kwargs)`
  - Also scan: `flext-core/tests/integration/test_integration.py`, `test_config_integration.py`, `test_infra_integration.py`, `test_service.py`, `test_system.py`, `test_migration_validation.py`
  - Also scan: `flext-core/tests/benchmark/test_container_memory.py`, `test_container_performance.py`
  - Fix ALL cast() found regardless of count (grep is authoritative, not estimates)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocked By**: Tasks 4-8

  **Acceptance Criteria**:
  - [ ] `grep -rn 'cast(' flext-core/tests/integration/ flext-core/tests/benchmark/` returns ZERO lines

  **Commit**: YES (groups with Wave 3)
  - Message: `refactor(tests): eliminate cast() from integration/benchmark tests`

- [ ] 24. Full quality gate verification

  **What to do**:
  - Run ALL Definition of Done verification commands
  - Run `make check PROJECT=flext-core` (lint + type check)
  - Run `make test PROJECT=flext-core` (full test suite)
  - Grep for remaining violations: cast(), Any, type() is, custom JSON functions, StrictJsonScalar/Value
  - Generate evidence report for final verification wave

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-quality-gates`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Blocked By**: ALL tasks 1-23

  **Acceptance Criteria**:
  - [ ] ALL Definition of Done commands return expected results
  - [ ] Zero remaining violations of any category
  - [ ] Evidence files generated for all checks

  **QA Scenarios:**
  ```
  Scenario: Zero violations remain across all categories
    Tool: Bash
    Steps:
      1. grep -rn 'cast(' flext-core/src/flext_core/ --include='*.py' | grep -v result.py
      2. grep -rn 'cast(' flext-core/tests/ --include='*.py' | grep -v test_result
      3. grep -rn ': Any\b\|-> Any\b\|, Any\b' flext-core/src/ --include='*.py'
      4. grep -rn 'type(.*) is ' flext-core/src/flext_tests/ --include='*.py'
      5. grep -rn 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|check_json_serializable\|StrictJsonScalar\|StrictJsonValue' flext-core/src/ --include='*.py'
      6. make check PROJECT=flext-core
      7. make test PROJECT=flext-core
    Expected Result: ALL return zero violations, make check + test exit 0
    Evidence: .sisyphus/evidence/task-24-final-verification.txt
  ```

  **Commit**: YES
  - Message: `chore(flext-core): verify zero-tolerance compliance`
## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. For each "Must Have": verify implementation exists (grep for violations). For each "Must NOT Have": search codebase for forbidden patterns — reject with file:line if found. Check evidence files exist in .sisyphus/evidence/. Compare deliverables against plan.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `make check PROJECT=flext-core`. Review all changed files for: `cast()`, `Any`, `type() is` patterns, `# type: ignore`. Check AI slop: excessive comments, over-abstraction.
  Output: `Build [PASS/FAIL] | Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  Start from clean state. Run EVERY verification command from Definition of Done. Verify zero violations remain. Save output to `.sisyphus/evidence/final-qa/`.
  Output: `Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  For each task: read "What to do", read actual diff. Verify 1:1 — everything in spec was built, nothing beyond spec was built. Check "Must NOT do" compliance. Flag unaccounted changes.
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `refactor(typings): add LazyExportType + AnnotationMap, remove dead TypeVars` — typings.py, registry.py, context.py
- **Wave 2a**: `refactor(flext-core): eliminate cast/Any/type-narrowing violations` — container.py, mixins.py, _models/context.py, protocols.py, settings.py, **init**.py files,_validator/tests.py
- **Wave 2b**: `refactor(mapper): eliminate custom JSON functions, use Pydantic v2 native JSON` — mapper.py
- **Wave 2c**: `refactor(conversion+parser): eliminate custom JSON types, use pydantic.JsonValue` — conversion.py, parser.py
- **Wave 2d**: `refactor(core): eliminate custom JSON from context/runtime/utilities, use Pydantic v2` — _models/context.py, runtime.py, utilities.py
- **Wave 3**: `refactor(tests): eliminate all cast() from test files` + `refactor(tests): update JSON test refs` — tests/unit/*.py, tests/integration/*.py
- **Wave 4**: `chore(flext-core): verify zero-tolerance compliance` — evidence files

---

## Success Criteria

### Verification Commands
```bash
# Zero cast() outside result.py
grep -rn "cast(" flext-core/src/flext_core/ --include="*.py" | grep -v result.py
# Expected: empty

# Zero cast() in tests
grep -rn "cast(" flext-core/tests/ --include="*.py" | grep -v test_result
# Expected: empty

# Zero Any in source
grep -rn ": Any\b\|-> Any\b\|, Any\)" flext-core/src/ --include="*.py"
# Expected: empty

# Zero type() narrowing
grep -rn "type(.*) is \|type(.*) == " flext-core/src/flext_tests/_validator/tests.py
# Expected: empty

# Full quality gate
make check PROJECT=flext-core
# Expected: exit 0

# Full test suite
make test PROJECT=flext-core
# Expected: exit 0

# Zero custom JSON functions
grep -rn 'convert_to_json_value\|convert_dict_to_json\|convert_list_to_json\|is_json_primitive\|check_json_serializable\|StrictJsonScalar\|StrictJsonValue' flext-core/src/ --include='*.py'
# Expected: empty

# Zero import json in runtime
grep -n 'import json' flext-core/src/flext_core/runtime.py
# Expected: empty
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass
- [ ] Zero `cast()` (except result.py)
- [ ] Zero `Any`
- [ ] Zero `type()` narrowing
- [ ] New types `t.LazyExportType` and `t.AnnotationMap` created and used
- [ ] Zero custom JSON functions in source
- [ ] `import json` removed from runtime.py
- [ ] `pydantic.JsonValue` used where custom JSON types existed
- [ ] All facade aliases for deleted JSON methods removed from utilities.py
