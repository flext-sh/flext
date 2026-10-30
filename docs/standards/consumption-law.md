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

**Fix hints**: Resolve the declaration's native identity and its nearest published lazy
surface under [ADR-028 Decision 10](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10).
A class name alone does not establish a facade letter. Preserve hierarchical family
composition; rewrites must retain the resolved object's identity.

**Enforcement**: `FlextInfraConsumerImportViolationsDetector` → ENFORCE-099
(flext-infra, source: `flext_infra_detector`, violation_field:
`consumer_import_violations`).

### R1a — Lazy-Init Re-Export Derivation (how `pkg.__all__` is built)

The published lazy contract (`__all__` + `_LAZY_IMPORTS`) is generated, never
hand-written. [ADR-018](../../docs/architecture/adr/018-generator-declarations.md)
owns its derivation from explicit declarations and source-authenticated MRO.
Filename-to-letter tables and closed alias lists are superseded, not additional
inputs to generation.

The declaring module publishes its own letter in `__all__`; an initializer re-exports
its immediate modules and never invents a declaration. Local explicit declarations
retain their ownership; inherited letters follow their verified upstream identity.
Nested domains compose through their nearest owning facade. A child's export list
never authorizes an ancestor to publish its leaf implementations
([ADR-028 Decision 10](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-10)).

**Determinism (flext-b3xmn)**: the facade-letter set derives from the statically indexed
workspace source (`u.Infra` `_lazy_init_package_names`), never from the ambient
installed/editable venv surface. A local venv (branch tips) and a pinned CI checkout
(gitlink SHAs) must render the identical root facade set; the prior ambient union of
`installed_package_exports` caused environment-dependent drift.

**Ownership**: ADR-018 owns the declaration contract; the existing Infra initializer
planner and renderer own its implementation. Current generation and consumer evidence
belongs to the active Bead, not to this explanatory standard.

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

**Rule**: [ADR-028 Decisions 3–4](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-3)
own declaration placement: `c` owns constants, `t` type aliases, `p` protocols and
`m` Pydantic data models. Protocol signatures and Pydantic validation follow their
declared contracts; they do not authorize reusable application behavior in those
families. `u` owns reusable behavior. Bases, services, the API composition root and
the thin CLI compose those capabilities within their declared responsibilities.
Operational facades retain their own contracts; they are not classified as methodless
data merely because they have short public names.

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

**Enforcement**: budget gate delivered (`FlextInfraGatesBudget`, validates one declared
budget row per `c.Infra.ALLOWED_GATES` gate); catalog row pending its next free ID (101)
— WS-F4 validation. Runtime budget telemetry (measured time/memory in reports) remains
open.

---

## R5 — Release Consumption (Versioning + AI_HUB_CONSUMER)

**Rule**: Every FLEXT member releases on the **0.12.x line** via per-repository GitHub
Releases (wheel + sdist artifacts) at per-repository SEMVER (`0.12.x`) determined by
`make release-plan` with:

- Committed `.github/workflows/release.yml` and `.github/workflows/release-plan.yml`
  across all 32 repositories (`publishes_release: true` in `config/codegen.yaml`)
- Signed tags `@v0.12.x` cut on green tips after `candidate-ci` gates pass; published tags
  are never deleted or moved (historical local `rc*` tags are pushed to align before cut,
  and repos where `v0.12.0` already exists advance to `v0.12.1`)
- `gc-mail` ceremony protocol: `[coord] [@city-hall] gate-window START <repo> release-build`
  before merge/cut and `[coord] landed <repo> v0.12.x` naming downstream consumers
  (`ai-hub`, `algar-oud-mig`, `cosmos-*`, `invest`, `dataop`) before `gate-window END`
- Consumer SSOT projection: external consumers (`ai-hub`) declare `@v0.12.x` tag refs in
  `config/codegen.yaml` (`branch_policy.integration_branch`, `project.flext_source`, and
  per-distribution overrides in `toolchain.uv_override_dependencies` + `tools.yaml`
  `uv-tools`) and project `pyproject.toml` via `make gen` and `uv.lock` via `make upg`
  (never hand-editing `pyproject.toml`)
- `AI_HUB_CONSUMER.md` versioned with each release in English (consumer-facing contract
  and clean-consumer receipt proving fresh `.venv` install and public smoke imports
  without `FLEXT=`)
- Dependencies: F1 (grammar), F4 (budget), F7 (doc hardening)

**AI_HUB_CONSUMER.md**: Machine-readable and human-auditable English consumer contract
recording exact per-repository `@v0.12.x` release tags, what changed, what is legal,
migration path, and clean-consumer verification evidence.

**Enforcement**: Release pipeline (`release-plan` / `release.yml`), `deps` gate tag-ref
alignment, and consumer docs gate.

---

## R6 — Contribution Path Law

**Rule**: Every contribution follows its declared execution and integration path.
Root `AGENTS.md` owns the current shared-worktree and suspended-orchestration
boundary. [ADR-029](../../docs/architecture/adr/029-always-working-one-complete-cycle.md)
owns global admission, the complete per-slice cycle and integrated runtime proof.
Canonical global Git governance owns preservation refs, reviewed publication and
non-rewriting merges. This standard does not create a separate formula, WIP or
landing procedure.

Beads closes work only with registered state, integration history, measured reality
and current integrated code. Superproject gitlinks advance only after their member
commits are available on the declared remote integration branches.

**Zero residue**: Follow the canonical `runtime/zero-residue` owner and
[ADR-028 Decision 7](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-7).
A renamed public signature with consumers retains only its marked delegation to the
new owner, without parallel behavior. Rewire the complete fleet and external census,
then delete the old signature when no use remains. Unmarked legacy and zero-use
survivors are defects.

**Enforcement**: Workflow gates + bead verification + CI.

---

## Canonical Sources

| Concern        | SSOT Location                                                         |
| -------------- | --------------------------------------------------------------------- |
| R1 Grammar     | `flext_core._utilities.family_surface.FlextUtilitiesFamilySurface`    |
| R1a Lazy-Init  | `flext_infra._utilities.lazy_init_letters` (`lazy_init_resolve_aliases`) |
| R1 Enforcement | `flext_infra.detectors.consumer_import_violations_detector`           |
| R2 Duplication | [ADR-028 Decision 16](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16); typed Infra tooling declaration and the declared duplication/smells gates |
| R3 Layer Law   | `flext_infra.gates.namespace.FlextInfraGatesNamespace`                 |
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
- Tests that freeze mutable configuration or duplicate its policy values

**Required**:

- Gates derive in runtime (`__all__`, `_LAZY_IMPORTS`, `importlib.metadata`
  namespace-shape, `c.Infra` constants)
- Config keys only (reference config keys, not hardcoded default paths)
- Owner-first reuse and simplification over local reimplementation
- Rule fixtures are artifacts under the canonical `testing/observable-runtime`
  contract and
  [ADR-028 Decision 6](../../docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-6);
  executable builders and wiring remain with test-code owners, and fixture existence
  is not proof of real runtime correctness

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
