---
name: rules-src
description: 'Rules for shared source modules under top-level `src/`. Use when editing common source code that impacts multiple packages or utilities.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Src

## Workflow

1. Identify the shared source module being changed.
2. Apply scoped edits with explicit contract impact.
3. Verify no boundary violations in imports.

## Enforced contracts

- Shared source modules should use postponed annotations.
- Shared source code should avoid wildcard imports.

## Resources

- [`rules/ban-star-import.yml`](rules/ban-star-import.yml)
- [`rules/require-future-annotations.yml`](rules/require-future-annotations.yml)
