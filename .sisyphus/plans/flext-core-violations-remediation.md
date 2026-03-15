# flext-core Violations Remediation

## TL;DR

> **Quick Summary**: Fix ALL violations to AGENTS.md governance standards in `flext-core/src/flext_core/` — eliminate forbidden constructs, standardize type patterns, audit and triage 400+ dynamic dispatch calls, convert fallible returns to `r[T]`.
> 
> **Deliverables**:
> - 0 `model_rebuild()` calls (from 6)
> - 0 `type()` narrowing (from 1)
> - 0 deprecated `TypeAlias` syntax (from 1)
> - 0 bare `object` violations (from 3 real; 6 were false positives)
> - 0 `r[bool] | None` redundant returns (from 16)
> - 0 `except Exception` broad catches (from 8)
> - 0 loose module-level functions (from 11)
> - Classified audit of 186 getattr + 52 setattr + 192 try/except
> - Converted fallible `T | None` returns to `r[T]` (~42 return sites)
> 
> **Estimated Effort**: Large
> **Parallel Execution**: YES — 4 waves + FINAL
> **Critical Path**: T1 (baseline) → T3 (model_rebuild) → T11 (protocols) → FINAL

---

## Context

### Original Request
Fix ALL violations to AGENTS.md and skills in flext-core to standardize patterns, remove duplications, and eliminate forbidden constructs. User confirmed: ALL getattr/setattr/try-except audited, ALL T|None converted.

### Interview Summary
**Key Decisions**:
- Scope: ALL violations, not phased
- ALL 230+ getattr/setattr audited
- ALL T|None returns converted to r[T]
- ALL try/except blocks audited

**Research Findings**:
- 63 .py files scanned exhaustively
- ~39 distinct violation types across 8 categories
- 6 `__eq__(other: object)` are FALSE POSITIVES (Python dunder mandate)
- `make check` is BROKEN (CliArgs validation error) — use direct `ruff check`/`pytest`
- FROZEN files per §10.2: context.py, settings.py, models.py, utilities.py, __version__.py
- Baseline: 3197 passed, 4 failed tests; ruff clean

### Metis Review
**Identified Gaps (addressed)**:
- False positives in bare `object` (6 of 9 are Python-mandated dunder signatures) — EXCLUDED
- FROZEN file violations — DEFERRED to separate plan
- container.py setattr (14) and result.py setattr (12) are DI/Result MECHANISMS — EXCLUDED
- Logging try/except (19 blocks) are defensive guards — classified as LEGITIMATE
- T|None overcount corrected: 42 actual return-type violations (not 85+)
- 200-line cap violations (12+ files) — OUT OF SCOPE (separate plan)
- Downstream consumer cascade risk — audit-before-change protocol added
- model_rebuild() removal needs import verification — added pre-check

---

## Work Objectives

### Core Objective
Bring flext-core/src/flext_core/ into FULL compliance with AGENTS.md §2-§4 and all governance skills by eliminating forbidden constructs, standardizing type patterns, and auditing dynamic dispatch usage.

### Concrete Deliverables
- Zero forbidden constructs (`model_rebuild`, `type()` narrowing, deprecated `TypeAlias`)
- Zero `r[T] | None` redundant patterns
- Zero `except Exception` broad catches
- Zero loose module-level functions
- Triage matrix for all getattr/setattr/try-except (LEGITIMATE vs VIOLATION vs DEFERRED)
- All fallible return types converted from `T | None` to `r[T]`

