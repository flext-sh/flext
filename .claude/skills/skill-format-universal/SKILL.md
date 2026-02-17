---
name: skill-format-universal
description: Canonical SKILL.md structure with evidence-first writing rules.
scope: /home/marlonsc/flext/.claude/skills/
tags: [skills,docs,standards]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/.claude/skills/`

## Sources

- `/home/marlonsc/flext/CLAUDE.md`
- `/home/marlonsc/flext/AGENTS.md`
- `/home/marlonsc/flext/context/core/agent-patterns.md`

## Enforced Rules

- Enforced by: every SKILL file must include frontmatter and the six sections used by this repository.
- Guideline: every rule must point to a repository anchor file or an official project URL.
- Guideline: avoid vague wording like "best practice" without concrete do/avoid instructions.

## Guidance

- Write short operational bullets that a developer can execute directly.
- Keep scope explicit in `## Applies To` and avoid cross-scope policy leakage.
- Use repository paths for internal behavior and official docs links for library behavior.
- Keep examples minimal and tied to real files in this workspace.

## Examples

- Good: "Use `.lash` for Result recovery (see `flext-core/src/flext_core/result.py`)".
- Avoid: "Handle errors functionally" without file-level evidence or API names.

## Verification

- `rg -n "^---$" .claude/skills/*/SKILL.md`
- `rg -n "^##\s+Applies To$|^##\s+Sources$|^##\s+Enforced Rules$|^##\s+Guidance$|^##\s+Examples$|^##\s+Verification$" .claude/skills/*/SKILL.md`
