---
name: lib-pyyaml
description: Official PyYAML guidance with secure loader defaults for project usage.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://pyyaml.org/wiki/PyYAMLDocumentation`
- `https://github.com/yaml/pyyaml`
- `/home/marlonsc/flext/flext-core/pyproject.toml`
- `/home/marlonsc/flext/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Use `safe_load`/`safe_dump` for untrusted input paths.
- Prefer block-style output (`default_flow_style=False`) for readable config diffs.
- Use CLoader/CDumper when available on performance-sensitive paths with safe fallback.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/pyproject.toml`, `/home/marlonsc/flext/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-pyyaml/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-pyyaml/SKILL.md`
