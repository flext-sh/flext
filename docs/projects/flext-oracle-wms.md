# FLEXT Oracle WMS

FLEXT Oracle WMS is the domain package for Oracle Warehouse Management System
(WMS) integration. Its executable source lives under
`flext-oracle-wms/src/flext_oracle_wms/`.

## Status & health

- **Version**: 0.20.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_oracle_wms`
- **Location in this repo**: `flext-oracle-wms/` at the workspace root

### Quality signals

- Run `make check PROJECT=flext-oracle-wms` and
  `make test PROJECT=flext-oracle-wms` through the workspace root.

## Quick start

Use the generated API reference for verified public imports and method
signatures.

## Architecture & modules

The project uses the canonical tiered layout: `api.py` is the public facade;
`_utilities/` contains implementation details; and `config/` is the
configuration source of truth.

### Key architectural patterns

- One public facade, Pydantic boundary models, and the workspace
  config/settings SSOT define the package contract.

## Testing & quality

The root Make gates provide current quality evidence.

## Resources

- [Project README](../../flext-oracle-wms/README.md)
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-core`, `flext-api`, `flext-db-oracle`, `flext-meltano`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
