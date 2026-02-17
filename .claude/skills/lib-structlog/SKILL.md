---
name: lib-structlog
description: Official structlog guidance and FLEXT structured logging integration.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://www.structlog.org/en/stable/`
- `https://www.structlog.org/en/stable/processors.html`
- `https://www.structlog.org/en/stable/standard-library.html`
- `https://github.com/hynek/structlog`
- `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/loggings.py`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Configure structlog once at application startup via runtime helpers.
- Use context binding/clearing APIs for request-scoped correlation data.
- Keep processor chain deterministic and renderer-last for predictable output.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`, `/home/marlonsc/flext/flext-core/src/flext_core/loggings.py`, `/home/marlonsc/flext/flext-core/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-structlog/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-structlog/SKILL.md`
