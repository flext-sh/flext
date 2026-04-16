# FLEXT Monorepo Hardening & Modernization

## What This Is

A 33-project Python monorepo built on MRO-based namespace composition, DDD/CQRS with a dispatcher-first message bus, and strict Pydantic v2 models. v1.0 shipped production-grade quality: zero type errors across all 33 projects, zero typing shortcuts, zero workarounds, Python 3.13 stdlib modernization, and full migration from Poetry to uv workspaces. The codebase enforces AGENTS.md governance at every layer.

## Core Value

Zero type errors, zero typing shortcuts, zero workarounds — a clean, strict, fully typed Python 3.13 monorepo that enforces AGENTS.md governance at every layer.

## Requirements

### Validated

- ✓ MRO namespace composition (`c, m, t, u, p, r` facades) — existing architecture
- ✓ Pydantic v2 BaseModel validation across domain layers — established pattern
- ✓ `t.*` validation types (290+ annotated-types constraints) — completed refactor
- ✓ `r[T]` Result type for all fallible operations — established pattern
- ✓ `make pyrefly-repo` authoritative repo-wide entrypoint — v1.0
- ✓ **TYPE-01**: Repo-wide pyrefly returns 0 errors (from 4,385 baseline) — v1.0
- ✓ **TYPE-02**: Zero `Any`, `object`, `# type: ignore` in type annotation positions — v1.0
- ✓ **TYPE-03**: Zero `cast()` outside `flext-core/result.py` — v1.0
- ✓ **TYPE-04**: All `__class__` comparisons replaced with `isinstance`/`TypeIs` — v1.0
- ✓ **TYPE-07**: `TypeGuard` → `TypeIs` (PEP 742) across all 33 projects — v1.0
- ✓ **TYPE-08**: All empty container literals annotated at assignment sites — v1.0
- ✓ **ARCH-01**: All public APIs use protocol types (`p.*`) not concrete types — DIP enforced — v1.0
- ✓ **ARCH-02**: `c,m,t,u,p` imported from local namespace root in tests/examples/scripts — v1.0
- ✓ **ARCH-03**: Pydantic v2 `Field()` migrated to `Annotated[X, m.Field(...)]` canonical form — v1.0
- ✓ **ARCH-04**: 6 pure ABCs converted to `@runtime_checkable` Protocol — v1.0
- ✓ **ARCH-05**: 8 template ABCs have Protocol interface extracted — v1.0
- ✓ **ARCH-06**: ~100 inline `TypeAdapter()` instantiations cached as ClassVar/module constants — v1.0
- ✓ **ARCH-07**: 13 mutable `Field(default=[])` replaced with `default_factory=list` — v1.0
- ✓ **ARCH-08**: Type aliases use PEP 695 `type X = ...` form — v1.0
- ✓ **INFRA-01**: `u.Infra.run_cli()` centralizes bootstrap + dispatch + error-to-exit — v1.0
- ✓ **INFRA-02**: `u.Infra.iter_projects()` centralizes project iteration — v1.0
- ✓ **INFRA-03**: `workspace_root` canonical parameter name across all `flext_infra` signatures — v1.0
- ✓ **INFRA-04**: `NamespaceSourceDetector` + auto-fixer in `flext_infra` — v1.0
- ✓ **INFRA-05**: `make pyrefly-repo` policy gate enforces 0 `Any`/`object`/`ignore` violations — v1.0
- ✓ **WA-01**: Zero `try/except ImportError` in production code — v1.0
- ✓ **WA-02**: Zero `model_rebuild()` anywhere — v1.0
- ✓ **WA-03**: Zero bare `except Exception:` — all handlers catch specific exceptions — v1.0
- ✓ **WA-04**: Zero `sys.exit()` outside `__main__.py` files — v1.0
- ✓ **WA-05**: Zero `print()` in production (except documented CLI output services) — v1.0
- ✓ **WA-06**: Zero `subprocess.run()` outside designated subprocess wrapper — v1.0
- ✓ **MOD-01**: `itertools.batched` replaces all custom chunking/batching code — v1.0
- ✓ **MOD-02**: `warnings.deprecated` (PEP 702) replaces custom deprecation framework — v1.0
- ✓ **MOD-03**: 147+ `StrEnum` classes decorated with `@unique` — v1.0
- ✓ **MOD-04**: 70 `Literal[str, ...]` unions convertible to `StrEnum` converted — v1.0
- ✓ **MOD-05**: `defaultdict` replaces hand-rolled grouping patterns — v1.0
- ✓ **MOD-06**: `UserDict`/`UserString` usages replaced with Pydantic `BaseModel` — v1.0
- ✓ **MIG-01**: `flext_infra` extracted as independent repo + git submodule — v1.0
- ✓ **MIG-02**: `flext_tests` extracted as independent repo + git submodule — v1.0
- ✓ **MIG-03**: `flext-core/pyproject.toml` ships only `flext_core` namespace — v1.0
- ✓ **MIG-04**: 33 `pyproject.toml` files converted from Poetry to PEP 621 + uv workspace — v1.0
- ✓ **MIG-05**: Root `uv.lock` unified (replaces 33 `poetry.lock` files) — v1.0
- ✓ **MIG-06**: All `make` targets updated from `poetry run` to `uv run` — v1.0

