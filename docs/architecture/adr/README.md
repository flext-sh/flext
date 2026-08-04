# ADR Index

<!-- TOC START -->
- [Published ADRs](#published-adrs)
- [Make work lane saga](#make-work-lane-saga)
<!-- TOC END -->

<!-- mro-wkii.17.7 (agent: codex) — keep ADR pointers aligned with the accepted conform architecture. -->

This directory contains the accepted Architecture Decision Records that are currently published in the root FLEXT
portal.

## Published ADRs

- [ADR-001: Railway-Oriented Programming with r[T]](001-railway-oriented-programming.md)
- [ADR-002: v0.13.0 Platform Baseline](002-v0-13-0-platform-baseline.md)
- [ADR-003: Manifest-owned topology, root workspace, and autonomous Git
  libraries](003-workspace-tooling-hub-distribution.md)
- [ADR-004: Generated Make and codegen SSOT owned by `flext-infra`](004-generic-make-framework-in-flext-tests.md)
- [ADR-005: Config, settings, constants, templates, and schemas
  SSOT](005-config-settings-constants-templates-schemas-ssot.md)
- [ADR-006: Thin Domain Drivers over flext-meltano Bases + Action
  Libraries](006-thin-domain-drivers-over-meltano-bases.md) — _Accepted_
- [ADR-007: Performance optimization of worktree transactions and mutating CLI
  commands](007-worktree-transaction-performance.md) — _Accepted_
- [ADR-0016: Public make work lane saga](016-make-work-lane-saga.md) — _Accepted_
- [ADR-008: Neutral consumer boundaries for docs, Office bytes, and artifact
  metadata](008-neutral-consumer-boundaries.md) — _Accepted_
- [ADR-009: Ecosystem coordination and reusable-library evaluation](009-ecosystem-coordination-and-library-evaluation.md)
  — _Accepted (planning, `0.20.0-dev`)_
- [ADR-010: Unified project standardization (Make, scripts, tests, structure) via
  codegen](010-unified-project-standardization-via-codegen.md) — _Accepted (0.12
  compatibility subset; forward architecture on `0.20.0-dev`)_

New ADRs should be added only when they represent a real architectural decision with an owning implementation path.

## Make work lane saga

Public lane lifecycle is `make work WHAT=start|status|land|finish` (flext-infra `FlextInfraWorkService`). Worktree add/update/remove remains an internal engine only. Operator guide: [make-commands.md](../../guides/make-commands.md#work-saga).
