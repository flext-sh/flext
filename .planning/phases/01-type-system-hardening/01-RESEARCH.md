# Phase 1: Type System Hardening — Research

**Researched:** 2026-03-23
**Domain:** Python static typing, pyrefly/pyright remediation, ast-grep structural rewrites, Pydantic v2 type contracts
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Phase 1 is organized as big wave plans, not per-project or per-error-category. Wave order: `flext-core` → `flext-infra + flext-tests` → `flext-cli (solo)` → remaining consumers.
- **D-02:** Each wave plan covers ALL error categories for that batch in a single pass: pyrefly errors, pyright errors, and any applicable TYPE-0X requirements (no separate `__class__` pass, no separate `cast()` pass).
- **D-03:** Researchers and planners MUST read the existing `.sisyphus` plans as reference input — they contain baseline counts, wave analyses, and proven ast-grep rewrite rules. Do not re-derive what's already documented there.
- **D-04:** flext-cli gets a **dedicated solo plan** between the `flext-infra+tests` wave and the remaining consumers wave. Rationale: largest consumer by error count; placing it after infra ensures the dependency foundation is clean before tackling the largest consumer.
- **D-05:** Phase 1 success requires **both** `make pyre` AND `make check CHECK_GATES=pyright` returning 0 errors/warnings. The `pyright-zero-errors.md` sisyphus plan is in scope for Phase 1. Each wave plan must pass both tools before the wave is considered done.
- **D-06:** TYPE-07 (12 TypeGuard functions → TypeIs, PEP 742) and TYPE-08 (annotated empty container literals) are handled in a **separate final micro-plan** after the main waves complete. Main waves focus on the error mass; the micro-plan sweeps these targeted items across all projects at once.
- **D-07:** `make pyre` is currently broken: `${PWD}` variable in `pyproject.toml` `[tool.pyrefly] search-path` is not being expanded by pyrefly. **The first task of Wave 1 (flext-core plan) must fix this entrypoint before any type error measurement can be authoritative.** Fix approach: replace `${PWD}/flext-core/src` literals with project-relative paths or absolute paths that pyrefly can resolve.
- **D-08:** The historical 4,385 figure is from pre-Wave 0 sisyphus analysis. A fresh baseline must be established as Wave 1's first action (after fixing `make pyre`). The planner should include a "baseline measurement" task at the start of each wave plan.

### Claude's Discretion

- Within each wave plan, the sequencing of individual projects is at Claude's discretion (as long as dependency order is respected: flext-core before infra, infra before consumers).
- The exact boundary between "small consumers" and "remaining consumers" within the final wave can be determined by the planner based on error counts and project dependencies.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TYPE-01 | Repo-wide `make pyre` returns exit code 0 with 0 errors | D-07/D-08 fix `make pyre` entrypoint first; pyrefly-repo-hardening.md provides the full wave strategy |
| TYPE-02 | Zero `# type: ignore` annotations in any `.py` file across all 33 projects | Wave 3 of pyrefly-repo-hardening.md; policy gate `make pol` |
| TYPE-03 | Zero `typing.Any` imports or annotations across all 33 projects | bare-object-elimination.md + Wave 3 of pyrefly-repo-hardening.md; `make pol` enforces |
| TYPE-04 | Zero `object` used as a type annotation across all 33 projects | bare-object-elimination.md 7-wave strategy; new `t.*` aliases required |
| TYPE-05 | Zero `cast()` calls outside `flext-core/result.py` | strict-typing-execution-plan.md Wave 1.2; 15 violations mapped to concrete replacements |
| TYPE-06 | Zero `__class__ is/not in` comparisons | strict-typing-execution-plan.md Wave 1.0–1.1; 65 violations with ast-grep rules A1–A4 ready |
| TYPE-07 | `TypeGuard` → `TypeIs` migration in all 12 type-guard functions | Final micro-plan (D-06); 12 functions identified across `_utilities/guards.py` |
| TYPE-08 | All empty container literals annotated at their assignment sites | Final micro-plan (D-06); `implicit-any` error class in pyrefly |
</phase_requirements>

---

## Summary

Phase 1 is a pure type-system cleanup with no architecture changes. The monorepo carries an estimated 4,000+ pyrefly errors and ~2,098 pyright issues accumulated from technical debt. Both toolchains must reach zero before Phase 1 is complete. The work is structured as four wave plans plus a final micro-plan, sequenced by the hard dependency order: `flext-core` (foundation) → `flext-infra + flext-tests` (infrastructure) → `flext-cli` (largest consumer, solo) → remaining 27 projects → TYPE-07/TYPE-08 micro-sweep.

