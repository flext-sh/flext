# Roadmap

<!-- TOC START -->

- [Current documents](#current-documents)
- [Operational authority (2026-09-17)](#operational-authority-2026-09-17)
- [Runtime status](#runtime-status)

<!-- TOC END -->

This directory holds maintained roadmap and runbook documents for the FLEXT workspace.
The prose is hand-curated; managed TOCs remain generator-owned. Documentation validation
supplies evidence, not automatic execution status.

## Current documents

- [Rope-Gen Engine runbook (2026-09-15)](rope-gen-engine-runbook-2026-09-15.md) — owner,
  taxonomy, findings flow and resume procedure for `make gen` / `make fix` / `make mod`.
  **Resume authority updated 2026-09-17:** the coordinator is Gas City Bead
  `flext-itpd1.3`; `flext-itpd1.2` owns documentation and `flext-itpd1.4` owns Make
  machinery. The runbook retains concrete technical Bead references for reconciliation,
  not unverified completion claims.

## Operational authority (2026-09-17)

Gas City Bead `flext-itpd1.3` under `flext-itpd1` coordinates the current cycle, Beads,
serialized gates, integration and closure. Sibling workstreams `.2` (documentation) and
`.4` (Make machinery) deliver bounded owner repairs; workers do not merge or close
Beads. The versioned recovery contracts are this roadmap and the
[stabilization runbook](../ways-of-working/stabilization-checkpoint-0.12.md). Follow the
explicitly approved recovery scope, not the newest local plan. Workspace-local plans and
addenda remain session context; approval to use them does not authorize copying or
publication.

Earlier roadmap plans (`1789489334832`, `1789500358999`, `1789500368402`,
`1789501099301`, `1789564863139`, and the `1788961161018-*` / `1788987078557-*` /
`1789065585607-*` checkpoint plans) are superseded history. They remain on disk as dated
evidence and do not define the resume or execution route.

## Runtime status

Fleet stability on `0.12.0-dev` is **unproved** as of this recovery update. The
canonical root cycle is `make setup` → `make gen` → `make mod` → `make gen` → `make gen`
→ `make fix` → `make fmt` → `make check` → `make test` → `make build`, followed by
applicable public runtime and native documentation/link validation. Repeated gen/fix/fmt
must be no-op, exit-zero runs on the unchanged candidate. No new cycle starts before
warning-free and finding-free fleet receipts on the published integrated SHAs. Later
changes invalidate affected receipts; this roadmap is not runtime proof.
