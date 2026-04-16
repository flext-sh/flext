# Milestones

## v1.0 FLEXT Monorepo Hardening (Shipped: 2026-03-25)

**Phases completed:** 9 phases, 28 plans, 52 tasks

**Key accomplishments:**

- Fixed make pyre entrypoint, established 0-error baseline, eliminated all typing shortcuts in flext-core foundation
- flext-infra and flext-tests pass all type gates with zero errors — 1 bare object annotation fixed in matchers.py TypeIs guard
- flext-cli already type-clean — 0 pyrefly/pyright errors, 0 typing shortcuts, no code changes needed
- All 34 projects pass pyrefly+pyright with 0 errors — entire repo type-clean, no code changes needed
- TypeGuard→TypeIs already migrated, all TYPE-01 through TYPE-08 requirements verified — Phase 01 complete
- Removed last ABC from s — all flext-core interfaces now use @runtime_checkable Protocol via p.Service
- Replaced concrete type annotations with protocol types (p.Settings, p.Container, p.Logger) in flext-core and 2 consumer projects
- Migrated ~500 m.Field() usages to Annotated[T, m.Field(...)] canonical Pydantic v2 form across 33 projects, fixed 2 mutable defaults, cleaned up redundant m.Field() assignments
- ~45 inline TypeAdapter() instantiations cached as ClassVar/module-level across 22 files in 15 projects, eliminating repeated construction in hot paths
- Migrated 4 remaining TypeAlias assignments to PEP 695 form and normalized ~60 test files to import c,m,t,u,p from local namespace root
- Added iter_projects() and emit() to CLI facade, normalized all bare root: Path to semantic variants (workspace_root, repo_root, scan_root) across 9 flext-infra files
- Result:
- Removed all model_rebuild() calls and routed 5 direct subprocess.run invocations through the flext-cli runtime via `u.Cli.*`, with input_data support
- One-liner:
- One-liner:
- Result: No changes needed.
- @unique enforced on all 297 StrEnum classes; 65+ redundant Literal[str,...] aliases removed/converted across 17 projects
- 3 foundation projects (flext-core, flext-infra, flext-tests) converted from Poetry to hatchling build backend; modernizer updated to validate hatchling
- All 34 pyproject.toml files converted to hatchling, unified uv.lock generated, 34 poetry.lock files removed
- All Poetry references removed from base.mk, root Makefile, CI workflows, and .envrc — full uv hard-cut complete
- Last TypeGuard import replaced with TypeIs (PEP 742) in flext-cli/api.py — zero TypeGuard in monorepo src/
- BeforeValidator pattern fixes StrEnum+strict Pydantic coercion across 5 fields, deprecation framework stubbed per FROZEN policy, UserDict/UserString confirmed absent
- Added OutputBackend inner class to FlextInfraUtilitiesOutput, fixing 2 test collection errors and enabling instance-based output testing
- Tests fixed (26 occurrences across 10 files):
- 1. [Rule 2 - Scope clarification] print() calls were in docstrings, not executable code

---