**Critical blocker:** `make pyre` currently exits non-zero because pyrefly cannot resolve the `search-path` entries in `[tool.pyrefly]`. Inspection of `pyproject.toml` lines 127–174 confirms the paths are already expressed as project-relative strings (e.g., `"flext-core/src"`) — no `${PWD}` tokens present in the committed config. However per CONTEXT.md D-07, the entrypoint is still failing. Wave 1 must begin by diagnosing and fixing this before any error count is authoritative. The authoritative make target is `make pyre` (not `make pyrefly-repo` — that label was used in the sisyphus plan; the actual Makefile target is `pyre`).

**Policy gate** (`make pol`) already exists and enforces zero `Any`, zero `t.NormalizedValue`, zero `# type: ignore`. This gate is the evidence artifact for TYPE-02/TYPE-03 acceptance.

**Primary recommendation:** Fix the `make pyre` entrypoint as task 0 of Wave 1, capture a fresh baseline, then execute the four-wave plan in strict dependency order with both `make pyre` and `make check CHECK_GATES=pyright` as the exit criteria for each wave.

---

## Project Constraints (from CLAUDE.md)

- **Tooling**: All changes via `make` targets, `ast-grep`, native tools — NEVER direct `grep`/`find`/`sed`
- **Typing**: No `Any`, no `object` annotations, no `cast()`, no `# type: ignore` — zero exceptions
- **Freeze policy**: `flext-core/_utilities/*` FROZEN per AGENTS.md §10.2 — **operator unfreeze ALREADY AUTHORIZED (2026-03-12)** for `__class__` + `cast()` fixes
- **Autogenerated files**: `__init__.py` exports are autogenerated — fix generators, never hand-edit; run `make gen` after touching exports
- **Commit protocol**: Stage → commit → push before ending each session
- **Dependency order**: flext-core → flext-infra → flext-tests → consumers (hard constraint — type changes cascade)
- **`algar-oud-mig`**: EXCLUDED from all waves — do not touch

---

## Standard Stack

### Core Tooling

| Tool | Make Target | Purpose | Authoritative For |
|------|-------------|---------|-------------------|
| pyrefly | `make pyre` | Repo-wide type check, JSON + summary report | TYPE-01 (exit code gate) |
| pyright | `make check CHECK_GATES=pyright` | Per-project pyright gate | D-05 (wave exit gate) |
| ruff | `make check CHECK_GATES=lint` | Linter / formatter | Pre-commit correctness |
| policy gate | `make pol` | Zero Any/t.NormalizedValue/type: ignore | TYPE-02, TYPE-03 |
| ast-grep (`sg`) | direct CLI | Structural find/replace for mechanical rewrites | TYPE-05, TYPE-06 rewrites |
| `make check` | combined | All gates in one pass | Per-task verification |
| `make test` | per-project | Non-regression after type changes | Behavioral safety |

### Supporting Libraries / Patterns

| Library / Pattern | Version | Purpose | Why Standard |
|-------------------|---------|---------|--------------|
| `t.*` contracts | flext-core typings.py | Replace `Any`/`object` annotations | Monorepo-standard; 290+ constraints already deployed |
| `u.Guards.is_*()` | flext-core utilities | TypeGuard replacements for `__class__` narrowing | 56 functions already exist, verified |
| `r[T]` (returns) | flext-core result.py | Fallible return types | AXIOMATIC — sole fallibility mechanism |
| Pydantic v2 `model_dump_json()` / `model_validate_json()` | pydantic 2.12+ | Replace `json.loads`/`json.dumps` | TYPE-03/TYPE-04 impact |
| `TypeIs` (PEP 742) | typing 3.13 | Replace `TypeGuard` where narrowing is bidirectional | TYPE-07 requirement |
| `t.PRIMITIVES_TYPES`, `t.SCALAR_TYPES` | flext-core | Runtime isinstance tuples (NOT PEP 695 aliases) | TYPE-06 fix for alias misuse |

---

## Architecture Patterns

### Wave Plan Structure

Each wave plan is a GSD plan file that covers ALL error categories for the given project batch in a single pass:

