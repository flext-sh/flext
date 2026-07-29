---
name: rules-typings
description: 'Rules for typing support assets in `typings/` (stubs, compatibility shims, and local type metadata). Use when editing `.pyi` files or typing helper packages.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Typings

## Workflow

1. Identify runtime API change requiring stub update.
2. Update matching `.pyi` declarations.
3. Validate imports/exports in stubs remain coherent.

## Enforced contracts

- Prefer explicit typing_extensions imports when backport compatibility is needed.

## Resources

- [`rules/require-typing-extensions-compat.yml`](rules/require-typing-extensions-compat.yml)
