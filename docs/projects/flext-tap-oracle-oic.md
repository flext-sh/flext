# FLEXT Tap Oracle OIC

FLEXT Tap Oracle OIC (v1.0.0 release prep) is the Singer tap that extracts metadata, configurations, and streams from Oracle Integration Cloud (OIC). It pairs the flext-core patterns with flext-oracle-oic and flext-meltano to deliver OAuth2/IDCS authentication, retrying stream discovery, and error recovery inside a clean architecture shell.

## Status & signals

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+
- **Status**: production-ready but documentation still being finalized; quality gates succeed while README notes remaining docs work.
- **Coverage**: 90%+ (see `reports/coverage-scan-*`)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring + Singer tests) is enforced before merges; `make lint`, `make type-check`, `make security`, `make test`, and Singer helper commands operate cleanly.
- **Dependencies**: `flext-core`, `flext-oracle-oic`, `flext-meltano`, `flext-observability`, Singer SDK, Oracle OIC OAuth2 endpoints
- **Zero tolerance**: no direct Singer SDK, httpx, or Oracle OIC imports; rely on flext-oracle-oic for connectors, flext-meltano for orchestration, and `FlextResult[T]` for flow control.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-tap-oracle-oic.git
cd flext-tap-oracle-oic
poetry install
make setup
make check
make validate
```

```bash
tap-oracle-oic --config config.json --discover > catalog.json
tap-oracle-oic --config config.json --catalog catalog.json --state state.json
```

## Architecture & patterns

- **Clean layers**: Tier 0 (`constants`, `typings`, `protocols`), Tier 1 (`models`, `utilities`), Tier 2 (`client`, `auth`, `streams`), Tier 3 (`api`, `tap`, CLI). Each tier only imports lower-level functionality.
- **Auth & streaming**: `OicAuth` handles OAuth2/IDCS flows, `OicBaseStream` powers OIC entity streams, `TapOracleOic` implements the Singer tap entry point, and `settings.py` centralizes config.
- **Integration**: uses `flext-oracle-oic` for API calls, `flext-core` for FlextResult DI, and `flext-meltano` to integrate with Singer orchestration; instrumentation reuses `flext-observability` helpers.
- **Stream coverage**: 12+ entity types (integrations, connections, packages, etc.) with built-in pagination, retry, rate-limit awareness, and backoff.

## Quality & operations

- Validation commands: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate`, plus Singer-specific commands (`make discover`, `make run`, `make sync`).
- Testing: unit/integration/Singer tests (authentication, streams, errors) run via `pytest -m singer`, `make test-singer`, and the `tap-oracle-oic` CLI.
- Security: Bandit and pip-audit enforced in `make security`; zero tolerance for unverified HTTP calls or exception-based flows.
- Observability: integrated with `flext-observability` for instrumentation, traces, and metrics.

## Resources & references

- [Project README](../../flext-tap-oracle-oic/README.md)
- [Project CLAUDE](../../flext-tap-oracle-oic/CLAUDE.md) for zero-tolerance policies and commands
- `docs/` (getting started, architecture, configuration, testing, troubleshooting)
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`
- Related projects: `flext-oracle-oic`, `flext-meltano`, `flext-dbt-oracle-wms`, `flext-target-oracle-oic`, `flext-observability`

## Support & contributions
- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle-oic/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle-oic/discussions>
- Follow `docs/standards/README.md` and the project CLAUDE before editing docs or code so the portal stays accurate.
