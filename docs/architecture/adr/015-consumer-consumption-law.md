# ADR-015: Consumer Consumption Law (R1-R6)

<!-- TOC START -->

- [Status](#status)
- [Context](#context)
- [Decision](#decision)
  - [R1 — Facade-Only Import Grammar](#r1-facade-only-import-grammar)
  - [R1a — Lazy-Init Re-Export Derivation](#r1a-lazy-init-re-export-derivation)
  - [R2 — No Duplication (Structural Scan)](#r2-no-duplication-structural-scan)
  - [R3 — Layer Law (Declaration vs Behavior)](#r3-layer-law-declaration-vs-behavior)
  - [R4 — Gates as Products](#r4-gates-as-products)
  - [R5 — Release Consumption](#r5-release-consumption)
  - [R6 — Contribution Path Law](#r6-contribution-path-law)
- [Anti-Hardcode Law (Binding)](#anti-hardcode-law-binding)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Implementation](#implementation)
- [References](#references)
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

## Status

CURRENT IMPLEMENTATION (accepted 2026-09-11)

Declaration derivation is amended by ADR-018; family and lazy-export boundaries by
ADR-028; execution admission and landing by ADR-029. Those topic decisions supersede
the older tables and workflow prescriptions recorded here. Historical implementation
rows below are dated context, not current runtime acceptance.

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

We ratify the **Consumer Consumption Law (R1-R6)** as the canonical standard for all
FLEXT packages. This law is codified in `docs/standards/consumption-law.md` and enforced
through the following mechanisms:

### R1 — Facade-Only Import Grammar

- Legal: `from <pkg> import X` where `X ∈ pkg.__all__`
- Illegal: any `pkg.<submodule>` path (facet modules, reach-throughs, internal
  machinery)
- Enforcement: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099
- Derivation: `FlextUtilitiesFamilySurface` from published lazy contract (`__all__` +
  `_LAZY_IMPORTS`)

### R1a — Lazy-Init Re-Export Derivation

[ADR-018](018-generator-declarations.md) supersedes filename-to-letter tables and
closed alias lists. Explicit module `__all__` declarations and authenticated source
MRO determine owned and inherited letters. An initializer propagates its immediate
modules' declarations; it never declares aliases or lifts descendants into ancestors.
[ADR-028 Decision 10](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10)
owns the nearest-package and hierarchical composition boundary.

Determinism (flext-b3xmn): source declarations determine the rendered surface, never
an ambient installed export union. The consumer explanation in
`docs/standards/consumption-law.md` R1a links to these decision owners.

### R2 — No Duplication (Structural Scan)

- Extended duplication gate covers consumer+family scope
- Thresholds via `[tool.flext.project]` config SSOT
- Semantic classifier: only executable behavior counts
- Enforcement: `FlextInfraGatesDuplication` extended → ENFORCE-100+

### R3 — Layer Law (Declaration vs Behavior)

[ADR-028 Decisions 3–4](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-3)
own placement: constants in `c`, type aliases in `t`, protocols in `p`, Pydantic
models in `m`, and reusable behavior in `u`. Protocol declarations and Pydantic
validators retain their native responsibilities. Operational facades are not
methodless data. Bases, services, API and CLI compose the capabilities they consume.
Reverse imports remain `TYPE_CHECKING`-only; module shape follows Decision 6 and
module-size budgets come from typed configuration, never a frozen number in this ADR.

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

### R4 — Gates as Products

- Every gate has typed config via `[tool.flext.project]`
- Budget gate (time/memory/token limits) is non-optional
- Atomic `O_APPEND` primitive in `flext-core.u`
- Fixed-point exposure via conform check

### R5 — Release Consumption

- 0.12.x tags on green tips
- `AI_HUB_CONSUMER.md` versioned per release
- Depends on F1, F4, F7
- Canonical R1–R6 text: [consumption-law](../../standards/consumption-law.md) — its R5 carries the
  expanded ceremony (per-repository GitHub Releases with wheel+sdist, per-repo SEMVER derived by
  `make release-plan`, gc-mail gate windows, consumer SSOT tag-refs projected by `make gen` and
  locked only by `make upg`); this summary stays thin on purpose.

### R6 — Contribution Path Law

Follow root `AGENTS.md` for current workspace/orchestration ownership and
[ADR-029](029-always-working-one-complete-cycle.md) for admission, the complete
cycle and integrated proof. Global Git governance owns preservation and reviewed
non-rewriting landing. Close Beads only with registered state, integration history,
measured reality and integrated code.

Zero residue follows
[ADR-028 Decision 7](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7):
deprecated signatures disappear after their complete consumer census reaches zero,
without breaking active consumers.

## Anti-Hardcode Law (Binding)

- **No bypass lists**: `BOUNDARY_SKIP_PROJECTS`, `CLICK_FILES`, `TOML_ALLOWED`,
  `BOUNDARY_FLEXT_CLI_CONCRETE_RE`, `startswith("flext_")` — all exterminated
- **No frozen enumerations**: facts derivable from SSOT/code are never fixed
- **No absolute paths**: config keys only
- **Tests**: never freeze mutable configuration. Rule fixtures follow
  [ADR-028 Decision 6](028-facade-boundary-orchestrators-declarative-enforcement.md#decision-6);
  tests confirm real runtime behavior and do not define it.

## Consequences

### Positive

- Consumers couple only to published contracts (stable)
- Duplication eliminated at owner (single source of truth)
- Gates are products with budgets (predictable CI)
- Contribution path is explicit (no WIP residue)
- All enforcement derives from typed config SSOT

### Negative

- Migration required for existing consumers using internal imports
- Duplication gate may surface existing debt (must fix at owner)
- Budget gate may require optimization of slow gates
- Forward-line ADR numbering remains branch-specific; this branch's index is
  authoritative for the `0.12.0-dev` decision set.

## Implementation

| Workstream | Deliverable                                                   | Bead            |
| ---------- | ------------------------------------------------------------- | --------------- |
| WS-F1      | R1 grammar + SSOT derivation cutover                          | flext-ssnc7.1 ✓ |
| WS-F1.v    | Synthetic RED/GREEN validation                                | flext-ssnc7.1.1 |
| WS-F2      | Consumer+family structural scan                               | flext-ssnc7.2   |
| WS-F2.v    | Planted structural twin RED proof                             | flext-ssnc7.2.1 |
| WS-F3      | consumption-law.md + ADR-015 + ADR index repair               | flext-ssnc7.3   |
| WS-F4      | `[tool.flext.project]` + budget gate + atomic append          | flext-ssnc7.4   |
| WS-F5      | 0.12.x tags + AI_HUB_CONSUMER versioned                       | flext-ssnc7.5   |
| WS-F6      | Contribution path law                                         | flext-ssnc7.6   |
| WS-F7      | ADR bijection + owner-resolution gates + three-file gate docs | flext-ssnc7.7   |

## References

- `docs/standards/consumption-law.md` (canonical R1-R6 text)
- `flext_core._utilities.family_surface` (R1 derivation SSOT)
- `flext_infra.detectors.consumer_import_violations_detector` (R1 enforcement)
- `flext_infra.gates.duplication` (R2 enforcement)
- `flext-infra/config/codegen.yaml` (R4/R5 config SSOT)
- `docs/GOVERNANCE.md` (R6 router)

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Update public consumption and exports; do not
  confuse Protocol signatures with behavior.
- This note records planning reconciliation only. It does not change the ADR's recorded
  maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
