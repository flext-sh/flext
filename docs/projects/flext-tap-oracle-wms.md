# FLEXT Tap Oracle WMS

<!-- TOC START -->
- [Status & health](#status-health)
  - [Quality signals](#quality-signals)
- [Quick start](#quick-start)
- [Architecture & modules](#architecture-modules)
  - [Key architectural patterns](#key-architectural-patterns)
- [Testing & quality](#testing-quality)
- [Resources](#resources)
- [Support & issues](#support-issues)
<!-- TOC END -->

FLEXT Tap Oracle WMS is the Singer tap that extracts data from Oracle Warehouse Management System (WMS). It composes the
FLEXT facades with `flext-oracle-wms` (WMS connectivity) and `flext-meltano` (Singer tap base) behind `r[T]` contracts
and the canonical `c/m/p/t/u` facade layout.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Status**: Active development on the `0.12.0-dev` branch; current health is
  established by the root gates below, not by this page.
- **Description** (from `pyproject.toml`): "FLEXT Tap Oracle WMS - Singer Tap for Oracle Warehouse Management System"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-meltano`, `flext-oracle-wms`
- **Console scripts**: `tap-oracle-wms` and `flext-tap-oracle-wms` (both bound to `flext_tap_oracle_wms.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract:
  `make check`, `make test`, and `make build`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

From the workspace root, provision and validate with `make setup`, `make check`,
and `make test`.

Singer discovery and sync through the console script:

```bash
tap-oracle-wms --config settings.json --discover > catalog.json
tap-oracle-wms --config settings.json --catalog catalog.json --state state.json
```

Programmatic use via the public facade:

```python
from flext_tap_oracle_wms import tap_oracle_wms

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

- Tests live under the project `tests/` tree and run via root `make test`; Singer behavior is
  exercised through the tap CLI and discovery flow.
- Pre-merge verification uses root `make check`, `make test`, and `make build`.

## Resources

- [Project README](https://github.com/flext-sh/flext-tap-oracle-wms/blob/0.12.0-dev/README.md)
- [Project docs portal](https://github.com/flext-sh/flext-tap-oracle-wms/tree/0.12.0-dev/docs)
- Related projects: `flext-oracle-wms`, `flext-meltano`, `flext-target-oracle-wms`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle-wms/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle-wms/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
