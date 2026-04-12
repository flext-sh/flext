# Phase 6: Typing Gap Closure - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate all TypeGuard functions to TypeIs (PEP 742) and annotate all empty container literals at their assignment sites. This closes the 2 remaining typing requirements (TYPE-07, TYPE-08) from the v1.0 milestone audit.

</domain>

<decisions>
## Implementation Decisions

### TypeGuard → TypeIs Migration (TYPE-07)
- **D-01:** All 12 TypeGuard functions across the monorepo must be converted to TypeIs (PEP 742). TypeIs narrows in both branches (true AND false), which is strictly more useful than TypeGuard's true-only narrowing.
- **D-02:** Import `TypeIs` from `typing` (Python 3.13 stdlib) — not from `typing_extensions`.
- **D-03:** Each converted function must pass pyrefly and pyright strict checks.

### Empty Container Annotations (TYPE-08)
- **D-04:** All empty container literals (`[]`, `{}`, `set()`) at assignment sites must have explicit type annotations. Pattern: `items: list[SomeType] = []` not `items = []`.
- **D-05:** Use the most specific type from `t.*` contracts where applicable (e.g., `t.RecursiveContainerList`, `t.RecursiveContainerMapping`).

### Claude's Discretion
- Ordering and grouping of changes within tasks
- Whether to batch small changes or commit per-file

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Type System
- `AGENTS.md` — Naming conventions, typing rules, t.* contracts
- `flext-core/src/flext_core/_typings/` — Type alias definitions
- `flext-core/src/flext_core/_utilities/guards.py` — Primary location of TypeGuard functions

### Audit
- `.planning/v1.0-MILESTONE-AUDIT.md` — Gap details for TYPE-07, TYPE-08

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- TypeGuard functions are concentrated in `flext-core/src/flext_core/_utilities/guards.py` and scattered in a few consumer projects
- `t.*` type contracts are well-established and should be used for container annotations

### Established Patterns
- All type aliases use PEP 695 `type X = ...` syntax
- Imports from `typing` stdlib (Python 3.13), not `typing_extensions`

### Integration Points
- TypeIs changes affect all downstream projects that import guard functions from flext-core

</code_context>

<specifics>
## Specific Ideas

No specific requirements — straightforward mechanical migration with strict type checking validation.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-typing-gap-closure*
*Context gathered: 2026-03-24*
