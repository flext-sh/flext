# ADR Index

<!-- TOC START -->

- [Published ADRs](#published-adrs)

<!-- TOC END -->

<!-- mro-wkii.17.7 (agent: codex) — keep ADR pointers aligned with the accepted conform architecture. -->

This directory contains the accepted Architecture Decision Records that are currently
published in the root FLEXT portal.

Catalog classifications describe recorded decision maturity, not fresh runtime receipts.
Historical implementation labels require revalidation on the current integrated
candidate; acceptance never proves fleet stability.

**Status classification:**

- **CURRENT IMPLEMENTATION** — decision is implemented and active in the current tree.
- **ACCEPTED TARGET** — decision is accepted; implementation targets a forward line or
  is in progress.
- **PROPOSED** — decision is proposed, not yet accepted.

## Published ADRs

- [ADR-001: Railway-Oriented Programming with r[T]](001-railway-oriented-programming.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-002: v0.13.0 Platform Baseline](002-v0-13-0-platform-baseline.md) —
  **ACCEPTED TARGET** (forward baseline `0.13.0`)
- [ADR-003: Manifest-owned topology, root workspace, and autonomous Git libraries](003-workspace-tooling-hub-distribution.md)
  — **CURRENT IMPLEMENTATION** (§1 superseded by ADR-024: `.gitmodules` owns composition)
- [ADR-004: Generated Make and codegen SSOT owned by `flext-infra`](004-generated-make-codegen-ssot-flext-infra.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-005: Config, settings, constants, templates, and schemas SSOT](005-config-settings-constants-templates-schemas-ssot.md)
  — **CURRENT IMPLEMENTATION** (§§1–5); **ACCEPTED TARGET** (§6 enforcement migration)
- [ADR-006: Thin Domain Drivers over flext-meltano Bases + Action Libraries](006-thin-domain-drivers-over-meltano-bases.md)
  — **ACCEPTED TARGET** (pilot realized; rollout in progress)
- [ADR-007: Performance optimization of worktree transactions and mutating CLI commands](007-worktree-transaction-performance.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-008: Neutral consumer boundaries for docs, Office bytes, and artifact metadata](008-neutral-consumer-boundaries.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-009: Ecosystem coordination and reusable-library evaluation](009-ecosystem-coordination-and-library-evaluation.md)
  — **ACCEPTED TARGET** (`0.20.0-dev` line)
- [ADR-010: Unified project standardization (Make, scripts, tests, structure) via codegen](010-unified-project-standardization-via-codegen.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-014: Family Part Shape, Rope, Codemod Rules](014-family-part-shape-rope-codemod-rules.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-015: Consumer Consumption Law (R1-R6)](015-consumer-consumption-law.md) —
  **CURRENT IMPLEMENTATION**
- [ADR-016: Settings/Config Singleton Contract](016-settings-config-singleton-contract.md)
  — **PROPOSED**
- [ADR-017: Parametrized Rule Surfaces and the Single Modernize CLI](017-parametrized-rule-surfaces-single-modernize-cli.md)
  — **ACCEPTED TARGET** (`make mod` wired; `flext-infra/config/rules/mod/` exists;
  distribution/migration acceptance remains unproved)
- [ADR-018: Generator Declarations Law](018-generator-declarations.md) — **ACCEPTED**
  (operator law 2026-09-20; rule owner: global governance rule
  `flext/generator-declarations` in the `agents-governance` catalog; phased under
  `flext-0in0k`)
- [ADR-019: Service Contract — Protocol Ports, Explicit Composition Root, Typed Operations](019-service-contract-ports-operations.md)
  — **PROPOSED** (operator-approved plan V8, 2026-09-25; phased under `flext-4jtcb`)
- [ADR-021: Mandatory Unsafe-Fix Lint Repair Channel](021-mandatory-unsafe-fix-lint-repair-channel.md)
  — **ACCEPTED** (operator law 2026-10-05: `make fix` always runs
  `ruff check --fix --unsafe-fixes --preview`; `MakeRuffSpec` requires the flag;
  supersedes the 2026-09-08 safe-only posture)
- [ADR-022: External Consumers as Propagation Guests](022-external-consumers-propagation-guests.md)
  — **SUPERSEDED** by ADR-024 (a workspace never lists or pushes into its consumers)
- [ADR-023: Repair Phases as Mod-Loop Callbacks](023-repair-phases-mod-loop-callbacks.md)
  — **ACCEPTED** (`p.Infra.ModLoopPhase`; namespace-relocations + accessor-rename
  inside `refactor mod`'s joint fixed point; one engine per repair, three invocation
  surfaces)
- [ADR-024: DI Config Contract — Derived Defaults, Self-Only Minimal Overrides, Generated Commented Defaults](024-di-config-contract-derived-defaults-minimal-overrides.md)
  — **ACCEPTED TARGET** (operator order 2026-10-08; a repository declares only its own
  deltas; library ships generic defaults; injected root with library < repo < local
  layers; pull never push; phased under `flext-itpd1.11`)

> **Historical numbering evidence:** the recorded `0.20.0-dev` catalog associates
> ADR-011/012 with the forward line and ADR-012 with worktree transaction performance
> (ADR-007 here). That remote catalog was not revalidated in this reconciliation; the
> collision warning remains. This local catalog has no ADR-011, ADR-012 or ADR-013 files
> (none ever existed in this repository's history). ADR-016 indexes the proposed
> settings/config singleton contract; ADR-005 (§1–§2) and the
> `_settings.py`/`_config.py` owner docstrings define the canonical pattern on this
> line. The historical citation correction remains attributed to `flext-z0zkq`
> (2026-09-11).

**Recovery ownership (2026-09-17):** `flext-itpd1.3` coordinates the current cycle under
`flext-itpd1`; sibling owners are `flext-itpd1.2` (documentation) and `flext-itpd1.4`
(Make machinery). Beads records execution state, not runtime truth. See the
[stabilization runbook](../../ways-of-working/stabilization-checkpoint-0.12.md).
Local/private plans remain session context, never automatic authority or publication
sources; only actual consumer and gate receipts prove behavior.

**Runtime status (2026-09-17):** fleet stability on `0.12.0-dev` is **unproved**.
ADR-010's verification contract (zero drift, zero findings, consecutive no-op
generation) is an acceptance requirement, not a fresh receipt. Do not cite this catalog
as proof of a green baseline.

New ADRs should be added only when they represent a real architectural decision with an
owning implementation path.
