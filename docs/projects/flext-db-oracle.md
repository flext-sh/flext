# FLEXT DB Oracle

FLEXT DB Oracle is the enterprise Oracle Database operations library of the FLEXT ecosystem. It wraps `python-oracledb`
behind the canonical FLEXT facades (`c/m/t/p/u`, `r[T]` result contracts) so every Oracle-facing project — taps,
targets, dbt adapters — reuses one typed connection, query, and schema-introspection stack instead of reimplementing it.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: domain library
- **Dependencies**: `flext-core`, `flext-cli`, `oracledb`, `pydantic`

### Quality signals

- All fallible operations return `r[T]` (`p.Result[T]`); no exceptions cross the public API as control flow.
- Settings are validated Pydantic models (`FlextDbOracleSettings`, env prefix `ORACLE_`, nested delimiter `__`).
- Gates: `make check PROJECT=flext-db-oracle`, `make test PROJECT=flext-db-oracle`, and `make val` produce the
  authoritative lint/type/test evidence — see those outputs rather than any number stated here.

## Quick start

```bash
make boot                                  # workspace bootstrap (once)
make check PROJECT=flext-db-oracle         # lint + type gates
```

```python
from flext_db_oracle import FlextDbOracleApi, FlextDbOracleSettings

# Settings resolve from env (ORACLE_DBORACLE__HOST, ORACLE_DBORACLE__PASSWORD, ...)
# or from defaults; the DbOracle namespace carries host/port/service_name/
# username/password/timeout/pool bounds.
settings = FlextDbOracleSettings()
api = FlextDbOracleApi(settings)

connected = api.connect()
if connected.success:
    health = api.fetch_health_status()
    tables = api.fetch_tables()  # r[StrSequence]
    rows = api.execute_sql(
        "SELECT table_name FROM user_tables FETCH FIRST :n ROWS ONLY", {"n": 5}
    )
    api.disconnect()
```

Alternative constructors on the same facade: `FlextDbOracleApi.from_config(settings)`,
`FlextDbOracleApi.from_env(prefix="ORACLE_")`, and `FlextDbOracleApi.from_url(url)` — each returns `r[Self]`.

## Architecture & modules

The package follows the canonical FLEXT layout under `src/flext_db_oracle/`:

- `api.py` — `FlextDbOracleApi`, the thin MRO facade (also exported as `db_oracle`) over the composed runtime.
- `base.py` — `FlextDbOracleServiceBase` (`s`), the service base composing project utilities over `flext-core`'s service
  contract.
- `services/` — behavior by responsibility: `api_runtime` (facade runtime), `connection` (pool/lifecycle), `query` and
  `execute_*` paths, `schema` (tables, columns, primary keys, metadata), `sql_builder`, `singer` (Singer type mapping),
  and `plugin` (plugin registry: `list_plugins`, `fetch_plugin`).
- `client.py` / `dispatcher.py` — `FlextDbOracleClient` and `FlextDbOracleDispatcher` for lower-level call routing.
- `_settings.py` / `config/` — SSOT configuration: `FlextDbOracleSettings` extends `flext-cli`'s `FlextCliSettings`;
  every project field lives under the `DbOracle` namespace.
- `_models/`, `_utilities/`, `constants.py`, `typings.py`, `protocols.py`, `models.py`, `utilities.py` — the `c/m/t/p/u`
  facet declarations and behavior.

### Key architectural patterns

- **Single facade**: `FlextDbOracleApi` is the only entry point consumers need; connection, query, schema introspection,
  Singer mapping, and plugin lookup all hang off it.
- **Settings SSOT**: no `os.environ` reads in runtime code; configuration arrives only through the validated
  `FlextDbOracleSettings` singleton form (`from flext_db_oracle import settings`).
- **Result contracts**: `connect()`, `execute_sql(...)`, `fetch_tables()`, `fetch_health_status()`, and
  `fetch_observability_metrics()` all return `p.Result[...]`.
- **Facade aliases**: the root package exports `c`, `m`, `t`, `p`, `u`, `r`, `e`, `x`, `h`, `d`, `s`, and `settings` so
  downstream projects compose by MRO instead of importing `oracledb` directly.

## Testing & quality

- Tests live in the project `tests/` tree and run through `make test PROJECT=flext-db-oracle` (unit scope) and the
  workspace gates.
- Oracle-backed integration paths require a reachable Oracle instance; without one, unit suites and static gates are the
  evidence of record.
- The authoritative quality verdict comes from `make check PROJECT=flext-db-oracle` and `make val` — consult their
  output for current lint, typing, and test status.

## Resources

- [Project README](../../flext-db-oracle/README.md) (auto-generated module map and integration pointers)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law (facades, `r[T]`, settings SSOT)
- Generated API overview: `flext-db-oracle/docs/api-reference/generated/overview.md`
- Downstream consumers: `flext-dbt-oracle`, `flext-tap-oracle`, `flext-target-oracle`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run `make check PROJECT=flext-db-oracle` on your change.
