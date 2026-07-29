---
name: lib-orjson
description: 'Deterministic high-performance JSON serialization with orjson in flext_core utilities. Use when editing sort keys, cache normalization, or JSON boundary conversion logic.'
license: MIT
metadata:
  version: 1.0.0
---
# Skill

## Workflow

1. Locate existing `orjson` imports and calls in the target module.
2. Confirm deterministic options (`OPT_SORT_KEYS`) remain present.
3. Confirm decoded text output remains `str` for tuple sorting and key comparison.

## Enforced contracts

- json.dumps usage in validation utilities should remain a fallback path behind orjson.dumps.
- orjson serialization must include OPT_SORT_KEYS for deterministic ordering.

## Resources

- [`rules/prefer-orjson-dumps.yml`](rules/prefer-orjson-dumps.yml)
- [`rules/require-sort-keys.yml`](rules/require-sort-keys.yml)
