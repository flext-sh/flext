# Architecture Index

<!-- TOC START -->
- [Canonical Documents](#canonical-documents)
- [Interpretation Rule](#interpretation-rule)
<!-- TOC END -->

This directory contains the canonical architecture baseline for the FLEXT workspace plus the ADR set that records formal
platform decisions.

## Canonical Documents

- [Baseline v0.13.0](baseline-v0.13.0.md)
- [ADR Index](adr/README.md)
- [Ecosystem coordination (internal + external projects, `0.20.0-dev`)](ecosystem-coordination.md)
- [Migration Guide](../guides/migration-to-v0.13.0.md)

## Interpretation Rule

If an older architecture document conflicts with the baseline, the baseline wins until that older document is rewritten
or retired.

Historical architecture files may still exist in this tree, but they are supporting context only. They are not the
current platform contract.
