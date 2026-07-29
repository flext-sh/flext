---
name: lib-returns
description: 'Railway-oriented `r` composition built on dry-python/returns. Use when implementing result-flow operations, error recovery chains, or converting between container types.'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Returns — r Railway Composition

## Workflow

1. Import `r` from `flext_core`
2. Create results via `r[T].ok(value)` or `r[T].fail("error")`
3. Compose with `.map()` → `.flat_map()` → `.lash()` chains

## Enforced contracts

- Detect deprecated .unwrap() calls on r-like values.

## Resources

- [`rules/unwrap-to-value.yml`](rules/unwrap-to-value.yml)
