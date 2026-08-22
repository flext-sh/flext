# flext-tap-oracle-wms — legado + dead-code + protocols pilot

**Date:** 2026-07-12
**Bead lane:** mro-rn88 (uncontested) + aligns with mro-pzxd (polymorphic/legado initiative)
**Status:** approved design → implementation

## Problem

Prior Pydantic-2-way work (`model_validate({dict})` → `Model()`) was **cosmetic**. The real
flext-law violations remain:

1. **Polymorphic concrete-model types in interfaces** instead of `p.*` protocols
   (flext-law §3.2 "a model is never a type").
2. **Tests/examples act as false consumers**, masking genuinely dead production code.
3. **Dead / duplicated / disconnected code** never validated against the real usage universe.

This pilot proves the complete template on ONE uncontested, fully-green, leaf project.

## Target: flext-tap-oracle-wms (why)

- Baseline fully green: ruff 0, pyrefly 0, pyright 0, import ok.
- Uncontested: 0 active-lane mentions; mine via mro-rn88.
- NOT in the broken `m.Ldif.EntryMetadata` refactor chain (unlike ldap/ldif/tap-ldap).
- Leaf **end-user tap**: 0 external consumers reference it → acceptance = its own **public CLI**.
- Real scope: 24 test files, 2 examples, 4 polymorphic-interface sites, 14 public classes.

## Usage universe (SSOT — memory:flext-external-consumer-universe)

Dead-code is judged against: **flext monorepo `src/` + these external consumers**:
`../projeto_a` (88), `../cosmos-main` (60), `../cosmos-docgen` (58), `../.ai-hub` (25).
`legado/` is **excluded from every search** (archival false-consumers). `meltano/` dir = 0 code imports.
`flext-(tap|target|dbt)-*` are **end-users validated via their public CLI**, not by external refs.

## Phase 1 — Quarantine tests + examples → legado/ (dir-level, out of every gate)

```bash
mkdir legado
mv tests legado/tests
mv examples legado/examples
mkdir tests && printf '' > tests/__init__.py
```

- Add `legado/` to `.gitignore` (dir-level boundary; invisible to ruff/format/typecheck/
  pytest/coverage/import-discovery/codegen/census). No file-by-file tool excludes.
- Archive, not delete (flext-law §13). Reversible.

## Phase 2 — Validate real code + classify-before-remove (memory:dead-code-classify-before-remove)

No candidate is deleted on "zero refs" alone. Each is classified:

1. **Duplicated** → consolidate DRY, keep canonical, remove copy.
2. **Useful but disconnected** → wire in + replace the wrong/inferior code it should supersede
   (improve/correct the useful code first if needed).
3. **Correctly generalized + in-domain** → keep and connect.
4. **Genuine legacy** → remove at root, net-negative LOC.

Only category 4 is deleted. 1–3 are architectural fixes. 6-gate FLEXT reference check
(rg word-boundary + lazy-map + `__all__` + facade alias + MRO base + `p.*` impl) across the
usage universe, excluding legado.

## Phase 3 — Collapse polymorphic interfaces → canonical model + protocol

4 `: p.X` / `-> p.X` concrete-model signatures → `p.*` protocol types (no polymorphic
unions / shadow DTOs). Extend the local `p.TapOracleWms.*` facet if a protocol is missing.
Models stay pure data; signatures depend on protocols (§3.2).

## Phase 4 — Static gate + CLI acceptance (no pytest)

After each ≤5-file batch: **ruff + pyrefly + mypy + pyright + import-smoke + CLI-smoke**
(`python -m flext_tap_oracle_wms.cli --help` + real Singer discovery). NO pytest (tests are
legado). Pathspec commit + fast-forward push per batch. Fix-forward only.

## Out of scope

- Contested/foreign-lane projects (ldap/ldif/core/meltano/oracle-*/cli/web/auth, mro-pzxd's own targets).
- Rewiring legado back into any tool.
