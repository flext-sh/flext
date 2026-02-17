---
name: flext-import-rules
description: Import conventions and alias usage for flext-core and workspace modules.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/flext-core/docs/api-reference/foundation.md`
- `/home/marlonsc/flext/flext-core/src/flext_core/result.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/loggings.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/container.py`

## Enforced Rules

- Guideline: prefer canonical alias exports (`r`, `t`, `c`, `m`, `p`, `u`) where the project already uses them.
- Guideline: avoid creating parallel alias schemes inside feature modules.

## Guidance

- Follow `foundation.md` import patterns for consistency in public-facing code examples and docs.
- Keep imports grouped and stable to reduce churn in broad refactors.

## Examples

- Canonical alias list and usage examples are documented in `flext-core/docs/api-reference/foundation.md`.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-import-rules/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-import-rules/SKILL.md`
