---
name: lib-dependency-injector
description: Official dependency-injector usage aligned with FlextContainer patterns.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://python-dependency-injector.ets-labs.org/`
- `https://python-dependency-injector.ets-labs.org/providers/index.html`
- `https://python-dependency-injector.ets-labs.org/wiring.html`
- `https://github.com/ets-labs/python-dependency-injector`
- `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`
- `/home/marlonsc/flext/flext-core/src/flext_core/container.py`
- `/home/marlonsc/flext/flext-core/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Define providers in container layer and consume through runtime/container bridge methods.
- Use provider override patterns in tests instead of monkey-patching dependencies.
- Keep DI framework symbols out of business logic where project wrappers already exist.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/src/flext_core/runtime.py`, `/home/marlonsc/flext/flext-core/src/flext_core/container.py`, `/home/marlonsc/flext/flext-core/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-dependency-injector/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-dependency-injector/SKILL.md`
