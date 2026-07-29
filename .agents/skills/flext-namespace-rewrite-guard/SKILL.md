---
name: flext-namespace-rewrite-guard
description: 'A safe procedure for workspace-wide namespace propagation (`c.X` → `c.NS.X`, etc.). Required before any bulk rewrite. Any task that propagates a collision-aware rewrite across the workspace.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Namespace Rewrite Guard

## Workflow

1. Inventory definitions, exports, callers, string references, and generated projections.
2. Classify collisions and choose the single final namespace owner.
3. Apply a structural dry-run, inspect the diff, then update the complete consumer set.
4. Validate imports and tests before proving the old namespace has no live references.

## Contracts

- Build a symbol census before rewriting and classify collisions by owner and consumer.
- Use structural refactoring for Python symbols; never apply blind regex replacement.
- Update definition, exports, callers, docs, and tests atomically, then prove the old path has zero live references.
