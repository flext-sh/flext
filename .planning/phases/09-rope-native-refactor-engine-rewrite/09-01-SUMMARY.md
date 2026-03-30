---
phase: 09-rope-native-refactor-engine-rewrite
plan: "01"
subsystem: infra
tags: [rope, libcst, refactor, engine, hooks]

requires: []
provides:
  - RopeProject import and lazy init on FlextInfraRefactorEngine
  - _init_rope_project with monorepo-rooted Project (ropefolder=None, save_objectdb=False)
  - rope_project property
  - _run_rope_pre_hooks / _run_rope_post_hooks stub call sites
  - Wave 0 import stubs confirming rope importability
affects: [09-02, 09-03]

tech-stack:
  added: [rope>=1.14.0,<2.0.0 (explicit uv add)]
  patterns:
    - Direct rope import (from rope.base.project import Project as RopeProject)
    - Hook stubs use del path, dry_run to satisfy pyright without ARG noqa
    - monorepo-rooted Project covers all flext-*/src via source_folders discovery

key-files:
  created:
    - flext-infra/tests/refactor/__init__.py
    - flext-infra/tests/refactor/test_rope_stubs.py
    - flext-infra/tests/refactor/test_rope_project.py
  modified:
    - flext-infra/src/flext_infra/refactor/engine.py

key-decisions:
  - "ropefolder=None — no .ropeproject disk artifact created"
  - "save_objectdb=False — no persistent object db"
  - "Hook stubs return [] — Plan 02 wires actual transformer migrations"
  - "pre_hooks called before refactor_files in refactor_project"
  - "pre_hooks called once before project loop in refactor_workspace; post_hooks once after"
  - "uv add rope>=1.14.0,<2.0.0 normalizes pyproject.toml from Poetry to PEP 508 syntax"

patterns-established:
  - "Rope stubs: del unused_param to satisfy pyright without noqa"
  - "source_folders: sorted(str(p/src) for p in workspace.iterdir() if p.name.startswith('flext-') and (p/src).is_dir())"

requirements-completed: [ROPE-01, ROPE-05, ROPE-06]

duration: 30min
completed: 2026-03-25
---

# Phase 09-01: Rope Project init + hook infrastructure Summary

**rope Project lazy init and pre/post hook call sites on FlextInfraRefactorEngine — 15 tests passing, 769 logical LOC (under 800 gate)**

## Performance

- **Duration:** ~30 min
- **Completed:** 2026-03-25
- **Tasks:** 2 (Wave 0 stubs + Task 1 implementation)
- **Files modified:** 4

## Accomplishments

- Added `from rope.base.project import Project as RopeProject` direct import (no wrapper layer)
- `_init_rope_project(workspace_root)` discovers all `flext-*/src` dirs, creates monorepo-rooted Project with zero disk artifacts
- `rope_project` property returns `None` before init, `RopeProject` after
- `_run_rope_pre_hooks` / `_run_rope_post_hooks` stubs wired into `refactor_project` and `refactor_workspace` call sites
- Wave 0 import stubs confirm rope importability (3 tests)
- 12 additional tests cover init, property, hook ordering
- `uv add rope>=1.14.0,<2.0.0` explicit in flext-infra pyproject.toml

## Files Created/Modified

- `flext-infra/tests/refactor/test_rope_stubs.py` — Wave 0: 3 import tests
- `flext-infra/tests/refactor/test_rope_project.py` — 12 tests: init, property, stubs, ordering
- `flext-infra/tests/refactor/__init__.py` — package init
- `flext-infra/src/flext_infra/refactor/engine.py` — rope import + `_rope_project` attr + 4 new methods + hook call sites

## Decisions Made

- `del path, dry_run` in hook stubs instead of `# noqa: ARG002` — satisfies pyright without suppression comments
- Test file at `tests/refactor/test_rope_project.py` (not `tests/test_infra_refactor_rope_project.py`) — matches existing `tests/refactor/` directory structure
- `uv add` normalized Poetry `rope (>=1.14.0,<2.0.0)` to PEP 508 `rope>=1.14.0,<2.0.0`

## Deviations from Plan

- Plan specified `tests/test_infra_refactor_rope_project.py` — actual file is `tests/refactor/test_rope_project.py` (pre-existing directory structure)
- `test_rope_stubs.py` initially used in-function imports (PLC0415 ruff violation) — moved to top-level

## Issues Encountered

- `from flext_infr import FlextInfraRefactorEngine` typo in pre-generated test file — fixed to `from flext_infra import FlextInfraRefactorEngine`

## Next Phase Readiness

- Plan 02 can now wire `symbol_propagator`, `mro_reference_rewriter`, `nested_class_propagation` into `_run_rope_pre_hooks`
- Engine is ready to hold a `RopeProject` instance for Plan 02 transformer migrations

---
*Phase: 09-rope-native-refactor-engine-rewrite*
*Completed: 2026-03-25*
