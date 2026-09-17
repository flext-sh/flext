# Roadmap

<<<<<<< HEAD
<!-- TOC START -->
- No sections found
<!-- TOC END -->

Roadmap updates are generated from docs validation outputs.
=======
This directory holds maintained roadmap and runbook documents for the FLEXT
workspace. It is hand-curated, not generated.

## Current documents

- [Rope-Gen Engine runbook (2026-09-15)](rope-gen-engine-runbook-2026-09-15.md) —
  owner, taxonomy, findings flow and resume procedure for `make gen` /
  `make fix` / `make mod`. **Resume authority updated 2026-09-17:** the
  canonical route is Gas City Bead `flext-itpd1.2` plus this versioned runbook;
  earlier workspace-local plans remain dated history.

## Operational authority (2026-09-17)

The live execution route for stabilization and modernization is Gas City Bead
`flext-itpd1.2`. The versioned recovery contracts are this roadmap and
`docs/ways-of-working/stabilization-checkpoint-0.12.md`. Workspace-local plans
and addenda carry session evidence only and are intentionally not published.

Earlier roadmap plans (`1789489334832`, `1789500358999`,
`1789500368402`, `1789501099301`, `1789564863139`, and the
`1788961161018-*` / `1788987078557-*` / `1789065585607-*` checkpoint
plans) are superseded history. They remain on disk as dated evidence and do
not define the resume or execution route.

## Runtime status

The `0.12.0-dev` line is **not globally green** as of 2026-09-17. The
canonical cycle (`make setup` → `make gen` ×2 → `make fix` → `make fmt` →
`make check` → `make test` → `make build`) is the target contract; a proven
green run on the integration tip is required before any lane reports
completion. See `docs/ways-of-working/stabilization-checkpoint-0.12.md`.
>>>>>>> origin/0.12.0-dev