### Definition of Done
- [ ] `python -m ruff check src/` → "All checks passed!"
- [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= 3197, failed <= 4
- [ ] `python -c "from flext_core import r, t, c, m, p, u"` → "OK"
- [ ] Zero grep hits for `model_rebuild()`, `type(.*) is type(`, `TypeAlias` in governed files
- [ ] Evidence stored in `.sisyphus/evidence/`

### Must Have
- ALL forbidden constructs eliminated
- ALL `r[bool] | None` converted to `r[bool]`
- ALL loose functions absorbed into namespace classes
- ALL `except Exception` replaced with specific exception types
- Triage report for getattr/setattr/try-except audit
- ALL fallible `T | None` returns converted to `r[T]`

### Must NOT Have (Guardrails)
- **DO NOT** change `__eq__(self, other: object)` or `model_post_init(__context: object)` — Python/Pydantic mandate
- **DO NOT** change setattr in container.py (14 calls) or result.py (12 calls) — these ARE the mechanism
- **DO NOT** change try/except in loggings.py defensive guards unless classified as BUSINESS_LOGIC per audit
- **DO NOT** touch FROZEN files behaviorally (context.py, settings.py, models.py, utilities.py, __version__.py)
- **DO NOT** enforce 200-line cap (separate plan)
- **DO NOT** touch `__init__.py` files (auto-generated — use `make codegen`)
- **DO NOT** fix pre-existing 4 test failures
- **DO NOT** fix downstream consumer breakage (scope is flext-core only)
- **TEMPORARY GOVERNANCE EXCEPTION** (§5 Make Contract): `make check PROJECT=flext-core` is currently broken due to a CliArgs validation error in `flext_infra` (separate package, out of scope). Until that is fixed, this plan uses direct tool invocations as substitute `make` targets:
    - `python -m ruff check src/` substitutes `make check PROJECT=flext-core CHECK_GATES=lint`
    - `python -m pytest tests/ --ignore=tests/infra --tb=no -q` substitutes `make test PROJECT=flext-core`
    - This exception applies ONLY to this plan. A separate beads issue should be filed to fix `make check`.
    - **Justification**: §5 says "make is the mandatory entrypoint" but also §6 says "No Silent Failures" — a broken make target silently prevents quality gates. Direct tool invocation preserves the gate intent while the make infrastructure is repaired.

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — ALL verification is agent-executed. No exceptions.

### Test Decision
- **Infrastructure exists**: YES
- **Automated tests**: YES (Tests-after — verify characterization)
- **Framework**: pytest
- **Approach**: Capture baseline → make fix → verify no regression

### QA Policy
Every task MUST include agent-executed QA scenarios.
Evidence saved to `.sisyphus/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Import health**: `python -c "from flext_core.MODULE import CLASS"` after every file change
- **Test suite**: `python -m pytest tests/ --ignore=tests/infra --tb=no -q` after every file change
- **Lint**: `python -m ruff check src/` after every file change
- **Grep verification**: Specific grep commands to verify violation is gone

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — baseline + zero-risk mechanical fixes):
├── Task 1: Capture baseline metrics [quick]
├── Task 2: Fix TypeAlias + type() narrowing [quick]
├── Task 3: Remove model_rebuild() safely [deep]
├── Task 4: Fix bare object violations (3 real) [quick]
├── Task 5: Fix orjson direct calls [quick]
└── Task 6: Absorb loose functions into namespace classes [unspecified-high]

Wave 2 (After Wave 1 — audit frameworks + medium fixes):
├── Task 7: Fix except Exception → specific types (8 sites) [quick]
├── Task 8: Fix r[bool] | None → r[bool] in loggings.py [unspecified-high]
├── Task 9: Audit + classify getattr (186 calls) [deep]
├── Task 10: Audit + classify setattr (52 calls) [deep]
└── Task 11: Audit + classify try/except (192 blocks) [deep]

Wave 3 (After Wave 2 — apply audit results):
├── Task 12: Fix getattr violations (from audit) [unspecified-high]
├── Task 13: Fix setattr violations (from audit) [unspecified-high]
├── Task 14: Fix try/except violations (from audit) [unspecified-high]
├── Task 15: Convert T|None returns → r[T] in non-protocol files [deep]
└── Task 16: Fix classes without MRO lineage [unspecified-high]

Wave 4 (After Wave 3 — protocol/signature changes, SEQUENTIAL):
├── Task 17: Fix r[bool] | None in protocols.py + downstream audit [deep]
├── Task 18: Convert T|None returns → r[T] in protocol-adjacent files [deep]
└── Task 19: Final grep verification + evidence collection [quick]

Wave FINAL (After ALL tasks — independent review, 4 parallel):
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
├── Task F3: Real QA — full test + import smoke (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: T1 → T3 → T8 → T11 → T14 → T17 → T19 → F1-F4
Parallel Speedup: ~60% faster than sequential
Max Concurrent: 5 (Waves 1 & 2)
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| T1 | — | T2-T6, T7-T11 |
| T2 | T1 | T19 |
| T3 | T1 | T19 |
| T4 | T1 | T19 |
| T5 | T1 | T19 |
| T6 | T1 | T19 |
| T7 | T1 | T19 |
| T8 | T1 | T17 |
| T9 | T1 | T12 |
| T10 | T1 | T13 |
| T11 | T1 | T14 |
| T12 | T9 | T19 |
| T13 | T10 | T19 |
| T14 | T11 | T19 |
| T15 | T1 | T18 |
| T16 | T1 | T19 |
| T17 | T8 | T19 |
| T18 | T15, T17 | T19 |
| T19 | T2-T18 | F1-F4 |
| F1-F4 | T19 | — |

### Agent Dispatch Summary

- **Wave 1**: **6** — T1 → `quick`, T2 → `quick`, T3 → `deep`, T4 → `quick`, T5 → `quick`, T6 → `unspecified-high`
- **Wave 2**: **5** — T7 → `quick`, T8 → `unspecified-high`, T9 → `deep`, T10 → `deep`, T11 → `deep`
- **Wave 3**: **5** — T12-T14 → `unspecified-high`, T15 → `deep`, T16 → `unspecified-high`
- **Wave 4**: **3** — T17 → `deep`, T18 → `deep`, T19 → `quick`
- **FINAL**: **4** — F1 → `oracle`, F2 → `unspecified-high`, F3 → `unspecified-high`, F4 → `deep`

---

## TODOs

- [x] 1. Capture Baseline Metrics

  **What to do**:
  - Run full test suite and record pass/fail counts
  - Run ruff check and record clean status
  - Run import smoke test for all public API entries
  - Store baseline in `.sisyphus/evidence/task-1-baseline.txt`

  **Must NOT do**:
  - Change any files
  - Fix any pre-existing test failures

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (must complete first)
  - **Blocks**: T2-T19
  - **Blocked By**: None

  **References**:
  - `flext-core/pyproject.toml` — test configuration and coverage thresholds
  - `flext-core/tests/` — test directory structure

  **Acceptance Criteria**:
  - [ ] `.sisyphus/evidence/task-1-baseline.txt` exists with test counts, ruff status, import result
  - [ ] Baseline test count recorded (expected: ~3197 passed, ~4 failed)

  **QA Scenarios**:
  ```
  Scenario: Baseline capture
    Tool: Bash
    Steps:
      1. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q 2>&1 | tee /tmp/baseline.txt
      2. python -m ruff check src/ 2>&1 | tee -a /tmp/baseline.txt
      3. python -c "from flext_core import r, t, c, m, p, u; print('IMPORT OK')" 2>&1 | tee -a /tmp/baseline.txt
      4. cp /tmp/baseline.txt .sisyphus/evidence/task-1-baseline.txt
    Expected Result: File created with test/lint/import results
    Evidence: .sisyphus/evidence/task-1-baseline.txt
  ```

  **Commit**: NO (no code changes)

- [x] 2. Fix TypeAlias Deprecated Syntax + type() Narrowing

  **What to do**:
  - `_models/entity.py:17,38`: Replace `from typing import TypeAlias` import and `DomainEvent: TypeAlias = FlextModelsDomainEvent.Entry` with PEP 695 `type DomainEvent = FlextModelsDomainEvent.Entry`
  - Remove `TypeAlias` from the typing import line
  - Verify `DomainEvent` is NOT used in any `isinstance()` call (PEP 695 TypeAliasType would crash)
  - `_utilities/domain.py:30`: Replace `return type(obj_a) is type(obj_b)` with `return isinstance(obj_a, type(obj_b))` or better type-safe comparison

  **Must NOT do**:
  - Change any other code in these files
  - Introduce new imports beyond what's needed

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T3, T4, T5, T6)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - `flext-core/src/flext_core/_models/entity.py:17,38` — TypeAlias usage to fix
  - `flext-core/src/flext_core/_utilities/domain.py:30` — type() narrowing to fix
  - `flext-core/src/flext_core/typings.py` — PEP 695 `type X = ...` canonical pattern examples
  - **flext-strict-typing Rule 2**: PEP 695 is canonical; `TypeAlias` is DEPRECATED
  - **AGENTS.md §3.2**: NEVER use type(x) is T for narrowing

  **Acceptance Criteria**:
  - [ ] `grep -rn "TypeAlias" flext-core/src/flext_core/_models/entity.py` → 0 results
  - [ ] `grep -rn "type(.*) is type(" flext-core/src/flext_core/_utilities/domain.py` → 0 results
  - [ ] `python -c "from flext_core._models.entity import FlextModelsEntity; print('OK')"` → OK
  - [ ] `python -m ruff check src/` → clean

  **QA Scenarios**:
  ```
  Scenario: TypeAlias removal verified
    Tool: Bash
    Steps:
      1. grep -rn "TypeAlias" flext-core/src/flext_core/_models/entity.py
      2. python -c "from flext_core._models.entity import FlextModelsEntity; print(FlextModelsEntity.DomainEvent)"
    Expected Result: Step 1: 0 matches. Step 2: prints the type alias reference
    Evidence: .sisyphus/evidence/task-2-typealias.txt

  Scenario: type() narrowing eliminated
    Tool: Bash
    Steps:
      1. grep -rn "type(.*) is type(" flext-core/src/flext_core/_utilities/domain.py
      2. python -c "from flext_core._utilities.domain import FlextUtilitiesDomain; print('OK')"
    Expected Result: Step 1: 0 matches. Step 2: OK
    Evidence: .sisyphus/evidence/task-2-type-narrowing.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): replace deprecated TypeAlias and type() narrowing`
  - Files: `_models/entity.py`, `_utilities/domain.py`
  - Pre-commit: `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q`

- [x] 3. Remove model_rebuild() Safely

  **What to do**:
  - **FIRST**: Verify forward reference graph in `_models/cqrs.py` — map which classes reference which
  - **SECOND**: Test removal safety: comment out all 6 `model_rebuild()` calls (lines 507-512) and run `python -c "from flext_core._models.cqrs import FlextModelsCqrs; print(FlextModelsCqrs.Command.model_fields)"`
  - **IF import fails**: Resolve forward references by reordering class definitions or using `from __future__ import annotations` (already present) + ensuring no runtime class introspection at definition time
  - **IF import succeeds**: Delete the 6 lines permanently
  - Remove the `__all__` export on line 505 if it only exists for model_rebuild

  **Must NOT do**:
  - Change class definitions unless strictly needed for forward reference resolution
  - Add new model_rebuild() calls anywhere
  - Use eval/exec to resolve references

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`rules-flext-core`, `flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2, T4, T5, T6)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - `flext-core/src/flext_core/_models/cqrs.py:507-512` — 6 model_rebuild() calls to remove
  - `flext-core/src/flext_core/_models/cqrs.py:1-506` — class definitions with potential forward references
  - **AGENTS.md §3.4**: "model_rebuild() is TOTALLY FORBIDDEN"
  - **flext-patterns**: "PROHIBITED. Fix the graph or use Protocols."

  **Acceptance Criteria**:
  - [ ] `grep -rn "model_rebuild" flext-core/src/flext_core/` → 0 results
  - [ ] `python -c "from flext_core._models.cqrs import FlextModelsCqrs; print(list(FlextModelsCqrs.Command.model_fields.keys()))"` → prints field names
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline

  **QA Scenarios**:
  ```
  Scenario: model_rebuild eliminated + imports work
    Tool: Bash
    Steps:
      1. grep -rn "model_rebuild" flext-core/src/flext_core/
      2. python -c "from flext_core._models.cqrs import FlextModelsCqrs; print(list(FlextModelsCqrs.Command.model_fields.keys()))"
      3. python -c "from flext_core import m; print(m.Cqrs.Command.model_fields.keys())"
    Expected Result: Step 1: 0 matches. Steps 2-3: print field key lists without error
    Evidence: .sisyphus/evidence/task-3-model-rebuild.txt

  Scenario: Full test suite passes
    Tool: Bash
    Steps:
      1. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: passed >= 3197, failed <= 4
    Evidence: .sisyphus/evidence/task-3-tests.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): remove forbidden model_rebuild() calls from cqrs models`
  - Files: `_models/cqrs.py`
  - Pre-commit: `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q`

