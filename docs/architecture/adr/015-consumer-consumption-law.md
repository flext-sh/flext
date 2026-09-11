# ADR-015: Consumer Consumption Law (R1-R6)

## Status

Accepted (2026-09-11)

## Context

The FLEXT fleet (31+ `flext-*` packages) lacked a unified consumption standard. Consumers imported internal machinery (`flext_cli.models`, `flext_infra.workspace.detector`, `flext_core.lazy`), duplication went undetected across consumer+family scope, gates had hardcoded thresholds and bypass lists, and there was no budget enforcement or contribution path law.

This led to:
- Fragile consumer code that broke on internal refactors
- Untracked duplication across the fleet
- Gates that could be bypassed via allowlists
- No time/memory budgets on gate execution
- Unclear contribution workflow causing WIP residue

## Decision

We ratify the **Consumer Consumption Law (R1-R6)** as the canonical standard for all FLEXT packages. This law is codified in `docs/standards/consumption-law.md` and enforced through the following mechanisms:

### R1 — Facade-Only Import Grammar
- Legal: `from <pkg> import X` where `X ∈ pkg.__all__`
- Illegal: any `pkg.<submodule>` path (facet modules, reach-throughs, internal machinery)
- Enforcement: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099
- Derivation: `FlextUtilitiesFamilySurface` from published lazy contract (`__all__` + `_LAZY_IMPORTS`)

### R2 — No Duplication (Structural Scan)
- Extended duplication gate covers consumer+family scope
- Thresholds via `[tool.flext.project]` config SSOT
- Semantic classifier: only executable behavior counts
- Enforcement: `FlextInfraDuplicationGate` extended → ENFORCE-100+

### R3 — Layer Law (Declaration vs Behavior)
- Declaration layers (`c,t,p,m,u,r,e,x,h,d,s`) = pure data, zero methods
- Behavior only in `u`, `base.py`, `services/*.py`, `api.py`, `cli.py`
- Reverse imports `TYPE_CHECKING`-only; `c` never imports `m` at runtime
- One class per module, ≤200 LOC, Pydantic-2-way only

### R4 — Gates as Products
- Every gate has typed config via `[tool.flext.project]`
- Budget gate (time/memory/token limits) is non-optional
- Atomic `O_APPEND` primitive in `flext-core.u`
- Fixed-point exposure via conform check

### R5 — Release Consumption
- 0.12.x tags on green tips
- `AI_HUB_CONSUMER.md` versioned per release
- Depends on F1, F4, F7

### R6 — Contribution Path Law
- Bead → formula lane → canonical Make verbs → WIP commits → PR → `--no-ff` merge → gates on merged SHA → roll-up gitlinks → bead closure with 4 evidences
- Zero residue: dead code/compat shims are defects

## Anti-Hardcode Law (Binding)

- **No bypass lists**: `BOUNDARY_SKIP_PROJECTS`, `CLICK_FILES`, `TOML_ALLOWED`, `BOUNDARY_FLEXT_CLI_CONCRETE_RE`, `startswith("flext_")` — all exterminated
- **No frozen enumerations**: facts derivable from SSOT/code are never fixed
- **No absolute paths**: config keys only
- **Tests**: synthetic runtime-derived violations only; no committed fixtures

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
- ADR index repair needed (014 unindexed, 011/012 stranded on 0.20.0-dev)

## Implementation

| Workstream | Deliverable | Bead |
|------------|-------------|------|
| WS-F1 | R1 grammar + SSOT derivation cutover | flext-ssnc7.1 ✓ |
| WS-F1.v | Synthetic RED/GREEN validation | flext-ssnc7.1.1 |
| WS-F2 | Consumer+family structural scan | flext-ssnc7.2 |
| WS-F2.v | Planted structural twin RED proof | flext-ssnc7.2.1 |
| WS-F3 | consumption-law.md + ADR-015 + ADR index repair | flext-ssnc7.3 |
| WS-F4 | `[tool.flext.project]` + budget gate + atomic append | flext-ssnc7.4 |
| WS-F5 | 0.12.x tags + AI_HUB_CONSUMER versioned | flext-ssnc7.5 |
| WS-F6 | Contribution path law | flext-ssnc7.6 |
| WS-F7 | ADR bijection + owner-resolution gates + three-file gate docs | flext-ssnc7.7 |

## References

- `docs/standards/consumption-law.md` (canonical R1-R6 text)
- `flext_core._utilities.family_surface` (R1 derivation SSOT)
- `flext_infra.detectors.consumer_import_violations_detector` (R1 enforcement)
- `flext_infra.gates.duplication` (R2 enforcement)
- `config/codegen.yaml` (R4/R5 config SSOT)
- `docs/GOVERNANCE.md` (R6 router)