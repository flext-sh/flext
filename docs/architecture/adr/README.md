# ADR Index

<!-- TOC START -->
- [Published ADRs](#published-adrs)
<!-- TOC END -->

<!-- mro-wkii.17.7 (agent: codex) — keep ADR pointers aligned with the accepted conform architecture. -->

This directory contains the accepted Architecture Decision Records that are currently published in the root FLEXT
portal.

**Status classification:**

- **CURRENT IMPLEMENTATION** — decision is implemented and active in the current tree.
- **ACCEPTED TARGET** — decision is accepted; implementation targets a forward line or is in progress.
- **PROPOSED** — decision is proposed, not yet accepted.

## Published ADRs

- [ADR-001: Railway-Oriented Programming with r[T]](001-railway-oriented-programming.md) — **CURRENT IMPLEMENTATION**
- [ADR-002: v0.13.0 Platform Baseline](002-v0-13-0-platform-baseline.md) — **ACCEPTED TARGET** (forward baseline `0.13.0`)
- [ADR-003: Manifest-owned topology, root workspace, and autonomous Git libraries](003-workspace-tooling-hub-distribution.md) — **CURRENT IMPLEMENTATION**
- [ADR-004: Generated Make and codegen SSOT owned by `flext-infra`](004-generic-make-framework-in-flext-tests.md) — **CURRENT IMPLEMENTATION**
- [ADR-005: Config, settings, constants, templates, and schemas SSOT](005-config-settings-constants-templates-schemas-ssot.md) — **CURRENT IMPLEMENTATION** (§§1–5); **ACCEPTED TARGET** (§6 enforcement migration)
- [ADR-006: Thin Domain Drivers over flext-meltano Bases + Action Libraries](006-thin-domain-drivers-over-meltano-bases.md) — **ACCEPTED TARGET** (pilot realized; rollout in progress)
- [ADR-007: Performance optimization of worktree transactions and mutating CLI commands](007-worktree-transaction-performance.md) — **CURRENT IMPLEMENTATION**
- [ADR-008: Neutral consumer boundaries for docs, Office bytes, and artifact metadata](008-neutral-consumer-boundaries.md) — **CURRENT IMPLEMENTATION**
- [ADR-009: Ecosystem coordination and reusable-library evaluation](009-ecosystem-coordination-and-library-evaluation.md) — **ACCEPTED TARGET** (`0.20.0-dev` line)
- [ADR-010: Unified project standardization (Make, scripts, tests, structure) via codegen](010-unified-project-standardization-via-codegen.md) — **CURRENT IMPLEMENTATION**
- [ADR-014: Family Part Shape, Rope, Codemod Rules](014-family-part-shape-rope-codemod-rules.md) — **CURRENT IMPLEMENTATION**
- [ADR-015: Consumer Consumption Law (R1-R6)](015-consumer-consumption-law.md) — **CURRENT IMPLEMENTATION**
- [ADR-016: Settings/Config Singleton Contract](016-settings-config-singleton-contract.md) — **PROPOSED**
- [ADR-017: Parametrized Rule Surfaces and the Single Modernize CLI](017-parametrized-rule-surfaces-single-modernize-cli.md) — **ACCEPTED TARGET** (make mod implemented; config/rules/ tree in progress)

New ADRs should be added only when they represent a real architectural decision with an owning implementation path.
