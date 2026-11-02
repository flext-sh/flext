# FLEXT Consumer Consumption Law

<!-- TOC START -->

- [R1 — Facade-Only Import Grammar (Consumer Legality)](#r1-facade-only-import-grammar-consumer-legality)
  - [R1a — Lazy-Init Re-Export Derivation (how pkg.\_\_all\_\_ is built)](#r1a-lazy-init-re-export-derivation-how-pkg__all__-is-built)
- [R1b — MRO OO Facade Composition (Namespace-Matched Access)](#r1b-mro-oo-facade-composition-namespace-matched-access)
- [R2 — No Duplication (Structural Scan)](#r2-no-duplication-structural-scan)
- [R3 — Layer Law (Declaration vs Behavior)](#r3-layer-law-declaration-vs-behavior)
- [R4 — Gates as Products (Budget + Primitives)](#r4-gates-as-products-budget-primitives)
- [R5 — Release Consumption (Versioning + AI\_HUB\_CONSUMER)](#r5-release-consumption-versioning-ai_hub_consumer)
- [R6 — Contribution Path Law](#r6-contribution-path-law)
- [Canonical Sources](#canonical-sources)
- [Anti-Hardcode Law (Enforcement)](#anti-hardcode-law-enforcement)
- [ADR Cross-Reference](#adr-cross-reference)
- [Change Log](#change-log)

<!-- TOC END -->

> **Authority**: This document is the canonical R1-R6 consumption standard for the FLEXT
> fleet. All enforcement derives from this law; no parallel rules or bypass lists exist.
>
> **Status**: Accepted target. Conformance requires current native evidence;
> historical gate IDs and implementation counts are not acceptance receipts.
> Generator declarations follow ADR-018 and service composition follows ADR-019.
>
> **Version**: 0.12.x line; forward baseline 0.13.0.

---

## R1 — Facade-Only Import Grammar (Consumer Legality)

**Rule**: A consumer import is **legal** iff it matches:

```{.python .notest}
from <flext-package> import <symbol>
```

where `<symbol>` ∈ `pkg.__all__` (the published lazy export contract).

**Violations** (any other form):

- `import flext_cli.models` (facet module)
- `from flext_cli import models` (submodule import)
- `from flext_infra.workspace import detector` (nested reach-through)
- `import flext_core.lazy` (internal machinery)
- `from flext_core import lazy` (internal machinery)
- Any `pkg.<submodule>` path — zero exceptions

**Intra-family exemption**: Facade assembly _within the same package_ remains legal
(e.g., `flext_cli` importing `flext_cli._models`).

**Fix hints**: Derived by inverting the published `_LAZY_IMPORTS` map — every `Flext*`
long name maps to its canonical single-letter alias (`c,t,p,m,u,r,e,x,h,d,s`).

**Enforcement**: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099
(flext-infra, source: `flext_infra_detector`, violation_field:
`consumer_import_violations`).

### R1a — Lazy-Init Re-Export Derivation (how `pkg.__all__` is built)

The published lazy contract is generated from original source declarations and
MRO, never authored at its consumer. [ADR-018](../architecture/adr/018-generator-declarations.md)
owns the detailed derivation and supersedes the historical filename-to-letter,
closed folder and ALIAS_NAMES tables. A remaining implementation table is a
migration finding, not a second rule. Local explicit exports override inherited
ones according to that declaration contract. Ambient installed exports never
replace the authenticated source input to generation.

---

## R1b — MRO OO Facade Composition (Namespace-Matched Access)

**Rule**: A package facade composes the **upstream facade** (inheriting its namespaces
through the MRO) and adds **only its own namespaces**. Consumers access each namespace
by its owning package: `m.Api.*` for api-owned models, `m.Web.*` for web-owned models
resolved through the inheritance chain.

**Forbidden**: composing a sibling/upstream namespace as a base of your own namespace
(it leaks foreign members across domains — e.g. `class Api(..., m.Web)` puts web models
under `m.Api.*`), and referencing an upstream namespace by a renamed alias (the
`Web`→`Api` rename of a facade orphaned every `m.Web.*` consumer while nothing
referenced the new name).

**Runtime proof** (flext-api `3c004ef0`, flext-web `dced660`/`4bc984c`):
`flext_api.m.Api` carries no web members; `flext_api.m.Web` resolves the web namespace
through the chain; `flext_web.m.Web.FastAPIAppConfig` resolves.

**Canonical source**: this section owns namespace-matched composition; ADR-015
ratifies it and local flext-law routes here.

---

## R2 — No Duplication (Structural Scan)

**Rule**: Every clone detected by the duplication gate (jscpd + semantic classifier)
that spans **consumer+family scope** must be eliminated at its owner — no per-site
allowlists.

**Scope and thresholds**: derive them from the selected gate's typed configuration
owner. Do not duplicate current scalar defaults or invent a configuration table in
this standard. Tests, scripts and examples retain their declared gate coverage.

**Semantic classifier**: Only executable behavior counts (module licenses, docstrings,
imports, TYPE_CHECKING blocks, class shells, function signatures, declaration-only
assignments are excluded).

**Enforcement**: the current duplication gate and its typed declaration; completion
requires a native receipt for the complete declared scope.

---

## R3 — Layer Law (Declaration vs Behavior)

**Rule**: c/t/p/m own constants, type aliases, protocol signatures and models.
Protocol method signatures and supported Pydantic validation metadata are
declarations. They do not authorize use-case behavior in those layers.
Utilities and operational r/e/x/h/d/s families own their declared behavior.
Domain behavior belongs in:

- `u` (utilities)
- `base.py` (services)
- `services/*.py`
- `api.py` (composition root)
- `cli.py` (thin CLI)

**Reverse imports**: `TYPE_CHECKING`-only. `c` never imports `m` at runtime.

**Real facades only**: ADR-019 decision 6 derives the API, service foundation and
transport requirements from the project role. No-op files are not conformance.

**Internals**: under `_[module]/*.py` starting with `base.py`.

**One class per module**; module size cap is config-owned (`loc_cap.max_lines`),
enforced by the `loc-cap` gate.

**No local redeclarations**, aliases, or competing long-name layers.

**Pydantic-2-way only** for owned payloads (`model_validate` in, `model_dump` out). No
`dict`/`TypedDict`/`dataclass`/`NamedTuple`/`m.Dict` as data contract.

**Typing**: never `Any`/`object`/concrete-class annotations; type via `t.*` aliases and
`p.*` protocols; `T | None` (never `Optional`). A model is never a type.

**Enforcement**: namespace gate (NS-STRUCT, NS-CONTRACT) + canonical-alias gate
(ENFORCE-080) + typing gates.

---

## R4 — Gates as Products (Budget + Primitives)

**Rule**: the selected typed gate declaration owns its configuration, execution,
diagnostics and reporting. Reuse the existing atomic primitive where the operation
requires it. Do not copy a registry, parser, append helper or reporting engine
into the consumer.

The historical standalone budget-gate namespace and its proposed registration
rows are retired implementation guidance. This standard does not reinstate them
or invent a generic append API. Applicable invocation deadlines remain owned by
universal command governance; product-specific limits come from their current
typed owner. Prove the actual gate and generated configuration through native
verbs and fixed-point evidence.

---

## R5 — Release Consumption (Versioning + AI_HUB_CONSUMER)

**Rule**: Every FLEXT member releases on the **0.12.x line** with:

- Tags on green tips after gates pass
- `AI_HUB_CONSUMER.md` versioned with each release (consumer-facing changelog)
- Acceptance comes from the current release owner; historical WS-F labels do
  not create another gate or restore a retired budget namespace.

**AI_HUB_CONSUMER.md**: Machine-readable consumer contract — what changed, what's legal,
migration path.

**Enforcement**: Release pipeline + consumer docs gate.

---

## R6 — Contribution Path Law

**Rule**: Every contribution follows a **declared path**:

1. Work filed as bead (tracker-owned)
2. Lane created by formula (Gas City owns workspace/branch lifecycle)
3. Implementation on lane, gates via canonical Make verbs
4. WIP commits (scoped paths, `[WIP]` subject, local only)
5. PR → review → `--no-ff` merge into integration branch (`0.12.0-dev`)
6. Gates rerun on merged SHA → runtime proved on integrated state
7. Roll-up gitlinks in superproject after commits on remote
8. Beads closed with 4 evidences (registered state, git history, measured reality,
   integrated code)

**Zero residue**: Dead code, compat shims, un-rewired consumers/tests are defects —
never carry-over.

**Enforcement**: Workflow gates + bead verification + CI.

---

## Canonical Sources

This standard owns R1-R6 consumption; ADR-018 owns generator declarations and
ADR-019 owns service contracts. The selected flext-infra typed gate catalog and
implementation own enforcement. Resolve their current identities there rather
than maintaining another symbol/path registry here. A historical implementation
name does not prove that a current gate exists or passed.

---

## Anti-Hardcode Law (Enforcement)

**Prohibited**:

- Bypass/leniency lists (e.g., `BOUNDARY_SKIP_PROJECTS`, `CLICK_FILES`, `TOML_ALLOWED`)
- Fixed enumerated lists for facts derivable from SSOT/code
- Hardcoded host paths or private cross-repository identities in portable policy
- Tests with frozen fixture lists — synthetic runtime-derived violations only

**Required**:

- Gates derive in runtime (`__all__`, `_LAZY_IMPORTS`, `importlib.metadata`
  namespace-shape, `c.Infra` constants)
- Config keys only (reference config keys, not hardcoded default paths)
- Owner-first reuse and simplification over local reimplementation

---

## ADR Cross-Reference

| ADR         | Topic                                | Status       |
| ----------- | ------------------------------------ | ------------ |
| ADR-001     | Railway Result (`r`)                 | Accepted     |
| ADR-005     | Config SSOT                          | Accepted     |
| ADR-006     | Thin Drivers (Meltano)               | Accepted     |
| ADR-008     | Agent-runtime symmetry               | Accepted     |
| ADR-010     | Codegen Standardization              | Accepted     |
| ADR-014     | Codemod Governance                   | Accepted     |
| **ADR-015** | **Consumer Consumption Law (R1-R6)** | **Accepted** |

---

## Change Log

| Version | Date       | Change                                                                                                                                                                     |
| ------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.12.0  | 2026-09-11 | Initial ratification (ADR-015)                                                                                                                                             |
| 0.12.1  | 2026-09-18 | Add R1a lazy-init re-export derivation rule (ALIAS_NAMES, inherited operational letters, local-`__all__` override, directory-only module exports, flext-b3xmn determinism) |
| 0.12.2  | 2026-09-19 | Add R1b MRO OO facade composition rule (namespace-matched access; upstream composes, own namespaces only) — verified in flext-api 3c004ef0 / flext-web 4bc984c             |
