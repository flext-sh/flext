# FLEXT dbt LDIF

FLEXT dbt LDIF (v1.0.0 release prep) is the dbt project that turns LDAP/LDIF data into analytics-ready marts, pairing flext-core discipline with programmatic model generation, anomaly/risk detection, and 90%+ coverage.

## Status & health

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+ with Poetry-managed dependencies
- **Tests**: 339+ unit/integration/e2e suites (Python + dbt); `make validate` (lint + type + security + tests + coverage) is the gating command, and everyone is expected to run it before merging.
- **Coverage**: 90%+ (See `reports/coverage-scan-*` for snapshots)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + dbt tests + coverage + docstring checks); `make check`, `make lint`, `make type-check`, and `make security` are green.
- **Dependencies**: `flext-core`, `flext-ldap`, `flext-meltano`, `dbt-core`, `dbt-postgres`, `flext-dbt-ldif` macros built on the Singer tap/target ecosystem.
- **Zero tolerance**: no direct dbt/ldif/click/rich imports; use flext-meltano/flext-ldif/flext-cli; all flows return `FlextResult[T]`, no `Any`, `cast`, or `TYPE_CHECKING`.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-dbt-ldif.git
cd flext-dbt-ldif
poetry install
make setup
make validate
```

```bash
dbt deps
make generate-models
dbt run
dbt test
dbt docs generate
dbt docs serve --port 8080
```

## Architecture & patterns

- **Layers**: Clean architecture (Domain → Application → Infrastructure → Protocol); tiers enforce one-way imports and rely on flext-core short aliases (`r`, `t`, `m`).
- **Model generation**: `DBTModelGenerator` and `LDIFAnalytics` classes inside `src/flext_dbt_ldif` programmatically produce staging/intermediate/mart models, macros, and metrics for LDAP analytics.
- **Data modeling**: staging (`stg_ldif_entries`), intermediate, and mart layers (e.g., `analytics_ldif_insights`) plus macros for DN validation, depth calculation, anomaly detection, and risk scoring.
- **Integration**: relies on `flext-meltano` (Singer orchestration), `flext-ldif` (LDIF parsing), and `flext-core` (FlextResult, DI, logging) for consistent behavior.

## Quality & operations

- Validation commands: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make dbt-test`, and `make validate` (combines all gates).
- Testing categories: Python (`pytest` for generators, CLI, infrastructure), dbt tests (staging/marts) triggered via `dbt test`, Docker/LDAP integration for Singer flows, and scenario-specific `tests/test_ldif_*.py` modules.
- Quality policy: zero Ruff/Pyrefly errors, zero `Any`, zero `cast`, and all CLI flows routed through `flext-cli` to respect zero-tolerance rules.

## Resources & references

- [Project README](../../flext-dbt-ldif/README.md)
- [CLAUDE governance](../../flext-dbt-ldif/CLAUDE.md) covering zero-tolerance dependencies and commands
- `docs/` (getting started, architecture, configuration, troubleshooting, testing plays)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for the quality evidence referenced above
- Related projects: `flext-core`, `flext-ldif`, `flext-meltano`, `flext-tap-ldif`, `flext-target-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-dbt-ldif/issues>
- Discussions: <https://github.com/flext-sh/flext-dbt-ldif/discussions>
- Follow `docs/standards/README.md` and this project’s `CLAUDE` before editing docs or code so the portal remains accurate.
