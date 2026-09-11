# ADR-009 — Ecosystem coordination and reusable-library evaluation across internal and external projects

- **Status:** Accepted (planning) — targets the `0.20.0-dev` line
- **Date:** 2026-07-18
- **Target line:** FLEXT `0.20.0-dev`, an early development and planning branch.
  This coordination contract is the forward target for `0.20.0-dev`; it does not
  retro-fit the `0.12.0-dev` release line, whose critical fixes stay separate.
- **Scope:** Coordination contract for the whole Cosmos ecosystem: FLEXT
  packages (`flext-core`, `flext-cli`, `flext-infra`, and the rest) plus the
  independent external applications `cosmos-docgen`/`dcdoc`, DataOP, and
  DcBackup, and the external platforms they integrate with.
- **Tracking:** `mro-ib6t` (FLEXT boundaries) plus the ecosystem-coordination
  epic and children created for this ADR, all labelled `branch:0.20.0-dev`.
- **Complements:** ADR-002 (v0.13.0 baseline), ADR-003 (topology), ADR-004
  (Make/codegen), ADR-005 (config/settings SSOT), ADR-008 (neutral consumer
  boundaries).

This ADR is the single FLEXT-side coordination contract. The owner-local
decisions live in each application repository and are referenced here; this ADR
does not restate their internals and does not make any external repository a
FLEXT dependency.

## Context

The workspace root FLEXT project is the coordination point for a set of
independent applications that all consume FLEXT foundations:

- `cosmos-docgen`/`dcdoc` — document, proposal, and RCA artifact application.
- DataOP (`/home/marlonsc.new/.leaks`) — dataset organization and evidence.
- DcBackup (`/home/datacosmos.bkp/datacosmos-backup`) — Google Workspace backup.

Each has its own Beads tracker, its own ADRs, and its own release lifecycle.
They must work together — documentation platform, data ingestion, backup — and
they must reuse FLEXT libraries, without turning application details into FLEXT
dependencies and without creating new packages that merely relocate code.

ADR-008 already fixed the neutral-boundary rules FLEXT itself must honor. This
ADR adds the coordination view: which project owns what, in which order actions
run, how the still-open libraries are evaluated, and the gate any new `flext-*`
package must pass.

Timing: `0.20.0-dev` is at the start of development and planning. This ADR is
therefore a forward planning contract. Coordination targets, the static-consumer
docs mode, the Office boundary completion, and every open-library evaluation are
implemented on the `0.20.0-dev` line; nothing here forces changes onto the
`0.12.0-dev` release line.

## Decision

### 1. Four coordination planes

| Plane | Members | Role |
| --- | --- | --- |
| Domain applications | `dcdoc`, DataOP, DcBackup | Own domain intent, configuration, adapters, manifests, authorization |
| Reusable libraries | `flext-core`, `flext-cli` | Own generic, neutral, typed contracts consumed downward |
| Repository tooling | `flext-infra` + MkDocs | Externally invoked docs/build/codegen tooling |
| External platforms | Airflow, Dify, Drive/DMS, Backstage, XWiki, PipesHub, ClickHouse | Integrated through commands, files, manifests, APIs, events |

### 2. Dependency direction is one-way and enforced

```text
dcdoc / DataOP / DcBackup ---> flext-cli ---> flext-core
flext-infra --------------------> flext-cli / flext-core
```

Forbidden, and verified by the ADR-008 gates:

```text
any flext-* -X-> dcdoc / cosmos-docgen / dataop / dc_backup
dcdoc       -X-> flext_infra   (runtime/source import)
dcdoc  -X-> DataOP   -X-> DcBackup   (no lateral application imports)
```

Applications never import one another. They cooperate only through versioned
files, manifests, APIs, events, and an external orchestrator.

### 3. Ownership matrix (authoritative)

| Capability | Owner | Coordinated action |
| --- | --- | --- |
| Document/proposal/RCA artifacts, brand, formulas, publication authorization | `dcdoc` | Produces artifacts + neutral manifest |
| Dataset scan, manifest, provenance, catalog/dedup/archive/report | DataOP | Produces datasets/manifests/evidence |
| Backup, snapshot, retention, restore, recovery drills | DcBackup | Consumes neutral artifact inputs |
| Generic DOCX/PPTX/XLSX bytes, CLI, file, hash primitives | `flext-cli` | Extended only with neutral primitives |
| Typed foundations (`Result`, models, protocols, settings) | `flext-core` | Reused unchanged by domain |
| Docs site: generate/build/validate/audit/publish | `flext-infra` + MkDocs | Invoked externally per repository |
| Orchestration/scheduling | Airflow (external) | Composes the commands above |
| Content/RAG assist | Dify/Weaviate (external) | Feeds structured content into `dcdoc` |
| Portal/DMS/catalog | Backstage, XWiki, PipesHub, Drive (external) | Consume static output/artifacts by contract |

