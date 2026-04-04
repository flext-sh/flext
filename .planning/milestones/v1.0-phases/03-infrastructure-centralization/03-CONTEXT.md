# Phase 3: Infrastructure Centralization - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Centralize runtime helpers with zero duplication and eradicate every workaround antipattern (`try/except ImportError`, `model_rebuild()`, bare `except`, `sys.exit`, `print`, subprocess sprawl) from production code across all 33 projects.

Two work streams:
1. **INFRA (01-05)**: Centralize `u.Infra.run_cli()`, `u.Infra.iter_projects()`, normalize `workspace_root`, build `NamespaceSourceDetector`, enforce pyrefly policy gate
2. **WA (01-06)**: Eradicate 6 categories of workarounds from production code

</domain>

<decisions>
## Implementation Decisions

### Execution ordering
- **D-01:** INFRA stream first (01→05), then WA stream (01→06). Rationale: centralized helpers (`run_cli`, `iter_projects`) must exist before workaround fixes can use them.
- **D-02:** Within INFRA: foundation utilities first (run_cli, iter_projects), then normalization (workspace_root), then new tooling (NamespaceSourceDetector), then policy gate.
- **D-03:** Within WA: dependency order — flext-core → flext-infra → flext-tests → consumers. Each workaround category can be swept across all projects in one plan.

### CLI bootstrap centralization (INFRA-01, INFRA-02)
- **D-04:** `u.Infra.run_cli(main_fn)` centralizes: structlog init, argparse construction, dispatch, exception-to-exit-code. Eliminates 18 duplicate bootstrap patterns.
- **D-05:** `u.Infra.iter_projects(cli)` centralizes project discovery + filtering + iteration. Eliminates 13 `discover_projects()` clones.
- **D-06:** CLI args standardized: `--workspace PATH`, `--dry-run`/`--apply` (mutually exclusive), `--format json|text`, `--check`, `--projects NAME`. Typed resolution via Pydantic model, not loose tuples.
- **D-07:** Fix known bug: `release/__main__.py:143` has `dry_run=cli.apply` (semantically inverted).

### Parameter normalization (INFRA-03)
- **D-08:** `workspace_root` is the canonical parameter name. Kill all `root`, `project_root` variants across all `flext_infra` signatures.

### NamespaceSourceDetector (INFRA-04)
- **D-09:** New class in `flext_infra` — detects and rewrites namespace source violations. Must pass its own test suite.

### Policy gate (INFRA-05)
- **D-10:** `make pyrefly-repo` enforces 0 `Any`/`object`/`ignore` violations with file+line output on failure.

### Workaround scope definitions
- **D-11:** `try/except ImportError` (WA-01): Replace with `importlib.util.find_spec()` feature flags at module level. Zero in production `src/`.
- **D-12:** `model_rebuild()` (WA-02): Zero everywhere. Already 0 in production (only tests). Remove from tests too.
- **D-13:** `bare except Exception:` (WA-03): Replace with specific exception types per domain. ~68 instances across 15+ files.
- **D-14:** `sys.exit()` (WA-04): Zero outside `__main__.py`. ~8 instances to fix — propagate errors up to `__main__` for exit handling.
- **D-15:** `print()` (WA-05): Zero in production except documented CLI output services. ~4 instances in 3 files. Replace with `FlextLogger`.
- **D-16:** `subprocess.run()` (WA-06): Zero direct calls outside designated wrapper. ~76 instances, 4 files in prod. Route through `u.Infra.subprocess_run()`.

### Claude's Discretion
- Internal decomposition of centralized utilities (`run_cli`, `iter_projects`) — implementation approach is flexible
- Whether to batch WA categories into one plan per category or per project
- Exact exception type hierarchy for WA-03 replacements
- NamespaceSourceDetector internal architecture

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Infrastructure centralization
- `.sisyphus/plans/infra-runtime-centralization.md` — Detailed audit of 7 duplication categories, task breakdown, verification strategy
- `.sisyphus/plans/cli-infra-standardization.md` — CLI argument centralization plan, standardized parser design
- `.sisyphus/plans/centralize-u-utilities.md` — Utilities MRO dedup plan

### Workaround eradication
- `.sisyphus/plans/workaround-eradication.md` — Root cause matrix (10 RCs), violation counts, fix patterns per category
- `.sisyphus/notepads/workaround-eradication/decisions.md` — Prior decisions from workaround analysis
- `.sisyphus/notepads/workaround-eradication/learnings.md` — Learnings from prior workaround work

### Parameter normalization
- `.sisyphus/plans/import-normalization-infra.md` — Import and parameter normalization across flext-infra
- `.sisyphus/plans/infra-tier-reorg.md` — Infrastructure tier reorganization

### Namespace enforcement
- `.sisyphus/plans/namespace-source-enforcement.md` — NamespaceSourceDetector design and enforcement plan

### Project governance
- `AGENTS.md` — Canonical rules, architecture layers, code conventions
- `.planning/REQUIREMENTS.md` — INFRA-01 through INFRA-05, WA-01 through WA-06 requirements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `flext-infra/src/flext_infra/refactor/_utilities.py` — Has `create_refactor_parser()` and `resolve_workspace_args()` — prototype for centralized CLI builder
- `flext-core/src/flext_core/_utilities/` — Established MRO utility pattern for `u.Infra.*` namespace
- `flext-infra/src/flext_infra/transformers/` — Existing CST visitors for code transformation (reuse for NamespaceSourceDetector)

### Established Patterns
- MRO namespace composition: all utilities via `u.Infra.*` facade
- Result-oriented error handling: `r[T]` for all fallible operations
- CLI entry points: 11 `__main__.py` files in flext-infra subpackages

### Integration Points
- All 11 `__main__.py` entry points consume centralized CLI helpers
- `make pyrefly-repo` Makefile target needs policy gate enhancement
- `u.Infra` facade class needs new method composition via MRO

</code_context>

<specifics>
## Specific Ideas

No specific requirements — implementation follows existing sisyphus plans and established codebase patterns.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-infrastructure-centralization*
*Context gathered: 2026-03-24*
