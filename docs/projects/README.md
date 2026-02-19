# FLEXT Projects Documentation


<!-- TOC START -->
- [Active project briefs](#active-project-briefs)
- [Projects without a dedicated brief](#projects-without-a-dedicated-brief)
- [Keeping the briefs accurate](#keeping-the-briefs-accurate)
- [Related resources](#related-resources)
<!-- TOC END -->

This directory keeps one-page summaries that mirror the authoritative README/CLAUDE guidance inside each project. Think of each brief as the "project status" card that points readers back to the real implementation, the quality gate reports, and the release information stored in `reports/`.

## Active project briefs

- **[FLEXT API](./flext-api/README.md)** – version 0.9.9, fully covered HTTP client + FastAPI integration, production-ready FastAPI app factory,
  and modern protocol support. Quick start: clone the repo, run `poetry install`, and import `FlextApiClient`/`FlextApi`. Quality gate: `pytest` +
  `make validate`; documentation surfaces live inside `docs/` and the `README`/`CLAUDE` files in `flext-api/`.
- **[FLEXT Auth](./flext-auth.md)** – version 2.0.0 with the registry-based authentication foundation, multi-provider architecture, and the
  FlextAuth facade that integrates JWT, OAuth2, OIDC, and future transports. Quick start: `poetry install` inside `flext-auth` and use
  `FlextAuth.quick_start()` or `FlextAuth.with_provider`/`with_registry`. Quality gate: `make validate` (ruff + pyrefly + bandit + pytest + coverage);
  docs live inside the project README/CLAUDE and `docs/` tree.
- **[FLEXT CLI](./flext-cli.md)** – version 0.10.0, 1 016 tests (100% passing), 96%+ coverage per the coverage scan, and the zero-tolerance CLI
  foundation that abstracts Click, Rich, and Tabulate for 32+ projects. Quick start: `poetry add flext-cli`/`pip install flext-cli`, import
  `FlextCli`, and use the direct-access helpers (`formatters`, `file_tools`, `prompts`, `output`). Quality gate: `make validate` with Ruff, Pyrefly,
  Bandit, and pytest; document links live under the project’s `README`, `CLAUDE`, and `docs/` tree.
- **[FLEXT Core](./flext-core.md)** – version 0.10.0, Python 3.13+, 2 820 tests, 81.41% coverage, production-ready foundation for FlextResult, DI,
  and CQRS dispatchers. Quick start: `pip install flext-core`, import `FlextContainer`, `FlextDispatcher`, `FlextResult`. Quality gate: `make validate`.
  Link to `README.md`, `CLAUDE.md`, and core documentation under `docs/`.
- **[FLEXT DB Oracle](./flext-db-oracle.md)** – version 0.9.9, Oracle connectivity + schema introspection built on SQLAlchemy 2 + python-oracledb,
  30 integration test suites (8,633+ lines), and a production-ready FlextDbOracleApi facade. Quick start: clone `flext-db-oracle`, run `poetry install`,
  and use `FlextDbOracleApi` with `FlextDbOracleModels.OracleConfig`. Quality gate: `make validate` (ruff + pyrefly + bandit + pytest + coverage);
  zero tolerance pattern rules live in the project README/CLAUDE docs.
- **[FLEXT DBT LDAP](./flext-dbt-ldap.md)** – version 1.0.0 release prep, dbt Core transformation suite for LDAP/AD with staging → intermediate →
  marts layering, zero-tolerance macros, and 90%+ coverage. Quick start: run `poetry install`, configure `profiles.yml`, then `dbt run`/`dbt test` with
  `make validate`. Documentation lives inside `flext-dbt-ldap/docs/` and the README/CLAUDE files referenced below.
- **[FLEXT dbt LDIF](./flext-dbt-ldif.md)** – version 1.0.0 release prep, dbt project for LDAP/LDIF analytics with programmatic model generation,
  anomaly/risk detection, and 90%+ coverage. Quick start: `poetry install`, `make setup`, `make validate`, `dbt run`, `dbt test`, and `dbt docs serve`;
  quality gates align with the README/CLAUDE docs.
- **[FLEXT dbt Oracle](./flext-dbt-oracle.md)** – version 1.0.0 release prep, dbt Oracle integration with flext-db-oracle connectivity,
  Oracle-specific optimizations, and Singer compliance; quick start runs `poetry install`, `make setup`, `make validate`, `dbt run`, `dbt test`, and
  `dbt docs serve`. Documentation links point to the project README/CLAUDE and `docs/` tree.
- **[FLEXT dbt Oracle WMS](./flext-dbt-oracle-wms.md)** – version 2.1.0, Oracle WMS-focused dbt project with staged/mart models, macros, data
  quality tests, and the mandatory flext-db-oracle/flext-oracle-wms/flext-meltano stack; quick start runs `poetry install`, `make validate`, `dbt run`,
  `dbt test`, and `dbt docs serve`. Docs live inside the project README/CLAUDE and `docs/` directories.
- **[FLEXT gRPC](./flext-grpc.md)** – version 0.9.0, gRPC communication foundation with FlextResult services, Clean Architecture layering, and
  grpcio/protobuf integrations; quality gate `make validate` (ruff + pyrefly + bandit + pytest + coverage) is blocked while coverage/test gaps remain
  (current coverage 39%). Quick start: `poetry install`, `make setup`, `make check`, `make validate`, and use `create_server`/`create_client`; docs live
  inside the project README/CLAUDE and `docs/` tree.
- **[FLEXT LDAP](./flext-ldap.md)** – version 0.10.3, the universal LDAP services foundation covering OpenLDAP 1.x/2.x, Oracle OID/OUD, AD, and
  generic LDAP with FlextResult-driven services, entry adapters, and server-specific implementations. Quick start: `poetry add flext-ldap`, run
  `make setup`+ `make validate`, and use `FlextLdap` + `FlextLdapEntryAdapter` for production flows. Quality gate: `make validate` (ruff, pyrefly,
  Bandit, pytest, coverage) with zero tolerance import/alias rules documented in `CLAUDE.md`.
- **[FLEXT LDIF](./flext-ldif.md)** – version 1.0.0, 1 766 tests, 78% coverage, RFC 2849/4512-compliant parser, quirk registry, and migration
  pipelines for LDAP directories. Quick start: `pip install flext-ldif`, use `FlextLdif.parse`/`migrate`. Quality gate: `make validate`. This brief also
  references the `README`, `CLAUDE`, and the `docs/` folder inside the project.
- **[FLEXT Meltano](./flext-meltano.md)** – version 0.9.0, Singer/Meltano orchestration foundation with plugin scaffolding, pipeline execution, and
  orchestration features; MyPy/Ruff/Bandit pass while the blocked `make test`/coverage gates are noted in the README. Quick start: `poetry install`, `make
setup`, `make validate`, run dbt/deploy commands; docs live inside `flext-meltano/docs/` and the CLAUDE file.
- **[FLEXT Observability](./flext-observability.md)** – version 0.9.0, observability monitoring/tracing foundation with completed architecture,
  instrumentation decorators, and zero tolerance rules; quality validation is blocked by a `flext-core` import issue, so tests currently fail while the
  entity/services surface remains ready. Quick start: `poetry install`, `make setup`, `make validate` (blocked), import `flext_create_metric`/`flext_monitor_function`. Documentation lives inside the project README/CLAUDE and `docs/` tree.
- **[FLEXT Oracle OIC](./flext-oracle-oic.md)** – version 0.9.9, Oracle Integration Cloud client library with OAuth2/IDCS authentication,
  integration pattern execution, and FlextService architecture in early development; quality gate, tests, and coverage are currently blocked by FlextCore
  refactors. Quick start: `poetry install`, `make setup`, configure `OracleOicExtensionSettings`, and use the OAuth2 helpers; docs live inside the
  project README/CLAUDE and `docs/` tree.
- **[FLEXT Oracle WMS](./flext-oracle-wms.md)** – version 0.9.9 RC, Oracle Warehouse Management System integration framework with 25+ LGF v10
  endpoints, FlextResult operations, and architecture-level compliance to migrate httpx → flext-api, integrate flext-auth, and prove connectivity;
  quality gate + tests remain blocked pending the FlextCore refactor. Quick start: `poetry install`, `make setup`, install credentials, and use the
  structured client/test flows; docs live inside the project README/CLAUDE and `docs/` tree.
- **[FLEXT Plugin](./flext-plugin.md)** – version 0.9.0, production-grade plugin management system with discovery, lifecycle, hot reload, security
  validation, and Clean Architecture layering; quality gate `make validate` (ruff + pyrefly + bandit + pytest + coverage) protects the 339-test-suite
  pipeline. Quick start: `make setup`, `make check`, `make validate`, and instantiate `FlextPluginPlatform` from `flext-core`; docs live inside the
  project README/CLAUDE and `docs/` tree.
- **[FLEXT Quality](./flext-quality.md)** – version 0.9.9, centralized quality analysis and reporting platform for the FLEXT ecosystem; architecture is
  solid but `make validate` and the blocked tests depend on FlextModels/BaseModel fixing before they can run again. Quick start: `make setup`, `make
check`, `make validate` (imports currently blocked), instantiate `FlextQualityService`, and run the direct analyzer import; docs link to README/CLAUDE
  and the reports folder.
- **[FLEXT Tap LDAP](./flext-tap-ldap.md)** – version 1.0.0 release preparation, Singer tap for LDAP+LDIF extraction with Clean Architecture, 90%+
  coverage, and enforced flext-core/flext-ldap/flext-meltano dependency rules; quick start runs `poetry add flext-tap-ldap`, `make check`, `make
validate`, and `tap-ldap --discover/run`; docs live inside the project README/CLAUDE/docs tree.
- **[FLEXT Tap LDIF](./flext-tap-ldif.md)** – version 1.0.0 release prep, Singer tap for LDIF extraction with Clean Architecture, 90%+ coverage, and
  flext-core/flext-meltano/flext-ldif dependency hygiene; quick start runs `poetry add flext-tap-ldif`, `make validate`, and Singer discovery/run
  commands; docs reference the project README/CLAUDE and `docs/` folder.
- **[FLEXT Tap Oracle](./flext-tap-oracle.md)** – version 1.0.0 release prep, Oracle Singer tap built on flext-db-oracle/flext-meltano, 90% coverage,
  and zero tolerance rules; quick start runs `poetry install`, `make validate`, Singer discovery/run commands, and CLI entry points; docs live under
  the project README/CLAUDE and `docs/` tree.
- **[FLEXT Tap Oracle OIC](./flext-tap-oracle-oic.md)** – version 1.0.0 release prep, Oracle Integration Cloud Singer tap with OAuth2/IDCS auth, 12+
  streams, retry/backoff, and flext-oracle-oic/flext-meltano re-use; quick start runs `poetry install`, `make validate`, Singer discovery/run
  commands, and uses the tap CLI; docs live inside the project README/CLAUDE and the `docs/` folder.
- **[FLEXT Tap Oracle WMS](./flext-tap-oracle-wms.md)** – version 1.0.0 release prep, Oracle Warehouse Management System Singer tap with 10 working
  streams, over-engineered architecture refactor, and Singer/meltano integration; quick start runs `poetry install`, `make validate`, Singer discovery/run
  commands, and references the TODO/refactor docs; docs live under the project README/CLAUDE and `docs/` tree.
- **[FLEXT Target LDAP](./flext-target-ldap.md)** – version 1.0.0, Singer target for LDAP data loading with Clean Architecture, 90% coverage, and
  MELTANO/Singer compliance; quick start installs `flext-target-ldap`, runs the validation pipeline, and executes `tap-ldap` commands; docs and
  reports live inside the project tree.
- **[FLEXT Target Oracle](./flext-target-oracle.md)** – version 0.9.9 (1.0.0 prep), Singer target for Oracle with strong documentation but blocked
  production readiness because of SQL injection and Singer standard gaps; quick start installs the target, runs `make validate`, and uses
  `FlextOracleTargetSettings`; docs link to README/CLAUDE and the reports folder.

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
