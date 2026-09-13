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

> **AUTO-GENERATED — DO NOT EDIT MANUALLY.**
> Sources: `docs/` tree (manual-curated), CRG graph (code knowledge graph),
> and `mkdocstrings` directives (live from code).
> Regenerate with: `make gen`

## Purpose

This index is the single entry point for finding documentation across the three
documentation layers of the FLEXT workspace:

1. **Manual & Curated** — human-authored guides, ADRs, arc42 architecture, and standards.
2. **Community Wiki (CRG)** — code knowledge graph communities discovered by
   `code-review-graph`, linking responsibility clusters to concrete source symbols.
3. **Auto-Generated API Reference** — `mkdocstrings`-driven pages generated from
   `pyproject.toml`, public exports, and docstrings.

Each section below cross-references the other layers so readers can navigate from
a conceptual topic (ADR) → the code community that implements it (CRG wiki) →
the live API surface for that package (mkdocstrings).

## Documentation Layers

### 1. Manual & Curated

Curated documents that own architectural decisions, workflow guidance, and
authoring standards. These are hand-written and reviewed.

| Topic | Document | What It Covers |
| --- | --- | --- |
| Architecture Index | [architecture/README.md](architecture/README.md) | Canonical architecture baseline + ADR index |
| arc42 | [architecture/arc42/README.md](architecture/arc42/README.md) | 12-chapter architecture template |
| ADRs | [architecture/adr/README.md](architecture/adr/README.md) | 10 formal decision records |
| Code Communities | [architecture/communities/index.md](architecture/communities/index.md) | CRG community wiki index |
| Guides Index | [guides/README.md](guides/README.md) | Workflow, migration, day-to-day guides |
| Standards | [standards/README.md](standards/README.md) | Cross-workspace authoring standards |
| Governance | [GOVERNANCE.md](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md) | Active rule routing and validation surfaces |
| Version Policy | [version-policy.md](version-policy.md) | Versioning and release policy |

### 2. Community Wiki (CRG)

The CRG knowledge graph (SQLite at `.code-review-graph/graph.db`) indexes every
file, class, function, and test across all submodules. The `wiki` subcommand
runs Leiden community detection on the call/import graph and emits one page per
community. Only communities with >= 50 nodes are published here; smaller
clusters exist in the full CRG wiki.

| Community | Size | Primary Package | Link |
| --- | --- | --- | --- |
| `codegen-infra` | 688 | flext-infra | [codegen-infra.md](architecture/communities/codegen-infra.md) |
| `utilities-flext` | 590 | flext-core/cli | [utilities-flext.md](architecture/communities/utilities-flext.md) |
| `codegen-infra-flext` | 345 | flext-infra | [codegen-infra-flext.md](architecture/communities/codegen-infra-flext.md) |
| `services-server` | 317 | flext-api/web | [services-server.md](architecture/communities/services-server.md) |
| `detectors-infra` | 302 | flext-infra | [detectors-infra.md](architecture/communities/detectors-infra.md) |
| `gates-check` | 290 | flext-infra/quality | [gates-check.md](architecture/communities/gates-check.md) |
| `phases-apply` | 240 | flext-infra | [phases-apply.md](architecture/communities/phases-apply.md) |
| `flext-core-container` | 203 | flext-core | [flext-core-container.md](architecture/communities/flext-core-container.md) |
| `services-context` | 169 | flext-core/cli | [services-context.md](architecture/communities/services-context.md) |
| `matchers-validate` | 155 | flext-quality | [matchers-validate.md](architecture/communities/matchers-validate.md) |

See the [full community index](architecture/communities/index.md) for all 50
published clusters.

### 3. Auto-Generated API Reference

Every FLEXT package renders its API from live code via
`mkdocstrings`. The root portal aggregates; per-package detail lives with each
project.

| Layer | Source | Link |
| --- | --- | --- |
| Root overview | workspace discovery | [api-reference/generated/overview.md](api-reference/generated/overview.md) |
| Root catalog | project manifest | [projects/generated/catalog.md](projects/generated/catalog.md) |
| Per-package API | `src/<pkg>/__init__.py` + docstrings | [api-reference/generated/<pkg>.md](api-reference/generated/overview.md) |
| Per-package modules | module docstrings | [projects/<pkg>/modules/index.md](api-reference/generated/projects/index.md) |

## Package Quick Reference

