# Phase 1: Type System Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 01-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-23
**Phase:** 01-type-system-hardening
**Mode:** --auto (Claude-selected recommended defaults)
**Areas discussed:** Pyrefly entrypoint health, Error baseline strategy, Wave plan structure, TypeGuard migration, Scope exclusions

---

## Pyrefly Entrypoint Health

| Option | Description | Selected |
|--------|-------------|----------|
| Fix as first task in Wave 1 | Before any error measurement, fix `${PWD}` expansion in pyrefly search paths | ✓ |
| Defer to later wave | Attempt to measure errors with broken entrypoint | |

**Auto-selected:** Fix as first task in Wave 1 (prerequisite — can't measure progress without working tool)
**Notes:** Discovered via `make pyre` returning exit 1 with "Invalid search-path: /home/marlonsc/flext/${PWD}/flext-core/src does not exist"

---

## Error Baseline Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Use historical 4,385 figure | Proceed with pre-Wave 0 sisyphus analysis numbers | |
| Establish fresh baseline first | Run `make pyre` (after fix) + per-project checks to get current counts | ✓ |

**Auto-selected:** Fresh baseline (historical numbers are stale; Wave 0 may have reduced the count)
**Notes:** Wave 0 completed "pyrefly entrypoint, legacy artifacts, 27 test fixes" — actual current count unknown

---

## Wave Plan Structure

| Option | Description | Selected |
|--------|-------------|----------|
| Keep existing D-01 through D-06 | Wave-based: core → infra+tests → cli solo → consumers | ✓ |
| Reorganize by error category | Separate passes for **class**, cast(), Any, object | |

**Auto-selected:** Keep existing decisions (already well-reasoned in prior context)
**Notes:** Added D-07 (pyre entrypoint fix) and D-08 (fresh baseline) as new locked decisions

---

## TypeGuard → TypeIs (TYPE-07)

| Option | Description | Selected |
|--------|-------------|----------|
| Separate final micro-plan | After main waves, sweep all 12 functions | ✓ |
| Fold into each wave | Handle TypeGuard functions in-situ per project | |

**Auto-selected:** Separate final micro-plan (keeps wave complexity manageable)

---

## Scope Exclusions

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude algar-oud-mig | 370 errors but not in flext-sh org scope | ✓ |
| Include algar-oud-mig | Fix all projects | |

**Auto-selected:** Exclude (explicitly out of scope per project charter)

---

## Claude's Discretion

- Per-project sequencing within each wave (within dependency constraints)
- Boundary between "small consumers" and "remaining consumers" in final wave
- Exact fix approach for `${PWD}` pyrefly search-path issue (use relative paths or absolute with resolved root)

## Deferred Ideas

None captured during this session.
