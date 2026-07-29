---
name: flext-type-system
description: 'Canonical FLEXT type-system map for aliases, generics, result interplay, and settings contracts. Use when changing shared typing primitives.'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Type System

## Workflow

1. Locate existing alias/type-var nearest to intended change.
2. Extend or refine canonical alias in `typings.py`.
3. Validate impacted consumers in result/settings/protocol modules.

## Enforced contracts

- Bare dict return annotations are discouraged in favor of explicit aliases/contracts.
- Define shared aliases in `t`, runtime protocols in `p`, models in `m`, and fallible results as `r[T]`.
- Keep generic parameters explicit and preserve error types across result composition.
- Change shared typing primitives only with consumer-wide Pyrefly, Pyright, Mypy, and test evidence.

## Resources

- [`rules/ban-bare-dict-return.yml`](rules/ban-bare-dict-return.yml)
