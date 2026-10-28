# ADR Index

<!-- TOC START -->

- [Published ADRs](#published-adrs)
- [Release and forward-planning boundaries](#release-and-forward-planning-boundaries)

<!-- TOC END -->

<!-- mro-wkii.17.7 (agent: codex) — keep ADR pointers aligned with the accepted conform architecture. -->

This directory contains Architecture Decision Records that are currently
published in the root FLEXT portal.

Read the [governance authority route](../../GOVERNANCE.md#authority) and
[engineering conformance review](../../GOVERNANCE.md#engineering-conformance-review)
before applying an ADR. Operator and universal governance remain higher authority. For
technical design, the accepted ADR that owns the topic is the precise decision source;
root and member `AGENTS.md` files route and enforce that decision, while skills and
supporting docs consume it without creating a competing design. Beads own work scope,
ownership, status, and evidence, not architecture. Proposed ADRs are not accepted
contracts, and an accepted ADR is not proof that its implementation is complete. Record
implementation and acceptance evidence in Beads. `TODO.md` is a generated Beads
projection; update its owner, never the projection by hand.

Catalog classifications describe recorded decision maturity, not fresh runtime receipts.
Historical implementation labels require revalidation on the current integrated
candidate; acceptance never proves fleet stability.

**Status classification:**

- **CURRENT IMPLEMENTATION** — recorded implementation classification; revalidate its
  current scope and runtime on the candidate before using it as acceptance evidence.
- **ACCEPTED TARGET** — decision is accepted; implementation targets a forward line or
  is in progress.
- **PROPOSED** — decision is proposed, not yet accepted.
- **ACCEPTED** — recorded policy/decision acceptance; not a claim that its rollout or
  validation is complete.
- **SUPERSEDED** — historical decision replaced by the named successor, not live law.

## Published ADRs

- [ADR-001: Railway-Oriented Programming with r[T]](001-railway-oriented-programming.md)
  — **CURRENT IMPLEMENTATION**
- [ADR-002: v0.13.0 Platform Baseline](002-v0-13-0-platform-baseline.md) —
  **ACCEPTED TARGET** (forward baseline `0.13.0`)
- [ADR-003: Manifest-owned topology, root workspace, and autonomous Git libraries](003-workspace-tooling-hub-distribution.md)
  — **CURRENT IMPLEMENTATION** (§1 superseded by ADR-024: `.gitmodules` owns composition;
  lock ownership in §3 and the verification contract superseded by ADR-030: member
  locks are kept and the workspace lock composes them)
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
  — **ACCEPTED TARGET** (unified `0.13.0` planning; historical origin `0.20.0-dev`;
  accepted-to-build, rejected and deferred feature verdicts preserved; no implementation
  receipt)
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
  (operator law 2026-09-20; authority routing reconciled 2026-10-26: branch-matched
  ADR-018 and local FLEXT law, not the retired global copy; phased under
  `flext-0in0k`; amended 2026-10-28 with single-read, single-batch transactional
  publication under campaign `flext-pipol`)
- [ADR-019: Service Contract — Protocol Ports, Explicit Composition Root, Typed Operations](019-service-contract-ports-operations.md)
  — **PROPOSED** (operator-approved plan V8, 2026-09-25; phased under `flext-4jtcb`)
- [ADR-020: Bun installs the npm-backed mise tools fleet-wide](020-npm-installer-bun.md)
  — **SUPERSEDED** by ADR-025 (the fleet toolchain has no npm backend)
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
- [ADR-025: The fleet toolchain has no npm backend](025-npm-free-fleet-toolchain.md)
  — **ACCEPTED** (operator approval 2026-10-08; ast-grep from aqua, rumdl formats
  markdown, setup installs only declared tools and proves each one; supersedes ADR-020;
  bead `flext-0shvv`)
- [ADR-026: Engine Federation — Unified Loop and Parametrized Rule Registry](026-engine-federation-unified-loop-kernel.md)
  — **PROPOSED** (campaign D1–D7, 2026-10-13; orchestration, registry, extraction and
  retirement proposals, not implementation receipts; preserves ast-grep mechanical fixes,
  Rope semantic refactors and LSP validation under current law; proposed supersession and
  amendments do not override authority; acceptance requires full inventory provenance,
  actual runtime and canonical gate evidence, not campaign closure)
- [ADR-027: Facade Single-Owner Law](027-facade-single-owner-law.md)
  — **PROPOSED** (implementation tracking: `flext-vjj1s.11`; no acceptance or rollout
  evidence is implied)
- [ADR-028: Facade Boundary — External Libraries, Orchestrators, Declarative Enforcement](028-facade-boundary-orchestrators-declarative-enforcement.md)
  — **ACCEPTED** (operator orders 2026-10-24/25; Decisions 15–19 are accepted technical
  contracts: [Decision 15](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15),
  [Decision 16](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16),
  [Decision 17](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17),
  and [Decision 18](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18).
  Implementation tracking: `flext-43iz8` for Decision 5 static-enforcement migration,
  `flext-1engx.15` for Decisions 16–17 and zero-quality exit, `flext-13s6n` for Decision
  18 rule projection. Decision 8 was amended 2026-10-28 (generated projections are
  gate-clean by construction, zero manual or automated post-adjustment; campaign
  `flext-pipol`). The external deprecation census `flext-1engx.11` applies to the
  Decision 7 compatibility window. These Beads track work; they do not establish
  completion.)
- [ADR-029: Always Working — One Complete Cycle Per Slice](029-always-working-one-complete-cycle.md)
  — **ACCEPTED** (operator orders 2026-10-24; the project and its runtime work 100% of
  the time; one active slice completes gen → fmt → fix → mod → check → tests, runtime
  proof and integration merge before anything else starts; nothing skipped or parked)
- [ADR-030: Member Locks, Workspace Lock Composition, and the Upgrade Guard](030-member-locks-composition-upg-guard.md)
  — **ACCEPTED** (operator ruling 2026-10-25, tracker memory
  `operator-ruling-2026-10-25-member-locks-uv-mise-upg-guard`; member `uv.lock` and
  `mise.lock` kept and formed by each member; the workspace lock is their
  composition; only `make upg` writes locks; exact SHA pinning; the upgrade guard is
  the target contract, implementation pending; supersedes the same-day root-only lock
  statements)

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

## Release and forward-planning boundaries

The [0.12 checkpoint](../../releases/latest.md) validates and publishes the existing
surface. Operational root aliases and current `core` facade behavior are not removed
by a forward ADR or a documentation-only reconciliation. Their proposed removal and
typed lazy `core` namespace redesign belong to the 0.13 contract/migration decision,
not to 0.12 release acceptance.

ADR-009's historical 0.20 coordination plan is retargeted to that same 0.13 planning
line, without promoting it to CURRENT IMPLEMENTATION. Static-consumer docs mode and
Office-byte completion remain accepted future work. Package extractions retain their
individual rejected, conditional or deferred verdicts. Retargeting is neither wholesale
feature approval nor a promise of a separate 0.20 delivery.

The supplied 2026-10-20 tracker evidence identifies `flext-ik359` as the open **0.13**
gate epic (old 0.20 name retired), waiting for publication work `flext-1wjg1` and separate
authorization. Approval of applicable contracts and the consumer migration matrix is
also required before the proposed migration. This ordering does not prohibit authorized
0.12 repairs or documentation work. It does not prove publication, current CI, completed
migration, or closure of either Bead; this index makes no tracker changes.

This bounded reconciliation does not certify the entire ADR corpus or companion docs.
In particular, `docs/architecture/ecosystem-coordination.md` and the ecosystem row in
`docs/GOVERNANCE.md` still carry historical 0.20 targeting. Their owner must reconcile
those references before claiming documentation-wide consistency. Existing dated notes
and implementation classifications elsewhere remain subject to candidate-specific
runtime and gate evidence.