- [x] 4. Fix Bare `object` Type Violations (3 Real)

  **What to do**:
  - **EXCLUDE** (FALSE POSITIVES — Python/Pydantic mandated signatures):
    - ALL `__eq__(self, other: object)` signatures (6 occurrences) — Python dunder contract
    - `model_post_init(self, __context: object)` — Pydantic v2 contract
  - **FIX** (3 real violations):
    - `_utilities/guards.py:75` — `type _GuardInput = object` → replace with specific type union or `t.Container`
    - `decorators.py:997` — `args: tuple[object, ...]` → replace with `tuple[t.Container | BaseModel, ...]` or appropriate typed tuple
    - `runtime.py:1135` — `Callable[..., object] | None` → replace with `Callable[..., t.Container | BaseModel] | None` or specific return type
  - Use `lsp_find_references` before each change to verify no downstream breakage

  **Must NOT do**:
  - Change `__eq__`, `__hash__`, `model_post_init` parameter types
  - Change to `Any` (equally forbidden)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-strict-typing`, `flext-type-system`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2, T3, T5, T6)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - `flext-core/src/flext_core/_utilities/guards.py:75` — `type _GuardInput = object`
  - `flext-core/src/flext_core/decorators.py:997` — `args: tuple[object, ...]`
  - `flext-core/src/flext_core/runtime.py:1135` — `Callable[..., object]`
  - `flext-core/src/flext_core/typings.py` — `t.Container`, `t.Scalar` contract definitions
  - **AGENTS.md §3.2**: "bare object is TOTALLY FORBIDDEN — use t.* contracts"

  **Acceptance Criteria**:
  - [ ] `grep -rn ": object" flext-core/src/flext_core/ | grep -v "__eq__\|model_post_init\|__hash__\|#"` → only expected results
  - [ ] `python -m ruff check src/` → clean
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline

  **QA Scenarios**:
  ```
  Scenario: Bare object eliminated (excl. dunders)
    Tool: Bash
    Steps:
      1. grep -rn ": object" flext-core/src/flext_core/ | grep -v "__eq__\|model_post_init\|__hash__\|#\|docstring"
      2. python -c "from flext_core._utilities.guards import FlextUtilitiesGuards; print('OK')"
      3. python -m ruff check src/
    Expected Result: Step 1: 0 non-dunder matches. Steps 2-3: clean
    Evidence: .sisyphus/evidence/task-4-bare-object.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): replace bare object annotations with t.* contracts`
  - Files: `_utilities/guards.py`, `decorators.py`, `runtime.py`
  - Pre-commit: `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q`

- [x] 5. Fix orjson Direct Calls

  **What to do**:
  - `runtime.py:625` — `orjson.loads(value)` → Check if `u.*` provides JSON utility; if so use it; if not, document as legitimate bridge-level usage
  - `_utilities/model.py:279` — `orjson.dumps(plain_mapping).decode()` → Same check
  - If no `u.*` JSON wrapper exists: leave as-is and document rationale (bridge code exception)
  - If wrapper exists: replace with canonical utility

  **Must NOT do**:
  - Create new utility wrappers (not in scope)
  - Use `json.loads`/`json.dumps` (slower, not canonical)

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`rules-flext-core`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2, T3, T4, T6)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - `flext-core/src/flext_core/runtime.py:625` — `orjson.loads(value)`
  - `flext-core/src/flext_core/_utilities/model.py:279` — `orjson.dumps(plain_mapping).decode()`
  - `flext-core/src/flext_core/utilities.py` — Check for existing JSON utility methods
  - **AGENTS.md §3.4**: "Use model_dump_json/model_validate_json"

  **Acceptance Criteria**:
  - [ ] orjson calls either replaced with `u.*` utilities OR documented as legitimate bridge exceptions
  - [ ] `python -m ruff check src/` → clean

  **QA Scenarios**:
  ```
  Scenario: orjson usage audited
    Tool: Bash
    Steps:
      1. grep -rn "orjson\.\(loads\|dumps\)" flext-core/src/flext_core/
      2. python -c "from flext_core.runtime import FlextRuntime; print('OK')"
    Expected Result: Either 0 matches or documented exceptions
    Evidence: .sisyphus/evidence/task-5-orjson.txt
  ```

  **Commit**: YES (if changes made)
  - Message: `fix(flext-core): replace orjson direct calls with canonical utilities`
  - Files: `runtime.py`, `_utilities/model.py`

- [x] 6. Absorb Loose Module-Level Functions into Namespace Classes

  **What to do**:
  - Absorb 11 loose functions into their nearest namespace class as `@staticmethod`:
    - `_utilities/configuration.py:57` — `_duck_dump_get_parameter()` → into `FlextUtilitiesConfiguration`
    - `_utilities/lazy.py:21` — `lazy_getattr()` → into a namespace class or keep as module utility (lazy.py is infrastructure)
    - `_utilities/lazy.py:46` — `cleanup_submodule_namespace()` → same
    - `_models/container.py:35` — `_is_metadata_instance()` → into `FlextModelsContainer`
    - `_models/container.py:41` — `_normalize_metadata()` → into `FlextModelsContainer`
    - `_models/domain_event.py:26` — `_metadata_to_normalized()` → into `FlextModelsDomainEvent`
    - `_models/domain_event.py:83` — `_normalize_event_data()` → into `FlextModelsDomainEvent`
    - `_models/context.py:35` — `_normalize_to_mapping()` → into `FlextModelsContext`
    - `_models/context.py:50` — `_normalize_metadata_before()` → into `FlextModelsContext`
    - `_models/context.py:64` — `_normalize_statistics_before()` → into `FlextModelsContext`
    - `_models/base.py:38` — `_ensure_utc_datetime()` → into `FlextModelFoundation`
  - Update ALL call sites to use the new class path (use `lsp_find_references`)
  - Verify `@field_validator` and `@model_validator` references still resolve (Pydantic validators often reference module-level functions)

  **Must NOT do**:
  - Move `__getattr__`/`__dir__` from `__init__.py` files (these are expected for lazy loading)
  - Change function behavior — only move location
  - Break Pydantic validator references

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-patterns`, `rules-flext-core`, `flext-architecture-layers`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with T2-T5)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - All 11 files listed above — specific line numbers for each loose function
  - `flext-core/src/flext_core/_models/base.py:38` — `_ensure_utc_datetime` used by Pydantic validators
  - **AGENTS.md §3.1**: "Loose functions outside facade classes are STRICTLY FORBIDDEN"
  - **flext-patterns**: "Absorb into namespace classes as attributes/methods"

  **Acceptance Criteria**:
  - [ ] ast-grep search for module-level `def` (excluding `__init__.py` and `__getattr__`/`__dir__`) → 0 results
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline
  - [ ] `python -m ruff check src/` → clean

  **QA Scenarios**:
  ```
  Scenario: No loose module-level functions remain
    Tool: Bash
    Steps:
      1. sg run --pattern 'def $FUNC($$$): $$$' --lang python --json flext-core/src/flext_core/_models/base.py flext-core/src/flext_core/_models/container.py flext-core/src/flext_core/_models/context.py flext-core/src/flext_core/_models/domain_event.py flext-core/src/flext_core/_utilities/configuration.py flext-core/src/flext_core/_utilities/lazy.py | python -c "import sys,json; data=json.load(sys.stdin); top=[m for m in data if m.get('metaVariables',{}).get('single',{}).get('FUNC',{}).get('start',{}).get('column',99)==0]; print(f'Top-level defs: {len(top)}')"
         (Alternative simpler check): grep -rn "^def [a-z_]" flext-core/src/flext_core/_models/base.py flext-core/src/flext_core/_models/container.py flext-core/src/flext_core/_models/context.py flext-core/src/flext_core/_models/domain_event.py flext-core/src/flext_core/_utilities/configuration.py flext-core/src/flext_core/_utilities/lazy.py
      2. python -c "from flext_core._models.base import FlextModelFoundation; print('OK')"
      3. python -c "from flext_core._models.context import FlextModelsContext; print('OK')"
      4. python -c "from flext_core._models.container import FlextModelsContainer; print('OK')"
      5. python -c "from flext_core._models.domain_event import FlextModelsDomainEvent; print('OK')"
      6. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Step 1: 0 matches for `^def` at column 0 (excluding __init__.py __getattr__/__dir__). Steps 2-6: all pass.
    Failure Indicators: Any `^def [a-z_]` match at column 0 in the listed files means a loose function was not absorbed.
    Evidence: .sisyphus/evidence/task-6-loose-functions.txt
  ```

  **Commit**: YES
  - Message: `refactor(flext-core): absorb loose module-level functions into namespace classes`
  - Files: All 7 affected files
  - Pre-commit: `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q`

