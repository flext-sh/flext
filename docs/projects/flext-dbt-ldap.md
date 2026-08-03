# FLEXT dbt LDAP

FLEXT dbt LDAP is the integration project that turns LDAP/Active Directory data into analytics-ready warehouse tables.
It composes `flext-ldap` (directory transport), `flext-meltano` (dbt orchestration), and `flext-core` (result contracts,
settings SSOT) behind one MRO facade so extraction, transformation, sync, and quality validation share identical
patterns.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: integration
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldap`, `flext-meltano`, `pydantic`

### Quality signals

- All operations return `r[T]` (`p.Result[...]`) with typed payload models under `m.DbtLdap.*`.
- Settings are validated Pydantic models (`FlextDbtLdapSettings`); no direct environment reads in runtime code.
- Gates: `make check PROJECT=flext-dbt-ldap`, `make test PROJECT=flext-dbt-ldap`, and `make val` produce the
  authoritative evidence.

## Quick start

```bash
make setup                              # workspace bootstrap (once)
make check PROJECT=flext-dbt-ldap      # lint + type gates
```

```python
from flext_dbt_ldap import FlextDbtLdap

# With no override, the facade resolves the global FlextDbtLdapSettings singleton.
api = FlextDbtLdap()

# Full pipeline: extract entries via flext-ldap, transform via flext-meltano dbt.
result = api.run_full_pipeline()
if result.success:
    sync = api.run_full_data_warehouse_sync(incremental=True)
    quality = api.validate_warehouse_data_quality()
```

Granular entry points on the same facade include `extract_ldap_entries(...)`, `transform_with_dbt(...)`,
`sync_users_to_warehouse(...)`, `sync_groups_to_warehouse(...)`, `sync_memberships_to_warehouse(...)`,
`run_dbt_models(...)`, and `generate_analytics_report(...)`.

## Architecture & modules

The package follows the canonical FLEXT layout under `src/flext_dbt_ldap/`:

- `api.py` — `FlextDbtLdap` (also exported as `dbt_ldap`), the unified MRO facade. All extraction, transformation, sync,
  and validation behavior arrives through mixins; there are no wrapper or delegation methods.
- `services/client.py` — client mixin: `create_ldap_api`, `extract_ldap_entries`, `transform_with_dbt`,
  `validate_ldap_data`, `run_full_pipeline`.
- `services/sync.py` — `FlextDbtLdapSyncMixin`: warehouse sync for users/groups/memberships, dbt model runs, full
  warehouse sync, data-quality validation, analytics reports, with bookmark state persisted under `history/`.
- `base.py` — service base (`s`) over `flext-meltano`'s dbt service base.
- `_settings.py` / `config/` — settings SSOT (`FlextDbtLdapSettings`), consumed as `from flext_dbt_ldap import
  settings`.
- `_constants/`, `_models/`, `_utilities/`, `constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py` —
  `c/m/t/p/u` facet declarations and behavior.

### Key architectural patterns

- **MRO composition**: one public facade class per project; behavior lives in service mixins, never in loose helper
  functions.
- **Zero direct dbt/ldap imports**: directory access goes through `flext-ldap`; dbt execution goes through `flext-
  meltano`.
- **Settings SSOT**: `FlextDbtLdapSettings.fetch_global()` supplies configuration when the caller passes no override.
- **Typed payloads**: sync results, run status, and analytics reports are `m.DbtLdap.*` Pydantic models, not raw
  dictionaries.

## Testing & quality

- Tests live in the project `tests/` tree and run through `make test PROJECT=flext-dbt-ldap`.
- Warehouse sync paths need a reachable LDAP directory and a dbt target; without them, unit suites and static gates are
  the evidence of record.
- The authoritative quality verdict comes from `make check PROJECT=flext-dbt-ldap` and `make val`.

## Resources

- [Project README](../../flext-dbt-ldap/README.md) (auto-generated module map and integration pointers)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law
- Generated API overview: `flext-dbt-ldap/docs/api-reference/generated/overview.md`
- Related projects: `flext-core`, `flext-ldap`, `flext-meltano`, `flext-tap-ldap`, `flext-target-ldap`, `flext-dbt-ldif`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run `make check PROJECT=flext-dbt-ldap` on your change.
