---
phase: 10-unified-docs-generation-baseline
plan: 08
subsystem: infra
tags: [factory-method, facade, flext-infra, api, domain-services]

# Dependency graph
requires:
  - phase: 10-unified-docs-generation-baseline (plans 01-07)
    provides: Refactored domain services (basemk, check, codegen, deps, github, refactor, release, validate, workspace)
provides:
  - FlextInfra factory-method facade with 9 domain service accessors
  - Verified library domains (detectors, gates, rules, transformers) follow correct patterns
  - Zero direct rope imports in detectors and transformers (all through t.Infra.RopeProject)
affects: [flext-infra consumers, future domain extensions]

# Tech tracking
tech-stack:
  added: []
  patterns: [factory-method-facade, lazy-import-for-circular-avoidance, type-returning-factory]

key-files:
  created: []
  modified:
    - flext-infra/src/flext_infra/api.py
    - flext-infra/pyproject.toml

key-decisions:
  - "Factory methods return type[ServiceClass] (not instances) to avoid kwargs type mismatch across heterogeneous domain constructors"
  - "validate renamed to validate_scanner to avoid clash with Pydantic BaseModel.validate"
  - "PLC0415 per-file-ignore for api.py — inline imports required to break circular dependency chains"
  - "No _base_rule.py exists in rules/ — rules use FlextInfraRefactorRule from refactor/_base_rule.py or standalone classes"

patterns-established:
  - "Factory-method facade: FlextInfra.domain() returns the class, caller instantiates with domain-specific kwargs"
  - "9 domain accessors: basemk, check, codegen, deps, github, refactor, release, validate_scanner, workspace"

requirements-completed: [DOCS-08]

# Metrics
duration: 9min
completed: 2026-04-06
---

# Phase 10 Plan 08: Library Domains Verification and FlextInfra Facade Summary

**FlextInfra factory-method facade with 9 domain accessors returning service classes, all library domains (detectors, gates, rules, transformers) verified clean**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-06T00:41:01Z
- **Completed:** 2026-04-06T00:50:56Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Verified all 4 library domains pass ruff + pyrefly with 0 errors (detectors, gates, rules, transformers)
- Verified zero direct `from rope` imports in detectors/ and transformers/ (all through t.Infra.RopeProject)
- Verified inheritance patterns: 11 detectors from FlextInfraScanFileMixin, 8 gates from FlextInfraGate, 12 transformers from FlextInfraRopeTransformer/FlextInfraChangeTrackingTransformer
- Finalized FlextInfra api.py with 9 static factory-method accessors for all domain services
- All factory methods return the domain service class (not instance) to preserve type safety

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify library domains** - No commit (verification-only, zero changes needed)
2. **Task 2: Finalize FlextInfra api.py facade** - `5e9d309` (feat)

## Files Created/Modified

- `flext-infra/src/flext_infra/api.py` - FlextInfra facade with 9 factory-method accessors for domain services
- `flext-infra/pyproject.toml` - Added PLC0415 per-file-ignore for api.py (inline imports required for circular avoidance)

## Decisions Made

- **Factory methods return type[ServiceClass]**: Domain constructors have heterogeneous kwargs (Path, bool, Mapping, etc.). Using `type[ServiceClass]` avoids the impossible `**kwargs: str` typing issue and lets callers instantiate with correct domain-specific parameters.
- **validate renamed to validate_scanner**: BaseModel has a built-in `validate` classmethod. Pyrefly correctly flags the override clash. Renamed to `validate_scanner` to be explicit.
- **Per-file-ignore over noqa comments**: Adding `"**/api.py" = ["PLC0415"]` to pyproject.toml is cleaner than 9 individual `# noqa: PLC0415` comments, consistent with existing patterns (models.py, settings.py, workspace/).
- **No _base_rule.py in rules/**: The rules/ directory has concrete rule classes. Some inherit from `FlextInfraRefactorRule` (in refactor/_base_rule.py), others are standalone. This is the existing pattern — no changes needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed validate method name clash**

- **Found during:** Task 2 (FlextInfra facade)
- **Issue:** `validate` as a staticmethod on FlextInfra clashes with Pydantic `BaseModel.validate` (pyrefly `missing-override-decorator` error)
- **Fix:** Renamed to `validate_scanner` to be explicit and avoid the clash
- **Files modified:** flext-infra/src/flext_infra/api.py
- **Verification:** pyrefly check passes with 0 errors on api.py
- **Committed in:** 5e9d309 (Task 2 commit)

**2. [Rule 1 - Bug] Changed factory return type from instance to class**

- **Found during:** Task 2 (FlextInfra facade)
- **Issue:** `**kwargs: str` on factory methods is incompatible with domain constructors that accept Path, bool, Mapping, etc. (pyrefly reported 90+ bad-argument-type errors)
- **Fix:** Changed factory methods to return `type[ServiceClass]` instead of instantiating. Callers get the class and instantiate with correct kwargs.
- **Files modified:** flext-infra/src/flext_infra/api.py
- **Verification:** All 3 linters pass with 0 errors; runtime import test confirms all 9 factory methods return correct classes
- **Committed in:** 5e9d309 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes were necessary for type correctness. The factory-method-returns-class pattern is cleaner than the plan's `**kwargs` approach and avoids type safety issues.

## Verification Results

### Library Domain Verification (Task 1)

| Domain | Files | LOC | Ruff | Pyrefly | Direct Rope Imports | Base Pattern |
|--------|-------|-----|------|---------|--------------------|----|
| detectors/ | 16 | ~1800 | 0 errors | 0 errors | 0 (all via t.Infra.RopeProject) | FlextInfraScanFileMixin + p.Infra.Scanner |
| gates/ | 10 | ~1160 | 0 errors | 0 errors | N/A | FlextInfraGate (ABC) |
| rules/ | 7 py + 16 yml | ~1000 | 0 errors | 0 errors | N/A | FlextInfraRefactorRule or standalone |
| transformers/ | 25 | ~3250 | 0 errors | 0 errors | 0 (all via t.Infra.RopeProject) | FlextInfraRopeTransformer |

### Factory Method Verification (Task 2)

| Factory Method | Returns | Runtime Test |
|---------------|---------|--------------|
| FlextInfra.basemk() | FlextInfraBaseMkGenerator | OK |
| FlextInfra.check() | FlextInfraWorkspaceChecker | OK |
| FlextInfra.codegen() | FlextInfraCodegenFixer | OK |
| FlextInfra.deps() | FlextInfraPyprojectModernizer | OK |
| FlextInfra.github() | FlextInfraGithubService | OK |
| FlextInfra.refactor() | FlextInfraRefactorEngine | OK |
| FlextInfra.release() | FlextInfraReleaseOrchestrator | OK |
| FlextInfra.validate_scanner() | FlextInfraTextPatternScanner | OK |
| FlextInfra.workspace() | FlextInfraOrchestratorService | OK |

## Issues Encountered

- Pre-existing ruff and pyrefly errors in deps/_phases/ files (tomlkit `Item`/`Container`/`Table` not imported) and other files — these are from uncommitted changes from prior plans, not introduced by this plan.

## Known Stubs

None - all factory methods are wired to actual domain service classes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 10 complete: all 8 plans executed
- FlextInfra facade provides single-entry-point discovery for all domain services
- All library domains verified clean with consistent patterns
- Ready for docs generation or next milestone work

---
*Phase: 10-unified-docs-generation-baseline*
*Completed: 2026-04-06*