### 4. Coordination flow across all projects

```text
Airflow / operator / CI
  1. DataOP        -> datasets + manifest + evidence        (ClickHouse/Iceberg)
  2. Dify          -> structured content / tokens           (optional, into dcdoc)
  3. dcdoc build   -> artifacts + neutral artifact manifest
  4. dcdoc publish -> stage/dry-run/apply (authorized only)
  5. DcBackup      -> snapshot + checksummed manifest + restore drill
  6. flext-infra   -> docs generate/build/validate/audit
  7. publish       -> static site (later: Backstage TechDocs)
```

Every step is an isolated process. A failure in one step stops the chain
without any cross-application import.

### 5. Neutral integration contract

Applications exchange a neutral artifact envelope carrying only cross-domain
facts: schema version, producer, artifact identifier, media type, byte size,
SHA-256 digest, creation time, source digest, and URI/path. Domain-specific
fields (document kind, dataset source category, backup snapshot set) remain
producer extensions and never leak into FLEXT libraries.

### 6. Platform selection (ecosystem-wide)

| Candidate | Decision | Rationale |
| --- | --- | --- |
| MkDocs via `flext-infra` | Adopt after static-consumer gate (`mro-ib6t.1`) | Existing owner for site/search/nav/build/audit |
| Sphinx + MyST | Do not add in parallel | Duplicates the site owner; no measured gap justifies it |
| Pandoc | Keep, use directly | Mature conversion already used by `dcdoc` |
| Quarto | Corpus bake-off only (`bd-bhg1.2`) | Unproven for rich editable Office fidelity |
| Antora | Conditional future migration | Only if multi-repo/multi-version docs dominate |
| Docusaurus | Reject for current requirements | Adds React/MDX/Node without demonstrated need |
| Backstage TechDocs | Future reader/catalog | Consumes MkDocs static output |
| Zensical | Track with compatibility probes | Plugin coverage not yet equivalent |

No candidate replaces DOCX/PPTX/XLSX domain production.

### 7. Open libraries and possible new `flext-*` packages

The previously proposed `flext-docs`, `flext-gworkspace`, and a
backup-as-library were all rejected as premature extractions. This ADR keeps
them as explicitly evaluated, gated candidates rather than silent backlog:

| Candidate | Current verdict | Re-evaluation trigger | Tracking |
| --- | --- | --- | --- |
| `flext-docs` (generation engine) | Rejected | A second real consumer of the generation engine appears AND extraction is deletion-positive | epic child |
| `flext-gworkspace` (Drive DMS) | Rejected in current form | A deployed DMS owner + neutral Google contract + ≥2 consumers | epic child |
| Backup as shared library | Not created | DcBackup primitives proven reusable by a second consumer | epic child |
| Static-consumer docs mode in `flext-infra` | Accepted, to build | Immediate: required by Cosmos site | `mro-ib6t.1` |
| Generic Office byte completion in `flext-cli` | Accepted, to build | Immediate: required by ADR-018 | `mro-ib6t.2` |
| Neutral artifact-envelope model in a FLEXT owner | Deferred | ≥2 consumers need the identical neutral contract | epic child |

### 8. Extraction gate for any new `flext-*` package

A capability moves from an application into a FLEXT package only when all hold:

1. at least two independent real consumers need the same neutral behavior;
2. the contract carries no producer-domain models, names, config, or literals;
3. the migration deletes more code/dependencies than it adds;
4. every consumer migrates in one cut with no compatibility shim;
5. the owning FLEXT repository accepts and tests the public contract.

Otherwise the behavior stays in its application. "Might be reusable" is not a
reason to create a package.

## Consequences

- The root FLEXT workspace has one consultable coordination contract covering
  internal and external projects.
- The open libraries are tracked as gated candidates, not lost backlog.
- No application becomes a FLEXT dependency; no new package is created without
  the extraction gate.
- External platforms integrate by process/file/API/event, keeping FLEXT
  reusable and the applications independently deployable.

## Verification contract

1. ADR-008 reverse-dependency gate stays green across every `flext-*` package.
2. The coordination document `docs/architecture/ecosystem-coordination.md`
   stays consistent with this ADR and each owner-local ADR.
3. Each open-library candidate has a Bead recording its verdict and trigger.
4. No new `flext-*` package lands without a recorded two-consumer,
   deletion-positive extraction proof.

## References

- [ADR-008 — Neutral consumer boundaries](008-neutral-consumer-boundaries.md)
- [Ecosystem coordination](../ecosystem-coordination.md)
- Cosmos ADR-020 (`bd-bhg1`)
- DataOP ADR-001 (`data-organization-pipeline-4dt`)
- DcBackup ADR-001 (`datacosmos-backup-o6w`)
