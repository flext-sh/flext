# Architecture Index

<!-- TOC START -->

- [Canonical Documents](#canonical-documents)
- [Code Communities](#code-communities)
  - [Purpose](#purpose)
  - [Regeneration and Publication](#regeneration-and-publication)
  - [See Also](#see-also)
- [Interpretation Rule](#interpretation-rule)

<!-- TOC END -->

This directory contains the canonical architecture baseline for the FLEXT workspace plus
the ADR set that records formal platform decisions.

## Canonical Documents

- [Baseline v0.13.0](baseline-v0.13.0.md)
- [ADR Index](adr/README.md)
- [Ecosystem coordination (internal + external projects, `0.20.0-dev`)](ecosystem-coordination.md)
- [Migration Guide](../guides/migration-to-v0.13.0.md)

## Code Communities

### Purpose

Code communities are cohesive clusters of symbols discovered through Leiden community
detection over a code knowledge graph's call/import relationships. Community pages list
member symbols, locations, and line ranges to help readers navigate the architecture by
responsibility instead of directory layout.

The [community index](communities/index.md) is the publication entry point. Community
tables are graph-derived snapshots, not architectural authority. Selection thresholds,
node counts, and membership must come from the publishing owner's current inputs; this
maintained guide does not freeze snapshot values.

The [historical community overview](communities/historical-overview.md) preserves the
formerly published community README, including its complete membership table and
original regeneration claims. It is historical evidence, not the current community
source of truth or an executable regeneration contract. Its relocation changes only
the publication path and the architecture overview link; all community pages remain
preserved.

### Regeneration and Publication

The CRG wiki generator emits community pages and a single `index.md` into
`.code-review-graph/wiki/`. Its graph must match the intended repository and revision
before its output can be used to refresh published documentation.

The current FLEXT documentation generator renders API references and project catalogs;
it does not copy the CRG wiki into `docs/architecture/communities/`. Consequently,
`make gen` is not a regeneration route for the published community snapshots. Publication
requires an owned source and generated-file inventory before any existing snapshot is
replaced or retired. Historical tables and unmanifested pages must remain preserved
until their disposition is authenticated; an auto-generated comment alone is not proof
that a file can be deleted.

MkDocs treats `README.md` and `index.md` in the same directory as the same landing-page
identity. A publication inventory must elect only one of them, preserving maintained
explanatory prose separately from generated membership tables rather than excluding a
conflicting page or weakening strict validation.

The current documentation migration retains `communities/index.md` as the sole landing
page and publishes the former README as `communities/historical-overview.md`. The
historical snapshot's original bytes are preserved in the published Git history.

### See Also

- [Code Communities Index](communities/index.md)
- [Historical Community Overview](communities/historical-overview.md)
- [Documentation Knowledge Index](../knowledge-index.md)
- [API Reference Overview](../api-reference/generated/overview.md)

## Interpretation Rule

If an older architecture document conflicts with the baseline, the baseline wins until
that older document is rewritten or retired.

Historical architecture files may still exist in this tree, but they are supporting
context only. They are not the current platform contract.
