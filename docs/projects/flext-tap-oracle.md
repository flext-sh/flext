# FLEXT Tap Oracle

FLEXT Tap Oracle is the Singer extraction package for Oracle Database. Its
executable source lives under `flext-tap-oracle/src/flext_tap_oracle/`.

## Status & health

- **Version**: 0.12.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_tap_oracle`
- **Location in this repo**: `flext-tap-oracle/` at the workspace root

### Quality signals

- Run `make check PROJECT=flext-tap-oracle` and
  `make test PROJECT=flext-tap-oracle` through the workspace root.

## Quick start

Use the generated API reference and the console entry-point metadata in
`pyproject.toml` for verified command and import details.

## Architecture & modules

The project uses the canonical Singer thin-driver layout: `tap.py` owns the
console adapter, `api.py` owns the public facade, and `config/` owns execution
parameters.

### Key architectural patterns

- The driver delegates Oracle access to `flext-db-oracle` and Singer
  orchestration to `flext-meltano`.

## Testing & quality

The root Make gates provide current quality evidence.

## Resources

- [Project README](../../flext-tap-oracle/README.md)
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`, `flext-target-oracle`,
  `flext-dbt-oracle`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
