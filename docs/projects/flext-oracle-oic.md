# FLEXT Oracle OIC

FLEXT Oracle OIC (`flext-oracle-oic`) is the Oracle Integration Cloud (OIC) extension library of the FLEXT platform. It
provides a typed, `r[T]`-based API facade for OIC integration lifecycle management (create, activate, run, monitor),
OAuth2 client-credentials authentication, and paginated REST access to integrations, connections, lookups, and packages.

## Status & health

- **Version**: 0.12.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_oracle_oic` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-oracle-oic/` at the workspace root

### Quality signals

- Lint, formatting, and type gates run through the workspace Make contract:
  `make check PROJECT=flext-oracle-oic`, `make test PROJECT=flext-oracle-oic`, `make check`.
- Strict typing policy per workspace `AGENTS.md`: no `Any`/`object`, Pydantic 2-way models for owned payloads, `r[T]`
  contracts on every fallible path.
- No health metrics (coverage or test counts) are asserted on this page; the gates above produce the authoritative
  numbers.

## Quick start

The package is developed inside the FLEXT monorepo; the console entry points are `flext-oracle-oic` and `oracle-oic-
ext`.

```python
from flext_oracle_oic import FlextOracleOicApi, FlextOracleOicSettings

settings = FlextOracleOicSettings()  # namespaced under settings.OracleOic.*
api = FlextOracleOicApi(settings)

result = api.test_connection()
if result.is_success:
    integrations = api.list_integrations()
```

The `settings.OracleOic.*` group carries `base_url`, `api_version`, `request_timeout`, `max_retries`, SSL toggles, and
the OAuth2 fields (`oauth_client_id`, `oauth_client_secret`, `oauth_token_url`, `oauth_scope`, `oauth_client_aud`).

## Architecture & modules

Source lives under `flext-oracle-oic/src/flext_oracle_oic/`:

- `api.py` — `FlextOracleOicApi`, the public MRO facade over the composed service; exported as the operational alias
  `oracle_oic`. Operations include `test_connection`, integration CRUD and lifecycle (`create_integration`,
  `activate_integration`, `deactivate_integration`, `update_integration`, `delete_integration`, `list_integrations`,
  `fetch_integration`), execution entry points (`execute_app_driven_orchestration`, `execute_scheduled_orchestration`,
  `execute_file_transfer`), monitoring (`fetch_health_status`, `fetch_performance_metrics`), and auth helpers
  (`fetch_auth_context`, `refresh_auth_token`, `validate_auth_token`).
- `service.py` / `services/` — the composed service class assembled from focused mixins: `auth`, `integration_crud`,
  `integration_lifecycle`, `monitoring`, `orchestration`, over a shared `base`.
- `ext_client.py` — `FlextOracleOicClient`, the lower-level OIC REST client: OAuth client-credentials flow, connections,
  lookups, packages, and paginated request handling built on the FLEXT API abstraction.
- `main.py` / `__main__.py` — CLI entry point (`FlextOracleOicCli`, `main`).
- `config/oracle-oic.yaml` — execution parametrization (SSOT per ADR-005).
- Canonical facet facades: `c`, `m`, `p`, `t`, `u`, `s`, plus `settings`/`config` singletons; operational aliases `d`,
  `e`, `h`, `r`, `x` come from the parent chain (`flext_auth`).

### Key architectural patterns

- Single public facade per responsibility, composed by MRO; all fallible operations return `p.Result[...]` (`r[T]`)
  instead of raising.
- Settings and config are the only source of parametrization: `settings.OracleOic.*` validated once at singleton
  construction; facets never re-read the environment.
- Private implementation modules (`_settings`, `_config`, `_utilities`) stay declaration-only; behavior lives in
  `services/`, `utilities.py`, `api.py`, and `main.py`.

## Testing & quality

- Run the scoped suites through the workspace gates: `make check PROJECT=flext-oracle-oic` and `make test PROJECT=flext-
  oracle-oic`; full workspace validation is `make check`.
- Tests exercise the public surface only (facade methods, exported models, CLI behavior) per the workspace testing law.

## Resources

- [Project README](../../flext-oracle-oic/README.md)
- Source: `flext-oracle-oic/src/flext_oracle_oic/`
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-core`, `flext-cli`, `flext-auth`, `flext-api`, `flext-tap-oracle-oic`, `flext-target-oracle-
  oic`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
