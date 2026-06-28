# FLEXT Documentation Index

The root portal is intentionally small. It documents the FLEXT workspace itself, not every historical note or every non-FLEXT directory in the repository.

## Quick Start

- [Onboarding (Collection Rules)](guides/onboarding.md) — required pre-work for ANY FLEXT project.
- [Architecture baseline for v0.13.0](architecture/baseline-v0.13.0.md)
- [ADR index](architecture/adr/README.md)
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

FLEXT participates in the `~/.ai-hub` distributed workspace base. The common
thin-wrapper is included via `workspace_custom.mk` and exposes dispatcher verbs
through `make cosmos-help`. Existing FLEXT targets (`make check`, `make test`,
etc.) are unchanged. See [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md).

The generic registry-driven Make framework is owned by `flext-tests` and exposed
through `c/m/t/u.Tests`; `flext-infra` consumes it when rendering workspace
artifacts. See [ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md).

## Scope Boundary

The root portal governs only FLEXT packages and shared FLEXT infrastructure. If another internal directory lives in the same repository but is not a FLEXT package, it must be documented in its own local tree and is not part of this portal.
