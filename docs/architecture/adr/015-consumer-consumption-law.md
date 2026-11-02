# ADR-015: Consumer Consumption Law (R1-R6)

<!-- TOC START -->

- [Status](#status)
- [Context](#context)
- [Decision](#decision)
  - [Runtime alias inspection amendment](#runtime-alias-inspection-amendment)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Implementation](#implementation)
- [References](#references)

<!-- TOC END -->

## Status

ACCEPTED TARGET (ratified 2026-09-11; ownership reconciled 2026-10-20)

## Context

The FLEXT fleet (31+ `flext-*` packages) lacked a unified consumption standard.
Consumers imported internal machinery (`flext_cli.models`,
`flext_infra.workspace.detector`, `flext_core.lazy`), duplication went undetected across
consumer+family scope, gates had hardcoded thresholds and bypass lists, and there was no
budget enforcement or contribution path law.

This led to:

- Fragile consumer code that broke on internal refactors
- Untracked duplication across the fleet
- Gates that could be bypassed via allowlists
- No time/memory budgets on gate execution
- Unclear contribution workflow causing WIP residue

## Decision

The [consumption standard](../../standards/consumption-law.md) owns the R1-R6
contract. This ADR ratifies it rather than copying another normative body.
[ADR-018](018-generator-declarations.md) supersedes older alias/folder tables;
[ADR-019](019-service-contract-ports-operations.md) owns the service and model
amendment. The 2026-10-20 consolidation removes competing restatements and false
current-implementation claims. Native evidence, not historical gate numbers,
establishes implementation completeness.

### Runtime alias inspection amendment

Runtime alias inspection refinement (`flext-edcqq`).
**State at 0.12.0-dev (2026-09-27):** the flext-core side exists
(`DeferredInspection`/`DeferredAlias` on the integration tip); the flext-infra
runtime-census consumer cutover is still pending:

- PEP 695 aliases retain Python's lazy evaluation. Before forcing `__value__`, the core
  inspector matches the runtime alias identity to one module-bound source declaration
  and its lexical imports. Only unavailable names proven to be imported under
  `typing.TYPE_CHECKING` justify deferral; matching a name or catching `NameError` is
  insufficient proof.
- The existing public `u.resolve_type_alias_value` contract remains value-or-None:
  `None` represents a non-alias or this proven deferral. Local/dynamic aliases without
  declaration evidence do not inherit a deferral exemption. Ambiguous declarations fail
  explicitly; unexpected evaluation errors retain their original exception and
  traceback.
- The typed resolution owner distinguishes resolved values from `DeferredAlias`
  provenance. Rules that require an unavailable value record a `DeferredInspection` in
  `Report.deferred`, including the rule, location, declaration and unavailable imports.
  `Report.complete` is false when any requested inspection was deferred. Existing
  violation iteration describes violations only, so zero violations alone cannot
  establish a complete check.
- Deferral preserves a legal reverse import; it does not import the later layer at
  runtime or manufacture a runtime violation. Static type gates own those annotations.
  Runtime-census aggregation must retain deferral provenance and must not publish an
  incomplete report as passed or clean.

## Consequences

### Positive

- Consumers couple only to published contracts (stable)
- Duplication eliminated at owner (single source of truth)
- Gate contracts and applicable limits come from their typed owners
- Contribution path is explicit (no WIP residue)
- All enforcement derives from typed config SSOT

### Negative

- Migration required for existing consumers using internal imports
- Duplication gate may surface existing debt (must fix at owner)
- Measured slow gates require correction at their implementation owner
- Forward-line ADR numbering remains branch-specific; this branch's index is
  authoritative for the `0.12.0-dev` decision set.

## Implementation

The selected canonical tracker owns current work, dependencies and closure.
The historical WS-F assignment table is retained in Git history. Its proposed
gate names, registrations and check marks are not a current implementation
census or permission to restore a retired product.

## References

- [Consumption standard](../../standards/consumption-law.md)
- [Generator declarations](018-generator-declarations.md)
- [Service contracts](019-service-contract-ports-operations.md)
- The current flext-infra typed gate declarations and native public interface
