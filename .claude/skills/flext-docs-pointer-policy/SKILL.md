---
name: flext-docs-pointer-policy
description: Single-root CLAUDE policy and root-skills-only governance model.
scope: /home/marlonsc/flext/
tags: [skills,policy,docs]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/CLAUDE.md`
- `/home/marlonsc/flext/AGENTS.md`
- `/home/marlonsc/flext/.gitignore`

## Enforced Rules

- Enforced by: exactly one `CLAUDE.md` must exist at workspace root.
- Guideline: scoped guidance belongs in `.claude/skills/*/SKILL.md`, not extra CLAUDE files.

## Guidance

- Keep governance hierarchy simple: root `CLAUDE.md` + root skill files.
- When adding a new scope rule, create/update a skill instead of creating another CLAUDE file.
- Reference root CLAUDE from other agent configs (Copilot/Cursor/etc.) through pointer-style docs already present in repo.

## Examples

- Valid state: `/home/marlonsc/flext/CLAUDE.md` exists and no other `CLAUDE.md` exists anywhere under the workspace.

## Verification

- `python - <<'PY'
from pathlib import Path
root=Path('/home/marlonsc/flext')
print([str(p) for p in root.rglob('CLAUDE.md')])
PY`