```
Wave 1 (Plan 1):  flext-core only
  Task 0: Fix make pyre entrypoint + capture fresh baseline
  Task 1: pyrefly errors — all categories
  Task 2: pyright errors — _operation_stats PrivateAttr, _GuardInput widening, overrides
  Task 3: TYPE-05 cast() removal (15 violations — FROZEN, authorized)
  Task 4: TYPE-06 __class__ rewrites (17 FROZEN violations — authorized; 14 MODIFIABLE)
  Task 5: bare-object elimination (36 violations — new t.* aliases required)
  Gate: make pyre + make check CHECK_GATES=pyright both exit 0 for flext-core

Wave 2 (Plan 2):  flext-infra + flext-tests
  Task 0: git pull --rebase (get Wave 1 foundation)
  Task N: same categories for both projects
  Gate: both tools exit 0 for both projects

Wave 3 (Plan 3):  flext-cli (solo — D-04)
  Task 0: git pull --rebase
  Task N: all categories; ~1,419 pyrefly errors + ~150+ pyright issues
  Gate: both tools exit 0 for flext-cli

Wave 4 (Plan 4):  remaining 27 projects (excluding algar-oud-mig)
  Sequencing: by decreasing error count per STATE.md: flext-quality (298),
              flext-observability (280), flext-ldif, flext-meltano, ...
  Independent consumers can run in parallel within the wave (planner decides)
  Gate: make pyre exits 0 (all projects) + make check CHECK_GATES=pyright per project

Micro-plan (Plan 5):  TYPE-07 + TYPE-08 sweep
  Scope: 12 TypeGuard→TypeIs migrations + empty container literal annotation
  All projects; single pass after main waves complete
  Gate: make pyre + make pol both exit 0
```

### Dependency Order (HARD CONSTRAINT)

```
flext-core  ──→  flext-infra  ──→  flext-tests  ──→  all consumers
     ↑                ↑                  ↑
  Wave 1            Wave 2            Wave 2
```

Type changes in `flext-core` cascade to all 32 consumers. Always fix foundation first. Each subsequent wave must `git pull --rebase` before starting to pick up foundation changes.

### ast-grep Rewrite Rules (from sisyphus plans — pre-validated)

**Rule A1** (`__class__ is` → `isinstance`):
```yaml
id: class-is-to-isinstance
language: python
rule:
  pattern: $X.__class__ is $Y
fix: isinstance($X, $Y)
```

**Rule A2** (`__class__ is not` → `not isinstance`):
```yaml
id: class-is-not-to-isinstance
language: python
rule:
  pattern: $X.__class__ is not $Y
fix: not isinstance($X, $Y)
```

**Rule A3** (`__class__ in {…}` → `isinstance(…, (…))`):
```yaml
id: class-in-to-isinstance
language: python
rule:
  pattern: $X.__class__ in {$$$Y}
fix: isinstance($X, ($$$Y))
```

**Rule A4** (`__class__ not in {…}` → `not isinstance`):
```yaml
id: class-not-in-to-isinstance
language: python
rule:
  pattern: $X.__class__ not in {$$$Y}
fix: not isinstance($X, ($$$Y))
```

**Note:** All four rules require dry-run first. Exclude `domain.py:49,75` (Option C — architectural refactor required). Exclude `collection.py:95` (TypeGuard edge case — verify subclass behavior with tests first). Exclude `data_validator.py:221` (`type(None)` edge case — manual rewrite to `isinstance(...) or x is None`).

### Anti-Patterns to Avoid

