# Phase 2: Architecture & SOLID - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 02-architecture-solid
**Areas discussed:** Plan Decomposition, Field Migration Scope, ABC→Protocol Strategy, TypeAdapter Caching
**Mode:** Auto (all decisions auto-selected with recommended defaults)

---

## Plan Decomposition

| Option | Description | Selected |
|--------|-------------|----------|
| Wave-based (core→consumers) | Same project-cascade approach as Phase 1 | |
| Requirement-based waves | Group by requirement cluster (protocols→Field→aliases) | ✓ |
| Per-requirement plans | One plan per ARCH requirement | |

**User's choice:** [auto] Requirement-based waves
**Notes:** Phase 2 requirements are independent unlike Phase 1's cascading type errors. Protocols change signatures (do first), Field migration is mechanical (do second), aliases/imports are cleanup (do last).

---

## Field Migration Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Production only | ~1,100 Field() usages in src/ | |
| All including tests | ~1,551 Field() usages across src/ and tests/ | ✓ |

**User's choice:** [auto] All including tests
**Notes:** Sisyphus plan confirms tests in scope. PrivateAttr (94 usages) explicitly excluded.

---

## ABC→Protocol Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Blocking Wave 0 | Fix 6 issubclass() calls before any ABC conversion | ✓ |
| Inline with ABC wave | Fix issubclass() as encountered during conversion | |

**User's choice:** [auto] Blocking Wave 0 prerequisite
**Notes:** issubclass() with Protocol can fail at runtime if not @runtime_checkable. Safer to fix first.

---

## TypeAdapter Caching

| Option | Description | Selected |
|--------|-------------|----------|
| ClassVar on owning class | Cache as ClassVar on the model/class that uses it | ✓ |
| Module-level constants | Cache as module-level constant | |
| Mixed approach | ClassVar for class-bound, module for shared | |

**User's choice:** [auto] ClassVar on owning class
**Notes:** Keeps adapter co-located with its model. Follows existing caching pattern in flext-core.

---

## Claude's Discretion

- Wave-internal project sequencing and parallelism
- ast-grep rule design for mechanical migrations
- Batching strategy for small consumer projects

## Deferred Ideas

- Dispatcher hot-path optimization → Phase 3
- Protocol introspection caching → Phase 3
- Pydantic v2 governance doc → post-Phase 2
- CI performance benchmarks → Phase 3
