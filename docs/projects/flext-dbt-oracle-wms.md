# FLEXT dbt Oracle WMS

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & integration](#architecture-integration)
- [Features & quality](#features-quality)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT dbt Oracle WMS (v2.1.0) is the enterprise dbt project for Oracle Warehouse Management System data transformations. It blends flext-db-oracle and flext-oracle-wms connectivity with flext-meltano orchestration so every analyst can deliver WMS dashboards with Singer, dbt, and Clean Architecture patterns.

## Status & health

- **Version**: 2.1.0 (Production-ready)
- **Python**: 3.13+
- **Tests**: ~339+ unit/integration/e2e methods; `make validate` (ruff + pyrefly + bandit + pytest + dbt tests + coverage) is the QA gate before merging.
- **Coverage**: 90%+ per README + coverage reports (`reports/coverage-scan-*`).
- **Dependencies**: `flext-core`, `flext-db-oracle`, `flext-oracle-wms`, `flext-meltano`, `flext-cli`, `flext-observability`, `dbt-core`, `dbt-oracle`, `Singer SDK`.
- **Zero tolerance**: no direct dbt/oracle/Singer imports; always route through flext-\* adapters, return `FlextResult[T]`, avoid `Any`/`cast`/`TYPE_CHECKING`, and keep CLI logic in flext-cli.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-dbt-oracle-wms.git
cd flext-dbt-oracle-wms
poetry install
make setup
make validate
```

```bash
dbt deps
dbt debug --target dev
dbt run --target dev
dbt test --target dev
dbt docs generate --target dev
dbt docs serve --port 8080
```

## Architecture & integration

- **Layered data flow**: Oracle WMS → Singer tap (flext-tap-oracle-wms) → raw tables → dbt staging/intermediate/marts → analytics dashboards.
- **Clean architecture enforcement**: foundation modules (`constants.py`, `typings.py`, `protocols.py`) feed into domain, service, and adapter layers; each layer only imports lower tiers per CLAUDE guidance.
- **Model organization**: staging models handle cleansing (`stg_wms__*`), marts produce operational, analytical, and metrics tables (`marts/operational`, `marts/analytical`, `marts/metrics`), and `analyses/` houses ad-hoc queries.
- **Integration contracts**: depends on `flext-oracle-wms` for WMS definitions, `flext-db-oracle` for loader/pooling, `flext-meltano` for dbt orchestration, and `flext-core` for DI/logging.

## Features & quality

- **Oracle WMS analytics**: allocation, inventory, order, location, task, and wave models plus KPI dashboards.
- **Macros**: helper macros for allocation efficiency, inventory turnover, ABC classification, SLA compliance, and labor productivity.
- **Testing & quality**: schema tests, data tests, Python component tests, and coverage checks run via `make validate`; 90%+ coverage enforced.
- **Performance**: incremental models, partitioning, clustering, and query optimization tuned for enterprise WMS datasets.
- **Instrumentation**: integrates with `flext-observability` and `flext-cli` for telemetry and consistent CLI behavior.

## Resources & references

- [Project README](../../flext-dbt-oracle-wms/README.md)
- [Project CLAUDE](../../flext-dbt-oracle-wms/CLAUDE.md) for zero-tolerance rules and command checklists
- `docs/` subfolders for getting started, architecture, models, integration, development, and troubleshooting
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for the QA claims
- Related projects: `flext-core`, `flext-db-oracle`, `flext-oracle-wms`, `flext-meltano`, `flext-tap-oracle-wms`, `flext-target-oracle-wms`, `flext-observability`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-dbt-oracle-wms/issues>
- Discussions: <https://github.com/flext-sh/flext-dbt-oracle-wms/discussions>
- Follow `docs/standards/README.md`, this project’s CLAUDE, and the portal checklist before editing docs or code to keep the ecosystem synchronized.
