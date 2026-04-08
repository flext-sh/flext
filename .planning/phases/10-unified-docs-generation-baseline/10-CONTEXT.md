# Phase 10: Unified Docs Generation Baseline - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning
**Source:** PRD Express Path (user inline spec)

<domain>
## Phase Boundary

Refactor ALL flext-infra command domains (excluding docs — separate agent) to:
1. Follow modern MRO service facade pattern (flext-cli reference implementation)
2. Create api.py MRO facade composing all service mixins
3. Simplify base.py to thin FlextServiceBase (~30 LOC)
4. Services as thin s orchestrators over u.Infra.* utilities
5. Centralize rope library usage through u.Infra.* (already partially done)
6. pyproject.toml as config SSOT where possible
7. Flat type aliases in c/t/p/m/u with no duplicate declarations
8. ruff + pyrefly clean at ALL times during refactoring

Domains in scope: basemk, check, codegen, deps, github, refactor, release, validate, workspace
Library domains (detectors, gates, rules, transformers) — verify patterns, no structural changes
Docs domain — EXCLUDED (separate agent)

</domain>

<decisions>
## Implementation Decisions

### Architecture Pattern
- Services MUST follow s base from base.py — thin orchestrators only
- Services MUST delegate ALL logic to u.Infra.* utility functions
- No generic helpers that could be reused across modules — everything goes through u.* namespace
- Import private classes directly in _utilities (e.g., `from flext_infra import FlextInfraUtilitiesDocsScope`)

### Config SSOT: pyproject.toml + Minimal JSON
- Maximize information read from pyproject.toml (project metadata, dependencies, package info)
- Use [tool.flext.docs] entries in each project's pyproject.toml for project-specific docs config
- docs/docs_config.json for workspace-level policy that can't live in pyproject.toml (exclusions, audit rules, stale symbols)
- NEVER duplicate what pyproject.toml already provides

### Library Reuse Over Custom Code
- Use mkdocs, mkdocs-material, mkdocstrings, mkdocstrings-python as Python libraries directly
- Use rope library for Python code analysis (public exports, module structure, docstring extraction)
- Do NOT write custom Python code that reimplements what these libraries already do
- Template rendering via existing infrastructure (Jinja2), not custom string builders

### Namespace Patterns (LOCKED)
- c = constants, t = types, p = protocols, m = models, u = utilities — canonical aliases
- Flat type aliases with descriptive prefixes, separated in _constants/*.py, _typings/*.py, etc.
- Zero duplicate declarations across c/t/p/m/u
- Access via `from flext_infra import c, m, t, u` — u provides u.Cli.*and u.Infra.* directly
- NEVER import as `from flext_cli import u as cli_u` — the MRO provides everything

### Docs Generation Phases (LOCKED)
- **generate**: per-project mkdocs.yml, per-project docs/api-reference/generated/*.md, root generated catalog
- **fix**: repair links, TOCs, normalize headers — mechanical only
- **audit**: governance checks (placeholders, stale symbols, missing docstrings, scope violations)
- **build**: mkdocs build for root and every FLEXT project
- **validate**: contract compliance, required paths, SSOT verification

### Project Docs Contract (LOCKED)
- Every governed FLEXT project gets: README.md, docs/index.md, docs/guides/README.md, docs/api-reference/README.md, docs/api-reference/generated/, mkdocs.yml
- Generated pages use mkdocstrings directives (::: package_name), not copied code snippets
- Curated docs must not duplicate generated API surface

### Scope Policy (LOCKED)
- Governed scope: all flext-* projects + flext-infra + flext-tests
- Excluded: algar-oud-mig, gruponos-meltano-native, flexcore, non-project folders
- Project classes: platform, domain, integration, infra, test

### Quality (LOCKED)
- ruff + pyrefly MUST be clean at all times — never defer to later
- Fix errors immediately after each code change, not at the end
- Full test suite must pass

### Claude's Discretion
- Internal decomposition of utility classes (how many files, method organization)
- Exact mkdocstrings handler configuration options
- Order of generation operations within generate phase
- Specific rope API calls for export/docstring extraction
- Template structure for mkdocs.yml generation

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Architecture Governance
- `AGENTS.md` — Supreme engineering law, all sections apply
- `AGENTS.md §2.2` — Facades & Namespaces
- `AGENTS.md §2.5` — Service Facade Pattern (api.py + base.py + services/)
- `AGENTS.md §2.6` — Settings Law
- `AGENTS.md §3.1` — Architecture & Code Structure (200-line cap)
- `AGENTS.md §3.2` — Types & Contracts
- `AGENTS.md §4` — Import Law

### Reference Implementations
- `flext-cli/src/flext_cli/api.py` — MRO facade class pattern
- `flext-cli/src/flext_cli/base.py` — FlextServiceBase pattern
- `flext-cli/src/flext_cli/services/` — Service mixin pattern
- `flext-cli/src/flext_cli/_utilities/` — Private utility import pattern
- `flext-cli/src/flext_cli/constants.py` — Constants facade pattern

### Existing Docs Code (to refactor)
- `flext-infra/src/flext_infra/docs/` — Current docs service layer
- `flext-infra/src/flext_infra/_utilities/docs*.py` — Current docs utilities (10 files, ~2000 LOC)
- `flext-infra/src/flext_infra/_models/docs.py` — Current docs models
- `flext-infra/src/flext_infra/_constants/docs.py` — Current docs constants
- `flext-infra/src/flext_infra/base.py` — FlextInfraServiceBase

### Configuration
- `docs/docs_config.json` — Workspace docs policy config
- `flext-infra/pyproject.toml` — [tool.flext.docs] entries
- `mkdocs.yml` — Root workspace mkdocs config

</canonical_refs>

<specifics>
## Specific Ideas

- Use rope.base.project.Project for Python code analysis instead of raw AST
- mkdocstrings-python handler extracts docstrings at build time — generation only creates directive pages
- pyproject.toml [project] section provides: name, version, description, dependencies
- pyproject.toml [tool.flext.docs] provides: project_class, site_title, module_include, module_exclude
- docs_config.json provides: scope exclusions, audit rules (placeholder terms, stale symbols), build policy
- Every generated file carries ownership marker (AUTO-GENERATED header)
- Generator must not overwrite curated pages
- Audit must fail on: missing public docstrings, stale symbols, placeholder text, scope violations

</specifics>

<deferred>
## Deferred Ideas

- Non-FLEXT project documentation (out of scope)
- Documentation hosting/deployment pipeline
- API versioning in generated docs
- Interactive API playground (Swagger/OpenAPI)

</deferred>

---

*Phase: 10-unified-docs-generation-baseline*
*Context gathered: 2026-04-05 via PRD Express Path*
