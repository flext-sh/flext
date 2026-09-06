# Ecosystem Coordination — FLEXT, Cosmos applications, and external platforms

<!-- TOC START -->
- [Projects and owners](#projects-and-owners)
- [Dependency law](#dependency-law)
- [End-to-end coordination flow](#end-to-end-coordination-flow)
- [Per-project responsibilities](#per-project-responsibilities)
  - [`dcdoc` (cosmos-docgen)](#dcdoc-cosmos-docgen)
  - [DataOP](#dataop)
  - [DcBackup](#dcbackup)
  - [`flext-cli`](#flext-cli)
  - [`flext-infra`](#flext-infra)
  - [`flext-core`](#flext-core)
- [External platforms](#external-platforms)
- Open libraries and possible new `flext-*` (gated)
- [Project standardization (ADR-010)](#project-standardization-adr-010)
- Extraction gate for any new `flext-*`
- [Coordination Beads](#coordination-beads)
<!-- TOC END -->

This document is the consultable coordination reference for the whole Cosmos
ecosystem from the FLEXT workspace. It is governed by
[ADR-009](adr/009-ecosystem-coordination-and-library-evaluation.md) and must
stay consistent with each owner-local ADR. It coordinates internal FLEXT
packages and the independent external applications and platforms; it never makes
an external repository a FLEXT dependency.

**Target line:** FLEXT `0.20.0-dev` (early development and planning). This is a
forward planning contract for `0.20.0-dev`; it does not retro-fit the
`0.12.0-dev` release line. Every coordination Bead is labelled
`branch:0.20.0-dev`.

## Projects and owners

| Project | Kind | Repository | Owner ADR / tracker |
| --- | --- | --- | --- |
| `flext-core` | FLEXT library | `flext-core` | ADR-002/005/008 |
| `flext-cli` | FLEXT library | `flext-cli` | ADR-008, `mro-ib6t.2` |
| `flext-infra` | FLEXT tooling | `flext-infra` | ADR-003/004/008, `mro-ib6t.1` |
| `dcdoc` | External application | `cosmos-docgen` | ADR-020 (`dcdoc-bhg1`) |
| DataOP | External application | `~/dataop` | DataOP ADR-001 (`data-organization-pipeline-4dt`) |
| DcBackup | External application | `/home/datacosmos.bkp/datacosmos-backup` | DcBackup ADR-001 (`datacosmos-backup-o6w`) |

## Dependency law

```text
dcdoc / DataOP / DcBackup ---> flext-cli ---> flext-core
flext-infra --------------------> flext-cli / flext-core
```

Forbidden:

```text
any flext-* -X-> dcdoc / cosmos-docgen / dataop / dc_backup
dcdoc       -X-> flext_infra   (runtime/source import)
dcdoc -X-> DataOP -X-> DcBackup   (no lateral application imports)
```

Applications cooperate only through versioned files, manifests, APIs, events,
and an external orchestrator.

## End-to-end coordination flow

```text
Airflow / operator / CI
  1. DataOP        -> datasets + manifest + evidence     (ClickHouse/Iceberg)
  2. Dify          -> structured content / tokens        (optional -> dcdoc)
  3. dcdoc build   -> artifacts + neutral manifest
  4. dcdoc publish -> stage / dry-run / apply (authorized)
  5. DcBackup      -> snapshot + checksummed manifest + restore drill
  6. flext-infra   -> docs generate/build/validate/audit
  7. publish       -> static site (later: Backstage TechDocs)
```

## Per-project responsibilities

### `dcdoc` (cosmos-docgen)

Owns `dcdoc.config.yaml`, documents/decks/charts/diagrams, brand, formulas,
manifests, publication authorization, and Pandoc/Chromium/Marp orchestration.
Produces artifacts and a neutral manifest. Invokes `flext-infra` externally for
docs. Does not import `flext-infra`, DataOP, or DcBackup.

### DataOP

Owns dataset scan, `manifest.json`/`manifest.parquet`, provenance, source
registry, ClickHouse/Iceberg adapters, and catalog/dedup/archive/report.
Full-scale post-processing is still open work. Publishes datasets, manifests,
and evidence as neutral outputs; is never imported by other projects.

### DcBackup

Owns backup, snapshot, retention, restore, and recovery drills. Currently
planning-first/fake-safe; live checksummed snapshot and verified restore are
future work. Consumes neutral artifact inputs from `dcdoc`/DataOP; imports
neither.

### `flext-cli`

Owns generic CLI/process/file/hash primitives and typed DOCX/PPTX/XLSX
plan-to-byte boundaries. No application vocabulary or reverse dependency.

### `flext-infra`

Owns repository tooling: generated Markdown, MkDocs config, strict build,
validation, audit, publication. Needs a static non-FLEXT consumer mode
(`mro-ib6t.1`) before Cosmos adoption, because current API pages use live
`mkdocstrings`.

### `flext-core`

Owns generic typed foundations only. A neutral artifact-envelope model may be
added later under the extraction gate, never preemptively.

## External platforms

| Platform | Role | Contract |
| --- | --- | --- |
| Airflow | Orchestration | Runs the coordination flow steps as isolated processes |
| Dify / Weaviate | Content/RAG assist | Feeds structured content/tokens into `dcdoc`; no authority over layout/publish |
| Google Drive / DMS | Publication target | `dcdoc` publishes via stage/apply; full DMS is a future gated capability |
| Backstage TechDocs | Reader/catalog | Consumes MkDocs static output when deployed |
| XWiki / PipesHub | Knowledge plane | Receive content by API when deployed; not FLEXT dependencies |
| ClickHouse | Warehouse | DataOP sink/source |

Platform deployment status is planned/conditional until proven by executable
evidence.

## Open libraries and possible new `flext-*` (gated)

| Candidate | Verdict | Re-evaluation trigger |
| --- | --- | --- |
| `flext-docs` | Rejected | Second real consumer + deletion-positive extraction |
| `flext-gworkspace` | Rejected in current form | Deployed DMS owner + neutral Google contract + 2 consumers |
| Backup shared library | Not created | DcBackup primitive proven reusable by a second consumer |
| Static-consumer docs mode | Accepted, to build | Immediate — `mro-ib6t.1` |
| Generic Office byte completion | Accepted, to build | Immediate — `mro-ib6t.2` / `dcdoc-gsnp` |
| Neutral artifact-envelope model | Deferred | Two consumers need the identical neutral contract |

## Project standardization (ADR-010)

All projects — root, internal members, loose internal (independent), and
external applications — share one generated base owned by `flext-infra` codegen
with `flext-tests`: identical Make verbs, `.venv`/mise/direnv/`pyproject` setup,
directory layout, `__init__.py` facades, `c/t/p/m/u` facade files and
`_constants/*`/`_utilities/*` private namespaces, `api.py`/`base.py`/
`_settings.py`/`_config.py`, and canonical module/class/prefix naming for `src`,
`tests`, `examples`, `scripts`. Rollout is validation-first, then refactoring,
then declarative enforcement. SSOT: `codegen.yaml` + `tooling.yaml` +
`flext-tests`. See
[ADR-010](adr/010-unified-project-standardization-via-codegen.md).

## Extraction gate for any new `flext-*`

1. Two independent real consumers need the same neutral behavior.
2. No producer-domain models, names, config, or literals in the contract.
3. Migration deletes more code/dependencies than it adds.
4. All consumers migrate in one cut, no compatibility shim.
5. The owning FLEXT repository accepts and tests the public contract.

## Coordination Beads

- FLEXT boundaries: `mro-ib6t` (+ `mro-ib6t.1`, `mro-ib6t.2`).
- Ecosystem coordination epic and open-library candidates: see the epic linked
  from ADR-009.
- Cosmos: `dcdoc-bhg1` (+ `dcdoc-bhg1.1`, `dcdoc-bhg1.2`), `dcdoc-gsnp`.
- DataOP: `data-organization-pipeline-4dt`.
- DcBackup: `datacosmos-backup-o6w` (+ `datacosmos-backup-o6w.1`).
