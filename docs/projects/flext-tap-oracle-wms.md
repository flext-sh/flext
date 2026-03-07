# FLEXT Tap Oracle WMS

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & integration](#architecture-integration)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Tap Oracle WMS (v1.0.0 release preparation) is the Singer tap that continuously extracts Oracle Warehouse Management System data with enterprise-grade telemetry, instrumentation, and documentation. The project is production-ready, but a major refactor is ongoing to simplify the architecture and unblock disabled tests.

## Status & health

- **Version**: 1.0.0 release preparation
- **Python**: 3.13+
- **Status**: Production-ready core features (10 working streams) while refactoring (26 files → 6‑8 target) and reopening disabled tests (27% of tests currently disabled)
- **Coverage goal**: 90%+ target; reporting shows coverage is limited while refactor completes
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring + Singer checks) is required before merges; `make lint`, `make type-check`, `make security`, `make test`, and Singer discovery/run commands currently run as part of `make check`
- **Zero tolerance**: No direct Singer SDK, Oracle WMS SDK, or SQLAlchemy imports; rely on flext-core/flext-oracle-wms/flext-db-oracle; everything returns `FlextResult[T]`

## Quick start

```bash
git clone https://github.com/flext-sh/flext-tap-oracle-wms.git
cd flext-tap-oracle-wms
poetry install
make setup
make check     # lint + type-check + tests
make validate  # full validation (currently monitors refactor progress)
```

```bash
tap-oracle-wms --config config.json --discover > catalog.json
tap-oracle-wms --config config.json --catalog catalog.json --state state.json
```

## Architecture & integration

- **Clean architecture**: 6‑8 simplified modules (target) replacing 26 current files; modules include API, CLI, services, connectors, models, and utilities.
- **Singer compliance**: Singer-spec discovery, state, catalog, and run helpers integrate with `flext-meltano` and Singer pipelines.
- **Oracle WMS focus**: 10 streams covering inventory, orders, shipments, tasks, and locations plus Singer instrumentation, retry/backoff, and dynamic pagination.
- **Integration**: depends on `flext-oracle-wms` for WMS API, `flext-db-oracle` for Oracle connections, `flext-core` for FlextResult/DI patterns, and `flext-observability` for telemetry.

## Quality & operations

- **Validation commands**: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate`, `make discover`, `make run`, `make wms-test`, `make validate-config`.
- **Testing**: 37 MyPy errors noted (regression), 27% of tests disabled, 8,179 lines marked for simplification; tests include Singer, integration, and WMS connectivity scenarios.
- **Security**: Bandit + pip-audit run via `make security`; zero tolerance for insecure default credentials.
- **Documentation**: TODO, architecture, and standards docs describe the refactor plan, quality principles, and simplification roadmap.

## Resources & references

- [Project README](../../flext-tap-oracle-wms/docs/README.md)
- [Project AGENTS.md](../../flext-tap-oracle-wms/AGENTS.md) for zero tolerance policies and commands
- `docs/` (architecture, TODO/refactor plan, standards, quality checklists)
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`
- Related projects: `flext-oracle-wms`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, `flext-tap-oracle`, `flext-target-oracle-wms`, `flext-dbt-oracle-wms`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle-wms/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle-wms/discussions>
- Follow `docs/standards/README.md`, this project’s `AGENTS.md`, and the portal checklist before editing docs or code so the portal stays synchronized.
