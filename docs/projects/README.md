# FLEXT Projects Documentation

This directory keeps one-page summaries that mirror the authoritative README/CLAUDE guidance inside each project. Think of each brief as the "project status" card that points readers back to the real implementation, the quality gate reports, and the release information stored in `reports/`.

## Active project briefs

 - **[FLEXT API](./flext-api/README.md)** – version 0.9.9, fully covered HTTP client + FastAPI integration, production-ready FastAPI app factory, and modern protocol support. Quick start: clone the repo, run `poetry install`, and import `FlextApiClient`/`FlextApi`. Quality gate: `pytest` + `make validate`; documentation surfaces live inside `docs/` and the `README`/`CLAUDE` files in `flext-api/`.
 - **[FLEXT Auth](./flext-auth.md)** – version 2.0.0 with the registry-based authentication foundation, multi-provider architecture, and the FlextAuth facade that integrates JWT, OAuth2, OIDC, and future transports. Quick start: `poetry install` inside `flext-auth` and use `FlextAuth.quick_start()` or `FlextAuth.with_provider`/`with_registry`. Quality gate: `make validate` (ruff + pyrefly + bandit + pytest + coverage); docs live inside the project README/CLAUDE and `docs/` tree.
 - **[FLEXT CLI](./flext-cli.md)** – version 0.10.0, 1 016 tests (100% passing), 96%+ coverage per the coverage scan, and the zero-tolerance CLI foundation that abstracts Click, Rich, and Tabulate for 32+ projects. Quick start: `poetry add flext-cli`/`pip install flext-cli`, import `FlextCli`, and use the direct-access helpers (`formatters`, `file_tools`, `prompts`, `output`). Quality gate: `make validate` with Ruff, Pyrefly, Bandit, and pytest; document links live under the project’s `README`, `CLAUDE`, and `docs/` tree.
 - **[FLEXT Core](./flext-core.md)** – version 0.10.0, Python 3.13+, 2 820 tests, 81.41% coverage, production-ready foundation for FlextResult, DI, and CQRS dispatchers. Quick start: `pip install flext-core`, import `FlextContainer`, `FlextDispatcher`, `FlextResult`. Quality gate: `make validate`. Link to `README.md`, `CLAUDE.md`, and core documentation under `docs/`.
- **[FLEXT DB Oracle](./flext-db-oracle.md)** – version 0.9.9, Oracle connectivity + schema introspection built on SQLAlchemy 2 + python-oracledb, 30 integration test suites (8,633+ lines), and a production-ready FlextDbOracleApi facade. Quick start: clone `flext-db-oracle`, run `poetry install`, and use `FlextDbOracleApi` with `FlextDbOracleModels.OracleConfig`. Quality gate: `make validate` (ruff + pyrefly + bandit + pytest + coverage); zero tolerance pattern rules live in the project README/CLAUDE docs.
- **[FLEXT DBT LDAP](./flext-dbt-ldap.md)** – version 1.0.0 release prep, dbt Core transformation suite for LDAP/AD with staging → intermediate → marts layering, zero-tolerance macros, and 90%+ coverage. Quick start: run `poetry install`, configure `profiles.yml`, then `dbt run`/`dbt test` with `make validate`. Documentation lives inside `flext-dbt-ldap/docs/` and the README/CLAUDE files referenced below.
- **[FLEXT LDIF](./flext-ldif.md)** – version 1.0.0, 1 766 tests, 78% coverage, RFC 2849/4512-compliant parser, quirk registry, and migration pipelines for LDAP directories. Quick start: `pip install flext-ldif`, use `FlextLdif.parse`/`migrate`. Quality gate: `make validate`. This brief also references the `README`, `CLAUDE`, and the `docs/` folder inside the project.

## Projects without a dedicated brief

- Every other repository (e.g., flext-ldap, flext-grpc, flext-auth, flext-observability, flext-plugin, flext-meltano, Singer taps/targets, etc.) publishes its documentation inside the project root (`README.md`, `CLAUDE.md`, `docs/`). Until a `docs/projects/<project>.md` file is added here, treat those files as the source of truth for architecture, quick starts, quality gates, and release status.

## Keeping the briefs accurate

1. **Mirror the repository's narrative** – copy the official version, status, test counts, coverage, and quality gate (Ruff, Pyrefly, pytest, Bandit, etc.) from the project README/CLAUDE so the brief never claims a phantom artifact.
2. **Link to real artifacts** – point readers at actual files under `reports/` and the project's own `docs/` folders. Do not reference workflows or controls that live outside the Git tree.
3. **Validate links and anchors** – rerun Markdown linting (`ruff`, `marksman`) and `lsp_diagnostics` after each change so the portal's table of contents continues to resolve correctly. The `docs/index.md` and `docs/reports/README.md` entries explain how we keep the global portal aligned.

## Related resources

- [Documentation Portal](../index.md)
- [Architecture Reference](../architecture/README.md)
- [Standards](../standards/README.md)
- [Reports archive](../reports/README.md)
