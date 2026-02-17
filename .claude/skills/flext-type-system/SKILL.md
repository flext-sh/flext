---
name: flext-type-system
description: Type-system anchors and usage map for FLEXT aliases and containers.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/flext-core/src/flext_core/typings.py`
- `/home/marlonsc/flext/flext-core/docs/api-reference/foundation.md`
- `/home/marlonsc/flext/flext-core/docs/guides/railway-oriented-programming.md`

## Enforced Rules

- Guideline: use centralized aliases from `typings.py` for shared vocabulary and consistency.
- Guideline: avoid redefining JSON/general value types in feature code when canonical aliases already exist.

## Guidance

- Use `t.GeneralValueType`, `t.JsonValue`, and container classes where data contracts cross module boundaries.
- Pair type usage with result flow patterns (`r[T]`) for clear success/failure contracts.

## Examples

- `typings.py` documents both module-level aliases and container classes used throughout flext-core.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-type-system/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-type-system/SKILL.md`
