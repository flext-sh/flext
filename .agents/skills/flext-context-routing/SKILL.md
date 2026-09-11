---
name: flext-context-routing
description: Route a detected FLEXT project through its local, materialized flext-law skill and project-owned instructions.
---

# FLEXT Context Routing

This is the local FLEXT activation surface. It composes only files present in
the active project checkout.

## Required composition

1. Read the active project's root instructions.
2. Read the local `.agents/skills/flext-law/SKILL.md` in full.
3. Use the project's documented build, generation, check, and test commands.
4. Validate the changed behavior through the active project's real interfaces.

Fail closed if a required local file is absent. Never resolve `flext-law` from
another checkout, branch, home-level catalog, or network source.

## Detection and scope

- Activate when the workspace provider marker or dependency graph contains
  `flext-core`.
- In workspace mode, use the active workspace root and its checked-out law.
- In standalone mode, use only the law materialized in that repository.
- Load only project-local surfaces. A projection must be an independent copy,
  never a symbolic link or cross-repository reference.
