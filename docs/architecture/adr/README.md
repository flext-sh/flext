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

<<<<<<< HEAD
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
=======
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
- [ADR-008: Neutral consumer boundaries for docs, Office bytes, and artifact
  metadata](008-neutral-consumer-boundaries.md) — _Accepted_
- [ADR-009: Ecosystem coordination and reusable-library evaluation](009-ecosystem-coordination-and-library-evaluation.md)
  — _Accepted (planning, `0.20.0-dev`)_
- [ADR-010: Unified project standardization (Make, scripts, tests, structure) via
  codegen](010-unified-project-standardization-via-codegen.md) - _Accepted and active, `0.12.0-dev`; forward baseline `0.13.0`_
- [ADR-014: Family Part Shape, Rope, Codemod Rules](014-family-part-shape-rope-codemod-rules.md) — _Accepted, on-disk unindexed until this change_
- [ADR-015: Consumer Consumption Law (R1-R6)](015-consumer-consumption-law.md) — _Accepted, `0.12.0-dev` line_
- [ADR-016: Settings/Config Singleton Contract](016-settings-config-singleton-contract.md) — _Proposed (unimplemented, `0.12.0-dev` line)_
- [ADR-017: Parametrized Rule Surfaces and the Single Modernize CLI](017-parametrized-rule-surfaces-single-modernize-cli.md) — _Accepted (evolving per cycle), `0.12.0-dev` line_

> **Note**: ADR-011/012 exist only on `0.20.0-dev` line (forward baseline); collision risk recorded. ADR-016 indexes the settings/config singleton contract on this line. On `0.12.0-dev`, the config/settings canonical pattern is owned by ADR-005 (§1–§2) plus the `_settings.py`/`_config.py` module docstrings — citations formerly pointing to "ADR-012 (config/settings canonical pattern)" were repointed there (`flext-z0zkq`, 2026-09-11); on the forward line ADR-012 is worktree transaction performance (= ADR-007 here).
>>>>>>> origin/0.12.0-dev

**Execution authority (2026-09-17):** Gas City Bead `flext-itpd1.2` owns the
live modernization state. The versioned resume route is
`docs/ways-of-working/stabilization-checkpoint-0.12.md`; workspace-local plans
remain session evidence only.

**Runtime status (2026-09-17):** the `0.12.0-dev` line is **not globally green**. `make check`/`make test` have no proven green run on the current integration tip; ADR-010's verification contract (zero drift, zero findings, two consecutive green `make gen` runs) is a target, not a recorded state. Do not cite these ADRs as proof of a green baseline.

New ADRs should be added only when they represent a real architectural decision with an owning implementation path.
