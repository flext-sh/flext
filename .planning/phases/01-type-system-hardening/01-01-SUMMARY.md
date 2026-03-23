---
phase: 01-type-system-hardening
plan: 01
subsystem: infra
tags: [pyrefly, pyright, typing, flext-core, type-safety]

requires:
  - phase: none
    provides: "First plan — no dependencies"
provides:
  - "Type-clean flext-core foundation (0 pyrefly, 0 pyright errors)"
  - "Working make pyre entrypoint with workspace-level pyrefly check"
  - "same_type() utility for exact-type identity comparisons"
  - "Fresh baseline: 0 pyrefly errors repo-wide (down from 4,385)"
affects: [01-02, 01-03, 01-04, 01-05]

tech-stack:
  added: [pyrefly-workspace-config, WORKSPACE_PYTHONPATH]
  patterns: [isinstance-over-class-check, TypeGuard-narrowing, t-star-contracts]

key-files:
  created:
    - ".reports/pyrefly/"
  modified:
    - "flext-core/src/flext_core/_utilities/guards.py"
    - "flext-core/src/flext_core/_utilities/domain.py"
    - "flext-core/src/flext_core/_models/domain.py"
    - "flext-core/src/flext_core/typings.py"
    - "flext-core/src/flext_core/result.py"
    - "pyproject.toml"
    - "base.mk"

key-decisions:
  - "cast() in decorators.py eliminated by widening _resolve_logger() param — no cast needed when using isinstance()"
  - "same_type() utility created for domain.py Option C sites (exact-type identity)"
  - "Workspace-level pyrefly config with WORKSPACE_PYTHONPATH replacing hardcoded paths"

patterns-established:
  - "isinstance() + TypeGuard replaces __class__ is comparisons"
  - "t.* contracts replace bare object/Any annotations"
  - "cast() only authorized in result.py"

requirements-completed: [TYPE-01, TYPE-02, TYPE-03, TYPE-04, TYPE-05, TYPE-06]

duration: multi-session
completed: 2026-03-23
---

# Plan 01-01: Wave 1 Summary

**Fixed make pyre entrypoint, established 0-error baseline, eliminated all typing shortcuts in flext-core foundation**

## Performance

- **Duration:** Multi-session (spread across several context windows)
- **Completed:** 2026-03-23
- **Tasks:** 2
- **Files modified:** 17+

## Accomplishments
- Fixed broken `make pyre` entrypoint — now reports authoritative 0-error counts repo-wide
- Eliminated all pyrefly and pyright errors in flext-core
- Replaced all `__class__ is` comparisons with `isinstance()` or `same_type()`
- Removed all `cast()` calls outside `result.py`
- Replaced all bare `object`/`Any` annotations with specific `t.*` contracts
- Removed all `# type: ignore` comments
- Introduced `WORKSPACE_PYTHONPATH` for dynamic path resolution in pyrefly config

## Task Commits

1. **Task 1: Fix make pyre entrypoint + baseline** — `80a6cc2c`, `5ee9c786`, `7eaf057b`, `7836fb43`
2. **Task 2: Eliminate all type errors in flext-core** — completed across prior sessions
**Plan metadata:** `0f5228a6` (docs: complete Wave 1 plan)

## Decisions Made
- cast() in decorators.py: widened parameter type instead of casting — isinstance() handles narrowing internally
- domain.py Option C sites: created `same_type()` utility rather than isinstance() (preserves exact-type semantics)
- WORKSPACE_PYTHONPATH: dynamic path resolution replaces hardcoded absolute paths in pyrefly config

## Deviations from Plan
None significant — plan executed as designed across multiple sessions.

## Issues Encountered
- `make pyre` was silently succeeding with 0 files checked — fixed by adding workspace root to search-path and showing summary on terminal
- Pyrefly needed `Sequence` instead of `list` for mutable usage patterns

## Next Phase Readiness
- flext-core foundation is type-clean, ready for Wave 2 (flext-infra + flext-tests)
- All downstream consumers can import from clean flext-core types

---
*Phase: 01-type-system-hardening*
*Completed: 2026-03-23*
