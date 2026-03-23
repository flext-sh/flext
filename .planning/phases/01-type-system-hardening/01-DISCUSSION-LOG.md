# Phase 1: Type System Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 01-CONTEXT.md — this log preserves the alternatives considered.

**Session:** 2026-03-23
**Mode:** Interactive (discuss)
**Areas discussed:** Plan decomposition, flext-cli sequencing, pyright scope, TypeGuard→TypeIs + empty containers

---

## Area 1: Plan Decomposition

**Q: How should GSD plans for Phase 1 be structured?**

Options presented:
- Follow sisyphus waves — one GSD plan per sisyphus wave, researcher reads existing plans directly
- **By project batch** ← SELECTED
- By error category — one plan per error type, maximizes intra-category parallelism

**Q: How granular should 'project batch' be? (33 projects total)**

Options presented:
- One plan per project — 33 plans, clear atomic units
- Small groups (3-5 projects/plan) — ~10 plans
- **Big waves (foundation / mid / consumers)** ← SELECTED — 3-4 plans total

**Captured decision:**
- D-01: Big wave organization: flext-core → flext-infra+tests → flext-cli (solo) → remaining consumers
- D-02: Each wave covers all error categories in one pass
- D-03: Researchers reference existing sisyphus plans as input

---

## Area 2: flext-cli Sequencing

**Q: When should flext-cli be tackled?**

Options presented:
- Last big-wave plan — natural dependency order
- **Dedicated solo plan before consumers** ← SELECTED — focused attention, after infra
- First, standalone plan — fastest metric wins but riskier

**Captured decision:**
- D-04: flext-cli gets its own dedicated plan between infra+tests wave and remaining consumers

---

## Area 3: Pyright Scope

**Q: Should Phase 1 require pyright 0 errors, or just pyrefly?**

Options presented:
- Pyrefly only — keep Phase 1 tight, pyright deferred
- **Both — pyright 0 errors is Phase 1** ← SELECTED — avoid two type-checker cleanup rounds

**Captured decision:**
- D-05: Phase 1 success = pyrefly 0 AND pyright 0. Both tools must pass per wave.

---

## Area 4: TypeGuard→TypeIs + Empty Containers

**Q: How to handle TypeGuard→TypeIs and empty container annotation?**

Options presented:
- Bundle into each project wave — one pass per project
- **Separate final micro-plan** ← SELECTED — main waves focus on error mass, micro-plan sweeps TYPE-07/08

**Captured decision:**
- D-06: Final separate micro-plan for all 12 TypeGuard→TypeIs rewrites + empty container annotations

---

*Generated: 2026-03-23*
