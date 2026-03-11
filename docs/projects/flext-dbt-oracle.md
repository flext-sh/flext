# FLEXT dbt Oracle

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & integration](#architecture-integration)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT dbt Oracle (v1.0.0 release prep) is the dbt integration for Oracle Database inside the FLEXT ecosystem. It pairs flext-db-oracle connectivity, flext-meltano orchestration, and Singer compliance to deliver Oracle analytics while enforcing zero-tolerance dependency rules.

## Status & health

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+ with Poetry-managed dependencies
- **Tests**: ~250 unit/integration/Oracle-focused suites; `make validate` (ruff + pyrefly + bandit + pytest + dbt tests + coverage) is the gating command that must pass before merging.
- **Coverage**: 90%+ (see `reports/coverage-scan-*` snapshots)
- **Quality gate**: `make validate` (lint + type + security + tests + docstring + dbt validations) - other commands (`make lint`, `make type-check`, `make security`, `make test`) already run successfully.
- **Dependencies**: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flr` (Singer), Oracle Instant Client, `dbt-core`, `dbt-oracle`
- **Zero tolerance**: no direct dbt/Singer imports (use flext-meltano), no direct SQLAlchemy/oracledb usage (use flext-db-oracle), no direct Click/Rich (use flext-cli), and every API returns `r[T]` without `Any` or `cast`.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-dbt-oracle.git
cd flext-dbt-oracle
poetry install
make setup
make validate
```

```bash
dbt deps
dbt debug --profiles-dir profiles/ --target dev
dbt run --target dev
dbt test --target dev
dbt docs generate --target dev
```

## Architecture & integration

- **Layers**: Clean Architecture (foundation constants/typings, domain models, services/orchestrators, adapters); layering enforces one-way imports per `AGENTS.md`.
- **Adapter stack**: `flext_dbt_oracle.adapters.oracle` implements the Oracle adapter plus connection manager, loader, and SQL optimizer; `FlextDbtOracle` façade orchestrates runs with the FlextContainer + r pipeline.
- **Integration points**: relies on `flext-db-oracle` for connections, `flext-meltano` for Singer orchestration, `flext-core` for logging/dependency injection, and `flext-observability` for instrumentation.
- **Security and compliance**: connection pooling, transaction management, dual-phase commit plan, and explicit guardrails for SQL hints, timeouts, and error mapping.

## Quality & operations

- Validation commands: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make dbt-test`, and `make validate`.
- Testing focus: Python unit tests, Oracle integration tests (connection, loader, macros), dbt model/tests, and `dbt run` with Oracle-specific macros.
- Security gating: Bandit and pip-audit run through `make security`; the README lists SQL compliance and connection timeouts as follow-ups when additional features ship.

## Resources & references

- [Project README](../../flext-dbt-oracle/README.md)
- [Project AGENTS.md](../../flext-dbt-oracle/AGENTS.md) for dependency and command rules
- `docs/` (architecture, configuration, API reference, debugging guides)
- Related artifacts: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` once blocked gates finish
- Related projects: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, `flext-tap-oracle`, `flext-target-oracle`, `flext-dbt-oracle-wms`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-dbt-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-dbt-oracle/discussions>
- Follow `docs/standards/README.md` and this project’s `AGENTS.md` before making doc or code changes so the portal stays accurate.
