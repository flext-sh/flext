---
name: lib-returns
description: Official returns library usage mapped to FLEXT result patterns.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://returns.readthedocs.io/en/latest/`
- `https://returns.readthedocs.io/en/latest/pages/result.html`
- `https://returns.readthedocs.io/en/latest/pages/pipeline.html`
- `https://github.com/dry-python/returns`
- `/home/marlonsc/flext/flext-core/src/flext_core/result.py`
- `/home/marlonsc/flext/flext-core/docs/guides/railway-oriented-programming.md`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Use `Result` composition with `.bind`/`.map` and project wrapper `FlextResult` at boundaries.
- Use `.lash` for failure recovery branches (project-standard pattern).
- Keep impure side-effect boundaries explicit when crossing IO-related operations.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/result.py`, `/home/marlonsc/flext/flext-core/docs/guides/railway-oriented-programming.md`, `/home/marlonsc/flext/flext-core/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-returns/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-returns/SKILL.md`
