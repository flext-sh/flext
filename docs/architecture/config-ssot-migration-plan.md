# Make/codegen, configuration, and uv SSOT migration plan

This plan implements [ADR-003](adr/003-workspace-tooling-hub-distribution.md),
[ADR-004](adr/004-generic-make-framework-in-flext-tests.md), and
[ADR-005](adr/005-config-settings-constants-templates-schemas-ssot.md) under
epic `mro-wkii.17`. The live config/settings and runtime-policy cutover is
tracked by `mro-7akn`; its Bead ledger, not this document, owns execution state
and command evidence.

<!-- mro-wkii.17.6 (agent: codex) — replace stale phased paths with the one live conform migration. -->

## Delivery rules

- Reuse and deletion come first. New code requires a demonstrated gap in the
  canonical owner; every replaced surface is deleted in the same slice.
- Each refactor targets neutral or negative net source lines.
- There is one public verb, one `WHAT` selector, and one handler for an action.
- There are no compatibility modes, aliases, fallback paths, duplicate
  generators, or old-and-new coexistence.
- Python follows the FLEXT facades, MRO composition, typed config/settings,
  Pydantic v2 boundary round trips, and `r[T]` failure contracts.
- The complete selection is validated before mutation. Every apply is atomic,
  deterministic, and byte-idempotent.
- Each repository is validated and landed independently before a parent
  gitlink is updated.

## Canonical ownership

| Surface | Sole owner |
| --- | --- |
| repository catalog and workspace manifest | validated data under `flext-infra/config/` and each workspace `config/` |
| universal config/schema/template/file/process operations | public `u.Cli.*` facades in `flext-cli` |
| typed conformance plan, enforcement, and transaction | `flext-infra codegen conform` |
| generated Makefiles | the single `flext-infra` template layer |
| project-specific Make behavior | private handlers in versioned `custom.mk` |
| runtime contracts and primitives | runtime-minimal `flext-core` |

## Phase 1 — Consolidate the engine

1. Inventory existing loaders, renderers, generators, routes, and templates;
   select canonical owners and record the deletion map.
2. Complete the reusable `flext-cli` public config, schema, template, file,
   process, and output primitives before adding consumer logic.
3. Define the typed repository, workspace, Make, uv environment, request, plan,
   and result models through the FLEXT facades.
4. Move catalog and manifest rows into validated config plus matching schemas.
5. Implement the single `codegen conform` check/apply transaction by composing
   the existing project generator and migration capabilities.
6. Make project creation emit the initial manifest and invoke conformance.
7. Delete every superseded route, loader, renderer, migration engine, bootstrap
   generator, and template with its final caller.

Acceptance:

- public model validation and round-trip tests pass;
- invalid config, managed-file drift, and partial-write scenarios fail closed;
- new and existing fixtures with one manifest produce byte-identical trees;
- check mode preserves hashes and the second apply has no diff.

## Phase 2 — Generate the complete Make and uv contract

1. Generate one self-contained Makefile for `workspace-root`,
   `workspace-member`, and `standalone` from the same template layer.
2. Validate `custom.mk` as private `_custom_<verb>_<what>` handlers only.
3. Expose `help` plus the twelve operational verbs defined by ADR-004, with one
   selector and handler per action.
4. Generate permanent Git-and-branch FLEXT sources, versioned locks, pinned
   Python/uv toolchain metadata, and root PEP 735 groups.
5. Implement root `setup` as locked Git installation followed by the local
   no-dependency editable overlay and provenance validation.
6. Make attached members delegate environment provisioning and make detached
   members use their own environment and lock.
7. Ensure every other command executes without implicit synchronization.

Acceptance:

- all profiles parse and expose only the canonical public surface;
- Git provenance is unchanged before and after local overlay installation;
- every member's `direct_url.json` points to its declared local checkout after
  root setup;
- `check` and `test` preserve locks, environments, generated files, and sources.

## Phase 3 — Conform the FLEXT fleet

1. Conform each declared member independently and validate its own lock and
   temporary standalone clone.
2. Land every green member before updating its gitlink.
3. Conform the FLEXT root after members are green.
4. Run root setup and prove all 31 declared members are editable in the root
   environment.
5. Run attached checks/tests for every member and a complete root conformance
   check.

Any missing, extra, or unclassified member is a hard inventory failure.

## Phase 4 — Conform Cosmos

1. Conform the Cosmos root as `workspace-root`.
2. Conform Charts and GitOps as members that also pass in independent clones.
3. Mark content-only repositories explicitly and remove invalid inventory
   entries rather than treating them as package members.
4. Preserve real chart release behavior behind the canonical commit and push
   checks, including the clean-commit prerequisite.

## Phase 5 — Conform standalone repositories

Conform `.ai-hub`, projeto_a migration, projeto_b Meltano Native, and Cosmos Docgen
as explicit standalone manifests. Classify each real capability under the
canonical Make responsibility, delete competing automation surfaces, and test
from temporary clones with no sibling directories.

## Phase 6 — Fleet acceptance and deletion proof

For every repository, record exact command, exit code, and decisive output for:

- real import smoke;
- Ruff without fixes;
- type checking;
- public-interface tests;
- Make parse and help;
- lock validation;
- conformance check;
- second-apply idempotence.

The final audit must find no local dependency sources, absolute operator paths,
native uv workspace declarations, external Make implementation includes,
competing task runners, alternative package bootstrap, dead templates, public
aliases, duplicate verbs, or CI error suppression. Any finding keeps the epic
open and is fixed at its canonical source.
