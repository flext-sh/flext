# Requirements — FLEXT Monorepo Hardening & Modernization

*Generated: 2026-03-23 | Source: 25 .sisyphus plans + codebase analysis*

---

## v1 Requirements

### TYPE — Type System Hardening

- [ ] **TYPE-01**: Repo-wide `make pyrefly-repo` returns exit code 0 with 0 errors (from 4,385 baseline)
- [ ] **TYPE-02**: Zero `# type: ignore` annotations in any `.py` file across all 33 projects
- [ ] **TYPE-03**: Zero `typing.Any` imports or annotations across all 33 projects
- [ ] **TYPE-04**: Zero `object` used as a type annotation (parameter, return, field, alias)
- [ ] **TYPE-05**: Zero `cast()` calls outside `flext-core/result.py`
- [ ] **TYPE-06**: Zero `__class__ is` / `__class__ not in` comparisons — all replaced with `isinstance()` or `TypeGuard`/`TypeIs`
- [ ] **TYPE-07**: `TypeGuard` → `TypeIs` (PEP 742) migration in all 12 type-guard functions
- [ ] **TYPE-08**: All empty container literals annotated at their assignment sites

### ARCH — Architecture & SOLID

- [ ] **ARCH-01**: All public API type annotations use protocol types (`p.Context`, `p.DI`, `p.Config`, `p.StructlogLogger`) not concrete types (`FlextContext`, `FlextContainer`, etc.)
- [ ] **ARCH-02**: `c,m,t,u,p` always imported from local namespace root in `tests/`, `examples/`, `scripts/` — never from `flext_core` directly
- [ ] **ARCH-03**: All ~1,551 `Field(...)` usages migrated to `Annotated[X, Field(...)]` canonical Pydantic v2 form
- [ ] **ARCH-04**: 6 pure ABCs converted to `@runtime_checkable` Protocol
- [ ] **ARCH-05**: 8 template ABCs have Protocol interface extracted (keep concrete base)
- [ ] **ARCH-06**: ~100 inline `TypeAdapter()` instantiations cached as `ClassVar`/module constants
- [ ] **ARCH-07**: 13 mutable `Field(default=[])` replaced with `default_factory=list`
- [ ] **ARCH-08**: Type aliases use PEP 695 `type X = ...` form, not `TypeAlias` assignments

### INFRA — Infrastructure Centralization

- [ ] **INFRA-01**: `u.Infra.run_cli()` helper centralizes bootstrap + dispatch + error-to-exit (eliminates 18 duplicate patterns)
- [ ] **INFRA-02**: `u.Infra.iter_projects()` centralizes project iteration (eliminates 13 duplicate `discover_projects()` calls)
- [ ] **INFRA-03**: `workspace_root` is the canonical parameter name across all `flext_infra` signatures (replaces `root`, `project_root`)
- [ ] **INFRA-04**: `NamespaceSourceDetector` + auto-fixer in `flext_infra` — detects and rewrites namespace source violations
- [ ] **INFRA-05**: `make pyrefly-repo` policy gate enforces 0 `Any`/`object`/`ignore` violations (with file+line output)

### WORKAROUND — Workaround Eradication

- [ ] **WA-01**: Zero `try/except ImportError` in production code (`.*/src/**/*.py`)
- [ ] **WA-02**: Zero `model_rebuild()` calls anywhere in the monorepo
- [ ] **WA-03**: Zero bare `except Exception:` — all exception handlers catch specific exception types
- [ ] **WA-04**: Zero `sys.exit()` calls outside `__main__.py` files
- [ ] **WA-05**: Zero `print()` calls in production code (except documented CLI output services)
- [ ] **WA-06**: Zero `subprocess.run()` calls outside the designated subprocess wrapper

### MOD — Python 3.13 Modernization

- [ ] **MOD-01**: `itertools.batched` replaces all custom chunking/batching utility code
- [ ] **MOD-02**: `warnings.deprecated` (PEP 702) replaces custom `FlextUtilitiesDeprecation` framework
- [ ] **MOD-03**: 147+ `StrEnum` classes decorated with `@unique`
- [ ] **MOD-04**: 70 `Literal[str, ...]` unions convertible to `StrEnum` converted
- [ ] **MOD-05**: `defaultdict` replaces hand-rolled grouping patterns
- [ ] **MOD-06**: `UserDict`/`UserString` usages replaced with Pydantic `BaseModel`

### MIG — Package Migration

- [ ] **MIG-01**: `flext_infra` extracted to `https://github.com/flext-sh/flext-infra.git` as independent repo + git submodule
- [ ] **MIG-02**: `flext_tests` extracted to `https://github.com/flext-sh/flext-tests.git` as independent repo + git submodule
- [ ] **MIG-03**: `flext-core/pyproject.toml` ships only `flext_core` namespace
- [ ] **MIG-04**: 33 `pyproject.toml` files converted from Poetry to PEP 621 + uv workspace format
- [ ] **MIG-05**: Root `uv.lock` unified (replaces 33 `poetry.lock` files)
- [ ] **MIG-06**: All `make` targets updated from `poetry run` to `uv run`

---

## v2 Requirements (deferred)

- CI/CD pipeline updated to use `uv` cache strategy (post-migration)
- PyPI publication automation for ~30 packages (enabled by uv workspaces)
- `flext-quality` maintenance scripts typed and clean (secondary to main type hardening)
- Benchmarks added for dispatcher hot-path after TypeAdapter caching (MIG milestone)
- Polylith `workspace.toml` with formal bases/components/projects categorization

---

## Out of Scope

- New feature development — hardening milestone only
- Frontend/UI changes — backend-only monorepo
- Backward compatibility shims — all consumers internal, break-and-fix-forward
- Manual `__init__.py` edits — fix generators, never hand-edit
- Per-project `poetry.lock` preservation — replaced by unified `uv.lock`
- `algar-oud-mig` deep typing cleanup — excluded project, not part of flext-sh org publishing

---

## Traceability

| Requirement | Phase | .sisyphus Plan(s) |
|-------------|-------|-------------------|
| TYPE-01..08 | Phase 1 | pyrefly-repo-hardening, strict-typing-execution-plan, bare-object-elimination, pyright-zero-errors |
| ARCH-01 | Phase 2 | protocol-solid-standardization |
| ARCH-02 | Phase 2 | namespace-source-enforcement |
| ARCH-03..08 | Phase 2 | pydantic-v2-advanced-modernization |
| INFRA-01..05 | Phase 3 | infra-runtime-centralization, namespace-source-enforcement, infra-type-alias-unification, utilities-mro-dedup, centralize-u-utilities, constants-dedup-infra, cli-infra-standardization, flext-core-typing-simplification, flext-core-violations-remediation, flext-infra-mro-base-order-command, flext-infra-typing-census-engine, import-normalization-infra, infra-tier-reorg, typing-protocol-simplification |
| WA-01..06 | Phase 3 | workaround-eradication |
| MOD-01..06 | Phase 4 | python313-datatypes, python313-stdlib-modernization |
| MIG-01..06 | Phase 5 | split-core-packages, polylith-uv-migration |
