# FLEXT Governance Router

<!-- TOC START -->

- [Purpose](#purpose)
- [Authority](#authority)
- [Owner Routing](#owner-routing)
- [Declaration invariants (apply to every slice)](#declaration-invariants-apply-to-every-slice)
  - [ADR-028 Decision Map](#adr-028-decision-map)
- [Engineering Conformance Review](#engineering-conformance-review)
- [Execution Contract](#execution-contract)
- [Universal test contract (P0)](#universal-test-contract-p0)
- [Baseline Commands](#baseline-commands)

<!-- TOC END -->

## Purpose

This file maps each change to its canonical owner. It does not restate engineering law
or skill procedures.

## Authority

Apply the newest applicable source in this order, with technical decisions and execution
state kept in their separate owners:

1. Newest operator request.
2. `~/.agents` universal authority (`AGENTS.md` and universal skills).
3. The topic-owning **accepted ADR** in the [architecture ADR index](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/README.md)
   is the precise source for its technical decision. For this boundary, follow the exact
   [ADR-028 Decision 15](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15),
   [Decision 16](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16),
   [Decision 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17), and
   [Decision 18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18).
   A proposed ADR is not an accepted contract.
4. [Root `AGENTS.md`](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md), exact
   local [session router](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/commands/flext-law.md),
   [context router](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-context-routing/SKILL.md),
   [FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md),
   then the nearest member scope. These route and enforce ADRs; a conflict is repaired
   at the lower instruction owner unless higher operator/global law requires stricter
   behavior.
5. Beads own the active work's scope, owner, dependencies, status, and evidence; they do
   not redefine accepted architecture.
6. Supporting documentation and generated projections consume the owners above. `TODO.md`
   is generated from Beads and is never edited by hand.

When a higher source changes reality, update the affected lower sources in the same
change. Ask before acting only when the conflict cannot be resolved from this order.

Universal authority is installed at `~/.agents/AGENTS.md`; it is not copied into
this portal. The context router names the exact global Make and verification skills.
Resolve global engineering skills at their installed canonical locations:
`project-wide/configuration/ssot`, `project-wide/refactoring/yagni`,
`project-wide/architecture/dry`, `project-wide/architecture/solid`,
`project-wide/refactoring/search-first`, `domain/dep-injection`,
`domain/clean-architecture`, and `technology/pydantic-development`, each under
`~/.agents/skills/` with `SKILL.md`. These filesystem references are deliberately
not site links. Missing authority fails closed; do not substitute another branch,
worktree, generated copy, or a similarly named skill.

This router applies to maintained first-party workspace and member documentation,
including executable examples. Member portals already route here through their
generated Governance Pointer; root guides are their writable shared source.
Vendor, archive, cache, historical evidence, and generated pages are not writable
rule owners. In standalone mode, resolve the parent law on the same branch/release
as the member, as required by its `AGENTS.md`.

## Owner Routing

| Concern                                               | Canonical owner                                                                                                                                          | Decisive validation                                                     |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Provider activation and exported paths                | `~/.agents` provider authority                                                                                                                           | typed manifest and exact-path inventory validation                      |
| Session routing                                       | `.agents/skills/flext-context-routing/SKILL.md`                                                                                                          | marker and selected-skill evidence                                      |
| Architecture and public contracts                     | [ADR registry](architecture/adr/README.md) and owning source declaration                                                                                 | consumer audit plus affected project gates                              |
| Ecosystem coordination (internal + external projects) | [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md) and [ecosystem-coordination.md](architecture/ecosystem-coordination.md) | reverse-dependency gate plus owner-local ADR consistency; future 0.13 work remains gated by `flext-ik359` |
| Runtime coding patterns                               | smallest matching skill under `~/.agents/skills/`                                                                                                        | fresh import, lint, typecheck, behavior gate                            |
| Quality commands                                      | `~/.agents/skills/project-wide/shell/make-check/SKILL.md`                                                                                                | exact command, exit code, decisive output                               |
| Documentation lifecycle                               | [`standards/documentation.md`](standards/documentation.md)                                                                                               | narrow markdown gate, then docs audit                                   |
| Workspace Make behavior                               | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) and [ADR-004](architecture/adr/004-generated-make-codegen-ssot-flext-infra.md)     | `make help` and affected dispatcher gate                                |
| Enforcement catalog identity and routing              | `flext-infra` declarative catalog; any remaining Core declarations are migration input under [ADR-028 Decision 5](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-5) | active owner-claim census and affected project gate                     |
| Declarative enforcement payloads and execution        | `flext-infra` rules, schemas, and engine                                                                                                                 | enforcement engine result                                               |
| Git repositories and local Git operations             | `flext-infra` public facades                                                                                                                             | local repository behavior and native gates                              |
| GitHub operations and credentials                     | ai-hub public runtime surface                                                                                                                            | ai-hub command, hook, MCP, or daemon evidence                           |
| CRG runtime, database, watcher, and graph services    | ai-hub validated config and runtime                                                                                                                      | ai-hub public health and routing evidence                               |
| Structural codemods                                   | `flext-infra` workspace-analysis and semantic-refactoring capabilities, composed with the declared structural-rule provider ([ADR-028 Decision 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17), [Decision 18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-18)) | preview, exact cardinality, apply, idempotence                          |

The owning declaration, validated config, or fundamental rule is the source of truth.
Tests and checks validate it; they never define the contract, catalog, or routing
decision.

## Declaration invariants (apply to every slice)

Forward obligations on every code, docs, and example slice — applied while
writing, before any review. The law owns the rules; this table only routes each
invariant to its canonical authority and never restates it. Record how each
invariant was satisfied in the active Bead before completion; place declarations
through `make mod` and regenerate projections through `make gen`.

| Invariant       | Always                                                                                                                                              | Canonical authority                                                                                                                                                                                                                                                                                              |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SSOT            | One canonical owner per fact; derive every projection from its owner; never redeclare, freeze a configured value, or hand-edit a generated surface. | [P0 in the root law](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md#p0--tests-validate-configsettings-changes-by-construction), [ADR-005](architecture/adr/005-config-settings-constants-templates-schemas-ssot.md), [ADR-024](architecture/adr/024-di-config-contract-derived-defaults-minimal-overrides.md)                                        |
| YAGNI           | Build or port nothing without a live consumer; adopt the existing lane or owner first; delete the superseded owner in the same slice.               | [FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md) and [Engineering Conformance Review](#engineering-conformance-review)                                                                                                                                                                                           |
| DRY             | One behavior, one owner; reuse the facade letters and existing helpers instead of adding a parallel helper, registry, wrapper, or fallback.         | [Owner Routing](#owner-routing), [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md), and [ADR-028 Decision 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17)                                                                 |
| Pydantic        | Owned payloads are Pydantic v2 models extending `m.*` presets; JSON enters via `model_validate_json`; declarations stay data-only; no `model_rebuild`. | `~/.agents/skills/technology/pydantic-development/SKILL.md` (filesystem reference; a missing authority fails closed) and the [Pydantic review](#engineering-conformance-review)                                                                                                                                  |
| SOLID           | One specialized service per use case; declaration layers carry zero methods; behavior lives only in `u`, bases, services, `api`, and `cli`.         | [Domain, namespace, MRO review](#engineering-conformance-review) and [FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md)                                                                                                                                                                                            |
| DI              | Dependencies cross use-case boundaries through generic `p` protocol ports injected at the `api` composition root; consumers never identify an implementation by its library. | [ADR-028 Decision 15](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15), [Decision 16](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-16), and [ADR-024](architecture/adr/024-di-config-contract-derived-defaults-minimal-overrides.md) |
| Clean Architecture | Facades compose strictly `c -> t -> p -> m -> u`; reverse imports are `TYPE_CHECKING`-only; internal tiers never import public `src` upward.     | [Architecture overview](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md#architecture-overview), [ADR-014](architecture/adr/014-family-part-shape-rope-codemod-rules.md), and [ADR-028 Decisions 1–4 and 17](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17) |
| FLEXT placement | Every declaration sits in its canonical namespace and family location; structural moves run through `make mod`; consumption follows R1-R6.          | [ADR-018](architecture/adr/018-generator-declarations.md), [ADR-015](architecture/adr/015-consumer-consumption-law.md), and [ADR-028 Decisions 15–18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15)                                                    |

### ADR-028 Decision Map

| ADR declaration | Nearest workspace declaration |
| --- | --- |
| [Decision 5](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-5) | [Owner Routing, enforcement catalog](#owner-routing) |
| [Decisions 15 and 16](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-15) | [Declaration invariants, DI](#declaration-invariants) |
| [Decisions 17 and 18](https://github.com/flext-sh/flext/blob/0.12.0-dev/docs/architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md#decision-17) | [Owner Routing, structural codemods](#owner-routing) |

## Engineering Conformance Review

Use this review route before accepting a change; the linked law owns the rules,
not this checklist. Record decisions and evidence in the active Bead.

| Review | Required evidence and canonical reference |
| --- | --- |
| SSOT, YAGNI, DRY, SOLID | Search existing libraries, owners, consumers, lanes, and public helpers first. Name the current requirement and one writable owner; reuse or extend it instead of adding a parallel helper, registry, facade, or speculative framework. See [ADR-005](architecture/adr/005-config-settings-constants-templates-schemas-ssot.md) and [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md), whose maturity is recorded in the [ADR index](architecture/adr/README.md). |
| Domain, namespace, MRO | Identify the introducing declaration and public namespace, not merely a matching path. Compose `c -> t -> p -> m -> u`; place constants, aliases, ports, models, and utilities at their respective canonical private-family owners and expose them through generated public facades. See [FLEXT law](https://github.com/flext-sh/flext/blob/0.12.0-dev/.agents/skills/flext-law/SKILL.md), [ADR-014](architecture/adr/014-family-part-shape-rope-codemod-rules.md), [ADR-015](architecture/adr/015-consumer-consumption-law.md), and [ADR-018](architecture/adr/018-generator-declarations.md). |
| Pydantic and behavior | Keep declaration layers data-only with permitted Pydantic validation/computed fields; use the existing `m.*` presets and typed `t.*`/`p.*` contracts. Parse owned payloads with `model_validate`/`model_validate_json`, serialize with `model_dump`; algorithms belong in `u`, reusable foundations in `base`, use cases in services, composition in `api`, and transport in `cli`. Follow the canonical `pydantic-development` skill, not a local model/helper clone. |
| DI and Clean Architecture | Inject `p` ports explicitly at the `api` composition root. Keep dependencies inward toward `flext-core`; services do not construct adapters, resolve hidden globals, or import build tooling at runtime. Config/settings remain layer zero. See [ADR-024](architecture/adr/024-di-config-contract-derived-defaults-minimal-overrides.md); [ADR-019](architecture/adr/019-service-contract-ports-operations.md) records proposed service rationale, not independent acceptance evidence. |
| Complete cutover | Rewire inherited consumers, public imports, tests, scripts, examples, and executable docs through the existing semantic automation; remove the superseded owner in the same slice. No suppression, fallback, shim, compatibility alias, duplicate route, or weakened gate substitutes for root-cause repair. See [ADR-023](architecture/adr/023-repair-phases-mod-loop-callbacks.md). |
| Runtime and fixed point | Prove the staged artifact with real public consumers before publication, then public behavior tests and all applicable lint/type/rule/build/docs gates. Expected config values come from typed SSOT, not frozen literals. Regenerate only from owners and prove repeated gen/fix/fmt and affected migrations are no-op on the unchanged candidate. Follow [root completion law](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md), [Make commands](guides/make-commands.md), and [stabilization](ways-of-working/stabilization-checkpoint-0.12.md). |

## Execution Contract

- Use the workspace Beads database for the root and every member project. Only an
  independent project owns a separate tracker.
- Claim and record disjoint path ownership before writes. Append evidence after every
  state-changing step.
- Inspect the real owner and all affected consumers before changing behavior.
- Update docs, skills, agents, and provider metadata when reality changes; when it does
  not, verify the impacted surfaces are current.
- Keep one owner per fact. Delete replaced prose, aliases, wrappers, fallbacks, and
  parallel paths in the same change.
- Land only after narrow gates and the affected native gate pass. Use explicit
  pathspecs, a scoped commit, a fast-forward push, and Bead evidence.

Static enforcement and structural codemods are separate responsibilities. Declarative
enforcement data owns policy; the referenced codemod provider owns safe, deterministic
source transformations. Neither duplicates the other. Public ai-hub runtime services may
enrich discovery when available, but FLEXT never imports them as libraries and their
absence does not invalidate its local deterministic path. A selected, available
integration still fails causally.

## Universal test contract (P0)

Follow [P0 in the root law](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md#p0--tests-validate-configsettings-changes-by-construction),
projected from `~/.agents/AGENTS.md`. At review, identify the typed config/settings
owner used by production and verify that tests, goldens, and executable examples
validate its contract rather than freezing today's values. This checkpoint does
not define a second test policy.

## Baseline Commands

Use the standard workspace commands; mutation is the verb's declared default operation
(selector-free):

```bash
make help
make setup
make check
make tests
```

`make help` owns the current inventory; the complete lifecycle is documented in
[Make Commands](guides/make-commands.md) without freezing a target count here. All FLEXT
validation uses the root Make dispatcher and every Python test run retains the canonical
testmon cache; never run bare `ruff`, `pyrefly`, `pyright`, `mypy`, or `pytest`
commands.

Record every red or green result with its exit code and decisive output in the active
workspace Bead.

For the worker lane contract, see
[`ways-of-working/worker-lane-contract.md`](ways-of-working/worker-lane-contract.md).
