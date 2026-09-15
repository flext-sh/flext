# Runbook — Rope-Gen Engine (owner, taxonomy, findings flow, resume)

- **Status:** Active runbook (plan-of-record §F2.W0)
- **Date:** 2026-09-15
- **Plan:** `.kilo/plans/1789489334832-rope-gen-engine-strict-init.md` (unified v4)
- **Law:** ADR-014 §3b (rope-in-gen), ADR-010 §3b (alignment), render purity law
- **Beads:** engine = `flext-crd1y` (discovered-from `flext-5fxu6.4`); loc-cap = `flext-471ws`;
  journal lock = `flext-fkfmu`; mission tests = `flext-wjozx` / `flext-c4k44`

## 1. Owner → responsibility

| Concern | Owner | Hard rule |
| --- | --- | --- |
| Generated projections (`__init__`, lazy-init exports, facets) | `make gen` (flext-infra codegen) | gen is the ONLY writer; hand output = adoption input; gen output wins |
| Auto-fixable findings (rel-import self-import, etc.) | `make fix` (rope via engine) | fix corrects, never suppresses |
| Reporting of remaining findings | `make check` | detectors never disabled; no silent success |
| Ad-hoc structural moves | `make mod` | consumes the same Rope primitives; one engine |
| Config/rules surface | `config/codegen.yaml`, `rules/*.yaml` | rules-as-data; exceptions = one data line |
| Render inputs | SSOT + templates + PINS only | any environment input in render = P0 defect |
| Landing | flext-infra via PR + `merge --admin --merge` on `0.12.0-dev`; members via FF push at tips; gitlinks last | never land with local-green/open PR/mergable |

## 2. Findings taxonomy (ONE vocabulary, engine + gates + receipts)

| Code | Meaning | Level | Behavior |
| --- | --- | --- | --- |
| `GEN-W001` | sibling part without `__all__` | gen emits warn; fix auto-fills from public surface union; check reports | warn → auto-fixable |
| `GEN-W002` | module imports itself through absolute self path | fix relativizes (scope = declared table; flext-core overlay is a declared exception; lazy facets are exempt) | warn → auto-fixable |
| `GEN-W003` | module outside its family layout | check reports; move via mod | report |
| `GEN-W004` | format/header drift on generated facet | fix restores rendered shape | warn → auto-fixable |
| `GEN-W005` | runtime SCC cycle in imports (SCC solver) | check reports; root cause at owner | report |
| `GEN-E001` | stale `__all__` (export declared, absent in sibling) | gen FAILS LOUD | error |
| siblings symbol collision | same public name in two parts of one family | gen FAILS LOUD | error |

## 3. Findings flow (one detector, one consumer)

1. Engine stages read typed rules (Pydantic models parsed once via `u.Cli.yaml_*`).
2. `gen` emits warnings into the single per-repo receipt (findings + timings).
3. `fix` consumes only fixable codes from the same table; re-runs gen to prove the fixed point.
4. `check` reports the remainder; the invocation stays red while findings remain.
5. New rule = typed section in `config/codegen.yaml` / `rules/*.yaml` — never an ad-hoc detector class.

## 4. Transaction loop per repository

```
snapshot (input-CAS, authenticated)
 → plan EVERYTHING (pyproject, templates, mise, lazy-init, docs) — ONE rope project per repo
 → publish in one transactional batch (Journal CAS: content+mode)
 → single receipt (findings + timings)
```

- Failure mid-publication (gen **and** fix): reverse-apply ONLY this invocation's
  effects; acceptance criterion = empty diff post-rollback. Mandatory injected-failure test.
- Race handling: max 3 cycles (adopt tip, repeat); then proceed and record on
  `flext-fkfmu`. Fix-forward/adopt ALWAYS; reset/restore/stash/rebase/force-push
  of shared work are forbidden.

## 5. Resume procedure (new session)

1. Read plan-of-record v4 (`.kilo/plans/1789489334832-…-strict-init.md`) — the only authority.
2. `git fetch` every touched repo; compare tips; confirm your lane basis (no peer lanes are open).
3. `direnv exec <repo> gc bd ...` is the canonical beads route (Gas City shared standard;
   central DB flext, server mode). Record command + exit + decisive output per grain.
4. Working tree discipline: status must match the expected 15-path `_config` family set (or the
   current wave's scoped set); anything beyond it belongs to history, reclassify before acting.
5. Gates order per wave: `make gen ×2` → `make fix ×2` → `make fmt ×2` → `make check` → tests on
   touched families. gen/fix/fmt NEVER fail-to-finish; a failing one is a defect at its owner.
6. Phase gating: F0 `_config` landing → F1 gen×2/fix×2 idempotence → F2 engine (gate: cosmos-docgen
   ×2 green, bead `flext-crd1y`) → F3 fleet re-projection + sweeps → F4 0.12.0 closure (tag only on
   all-green ×2 + CI SHA).
7. Scope: only `flext-infra-worktrees/` is foreign — never touch. Operator accepts remaining check
   violations/warnings at the 0.12.0 checkpoint IF every Make verb completes in every cycle
   (correction recorded).

## 6. Resume context (2026-09-15, proven)

- flext-infra tip `c3f574807` (0.12.0-dev); `_conform` stale drift adopted via tip; `_models/_config`
  split (13 untracked + 2 M) ready to land through gen ×2 with parity probe 107/107 dunders vs
  `pre_config.json` (scratch snapshots intact).
- `bd`/`rg` shims of this environment may fail; use `direnv exec … gc bd` (bd works outside too,
  same central store) and grep/ls instead of rg.
