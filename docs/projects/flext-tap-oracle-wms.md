# FLEXT Tap Oracle WMS

FLEXT Tap Oracle WMS is the Singer tap that extracts data from Oracle Warehouse Management System (WMS). It composes the
FLEXT facades with `flext-oracle-wms` (WMS connectivity) and `flext-meltano` (Singer tap base) behind `r[T]` contracts
and the canonical `c/m/p/t/u` facade layout.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Status**: Active development on the `0.12.0-dev` branch; the package builds and exports its full public surface.
- **Description** (from `pyproject.toml`): "FLEXT Tap Oracle WMS - Singer Tap for Oracle Warehouse Management System"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-meltano`, `flext-oracle-wms`
- **Console scripts**: `tap-oracle-wms` and `flext-tap-oracle-wms` (both bound to `flext_tap_oracle_wms.cli:main`)

### Quality signals

- Quality gates run through the workspace Make contract: `make check PROJECT=flext-tap-oracle-wms`, `make test
  PROJECT=flext-tap-oracle-wms`, and `make val`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

```bash
cd flext-tap-oracle-wms
poetry install
make check PROJECT=flext-tap-oracle-wms
```

Singer discovery and sync through the console script:

```bash
tap-oracle-wms --config settings.json --discover > catalog.json
tap-oracle-wms --config settings.json --catalog catalog.json --state state.json
```

Programmatic use via the public facade:

```python
from flext_tap_oracle_wms import FlextTapOracleWmsService, tap_oracle_wms

# tap_oracle_wms is the operational alias for FlextTapOracleWmsService
service = tap_oracle_wms()
```

## Architecture & modules

```text
src/flext_tap_oracle_wms/
├── api.py        # FlextTapOracleWmsService (tap_oracle_wms alias)
├── cli.py        # main entry point
├── tap.py        # FlextTapOracleWms tap class
├── streams.py    # FlextTapOracleWmsStream (dynamic WMS entity stream)
├── _settings.py  # FlextTapOracleWmsSettings + settings singleton
├── config/       # Execution parametrization (YAML)
├── constants.py  # c facade
├── models.py     # m facade
├── protocols.py  # p facade
├── typings.py    # t facade
└── utilities.py  # u facade
```

### Key architectural patterns

- **Meltano tap service**: `FlextTapOracleWmsService` extends `FlextMeltanoTapServiceBase`, which provides CLI dispatch
  (`cli_main`), catalog discovery (`run_discover`), and sync execution (`run_sync`) via MRO. Its `create_tap_instance`
  wraps `FlextTapOracleWms` in the `FlextMeltanoSingerTapAdapter`.
- **Dynamic stream model**: `FlextTapOracleWmsStream` extends `m.Meltano.SingerStreamBase` and adapts generically to any
  Oracle WMS entity, so entity coverage is configuration-driven instead of one class per entity.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_meltano`.
- **Result contracts**: fallible paths return `r[T]`; WMS API concerns stay inside `flext-oracle-wms`, never in direct
  third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test PROJECT=flext-tap-oracle-wms`; Singer behavior is
  exercised through the tap CLI and discovery flow.
- Pre-merge verification: `make check PROJECT=flext-tap-oracle-wms` (lint + typing + security selectors) and `make val`.

## Resources

- [Project README](../../flext-tap-oracle-wms/README.md)
- [Project docs portal](../../flext-tap-oracle-wms/docs/index.md)
- Related projects: `flext-oracle-wms`, `flext-meltano`, `flext-target-oracle-wms`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle-wms/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle-wms/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
