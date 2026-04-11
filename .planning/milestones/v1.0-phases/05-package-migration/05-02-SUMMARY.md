---
phase: 05-package-migration
plan: 02
subsystem: build
tags: [hatchling, uv, workspace, poetry-removal, pyproject]

requires:
  - phase: 05-01
    provides: 3 foundation projects on hatchling + modernizer updated
provides:
  - All 34 pyproject.toml files use hatchling build backend
  - Single unified uv.lock for entire workspace
  - Zero poetry.lock files remain
  - Root uv workspace with all members wired
affects: [05-03]

tech-stack:
  added: [uv-workspace]
  patterns: [uv workspace member resolution replaces @ file: path deps]

key-files:
  created:
    - uv.lock
  modified:
    - pyproject.toml
    - flext-api/pyproject.toml
    - flext-auth/pyproject.toml
    - flext-cli/pyproject.toml
    - flext-web/pyproject.toml
    - flext-observability/pyproject.toml
    - flext-quality/pyproject.toml
    - flext-plugin/pyproject.toml
    - flext-db-oracle/pyproject.toml
    - flext-grpc/pyproject.toml
    - flext-ldap/pyproject.toml
    - flext-ldif/pyproject.toml
    - flext-meltano/pyproject.toml
    - flext-oracle-oic/pyproject.toml
    - flext-oracle-wms/pyproject.toml
    - flext-tap-ldap/pyproject.toml
    - flext-tap-ldif/pyproject.toml
    - flext-tap-oracle/pyproject.toml
    - flext-tap-oracle-oic/pyproject.toml
    - flext-tap-oracle-wms/pyproject.toml
    - flext-target-ldap/pyproject.toml
    - flext-target-ldif/pyproject.toml
    - flext-target-oracle/pyproject.toml
    - flext-target-oracle-oic/pyproject.toml
    - flext-target-oracle-wms/pyproject.toml
    - flext-dbt-ldap/pyproject.toml
    - flext-dbt-ldif/pyproject.toml
    - flext-dbt-oracle/pyproject.toml
    - flext-dbt-oracle-wms/pyproject.toml
    - flexcore/pyproject.toml
    - gruponos-meltano-native/pyproject.toml
    - algar-oud-mig/pyproject.toml
    - flext-core/pyproject.toml
    - flext-infra/pyproject.toml
    - flext-tests/pyproject.toml

key-decisions:
  - "algar-oud-mig included in conversion despite not being in original plan member list (Rule 2 - completeness)"
  - "Foundation projects (flext-core/infra/tests) @ file: deps also cleaned for workspace resolution"
  - "uv.lock resolves 393 packages across all 34 workspace members"

requirements-completed: [MIG-04, MIG-05]

duration: 4min
completed: 2026-03-24
---

# Phase 05 Plan 02: Bulk Consumer Hatchling Migration + UV Workspace Summary

**All 34 pyproject.toml files converted to hatchling, unified uv.lock generated, 34 poetry.lock files removed**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-24T20:54:56Z
- **Completed:** 2026-03-24T20:58:40Z
- **Tasks:** 2
- **Files modified:** 36

## Accomplishments

- Converted all 30 consumer + root pyproject.toml from poetry.core.masonry to hatchling.build
- Added [tool.hatch.build.targets.wheel] with correct packages path to all projects
- Removed all [tool.poetry] empty sections across entire workspace
- Replaced all `@ file:` dependency references with bare package names (including foundation projects from Plan 01)
- Added [tool.uv.workspace] with 34 members and [tool.uv.sources] entries to root pyproject.toml
- Generated unified uv.lock resolving 393 packages
- Removed 34 poetry.lock files (backed up to .bak first)
- `uv lock --check` passes cleanly

## Task Commits

1. **Task 1: Convert all pyproject.toml + wire workspace** - `401644ea` (feat)
2. **Task 2: Generate uv.lock + remove poetry.lock files** - `3c650a72` (feat)

## Decisions Made

- algar-oud-mig was not in the plan's member list but existed as a submodule with poetry settings; included for completeness
- Foundation projects from Plan 01 still had `@ file:` deps that needed cleaning for uv workspace resolution
- No `[tool.uv.override]` entries needed; resolution succeeded cleanly on first attempt

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing] Foundation projects @ file: deps not cleaned in Plan 01**
- **Found during:** Task 1
- **Issue:** flext-core, flext-infra, flext-tests still had `@ file:` dependency references
- **Fix:** Cleaned them alongside consumer projects
- **Files modified:** flext-core/pyproject.toml, flext-infra/pyproject.toml, flext-tests/pyproject.toml

**2. [Rule 2 - Missing] algar-oud-mig not in plan member list**
- **Found during:** Task 1
- **Issue:** algar-oud-mig is a submodule with poetry settings but was omitted from the plan
- **Fix:** Converted to hatchling and added to workspace members/sources
- **Files modified:** algar-oud-mig/pyproject.toml, pyproject.toml

## Known Stubs

None.

## Self-Check: PASSED
---
*Phase: 05-package-migration*
*Completed: 2026-03-24*
