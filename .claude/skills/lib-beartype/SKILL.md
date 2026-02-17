---
name: lib-beartype
description: Official beartype runtime-check guidance with FLEXT runtime anchors.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://beartype.readthedocs.io/en/latest/`
- `https://beartype.readthedocs.io/en/latest/api_claw/`
- `https://beartype.readthedocs.io/en/latest/api_decor/`
- `https://github.com/beartype/beartype`
- `/home/marlonsc/flext/flext-core/src/flext_core/_beartype_conf.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Centralize runtime checking enablement in runtime utilities.
- Prefer shared configuration object for consistent violation behavior across packages.
- Use targeted runtime checks for high-risk boundaries rather than blanket noise-heavy checks.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/_beartype_conf.py`, `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`, `/home/marlonsc/flext/flext-core/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-beartype/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-beartype/SKILL.md`