- [x] 7. Fix `except Exception` → Specific Exception Types (8 Sites)

  **What to do**:
  - Replace all 8 `except Exception` catches with specific exception types:
    - `container.py:532` — Determine actual exception type (likely `KeyError`/`TypeError`)
    - `container.py:554` — Same pattern
    - `container.py:770` — Same pattern
    - `result.py:393` — Determine exception from result operations
    - `mixins.py:378` — Determine from bootstrap logic
    - `dispatcher.py:271` — Determine from dispatch operations
    - `_utilities/guards.py:1368` — Determine from guard validation
    - `_utilities/result_helpers.py:63` — Determine from result operations
  - For each site: READ the try block, identify what CAN fail, catch THAT specific exception
  - If multiple exception types possible, use `except (TypeError, ValueError) as e:`
  - If genuinely ANY exception possible (infrastructure boundary), use `except BaseException as e:` with comment explaining why

  **Must NOT do**:
  - Use bare `except:` (equally forbidden)
  - Remove try/except without replacing with `r[T]` composition
  - Change behavior — same error handling, just typed

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`flext-patterns`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T8, T9, T10, T11)
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - All 8 files/lines listed above
  - **AGENTS.md §3.3**: "Bare except: is universally forbidden. Catch explicit exceptions."

  **Acceptance Criteria**:
  - [ ] `grep -rn "except Exception" flext-core/src/flext_core/` → 0 results
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline

  **QA Scenarios**:
  ```
  Scenario: Zero broad exception catches
    Tool: Bash
    Steps:
      1. grep -rn "except Exception" flext-core/src/flext_core/
      2. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Step 1: 0 matches. Step 2: passed >= baseline
    Evidence: .sisyphus/evidence/task-7-except-exception.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): replace broad except Exception with specific types`
  - Files: 6 files affected
  - Pre-commit: `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q`

- [x] 8. Fix `r[bool] | None` → `r[bool]` in loggings.py

  **What to do**:
  - Convert 10 `-> r[bool] | None:` return signatures in loggings.py to `-> r[bool]:`
  - For each method: determine what `None` meant:
    - If "not applicable / skipped" → return `r[bool].ok(True)` instead of `None`
    - If "validator not present" → return `r[bool].ok(True)` (no-op success)
  - Update all call sites that check `if result is None:` to use `result.is_success`
  - Use `lsp_find_references` for each method to find call sites

  **Must NOT do**:
  - Change the METHOD body logic — only the return type and None-to-Result conversion
  - Touch protocols.py (separate task T17)
  - Change defensive try/except guards in logging

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-strict-typing`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T7, T9, T10, T11)
  - **Blocks**: T17
  - **Blocked By**: T1

  **References**:
  - `flext-core/src/flext_core/loggings.py` — lines 811, 836, 861, 886, 952, 1006, 1050, 1065, 1080, 1119
  - **AGENTS.md §3.3**: "r[T] IS the fallibility mechanism; | None on top is redundant"

  **Acceptance Criteria**:
  - [ ] `grep -rn "r\[bool\] | None" flext-core/src/flext_core/loggings.py` → 0 results
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline

  **QA Scenarios**:
  ```
  Scenario: Zero r[bool] | None in loggings
    Tool: Bash
    Steps:
      1. grep -rn "r\[bool\] | None" flext-core/src/flext_core/loggings.py
      2. python -c "from flext_core.loggings import FlextLogger; print('OK')"
      3. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Step 1: 0 matches. Steps 2-3: pass
    Evidence: .sisyphus/evidence/task-8-result-none.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): convert r[bool] | None to r[bool] in loggings`
  - Files: `loggings.py`

- [x] 9. Audit + Classify getattr (186 Calls)

  **What to do**:
  - Read EVERY `getattr()` call site across all 36 files (186 total)
  - Classify each into one of 3 categories:
    - **LEGITIMATE**: 3-arg defensive access `getattr(obj, attr, default)`, Pydantic introspection, dunder access, Protocol attribute discovery. Mark as NO_ACTION.
    - **VIOLATION**: Architectural dynamic dispatch that should use typed protocols/contracts. Mark for fix in T12.
    - **DEFERRED**: In FROZEN files (context.py, settings.py). Document but don't fix.
  - Produce a triage matrix as `.sisyphus/evidence/task-9-getattr-triage.md`
  - Focus areas with highest violation probability: `mixins.py` (10 calls), `handlers.py` (8 calls), `_utilities/configuration.py` (12 calls)

  **Must NOT do**:
  - Fix any violations (that's T12)
  - Change any files
  - Touch FROZEN files

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-patterns`, `flext-architecture-layers`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T7, T8, T10, T11)
  - **Blocks**: T12
  - **Blocked By**: T1

  **References**:
  - All 36 files with getattr calls (see draft for full list)
  - **AGENTS.md §3.4**: "getattr() for architecture or dynamic logic are PROHIBITED"
  - **AGENTS.md §10.2**: FROZEN files list

  **Acceptance Criteria**:
  - [ ] `.sisyphus/evidence/task-9-getattr-triage.md` exists with all 186 calls classified
  - [ ] Each call tagged as LEGITIMATE, VIOLATION, or DEFERRED with justification

  **QA Scenarios**:
  ```
  Scenario: Triage matrix complete
    Tool: Bash
    Steps:
      1. wc -l .sisyphus/evidence/task-9-getattr-triage.md
      2. grep -c "LEGITIMATE\|VIOLATION\|DEFERRED" .sisyphus/evidence/task-9-getattr-triage.md
    Expected Result: File has 186+ classified entries
    Evidence: .sisyphus/evidence/task-9-getattr-triage.md
  ```

  **Commit**: NO (audit only, no code changes)

