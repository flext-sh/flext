---
phase: 10-unified-docs-generation-baseline
plan: 06
subsystem: infra
tags: [flext-infra, deps, thin-orchestrator, toml, modernizer, detection, sync]

requires:
  - phase: 10-01
    provides: "api.py MRO facade, base.py simplification, u.Infra.* utility foundation"
provides:
  - "All deps domain services refactored to thin orchestrator pattern"
  - "New u.Infra.table(), u.Infra.document(), u.Infra.parse_text(), u.Infra.is_table(), u.Infra.is_aot() TOML utilities"
  - "Zero direct tomlkit manipulation in deps service methods"
affects: [10-07, 10-08]

tech-stack:
  added: []
  patterns:
    - "u.Infra.table()/document()/parse_text() for TOML object creation"
    - "u.Infra.ensure_dir() for directory creation instead of direct mkdir"

key-files:
  created: []
  modified:
    - "flext-infra/src/flext_infra/_utilities/toml.py"
    - "flext-infra/src/flext_infra/deps/modernizer.py"
    - "flext-infra/src/flext_infra/deps/_detector_runtime.py"
    - "flext-infra/src/flext_infra/deps/path_sync_rewrite.py"
    - "flext-infra/src/flext_infra/deps/fix_pyrefly_config.py"
    - "flext-infra/src/flext_infra/deps/internal_sync.py"

key-decisions:
  - "detection_analysis.py (361 LOC) accepted as internal mixin helper -- pure analysis logic inherited by detection.py, not a standalone service"
  - "tomlkit type imports retained for type annotations -- plan targets manipulation not annotations"
  - "read_text() for deptry JSON output accepted -- reads external tool output, not TOML manipulation"

patterns-established:
  - "u.Infra.table()/document()/parse_text() as SSOT for TOML object creation in deps domain"

requirements-completed: [DOCS-06]

duration: 9min
completed: 2026-04-06
---

# Phase 10 Plan 06: Deps Domain Thin Orchestrators Summary

**Deps domain (13 files, 2942 LOC) refactored to thin orchestrator pattern -- all direct tomlkit manipulation and mkdir calls replaced with u.Infra.* utility delegation**

## Performance

- **Duration:** 9 min
- **Started:** 2026-04-06T00:15:48Z
- **Completed:** 2026-04-06T00:25:32Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Eliminated all direct `tomlkit.table()`, `tomlkit.array()`, `tomlkit.parse()`, `tomlkit.document()` calls from deps service methods
- Replaced 4 direct `mkdir` calls with `u.Infra.ensure_dir()` across 3 files
- Added 5 new TOML utility methods to `FlextInfraUtilitiesToml`: `table()`, `document()`, `parse_text()`, `is_table()`, `is_aot()`
- Zero ruff + pyrefly + pyright errors maintained across entire deps domain

## Task Commits

Each task was committed atomically:

1. **Task 1: Refactor deps modernizer and detection services** - `71b6d33` (feat)
2. **Task 2: Refactor deps sync and config fixer services** - `51bcf77` (feat)

## Files Created/Modified
- `flext-infra/src/flext_infra/_utilities/toml.py` - Added table(), document(), parse_text(), is_table(), is_aot() utilities
- `flext-infra/src/flext_infra/deps/modernizer.py` - Removed `import tomlkit`, replaced tomlkit.table() with u.Infra.table()
- `flext-infra/src/flext_infra/deps/_detector_runtime.py` - Replaced mkdir with u.Infra.ensure_dir()
- `flext-infra/src/flext_infra/deps/path_sync_rewrite.py` - Removed `import tomlkit`, replaced tomlkit.table() with u.Infra.table()
- `flext-infra/src/flext_infra/deps/fix_pyrefly_config.py` - Removed `import tomlkit`, replaced tomlkit.array()/parse()/document() with u.Infra.*
- `flext-infra/src/flext_infra/deps/internal_sync.py` - Replaced 2 mkdir calls with u.Infra.ensure_dir()

## Decisions Made
- detection_analysis.py (361 LOC) accepted as internal mixin helper -- it provides analysis runners (deptry, mypy, pip-check) inherited by detection.py and is pure logic, not a standalone orchestrator
- tomlkit type imports (`Table`, `TOMLDocument`, `Item`, `AoT`, `Container`) retained for type annotations -- the plan targets runtime TOML manipulation, not type-level references
- The single `read_text()` in detection_analysis.py reads deptry's JSON output file, not TOML -- this is external tool output parsing, acceptable in the analysis helper

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added TOML creation utilities to u.Infra**
- **Found during:** Task 1
- **Issue:** u.Infra.* lacked table(), document(), parse_text() factory methods needed by deps services
- **Fix:** Added 5 methods to FlextInfraUtilitiesToml delegating to u.Cli.toml_*
- **Files modified:** flext-infra/src/flext_infra/_utilities/toml.py
- **Verification:** ruff + pyrefly + pyright 0 errors
- **Committed in:** 71b6d33 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Utility creation was explicitly anticipated by the plan ("If no matching utility exists, CREATE the utility method"). No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Deps domain fully compliant with thin orchestrator pattern
- Ready for 10-07 (engine domain refactoring) and 10-08 (library verification + facade finalization)

---
*Phase: 10-unified-docs-generation-baseline*
*Completed: 2026-04-06*
