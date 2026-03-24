# Phase 3: Infrastructure Centralization - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 03-infrastructure-centralization
**Areas discussed:** Execution ordering, CLI bootstrap centralization, Workaround scope definitions, Policy gate enforcement
**Mode:** --auto (all decisions auto-selected from recommended defaults)

---

## Execution Ordering

| Option | Description | Selected |
|--------|-------------|----------|
| INFRA first, then WA | Centralized helpers must exist before workarounds can use them | ✓ |
| WA first, then INFRA | Fix violations first, centralize after | |
| Interleaved | Mix INFRA and WA tasks | |

**User's choice:** [auto] INFRA first, then WA (recommended default — dependency order)
**Notes:** Centralized `run_cli` and `iter_projects` are prerequisites for clean workaround fixes.

---

## CLI Bootstrap Centralization

| Option | Description | Selected |
|--------|-------------|----------|
| Single `u.Infra.run_cli()` with Pydantic typed CLI model | Type-safe, canonical, matches codebase patterns | ✓ |
| Shared argparse builder only | Less invasive but still uses loose types | |

**User's choice:** [auto] Pydantic-typed CLI model (recommended — matches project's strict typing policy)
**Notes:** Follows existing sisyphus plan `cli-infra-standardization.md`.

---

## Workaround Scope Definitions

| Option | Description | Selected |
|--------|-------------|----------|
| Per-category sweep (all projects per workaround type) | Simpler planning, consistent fix patterns | ✓ |
| Per-project sweep (all workarounds per project) | Fewer cross-project commits | |

**User's choice:** [auto] Per-category sweep (recommended — ensures consistent patterns across all projects)
**Notes:** Each WA category (01-06) gets its own plan with consistent fix pattern applied to all 33 projects.

---

## Claude's Discretion

- Internal decomposition of centralized utilities
- Exception type hierarchy for WA-03
- NamespaceSourceDetector architecture
- Batching strategy within plans

## Deferred Ideas

None.
