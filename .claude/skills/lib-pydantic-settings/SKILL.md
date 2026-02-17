---
name: lib-pydantic-settings
description: Official pydantic-settings guidance with repository integration anchors.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://docs.pydantic.dev/latest/concepts/pydantic_settings/`
- `https://docs.pydantic.dev/latest/api/pydantic_settings/`
- `https://github.com/pydantic/pydantic-settings`
- `/home/marlonsc/flext/flext-core/src/flext_core/protocols.py`
- `/home/marlonsc/flext/flext-core/pyproject.toml`
- `/home/marlonsc/flext/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Use `SettingsConfigDict` for env prefix and source behavior; do not scatter env parsing across modules.
- Use nested env delimiters for structured config and validate defaults intentionally.
- Keep settings model contracts typed and consumed through protocol/config boundaries.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/protocols.py`, `/home/marlonsc/flext/flext-core/pyproject.toml`, `/home/marlonsc/flext/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-pydantic-settings/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-pydantic-settings/SKILL.md`
