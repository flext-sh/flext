# Documentation Knowledge Index

<!-- TOC START -->

- [Purpose](#purpose)
- [Documentation Layers](#documentation-layers)
  - [1. Manual & Curated](#1-manual-curated)
  - [2. Community Wiki (CRG)](#2-community-wiki-crg)
  - [3. Auto-Generated API Reference](#3-auto-generated-api-reference)
- [Package Quick Reference](#package-quick-reference)
- [Cross-Reference Map](#cross-reference-map)
- [Regeneration](#regeneration)
- [See Also](#see-also)

<!-- TOC END -->

> **AUTO-GENERATED — DO NOT EDIT MANUALLY.** Sources: `docs/` tree (manual-curated), CRG
> graph (code knowledge graph), and `mkdocstrings` directives (live from code).
> Regenerate with: `make gen`

## Purpose

This index is the single entry point for finding documentation across the three
documentation layers of the FLEXT workspace:

1. **Manual & Curated** — human-authored guides, ADRs, arc42 architecture, and
   standards.
2. **Community Wiki (CRG)** — code knowledge graph communities discovered by
   `code-review-graph`, linking responsibility clusters to concrete source symbols.
3. **Auto-Generated API Reference** — `mkdocstrings`-driven pages generated from
   `pyproject.toml`, public exports, and docstrings.

Each section below cross-references the other layers so readers can navigate from a
conceptual topic (ADR) → the code community that implements it (CRG wiki) → the live API
surface for that package (mkdocstrings).

## Documentation Layers

### 1. Manual & Curated

Curated documents that own architectural decisions, workflow guidance, and authoring
standards. These are hand-written and reviewed.

| Topic              | Document                                                               | What It Covers                                               |
| ------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------ |
| Architecture Index | [architecture/README.md](architecture/README.md)                       | Canonical architecture baseline + ADR index                  |
| arc42              | [architecture/arc42/README.md](architecture/arc42/README.md)           | 12-chapter architecture template                             |
| ADRs               | [architecture/adr/README.md](architecture/adr/README.md)               | 26 formal decision records (`ADR-001`–`010`, `014`–`030`)    |
| Code Communities   | [architecture/communities/index.md](architecture/communities/index.md) | CRG community wiki index                                     |
| Guides Index       | [guides/README.md](guides/README.md)                                   | Workflow, migration, day-to-day guides                       |
| Standards          | [standards/README.md](standards/README.md)                             | Cross-workspace authoring and library consumption standards  |
| Governance         | [GOVERNANCE.md](GOVERNANCE.md)                                         | Active rule routing, 5-layer governance, and validation      |
| Version Policy     | [version-policy.md](version-policy.md)                                 | Versioning and release policy                                |

### 2. Community Wiki (CRG)

The CRG knowledge graph (SQLite at `$CODE_REVIEW_GRAPH_DATA_DIR/graph.db`, defaulting to
`.code-review-graph/graph.db` when unset) indexes governed files, classes, functions, and
tests across all workspace members. The `wiki` subcommand runs Leiden community detection
on the call/import graph and emits one page per community into
`$CODE_REVIEW_GRAPH_DATA_DIR/wiki/`. Only governed communities with `>= 50` nodes are
published here; smaller clusters exist in the full CRG wiki.

| Community              | Size | Primary Package     | Link                                                                        |
| ---------------------- | ---- | ------------------- | --------------------------------------------------------------------------- |
| `codegen-infra`        | 688  | flext-infra         | [codegen-infra.md](architecture/communities/codegen-infra.md)               |
| `utilities-flext`      | 590  | flext-core/cli      | [utilities-flext.md](architecture/communities/utilities-flext.md)           |
| `codegen-infra-flext`  | 345  | flext-infra         | [codegen-infra-flext.md](architecture/communities/codegen-infra-flext.md)   |
| `services-server`      | 317  | flext-api/web       | [services-server.md](architecture/communities/services-server.md)           |
| `detectors-infra`      | 302  | flext-infra         | [detectors-infra.md](architecture/communities/detectors-infra.md)           |
| `gates-check`          | 290  | flext-infra/quality | [gates-check.md](architecture/communities/gates-check.md)                   |
| `phases-apply`         | 240  | flext-infra         | [phases-apply.md](architecture/communities/phases-apply.md)                 |
| `flext-core-container` | 203  | flext-core          | [flext-core-container.md](architecture/communities/flext-core-container.md) |
| `services-context`     | 169  | flext-core/cli      | [services-context.md](architecture/communities/services-context.md)         |
| `matchers-validate`    | 155  | flext-quality       | [matchers-validate.md](architecture/communities/matchers-validate.md)       |

See the [full community index](architecture/communities/index.md) for all 50 published
clusters.

### 3. Auto-Generated API Reference

Every FLEXT package renders its API from live code via `mkdocstrings`. The root portal
aggregates; per-package detail lives with each project.

| Layer               | Source                               | Link                                                                         |
| ------------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Root overview       | workspace discovery                  | [api-reference/generated/overview.md](api-reference/generated/overview.md)   |
| Root catalog        | project manifest                     | [projects/generated/catalog.md](projects/generated/catalog.md)               |
| Per-package API     | `src/<pkg>/__init__.py` + docstrings | [api-reference/generated/<pkg>.md](api-reference/generated/overview.md)      |
| Per-package modules | module docstrings                    | [projects/<pkg>/modules/index.md](api-reference/generated/projects/index.md) |

## Package Quick Reference

<!-- AUTO-GENERATED TABLE: commence -->

| Package                 | Class       | Docs Portal                                             | API Reference                                                                               | Top Community            |
| ----------------------- | ----------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------ |
| flext-api               | platform    | `flext-api/docs`                                        | [flext-api](api-reference/generated/flext-api.md)                                           | services-server          |
| flext-auth              | platform    | `flext-auth/docs`                                       | [flext-auth](api-reference/generated/flext-auth.md)                                         | api-cases-auth           |
| flext-cli               | platform    | `flext-cli/docs`                                        | [flext-cli](api-reference/generated/flext-cli.md)                                           | utilities-flext          |
| flext-core              | platform    | `flext-core/docs`                                       | [flext-core](api-reference/generated/flext-core.md)                                         | flext-core-container     |
| flext-db-oracle         | domain      | `flext-db-oracle/docs`                                  | [flext-db-oracle](api-reference/generated/flext-db-oracle.md)                               | services-oracle          |
| flext-dbt-ldap          | integration | `flext-dbt-ldap/docs`                                   | [flext-dbt-ldap](api-reference/generated/flext-dbt-ldap.md)                                 | flext-meltano-pipeline   |
| flext-dbt-ldif          | integration | `flext-dbt-ldif/docs`                                   | [flext-dbt-ldif](api-reference/generated/flext-dbt-ldif.md)                                 | unit-ldif                |
| flext-dbt-oracle        | integration | `flext-dbt-oracle/docs`                                 | [flext-dbt-oracle](api-reference/generated/flext-dbt-oracle.md)                             | services-oracle          |
| flext-dbt-oracle-wms    | integration | `flext-dbt-oracle-wms/docs`                             | [flext-dbt-oracle-wms](api-reference/generated/flext-dbt-oracle-wms.md)                     | services-server-grpc     |
| flext-grpc              | platform    | `flext-grpc/docs`                                       | [flext-grpc](api-reference/generated/flext-grpc.md)                                         | services-server-grpc     |
| flext-infra             | infra       | `flext-infra/docs`                                      | [flext-infra](api-reference/generated/flext-infra.md)                                       | codegen-infra            |
| flext-ldap              | domain      | `flext-ldap/docs`                                       | [flext-ldap](api-reference/generated/flext-ldap.md)                                         | utilities-dn             |
| flext-ldif              | domain      | `flext-ldif/docs`                                       | [flext-ldif](api-reference/generated/flext-ldif.md)                                         | services-ldif            |
| flext-meltano           | platform    | `flext-meltano/docs`                                    | [flext-meltano](api-reference/generated/flext-meltano.md)                                   | flext-meltano-pipeline   |
| flext-observability     | platform    | `flext-observability/docs`                              | [flext-observability](api-reference/generated/flext-observability.md)                       | utilities-output         |
| flext-oracle-oic        | domain      | `flext-oracle-oic/docs`                                 | [flext-oracle-oic](api-reference/generated/flext-oracle-oic.md)                             | services-oracle          |
| flext-oracle-wms        | domain      | `flext-oracle-wms/docs`                                 | [flext-oracle-wms](api-reference/generated/flext-oracle-wms.md)                             | flext-tap-oracle-wms-tap |
| flext-oud-mig           | domain      | `flext-oud-mig/docs`                                    | `flext-oud-mig` (not in API reference)                                                       | oud-acl                  |
| flext-plugin            | platform    | `flext-plugin/docs`                                     | [flext-plugin](api-reference/generated/flext-plugin.md)                                     | utilities-plugin         |
| flext-quality           | platform    | `flext-quality/docs`                                    | [flext-quality](api-reference/generated/flext-quality.md)                                   | matchers-validate        |
| flext-tap-ldap          | integration | `flext-tap-ldap/docs`                                   | [flext-tap-ldap](api-reference/generated/flext-tap-ldap.md)                                 | utilities-dn             |
| flext-tap-ldif          | integration | `flext-tap-ldif/docs`                                   | [flext-tap-ldif](api-reference/generated/flext-tap-ldif.md)                                 | services-ldif            |
| flext-tap-oracle        | integration | `flext-tap-oracle/docs`                                 | [flext-tap-oracle](api-reference/generated/flext-tap-oracle.md)                             | services-oracle          |
| flext-tap-oracle-oic    | integration | `flext-tap-oracle-oic/docs`                             | [flext-tap-oracle-oic](api-reference/generated/flext-tap-oracle-oic.md)                     | services-oracle          |
| flext-tap-oracle-wms    | integration | `flext-tap-oracle-wms/docs`                             | [flext-tap-oracle-wms](api-reference/generated/flext-tap-oracle-wms.md)                     | flext-tap-oracle-wms-tap |
| flext-target-ldap       | integration | `flext-target-ldap/docs`                                | [flext-target-ldap](api-reference/generated/flext-target-ldap.md)                           | utilities-dn             |
| flext-target-ldif       | integration | `flext-target-ldif/docs`                                | [flext-target-ldif](api-reference/generated/flext-target-ldif.md)                           | flext-target-ldif-record |
| flext-target-oracle     | integration | `flext-target-oracle/docs`                              | [flext-target-oracle](api-reference/generated/flext-target-oracle.md)                       | services-oracle          |
| flext-target-oracle-oic | integration | `flext-target-oracle-oic/docs`                          | [flext-target-oracle-oic](api-reference/generated/flext-target-oracle-oic.md)               | services-oracle          |
| flext-target-oracle-wms | integration | `flext-target-oracle-wms/docs`                          | [flext-target-oracle-wms](api-reference/generated/flext-target-oracle-wms.md)               | flext-tap-oracle-wms-tap |
| flext-tests             | test        | `flext-tests/docs`                                      | [flext-tests](api-reference/generated/flext-tests.md)                                       | flext-tests-compose      |
| flext-web               | platform    | `flext-web/docs`                                        | [flext-web](api-reference/generated/flext-web.md)                                           | services-server          |

<!-- AUTO-GENERATED TABLE: end -->

## Cross-Reference Map

The map below links conceptual topics to their implementing code communities and live
API surfaces.

| Concept                                   | ADR                                                                                                      | Community (CRG)          | API Reference                                                   |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------ | --------------------------------------------------------------- |
| Railway-Oriented Programming              | [ADR-001](architecture/adr/001-railway-oriented-programming.md)                                          | `result-parts-error`     | [flext-core](api-reference/generated/flext-core.md)             |
| v0.13.0 Platform Baseline                 | [ADR-002](architecture/adr/002-v0-13-0-platform-baseline.md)                                             | `flext-core-container`   | [flext-core](api-reference/generated/flext-core.md)             |
| Workspace Tooling & Hub Distribution      | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md)                                    | `base-entry`             | [flext-cli](api-reference/generated/flext-cli.md)               |
| Generated Make & Codegen SSOT             | [ADR-004](architecture/adr/004-generated-make-codegen-ssot-flext-infra.md)                               | `phases-apply`           | [flext-infra](api-reference/generated/flext-infra.md)           |
| Config/Settings/Templates/Schemas SSOT    | [ADR-005](architecture/adr/005-config-settings-constants-templates-schemas-ssot.md)                      | `base-parts-settings`    | [flext-core](api-reference/generated/flext-core.md)             |
| Thin Domain Drivers over Meltano          | [ADR-006](architecture/adr/006-thin-domain-drivers-over-meltano-bases.md)                                | `flext-meltano-pipeline` | [flext-meltano](api-reference/generated/flext-meltano.md)       |
| Worktree Transaction Performance          | [ADR-007](architecture/adr/007-worktree-transaction-performance.md)                                      | `base-process`           | [flext-infra](api-reference/generated/flext-infra.md)           |
| Neutral Consumer Boundaries               | [ADR-008](architecture/adr/008-neutral-consumer-boundaries.md)                                           | `services-server-grpc`   | [flext-grpc](api-reference/generated/flext-grpc.md)             |
| Ecosystem Coordination & Evaluation       | [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md)                         | `services-context`       | [flext-core](api-reference/generated/flext-core.md)             |
| Unified Project Standardization           | [ADR-010](architecture/adr/010-unified-project-standardization-via-codegen.md)                           | `codegen-infra`          | [flext-infra](api-reference/generated/flext-infra.md)           |
| Family/Part Shape, Rope & Codemod Rules   | [ADR-014](architecture/adr/014-family-part-shape-rope-codemod-rules.md)                                  | `transformers-import`    | [flext-infra](api-reference/generated/flext-infra.md)           |
| Consumer Consumption Law (R1–R6)          | [ADR-015](architecture/adr/015-consumer-consumption-law.md)                                              | `utilities-flext`        | [flext-core](api-reference/generated/flext-core.md)             |
| Settings/Config Singleton Contract        | [ADR-016](architecture/adr/016-settings-config-singleton-contract.md)                                    | `models-config`          | [flext-core](api-reference/generated/flext-core.md)             |
| Parametrized Rule Surfaces & Modernize    | [ADR-017](architecture/adr/017-parametrized-rule-surfaces-single-modernize-cli.md)                       | `detectors-infra`        | [flext-infra](api-reference/generated/flext-infra.md)           |
| Generator Declarations Law                | [ADR-018](architecture/adr/018-generator-declarations.md)                                                | `codegen-infra-flext`    | [flext-infra](api-reference/generated/flext-infra.md)           |
| Service Contract & Protocol Ports         | [ADR-019](architecture/adr/019-service-contract-ports-operations.md)                                     | `protocols-flext`        | [flext-core](api-reference/generated/flext-core.md)             |
| Mandatory Unsafe-Fix Lint Repair          | [ADR-021](architecture/adr/021-mandatory-unsafe-fix-lint-repair-channel.md)                              | `gates-check`            | [flext-infra](api-reference/generated/flext-infra.md)           |
| Repair Phases as Mod-Loop Callbacks       | [ADR-023](architecture/adr/023-repair-phases-mod-loop-callbacks.md)                                      | `phases-apply`           | [flext-infra](api-reference/generated/flext-infra.md)           |
| DI Config Contract & Derived Defaults     | [ADR-024](architecture/adr/024-di-config-contract-derived-defaults-minimal-overrides.md)                 | `models-config`          | [flext-infra](api-reference/generated/flext-infra.md)           |
| npm-Free Fleet Toolchain                  | [ADR-025](architecture/adr/025-npm-free-fleet-toolchain.md)                                              | `codegen-infra`          | [flext-infra](api-reference/generated/flext-infra.md)           |
| Engine Federation & Unified Loop          | [ADR-026](architecture/adr/026-engine-federation-unified-loop-kernel.md)                                 | `detectors-infra`        | [flext-infra](api-reference/generated/flext-infra.md)           |
| Facade Single-Owner Law                   | [ADR-027](architecture/adr/027-facade-single-owner-law.md)                                               | `utilities-source`       | [flext-infra](api-reference/generated/flext-infra.md)           |
| Facade Boundary & Declarative Enforcement | [ADR-028](architecture/adr/028-facade-boundary-orchestrators-declarative-enforcement.md)                 | `codegen-infra`          | [flext-infra](api-reference/generated/flext-infra.md)           |
| Always Working — One Complete Cycle       | [ADR-029](architecture/adr/029-always-working-one-complete-cycle.md)                                     | `gates-check`            | [flext-infra](api-reference/generated/flext-infra.md)           |
| Member Locks & Upgrade Guard              | [ADR-030](architecture/adr/030-member-locks-composition-upg-guard.md)                                    | `tests-deps`             | [flext-infra](api-reference/generated/flext-infra.md)           |

## Regeneration

The knowledge index is refreshed by the codegen conform transaction. From the workspace
root:

```bash
make gen
```

- **Manual & Curated** sections are authored by hand and synced via PR review.
- **Community Wiki** pages are regenerated by `code-review-graph wiki` and copied into
  `docs/architecture/communities/` during `make gen`.
- **Auto-Generated API Reference** pages are regenerated from live code exports and
  docstrings via `mkdocstrings`.

## See Also

- [Architecture Index](architecture/README.md)
- [Code Communities Index](architecture/communities/index.md)
- [API Reference Index](api-reference/README.md)
- [Projects Index](projects/README.md)
- [Guides Index](guides/README.md)
