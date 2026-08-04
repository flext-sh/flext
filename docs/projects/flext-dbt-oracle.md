# FLEXT dbt Oracle

FLEXT dbt Oracle is the integration project that runs dbt transformations against Oracle Database inside the FLEXT
ecosystem. It layers an Oracle-aware dbt service base on top of `flext-db-oracle` (connectivity) and `flext-meltano`
(dbt orchestration), so dbt project execution, connection profiles, and settings all come from the FLEXT SSOT rather
than hand-rolled profiles.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: integration
- **Dependencies**: `flext-core`, `flext-db-oracle`, `flext-meltano`, `dbt-common`, `agate`, `pydantic`

### Quality signals

- All service operations return `r[T]` (`p.Result[...]`) inherited from the `flext-meltano` dbt service contract.
- Settings are validated Pydantic models: `FlextDbtOracleSettings` extends both `FlextDbOracleSettings` and
  `FlextMeltanoSettings`.
- Gates: `make check PROJECT=flext-dbt-oracle`, `make test PROJECT=flext-dbt-oracle`, and `make check` produce the
  authoritative evidence.

## Quick start

```bash
make setup                                # workspace bootstrap (once)
make check PROJECT=flext-dbt-oracle      # lint + type gates
```

```python
from flext_dbt_oracle import s  # FlextDbtOracleServiceBase


class OracleMartService(s):
    """Concrete dbt pipeline service; inherits Oracle + dbt orchestration."""


service = OracleMartService()

# The Oracle dbt connection profile is built from settings.DbOracle.*
# (host/port/credentials/service name) plus the dbt schema from
# settings.DbtOracle.schema_name — no hand-written profiles.yml.
profile = service.connection_profile
```

Services for a concrete dbt pipeline subclass `FlextDbtOracleServiceBase` (exported as `s`) and inherit dbt execution
from `flext-meltano`'s service contract; the canonical `dbt_project_name` is `"dbt-oracle"`.

## Architecture & modules

The package follows the canonical FLEXT layout under `src/flext_dbt_oracle/`:

- `base.py` — `FlextDbtOracleServiceBase` (`s`): extends `FlextMeltanoDbtServiceBase`, pins `dbt_project_name = "dbt-
  oracle"`, and builds `m.DbtOracle.DbtConnectionProfile` from the settings namespaces.
- `_settings.py` — `FlextDbtOracleSettings`: multiple-inheritance settings model over the db-oracle and meltano settings
  trees; runtime bootstrap wires it as the service settings type.
- `_config.py` — `FlextDbtOracleConfig` over `FlextMeltanoConfig`; execution parametrization lives under `config/`.
- `adapters.py` — Oracle adapter helpers for dbt metadata normalization.
- `connections.py` — connection module re-export surface.
- `constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py` — `c/m/t/p/u` facet declarations
  (`FlextDbtOracleConstants/Models/Types/Protocols/Utilities`) that extend the `flext-db-oracle` and `flext-meltano`
  facets by MRO.

### Key architectural patterns

- **Service-base delivery**: the package ships a service base rather than a standalone facade — downstream dbt services
  inherit Oracle connectivity, settings resolution, and dbt orchestration in one MRO chain.
- **Settings SSOT, zero duplication**: connection scalars come from `settings.DbOracle.*` (owned by `flext-db-oracle`);
  only the dbt-specific schema/project fields live in `settings.DbtOracle.*`.
- **No direct dbt or oracledb imports**: dbt execution is routed through `flext-meltano`; database access through
  `flext-db-oracle`.
- **Facade aliases**: the root package exports `c`, `m`, `t`, `p`, `u`, and `settings` for MRO composition by consumers.

## Testing & quality

- Tests live in the project `tests/` tree and run through `make test PROJECT=flext-dbt-oracle`.
- dbt run paths need a reachable Oracle instance and a configured target; without one, unit suites and static gates are
  the evidence of record.
- The authoritative quality verdict comes from `make check PROJECT=flext-dbt-oracle` and `make check`.

## Resources

- [Project README](../../flext-dbt-oracle/README.md) (auto-generated module map and integration pointers)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law
- Generated API overview: `flext-dbt-oracle/docs/api-reference/generated/overview.md`
- Related projects: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-tap-oracle`, `flext-target-oracle`, `flext-
  dbt-oracle-wms`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run `make check PROJECT=flext-dbt-oracle` on your change.
