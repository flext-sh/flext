# Phase 2: Architecture & SOLID - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Enforce Dependency Inversion Principle via protocols across all 33 projects, canonicalize Pydantic v2 Field() patterns, convert ABCs to Protocols where appropriate, cache TypeAdapter instances, fix mutable defaults, adopt PEP 695 type aliases, and normalize test/example/script imports. Covers ARCH-01 through ARCH-08. No new features, no workaround eradication (Phase 3), no stdlib modernization (Phase 4).

Pre-conditions from Phase 1:
- Type system is clean: 0 pyrefly errors, 0 pyright errors, 0 typing shortcuts
- `algar-oud-mig` remains excluded from scope

</domain>

<decisions>
## Implementation Decisions

### Plan Decomposition
- **D-01:** Phase 2 uses **requirement-based waves**, not project-based waves. Unlike Phase 1 (where errors cascaded project-to-project), Phase 2 requirements are largely independent: protocols (ARCH-01/04/05), Field migration (ARCH-03/06/07), type aliases (ARCH-08), import normalization (ARCH-02). Each wave targets a requirement cluster.
- **D-02:** Wave order: (0) issubclass() prerequisite fixes → (1) Protocol DIP enforcement (ARCH-01, ARCH-04, ARCH-05) → (2) Pydantic v2 Field() canonicalization (ARCH-03, ARCH-06, ARCH-07) → (3) PEP 695 type aliases + import normalization (ARCH-08, ARCH-02).
- **D-03:** Researchers and planners MUST read the existing `.sisyphus` plans as reference input — they contain audits, counts, and proven ast-grep patterns. Do not re-derive what's already documented.

### issubclass() Prerequisite (Wave 0)
- **D-04:** 6 `issubclass()` calls in flext-core must be refactored to Protocol-safe patterns BEFORE any ABC→Protocol conversion. This is a **blocking prerequisite** (Wave 0). The sisyphus plan identifies all 6 call sites.

### Field() Migration Scope
- **D-05:** All ~1,551 `Field(...)` usages are in scope, **including tests**. `PrivateAttr()` (94 usages) is explicitly **excluded** — it is not a Field pattern.
- **D-06:** Migration pattern: `x: T = Field(...)` → `x: Annotated[T, Field(...)]`. For optional fields: `x: T | None = Field(...)` → `x: Annotated[T | None, Field(...)]` (NOT `Annotated[T, Field(...)] | None`).

### ABC→Protocol Conversion
- **D-07:** 6 pure ABCs → `@runtime_checkable` Protocol (full conversion). 8 template ABCs → extract Protocol interface to `protocols.py` + retain concrete base class. 5 ABCs retained as-is (load-bearing inheritance). Per sisyphus plan audit.
- **D-08:** `p.Base`, `p.HasModelDump`, `p.Handler` are FROZEN — they have isinstance/inheritance usage and must NOT be modified.

### TypeAdapter Caching
- **D-09:** ~100 inline `TypeAdapter()` instantiations cached as `ClassVar` on the owning class. ~40 already-cached instances left as-is. 5 dynamic instances accepted (cannot be cached). Most repeated pattern: `TypeAdapter(dict[str, object])` (11 instances across 6 files).

### PEP 695 Type Aliases
- **D-10:** All remaining `TypeAlias` assignments migrated to `type X = ...` form (PEP 695). 1,271 already use PEP 695 — this wave catches stragglers.

### Import Normalization
- **D-11:** `c,m,t,u,p` in `tests/`, `examples/`, `scripts/` must import from local namespace root (e.g., `from tests import c, m, t`) — never from `flext_core` directly. Per ARCH-02.

### Claude's Discretion
- Within each wave, the exact sequencing and parallelism of individual projects is at Claude's discretion (respecting dependency order: flext-core → flext-infra → consumers).
- The ast-grep rule design for Field() migration and protocol substitution is at Claude's discretion, informed by the sisyphus plan patterns.
- Whether to batch small consumer projects or handle them individually within a wave.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Sisyphus Plans (reference input — use as basis for GSD planning)
- `.sisyphus/plans/protocol-solid-standardization.md` — DIP enforcement: protocol mapping table, 6 waves, ast-grep rules, 12 DIP violations in flext-core, 23 in consumers
- `.sisyphus/plans/pydantic-v2-advanced-modernization.md` — Field() migration (1,551 usages), ABC audit (19 ABCs: 6 pure, 8 template, 5 retain), TypeAdapter audit (451 matches, ~100 inline), mutable defaults (13), dispatcher hot-path
- `.sisyphus/plans/flext-core-typing-simplification.md` — Literal/StrEnum dedup, protocol simplification, type alias cleanup
- `.sisyphus/plans/typing-protocol-simplification.md` — Protocol simplification patterns

### Requirements
- `.planning/REQUIREMENTS.md` §ARCH — ARCH-01 through ARCH-08 definitions and acceptance criteria
- `.planning/ROADMAP.md` §Phase 2 — Success criteria (5 criteria) that define done

### Prior Phase Context
- `.planning/phases/01-type-system-hardening/01-CONTEXT.md` — Phase 1 decisions (type system now clean)

### Governance
- `AGENTS.md` §10.2 — FROZEN file policy
- `AGENTS.md` §3 — MRO and namespace conventions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- 334 Protocol definitions across 25 files — extensive protocol infrastructure already in place
- 1,271 PEP 695 type aliases already in use — migration is catching stragglers
- ast-grep rules from Phase 1 — mechanical refactoring patterns proven
- `make codegen` — regenerates `__init__.py` exports after any protocol/model changes

### Established Patterns
- MRO namespace composition: `FlextXyzProtocols(FlextCoreProtocols)` inheritance chain
- `@runtime_checkable` on all flext-core protocols — safe for isinstance and Pydantic
- Dependency order: flext-core → flext-infra → flext-tests → consumers
- `__init__.py` autogenerated — never hand-edit

### Integration Points
- `make check PROJECT=<name> CHECK_GATES=pyrefly,pyright` — per-project validation
- `make pyre` — repo-wide pyrefly (now working after Phase 1)
- `make codegen` — MANDATORY after protocol/model/constants changes
- `make test PROJECT=<name>` — per-project test suite

</code_context>

<specifics>
## Specific Requirements

- `PrivateAttr()` (94 usages) is NOT in scope for Field() migration — it's a different pattern.
- `Mapping.register(_RootDictModel)` is excluded from ABC conversion scope.
- Factory methods that MUST return concrete types (e.g., `FlextContext.create()`) keep concrete return types — DIP applies to parameters and non-factory return types.
- `p.Base`, `p.HasModelDump`, `p.Handler` are FROZEN protocols — do not modify.
- PEP 702 `@deprecated` is NOT in scope for Phase 2 — it was assessed and deferred.

</specifics>

<deferred>
## Deferred Ideas

- Dispatcher hot-path optimization (pre-resolve at registration) — considered but fits better in Phase 3 (Infrastructure Centralization) alongside other runtime improvements.
- Protocol introspection caching (3 cache layers) — 0 production callers, defensive only. Defer to Phase 3.
- Pydantic v2 governance guideline document — defer to after Phase 2 completion.
- CI performance benchmarks for TypeAdapter caching — defer to Phase 3.

</deferred>

---

*Phase: 02-architecture-solid*
*Context gathered: 2026-03-24*
