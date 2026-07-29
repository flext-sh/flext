# FLEXT Documentation Index

<!-- mro-wkii.17.7 (agent: codex) — route Make and workspace guidance to the conform SSOT. -->

The root portal is intentionally small. It documents the FLEXT workspace itself, not every historical note or every
non-FLEXT directory in the repository.

## Quick Start

- [Governance router](GOVERNANCE.md) — active rule routing, ADRs, validation
  surfaces, and ratified refactor gates.
- [Onboarding (Collection Rules)](guides/onboarding.md) — required pre-work for ANY FLEXT project.
- [Architecture baseline for v0.13.0](architecture/baseline-v0.13.0.md)
- [ADR index](architecture/adr/README.md)
- [Ecosystem coordination (internal + external projects, `0.20.0-dev`)](architecture/ecosystem-coordination.md)
- [Migration guide](guides/migration-to-v0.13.0.md)
- [Workspace project catalog](projects/generated/catalog.md)
- [Workspace API overview](api-reference/generated/overview.md)

## Current Versioning Context

- Current workspace code: `0.12.0-dev`
- Forward baseline: `0.13.0`
- Latest tagged release documented here: `v0.11.0`

## Canonical Sections

- [Architecture](architecture/README.md)
- [Guides](guides/README.md)
- [Projects](projects/README.md)
- [API Reference](api-reference/README.md)
- [Standards](standards/README.md)

## Workspace tooling

`flext-infra codegen conform` is the sole owner of repository conformance and
generated Makefiles. It consumes the universal `flext-cli` config, schema, and
template engine and emits self-contained `workspace-root`, `workspace-member`,
or `standalone` profiles. Workspace topology comes only from the validated
manifest under `config/`; package metadata remains Git-and-branch sourced while
root `setup` installs declared local members as editable distributions.

The generated public Make surface contains thirteen targets: `help` plus the
twelve operational verbs defined by ADR-004. Project-specific behavior is
available only through validated private `custom.mk` handlers. See
[ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) for
topology and environments and
[ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md) for
Make/codegen ownership.

## Scope Boundary

The root portal governs only FLEXT packages and shared FLEXT infrastructure. If another internal directory lives in the
same repository but is not a FLEXT package, it must be documented in its own local tree and is not part of this portal.
