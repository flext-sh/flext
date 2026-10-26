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

> **Authority**: [ADR-015](../../docs/architecture/adr/015-consumer-consumption-law.md) owns the R1-R6 consumer contract. For an architectural concern,
> the accepted topic ADR is the precise technical source; this standard links to it and
> does not create a competing architecture rule. Typed configuration owns tool settings.
>
> **Status**: See the [ADR index](../../docs/architecture/adr/README.md) for decision maturity.
> This page is not a rollout receipt; current enforcement and gate evidence belong to
> the typed owners and active Beads.
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

**Intra-family exemption**: Facade assembly _within the same package_ imports from the
family package's generated lazy exports (e.g., `flext_cli` importing from
`flext_cli._models`), never from a module path below it or a module object reached by
attribute ([ADR-028 Decision 10](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10)).

**Fix hints**: Derived by inverting the published `_LAZY_IMPORTS` map — every `Flext*`
long name maps to its canonical single-letter alias (`c,t,p,m,u,r,e,x,h,d,s`).

**Enforcement**: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099
(flext-infra, source: `flext_infra_detector`, violation_field:
`consumer_import_violations`).

### R1a — Lazy-Init Re-Export Derivation (how `pkg.__all__` is built)

The published lazy contract (`__all__` + `_LAZY_IMPORTS`) is generated, never
hand-written. The root `__init__.py` derives it in this fixed order:

1. **Local facade letters win.** Files present in the package directory map to
   single-letter aliases: `constants.py→c`, `typings.py→t`, `protocols.py→p`,
   `models.py→m`, `utilities.py→u`, `config.py→config`, `settings.py→settings`
   (`NAMESPACE_LAYER_BY_FILE`).
2. **Operational letters are inherited from the highest upstream flext library.** `r`,
   `d`, `e`, `h`, `s`, `x` are re-exported from the immediate upstream (`flext_cli`,
   which sources them from `flext_core`) via
   `u.Infra.lazy_init_resolve_aliases`
   (nearest declaring, then nearest serving parent). The full canonical set is
   `ALIAS_NAMES = {c, t, m, p, u, r, d, e, h, s, x, tc}`.
3. **A local redeclaration published in `__all__` overrides the ancestor.** If the
   namespace redeclares any letter (e.g. `c`, `d`, `e`) and publishes it in its own
   `__all__`, the local declaration is used instead of the inherited upstream one.
4. **Module exports come from the current directory only.** `Flext*` long-name classes
   are re-exported from the current directory's modules' `__all__` — never from
   subdirectories, parent directories, or sibling packages.

**Determinism (flext-b3xmn)**: the facade-letter set derives from the statically indexed
workspace source (`u.Infra` `_lazy_init_package_names`), never from the ambient
installed/editable venv surface. A local venv (branch tips) and a pinned CI checkout
(gitlink SHAs) must render the identical root facade set; the prior ambient union of
`installed_package_exports` caused environment-dependent drift.

**Canonical source**: `flext_infra._utilities.lazy_init_letters` (owner
`u.Infra.lazy_init_resolve_aliases`) + `flext_infra._constants.validate.ALIAS_NAMES` +
`flext_infra._constants.namespace.NAMESPACE_LAYER_BY_FILE`.

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

**Canonical source**: this law (R1a/R1b); ADR-015; the accepted topic ADR; skill
`flext-law` ("Architecture and imports").

---

## R2 — No Duplication (Structural Scan)

**Rule**: Every change leaves zero jscpd duplication findings and zero qlty smells under
the strict FLEXT policy. The rule applies to the affected repository's governed source;
it is not limited to consumer+family pairs.

**Canonical decision**: [ADR-028 Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16)
owns the zero-finding requirement and prohibits hiding clones or smells with ignored
paths, raised thresholds, or narrowed scope. The sole authorized jscpd exception is the
mandated license header, declared by its typed owner.

**Configuration and execution**: typed flext-infra tooling configuration owns jscpd
settings and qlty repair guidance; qlty owns its smell thresholds. Do not copy mutable
settings or gate IDs into this standard. The jscpd semantic pass requires its declared
embeddings host; if it is unavailable, that pass is `NOT EXECUTED`, not a successful
zero-finding result. Use the affected project's declared command surface and report the
exact gate evidence in its active Bead.

---

## R3 — Layer Law (Declaration vs Behavior)

**Rule**: Declaration layers (`c,t,p,m,u` + `r,e,x,h,d,s`) carry **zero methods** — only
Pydantic `Field`/`validators`/`computed_field`. Behavior lives **only** in:

- `u` (utilities)
- `base.py` (services)
- `services/*.py`
- `api.py` (composition root)
- `cli.py` (thin CLI)

**Reverse imports**: `TYPE_CHECKING`-only. `c` never imports `m` at runtime.

**One public `api.py` per package** as composition root; thin `cli.py`.

