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
- [0.13 unified planning reconciliation (documentation only)](#013-unified-planning-reconciliation-documentation-only)

<!-- TOC END -->

- **Status:** Accepted (amended 2026-07-16); §1 SUPERSEDED (2026-10-08) by
  [ADR-024](024-di-config-contract-derived-defaults-minimal-overrides.md) — composition
  is owned by the workspace's `.gitmodules`, not by a manifest member list
- **Date:** 2026-06-24
- **Scope:** FLEXT, Cosmos, and standalone repository topology, dependency provenance,
  and development environments.
- **Tracking:** `mro-qb4y`, `mro-wkii.17`

<!-- mro-qb4y (agent: codex) — separate publishable Git metadata from the root development workspace. -->

## Context

Repository membership, dependency provenance, Make behavior, and local development
overlays had several competing owners. External Make includes, implicit sibling
discovery, and repository-local generators made a checkout depend on the operator's
filesystem. Member repositories also declared `workspace = true` in `tool.uv.sources`,
so installing one library directly from Git incorrectly required the complete parent
workspace to exist locally.

The same member must work inside the root checkout and as an independent Git source.
Standard dependency fields are the installable package contract; `tool.uv.sources` is a
uv-specific development overlay and cannot be the only owner of transitive FLEXT
provenance.

## Decision

### 1. A typed manifest owns repository topology

Each orchestrated workspace has one validated manifest under `config/`. It declares
members, exclusions, repository URL, branch, relative checkout path, role, profile, and
lifecycle state. A typed repository catalog covers:

- FLEXT repositories at `https://github.com/flext-sh/<repo>.git` on `0.12.0-dev`;
- Cosmos repositories at `https://github.com/datacosmos-br/<repo>.git` on `main`;
- explicitly declared standalone repositories, with no sibling discovery.

Submodule metadata, generated dependency groups, Makefiles, and inventories are derived
from that manifest. No other file may independently declare workspace membership.

### 2. Root workspace and library metadata have distinct responsibilities

Operator amendment (2026-10-10): the root and every member are independent UV
projects, each owning its physical `uv.lock` and Mise lock. Clarification (2026-10-13),
not a change to the editable standard: no `tool.uv.workspace` table or parallel
`workspace = true` dependency routing. The existing generator retains only a packaged
root's self-only implicit `workspace = true` source override, never member routing.
Composition remains owned by `.gitmodules` (ADR-024).

The root's existing `dev` group requests every declared package member, including
its declared extras and development groups. Local editable bindings select checkouts
only in the development environment; declared bounds, extras and markers remain intact.
External candidate Git pins never override a declared local member.

The `codegen` group remains the canonical bootstrap unit; it does not collect
all member development dependencies. Member groups compose into `dev`. The
generator marks only its added `dev` entries with inline TOML provenance comments.
Subsequent renders remove those owned entries before deriving the current member
environment, while unmarked CUSTOM requirements retain their constraints and
markers. This metadata records projection ownership, not another member registry
or dependency source of truth.

Every FLEXT distribution must be independently installable without a parent workspace
or consumer-side metadata rewrite. Registry-backed runtime and optional requirements
remain registry-backed; explicit Git requirements retain their declared URL and ref.
Both preserve declared constraints, extras and markers. Local editables are environment
bindings, not published requirement rewrites. Git and `pyproject.toml` own repository
identity; locks record resolved provenance, not a replacement dependency origin.

Mise and generated profiles consume the toolchain SSOT rather than versions copied into
this ADR.

### 3. Make orchestrates the root workspace environment

The generated root `setup` handler:

1. provisions the pinned toolchain;
2. validates the manifest and submodule inventory;
3. synchronizes the root dependency groups;
4. installs the root and declared workspace members into the root `.venv`;
5. runs the package consistency check and validates `direct_url.json` for every member.

This local selection is an environment operation, never a metadata rewrite. An attached
member delegates `setup` to the root. The same member in an independent clone uses its
own environment and its declared dependency origins.

All other commands execute with `uv run --project <environment-owner> --no-sync`. Checks
and tests therefore cannot synchronize, relock, rewrite metadata, or replace the
editable overlay implicitly. Dependency upgrades are an explicit, apply-gated `deps`
operation that updates the SSOT. `make upg` updates a member's own locks and
completes its convergence before invoking one root workspace upgrade for alignment.
Failure in the member prevents root alignment; a standalone upgrade runs only itself,
and a root upgrade never calls member upgrades back. `gen` writes managed projections,
and `setup` synchronizes the environment without writing locks.

### 4. Generated profiles define attachment behavior

The sole template layer supports exactly two profiles, derived from the checkout itself:

- `workspace` — the tree has `.gitmodules`;
- `standalone` — the tree does not.

No profile depends on files outside its repository checkout.

## Consequences

- Dependency origins remain declaration-owned and auditable; `.gitmodules` owns composition.
- Local source editing is selected by the root workspace without weakening the
  autonomous package metadata of any member.
- A missing, extra, or misclassified member is a manifest validation error.
- Apply-gated generation, build, and repair commands may mutate their declared outputs.
  Checks and tests never silently synchronize or rewrite dependencies.

## Verification contract

- Root lock/setup proves every declared internal dependency resolves to its workspace
  member.
- Every candidate distribution installs in a clean environment without a parent
  workspace. Verify dependency closure, package resources, and public runtime against
  the exact artifact; sampling members is not fleet release evidence.
- Standalone repositories pass from temporary clones with no neighboring repositories.
- Generated manifests are byte-idempotent; no native workspace table or member
  `workspace = true` routing survives. Only the packaged root's self-only implicit
  source override remains; local editability never rewrites published requirements.
- An attached member writes its own lock in the primary checkout, then aligns the
  root once. The native lock-owner guard rejects any remaining shared-lock topology.

## References

- [ADR-004 — Generated Make and codegen SSOT owned by `flext-infra`](./004-generated-make-codegen-ssot-flext-infra.md)
- [ADR-005 — Config, settings, constants, templates, and schemas SSOT](./005-config-settings-constants-templates-schemas-ssot.md)

## 0.13 unified planning reconciliation (documentation only)

- Disposition for the unified 0.13 plan: Reconcile `.gitmodules`, environments and locks; preserve superseded text.
- This note records planning reconciliation only. It does not change the ADR's recorded maturity, implementation status, or acceptance evidence.
- Future 0.13 API/ecosystem migration remains gated by `flext-ik359` (publication
  `flext-1wjg1` plus separate authorization) and approval of the documented contracts
  and consumer migration matrix. Current 0.12 validation, bug fixes and documentation
  continue under their owners; the ADR's proposal/status is unchanged.
