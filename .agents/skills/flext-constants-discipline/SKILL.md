---
name: flext-constants-discipline
description: 'Canonical constants layout using StrEnum, IntEnum, Literal, frozenset, MappingProxyType, tuple and Final. Use when adding or refactoring any c.* constant across the workspace.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Constants Discipline

## Workflow

1. Grep for raw module-scope collections in the target project:
2. For each hit, choose the immutable form that matches the runtime contract.
3. Relocate into the `c.<Project>.<Category>` namespace.

## Contracts

- Use `StrEnum` or `IntEnum` for closed runtime choices and `Literal` for static alternatives.
- Use immutable containers (`tuple`, `frozenset`, `MappingProxyType`) and annotate module constants with `Final`.
- Expose constants through the owning `c` namespace; do not duplicate values in consumers.
