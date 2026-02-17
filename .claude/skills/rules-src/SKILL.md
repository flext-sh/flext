---
name: rules-src
description: Scoped contribution rules for `src/` that align with root CLAUDE and project conventions.
scope: /home/marlonsc/flext/src/
tags: [rules,scope,docs]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/src/`

## Sources

- `/home/marlonsc/flext/CLAUDE.md`
- `/home/marlonsc/flext/AGENTS.md`
- `/home/marlonsc/flext/CONVENTIONS.md`
- `/home/marlonsc/flext/src/`

## Enforced Rules

- Guideline: keep changes local to this scope and follow existing file naming and structure patterns.
- Guideline: do not duplicate global governance text from root `CLAUDE.md` inside scope docs.

## Guidance

- Before editing, read sibling files in the same directory to match style and structure.
- Prefer incremental edits and verify with scope-relevant commands (tests/build/docs checks).
- Keep references path-anchored so future contributors can verify quickly.

## Examples

- When working in `src/`, cite concrete files under `/home/marlonsc/flext/src/` instead of generic statements.

## Verification

- `ls -la src`
- `rg -n "TODO|FIXME" src || true`
