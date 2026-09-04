---
name: flext-context-routing
description: Route FLEXT repositories through global execution skills and the branch-matched local flext-law domain delta after flext-core dependency detection.
---

# FLEXT Context Routing

This is the sole always-loaded local FLEXT surface. It selects the exact
branch-matched FLEXT law without duplicating universal execution governance.

## Required composition

1. Read `~/.agents/AGENTS.md`.
2. Before build, generation, docs, checks, tests, or diagnosis, read
   `~/.agents/skills/agent-wide/personal/make-check/SKILL.md`.
3. For every FLEXT task, read the exact local
   `.agents/skills/flext-law/SKILL.md`.
4. At every completion boundary, read
   `~/.agents/skills/agent-wide/verification/verification-loop/SKILL.md`.

Fail closed if a required file is absent. Never resolve `flext-law` by an
unqualified catalog name, from `main`, or from another checkout.

## Detection and scope

- Activate when the workspace provider marker or dependency graph contains
  `flext-core`.
- In workspace mode, use the active workspace root and its checked-out law.
- In standalone mode, use the FLEXT root law pinned to the same branch or
  release; never fall back to `main`.
- Load only local surfaces declared in `.agents/provider.toml`. Global skills
  remain owned by `~/.agents` and are not copied into the local provider.
