continu# Architecture Index

<!-- TOC START -->

- [Canonical Baseline](#canonical-baseline)
- [Formal Decisions](#formal-decisions)
- [Supporting Architecture References](#supporting-architecture-references)
- [Historical and Supporting Notes](#historical-and-supporting-notes)

<!-- TOC END -->

## Canonical Baseline

The canonical architecture source of truth for the forward workspace is:

- [FLEXT Workspace Baseline v0.13.0](./baseline-v0.13.0.md)

This baseline defines the forward public surface, DI ownership, extension storage model, naming rules, workspace taxonomy, and migration direction for the workspace.

When older architecture documents conflict with the baseline, the baseline wins until the older document is migrated.

## Formal Decisions

- [ADR Index](./adr/README.md)
- [ADR-001: Railway-Oriented Programming with r[T]](./adr/001-railway-oriented-programming.md)
- [ADR-002: v0.13.0 Platform Baseline](./adr/002-v0-13-0-platform-baseline.md)

## Supporting Architecture References

These documents remain useful as supporting material, but they are not the governing baseline:

- [Overview](./overview.md)
- [Clean Architecture](./clean-architecture.md)
- [FLEXT Service Architecture](./flext-service-architecture.md)
- [FLEXT CQRS Architecture](./flext-cqrs-architecture.md)
- [Arc42 Architecture Set](./arc42/README.md)
- [C4 Model Set](./c4-model/README.md)

## Historical and Supporting Notes

The older architecture documents in this directory should now be treated as:

- historical descriptions
- supporting references
- migration context

They are not the forward source of truth for:

- public class names
- DI ownership
- registry and catalog semantics
- project naming
- workspace taxonomy

For implementation work targeting `0.13.0`, start with:

1. [FLEXT Workspace Baseline v0.13.0](./baseline-v0.13.0.md)
2. [ADR-002: v0.13.0 Platform Baseline](./adr/002-v0-13-0-platform-baseline.md)
3. [Migration to v0.13.0](../guides/migration-to-v0.13.0.md)
