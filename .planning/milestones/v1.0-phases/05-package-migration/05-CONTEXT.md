# Phase 5: Package Migration - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate the 33-project Python monorepo from Poetry to uv workspace: convert all pyproject.toml files to PEP 621 + hatchling, unify lock files into a single root uv.lock, replace all `poetry install` with `uv sync` in Makefiles and CI, and validate that flext-infra/flext-tests submodule extraction is complete.

</domain>

<decisions>
## Implementation Decisions

### Submodule Extraction (MIG-01/02/03)

- **D-01:** Keep current git repo strategy as-is — one repo per namespace, submodules already in place. No history extraction or repo restructuring needed.
- **D-02:** Validate that imports resolve correctly across all 33 consumers and CI checks out submodules properly.
- **D-03:** Replace `@ file:////flext-infra` dependency syntax with bare workspace member names once uv workspace is wired.

### pyproject.toml Conversion (MIG-04)

- **D-04:** Incremental project-by-project conversion following dependency order (flext-core → flext-infra → flext-tests → consumers). Easier rollback per project.
- **D-05:** Build backend: `hatchling` replaces `poetry.core.masonry.api` across all 33 projects.
- **D-06:** Dev dependencies standardized on `[dependency-groups]` (PEP 735, uv-native). Collapse existing mixed `[dependency-groups]` + `[project.optional-dependencies]` patterns.

### Lock File Unification (MIG-05)

- **D-07:** Pure uv workspace — single root `uv.lock` with all members declared under `[tool.uv.workspace]`.
- **D-08:** Delete all per-project `poetry.lock` files after successful `uv lock` resolution.
- **D-09:** Run `uv lock --dry-run` before committing to surface cross-project dependency conflicts (Singer SDK / dbt / FastAPI chains).

### Make Target & CI Migration (MIG-06)

- **D-10:** Hard-cut to uv — replace `poetry install --all-extras --all-groups` with `uv sync` in all Makefiles.
- **D-11:** Replace `snok/install-poetry` with `astral-sh/setup-uv` in CI workflows (ci.yml, release.yml).
- **D-12:** Replace `poetry run pre-commit install` with direct `pre-commit install` (already in venv PATH).
- **D-13:** Clean up `.envrc` POETRY_VIRTUALENVS_* env vars — no longer needed with uv.

### Claude's Discretion

- Sequencing of incremental project conversion (which leaf projects first)
- Handling of `flext_infra.deps.modernizer` during migration (may need manual bootstrap)
- Specific `[tool.uv.workspace]` member list syntax and grouping
- Error handling strategy for `uv lock` resolution conflicts

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Build Configuration

- `pyproject.toml` — Root workspace manifest (add `[tool.uv.workspace]` here)
- `base.mk` — Shared Makefile patterns for all projects (replace POETRY variable)
- `.envrc` — direnv configuration (remove Poetry env vars, validate uv setup)
- `flext-core/pyproject.toml` — Core package manifest (first conversion target)
- `flext-infra/pyproject.toml` — Infrastructure package (modernizer lives here)

### CI/CD

- `.github/workflows/ci.yml` — CI pipeline (swap poetry install → uv sync)
- `.github/workflows/release.yml` — Release pipeline (swap poetry → uv)

### Infrastructure Tooling

- `flext-infra/src/flext_infra/deps/` — Dependency modernizer that manages [MANAGED] sections
- `.gitmodules` — Submodule configuration (already correct)

### Project Governance

- `AGENTS.md` — Dependency order: flext-core → flext-infra → flext-tests → consumers

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `flext_infra.deps.modernizer` — Manages [MANAGED] sections in pyproject.toml. Must be updated to emit hatchling build backend instead of poetry.core.masonry.api.
- Root `uv.lock` — Already exists (Python 3.13 pinned) but covers only root package, not workspace members.

### Established Patterns

- `[MANAGED]` / `[CUSTOM]` comment protocol in pyproject.toml — modernizer enforces managed sections, projects extend custom sections.
- All quality tools (ruff, pyrefly, pyright, pytest) already run via activated venv PATH, not `poetry run`.

### Integration Points

- `base.mk` POETRY variable (line 93) — defined but unused for `run`; needs removal.
- Root `Makefile` `POETRY_BIN` — used for `poetry -C <proj> install` setup loop.
- Per-project `Makefile` bootstrap targets — `poetry install --all-extras --all-groups`.
- `.envrc` — Creates venv via uv but keeps Poetry coexistence flags.

</code_context>

<specifics>
## Specific Ideas

- Run `uv lock --dry-run` early to surface cross-project dependency conflicts before committing to migration.
- Bootstrap sequence: manually convert flext-infra pyproject.toml first since modernizer lives there.
- Dependency order for incremental conversion: flext-core → flext-infra → flext-tests → leaf consumers.

</specifics>

<deferred>
## Deferred Ideas

- PyPI publication automation for ~30 packages (v2 requirement, enabled by uv workspaces)
- CI/CD uv cache strategy optimization (v2 requirement)
- Polylith `workspace.toml` with formal bases/components/projects categorization (v2 requirement)

</deferred>

---

*Phase: 05-package-migration*
*Context gathered: 2026-03-24*