- [x] 10. Audit + Classify setattr (52 Calls)

  **What to do**:
  - Read EVERY `setattr()` call site across all 13 files (52 total)
  - **PRE-EXCLUDE** (known legitimate):
    - `container.py` (14 calls) — DI wiring mechanism. LEGITIMATE.
    - `result.py` (12 calls) — Result `__slots__` bypass. LEGITIMATE.
  - Classify remaining ~26 calls as LEGITIMATE / VIOLATION / DEFERRED
  - Produce triage matrix as `.sisyphus/evidence/task-10-setattr-triage.md`

  **Must NOT do**:
  - Fix any violations (that's T13)
  - Change any files

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-patterns`, `flext-architecture-layers`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T7, T8, T9, T11)
  - **Blocks**: T13
  - **Blocked By**: T1

  **References**:
  - All 13 files with setattr calls
  - `container.py` (14 calls) — DI mechanism, PRE-EXCLUDED as LEGITIMATE
  - `result.py` (12 calls) — __slots__ bypass, PRE-EXCLUDED as LEGITIMATE
  - **AGENTS.md §3.4**: "setattr() for architecture or dynamic logic are PROHIBITED"

  **Acceptance Criteria**:
  - [ ] `.sisyphus/evidence/task-10-setattr-triage.md` exists with all 52 calls classified

  **QA Scenarios**:
  ```
  Scenario: Triage matrix complete
    Tool: Bash
    Steps:
      1. grep -c "LEGITIMATE\|VIOLATION\|DEFERRED" .sisyphus/evidence/task-10-setattr-triage.md
    Expected Result: 52 classified entries
    Evidence: .sisyphus/evidence/task-10-setattr-triage.md
  ```

  **Commit**: NO (audit only)

- [x] 11. Audit + Classify try/except (192 Blocks)

  **What to do**:
  - Read EVERY `try:` block across all 34 files (192 total)
  - Classify each into:
    - **INFRASTRUCTURE_GUARD**: Logging, cleanup, context propagation, import fallback. LEGITIMATE — fire-and-forget semantics require try/except. NO_ACTION.
    - **BUSINESS_LOGIC**: Domain operations that should use `r[T]` composition. Mark for fix in T14.
    - **DEFERRED**: In FROZEN files. Document but don't fix.
  - **PRE-EXCLUDE** as INFRASTRUCTURE_GUARD:
    - `loggings.py` (19 blocks) — logging must never crash
    - `__version__.py` (1 block) — FROZEN file
    - `protocols.py` (6 blocks) — Protocol introspection infrastructure
  - Focus areas: `_utilities/collection.py` (18 blocks), `decorators.py` (7), `result.py` (7)
  - Produce triage matrix as `.sisyphus/evidence/task-11-try-except-triage.md`

  **Must NOT do**:
  - Fix any violations (that's T14)
  - Change any files
  - Remove defensive guards from infrastructure code

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-patterns`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with T7-T10)
  - **Blocks**: T14
  - **Blocked By**: T1

  **References**:
  - All 34 files with try blocks
  - **AGENTS.md §3.3**: "Bare try/except in business logic is FORBIDDEN when r composition can handle the flow"
  - **Metis analysis**: Logging/context/container try/except are defensive guards

  **Acceptance Criteria**:
  - [ ] `.sisyphus/evidence/task-11-try-except-triage.md` exists with all 192 blocks classified

  **QA Scenarios**:
  ```
  Scenario: Triage matrix complete
    Tool: Bash
    Steps:
      1. grep -c "INFRASTRUCTURE_GUARD\|BUSINESS_LOGIC\|DEFERRED" .sisyphus/evidence/task-11-try-except-triage.md
    Expected Result: 192 classified entries
    Evidence: .sisyphus/evidence/task-11-try-except-triage.md
  ```

  **Commit**: NO (audit only)

- [ ] 12. Fix getattr Violations (from Audit T9)

  **What to do**:
  - Read triage matrix from `.sisyphus/evidence/task-9-getattr-triage.md`
  - Fix ALL items classified as VIOLATION:
    - Replace `getattr(obj, "method", None)` with `isinstance(obj, p.SomeProtocol)` + typed access
    - Replace `getattr(obj, attr)` dynamic dispatch with typed protocol method calls
    - Replace attribute duck-typing with `p.*` protocol checks
  - Use `lsp_find_references` for each changed call site
  - Skip LEGITIMATE and DEFERRED items

  **Must NOT do**:
  - Fix items classified as LEGITIMATE or DEFERRED
  - Change container.py or result.py getattr (PRE-EXCLUDED)
  - Touch FROZEN files

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with T13, T14, T15, T16)
  - **Blocks**: T19
  - **Blocked By**: T9

  **References**:
  - `.sisyphus/evidence/task-9-getattr-triage.md` — triage matrix (source of truth)
  - `flext-core/src/flext_core/protocols.py` — available protocol contracts for replacement

  **Acceptance Criteria**:
  - [ ] ALL VIOLATION items from triage matrix are fixed
  - [ ] `python -m pytest tests/ --ignore=tests/infra --tb=no -q` → passed >= baseline
  - [ ] `python -m ruff check src/` → clean

  **QA Scenarios**:
  ```
  Scenario: All getattr violations fixed — count-based verification
    Tool: Bash
    Steps:
      1. VIOLATION_COUNT=$(grep -c "VIOLATION" .sisyphus/evidence/task-9-getattr-triage.md)
      2. echo "Total VIOLATION items to fix: $VIOLATION_COUNT"
      3. For each VIOLATION entry in triage matrix: extract file:line, then grep that line in the current file to confirm getattr is gone:
         grep -c "getattr" <file> at <line> should be 0 for each VIOLATION site
         (Concrete: while read file line; do sed -n "${line}p" "$file" | grep -c "getattr"; done < <(grep "VIOLATION" .sisyphus/evidence/task-9-getattr-triage.md | awk '{print $1, $2}'))
      4. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
      5. python -m ruff check src/
    Expected Result: Step 3: 0 getattr remaining at each VIOLATION line. Step 4: passed >= 3197. Step 5: clean.
    Failure Indicators: Any VIOLATION line still containing getattr, or test failures beyond baseline 4.
    Evidence: .sisyphus/evidence/task-12-getattr-fixes.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): replace getattr violations with typed protocol access`

