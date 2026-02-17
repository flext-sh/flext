---
name: flext-development-workflow
description: Execution workflow for scoped changes, validation, and review hygiene.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/AGENTS.md`
- `/home/marlonsc/flext/context/core/agent-patterns.md`
- `/home/marlonsc/flext/context/core/tool-usage.md`
- `/home/marlonsc/flext/Makefile`

## Enforced Rules

- Guideline: explore patterns first, then edit, then verify with concrete commands.
- Guideline: keep edits minimal and tied to requested scope.

## Guidance

- Use direct tools for known paths; use background exploration for unfamiliar areas.
- Run scope-appropriate checks after edits (`make check` and project-local validation as needed).

## Examples

- Workflow loop: Explore -> Plan -> Execute -> Verify, from `context/core/agent-patterns.md`.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-development-workflow/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-development-workflow/SKILL.md`
