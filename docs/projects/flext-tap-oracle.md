# FLEXT Tap Oracle

<!-- TOC START -->

- [Status & signals](#status-signals)
- [Quick start](#quick-start)
- [Architecture overview](#architecture-overview)
- [Features & quality](#features-quality)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Tap Oracle (v1.0.0 release prep) is the Singer tap for Oracle Database extraction within the FLEXT data mesh. It pairs flext-db-oracle connectivity with flext-meltano orchestration, implements the Singer SDK, and enforces Clean Architecture plus zero-tolerance policies.

## Status & signals

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+
- **Status**: production-ready with 90%+ coverage and gating `make validate` pipeline; documentation still expanding.
- **Coverage**: 90%+ (see `reports/coverage-scan-*`, README badges)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + dbt/test + docstring checks) is required before merging; `make lint`, `make type-check`, `make security`, and `make test` all run clean individually.
- **Dependencies**: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, Singer SDK, `dbt-core`, `dbt-oracle`
- **Zero tolerance**: no direct Singer SDK, SQLAlchemy, or native Oracle imports; every public API returns `FlextResult[T]`, no `Any`, no `cast`, no `TYPE_CHECKING`.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-tap-oracle.git
cd flext-tap-oracle
poetry install
make setup
make check
make validate
```

```bash
tap-oracle --config config.json --discover > catalog.json
tap-oracle --config config.json --catalog catalog.json --state state.json
flext-tap-oracle --config config.json --catalog catalog.json --state state.json
```

## Architecture overview

- **Layered stack**: foundation modules (`constants`, `typings`, `protocols`), domain models/utilities, infrastructure services (`oracle_stream`, `tap`, `config`), and application/CLI entry points.
- **Core components**: `FlextTapOracle`, `OracleStream`, `TapOracleConfig`, `tap.py`, `cli.py`, `integration/` modules for telemetry.
- **Integration**: uses `flext-db-oracle` for Oracle connectivity, `flext-meltano` for Singer tap scaffolding, `flext-core` for FlextResult/DI, and `flext-observability` for instrumentation.
- **Performance**: Oracle-specific query hints, pagination, connection pooling, and streaming results minimize memory usage.

## Features & quality

- **Oracle extraction**: Supports Oracle 11g→23c, incremental replication, schema discovery, and type-safe mapping (VARCHAR2, NUMBER, TIMESTAMP, LOBs).
- **Singer compliance**: Catalog discovery, state management, and sync operations follow the Singer spec through `flext-meltano` adapters.
- **Testing**: Unit, integration, Singer, and Oracle-specific test suites run via `make test`, `pytest -m oracle`, and `make validate`.
- **Security**: Bandit + pip-audit run through `make security`; CLI operations run under flext-cli conventions.

## Resources & references

- [Project README](../../flext-tap-oracle/README.md)
- [Project AGENTS.md](../../flext-tap-oracle/AGENTS.md) for zero-tolerance policies and command guidance
- `docs/` folder (getting started, architecture, configuration, testing, troubleshooting)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for validation evidence
- Related projects: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, `flext-target-oracle`, `flext-dbt-oracle`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle/discussions>
- Follow `docs/standards/README.md` and the project AGENTS.md before editing docs or code so the portal remains aligned.
