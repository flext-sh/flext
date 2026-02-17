---
name: flext-strict-typing
description: Typing hardening patterns used across flext-core and related projects.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/flext-core/src/flext_core/typings.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/protocols.py`
- `/home/marlonsc/flext/context/project-intelligence/technical-patterns.md`

## Enforced Rules

- Guideline: prefer explicit typed aliases and protocol contracts over broad untyped payloads.
- Guideline: keep Python 3.13 typing style (`X | Y`, built-in generics).

## Guidance

- Use RootModel containers and typed aliases when representing nested map/list payloads.
- Use protocol interfaces for boundary contracts where implementation should remain swappable.

## Examples

- Protocol metaclass handling and structural checks are implemented in `flext-core/src/flext_core/protocols.py`.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-strict-typing/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-strict-typing/SKILL.md`
