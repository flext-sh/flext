---
phase: 05-package-migration
plan: 03
subsystem: infra
tags: [uv, poetry-removal, makefile, ci, envrc]

requires:
  - phase: 05-02
    provides: All 34 pyproject.toml on hatchling + unified uv.lock
provides:
  - Zero Poetry references in build tooling, CI, and environment config
  - CI uses astral-sh/setup-uv instead of snok/install-poetry
  - All make targets use direct venv invocation or uv commands
affects: []

tech-stack:
  added: [astral-sh/setup-uv]
  patterns: [direct venv invocation replaces poetry run, uv lock/sync replaces poetry lock/install]

key-files:
  created: []
  modified:
    - base.mk
    - Makefile
    - .github/workflows/ci.yml
    - .github/workflows/release.yml
    - .envrc

key-decisions:
  - "POETRY_VIRTUALENVS exports removed entirely (uv manages venv via UV_PROJECT_ENVIRONMENT)"
  - "All $(POETRY) run replaced with direct invocation since venv bin is on PATH"
  - "Per-project poetry lock/install replaced with uv lock/sync --directory equivalents"

patterns-established:
  - "uv lock / uv sync --all-groups for dependency management"
  - "astral-sh/setup-uv@v5 with enable-cache for CI"

requirements-completed: [MIG-06]

duration: 2min
completed: 2026-03-24
---

# Phase 05 Plan 03: Poetry Hard-Cut from Build Tooling Summary

**All Poetry references removed from base.mk, root Makefile, CI workflows, and .envrc — full uv hard-cut complete**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-24T21:01:18Z
- **Completed:** 2026-03-24T21:05:27Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Removed POETRY variable, POETRY_VIRTUALENVS exports, and all $(POETRY) run invocations from base.mk
- Removed POETRY_BIN, POETRY_ENV variables and all poetry commands from root Makefile (30+ occurrences)
- Replaced snok/install-poetry with astral-sh/setup-uv@v5 in both CI and release workflows
- Added submodules: recursive to ci.yml checkout step
- Cleaned POETRY_VIRTUALENVS_* exports from .envrc

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace Poetry in base.mk and root Makefile** - `5b222f72` (feat)
2. **Task 2: Update CI workflows and .envrc** - `a73885d4` (feat)

## Files Created/Modified

- `base.mk` - Removed POETRY variable, POETRY_VIRTUALENVS exports, replaced $(POETRY) run/lock/install/build with direct/uv commands
- `Makefile` - Removed POETRY_BIN, POETRY_ENV, replaced 30+ poetry command invocations with uv equivalents
- `.github/workflows/ci.yml` - Replaced snok/install-poetry with astral-sh/setup-uv, added submodules: recursive
- `.github/workflows/release.yml` - Replaced snok/install-poetry with astral-sh/setup-uv
- `.envrc` - Removed POETRY_VIRTUALENVS_CREATE/IN_PROJECT/PATH exports

## Decisions Made

- POETRY_VIRTUALENVS exports removed entirely — uv manages venv via UV_PROJECT_ENVIRONMENT already set in .envrc
- All $(POETRY) run replaced with direct invocation since venv bin is already on PATH via base.mk and .envrc
- Per-project poetry lock/install/update replaced with uv lock/sync --directory equivalents
- Removed poetry from pip install in setup target (only pip, pipx, uv remain)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Next Phase Readiness

- Phase 05 (package-migration) fully complete: all 34 projects on hatchling, uv workspace wired, Poetry fully removed
- The entire build/test/CI pipeline runs on uv without Poetry installed

## Self-Check: PASSED

---
*Phase: 05-package-migration*
*Completed: 2026-03-24*
