---
name: flext-architecture-layers
description: Layering map and dependency direction for FLEXT modules.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/flext-core/docs/architecture/overview.md`
- `/home/marlonsc/flext/flext-core/docs/architecture/patterns.md`
- `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/container.py`

## Enforced Rules

- Guideline: keep low-level modules free from high-level imports unless existing architecture docs show that dependency.
- Guideline: use layer bridge modules (`runtime`, `container`, `result`) rather than bypassing them.

## Guidance

- Use architecture docs to justify cross-layer dependencies in reviews and refactors.
- When introducing a new module, place it in the layer with nearest existing semantics and dependency direction.

## Examples

- Architecture overview in `flext-core/docs/architecture/overview.md` documents layer responsibilities and interactions.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-architecture-layers/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-architecture-layers/SKILL.md`