- [x] 13. Fix setattr Violations (from Audit T10)

  **What to do**:
  - Read triage matrix from `.sisyphus/evidence/task-10-setattr-triage.md`
  - Fix ALL items classified as VIOLATION
  - Skip LEGITIMATE (container.py, result.py) and DEFERRED items

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T19
  - **Blocked By**: T10

  **References**:
  - `.sisyphus/evidence/task-10-setattr-triage.md` — triage matrix

  **Acceptance Criteria**:
  - [ ] ALL VIOLATION items from triage matrix fixed
  - [ ] Tests pass >= baseline

  **QA Scenarios**:
  ```
  Scenario: All setattr violations fixed — count-based verification
    Tool: Bash
    Steps:
      1. VIOLATION_COUNT=$(grep -c "VIOLATION" .sisyphus/evidence/task-10-setattr-triage.md)
      2. echo "Total VIOLATION items to fix: $VIOLATION_COUNT"
      3. For each VIOLATION entry in triage matrix: extract file:line, then verify setattr is removed at that line:
         grep -c "setattr" <file> at <line> should be 0 for each VIOLATION site
         (Concrete: while read file line; do sed -n "${line}p" "$file" | grep -c "setattr"; done < <(grep "VIOLATION" .sisyphus/evidence/task-10-setattr-triage.md | awk '{print $1, $2}'))
      4. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
      5. python -m ruff check src/
    Expected Result: Step 3: 0 setattr remaining at each VIOLATION line. Step 4: passed >= 3197. Step 5: clean.
    Failure Indicators: Any VIOLATION line still containing setattr, or test failures beyond baseline 4.
    Evidence: .sisyphus/evidence/task-13-setattr-fixes.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): replace setattr violations with typed mechanisms`

- [ ] 14. Fix try/except Business Logic Violations (from Audit T11)

  **What to do**:
  - Read triage matrix from `.sisyphus/evidence/task-11-try-except-triage.md`
  - Fix ALL items classified as BUSINESS_LOGIC:
    - Convert imperative `try/except` to `r[T]` railway composition using `map/flat_map/lash`
    - Replace `try: x = fn() except: return None` with `r[T].ok(fn()).lash(lambda e: r.fail(str(e)))`
  - Skip INFRASTRUCTURE_GUARD and DEFERRED items
  - Each conversion MUST preserve error handling behavior

  **Must NOT do**:
  - Remove infrastructure guards (logging, cleanup, context)
  - Remove try/except from FROZEN files
  - Change error recovery behavior

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T19
  - **Blocked By**: T11

  **References**:
  - `.sisyphus/evidence/task-11-try-except-triage.md` — triage matrix
  - **AGENTS.md §3.3**: "r composition must replace try/except in business logic"
  - `flext-core/src/flext_core/result.py` — `r[T].ok()`, `.map()`, `.flat_map()`, `.lash()` patterns

  **Acceptance Criteria**:
  - [ ] ALL BUSINESS_LOGIC items from triage matrix converted to `r[T]` composition
  - [ ] Tests pass >= baseline

  **QA Scenarios**:
  ```
  Scenario: Business logic try/except converted
    Tool: Bash
    Steps:
      1. Count remaining try blocks: grep -rn "try:" flext-core/src/flext_core/ | wc -l
      2. Verify count matches (original 192 - BUSINESS_LOGIC fixes)
      3. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Reduced try count; tests pass
    Evidence: .sisyphus/evidence/task-14-try-except-fixes.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): convert business logic try/except to r[T] railway composition`

