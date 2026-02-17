---
name: lib-pydantic-v2
description: Official Pydantic v2 integration guidance mapped to FLEXT code.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://docs.pydantic.dev/latest/`
- `https://docs.pydantic.dev/latest/concepts/models/`
- `https://docs.pydantic.dev/latest/concepts/validators/`
- `https://docs.pydantic.dev/latest/concepts/serialization/`
- `https://github.com/pydantic/pydantic`
- `/home/marlonsc/flext/flext-core/src/flext_core/typings.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/result.py`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Use `model_validate()`/`model_validate_json()` when strictness or context matters.
- Use `model_dump()` at serialization boundaries and keep field/model serializers explicit.
- Use `ConfigDict(extra="forbid")` for strict input contracts unless third-party payload tolerance is required.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/typings.py`, `/home/marlonsc/flext/flext-core/src/flext_core/result.py`, `/home/marlonsc/flext/flext-core/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-pydantic-v2/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-pydantic-v2/SKILL.md`
