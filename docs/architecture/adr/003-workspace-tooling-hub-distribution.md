# ADR-003 — Manifest-owned topology, root workspace, and autonomous Git libraries

<!-- TOC START -->
- [Context](#context)
- [Decision](#decision)
  - [1. A typed manifest owns repository topology](#1-a-typed-manifest-owns-repository-topology)
  - [2. Root workspace and library metadata have distinct responsibilities](#2-root-workspace-and-library-metadata-have-distinct-responsibilities)
  - [3. Make orchestrates the root workspace environment](#3-make-orchestrates-the-root-workspace-environment)
  - [4. Generated profiles define attachment behavior](#4-generated-profiles-define-attachment-behavior)
- [Consequences](#consequences)
- [Verification contract](#verification-contract)
- [References](#references)
<!-- TOC END -->
- **Status:** Accepted (amended 2026-07-16)
- **Date:** 2026-06-24
- **Scope:** FLEXT, Cosmos, and standalone repository topology, dependency
  provenance, and development environments.
- **Tracking:** `mro-qb4y`, `mro-wkii.17`

<!-- mro-qb4y (agent: codex) — separate publishable Git metadata from the root development workspace. -->

## Context

Repository membership, dependency provenance, Make behavior, and local
development overlays had several competing owners. External Make includes,
implicit sibling discovery, and repository-local generators made a checkout
depend on the operator's filesystem. Member repositories also declared
`workspace = true` in `tool.uv.sources`, so installing one library directly from
Git incorrectly required the complete parent workspace to exist locally.

The same member must work inside the root checkout and as an independent Git
source. Standard dependency fields are the installable package contract;
`tool.uv.sources` is a uv-specific development overlay and cannot be the only
owner of transitive FLEXT provenance.

## Decision

### 1. A typed manifest owns repository topology

Each orchestrated workspace has one validated manifest under `config/`. It
declares members, exclusions, repository URL, branch, relative checkout path,
role, profile, and lifecycle state. A typed repository catalog covers:

- FLEXT repositories at `https://github.com/flext-sh/<repo>.git` on
  `0.12.0-dev`;
- Cosmos repositories at `https://github.com/datacosmos-br/<repo>.git` on
  `main`;
- explicitly declared standalone repositories, with no sibling discovery.

Submodule metadata, generated dependency groups, Makefiles, and inventories are
derived from that manifest. No other file may independently declare workspace
membership.

### 2. Root workspace and library metadata have distinct responsibilities

The root `flext` project is the only native uv workspace. It owns the complete
`tool.uv.workspace.members` list and one `tool.uv.sources.<member>` entry with
`workspace = true` for every manifest member. Those entries select local,
editable members only when work is orchestrated from the root.

Every non-root FLEXT library is independently installable. Its internal FLEXT
requirements in `project.dependencies`, `project.optional-dependencies`, and
`dependency-groups` are PEP 508 direct Git references pinned to the repository
URL and branch from `config/workspace.yaml`. Member and standalone projects do
not declare managed internal `tool.uv.sources` entries or a native
`tool.uv.workspace` table.

uv applies the root source table to attached workspace members, replacing their
direct Git requirements with the corresponding local members during root
development. Outside the root, standard package metadata resolves the same
distributions directly from Git without a sibling checkout or consumer-side
manifest rewrite. Repository lock policy does not own dependency identity.

Mise pins Python `3.13` and uv `0.9.21` for the root checkout. Generated
profiles require Python `3.13.11` and uv `0.9.21` from the toolchain SSOT.

### 3. Make orchestrates the root workspace environment

The generated root `setup` handler:

1. provisions the pinned toolchain;
2. validates the manifest and submodule inventory;
3. synchronizes the root dependency groups;
4. installs the root and declared workspace members into the root `.venv`;
5. runs the package consistency check and validates `direct_url.json` for every
   member.

This local selection is an environment operation, never a metadata rewrite. An
attached member delegates `setup` to the root. The same member in an independent
clone uses its own environment and Git-sourced FLEXT dependencies.

All other commands execute with `uv run --project <environment-owner>
--no-sync`. Checks and tests therefore cannot synchronize, relock, rewrite
metadata, or replace the editable overlay implicitly. Dependency upgrades are
an explicit, apply-gated `deps` operation followed by `setup`.

### 4. Generated profiles define attachment behavior

The sole template layer supports exactly two profiles, derived from the
checkout itself:

- `workspace` — the tree has `.gitmodules`;
- `standalone` — the tree does not.

No profile depends on files outside its repository checkout.

## Consequences

- Dependency identity and Git provenance remain manifest-owned and auditable.
- Local source editing is selected by the root workspace without weakening the
  autonomous package metadata of any member.
- A missing, extra, or misclassified member is a manifest validation error.
- Any command other than the explicit environment/dependency operations is
  read-only with respect to locks, environments, generated files, and sources.

## Verification contract

- Root lock/setup proves every declared internal dependency resolves to its
  workspace member.
- Representative members install from their Git URLs into fresh virtual
  environments with no parent workspace and no metadata rewrite.
- Standalone repositories pass from temporary clones with no neighboring
  repositories.
- Generated manifests are byte-idempotent; only the root contains managed
  `workspace = true` entries.

## References

- [ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`](./004-generic-make-framework-in-flext-tests.md)
- [ADR-005 — Config, settings, constants, templates, and schemas
  SSOT](./005-config-settings-constants-templates-schemas-ssot.md)