<!-- AUTO-GENERATED TABLE: commence -->
| Package | Class | Docs Portal | API Reference | Top Community |
| --- | --- | --- | --- | --- |
| flext-api | platform | [flext-api/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-api/docs) | [generated/flext-api.md](api-reference/generated/flext-api.md) | services-server |
| flext-auth | platform | [flext-auth/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-auth/docs) | [generated/flext-auth.md](api-reference/generated/flext-auth.md) | api-cases-auth |
| flext-cli | platform | [flext-cli/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-cli/docs) | [generated/flext-cli.md](api-reference/generated/flext-cli.md) | utilities-flext |
| flext-core | platform | [flext-core/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-core/docs) | [generated/flext-core.md](api-reference/generated/flext-core.md) | flext-core-container |
| flext-db-oracle | domain | [flext-db-oracle/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-db-oracle/docs) | [generated/flext-db-oracle.md](api-reference/generated/flext-db-oracle.md) | services-oracle |
| flext-dbt-ldap | integration | [flext-dbt-ldap/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-dbt-ldap/docs) | [generated/flext-dbt-ldap.md](api-reference/generated/flext-dbt-ldap.md) | flext-meltano-pipeline |
| flext-dbt-ldif | integration | [flext-dbt-ldif/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-dbt-ldif/docs) | [generated/flext-dbt-ldif.md](api-reference/generated/flext-dbt-ldif.md) | unit-ldif |
| flext-dbt-oracle | integration | [flext-dbt-oracle/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-dbt-oracle/docs) | [generated/flext-dbt-oracle.md](api-reference/generated/flext-dbt-oracle.md) | services-oracle |
| flext-dbt-oracle-wms | integration | [flext-dbt-oracle-wms/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-dbt-oracle-wms/docs) | [generated/flext-dbt-oracle-wms.md](api-reference/generated/flext-dbt-oracle-wms.md) | services-server-grpc |
| flext-grpc | platform | [flext-grpc/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-grpc/docs) | [generated/flext-grpc.md](api-reference/generated/flext-grpc.md) | services-server-grpc |
| flext-infra | infra | [flext-infra/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-infra/docs) | [generated/flext-infra.md](api-reference/generated/flext-infra.md) | codegen-infra |
| flext-ldap | domain | [flext-ldap/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-ldap/docs) | [generated/flext-ldap.md](api-reference/generated/flext-ldap.md) | utilities-dn |
| flext-ldif | domain | [flext-ldif/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-ldif/docs) | [generated/flext-ldif.md](api-reference/generated/flext-ldif.md) | services-ldif |
| flext-meltano | platform | [flext-meltano/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-meltano/docs) | [generated/flext-meltano.md](api-reference/generated/flext-meltano.md) | flext-meltano-pipeline |
| flext-observability | platform | [flext-observability/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-observability/docs) | [generated/flext-observability.md](api-reference/generated/flext-observability.md) | utilities-output |
| flext-oracle-oic | domain | [flext-oracle-oic/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-oracle-oic/docs) | [generated/flext-oracle-oic.md](api-reference/generated/flext-oracle-oic.md) | services-oracle |
| flext-oracle-wms | domain | [flext-oracle-wms/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-oracle-wms/docs) | [generated/flext-oracle-wms.md](api-reference/generated/flext-oracle-wms.md) | flext-tap-oracle-wms-tap |
| flext-plugin | platform | [flext-plugin/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-plugin/docs) | [generated/flext-plugin.md](api-reference/generated/flext-plugin.md) | utilities-plugin |
| flext-quality | platform | [flext-quality/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-quality/docs) | [generated/flext-quality.md](api-reference/generated/flext-quality.md) | matchers-validate |
| flext-tap-ldap | integration | [flext-tap-ldap/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-ldap/docs) | [generated/flext-tap-ldap.md](api-reference/generated/flext-tap-ldap.md) | utilities-dn |
| flext-tap-ldif | integration | [flext-tap-ldif/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-ldif/docs) | [generated/flext-tap-ldif.md](api-reference/generated/flext-tap-ldif.md) | services-ldif |
| flext-tap-oracle | integration | [flext-tap-oracle/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-oracle/docs) | [generated/flext-tap-oracle.md](api-reference/generated/flext-tap-oracle.md) | services-oracle |
| flext-tap-oracle-oic | integration | [flext-tap-oracle-oic/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-oracle-oic/docs) | [generated/flext-tap-oracle-oic.md](api-reference/generated/flext-tap-oracle-oic.md) | services-oracle |
| flext-tap-oracle-wms | integration | [flext-tap-oracle-wms/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tap-oracle-wms/docs) | [generated/flext-tap-oracle-wms.md](api-reference/generated/flext-tap-oracle-wms.md) | flext-tap-oracle-wms-tap |
| flext-target-ldap | integration | [flext-target-ldap/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-target-ldap/docs) | [generated/flext-target-ldap.md](api-reference/generated/flext-target-ldap.md) | utilities-dn |
| flext-target-ldif | integration | [flext-target-ldif/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-target-ldif/docs) | [generated/flext-target-ldif.md](api-reference/generated/flext-target-ldif.md) | flext-target-ldif-record |
| flext-target-oracle | integration | [flext-target-oracle/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-target-oracle/docs) | [generated/flext-target-oracle.md](api-reference/generated/flext-target-oracle.md) | services-oracle |
| flext-target-oracle-oic | integration | [flext-target-oracle-oic/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-target-oracle-oic/docs) | [generated/flext-target-oracle-oic.md](api-reference/generated/flext-target-oracle-oic.md) | services-oracle |
| flext-target-oracle-wms | integration | [flext-target-oracle-wms/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-target-oracle-wms/docs) | [generated/flext-target-oracle-wms.md](api-reference/generated/flext-target-oracle-wms.md) | flext-tap-oracle-wms-tap |
| flext-tests | test | [flext-tests/README](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-tests) | [generated/flext-tests.md](api-reference/generated/flext-tests.md) | flext-tests-compose |
| flext-web | platform | [flext-web/docs](https://github.com/flext-sh/flext/tree/0.12.0-dev/flext-web/docs) | [generated/flext-web.md](api-reference/generated/flext-web.md) | services-server |
<!-- AUTO-GENERATED TABLE: end -->

## Cross-Reference Map

The map below links conceptual topics to their implementing code communities and
live API surfaces.

| Concept | ADR | Community (CRG) | API Reference |
| --- | --- | --- | --- |
| Railway-Oriented Programming | [ADR-001](architecture/adr/001-railway-oriented-programming.md) | `result-parts-error` | [`flext-core`](api-reference/generated/flext-core.md) |
| Config/Settings SSOT | [ADR-005](architecture/adr/005-config-settings-constants-templates-schemas-ssot.md) | `base-parts-settings` | [`flext-core`](api-reference/generated/flext-core.md) |
| Thin Domain Drivers | [ADR-006](architecture/adr/006-thin-domain-drivers-over-meltano-bases.md) | `flext-meltano-pipeline` | [`flext-meltano`](api-reference/generated/flext-meltano.md) |
| Generic Make Framework | [ADR-004](architecture/adr/004-generic-make-framework-in-flext-tests.md) | `phases-apply` | [`flext-tests`](api-reference/generated/flext-tests.md) |
| Unified Codegen | [ADR-010](architecture/adr/010-unified-project-standardization-via-codegen.md) | `codegen-infra` | [`flext-infra`](api-reference/generated/flext-infra.md) |
| Workspace Tooling | [ADR-003](architecture/adr/003-workspace-tooling-hub-distribution.md) | `base-entry` | [`flext-cli`](api-reference/generated/flext-cli.md) |
| Consumer Boundaries | [ADR-008](architecture/adr/008-neutral-consumer-boundaries.md) | `services-server-grpc` | [`flext-grpc`](api-reference/generated/flext-grpc.md) |
| Ecosystem Coordination | [ADR-009](architecture/adr/009-ecosystem-coordination-and-library-evaluation.md) | `services-context` | [`flext-core`](api-reference/generated/flext-core.md) |
| Worktree Perf | [ADR-007](architecture/adr/007-worktree-transaction-performance.md) | `base-process` | [`flext-infra`](api-reference/generated/flext-infra.md) |
| v0.13.0 Baseline | [ADR-002](architecture/adr/002-v0-13-0-platform-baseline.md) | `flext-core-container` | [`flext-core`](api-reference/generated/flext-core.md) |

## Regeneration

The knowledge index is refreshed by the codegen conform transaction. From the
workspace root:

```bash
make gen
```

- **Manual & Curated** sections are authored by hand and synced via PR review.
- **Community Wiki** pages are regenerated by `code-review-graph wiki` and copied
  into `docs/architecture/communities/` during `make gen`.
- **Auto-Generated API Reference** pages are regenerated from live code exports
  and docstrings via `mkdocstrings`.

## See Also

- [Architecture Index](architecture/README.md)
- [Code Communities Index](architecture/communities/index.md)
- [API Reference Index](api-reference/README.md)
- [Projects Index](projects/README.md)
- [Guides Index](guides/README.md)
