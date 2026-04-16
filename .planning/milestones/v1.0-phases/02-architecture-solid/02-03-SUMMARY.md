---
phase: 02-architecture-solid
plan: 03
subsystem: architecture
tags: [pydantic, annotated, field, mutable-defaults, ast-grep]

requires:
  - phase: 02-02
    provides: "DIP protocol enforcement complete"
provides:
  - "All ~500 m.Field() usages migrated to Annotated[T, m.Field(...)] canonical form"
  - "Zero mutable m.Field(default=[]) or m.Field(default={}) in production code"
  - "Redundant Annotated[T, m.Field(...)] = m.Field(...) patterns cleaned up"
affects: [02-04, 02-05]

tech-stack:
  added: []
  patterns:
    - "Annotated[T, m.Field(...)] canonical Pydantic v2 field pattern"
    - "default_factory for all mutable defaults (list, dict)"

key-files:
  created: []
  modified:
    - "flext-core/src/flext_core/errors.py"
    - "flext-core/src/flext_core/service.py"
    - "flext-core/src/flext_core/registry.py"
    - "flext-core/src/flext_core/_models/dispatcher.py"
    - "flext-core/src/flext_core/_models/entity.py"
    - "flext-core/src/flext_core/_models/collections.py"
    - "flext-core/src/flext_core/_models/containers.py"
    - "flext-core/src/flext_core/_models/cqrs.py"
    - "flext-dbt-oracle/src/flext_dbt_oracle/models.py"
    - "flext-infra/src/flext_infra/check/_models.py"
    - "flext-ldif/src/flext_ldif/_models/domain_entries.py"

key-decisions:
  - "Redundant = m.Field(default_factory=...) removed when already inside Annotated metadata"
  - "Dynamic/programmatic m.Field() in test helpers excluded from migration (not annotations)"
  - "2 mutable defaults in flext-dbt-oracle fixed (default=[] -> default_factory=list)"

patterns-established:
  - "Annotated[T, m.Field(...)] for all Pydantic model fields with metadata"
  - "default_factory=list/dict for all collection defaults"

requirements-completed: [ARCH-03, ARCH-07]

duration: 20min
completed: 2026-03-24
---

# Phase 02 Plan 03: m.Field()->Annotated Migration Summary

**Migrated ~500 m.Field() usages to Annotated[T, m.Field(...)] canonical Pydantic v2 form across 33 projects, fixed 2 mutable defaults, cleaned up redundant m.Field() assignments**

## Performance

- **Duration:** 20 min
- **Started:** 2026-03-24T05:38:35Z
- **Completed:** 2026-03-24T05:58:11Z
- **Tasks:** 2
- **Files modified:** ~80 across 22 projects

## Accomplishments
- All m.Field() annotations in src/ and tests/ migrated to Annotated[T, m.Field(...)] form
- Zero mutable m.Field(default=[]) or m.Field(default={}) remaining in production code
- PrivateAttr() (94 usages) untouched as required
- 33/34 projects pass workspace check (1 failure is pre-existing Go toolchain issue in flexcore)

## Task Commits

1. **Task 1: m.Field()->Annotated migration in flext-core** - via `make save` (refactor)
2. **Task 2: m.Field()->Annotated migration across all consumer projects** - via `make save` (refactor)

## Files Created/Modified
- 16 files in flext-core/src/ — m.Field() to Annotated migration + redundant default cleanup
- ~60 files across 21 consumer projects — ast-grep bulk migration
- 17 files with Annotated import additions
- 15 files with double-Annotated artifact cleanup

## Decisions Made
- Redundant `Annotated[T, m.Field(default_factory=...)] = m.Field(default_factory=...)` patterns cleaned to just `Annotated[T, m.Field(default_factory=...)]` — the outer m.Field() was redundant
- Programmatic m.Field() in `flext-cli/tests/helpers/_impl.py` excluded — dynamic model construction, not annotations
- ast-grep `$NAME: $TYPE = m.Field($$$ARGS)` pattern used for bulk migration with post-processing for edge cases

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed double-Annotated artifacts from ast-grep**
- **Found during:** Task 2
- **Issue:** ast-grep matched `Annotated[T, m.Field(...)] = m.Field(...)` and wrapped it again, creating `Annotated[Annotated[T, m.Field(...)], m.Field(...)]`
- **Fix:** Python script to detect and remove outer Annotated wrapper + trailing m.Field()
- **Files modified:** 15 files across flext-infra, flext-ldif, flext-meltano, gruponos-meltano-native
- **Verification:** `grep -rn "Annotated\[Annotated\["` returns 0
- **Committed in:** Task 2 commit

**2. [Rule 2 - Missing Critical] Fixed 2 mutable defaults in flext-dbt-oracle**
- **Found during:** Task 2
- **Issue:** `Field(default=[])` in flext-dbt-oracle/models.py lines 41-42
- **Fix:** Changed to `Field(default_factory=list)`
- **Files modified:** flext-dbt-oracle/src/flext_dbt_oracle/models.py

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical)
**Impact on plan:** Both necessary for correctness. No scope creep.

## Issues Encountered
- Pre-existing test failure in flext-core (benchmark test imports renamed class) — out of scope
- Pre-existing Go toolchain version mismatch in flexcore — out of scope

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ARCH-03 and ARCH-07 complete
- Ready for remaining Phase 02 plans (PEP 695 type aliases, import normalization)

---
*Phase: 02-architecture-solid*
*Completed: 2026-03-24*
