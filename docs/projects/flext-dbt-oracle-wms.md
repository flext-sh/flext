# FLEXT dbt Oracle WMS

FLEXT dbt Oracle WMS is the integration project that transforms Oracle Warehouse Management System (WMS) data with dbt. It composes `flext-oracle-wms` (WMS domain and extraction), `flext-meltano` (dbt orchestration), and `flext-core` (result contracts, settings SSOT) behind one domain facade plus a CLI adapter, so WMS-to-dbt workflows run end to end through FLEXT contracts.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: integration
- **Dependencies**: `flext-core`, `flext-meltano`, `flext-oracle-wms`, `click`, `pydantic`

### Quality signals

- All operations return `r[T]` (`p.Result[...]`); workflow payloads are validated models, not raw dictionaries.
- Settings are validated Pydantic models (`FlextDbtOracleWmsSettings`), consumed through the settings SSOT.
- Gates: `make check PROJECT=flext-dbt-oracle-wms`, `make test PROJECT=flext-dbt-oracle-wms`, and `make val` produce the authoritative evidence.

## Quick start

```bash
make boot                                     # workspace bootstrap (once)
make check PROJECT=flext-dbt-oracle-wms       # lint + type gates
```

```python
from flext_dbt_oracle_wms.simple_api import FlextDbtOracleWms

api = FlextDbtOracleWms()  # settings resolved from the global singleton

health = api.validate_wms_connection()
if health.success:
    workflow = api.run_oracle_wms_to_dbt_workflow()
```

The CLI adapter exposes the same facade as commands (`info`, `discover`, `extract <entity>`, `pipeline`):

```python
from flext_dbt_oracle_wms import FlextDbtOracleWmsCliService

exit_code = FlextDbtOracleWmsCliService().main(["pipeline"])
```

## Architecture & modules

The package follows the canonical FLEXT layout under `src/flext_dbt_oracle_wms/`:

- `simple_api.py` — `FlextDbtOracleWms`, the domain facade composed by MRO from the private `_*` workflow/model/metadata mixins (`_simple_api_workflow`, `_simple_api_models`, `_simple_api_metadata`, `_simple_api_base`).
- `_simple_api_workflow.py` — `run_oracle_wms_to_dbt_workflow`, `validate_wms_connection` (real client health check), and the `execute` service contract.
- `_simple_api_models.py` — `generate_dbt_models_from_wms` and `monitor_dbt_execution`.
- `cli.py` — `FlextDbtOracleWmsCliService` and the `main` entry point: maps CLI commands to facade calls and returns process exit codes.
- `base.py` — `FlextDbtOracleWmsServiceBase` (`s`) over the `flext-meltano` service base.
- `_settings.py` / `config/` — settings SSOT (`FlextDbtOracleWmsSettings`), consumed as `from flext_dbt_oracle_wms import settings`.
- `constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py`, `_utilities/` — `c/m/t/p/u` facet declarations and behavior.

### Key architectural patterns

- **Facade + CLI adapter**: domain behavior lives in the MRO facade; the CLI service is a thin translator that returns exit codes and never reimplements workflow logic.
- **Real health checks**: `validate_wms_connection` delegates to the `flext-oracle-wms` client rather than simulating connectivity.
- **Workflow tracking**: workflow completion is logged through the service's tracking context, and results are validated through `m.Dict.model_validate(...)` before returning.
- **Zero direct dbt/Oracle imports**: WMS access goes through `flext-oracle-wms`; dbt execution through `flext-meltano`.

## Testing & quality

- Tests live in the project `tests/` tree and run through `make test PROJECT=flext-dbt-oracle-wms`.
- End-to-end workflow paths need a reachable Oracle WMS instance; without one, unit suites and static gates are the evidence of record.
- The authoritative quality verdict comes from `make check PROJECT=flext-dbt-oracle-wms` and `make val`.

## Resources

- [Project README](../../flext-dbt-oracle-wms/README.md) (auto-generated module map and integration pointers)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law
- Generated API overview: `flext-dbt-oracle-wms/docs/api-reference/generated/overview.md`
- Related projects: `flext-core`, `flext-oracle-wms`, `flext-meltano`, `flext-tap-oracle-wms`, `flext-target-oracle-wms`, `flext-dbt-oracle`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run `make check PROJECT=flext-dbt-oracle-wms` on your change.
