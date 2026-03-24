# Roadmap: FLEXT Monorepo Hardening & Modernization

## Overview

This roadmap sequences 39 requirements across 5 phases to drive a 33-project Python monorepo from 4,385 pyrefly type errors to zero — achieving production-grade quality through strict typing, clean architecture, infrastructure centralization, Python 3.13 modernization, and a final package migration to uv workspaces. Each phase clears the ground for the next: type safety first, then architecture, then runtime consistency, then stdlib modernization, then package restructuring.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Type System Hardening** - Eliminate all 4,385 pyrefly errors and every `Any`/`object`/`cast`/`ignore` shortcut
- [ ] **Phase 2: Architecture & SOLID** - Enforce DIP via protocols, canonicalize Pydantic v2, adopt PEP 695 type aliases
- [ ] **Phase 3: Infrastructure Centralization** - Centralize runtime helpers, eradicate all workarounds and antipatterns
- [ ] **Phase 4: Python 3.13 Modernization** - Replace custom code with stdlib (`TypeIs`, `StrEnum`, `batched`, etc.)
- [ ] **Phase 5: Package Migration** - Extract submodules, convert 33 projects from Poetry to uv workspaces

## Phase Details

### Phase 1: Type System Hardening
**Goal**: The monorepo type-checks clean — `make pyre` returns 0 errors and no typing shortcuts remain anywhere
**Depends on**: Nothing (Wave 0 already complete: pyrefly entrypoint, legacy artifacts, 27 test fixes)
**Requirements**: TYPE-01, TYPE-02, TYPE-03, TYPE-04, TYPE-05, TYPE-06, TYPE-07, TYPE-08
**Success Criteria** (what must be TRUE):
  1. `make pyre` exits 0 with 0 errors across all 33 projects (down from 4,385 baseline)
  2. Zero `# type: ignore`, `typing.Any`, or `object` in any annotation position across all `.py` files
  3. Zero `cast()` calls outside `flext-core/result.py`
  4. Zero `__class__ is` / `__class__ not in` comparisons — all replaced with `isinstance()` or `TypeIs`
  5. All `TypeGuard` usages (12 functions) migrated to `TypeIs` (PEP 742) and all empty container literals annotated
**Plans**: 5 plans

Plans:
- [x] 01-01-PLAN.md — Wave 1: Fix make pyre entrypoint + clean flext-core (foundation)
- [x] 01-02-PLAN.md — Wave 2: Clean flext-infra + flext-tests (infrastructure)
- [x] 01-03-PLAN.md — Wave 3: Clean flext-cli (largest consumer, solo)
- [x] 01-04-PLAN.md — Wave 4: Clean remaining ~27 consumer projects
- [x] 01-05-PLAN.md — Micro-plan: TypeGuard->TypeIs migration + empty container annotation

### Phase 2: Architecture & SOLID
**Goal**: Public APIs speak in protocols, Pydantic fields use canonical form, and type aliases follow PEP 695 — DIP enforced across all 33 projects
**Depends on**: Phase 1
**Requirements**: ARCH-01, ARCH-02, ARCH-03, ARCH-04, ARCH-05, ARCH-06, ARCH-07, ARCH-08
**Success Criteria** (what must be TRUE):
  1. All public API signatures reference `p.*` protocol types (`p.Context`, `p.DI`, `p.Config`, `p.StructlogLogger`) — no concrete class leakage
  2. `c,m,t,u,p` are never imported from `flext_core` directly in `tests/`, `examples/`, or `scripts/` — always from local namespace root
  3. All ~1,551 `Field(...)` usages use `Annotated[X, Field(...)]` canonical Pydantic v2 form
  4. 6 pure ABCs converted to `@runtime_checkable` Protocol; 8 template ABCs have Protocol interface extracted
  5. `TypeAdapter()` instantiations cached as `ClassVar`/module constants; mutable `Field(default=[])` replaced with `default_factory=list`; type aliases use PEP 695 `type X = ...`
