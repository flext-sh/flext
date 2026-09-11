# FLEXT Consumer Consumption Law

> **Authority**: This document is the canonical R1-R6 consumption standard for the FLEXT fleet. All enforcement derives from this law; no parallel rules or bypass lists exist.
>
> **Status**: ADR-015 ratified. Enforcement delivered: ENFORCE-099 (consumer_import_violations). Catalog rows for R2 duplication and R4 budget are **pending their next free IDs** (100, 101 — not yet registered in the enforcement catalog; landing them is part of WS-F2/F4 validation waves).
>
> **Version**: 0.12.x line; forward baseline 0.13.0.

---

## R1 — Facade-Only Import Grammar (Consumer Legality)

**Rule**: A consumer import is **legal** iff it matches:

```python
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

**Intra-family exemption**: Facade assembly *within the same package* remains legal (e.g., `flext_cli` importing `flext_cli._models`).

**Fix hints**: Derived by inverting the published `_LAZY_IMPORTS` map — every `Flext*` long name maps to its canonical single-letter alias (`c,t,p,m,u,r,e,x,h,d,s`).

**Enforcement**: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099 (flext-infra, source: `flext_infra_detector`, violation_field: `consumer_import_violations`).

---

## R2 — No Duplication (Structural Scan)

**Rule**: Every clone detected by the duplication gate (jscpd + semantic classifier) that spans **consumer+family scope** must be eliminated at its owner — no per-site allowlists.

**Scope**: Configured via `[tool.flext.project]` keys:

```toml
[tool.flext.project]
duplication.scope = ["src", "tests", "scripts", "examples", "templates"]
duplication.min-lines = 10
duplication.min-tokens = 62
duplication.threshold-percent = 0.0
```

**Semantic classifier**: Only executable behavior counts (module licenses, docstrings, imports, TYPE_CHECKING blocks, class shells, function signatures, declaration-only assignments are excluded).

**Enforcement**: `FlextInfraDuplicationGate` extended with consumer+family scope (config reader delivered); catalog row pending its next free ID (100) — registration belongs to WS-F2 validation.

---

## R3 — Layer Law (Declaration vs Behavior)

**Rule**: Declaration layers (`c,t,p,m,u` + `r,e,x,h,d,s`) carry **zero methods** — only Pydantic `Field`/`validators`/`computed_field`. Behavior lives **only** in:

- `u` (utilities)
- `base.py` (services)
- `services/*.py`
- `api.py` (composition root)
- `cli.py` (thin CLI)

**Reverse imports**: `TYPE_CHECKING`-only. `c` never imports `m` at runtime.

**One public `api.py` per package** as composition root; thin `cli.py`.

**Internals**: under `_[module]/*.py` starting with `base.py`.

**One class per module**; ≤200 logical LOC/module.

**No local redeclarations**, aliases, or competing long-name layers.

**Pydantic-2-way only** for owned payloads (`model_validate` in, `model_dump` out). No `dict`/`TypedDict`/`dataclass`/`NamedTuple`/`m.Dict` as data contract.

**Typing**: never `Any`/`object`/concrete-class annotations; type via `t.*` aliases and `p.*` protocols; `T | None` (never `Optional`). A model is never a type.

**Enforcement**: namespace gate (NS-STRUCT, NS-CONTRACT) + canonical-alias gate (ENFORCE-080) + typing gates.

---

## R4 — Gates as Products (Budget + Primitives)

**Rule**: Every gate is a **product** with:

1. Typed config via `[tool.flext.project]` (SSOT, never hardcoded)
2. Budget gate (time/memory/token limits) — non-optional
3. Atomic `O_APPEND` append primitive in `flext-core.u` (generic domain)
4. Fixed-point exposure via conform check (regenerated config matches running config)

**Budget gate**: New gate class + `_gate_classes` registry + `SARIF_TOOL_INFO` row + `codegen.yaml` entry. Registry divergence = hard error.

**Primitives**: `u.FlextUtilities.append_atomic(path, data)` — generic, reusable across fleet.

**Enforcement**: budget gate delivered (`FlextInfraBudgetGate`, validates one declared budget row per `c.Infra.ALLOWED_GATES` gate); catalog row pending its next free ID (101) — WS-F4 validation. Runtime budget telemetry (measured time/memory in reports) remains open.

---

## R5 — Release Consumption (Versioning + AI_HUB_CONSUMER)

**Rule**: Every FLEXT member releases on the **0.12.x line** with:

- Tags on green tips after gates pass
- `AI_HUB_CONSUMER.md` versioned with each release (consumer-facing changelog)
- Dependencies: F1 (grammar), F4 (budget), F7 (doc hardening)

**AI_HUB_CONSUMER.md**: Machine-readable consumer contract — what changed, what's legal, migration path.

**Enforcement**: Release pipeline + consumer docs gate.

---

## R6 — Contribution Path Law

**Rule**: Every contribution follows a **declared path**:

1. Work filed as bead (tracker-owned)
2. Lane created by formula (Gas City owns workspace/branch lifecycle)
3. Implementation on lane, gates via canonical Make verbs (`APPLY=Y`)
4. WIP commits (scoped paths, `[WIP]` subject, local only)
5. PR → review → `--no-ff` merge into integration branch (`0.12.0-dev`)
6. Gates rerun on merged SHA → runtime proved on integrated state
7. Roll-up gitlinks in superproject after commits on remote
8. Beads closed with 4 evidences (registered state, git history, measured reality, integrated code)

**Zero residue**: Dead code, compat shims, un-rewired consumers/tests are defects — never carry-over.

**Enforcement**: Workflow gates + bead verification + CI.

---

## Canonical Sources

| Concern | SSOT Location |
|---------|---------------|
| R1 Grammar | `flext_core._utilities.family_surface.FlextUtilitiesFamilySurface` |
| R1 Enforcement | `flext_infra.detectors.consumer_import_violations_detector` |
| R2 Duplication | `flext_infra.gates.duplication.FlextInfraDuplicationGate` |
| R3 Layer Law | `flext_infra.gates.namespace.FlextInfraNamespaceGate` |
| R4 Config | `config/codegen.yaml` → `codegen.yaml` scaffold.project.dev |
| R4 Budget Gate | `flext_infra.gates.budget` (new) |
| R4 Primitives | `flext_core._utilities.files` (new) |
| R5 Versioning | `config/codegen.yaml` scaffold.project.dev |
| R6 Workflow | `docs/GOVERNANCE.md`, Gas City contracts |

---

## Anti-Hardcode Law (Enforcement)

**Prohibited**:

- Bypass/leniency lists (e.g., `BOUNDARY_SKIP_PROJECTS`, `CLICK_FILES`, `TOML_ALLOWED`)
- Fixed enumerated lists for facts derivable from SSOT/code
- Absolute paths or out-of-repo references
- Tests with frozen fixture lists — synthetic runtime-derived violations only

**Required**:

- Gates derive in runtime (`__all__`, `_LAZY_IMPORTS`, `importlib.metadata` namespace-shape, `c.Infra` constants)
- Config keys only (reference config keys, not hardcoded default paths)
- Owner-first reuse and simplification over local reimplementation

---

## ADR Cross-Reference

| ADR | Topic | Status |
|-----|-------|--------|
| ADR-001 | Railway Result (`r`) | Accepted |
| ADR-005 | Config SSOT | Accepted |
| ADR-006 | Thin Drivers (Meltano) | Accepted |
| ADR-008 | Agent-runtime symmetry | Accepted |
| ADR-010 | Codegen Standardization | Accepted |
| ADR-012 | Config/Settings Pattern | Accepted |
| ADR-014 | Codemod Governance | Accepted |
| **ADR-015** | **Consumer Consumption Law (R1-R6)** | **Accepted** |

---

## Change Log

| Version | Date | Change |
|---------|------|--------|
| 0.12.0 | 2026-09-11 | Initial ratification (ADR-015) |