---
name: lib-orjson
description: 'Use this skill to deterministic high-performance JSON serialization
  with orjson in flext_core utilities. Use when editing sort keys, cache normalization,
  or JSON boundary conversion logic. DO NOT USE FOR: questions unrelated to lib-orjson
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Skill

**UTILITY SKILL**

## USE FOR

- Requests about lib orjson.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-orjson.
- creating projects or architecture from scratch.

## Workflow

1. Locate existing `orjson` imports and calls in the target module.
2. Confirm deterministic options (`OPT_SORT_KEYS`) remain present.
3. Confirm decoded text output remains `str` for tuple sorting and key comparison.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