**Internals**: under `_[module]/*.py` starting with `base.py`.

**One class per module**; module size cap is config-owned (`loc_cap.max_lines`),
enforced by the `loc-cap` gate.

**No local redeclarations**, aliases, or competing long-name layers.

**Boundaries and completeness**: external libraries and orchestrators follow [ADR-028
Decisions 1–4](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-1),
capability names follow [Decision 15](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15),
CA/DI and quality follow [Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16),
native workspace refactoring follows [Decision 17](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17),
generalized rules follow [Decision 18](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18),
and Pydantic completeness follows [Decision 14](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-14). This law restates none of them.

**Pydantic-2-way only** for owned payloads (`model_validate` in, `model_dump` out). No
`dict`/`TypedDict`/`dataclass`/`NamedTuple`/`m.Dict` as data contract.

**Typing**: never `Any`/`object`/concrete-class annotations; type via `t.*` aliases and
`p.*` protocols; `T | None` (never `Optional`). A model is never a type.

**Enforcement**: namespace gate (NS-STRUCT, NS-CONTRACT) + canonical-alias gate
(ENFORCE-080) + typing gates.

---

## R4 — Gates as Products (Budget + Primitives)

**Rule**: Every gate is a **product** with:

1. Typed config via `[tool.flext.project]` (SSOT, never hardcoded)
2. Budget gate (time/memory/token limits) — non-optional
3. Atomic `O_APPEND` append primitive in `flext-core.u` (generic domain)
4. Fixed-point exposure via conform check (regenerated config matches running config)

**Budget gate**: New gate class + `_gate_classes` registry + `SARIF_TOOL_INFO` row +
`codegen.yaml` entry. Registry divergence = hard error.

**Primitives**: `u.append_atomic(path, data)` — generic, reusable across fleet.

**Enforcement**: budget gate delivered (`FlextInfraBudgetGate`, validates one declared
budget row per `c.Infra.ALLOWED_GATES` gate); catalog row pending its next free ID (101)
— WS-F4 validation. Runtime budget telemetry (measured time/memory in reports) remains
open.

---

## R5 — Release Consumption (Versioning + AI_HUB_CONSUMER)

**Rule**: Every FLEXT member releases on the **0.12.x line** with:

- Tags on green tips after gates pass
- `AI_HUB_CONSUMER.md` versioned with each release (consumer-facing changelog)
- Dependencies: F1 (grammar), F4 (budget), F7 (doc hardening)

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

| Concern        | SSOT Location                                                         |
| -------------- | --------------------------------------------------------------------- |
| R1 Grammar     | `flext_core._utilities.family_surface.FlextUtilitiesFamilySurface`    |
| R1a Lazy-Init  | `flext_infra._utilities.lazy_init_letters` (`lazy_init_resolve_aliases`) |
| R1 Enforcement | `flext_infra.detectors.consumer_import_violations_detector`           |
| R2 Duplication | [ADR-028 Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16); typed Infra tooling declaration and the declared duplication/smells gates |
| R3 Layer Law   | `flext_infra.gates.namespace.FlextInfraNamespaceGate`                 |
| R4 Config      | `config/codegen.yaml` → `codegen.yaml` scaffold.project.dev           |
| R4 Budget Gate | `flext_infra.gates.budget` (new)                                      |
| R4 Primitives  | `flext_core._utilities.files` (new)                                   |
| R5 Versioning  | `config/codegen.yaml` scaffold.project.dev                            |
| R6 Workflow    | `docs/GOVERNANCE.md`, Gas City contracts                              |

---

## Anti-Hardcode Law (Enforcement)

**Prohibited**:

- Bypass/leniency lists (e.g., `BOUNDARY_SKIP_PROJECTS`, `CLICK_FILES`, `TOML_ALLOWED`)
- Fixed enumerated lists for facts derivable from SSOT/code
- Absolute paths or out-of-repo references
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
| [ADR-028 Decision 15](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15) | Capability-named boundaries | Accepted |
| [ADR-028 Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16) | CA/DI and zero quality findings | Accepted |
| [ADR-028 Decision 17](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17) | Native workspace model and refactorings | Accepted |
| [ADR-028 Decision 18](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18) | Generalized rules | Accepted |

---

## Change Log

| Version | Date       | Change                                                                                                                                                                     |
| ------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.12.0  | 2026-09-11 | Initial ratification (ADR-015)                                                                                                                                             |
| 0.12.1  | 2026-09-18 | Add R1a lazy-init re-export derivation rule (ALIAS_NAMES, inherited operational letters, local-`__all__` override, directory-only module exports, flext-b3xmn determinism) |
| 0.12.2  | 2026-09-19 | Add R1b MRO OO facade composition rule (namespace-matched access; upstream composes, own namespaces only) — verified in flext-api 3c004ef0 / flext-web 4bc984c             |
