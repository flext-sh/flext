# ADR-008 — Neutral consumer boundaries for docs, Office bytes, and artifact metadata

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
  - [Ownership](#ownership)
  - [Dependency direction](#dependency-direction)
  - [Static consumer documentation](#static-consumer-documentation)
  - [Neutral artifact metadata](#neutral-artifact-metadata)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
<!-- TOC END -->

- **Status:** Accepted
- **Date:** 2026-07-18
- **Scope:** FLEXT contracts consumed by independent Cosmos applications
- **Tracking:** `mro-ib6t`

## Context

`cosmos-docgen`/`dcdoc`, DataOP, and DcBackup are independent applications that
consume FLEXT foundations. They share needs for typed results, CLI and file
operations, hashing, Office byte mechanics, repository documentation tooling,
and possibly neutral artifact metadata. They do not share domain models,
configuration, adapters, or lifecycle rules.

Creating `flext-docs` by moving `dcdoc` modules would mix domain generation,
site generation, Office mechanics, and Google Workspace plans. Copying DataOP
adapters or DcBackup models into FLEXT would similarly turn application details
into unstable platform dependencies.

Name disambiguation: the rejected `flext-docs` in this ADR is a hypothetical
document-generation library extracted from `dcdoc`. It is unrelated to the
existing FLEXT `flext-docs-pointer-policy` skill and the `flext-docs
validate_links` tooling entrypoint, which stay valid.

## Decision

### Ownership

- `flext-core` owns generic typed foundations only.
- `flext-cli` owns generic CLI/process/file/hash operations and typed
  DOCX/PPTX/XLSX plan-to-byte boundaries.
- `flext-infra` owns repository tooling, including generated Markdown, MkDocs
  configuration, strict build, validation, audit, and static publication.
- Applications own their domain intent, configuration, adapters, manifests,
  orchestration, authorization, and deployment policy.

### Dependency direction

Every application may depend downward on public FLEXT packages. No `flext-*`
package may import or declare a dependency on `dcdoc`/`cosmos-docgen`, DataOP,
or DcBackup. `dcdoc` also does not import `flext-infra`; its repository invokes
that tool as a separate process.

### Static consumer documentation

The current API-page template uses live `mkdocstrings` directives. For
non-FLEXT repositories, accepted follow-up `mro-ib6t.1` must add a mode that
generates and builds a site from repository files and source text without
importing or executing the consumer package. Runtime-import-based API
documentation is not an accepted contract for these consumers.

### Neutral artifact metadata

An existing FLEXT owner may later expose a neutral artifact envelope containing
schema version, producer, artifact identifier, media type, byte size, SHA-256,
creation time, source digest, and URI/path. It must not contain `dcdoc`, DataOP,
DcBackup, Datacosmos, proposal, dataset-source, backup-service, or deployment
semantics.

No such shared model is required merely by this ADR. Extraction occurs only
when at least two real consumers need the identical contract and the migration
deletes more code/dependencies than it adds.

## Consequences

- MkDocs through `flext-infra` remains the single FLEXT documentation engine;
  Sphinx or another engine requires a measured migration decision rather than
  parallel adoption.
- ADR-018 Office work stays in `flext-cli`, with no domain literals or raw
  library objects crossing the boundary.
- `flext-docs` is not created.
- Cosmos applications integrate with each other through files, manifests,
  APIs, events, or orchestration, not through FLEXT reverse dependencies.

## Verification contract

1. Search every `flext-*` package for application imports and dependencies.
2. Before adoption, build non-FLEXT consumer docs with imports of that consumer
   package blocked.
3. Require two consumers and a deletion-positive diff before extracting a new
   public FLEXT contract.
4. Keep domain vocabulary out of generic Office, docs, file, and artifact
   modules.

## References

- Cosmos ADR-020 (`bd-bhg1`)
- DataOP ADR-001 (`data-organization-pipeline-4dt`)
- DcBackup ADR-001 (`datacosmos-backup-o6w`)
- [ADR-003 — Manifest-owned topology](003-workspace-tooling-hub-distribution.md)
- [ADR-004 — Generated Make and codegen SSOT](004-generic-make-framework-in-flext-tests.md)
- [ADR-005 — Config and settings SSOT](005-config-settings-constants-templates-schemas-ssot.md)