**Plans**: 5 plans

Plans:
- [x] 02-01-PLAN.md — issubclass() prereq + ABC-to-Protocol conversion in flext-core
- [x] 02-02-PLAN.md — DIP enforcement: concrete->protocol type substitution across all projects
- [ ] 02-03-PLAN.md — Field()->Annotated migration + mutable defaults fix (all 33 projects)
- [ ] 02-04-PLAN.md — TypeAdapter caching (~100 inline instances)
- [ ] 02-05-PLAN.md — PEP 695 type aliases + import normalization

### Phase 3: Infrastructure Centralization
**Goal**: Runtime helpers are centralized with zero duplication, and every antipattern (`try/except ImportError`, `model_rebuild()`, bare `except`, `sys.exit`, `print`, subprocess sprawl) is eradicated from production code
**Depends on**: Phase 1, Phase 2
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, WA-01, WA-02, WA-03, WA-04, WA-05, WA-06
**Success Criteria** (what must be TRUE):
  1. `u.Infra.run_cli()` and `u.Infra.iter_projects()` are the single implementations — 18 duplicate CLI bootstrap patterns and 13 `discover_projects()` clones are gone
  2. `workspace_root` is the canonical parameter name across all `flext_infra` signatures — no `root` or `project_root` variants remain
  3. `NamespaceSourceDetector` is live in `flext_infra` and passes its own test suite
  4. `make pyre` policy gate enforces 0 `Any`/`object`/`ignore` violations with file+line output on failure
  5. Zero `try/except ImportError`, `model_rebuild()`, bare `except Exception:`, `sys.exit()` outside `__main__.py`, `print()` in production, and `subprocess.run()` outside the designated wrapper — across all 33 projects
**Plans**: TBD

### Phase 4: Python 3.13 Modernization
**Goal**: Custom implementations of stdlib capabilities are deleted and replaced with Python 3.13 builtins and standard library modules
**Depends on**: Phase 3
**Requirements**: MOD-01, MOD-02, MOD-03, MOD-04, MOD-05, MOD-06
**Success Criteria** (what must be TRUE):
  1. All custom chunking/batching utilities replaced with `itertools.batched`; all custom deprecation framework replaced with `warnings.deprecated` (PEP 702)
  2. All 147+ `StrEnum` subclasses are decorated with `@unique`; all 70 convertible `Literal[str, ...]` unions are `StrEnum`
  3. All hand-rolled grouping patterns use `defaultdict`; all `UserDict`/`UserString` usages replaced with Pydantic `BaseModel`
**Plans**: TBD

### Phase 5: Package Migration
**Goal**: `flext_infra` and `flext_tests` live in independent repos as submodules, `flext-core` ships only `flext_core`, and all 33 projects run on a unified `uv.lock`
**Depends on**: Phase 4
**Requirements**: MIG-01, MIG-02, MIG-03, MIG-04, MIG-05, MIG-06
**Success Criteria** (what must be TRUE):
  1. `flext_infra` and `flext_tests` each have their own GitHub repo and are consumed as git submodules — no source files remain in `flext-core/src/` for these namespaces
  2. `flext-core/pyproject.toml` declares only the `flext_core` package (no `flext_infra`, `flext_tests`)
  3. All 33 `pyproject.toml` files use PEP 621 + uv workspace format — no `poetry` sections remain
  4. A single root `uv.lock` replaces all 33 individual `poetry.lock` files
  5. All `make` targets invoke `uv run` instead of `poetry run` — CI passes without Poetry installed
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Type System Hardening | 5/5 | Complete    |  |
| 2. Architecture & SOLID | 0/5 | Planned | - |
| 3. Infrastructure Centralization | 0/TBD | Not started | - |
| 4. Python 3.13 Modernization | 0/TBD | Not started | - |
| 5. Package Migration | 0/TBD | Not started | - |
