---
name: flext-context-routing
description: Route FLEXT Python repository and workspace tasks after flext-core dependency detection. Use for FLEXT workspace detection, local skill selection, MRO facade work, governance, imports, or shared test fixtures.
---

# FLEXT Context Routing

Read this skill first. It is the sole always-loaded local FLEXT surface and
selects only the on-demand law needed for the current task.

## Routing

- Load `flext-law` for FLEXT implementation, review, migration, refactoring,
  validation, generated surfaces, or architecture work.
- Load `flext-inviolable-rules` for governance, Beads coordination, shared
  worktree safety, completion gates, evidence, handoff, commit, or closure.
- Load both when FLEXT-law work also changes repository state.

## Workspace Rules

- Preserve facade direction `c -> t -> p -> m -> u`.
- Reverse imports are declaration-only and must remain under `TYPE_CHECKING`.
- `flext-tests` owns generic fixtures; do not create package-local duplicates.
- Do not load a local skill that is absent from `surfaces.on_demand` in
  `.agents/provider.toml`.
