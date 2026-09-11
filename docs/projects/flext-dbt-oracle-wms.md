# FLEXT dbt Oracle WMS

FLEXT dbt Oracle WMS is the integration package for Oracle Warehouse Management
System (WMS) transformations with dbt. Its executable source lives in
`flext-dbt-oracle-wms/src/flext_dbt_oracle_wms/`.

## Status & health

- **Version**: `0.12.0-dev` (active development cycle)
- **Python**: 3.13+
- **Project class**: integration
- **Dependencies**: `flext-core`, `flext-meltano`, `flext-oracle-wms`, `click`, `pydantic`

### Quality signals

- The implementation follows the workspace config/settings SSOT and
  thin-driver architecture.
- Authoritative evidence comes from the project-scoped root Make gates.

## Quick start

```bash
make boot
make check PROJECT=flext-dbt-oracle-wms
make test PROJECT=flext-dbt-oracle-wms
```

Use the generated API reference for public imports and method signatures; this
page deliberately avoids stale hand-maintained call examples.

## Architecture & modules

The package uses the canonical `c -> t -> p -> m -> u` layout, with the public
facade in `api.py`, CLI adapter in `cli.py`, service implementations in
`services/`, and project configuration under `config/`.

### Key architectural patterns

- **Thin driver**: WMS access is owned by `flext-oracle-wms`; dbt
  orchestration is owned by `flext-meltano`.
- **Typed boundary**: payloads use Pydantic models and `r[T]` result flow.

## Testing & quality

Use `make check PROJECT=flext-dbt-oracle-wms` and
`make test PROJECT=flext-dbt-oracle-wms` for project evidence.

## Resources

- [Project README](../../flext-dbt-oracle-wms/README.md)
- [Workspace AGENTS.md](../../AGENTS.md) — FLEXT engineering law
- [Workspace API overview](../api-reference/generated/flext-dbt-oracle-wms.md)
- Related projects: `flext-core`, `flext-oracle-wms`, `flext-meltano`, `flext-tap-oracle-wms`, `flext-target-oracle-
  wms`, `flext-dbt-oracle`

## Support & issues

- Issues and discussions: <https://github.com/flext-sh/flext> (monorepo)
- Before contributing, read the workspace `AGENTS.md` and run the project
  gates through the root Make dispatcher.
