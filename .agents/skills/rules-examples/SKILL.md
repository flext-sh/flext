---
name: rules-examples
description: 'Rules for runnable examples in `examples/` so they stay aligned with current APIs and tooling. Use when editing or adding example scripts.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Examples

## Workflow

1. Choose target example and its API dependencies.
2. Update script with current public imports and behavior.
3. Verify script syntax and invocation.

## Enforced contracts

- Examples should be directly runnable via a __main__ guard.
- Examples should opt into postponed annotations for consistency.

## Resources

- [`rules/require-future-annotations.yml`](rules/require-future-annotations.yml)
- [`rules/require-main-guard.yml`](rules/require-main-guard.yml)
