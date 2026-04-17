# Phase 7: Modernization & Integration Fixes - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Fix cross-phase integration breakage (circular import in `_utilities_loader.py`, StrEnum + strict Pydantic coercion mismatch) and complete deferred Python 3.13 modernization (replace custom deprecation framework with PEP 702, eliminate UserDict/UserString). Four tightly-scoped technical fixes with measurable pass/fail criteria.

</domain>

<decisions>
## Implementation Decisions

### Circular import resolution (INFRA-05)

- **D-01:** Break the circular import in `flext-infra/src/flext_infra/refactor/_utilities_loader.py` — module-level `from flext_infra import c,m,p,u` during lazy init causes 12 test collection failures and breaks `make pyre`
- **D-02:** Preferred approach: lazy/deferred imports inside functions, or restructure to avoid the cycle. TYPE_CHECKING guard acceptable if the import is only needed for type annotations.

### StrEnum coercion fix

- **D-03:** Fix StrEnum + strict Pydantic coercion mismatch — `FlextModels.Value` has `strict=True` (from Phase 2 ARCH-03), Phase 4 converted `Format` to StrEnum, call sites pass string literals instead of enum instances
- **D-04:** Fix at call sites first (pass enum instances). If too many call sites, add `m.BeforeValidator` coercion on the affected model fields. Do NOT relax `strict=True` globally — that was a deliberate Phase 2 decision.

### Deprecation framework (MOD-02)

- **D-05:** Replace `FlextUtilitiesDeprecation` in `flext-core/src/flext_core/_utilities/deprecation.py` with `warnings.deprecated` (PEP 702, Python 3.13 stdlib)
- **D-06:** No wrapper needed — use `@warnings.deprecated` decorator directly. Remove the custom class entirely.

### UserDict/UserString elimination (MOD-06)

- **D-07:** Replace any `UserDict`/`UserString` subclasses with Pydantic `BaseModel`. Grep shows zero current usages in `flext-*/src/` — verify and mark complete if already done.

### Claude's Discretion

- Exact import restructuring strategy for the circular import
- Whether to use `m.BeforeValidator` or fix call sites for StrEnum coercion
- How to migrate existing `@deprecated` decorators to PEP 702 form
- Test file adjustments needed for each fix

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Circular import

- `flext-infra/src/flext_infra/refactor/_utilities_loader.py` — The file with the circular import (line 18)
- `.planning/v1.0-MILESTONE-AUDIT.md` — Audit that identified this gap (integration issue #1)

### StrEnum coercion

- `.planning/v1.0-MILESTONE-AUDIT.md` — Audit that identified this gap (integration issue #2)
- `flext-core/src/flext_core/_models/` — Where `FlextModels.Value` with `strict=True` lives

### Deprecation framework

- `flext-core/src/flext_core/_utilities/deprecation.py` — Custom deprecation framework to replace
- `flext-core/src/flext_core/utilities.py` — Facade that exports deprecation utilities

### Requirements

- `.planning/REQUIREMENTS.md` — MOD-02, MOD-06, INFRA-05 definitions

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `flext-core/_utilities/deprecation.py`: Custom deprecation framework — to be replaced, not reused
- `warnings.deprecated` (PEP 702): stdlib replacement available in Python 3.13

### Established Patterns

- `strict=True` on Pydantic models is a deliberate Phase 2 decision — do not relax
- StrEnum with `@unique` decorator is the Phase 4 standard
- Lazy imports via `TYPE_CHECKING` guard used elsewhere in the codebase

### Integration Points

- `_utilities_loader.py` is imported by flext-infra's refactor module — fixing this unblocks 12 test collections
- StrEnum coercion fix touches `flext-tests` test suite (85 tests)
- Deprecation framework is exported through `flext-core` public API (`FlextUtilities` namespace)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — all items have clear technical definitions from the milestone audit.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-modernization-integration-fixes*
*Context gathered: 2026-03-24*
