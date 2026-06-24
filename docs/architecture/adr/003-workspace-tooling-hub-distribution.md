# ADR-003 — Workspace tooling distributed by `~/.ai-hub`

- **Status:** Accepted
- **Date:** 2026-06-24
- **Scope:** FLEXT monorepo Makefile, `workspace_custom.mk`, and agent/tooling
  integration with the operator's `~/.ai-hub` automation hub.
- **Relates to:** `~/.ai-hub/docs/adr/0002-workspace-common-make-base.md`
  (canonical decision in the hub); `flext/workspace_custom.mk` (extension point).

## Context

FLEXT already had a generated Makefile and its own `scripts/dispatch.py` using
`flext-command` headers. The operator's `~/.ai-hub` hub gained a generic
thin-wrapper model based on `cosmos-main` that can distribute common `make`
verbs to all CRG-catalogued workspaces.

We needed to adopt that model without breaking the existing Makefile or
replacing the existing FLEXT dispatcher.

## Decision

### D1 — FLEXT adopts the hub wrapper via `workspace_custom.mk`

- `flext/workspace_custom.mk` now includes
  `~/.ai-hub/templates/cosmos-wrapper.mk`.
- The main `Makefile` already includes `workspace_custom.mk` at the end, so all
  pre-existing FLEXT targets (`check`, `test`, `build`, `ship`, `val`, etc.)
  retain precedence.
- The wrapper exposes the existing FLEXT dispatcher through `make cosmos-help`
  and forwards any unknown verb to `scripts/dispatch.py`.

### D2 — FLEXT keeps its existing dispatcher

- `flext/scripts/dispatch.py` remains the canonical dispatcher for FLEXT.
- The hub distributor (`distribute-workspace-base.py`) detected the local
  dispatcher and did not overwrite it.
- No new `scripts/<verb>/<WHAT>` default scripts are introduced; FLEXT's
  `scripts/cmd/<verb>/<what>.py` layout remains authoritative.

### D3 — Documentation and skills converge on the hub model

- `AGENTS.md` references the common tooling base.
- Relevant skills (`flext-development-workflow`, `workspace-maintenance`,
  `flext-agent-integration`) document the new verbs and distribution mechanism.

## Consequences

- **Positive:** FLEXT gains the same cross-workspace command conventions as
  other CRG workspaces while preserving its existing build/test/release surface.
- **Cost / constraint:** `workspace_custom.mk` now depends on
  `~/.ai-hub/templates/cosmos-wrapper.mk`; developers without `~/.ai-hub` will
  still have the normal FLEXT Makefile (the include is harmless when the file
  exists; when absent, Make warns but continues).
- **Verification:** `make help`, `make check WHAT=help`, and `make cosmos-help`
  all work in FLEXT after adoption.

## Evidence

- `flext/workspace_custom.mk` includes the hub wrapper.
- `make cosmos-help` lists FLEXT verbs (`boot`, `build`, `check`, `test`,
  `ship`, `val`, etc.).
- `make check WHAT=help` continues to show FLEXT's own `check` actions.
