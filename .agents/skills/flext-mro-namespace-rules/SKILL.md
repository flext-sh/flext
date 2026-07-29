---
name: flext-mro-namespace-rules
description: 'Use when editing structural `c/t/p/m/u` facades, their internal family composition classes, nested domain namespaces, or same-package MRO imports and exports.'
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT MRO Namespace Rules

Internal family composition classes remain valid implementation structure. The root
facade is the public navigation surface; a skill must not invent a workspace-wide
rename or purge that is absent from an accepted baseline or ADR.

## Workflow

1. Identify the root structural facade, internal family owner, MRO parents, and exports.
2. Confirm the concept has one nested namespace owner and no sibling collision.
3. Keep implementation imports inside the package and consumer imports on the public
   facade.
4. Preserve intentional MRO order and update every export/caller with a public rename.
5. Validate namespace collisions, import cycles, facade exports, and direct consumers.

## Contracts

- Only `c/t/p/m/u` are structural facade families.
- Root facades contain composition and navigation, not application orchestration.
- Internal `FlextConstants*`, `FlextTypes*`, `FlextProtocols*`, `FlextModels*`, and
  `FlextUtilities*` classes may compose the public family but are not runtime primitives.
- Nested domains use direct nouns and one owner; sibling mixins must not expose the
  same public path.
- Tests may use project test facades where the owning test standard defines them;
  no universal rename is implied.

## References

- [`docs/architecture/baseline-v0.13.0.md`](../../../docs/architecture/baseline-v0.13.0.md)
- [`flext-architecture-layers`](../flext-architecture-layers/SKILL.md)