- **`isinstance(value, t.Primitives)`**: ALL `t.*` aliases are `TypeAliasType` (PEP 695) — CRASHES at runtime. Replace with `isinstance(value, t.PRIMITIVES_TYPES)` (tuple constant) — 2 violations in flext-api.
- **`cast(T, value)` in production code**: FORBIDDEN everywhere except `flext-core/result.py`. The `cast` in `result.py:fail()` is the single authorized exception (necessary due to `Failure` → `r[Never]` invariance).
- **Mechanical `object` → `t.NormalizedValue` swaps**: `t.NormalizedValue` is also FORBIDDEN. Replace with the most specific type available from the `t.*` hierarchy.
- **TypeGuard in new code**: TYPE-07 mandates migration to `TypeIs` (PEP 742) for all 12 existing functions. No new `TypeGuard` should be introduced.
- **Hand-editing `__init__.py`**: These are autogenerated. Run `make gen` after touching any facade exports.
- **Any suppression comment**: `# type: ignore`, `# pyright: ignore`, `# noqa: ANN401` are AXIOMATIC FORBIDDEN.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Type narrowing for primitives | custom isinstance combinations | `u.Guards.is_primitive()` / `u.Guards.is_scalar()` | 56 TypeGuard functions already exist |
| Runtime type tuple for isinstance | `(str, int, float, bool)` inline | `t.PRIMITIVES_TYPES`, `t.SCALAR_TYPES`, `t.CONTAINER_TYPES` | Centralized, correct, consistent |
| JSON serialization | `json.dumps(obj)` | `obj.model_dump_json()` / `TypeAdapter[T].dump_json()` | Pydantic v2 standard; eliminates `default=str` workarounds |
| JSON deserialization | `json.loads(str)` | `Model.model_validate_json(str)` / `TypeAdapter[T].validate_json(str)` | Validated + typed |
| Structural code search | regex grep | `sg --pattern` (ast-grep) | AST-level accuracy; handles nested expressions |
| New recursive type alias | inline union | `t.JsonValue` (already created) | Already exists in `_typings/core.py` |
| Logger factory typing | `Callable[[], Any]` | `t.LoggerFactory` (already created) | Already exists in `_typings/services.py` |
| DI container registration type | `object` | `t.RegisterableService` (already expanded) | Already covers factories + protocols |

**Key insight:** The `t.*` type contract library and `u.Guards.*` TypeGuard functions are mature and comprehensive. Phase 1 should consume them, not extend them (except where bare-object-elimination.md Wave 0 tasks are not yet done — verify against current codebase state at wave start).

---

## Violation Inventory (Authoritative Baselines)

### flext-core (CORRECTED_BASELINE_2026-03-12.md)

| Category | Count | Files Affected | Authorization Status |
|----------|------:|:--------------:|---------------------|
| `__class__` narrowing (FROZEN `_utilities/*`) | 17 | 7 | AUTHORIZED 2026-03-12 |
| `__class__` narrowing (MODIFIABLE `_models/*`, `loggings.py`) | ~14 | 3 | Ready NOW |
| `cast()` — `t.cast` form (FROZEN `result_helpers.py`) | 3 | 1 | AUTHORIZED |
| `cast()` — `t.cast` form (MODIFIABLE `loggings.py`) | 3 | 1 | Ready NOW |
| `cast()` — bare `cast` (FROZEN `mapper.py`) | 9 | 1 | AUTHORIZED |
| `isinstance(x, t.Primitives)` misuse | 2 | 2 (flext-api) | Ready NOW |
| bare `object` annotations (src/) | ~36 | multiple | Ready NOW |

### Consumer Projects (NARROWING-SCAN-SUMMARY.md — 223 violations, 19 of 31 projects)

| Category | Count | Top Offender |
|----------|------:|--------------|
| `cast()` usage | 119 | algar-oud-mig (23, EXCLUDED); flext-quality (15); flext-meltano (18) |
| `__class__` narrowing | 96 | gruponos-meltano-native (21); flext-ldif (28) |
| `Any` type annotations | 8 | flext-dbt-oracle (1); flext-oracle-wms (2) |

### Pyright Root Causes (pyright-zero-errors.md — ~2,098 total)

| Root Cause | Issue Count | Primary Fix |
|------------|------------:|-------------|
| `_operation_stats` PrivateAttr pattern | 121+ cascade | Fix `Annotated[T, PrivateAttr()]` declaration |
| `_GuardInput` union too narrow | widespread `reportArgumentType` | Widen to include `ResultLike`, `BaseModel`, `ConfigMap`, `HasModelDump` |
| Unnecessary isinstance (type already resolved) | 79 | Remove redundant checks |
| Incompatible method overrides | scattered | Fix `model_post_init`, `get`, `register` signatures |
| Missing type annotations | 317 `reportUnknownVariableType` | Add explicit annotations |

### Error Hotspots by Project (STATE.md blockers)

| Project | Pyrefly Errors | Priority | Wave |
|---------|---------------:|----------|------|
| flext-cli | ~1,419 | Dedicated solo plan | Wave 3 |
| flext-quality | 298 | High | Wave 4 |
| flext-observability | 280 | High | Wave 4 |
| flext-core | ~170 | Foundation first | Wave 1 |
| algar-oud-mig | 370 | EXCLUDED | n/a |

---

