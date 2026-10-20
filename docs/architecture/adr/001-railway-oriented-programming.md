# ADR-001: Railway-Oriented Programming with `r[T]`

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Related Documents](#related-documents)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

**Status**: Accepted — CURRENT IMPLEMENTATION **Reviewed**: 2026-02-17

## Context

FLEXT needs one consistent contract for fallible operations across packages. The
platform should make success and failure explicit in signatures and keep error handling
composable.

## Decision

FLEXT uses `r[T]` as the canonical result contract for operations that can fail.

This means:

- business flows return `r[T]` instead of `T | None`
- error handling is composed explicitly instead of relying on exceptions as routine
  control flow
- success and failure paths stay visible at the call site

## Consequences

### Positive

- consistent result handling across the workspace
- clearer signatures for commands, services, and transformations
- easier composition of multi-step workflows

### Negative

- more explicit wrapping and unwrapping in some call sites
- developers must follow the result contract consistently

## Related Documents

- [Architecture baseline](../baseline-v0.13.0.md)
- [ADR index](README.md)
- `AGENTS.md`

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Preserve railway semantics; replace public `r` access with the target contract without fragmenting Result.
- This note records planning reconciliation only. It does not change the ADR's recorded maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
