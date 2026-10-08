# ADR-024 — DI Config Contract: Derived Defaults, Self-Only Minimal Overrides, Generated Commented Defaults

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
  - [D1. A repository declares only facts about itself](#d1-a-repository-declares-only-facts-about-itself)
  - [D2. The library ships generic defaults only](#d2-the-library-ships-generic-defaults-only)
  - [D3. Injection, not discovery](#d3-injection-not-discovery)
  - [D4. Derive, never redeclare](#d4-derive-never-redeclare)
  - [D5. Pull, never push](#d5-pull-never-push)
  - [D6. Rules are data at their owner](#d6-rules-are-data-at-their-owner)
  - [D7. Versions only through locks](#d7-versions-only-through-locks)
  - [Fact owners](#fact-owners)
  - [Commented-defaults generator](#commented-defaults-generator)
- [Consequences](#consequences)
- [Rejected alternatives](#rejected-alternatives)
- [Verification contract](#verification-contract)

<!-- TOC END -->

- **Status:** ACCEPTED TARGET — operator order 2026-10-08; implementation phased under
  epic `flext-itpd1.11`
- **Date:** 2026-10-08
- **Target line:** FLEXT `0.12.0-dev`
- **Scope:** every repository `config/` directory the FLEXT toolchain reads — the
  workspace manifest (`config/workspace.yaml`), the `flext-infra` policy files
  (`codegen`, `tooling`, `infra`) and their per-repository overrides, and each
  package's own runtime config — across the `flext` workspace, its members, and every
  external repository that consumes `flext-infra`.
- **Supersedes:** ADR-022 in full; ADR-003 §1 ("a typed manifest owns repository
  topology"). Absorbs the operator decision of 2026-10-02 recorded on `flext-a0cjp`
  (`.gitmodules` is the sole composition owner).
- **Complements:** ADR-005 (config/settings SSOT — this ADR adds the override-layer law
  ADR-005 never declared), ADR-010 (standardization via codegen), ADR-018 (derive >
  list; a generator propagates, never compensates).
- **Tracking:** `flext-itpd1.11` (epic), `flext-a0cjp`, `flext-bvswv`, `flext-rg5ns`,
  `flext-7wpqk`, `flext-45kup`, `flext-dkoe4`, `flext-20yyv` (external push retired).

## Context

`flext-infra/config/workspace.yaml` redeclared, for one repository, values every typed
owner already derives — distribution, provider, URL, path, role, package, editability,
the whole project identity block, homepage, year, upstream — plus keys nothing reads
(`state`, `checkout: root`). Because `config/` is the package data directory, that
repository manifest shipped inside the `flext-infra` wheel and was merged, untyped, into
every consumer's config singleton.

The pattern repeated fleet-wide. The root manifest carried 31 member entries in which
only the name was data, and an `external_consumers` section naming private repositories
with absolute checkout paths of one machine, in a public repository. The packaged
`flext-infra` policy carried per-project sections (`project_overrides.<member>`,
per-consumer timeouts, a consumer-scoped text rule, a workspace publishing prefix, tool
version pins duplicating `mise.lock`), and `derive_class_stem` hardcoded two project
exceptions in Python.

The override layering was itself broken: the committed override file sorted before the
file it overrides, a consumer's local override file was never read, the organization
layer was read from the current directory, and four consumer channels had different
merge semantics.

Every one of these is the same defect: a component declaring or knowing facts owned by
another component. The operator ordered the whole class rewritten on 2026-10-08.

## Decision

### D1. A repository declares only facts about itself

No library, workspace, or consumer declares names, paths, branches, toggles, or
per-project keyed sections of another repository. The only composition fact a parent
owns is its own `.gitmodules` (path, url, branch, and the `flext-managed` attribute of
the 2026-10-02 decision); the parent's `make gen` is the single writer of the minimal
generated reference that marks a flext subproject as its member. A member's `kind` is
the member's own declaration. These are distinct facts with distinct owners: no
duplicate, no gate forcing two declarations to agree.

### D2. The library ships generic defaults only

`flext-infra`'s packaged configuration contains zero project names and zero per-project
maps. `flext-infra` as a repository is configured like any other repository: its own
manifest and tracker configuration are not package data.

### D3. Injection, not discovery

The engine receives the target repository root as a parameter. Effective configuration
for each owned file `F` is, in this explicit order:

1. the library default (packaged `F.yaml`);
2. the target repository's committed `config/F.yaml` (its own deltas);
3. the target repository's gitignored `config/F.local.yaml` (per-clone deltas).

Scalars of a later layer win, mapping keys add, lists concatenate. No current-directory
lookup and no ordering by file name. A config singleton reads only its own namespace
section (the flext-core `YAML_CONFIG_SECTION` hook, derived per subclass), so files of
other owners in the same directory never enter it.

### D4. Derive, never redeclare

A value the typed owner can derive from the repository's own tracked content is never
declared. A declaration equal to its derived default is a defect: `make check` reports
it and `make fix` removes it.

### D5. Pull, never push

A consumer advances by its own `make upg` → `make mod` → `make gen` → `make fix`.
Nothing in FLEXT lists consumers or pushes into them: the manifest `external_consumers`
section, its typed spec, the external propagation pass, the consumer list in fleet-gap
reporting, and candidate targets stored in a manifest are deleted. A candidate target
is injected by the invoker as a declared verb parameter.

### D6. Rules are data at their owner

Project exceptions never live in derivation code. The class-stem exceptions leave
`derive_class_stem`: `flext-core` declares `class_stem: Flext` and the workspace root
declares `class_stem: FlextRoot` (its live `FlextRoot*` code), each in its own manifest.

### D7. Versions only through locks

Tool version pins in configuration are deleted; the locks written by `make upg` are the
only version owners.

### Fact owners

| Fact | Single owner | In a repository manifest |
| --- | --- | --- |
| Composition (path, url, branch, `flext-managed`) | the parent's `.gitmodules` | never |
| Topology role | presence of `.gitmodules` | never |
| Distribution, description, license, authors, repository URL | PEP 621 `[project]` | never |
| provider, homepage, documentation | derived from `[project.urls].Repository` | only a genuine delta |
| package, class stem, namespace, alias, environment prefix | one derivation each in the existing owners | only a genuine delta with a live consumer |
| kind | the repository itself | required |
| integration branch | the repository itself; a composed member reads its parent's `.gitmodules` `branch` | only where it is the repository's own fact |

Deleted as dead (no reader): `checkout`, `state`, `beads_server`, `docs_audit`,
`integration.provider/organization/base_url`, `namespace_attribute`, `constant_name`,
`repository_root_rel`, the exclusion `reason` field (the reason becomes a YAML comment).

### Commented-defaults generator

One generic engine renders, into every repository `config/*.yaml` that overrides a
typed owner, a generator-owned marked block listing every overridable key with its
description and its resolved default as a YAML comment. Project-owned active deltas sit
above the block. Values come from library defaults and the repository's tracked content
only, so the block is clone-independent and deterministic in CI. `make gen` renders the
block; `make fix` drops deltas equal to their default; `make check` fails on a redundant
delta, an unknown key, or a stale block.

## Consequences

- A repository manifest shrinks to its kind plus its genuine deltas; the root manifest
  loses its member list and every consumer reference.
- The public `flext` repository no longer carries private repository names or
  machine-local paths.
- Consumers move on their own cadence through their own verbs; a red consumer never
  blocks the fleet, and the fleet never edits a consumer.
- The migration is a schema version boundary with no compatibility reader: retired keys
  are removed by a shipped codemod rule each repository applies through its own
  `make mod`.

## Rejected alternatives

- Keeping consumer declarations in a gitignored local layer — still a library that knows
  its consumers (D1, D5).
- Declaring kind both in `.gitmodules` and in the member, held together by an agreement
  gate — two owners of one fact plus a gate to hide the duplication.
- A separate generated `*.defaults.yaml` beside each override file — two files per
  contract for one fact set; the managed-block form keeps ownership explicit in one file.
- A compatibility reader for the previous manifest schema — forbidden residue.

## Verification contract

- `make gen` twice is byte-identical in every repository.
- A workspace checkout without initialized members renders byte-identical root
  projections.
- The installed `flext-infra` wheel contains no repository manifest, no tracker
  configuration, and no project name in its packaged configuration.
- A local-layer scalar beats the committed layer, which beats the library default,
  observed through the public read with an injected repository root.
- `make fix` removes a redundant declaration; re-adding it turns `make check` red.
- Zero occurrences fleet-wide of `checkout:`, `members:`, `external_consumers`,
  `candidate_bootstrap_targets`, `tool_version_pins`, `codegen-overrides`,
  `codegen-org`, or a machine-local absolute path in any tracked config.
