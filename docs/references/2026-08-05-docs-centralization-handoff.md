# Handoff — Docs centralization fleet

**Date:** 2026-08-05  
**Plan:** [docs_centralization_fleet_200d2651](file:///home/marlonsc/.cursor/plans/docs_centralization_fleet_200d2651.plan.md)  
**Bead:** `mro-nxqp` (status: deferred; parent program `mro-z89e` / `mro-1o6t`)  
**Engine owner:** `flext-infra` only — no parallel docs tooling

## Outcome (resume contract)

Any next agent must be able to:

1. Land remaining uncommitted engine/config deltas on `flext-infra` `0.12.0-dev`
2. Clear residual layout noise (`__pycache__` reviews) without re-relocating product docs
3. Drive curated `make docs WHAT=audit,validate,build` to green per tree
4. Commit/push consumers with scoped paths after flext-infra tip is published

## Locked decisions (do not reopen)

| Decision | Value |
| --- | --- |
| Root allowlist | `layout.canonical_root_files` only |
| Exceptions | `layout.project_overrides.<project>.keep_root_files` / `ignore_globs` only |
| Specials | `.agents/**` (dotdir skip); `data/` (`special_root_dirs`); `external-docs/` (`reference_root_dirs` ≈ `docs/references`) |
| Cross-repo links | Absolute GitHub URLs; branch from `make.docs.github_repos` |
| Branch pins | flext `0.12.0-dev`; datacosmos `develop` (provider SSOT — **not** local `dev` checkout name); invest `main` |
| cosmos-main MkDocs | Keep both `mkdocs.yml` (generated) and `mkdocs.yaml` (product); build both |

## Done (evidenced)

### Engine (`flext-infra`)

- Layout models: `keep_root_files`, `ignore_globs`, `special_root_dirs`, `reference_root_dirs` in [`_models/layout.py`](../../flext-infra/src/flext_infra/_models/layout.py)
- Plan: override resolver (incl. `.ai-hub` → `ai-hub`), ignore/specials, docs collision archive in [`codegen/_layout_plan.py`](../../flext-infra/src/flext_infra/codegen/_layout_plan.py)
- GitHub link policy: [`_utilities/_docs_github_links.py`](../../flext-infra/src/flext_infra/_utilities/_docs_github_links.py) + wire in `docs_audit` / `docs_fix`
- Dual MkDocs build: `docs_mkdocs_config_files` in [`_utilities/docs_build.py`](../../flext-infra/src/flext_infra/_utilities/docs_build.py)
- SSOT: `make.docs.github_repos` + layout specials/overrides in [`config/codegen.yaml`](../../flext-infra/config/codegen.yaml)
- Standards: [`docs/standards/documentation.md`](../standards/documentation.md), [`docs/standards/link-management.md`](../standards/link-management.md)
- Tests (2026-08-05): `27 passed` — `layout_tests.py` + `auditor_links_tests.py`

### Relocate / consumers

| Tree | Layout dry-run (2026-08-05) | Notes |
| --- | --- | --- |
| `~/flext` (31 members) | **6 actionable** — all `__pycache__` reviews/archives | Product docs relocated earlier (~389 applies) |
| `~/.ai-hub` | 0 actionable | keep/ignore overrides; skills/rules untouched |
| `~/cosmos-docgen` | canonical | `authoring/` → `docs/authoring`; `data/` skipped |
| `~/cosmos-main` | canonical (apps) | `docs-finais` → `cosmos/inventory/docs/docs-finais` |
| `~/invest` | canonical | `make docs WHAT=audit` works; WARN issues remain |

### Invest `make docs`

- Explicit `docs` target in [`invest/Makefile`](file:///home/marlonsc/invest/Makefile)
- Dispatch scripts under `invest/scripts/docs/{all,generate,fix,audit,build,validate}.py`
- Uses flext `.venv` + `PYTHONPATH` into flext-infra; `.markdownlint.json` + `exclude_docs` for `external-docs/**`

### Artifacts

- Ledger: [`docs/references/docs-centralization-ledger.md`](docs-centralization-ledger.md) (+ `.json`)
- Evidence: `.reports/docs/cross-repo-github-map.md`, `.reports/docs/layout-fixed-point.md`

## Not done / honest gaps

1. **Landing incomplete** — flext-infra still dirty at least on `config/codegen.yaml` and `_models/config.py`; member/consumer trees have uncommitted relocate/fix churn; **no coherent commit/push cycle** for this program.
2. **Layout not fixed-point on flext** — 6 actionable `__pycache__` findings (ephemeral; should be ignored, not archived). Do **not** re-add `__pycache__` to `archive_names`.
3. **`make docs` not fleet-green** — audit returns WARN (issues>0); validate previously FAIL on root required-file contract when scoping wrong; full `build --strict` not claimed green.
4. **`mro-nxqp` DoD** still open for absorbed beads (markdown-docs reactivation, BEARTYPE, etc.) — docs centralization is only one slice.
5. **ai-hub local branch is `dev`** while link pin is `develop` — correct for GitHub URLs; local checkout may diverge until consumer syncs.
6. **Ledger JSON may be stale** relative to post-relocate trees — regenerate before closing.

## Exact next actions (ordered)

```bash
# 0) Work only from flext root (not cosmos-charts cwd — beads MCP fails there)
cd /home/marlonsc/flext
bd update mro-nxqp --claim

# 1) Ignore ephemeral __pycache__ at project roots (layout SSOT)
#    Add to layout.ignore via special/artifact policy OR root ignore_globs fleet-wide
#    Prove: make/codegen layout --dry-run → 0 actionable

PYTHONPATH=flext-infra/src:flext-core/src:flext-cli/src \
  .venv/bin/python -m flext_infra codegen layout --dry-run | tail -5

# 2) Scoped engine gates
make test PROJECT=flext-infra MATCH='layout_tests or auditor_links'
make check PROJECT=flext-infra CHECK_GATES=lint,format,pyrefly

# 3) Land flext-infra first (scoped add — never git add -A)
#    Paths: config/codegen.yaml, src/flext_infra/_models/{layout,config}.py,
#    codegen/_layout_plan.py, _utilities/_docs_github_links.py, docs_*.py,
#    tests/unit/codegen/layout_tests.py, tests/unit/docs/auditor_links_tests.py

# 4) Per-consumer docs drain (one tree at a time)
make docs WHAT=fix APPLY=Y PROJECT=flext-core
make docs WHAT=audit PROJECT=flext-core
make docs WHAT=validate PROJECT=flext-core
make docs WHAT=build PROJECT=flext-core
# then ai-hub / cosmos-docgen / cosmos-main / invest analogously

# 5) Refresh ledger + evidence; comment on mro-nxqp; only then close DoD items
```

## Resume checklist

- [ ] Layout flext dry-run: `0 actionable`
- [ ] flext-infra layout/docs tests green
- [ ] flext-infra commit + FF push on `0.12.0-dev`
- [ ] Member gitlinks advanced after member docs commits
- [ ] Each of five roots: `docs audit/validate/build` exit 0 (or budgeted WARNs with bead note)
- [ ] `mro-nxqp` notes updated with SHAs; centralization slice closed or child bead filed for content drain

## Stop conditions

- Stop if FF push rejected (report local vs remote SHAs; no rebase/force).
- Stop if layout wants to archive/move `.agents`, `data/*`, or `external-docs` content.
- Stop if tempted to bypass `make docs` with raw mkdocs/rumdl.

## Authority

Newest operator instruction > Beads > ADRs > skills > docs.  
This handoff is resume evidence, not a second SSOT. Live execution status lives on `mro-nxqp` / `mro-z89e`.
