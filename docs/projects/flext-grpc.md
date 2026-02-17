# FLEXT gRPC

FLEXT gRPC (v0.9.0) is the gRPC communication foundation for the FLEXT platform. It abstracts grpcio/protobuf concerns, delivers FlextResult-based services, and enforces Clean Architecture across server/client lifecycles while the team ramps coverage toward 90%.

## Status & metrics

- **Version**: 0.9.0 (Development; core functionality operational)
- **Python**: 3.13+
- **Tests**: 18 018 lines in multiple suites; the README reports 28 failing tests that block full validation.
- **Coverage**: 39% actual (target 90%); coverage gates flagged in `pyproject.toml` and README.
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) remains blocked until coverage/test issues are resolved; `make lint`, `make type-check`, `make security`, `make test`, `poetry run pytest` commands currently pass individually.
- **Type discipline**: MyPy strict, zero `Any`/`cast`/`TYPE_CHECKING`; every public API returns `FlextResult[T]` with consistent error handling.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-grpc.git
cd flext-grpc
poetry install
make setup
make check       # lint + type
make validate    # runs lint, type, security, tests, coverage (currently blocked)
```

```bash
poetry run pytest tests/unit/test_config.py::TestFlextGrpcSettings::test_create_valid_config_with_defaults -v
poetry run pytest tests/unit/test_config.py --cov=src/flext_grpc --cov-report=term
poetry run mypy src/
poetry run ruff check src/
```

## Architecture & integration

- **Core layers**: Tier-0 (`constants.py`, `typings.py`, `protocols.py`), Tier-1 (`models`, `utilities`), Tier-2 (`services`, `platform`, `settings`), Tier-3 (`api.py`, `service_impls`, `streaming`). Each tier only imports lower layers.
- **Responsibilities**: gRPC abstraction (unary/bidirectional streams), service management (FlextGrpcService, FlextGrpcPlatform), client/server lifecycle, configuration (FlextGrpcSettings), instrumentation (FlextLogger, FlextObservability).
- **Integration**: Depends on `flext-core` for FlextResult/FlextContainer/FlextLogger, plugs into `flext-cli` for CLI flows, aligned with `flext-observability` for telemetry, and provides gRPC wiring for other FLEXT services.
- **Code status**: 4,923 source lines + 18 018 test lines; core imports (protobuf) verified after the latest fixes.

## Quality & operations

- **Validation commands**: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate` (currently blocked by coverage/test gaps).
- **Testing**: 28 failing tests noted in README, 39% coverage; scope includes single-file config tests, service/test_config, integration stubs.
- **Security**: Bandit + pip-audit invoked through `make security`; zero tolerance for SQL injection or dynamic code.
- **Next steps**: raise coverage from 39% → 90%, fix failing tests, verify protobuf integrations, and mature TLS/auth features.

## Resources & references

- [Project README](../../flext-grpc/README.md)
- [Project CLAUDE](../../flext-grpc/CLAUDE.md) for zero tolerance (FlextResult-only, 75%+ coverage, no `Any`)
- `docs/` (getting started, architecture, API reference, configuration, integration guides)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for QA evidence
- Related projects: `flext-core`, `flext-cli`, `flext-observability`, `flext-api`, `flext-grpc` clients/servers across FLEXT services

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-grpc/issues>
- Discussions: <https://github.com/flext-sh/flext-grpc/discussions>
- Follow `docs/standards/README.md` and the project CLAUDE before touching code or docs so the portal remains consistent.
