---
name: flext-ecosystem-patterns
description: 'Use when deciding which flext-sh package owns a capability, adding cross-package behavior, or reviewing dependency direction and generated workspace projections.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Ecosystem Patterns

## Ownership map

| Concern | Canonical owner | Consumer pattern |
| --- | --- | --- |
| Results, types, models, settings, DI, logging | `flext-core` | Import the public facade or protocol |
| CLI parsing, output, prompts, process execution | `flext-cli` | Keep package commands as typed routers |
| Shared fixtures, enforcement dispatch, Make framework | `flext-tests` | Configure and invoke; do not fork runners |
| Workspace automation, generation, dependency analysis | `flext-infra` | Extend the owning service and dispatcher |
| Domain behavior | Domain package | Expose typed services to adapters |
| Extraction/loading/transformation | `flext-tap-*`, `flext-target-*`, `flext-dbt-*` | Compose platform and domain contracts |

## Decision procedure

1. Classify the requested behavior by concern, not by the package where the need
   was first observed.
2. Search public facades, protocols, services, Make dispatch, and enforcement
   catalogs for an existing owner.
3. Verify the exact dependency contract in the baseline and accepted ADRs; do not
   infer a universal package-layer arrow from repository naming.
4. Extend the owner and update all consumers in one cutover. Do not put shared
   behavior in an integration package or create a convenience wrapper.
5. If the changed surface is managed, update its model/template/generator and prove
   regeneration is deterministic.
6. Validate the owner project first, then direct consumers, then the workspace gate
   appropriate to the contract.

## Ecosystem invariants

- Public packages depend inward; the kernel never imports integration packages.
- Facades expose stable concepts while private modules retain implementation detail.
- Configuration values have one typed owner and are never copied into tests or docs.
- A command, generator, or rule has one entry point and one declared owning skill.
- Package metadata and common tooling are generated from workspace standards;
  project-specific behavior uses documented custom extension points.
- Cross-package API changes require a caller census, export update, and consumer tests.
- The generic Make registry belongs to `flext-tests` through `c/t/m/u.Tests`; root
  public verbs are dispatcher-thin, while `flext-infra` renders managed artifacts.
- Workspace inventory comes only from declared workspace/submodule metadata, never
  dependency heuristics or hardcoded external project lists.

## Evidence

Record the ownership decision, searched symbols, changed source, regenerated files,
direct consumers, and the narrow-to-broad validation sequence. A passing owner test
alone does not prove an ecosystem cutover.

## References

- [`AGENTS.md`](../../../AGENTS.md)
- [`docs/GOVERNANCE.md`](../../../docs/GOVERNANCE.md)
- [`docs/architecture/baseline-v0.13.0.md`](../../../docs/architecture/baseline-v0.13.0.md)