## Common Pitfalls

### Pitfall 1: `make pyre` Search-Path Failure

**What goes wrong:** `make pyre` exits non-zero, reporting "Invalid search-path" or "0 files checked". All error counts appear to be 0 but nothing was actually checked.
**Why it happens:** pyrefly's `search-path` resolution doesn't expand shell variables (e.g., `${PWD}`) or fails to resolve relative paths when invoked from the repo root. Wave 0 of the sisyphus plan removed legacy artifacts; the current `pyproject.toml` already uses bare relative paths (confirmed: lines 127–174 have no `${PWD}`).
**How to avoid:** Wave 1 task 0 — run `make pyre` first and inspect `.sisyphus/evidence/pyrefly-toolchain.txt` and `.sisyphus/evidence/pyrefly-repo-before.txt`. If errors = 0 but files_checked = 0, the path resolution is still broken. Fix the config path or the invocation in the Makefile `pyre` target.
**Warning signs:** Output shows `projects: 0` or files scanned count is far below expected (~33 projects × average files).

### Pitfall 2: `make check` Reporting "Skipped: 1" for flext-core

**What goes wrong:** Per-project `make check` shows "Skipped: 1" — no pyrefly/pyright check runs.
**Why it happens:** The `check` target orchestration may be routing to wrong scope or the per-project gate has a path issue. CONTEXT.md documents this as a known issue (2026-03-23 state).
**How to avoid:** Investigate by running `make check PROJECT=flext-core CHECK_GATES=pyrefly` with `VERBOSE=1`. If the skip is a misconfigured gate, fix the `base.mk` gate selection before proceeding.
**Warning signs:** `make check PROJECT=flext-core` exits 0 with "Projects: 0" in output.

### Pitfall 3: `isinstance(value, t.SomeAlias)` Runtime Crash

**What goes wrong:** Code that passes `make check` crashes at runtime with `TypeError: Subscripted generics cannot be used with class and instance checks`.
**Why it happens:** ALL `t.*` aliases use PEP 695 `type X = ...` syntax which creates `TypeAliasType` objects. These are annotation-only and CANNOT be used as `isinstance()` arguments.
**How to avoid:** Replace with:
  - `isinstance(value, t.PRIMITIVES_TYPES)` — for `t.Primitives`
  - `isinstance(value, t.SCALAR_TYPES)` — for `t.Scalar`
  - `u.Guards.is_primitive(value)` — TypeGuard function alternative
  The 2 known violations in `flext-api/webhook.py:139` and `flext-api/utilities.py:130` are Wave 1.3 of the strict-typing plan.
**Warning signs:** Tests pass but integration tests or runtime hits TypeError.

### Pitfall 4: Cascade Errors After Foundation Change

**What goes wrong:** Fixing a type in `flext-core` produces hundreds of new errors in downstream projects.
**Why it happens:** 33 projects import from `flext-core`. A narrower type annotation in the foundation produces `reportArgumentType` cascades in every consumer that passes a wider type.
**How to avoid:** Always run `make pyre` (repo-wide) AND `make check CHECK_GATES=pyright` after each foundation change, not just the per-project check. Fix cascades immediately — do not merge a wave that leaves downstream projects broken.
**Warning signs:** `make pyre` shows a sudden spike in errors for projects that were not directly edited.

### Pitfall 5: FROZEN Files Without Authorization

**What goes wrong:** Edits to `flext-core/_utilities/*` get rejected by policy hooks or cause confusion about authorization state.
**Why it happens:** AGENTS.md §10.2 marks these files FROZEN. The unfreeze authorization exists but is verbal/documented only.
**How to avoid:** The authorization is documented in `.sisyphus/plans/strict-typing-execution-plan.md` (Decision 1, 2026-03-12) and confirmed in CONTEXT.md. Proceed directly — no additional authorization needed. Document in each commit message that changes are under the authorized unfreeze.
**Warning signs:** None — just proceed with confidence in the documented authorization.

### Pitfall 6: domain.py:49,75 — Mechanical Replace Breaks Semantics

**What goes wrong:** Applying Rule A2 to `entity_b.__class__ is not entity_a.__class__` produces `not isinstance(entity_b, entity_a.__class__)` — which changes semantics from exact-type identity to MRO traversal.
**Why it happens:** Both operands are variables, not concrete types. `isinstance` accepts subclasses; `__class__ is not` requires exact type match.
**How to avoid:** These 2 sites require Option C (architectural refactor): create `u.Domain.same_type(a, b) -> bool` utility or protocol-based equality check. Manual edit only; exclude from ast-grep sweep.
**Warning signs:** If ast-grep Rule A2 produces `isinstance(X, Y.__class__)` in output — stop, this is wrong for these two lines.

