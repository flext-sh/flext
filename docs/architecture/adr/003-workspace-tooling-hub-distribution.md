# ADR-003 — Manifest-owned topology and Git-first uv environments

- **Status:** Accepted (amended 2026-07-11)
- **Date:** 2026-06-24
- **Scope:** FLEXT, Cosmos, and standalone repository topology, dependency
  provenance, and development environments.
- **Tracking:** `mro-wkii.17`

<!-- mro-wkii.17.6 (agent: codex) — align topology and uv governance with the live operator decision. -->

## Context

Repository membership, dependency provenance, Make behavior, and local
development overlays had several competing owners. External Make includes,
implicit sibling discovery, and repository-local generators made a checkout
depend on the operator's filesystem. Native uv workspace membership also
requires member-local dependency provenance, which conflicts with the
requirement that every published FLEXT dependency always retain its Git URL and
branch in `pyproject.toml`.

The same member must work both inside its parent checkout and as an independent
clone. A static dependency declaration therefore cannot be rewritten merely
because a local checkout is available.

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

### 2. Package metadata is permanently Git-first

Every FLEXT source in every `pyproject.toml` is a Git URL pinned to the declared
branch. Local paths, absolute paths, conditional source selection, index
fallbacks, and native uv workspace membership are invalid source forms.

Every project owns a versioned lock and can provision an independent `.venv`.
Workspace roots additionally own PEP 735 `dev`, `codegen`, and `workspace`
groups; the `workspace` group lists every member through the same Git and branch
provenance used by an independent clone.

Python `3.13.11` and uv `0.11.28` are pinned consistently in Mise,
`.python-version`, and uv project metadata.

### 3. Make orchestrates the editable development overlay

The generated root `setup` handler:

1. provisions the pinned toolchain;
2. validates the manifest and submodule inventory;
3. synchronizes the locked root groups;
4. installs the root and all declared local members as no-dependency editable
   distributions into the root `.venv`;
5. runs the package consistency check and validates `direct_url.json` for every
   member.

This editable installation is an environment operation, never a metadata
rewrite. An attached member delegates `setup` to the root. The same member in
an independent clone uses its own lock, environment, and Git-sourced FLEXT
dependencies.

All other commands execute with `uv run --project <environment-owner>
--no-sync`. Checks and tests therefore cannot synchronize, relock, rewrite
metadata, or replace the editable overlay implicitly. Dependency upgrades are
an explicit, apply-gated `deps` operation followed by `setup`.

### 4. Generated profiles define attachment behavior

The sole template layer supports exactly three profiles:

- `workspace-root` — owns the shared environment and declared member fleet;
- `workspace-member` — delegates environment provisioning when attached and
  remains independently provisionable when detached;
- `standalone` — owns only itself and never inspects neighboring directories.

No profile depends on files outside its repository checkout.

## Consequences

- Dependency provenance remains auditable and identical in attached and
  independent operation.
- Local source editing is enabled by the root environment without weakening
  published metadata.
- A missing, extra, or misclassified member is a manifest validation error.
- Any command other than the explicit environment/dependency operations is
  read-only with respect to locks, environments, generated files, and sources.

## Verification contract

- Root `setup` proves every declared member is editable from its checkout.
- Each member passes attached and independent-clone checks with no metadata
  rewrite.
- Standalone repositories pass from temporary clones with no neighboring
  repositories.
- Lock hashes, generated files, environments, and source declarations remain
  unchanged across `check` and `test`.

## References

- [ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`](./004-generic-make-framework-in-flext-tests.md)
- [ADR-005 — Config, settings, constants, templates, and schemas SSOT](./005-config-settings-constants-templates-schemas-ssot.md)
