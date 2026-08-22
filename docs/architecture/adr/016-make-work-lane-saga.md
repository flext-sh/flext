# ADR-0016 — Retire the Make lane lifecycle

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
<!-- TOC END -->

- **Status:** Superseded
- **Date:** 2026-08-03
- **Superseded:** 2026-08-21
- **Scope:** Historical Make-based lane lifecycle

## Context

This ADR originally established a generated Make verb for Bead, branch,
worktree, pull-request, and lane cleanup coordination. Gas Town now owns that
workflow for the `flext` rig. Retaining two operational owners caused branch,
worktree, tracker, and handoff drift.

## Decision

1. Gas Town is the sole lane lifecycle owner.
2. Workers use `gt sling`, `gt hook status`, `gt done`, `gt convoy`, and
   `gt handoff` as applicable.
3. The Make lane verb and `FlextInfraWorkService` are extinct from current
   operational guidance and generated surfaces.
4. `FlextInfraWorktreeService` remains an internal Git worktree primitive. It
   is not an operator lane lifecycle.
5. Historical records may mention the retired command only when clearly marked
   historical and excluded from operational navigation.

## Consequences

- One system owns Bead dispatch, lane creation, merge-queue submission, and
  cleanup.
- The Make command guide documents build, generation, validation, and release
  only.
- Worker guidance routes directly to Gas Town.
- This ADR remains in the registry as the disposition record for the retired
  lifecycle.