### Pitfall 7: `cast()` in `result.py` Must Stay

**What goes wrong:** Over-aggressive sweep removes the `cast("r[U]", ...)` in `flext-core/result.py:fail()`.
**Why it happens:** Blanket `cast()` search-and-replace treats all sites identically.
**How to avoid:** TYPE-05 explicitly exempts `flext-core/result.py`. The `cast` there is the SOLE authorized exception — `Failure` produces `Result[Never, str]` and `cast` is the only way to widen to `r[U]` due to invariance. Verify the exemption list in ast-grep scope before running.
**Warning signs:** After cast removal, `result.py` pyright errors spike around the `fail()` classmethod.

### Pitfall 8: Double-Work JSON Patterns

**What goes wrong:** `json.dumps(model.model_dump())` pattern produces correct output but is inefficient and prevents type narrowing.
**Why it happens:** Historical pattern from before Pydantic v2 native JSON support.
**How to avoid:** Replace with `model.model_dump_json()` in one pass. Similarly replace `Model.model_validate(json.loads(x))` with `Model.model_validate_json(x)`. These are NOT in scope for TYPE-01 through TYPE-08 directly, but they appear in the same files as other violations — fix them opportunistically during the wave pass.

---

## Code Examples

### __class__ rewrite (Rule A1) — verified pattern

```python
# Source: .sisyphus/plans/strict-typing-execution-plan.md Wave 1.0

# BEFORE (violates TYPE-06)
if value.__class__ is str:
    process_string(value)

# AFTER (correct)
if isinstance(value, str):
    process_string(value)
```

### cast() removal via TypeGuard

```python
# Source: .sisyphus/plans/strict-typing-execution-plan.md Wave 1.2
# mapper.py line 2211 — BEFORE:
result = cast("Mapping[object, object]", value)

# AFTER:
if u.Guards.is_mapping(value):
    result = value  # narrowed to Mapping[str, object]
```

### t.cast replacement in loggings.py

```python
# Source: .sisyphus/evidence/CORRECTED_BASELINE_2026-03-12.md
# loggings.py lines 180–185 — BEFORE:
logger = t.cast(SomeType, get_logger())

# AFTER: use TypeGuard conditional
_logger = get_logger()
if u.Guards.is_logger(_logger):
    logger = _logger  # narrowed by TypeGuard
```

### PEP 695 alias isinstance fix

```python
# Source: .sisyphus/plans/strict-typing-execution-plan.md Wave 1.3
# flext-api/webhook.py:139 — BEFORE (crashes at runtime):
if isinstance(value, t.Primitives):
    ...

# AFTER (uses tuple constant):
if isinstance(value, t.PRIMITIVES_TYPES):
    ...
```

### domain.py Option C — protocol-based equality

```python
# Source: .sisyphus/plans/strict-typing-execution-plan.md Wave 1.1 — Special Handling
# domain.py:49 and :75 — Option C resolution
# Create utility in flext-core/_utilities/domain.py:
def same_type(a: object, b: object) -> bool:
    """Exact-type identity comparison (no MRO traversal, equivalent to __class__ is)."""
    return type(a) is type(b)  # noqa: E721 — intentional identity check


# Usage replaces: entity_b.__class__ is not entity_a.__class__
if not same_type(entity_b, entity_a):
    ...
```

### TypeIs migration (TYPE-07 — micro-plan)

```python
# Source: PEP 742, Python 3.13 typing module
# BEFORE (TypeGuard — bidirectional narrowing only in True branch):
from typing import TypeGuard


def is_str(value: object) -> TypeGuard[str]:
    return isinstance(value, str)


# AFTER (TypeIs — narrows in both branches):
from typing import TypeIs


def is_str(value: object) -> TypeIs[str]:
    return isinstance(value, str)
```

---

## Make Target Reference

