# FLEXT Oracle WMS

FLEXT Oracle WMS (`flext-oracle-wms`) is the enterprise client library for Oracle Warehouse Management System (WMS) Cloud in the FLEXT platform. It exposes a typed facade over the Oracle WMS REST surface (LGF v10 and legacy API versions) with client construction, authentication, entity discovery, and filtering utilities, all returning `r[T]` results.

## Status & health

- **Version**: 0.12.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_oracle_wms` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-oracle-wms/` at the workspace root

### Quality signals

- Gates run through the workspace Make contract: `make check PROJECT=flext-oracle-wms`, `make test PROJECT=flext-oracle-wms`, `make val`.
- Strict typing per workspace `AGENTS.md`: no `Any`/`object`, Pydantic 2-way models, `r[T]` on every fallible path.
- No coverage or test-count metrics are asserted here; the gates above produce the authoritative numbers.

## Quick start

```python
from flext_oracle_wms import FlextOracleWmsApi, FlextOracleWmsSettings

settings = FlextOracleWmsSettings()  # namespaced under settings.OracleWms.*
api = FlextOracleWmsApi(settings)

result = api.execute()
if result.is_success:
    endpoints = FlextOracleWmsApi.api_endpoints()
```

The `settings.OracleWms.*` group carries `base_url`, `api_version` (default `LGF_V10`), `auth_method`, `username`/`password`, `timeout`, `retry_attempts`, `verify_ssl`, `connection_pool_size`, and `cache_duration`.

## Architecture & modules

Source lives under `flext-oracle-wms/src/flext_oracle_wms/`:

- `api.py` — `FlextOracleWmsApi`, the public facade (a `s[bool]` service) exported as the operational alias `oracle_wms`. It provides `execute()`, the static `api_endpoints()` catalog (typed `m.OracleWms.ApiEndpoint` entries), and the factories `create_flext_http_client` / `create_oracle_wms_client`.
- `_utilities/` — private utility layer: `http_client` (HTTP transport on the FLEXT API abstraction), `auth` (authentication), `client` (WMS client), `discovery` (entity discovery), `filtering` (query filtering).
- `config/oracle-wms.yaml` — execution parametrization (SSOT per ADR-005).
- `errors.py` — `FlextOracleWmsErrors`, the package exception hierarchy extending the `flext_api` exception facade.
- Canonical facet facades: `c`, `m`, `p`, `t`, `u`, plus `settings` (`FlextOracleWmsSettings`) and `config` (`FlextOracleWmsConfig`) singletons; operational aliases `d`, `h`, `r`, `s`, `x` come from the parent chain (`flext_api`).

### Key architectural patterns

- One public facade composed by MRO; every fallible operation returns `p.Result[...]` (`r[T]`).
- Settings/config are the only parametrization source: `settings.OracleWms.*` is validated once when the frozen singleton is constructed.
- The typed endpoint catalog (`api_endpoints()`) is data, not ad-hoc URL strings, so consumers discover WMS operations through models.

## Testing & quality

- Scoped suites run via `make check PROJECT=flext-oracle-wms` and `make test PROJECT=flext-oracle-wms`; full workspace validation is `make val`.
- Tests assert the public surface only (facade methods, exported models, endpoint catalog) per the workspace testing law.

## Resources

- [Project README](../../flext-oracle-wms/README.md)
- Source: `flext-oracle-wms/src/flext_oracle_wms/`
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-core`, `flext-cli`, `flext-api`, `flext-auth`, `flext-db-oracle`, `flext-tap-oracle-wms`, `flext-target-oracle-wms`, `flext-dbt-oracle-wms`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
