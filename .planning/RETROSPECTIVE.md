# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

---

## Milestone: v1.0 — FLEXT Monorepo Hardening

**Shipped:** 2026-03-25
**Phases:** 8 | **Plans:** 28

### What Was Built

- **Zero type errors**: 4,385 pyrefly errors → 0 across all 33 projects, strict Pydantic v2 canonical form, PEP 695 type aliases
- **Protocol-first APIs**: 6 pure ABCs → `@runtime_checkable` Protocol, concrete types replaced by `p.*` protocol types in all public APIs
- **Centralized infrastructure**: `u.Infra.run_cli()` and `u.Infra.iter_projects()` replace 18 duplicated CLI bootstrap patterns and 13 `discover_projects()` clones
- **Zero workarounds**: No `try/except ImportError`, no `model_rebuild()`, no bare `except Exception:`, no `sys.exit()` outside `__main__.py`, no `print()` in production
- **Python 3.13 stdlib**: `itertools.batched`, `warnings.deprecated` (PEP 702), `@unique` StrEnum, `defaultdict` — all custom re-implementations replaced
- **uv workspace**: 33 `poetry.lock` files → 1 `uv.lock`; `flext_infra` and `flext_tests` extracted as independent submodules

### What Worked

- **Sequential wave execution**: Typing changes cascade across projects — sequential execution prevented merge conflicts in all 28 plans
- **Gap-closure phases**: Inserting Phases 6, 7, 8 for audit-found gaps was the right call — prevented "shipped but not clean" state
- **coarse phase granularity**: 25 `.sisyphus` plans → 8 phases was navigable; finer granularity would have increased overhead without benefit
- **make pyre policy gate**: Adding `Any`/`object`/`ignore` enforcement to the gate caught regressions automatically

### What Was Inefficient

- **Audit gaps found post-Phase 3**: WA-03, WA-04, WA-05 residuals required a dedicated Phase 8 — earlier end-to-end scanning would have caught these in Phase 3
- **ROADMAP.md started stale**: Initial progress table didn't reflect actual completion status (Phases 1-5 shown as planned when some were already done)
- **Submodule extraction scope**: `flext_infra`/`flext_tests` extraction was Phase 5 — in hindsight, should have been earlier since later phases depended on the submodule layout

### Patterns Established

- **Gap-closure phases**: Add decimal or numbered gap phases after milestone audit rather than retroactively marking requirements partial
- **BeforeValidator for StrEnum coercion**: On strict Pydantic models, apply coercion at field level via `BeforeValidator`, not model level
- **`workspace_root` canonical parameter**: Single parameter name across all `flext_infra` signatures eliminates cognitive load

### Key Lessons

1. **Audit early, close gaps before claiming done**: Run `/gsd:audit-milestone` after Phase 3 or midpoint — don't wait for all phases to surface residuals
2. **Sequential execution is correct for cascade changes**: Typing/import changes in 33 interdependent projects cannot safely parallelize
3. **Policy gates prevent regression**: `make pyre` with `Any`/`object`/`ignore` enforcement gate is more reliable than code review for these invariants
4. **Wave-zero work matters**: The historical baseline (4,385 errors) was already stale — actual starting point was 29 errors. Document baselines at session start, not from months-old data

### Cost Observations

- Sessions: multiple over ~2-3 days of intensive work
- Notable: Most plans completed in 1-6 minutes; Phase 2 Plan 03 (Field migration, 80 files) took 20+ minutes — bulk AST transforms are the bottleneck

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Key Change |
|-----------|--------|-------|------------|
| v1.0 | 8 | 28 | First milestone — established wave execution, gap-closure pattern |

### Cumulative Quality

| Milestone | Pyrefly Errors | Pyright Errors | Ruff Errors |
|-----------|----------------|----------------|-------------|
| v1.0 | 0 | 0 (src/) | 0 |

### Top Lessons (Verified Across Milestones)

1. Sequential wave execution is mandatory for cross-cutting refactors in large monorepos
2. Audit midpoint, not just at the end — residuals compound if left to gap-closure phases