| Target | Usage | What It Checks |
|--------|-------|----------------|
| `make pyre` | Repo-wide | pyrefly across src/tests/examples/docs/benchmarks/scripts; JSON report to `.reports/pyrefly/` |
| `make check PROJECT=X` | Per-project | All gates: lint, format, pyrefly, mypy, pyright, security |
| `make check PROJECT=X CHECK_GATES=pyright` | Per-project pyright only | pyright gate only |
| `make check PROJECT=X CHECK_GATES=pyrefly,pyright` | Per-project both type checkers | pyrefly + pyright gates |
| `make pol` | Repo-wide | Zero `Any`, zero `t.NormalizedValue`, zero `# type: ignore` |
| `make test PROJECT=X` | Per-project | pytest non-regression |
| `make validate VALIDATE_SCOPE=workspace` | Full workspace | All validation gates |
| `make gen` | Workspace | Regenerate `__init__.py` lazy exports (after facade changes) |

**IMPORTANT:** The authoritative make target for repo-wide pyrefly is `make pyre`, NOT `make pyrefly-repo`. The sisyphus plans use the latter name but the actual Makefile target (line 793) is `pyre`.

---

## Wave Plan Decomposition

The planner will create 5 GSD plans from this phase:

| Plan | Name | Scope | Prereq |
|------|------|-------|--------|
| 1 | Wave 1: flext-core | flext-core only | None — D-07 fix first |
| 2 | Wave 2: Infrastructure | flext-infra + flext-tests | Plan 1 complete |
| 3 | Wave 3: flext-cli | flext-cli solo | Plan 2 complete |
| 4 | Wave 4: Remaining Consumers | 27 projects (excl. algar-oud-mig) | Plan 3 complete |
| 5 | Micro-plan: TYPE-07 + TYPE-08 | All projects | Plan 4 complete |

### Wave 4 Project Sequencing (Claude's discretion — recommended order by error count)

From STATE.md error hotspots and NARROWING-SCAN-SUMMARY.md:

1. flext-quality (298 errors, 15 cast violations)
2. flext-observability (280 errors)
3. flext-ldif (high __class__ count: 28 violations, 6 cast)
4. flext-meltano (18 cast violations)
5. gruponos-meltano-native (21 __class__, 3 cast)
6. flext-api (3 cast, 2 __class__, isinstance alias misuse)
7. flext-auth, flext-web, flext-ldap (moderate)
8. flext-db-oracle, flext-dbt-* (moderate)
9. All remaining projects in parallel (independent consumers with low counts)

**Parallelization rule:** Projects with no imports from each other can run in parallel. All `flext-tap-*` and `flext-target-*` are leaf nodes and can be parallelized after Wave 2 foundation is clean.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `TypeGuard[T]` | `TypeIs[T]` (PEP 742) | Python 3.13 | Bidirectional narrowing; both True and False branches narrow |
| `X: TypeAlias = ...` | `type X = ...` (PEP 695) | Python 3.12+ | TypeAliasType — NOT isinstance-safe; all `t.*` are now PEP 695 |
| `json.loads` / `json.dumps` | `model_validate_json` / `model_dump_json` | Pydantic v2 | Validated, typed, no `default=str` hacks |
| `TypeGuard[list[object]]` in guards | `TypeIs[list[object]]` | TYPE-07 migration | Cleaner narrowing semantics |
| `Annotated[T, PrivateAttr()]` pattern | `PrivateAttr()` at field level | Pydantic v2.x | Some pyright versions don't recognize Annotated form — root cause of 121+ cascade |

**Deprecated/outdated:**
- `TypeAlias` import from `typing`: Deprecated in Python 3.12, replaced by PEP 695 `type` statement
- Legacy pyrefly artifacts at repo root (`pyrefly_*.{json,txt,csv}`): Wave 0 already removed; do not recreate
- `make pyrefly-repo`: This make target does NOT exist — use `make pyre`

---

## Open Questions

1. **`make check` "Skipped: 1" for flext-core**
   - What we know: CONTEXT.md documents this as a known issue (2026-03-23 state)
   - What's unclear: Whether it's a Makefile routing bug, gate configuration, or env issue
   - Recommendation: Wave 1 task 0 must investigate and fix before any check gate output can be trusted

2. **Fresh pyrefly error count**
   - What we know: Historical 4,385 figure is from pre-Wave 0 (sisyphus analysis). Wave 0 fixed the entrypoint, removed artifacts, and fixed 27 test errors.
   - What's unclear: Current count post-Wave 0 — could be lower
   - Recommendation: D-08 mandates a fresh baseline as the first authoritative measurement after `make pyre` is confirmed working. Do not plan against the 4,385 number.

