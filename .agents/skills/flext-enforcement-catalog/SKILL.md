---
name: flext-enforcement-catalog
description: >-
  Route a FLEXT rule to its one canonical catalog: runtime enforcement,
  declarative static policy, or deterministic structural codemod. Use when
  adding, changing, retiring, or auditing rule ownership and identifiers.
license: MIT
metadata:
  version: 2.0.0
---
# FLEXT Enforcement Catalog

## Owners

| Responsibility | Canonical owner |
| --- | --- |
| `ENFORCE-*` identity, metadata, routing, and executable descriptors | `flext-core` enforcement catalog declarations |
| Declarative detector/refactor policy payloads | `flext-infra/src/flext_infra/rules/*.yml` |
| Policy schemas and execution | `flext-infra` models and enforcement engine |
| Structural source transformations | codemod provider referenced by `.agents/provider.toml` |

Each rule ID and policy fact has one owner. Engines consume validated
declarations; they do not redefine rule catalogs in Python tables, tests,
snapshots, or documentation.

## Workflow

1. Classify the fact as catalog metadata, an engine policy payload, or a
   structural transformation.
2. Search every catalog and consumer for the ID and behavior.
3. Change the single owning declaration and remove superseded copies.
4. Update documentation and skill references to point at that owner.
5. Run the owning engine's narrow validation, then its affected native gate.
6. Record exact command, exit code, decisive output, and catalog census in the
   active root-workspace Bead.

## Boundaries

- Static policy describes violations; a codemod describes an approved rewrite.
  Do not duplicate one as the other.
- Rope-backed semantic enforcement in `flext-infra` and the external ast-grep
  codemod provider are distinct engines with distinct catalogs.
- Codemod IDs live only in the referenced codemod `provider.toml`.
- Rule tests, snapshots, and scans validate the owner; they are never SSOT.
- Unsafe generic rewrites and silent fallback behavior are forbidden.

## Validation Expectations

Prove unique IDs, schema validity, owner-path existence, positive and negative
behavior, exact preview cardinality for codemods, and idempotence after an
approved rewrite. A missing owner or duplicate ID blocks completion.

## References

- [`provider.toml`](../../provider.toml)
- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`ADR-005`](../../../docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md)