- [ ] 15. Convert T|None Fallible Returns → r[T] in Non-Protocol Files

  **What to do**:
  - Find ALL functions with `-> T | None` return types that represent FALLIBILITY (not business optionality)
  - Triage each of the ~42 return-type sites:
    - `exceptions.py` (7): `_safe_int() -> int | None`, `_safe_number()`, etc. — CONVERT
    - `loggings.py` (4): `_extract_class_name() -> str | None`, `_find_workspace_root()` — CONVERT
    - `context.py` (4): `get_correlation_id() -> str | None` — DEFERRED (FROZEN file)
    - `registry.py` (2): `-> t.Container | BaseModel | None` — CONVERT
    - `service.py` (2): `-> p.RuntimeBootstrapOptions | None` — EVALUATE semantics
    - `dispatcher.py` (3): Complex return types with `| None` — CONVERT
    - `settings.py` (2): DEFERRED (FROZEN file)
    - `handlers.py` (2): `-> t.Scalar | None` — CONVERT
    - Other scattered sites — evaluate individually
  - For each CONVERT site: change return type to `r[T]`, update `return None` to `return r.fail("reason")`, update call sites
  - Use `lsp_find_references` BEFORE each signature change

  **Must NOT do**:
  - Change FROZEN files (context.py, settings.py)
  - Convert parameter `| None` (these mean "optional argument", not fallibility)
  - Convert field `| None` annotations (these are model definitions)
  - Change protocol signatures (that's T17/T18)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-patterns`, `rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with T12-T14, T16)
  - **Blocks**: T18
  - **Blocked By**: T1

  **References**:
  - All files with `-> T | None` returns (see draft for full list with line numbers)
  - **AGENTS.md §3.3**: "r[T] is MANDATORY for fallible operations; T | None is FORBIDDEN"
  - **Metis analysis**: Only RETURN types in scope, not parameters or fields

  **Acceptance Criteria**:
  - [ ] All non-FROZEN, non-protocol fallible returns converted to `r[T]`
  - [ ] Tests pass >= baseline
  - [ ] Call sites updated to use `.is_success` / `.value` instead of `is None`

  **QA Scenarios**:
  ```
  Scenario: Fallible returns converted
    Tool: Bash
    Steps:
      1. grep -rn "-> .*| None" flext-core/src/flext_core/ | grep -v "context.py\|settings.py\|protocols.py\|__init__\|#" | wc -l
      2. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Reduced None-return count; tests pass
    Evidence: .sisyphus/evidence/task-15-tnone-returns.txt
  ```

  **Commit**: YES (1 commit per file group)
  - Message: `fix(flext-core): convert fallible T|None returns to r[T]`

- [ ] 16. Fix Classes Without MRO Lineage

  **What to do**:
  - Evaluate 6 classes without Pydantic/FLEXT base inheritance:
    - `_dispatcher/timeout.py:20` — `TimeoutEnforcer` → If stateful: make BaseModel-based. If namespace-only: document as exception.
    - `_dispatcher/reliability.py:22` — `CircuitBreakerManager` → Same evaluation
    - `_dispatcher/reliability.py:233` — `RateLimiterManager` → Same
    - `_dispatcher/reliability.py:311` — `RetryPolicy` → Same
    - `_decorators/discovery.py:18` — `FactoryDecoratorsDiscovery` → Namespace-only — likely exception
    - `_utilities/result_helpers.py:14` — `ResultHelpers` → Namespace-only — likely exception
  - For stateful classes: convert to Pydantic BaseModel, replace `__init__` with `Field()` declarations
  - For namespace-only classes: add comment documenting why no base class

  **Must NOT do**:
  - Break existing instantiation patterns
  - Add unnecessary Pydantic overhead to pure namespace classes

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: [`flext-patterns`, `flext-strict-typing`]

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3
  - **Blocks**: T19
  - **Blocked By**: T1

  **References**:
  - All 4 files listed above
  - **AGENTS.md §3.1**: "Every class MUST extend Pydantic v2 BaseModel or FLEXT base models via MRO"
  - **Note**: "Namespace classes that only organize nested types" are acceptable exceptions

  **Acceptance Criteria**:
  - [ ] Stateful classes converted to Pydantic BaseModel
  - [ ] Namespace-only classes documented with rationale comment
  - [ ] Tests pass >= baseline

  **QA Scenarios**:
  ```
  Scenario: MRO lineage verified
    Tool: Bash
    Steps:
      1. python -c "from flext_core._dispatcher.reliability import CircuitBreakerManager; print(CircuitBreakerManager.__mro__)"
      2. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: MRO includes proper base classes; tests pass
    Evidence: .sisyphus/evidence/task-16-mro-lineage.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): add proper MRO lineage to stateful classes`

- [ ] 17. Fix `r[bool] | None` in protocols.py + Downstream Audit

  **What to do**:
  - Convert 6 `-> r[bool] | None:` in `protocols.py` (lines 1100-1145) to `-> r[bool]:`
  - **BEFORE changing**: Use `lsp_find_references` for EACH protocol method to find ALL implementations across 29 downstream projects
  - List all downstream files that implement these protocol methods
  - Update protocol signatures
  - **NOTE**: Downstream implementations may need updating — document them but don't fix (scope is flext-core only)

  **Must NOT do**:
  - Change protocols.py section ownership (respect §10.2 agent matrix)
  - Fix downstream consumers (out of scope)
  - Change lines 1-236 or 1289+ (FROZEN behavioral region)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-patterns`, `flext-architecture-layers`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (sequential — protocol changes cascade)
  - **Blocks**: T18, T19
  - **Blocked By**: T8

  **References**:
  - `flext-core/src/flext_core/protocols.py:1100-1145` — 6 `r[bool] | None` methods
  - **AGENTS.md §10.2**: protocols.py section ownership matrix
  - **Metis analysis**: Protocol changes cascade to 29 downstream projects

  **Acceptance Criteria**:
  - [ ] `grep -rn "r\[bool\] | None" flext-core/src/flext_core/protocols.py` → 0 results
  - [ ] Downstream impact list documented in `.sisyphus/evidence/task-17-downstream-impact.md`
  - [ ] Tests pass >= baseline

  **QA Scenarios**:
  ```
  Scenario: Protocol signatures fixed + downstream documented
    Tool: Bash
    Steps:
      1. grep -rn "r\[bool\] | None" flext-core/src/flext_core/protocols.py
      2. wc -l .sisyphus/evidence/task-17-downstream-impact.md
      3. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Step 1: 0 matches. Step 2: impact list exists. Step 3: tests pass.
    Evidence: .sisyphus/evidence/task-17-protocol-fix.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): convert r[bool] | None protocol signatures to r[bool]`
  - Files: `protocols.py`

- [ ] 18. Convert T|None Returns → r[T] in Protocol-Adjacent Files

  **What to do**:
  - After T17 protocol changes, update any implementation files in flext-core that implement the changed protocols
  - Update loggings.py implementations if T8 didn't already cover them
  - Ensure all protocol implementations match the new `r[bool]` signatures

  **Must NOT do**:
  - Fix downstream project implementations (out of scope)
  - Change non-protocol-related return types (that's T15)

  **Recommended Agent Profile**:
  - **Category**: `deep`
  - **Skills**: [`flext-strict-typing`, `flext-patterns`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on T15 + T17)
  - **Blocks**: T19
  - **Blocked By**: T15, T17

  **Acceptance Criteria**:
  - [ ] All protocol implementations in flext-core match updated signatures
  - [ ] `grep -rn "r\[bool\] | None" flext-core/src/flext_core/ | grep -v protocols.py` → 0 results (protocols already fixed in T17)
  - [ ] Tests pass >= baseline

  **QA Scenarios**:
  ```
  Scenario: Protocol implementations aligned with r[bool] signatures
    Tool: Bash
    Steps:
      1. grep -rn "r\[bool\] | None" flext-core/src/flext_core/ | grep -v "protocols.py"
      2. python -c "from flext_core.loggings import FlextLogger; print('OK')"
      3. python -c "from flext_core.mixins import FlextMixins; print('OK')"
      4. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
    Expected Result: Step 1: 0 matches. Steps 2-3: OK. Step 4: passed >= 3197, failed <= 4
    Evidence: .sisyphus/evidence/task-18-protocol-impl.txt

  Scenario: No r[bool] | None remains anywhere
    Tool: Bash
    Steps:
      1. grep -rn "r\[bool\] | None" flext-core/src/flext_core/
    Expected Result: 0 matches across entire flext-core
    Evidence: .sisyphus/evidence/task-18-zero-result-none.txt
  ```

  **Commit**: YES
  - Message: `fix(flext-core): align protocol implementations with updated r[bool] signatures`

- [ ] 19. Final Grep Verification + Evidence Collection

  **What to do**:
  - Run ALL verification grep commands from Success Criteria section
  - Run full test suite
  - Run ruff check
  - Run import smoke test
  - Collect all results into `.sisyphus/evidence/task-19-final-verification.txt`
  - Verify ALL "Must Have" deliverables are present
  - Verify ALL "Must NOT Have" guardrails are respected

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: [`rules-flext-core`]

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all previous tasks)
  - **Blocks**: F1-F4
  - **Blocked By**: T2-T18

  **Acceptance Criteria**:
  - [ ] All grep checks pass (0 violations)
  - [ ] Test suite: passed >= 3197, failed <= 4
  - [ ] Ruff: clean
  - [ ] Import smoke: all 16+ entries load
  - [ ] Evidence file complete

  **QA Scenarios**:
  ```
  Scenario: Full verification pass
    Tool: Bash
    Steps:
      1. grep -rn "model_rebuild" flext-core/src/flext_core/ | grep -v "#" → 0
      2. grep -rn "type(.*) is type(" flext-core/src/flext_core/ → 0
      3. grep -rn "TypeAlias" flext-core/src/flext_core/ | grep -v "#\|TypeAliasType" → 0
      4. grep -rn "r\[bool\] | None" flext-core/src/flext_core/ → 0
      5. grep -rn "except Exception" flext-core/src/flext_core/ → 0
      6. python -m ruff check src/ → clean
      7. python -m pytest tests/ --ignore=tests/infra --tb=no -q → pass
      8. python -c "from flext_core import r, t, c, m, p, u, FlextModels, FlextProtocols" → OK
    Expected Result: ALL checks pass
    Evidence: .sisyphus/evidence/task-19-final-verification.txt
  ```

  **Commit**: YES
  - Message: `chore(flext-core): collect final verification evidence`

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> 4 review agents run in PARALLEL. ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`

  **What to do**: Read the plan end-to-end. For each "Must Have": verify implementation exists. For each "Must NOT Have": search codebase for forbidden patterns. Check evidence files exist. Compare deliverables against plan.

  **QA Scenarios**:
  ```
  Scenario: Must Have verification
    Tool: Bash
    Steps:
      1. grep -rn "model_rebuild" flext-core/src/flext_core/ | grep -v "#" | wc -l  → must be 0
      2. grep -rn "type(.*) is type(" flext-core/src/flext_core/ | wc -l  → must be 0
      3. grep -rn "TypeAlias" flext-core/src/flext_core/ | grep -v "#\|TypeAliasType" | wc -l  → must be 0
      4. grep -rn "r\[bool\] | None" flext-core/src/flext_core/ | wc -l  → must be 0
      5. grep -rn "except Exception" flext-core/src/flext_core/ | wc -l  → must be 0
      6. ls .sisyphus/evidence/task-9-getattr-triage.md .sisyphus/evidence/task-10-setattr-triage.md .sisyphus/evidence/task-11-try-except-triage.md  → all exist
      7. ls .sisyphus/evidence/task-17-downstream-impact.md  → exists
    Expected Result: Steps 1-5: all 0. Steps 6-7: all files exist.
    Evidence: .sisyphus/evidence/F1-compliance-audit.txt

  Scenario: Must NOT Have verification
    Tool: Bash
    Steps:
      1. git diff --name-only HEAD~20 | grep -E "context\.py|settings\.py|models\.py|utilities\.py|__version__\.py" | while read f; do git diff HEAD~20 -- "$f" | head -50; done
      2. Verify no behavioral changes in FROZEN files (annotation-only acceptable)
    Expected Result: No behavioral diff in FROZEN files.
    Evidence: .sisyphus/evidence/F1-frozen-check.txt
  ```
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`

  **What to do**: Run lint + tests. Review changed files for code quality issues.

  **QA Scenarios**:
  ```
  Scenario: Lint and test gates pass
    Tool: Bash
    Steps:
      1. cd flext-core && python -m ruff check src/ 2>&1 | tee /tmp/f2-lint.txt
      2. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q 2>&1 | tee /tmp/f2-tests.txt
      3. grep -rn "# type: ignore\|# noqa\|# pyright: ignore" flext-core/src/flext_core/ | grep -v "justified" | wc -l
      4. grep -rn "print(" flext-core/src/flext_core/ | grep -v "docstring\|#\|\.\.\." | wc -l
    Expected Result: Step 1: "All checks passed!". Step 2: passed >= 3197, failed <= 4. Steps 3-4: 0 unjustified.
    Evidence: .sisyphus/evidence/F2-quality-review.txt
  ```
  Output: `Lint [PASS/FAIL] | Tests [N pass/N fail] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real QA — Full Test + Import Smoke** — `unspecified-high`

  **What to do**: From clean state, run full import smoke test + test suite + grep checks.

  **QA Scenarios**:
  ```
  Scenario: Full import smoke test
    Tool: Bash
    Steps:
      1. python -c "
from flext_core import FlextModels, FlextConstants, FlextTypes
from flext_core import FlextUtilities, FlextProtocols, FlextContainer
from flext_core import FlextDispatcher, FlextRegistry, FlextService
from flext_core import FlextContext, FlextLogger, FlextSettings
from flext_core import FlextExceptions, FlextRuntime
from flext_core import r, t, c, m, p, u
print('ALL 16 IMPORTS OK')
"
      2. cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q 2>&1 | tail -1
      3. grep -rn "model_rebuild\|except Exception" flext-core/src/flext_core/ | grep -v "#" | wc -l
    Expected Result: Step 1: "ALL 16 IMPORTS OK". Step 2: passed >= 3197. Step 3: 0.
    Evidence: .sisyphus/evidence/F3-qa-smoke.txt
  ```
  Output: `Import Smoke [PASS/FAIL] | Tests [N/N] | Grep Checks [N/N] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`

  **What to do**: Verify all changes match plan spec 1:1. No scope creep, no missing items.

  **QA Scenarios**:
  ```
  Scenario: Scope fidelity — no FROZEN file behavioral changes
    Tool: Bash
    Steps:
      1. git log --oneline -30 | head -25  (review commit history)
      2. git diff --stat HEAD~30 -- flext-core/src/flext_core/context.py flext-core/src/flext_core/settings.py flext-core/src/flext_core/models.py flext-core/src/flext_core/utilities.py flext-core/src/flext_core/__version__.py
      3. For each changed FROZEN file: git diff HEAD~30 -- <file> | grep "^[+-]" | grep -v "^[+-][+-][+-]\|^[+-]#\|^[+-]$\|import\|Field(\|: " | wc -l
    Expected Result: Step 2: 0 behavioral changes in FROZEN files (annotation additions acceptable). Step 3: 0 non-annotation lines changed.
    Failure Indicators: Any FROZEN file showing behavioral (non-annotation) diff lines.
    Evidence: .sisyphus/evidence/F4-scope-fidelity.txt

  Scenario: No unaccounted file changes
    Tool: Bash
    Steps:
      1. git diff --name-only HEAD~30 -- flext-core/src/flext_core/ | sort > /tmp/changed.txt
      2. Compare against expected file list from plan tasks
    Expected Result: All changed files traceable to a specific task.
    Evidence: .sisyphus/evidence/F4-file-accounting.txt
  ```
  Output: `Tasks [N/N compliant] | FROZEN [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

| Wave | Commit Pattern | Pre-commit Check |
|------|----------------|------------------|
| 1 | 1 commit per file changed | `python -m ruff check src/ && python -m pytest tests/ --ignore=tests/infra --tb=no -q` |
| 2 | 1 commit per violation group | Same |
| 3 | 1 commit per logical audit batch | Same |
| 4 | 1 commit per protocol change | Same + downstream import check |
| FINAL | 1 commit for evidence collection | N/A |

---

## Success Criteria

### Verification Commands
```bash
# Zero model_rebuild
grep -rn "model_rebuild" flext-core/src/flext_core/ | grep -v "^.*:#"
# Expected: 0 results

# Zero type() narrowing
grep -rn "type(.*) is type(" flext-core/src/flext_core/
# Expected: 0 results

# Zero deprecated TypeAlias
grep -rn "TypeAlias" flext-core/src/flext_core/ | grep -v "^.*:#" | grep -v "TypeAliasType"
# Expected: 0 results

# Zero r[bool] | None
grep -rn "r\[bool\] | None" flext-core/src/flext_core/
# Expected: 0 results

# Zero except Exception
grep -rn "except Exception" flext-core/src/flext_core/
# Expected: 0 results

# Zero loose module-level functions (excl __init__.py)
# Verified via ast-grep structural check

# Full test suite
cd flext-core && python -m pytest tests/ --ignore=tests/infra --tb=no -q
# Expected: passed >= 3197, failed <= 4

# Lint clean
cd flext-core && python -m ruff check src/
# Expected: "All checks passed!"

# Import smoke
python -c "from flext_core import r, t, c, m, p, u, FlextModels, FlextProtocols, FlextContainer, FlextDispatcher"
# Expected: no errors
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All tests pass (>= baseline)
- [ ] Lint clean
- [ ] Evidence stored in `.sisyphus/evidence/`
- [ ] Triage matrix documented for getattr/setattr/try-except