### Active

*(Next milestone requirements will be defined via `/gsd:new-milestone`)*

### Out of Scope

- Backward compatibility shims — all consumers are internal, break-and-fix-forward
- New feature development — hardening milestone only
- Frontend or UI changes — monorepo is backend/data-pipeline only
- CI/CD changes beyond what Poetry→uv migration requires — separate milestone
- PyPI publication automation — enabled by uv workspaces but post-v1.0
- Polylith `workspace.toml` formal bases/components — deferred

## Context

**Shipped v1.0** — 2026-03-25
- 8 phases, 28 plans, 39 requirements delivered
- 4,385 → 0 pyrefly errors
- Poetry → uv: 33 `poetry.lock` files → 1 `uv.lock`
- `flext_infra` and `flext_tests` extracted as independent submodules
- Zero workarounds in production code

**Next milestone**: Phase 9 — Rope-native refactor engine rewrite (planned)

## Constraints

- **Tooling**: All changes via `make` targets, `ast-grep`, native tools — never direct `git`/`grep`/`find`
- **Typing**: No `Any`, no `object` annotations, no `cast()`, no `# type: ignore` — zero exceptions
- **Freeze policy**: `flext-core/_utilities/*` FROZEN per AGENTS.md §10.2 (except where explicitly unfrozen by operator)
- **Autogenerated files**: `__init__.py` exports are autogenerated — fix generators, never hand-edit
- **Commit protocol**: Stage → commit → `bd sync` → push before ending each session
- **Dependency order**: flext-core → flext-infra → flext-tests → consumers (respect this for all refactors)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Coarse granularity (5 phases → 8 phases) | 25 plans → 8 phases reduces cognitive overhead; 3 gap-closure phases inserted | ✓ Good |
| Sequential execution | Typing changes cascade across projects — parallel causes merge conflicts | ✓ Good |
| Unfreeze `_utilities/*` for §3 compliance | Operator authorized 2026-03-12 — `__class__` + `cast()` are behavioral, not annotation-only | ✓ Good |
| Poetry → uv migration last | Biggest blast radius — do type/arch cleanup first so lock file churn is final | ✓ Good |
| `flext_infra`/`flext_tests` submodule extraction before uv | Submodule structure must be stable before unified workspace lock | ✓ Good |
| cast() in decorators.py eliminated | Widened `_resolve_logger()` param to `tuple[object,...]` — no cast needed when method uses isinstance() internally | ✓ Good |
| Dynamic TypeAdapter accepted as uncacheable | ~7 instances in flext-core use runtime type params — accepted as uncacheable | ✓ Good |
| PEP 695 type aliases mandatory | Test fixtures with old syntax preserved as validator test data only | ✓ Good |
| ProviderConfiguration as BaseModel with extra=allow | Dict-like flexibility preserved without UserDict | ✓ Good |
| BeforeValidator pattern for StrEnum coercion | Strict Pydantic models + StrEnum coercion at field level, not model level | ✓ Good |
| Phase 8 gap closure | 30 bare except + 8 sys.exit() + print() residuals from Phase 3 audit — addressed in dedicated phase | ✓ Good |

---
*Last updated: 2026-03-25 after v1.0 milestone*
