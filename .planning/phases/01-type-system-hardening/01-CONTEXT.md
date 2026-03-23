# Phase 1: Type System Hardening - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate all 4,385 pyrefly errors and every `Any`/`object`/`cast`/`ignore` typing shortcut across 33 projects, achieving `make pyrefly-repo` = 0 errors AND `pyright` = 0 errors/warnings. Covers TYPE-01 through TYPE-08. No new features, no architecture changes — type system cleanup only.

Pre-authorized decisions already in place:
- `_utilities/*` unfreeze: authorized 2026-03-12 for `__class__` + `cast()` behavioral changes
- `algar-oud-mig`: excluded from scope (not part of flext-sh org publishing)

</domain>

<decisions>
## Implementation Decisions

### Plan Decomposition
- **D-01:** Phase 1 is organized as big wave plans, not per-project or per-error-category. Wave order: `flext-core` → `flext-infra + flext-tests` → `flext-cli (solo)` → remaining consumers.
- **D-02:** Each wave plan covers ALL error categories for that batch in a single pass: pyrefly errors, pyright errors, and any applicable TYPE-0X requirements (no separate `__class__` pass, no separate `cast()` pass).
- **D-03:** Researchers and planners MUST read the existing `.sisyphus` plans as reference input — they contain baseline counts, wave analyses, and proven ast-grep rewrite rules. Do not re-derive what's already documented there.

### flext-cli Sequencing
- **D-04:** flext-cli gets a **dedicated solo plan** between the `flext-infra+tests` wave and the remaining consumers wave. Rationale: 1,419 errors (33% of total) warrant focused attention; placing it after infra ensures the dependency foundation is clean before tackling the largest consumer.

### Type Checker Scope
- **D-05:** Phase 1 success requires **both** `make pyrefly-repo` AND `make typecheck` (pyright) returning 0 errors/warnings. The `pyright-zero-errors.md` sisyphus plan is in scope for Phase 1. Each wave plan must pass both tools before the wave is considered done.

### TypeGuard→TypeIs + Empty Containers (TYPE-07, TYPE-08)
- **D-06:** TYPE-07 (12 TypeGuard functions → TypeIs, PEP 742) and TYPE-08 (annotated empty container literals) are handled in a **separate final micro-plan** after the main waves complete. Main waves focus on the error mass; the micro-plan sweeps these targeted items across all projects at once.

### Claude's Discretion
- Within each wave plan, the sequencing of individual projects is at Claude's discretion (as long as dependency order is respected: flext-core before infra, infra before consumers).
- The exact boundary between "small consumers" and "remaining consumers" within the final wave can be determined by the planner based on error counts and project dependencies.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Authoritative Baselines
- `.sisyphus/evidence/CORRECTED_BASELINE_2026-03-12.md` — Authoritative pre-migration counts: `__class__` (65 violations), `cast()` (15), FROZEN file analysis (29 violations needing unfreeze), exclusion zones
- `.sisyphus/evidence/NARROWING-SCAN-SUMMARY.md` — Narrowing patterns by project

### Sisyphus Plans (reference, not prescriptive — use as input to GSD planning)
- `.sisyphus/plans/strict-typing-execution-plan.md` — Phase 1: __class__ rewrites (82 violations, ast-grep rules), Phase 2: JSON migration (103 matches), Phase 3: return None→r[T] triage. Includes operator decisions and rewrite rules.
- `.sisyphus/plans/bare-object-elimination.md` — Bare `object`/`dict`/`list` annotation strategy: new type aliases to create (`t.JsonValue`, `t.LoggerFactory`, etc.), ~350 annotation fixes, 7-wave execution plan.
- `.sisyphus/plans/pyright-zero-errors.md` — Pyright error distribution (~2,098 issues), root causes (`_operation_stats` PrivateAttr pattern = 121+ cascade, `_GuardInput` too narrow), wave plan.

### Requirements
- `.planning/REQUIREMENTS.md` §TYPE — TYPE-01 through TYPE-08 definitions and acceptance criteria
- `.planning/ROADMAP.md` §Phase 1 — Success criteria (5 criteria) that define done

### Governance
- `AGENTS.md` §10.2 — FROZEN file policy; operator unfreeze for `_utilities/*` authorized 2026-03-12

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `u.Guards.is_*()` (56 functions): TypeGuard functions in `flext-core/_utilities/guards.py` — primary replacement for `__class__ is` patterns. Key: `is_primitive()`, `is_scalar()`, `is_container()`, `is_list()`, `is_mapping()`
- ast-grep rewrite rules: Already designed in strict-typing-execution-plan.md (Rules A1–A5 for `__class__`, Rules B1–B3 for `cast()`, Rules C1–C2 for isinstance misuse)
- `t.*` validation types: 290+ annotated-types constraints already in `flext-core/src/flext_core/_typings/` — use these before creating new aliases

### Established Patterns
- Dependency order (HARD CONSTRAINT): `flext-core` → `flext-infra` → `flext-tests` → consumers. Type changes cascade — always fix foundation first.
- `__init__.py` files are AUTOGENERATED — fix generators, never hand-edit
- Sequential execution across projects — parallel execution within a wave is acceptable if projects are independent consumers

### Integration Points
- `make pyrefly-repo`: Authoritative entrypoint for repo-wide type checking (Wave 0 already set this up)
- `make check PROJECT=<name>`: Per-project validation gate
- `make validate VALIDATE_SCOPE=workspace`: Full workspace validation

### Error Hotspots (top offenders to watch)
- `flext-cli`: 1,419 errors (gets dedicated plan)
- `algar-oud-mig`: 370 errors (EXCLUDED — do not touch)
- `flext-quality`: 298 errors
- `flext-observability`: 280 errors
- `flext-core`: 170 errors (tackled first in foundation wave)

</code_context>

<specifics>
## Specific Requirements

- The `algar-oud-mig` project has 370 errors but is explicitly out of scope — skip it entirely in all waves.
- FROZEN file unfreeze already authorized for `_utilities/*` — `__class__` + `cast()` fixes proceed without additional authorization.
- domain.py:49,75 — two dynamic `__class__` comparisons require architectural refactor (protocol-based equality), not mechanical isinstance swap. These are "Option C" per the sisyphus plan.
- Every wave plan must validate with BOTH `make pyrefly-repo` AND `make typecheck` before the wave is marked done.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-type-system-hardening*
*Context gathered: 2026-03-23*
