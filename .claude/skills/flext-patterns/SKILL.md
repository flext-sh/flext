---
name: flext-patterns
description: Reusable project patterns for result flow, DI, logging, and typed payload handling.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/flext-core/docs/architecture/patterns.md`
- `/home/marlonsc/flext/flext-core/docs/guides/railway-oriented-programming.md`
- `/home/marlonsc/flext/flext-core/src/flext_core/result.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/container.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/loggings.py`

## Enforced Rules

- Guideline: prefer documented pattern implementations from flext-core over ad-hoc new abstractions.
- Guideline: examples must point to concrete repository files.

## Guidance

- Use this skill when reviewing a change for architectural fit and consistency with existing platform patterns.
- Extract examples from runtime/result/container/loggings rather than inventing pseudo-code.

## Examples

- Railway pattern and monadic composition are already documented and implemented; reuse them directly.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-patterns/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-patterns/SKILL.md`
