---
name: lib-orjson
description: Official orjson serialization guidance and workspace integration anchors.
scope: /home/marlonsc/flext/
tags: [libraries,skills,references]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `https://github.com/ijl/orjson`
- `https://github.com/ijl/orjson#serialize`
- `https://github.com/ijl/orjson#deserialize`
- `https://github.com/ijl/orjson#option`
- `/home/marlonsc/flext/flext-core/pyproject.toml`
- `/home/marlonsc/flext/pyproject.toml`

## Enforced Rules

- Enforced by: dependency presence and version constraints in workspace/package pyproject files.
- Guideline: external library usage should follow project wrappers and boundaries already present in flext-core.

## Guidance

- Remember `orjson.dumps()` returns `bytes`; decode only when a text API requires `str`.
- Use option flags intentionally and document deterministic/sorted output tradeoffs.
- Use `default` serializer handlers for unsupported custom types and raise `TypeError` for unknowns.

## Examples

- Project anchors: `/home/marlonsc/flext/flext-core/pyproject.toml`, `/home/marlonsc/flext/pyproject.toml`

## Verification

- `rg -n "https?://" .claude/skills/lib-orjson/SKILL.md`
- `rg -n "Project anchors:" .claude/skills/lib-orjson/SKILL.md`
