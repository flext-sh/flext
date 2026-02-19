# FLEXT DBT LDAP


<!-- TOC START -->
- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture & layers](#architecture-layers)
- [Key features](#key-features)
- [Testing & quality](#testing-quality)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT DBT LDAP (v1.0.0) is the dbt Core transformation suite that turns LDAP/Active Directory data into analytics-ready marts using the CLEAN ARCHITECTURE patterns from the FLEXT ecosystem.

## Status & metrics

- **Version**: 1.0.0 (Release preparation)
- **Python**: 3.13+ with Poetry-managed deps
- **Tests**: 90%+ coverage across Python tests and dbt suites
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + dbt test + coverage)
- **Dependencies**: `flext-core`, `flext-ldap`, `flext-meltano`, `dbt-core` (>=1.6), DuckDB/PostgreSQL adapters
- **Documentation**: full docs under `flext-dbt-ldap/docs/` (getting-started, architecture, guides)

## Quick start

```bash
git clone https://github.com/flext-sh/flext.git
cd flext-dbt-ldap
poetry install
cp profiles.yml.example profiles.yml  # fill in the PostgreSQL or DuckDB target
dbt deps
dbt run
```

```bash
make validate          # run lint/type/security/test/dbt checks
dbt docs generate
dbt docs serve --port 8080
```

## Architecture & layers

- **Facade**: `src/flext_dbt_ldap/simple_api.py` and `api.py` expose `FlextDbtLdap` with methods to run models, tests, and macros while keeping SQLAlchemy/dbt internals isolated.
- **Model tiers**: `models/` follows staging → intermediate → marts (dims/facts) → snapshots; macros handle LDAP DN parsing and attribute normalization.
- **Python domain**: `src/flext_dbt_ldap/ldap_integration.py`, `models.py`, and `dbt_services.py` provide FlextResult-friendly services that orchestrate macro rendering, dbt invocation, and metadata reporting.
- **Zero tolerance**: registry of `flext-meltano` for all dbt operations and `flext-ldap` for all LDAP transports; direct imports of dbt/ldap3 are forbidden (see `CLAUDE.md`).

## Key features

- LDAP-specific macros (`parse_dn`, `generate_hierarchy_path`, `normalize_array_field`, `ldap_timestamp_to_timestamp`).
- Data models for users, groups, memberships, and organizational hierarchy with incremental performance options.
- dbt snapshots plus historical tracking, anomaly detection tests, and analytics-focused marts (e.g., `dim_users`, `dim_groups`, `fact_memberships`).
- Integration with dbt docs/CI pipelines, including `make dbt-run`, `make dbt-test`, `make dbt-docs`, and `make dbt-clean`.

## Testing & quality

- `make validate` runs Pett, Pyrefly, Ruff, Bandit, coverage, and dbt tests (unit + integration + dbt compilation).
- dbt tests cover staging/intermediate/mart models plus LDAP macros (`dbt test --select staging`).
- Python tests run via `pytest tests/` with markers for `unit`, `integration`, `dbt`, `ldap`, and `validation`.
- `reports/coverage-scan-*`, `reports/lint-output/*`, and `reports/pytest/*` contain the artifacts referenced in the portal.

## Resources & references

- [Project README](../../flext-dbt-ldap/README.md)
- [CLAUDE governance](../../flext-dbt-ldap/CLAUDE.md) – zero tolerance rules and workflow commands
- `flext-dbt-ldap/docs/` – quick start, configuration, architecture, troubleshooting, and integration guides
- Related artifacts: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`
- Related projects: `flext-core`, `flext-ldap`, `flext-meltano`, `flext-tap-ldap`, `flext-target-ldap`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-dbt-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-dbt-ldap/discussions>
- Follow `docs/standards/README.md` and workspace CLAUDE instructions before editing docs or code to keep the portal trustworthy.