3. **Wave 0 bare-object tasks — completion status**
   - What we know: bare-object-elimination.md Tasks 1–5 are marked `[x]` (complete): `t.JsonValue`, `t.LoggerFactory`, `t.BootstrapInput`, expanded `t.RegisterableService`, committed `TypeHintSpecifier` changes
   - What's unclear: Whether these were actually committed to `0.12.0-dev` branch or remain local
   - Recommendation: Wave 1 task 0 should verify `t.JsonValue`, `t.LoggerFactory`, `t.BootstrapInput` are importable from `flext_core` before proceeding with bare-object Wave 1 fixes

4. **`domain.py:49,75` Option C implementation scope**
   - What we know: Requires creating `u.Domain.same_type(a, b) -> bool` utility (or equivalent)
   - What's unclear: Whether this requires a new `FlextDomain` subclass in `_utilities/` or can be a standalone function
   - Recommendation: Implement as a private module-level function in `_utilities/domain.py` — same file as the violations. No new subclass needed for a single-use utility.

---

## Environment Availability

| Dependency | Required By | Available | Fallback |
|------------|------------|-----------|---------|
| `make pyre` | TYPE-01 gate | Makefile target exists (line 793) | — |
| `make pol` | TYPE-02/03 gate | Makefile target exists (line 828) | — |
| `make check CHECK_GATES=pyright` | D-05 per-wave gate | Documented in Makefile help | — |
| `sg` (ast-grep) | TYPE-05, TYPE-06 mechanical rewrites | Present in workspace (sgconfig.yml exists) | Edit tool for small-count files |
| `.venv` Python 3.13 | All type checkers | Workspace venv established (Wave 0) | — |
| pyright | Per-project checks | Listed in pyproject.toml dev deps | — |

**Missing dependencies with no fallback:** None identified.

---

## Sources

### Primary (HIGH confidence)

- `.sisyphus/plans/strict-typing-execution-plan.md` — pre-validated ast-grep rules A1–A4, cast replacement map, complete violation inventory per file
- `.sisyphus/plans/bare-object-elimination.md` — new t.* aliases required, wave structure, ~250–350 annotation fixes
- `.sisyphus/plans/pyrefly-repo-hardening.md` — root-cause analysis of make pyre failures, policy gate design
- `.sisyphus/plans/pyright-zero-errors.md` — ~2,098 pyright issues, root causes, 7-wave plan
- `.sisyphus/evidence/CORRECTED_BASELINE_2026-03-12.md` — authoritative pre-migration counts: 65 `__class__`, 15 `cast()`, 29 FROZEN violations
- `.sisyphus/evidence/NARROWING-SCAN-SUMMARY.md` — 223 violations across 19 consumer projects
- `.planning/phases/01-type-system-hardening/01-CONTEXT.md` — locked decisions D-01 through D-08
- `flext/Makefile` — actual make target names (`pyre`, `pol`, `check`) verified directly
- `flext/pyproject.toml` lines 117–185 — `[tool.pyrefly]` config verified (no `${PWD}` in search-path)
- `.claude/skills/flext-strict-typing/SKILL.md` — rules for t.* contracts, TypeGuard, isinstance patterns
- `.claude/skills/flext-type-system/SKILL.md` — TypeAliasType isinstance incompatibility, cross-project namespace inheritance
- `.claude/skills/flext-pyrefly-typecheck-fix/SKILL.md` — recurring error cluster patterns

### Secondary (MEDIUM confidence)

- STATE.md error hotspots (flext-cli 1,419; flext-quality 298; flext-observability 280) — from pre-Wave 0 analysis; actual current count may differ
- NARROWING-SCAN-SUMMARY.md consumer project counts — from 2026-03-12 scan; may have shifted

---

## Metadata

**Confidence breakdown:**
- Standard stack / make targets: HIGH — verified directly in Makefile
- Wave plan structure: HIGH — derived from locked CONTEXT.md decisions D-01 through D-08
- Violation counts: MEDIUM — authoritative baseline from 2026-03-12; post-Wave 0 count unknown until `make pyre` is working
- ast-grep rewrite rules: HIGH — pre-validated in sisyphus plans with operator approval
- Architecture patterns: HIGH — extracted from AGENTS.md + project skills

**Research date:** 2026-03-23
**Valid until:** 2026-04-22 (30 days — tooling is stable; counts change as waves execute)
