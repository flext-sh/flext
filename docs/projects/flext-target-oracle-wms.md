# FLEXT Target Oracle WMS

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

FLEXT Target Oracle WMS (`flext-target-oracle-wms`) is the Singer target that loads data into Oracle WMS. It composes
the FLEXT facades with `flext-oracle-wms` (WMS connectivity), `flext-meltano` (Singer target base), and `flext-observability`
behind `r[T]` contracts and the canonical `c/m/p/t/u` facade layout. The package is a thin driver (ADR-006): all Singer
runtime plumbing comes from `flext-meltano`'s public `FlextMeltanoTargetServiceBase` via MRO; this package owns the
WMS-specific sink creation and transform logic in `_utilities/service_runtime.py`.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_oracle_wms` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-oracle-wms/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target Oracle WMS - Singer Target for Oracle WMS Data"
- **Dependencies**: `flext-cli`, `flext-core`, `flext-db-oracle`, `flext-meltano`, `flext-observability`,
  `flext-oracle-wms`
- **Console scripts**: `flext-target-oracle-wms` and `target-oracle-wms` (both bound to
  `flext_target_oracle_wms.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`, `make check`, `make test`.
  From the workspace root these fan out across every declared member; from within `flext-target-oracle-wms/` they apply
  to this package only.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

Provision the environment and run gates from the workspace root:

```bash
make setup
make check
make test
```

To run gates for this package only, invoke the selector-free per-project Makefile:

```bash
make -C flext-target-oracle-wms check
make -C flext-target-oracle-wms test
```

## Architecture & modules

```text
src/flext_target_oracle_wms/
├── api.py                # FlextTargetOracleWmsService(FlextMeltanoTargetServiceBase)
├── cli.py                # FlextTargetOracleWmsCli + main entry point
├── _utilities/
│   ├── client.py         # FlextTargetOracleWmsUtilitiesClient (CatalogManager, StreamProcessor, Target)
│   ├── helpers.py        # FlextTargetOracleWmsUtilitiesHelpers (WMSTableManager, WMSDataTransformer, etc.)
│   └── service_runtime.py  # FlextTargetOracleWmsServiceRuntime — WMS target + sink creation
├── _settings.py          # FlextTargetOracleWmsSettings + settings singleton
├── config/               # Execution parametrization (YAML)
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Thin-driver contract (ADR-006)**: `FlextTargetOracleWmsService` extends `FlextMeltanoTargetServiceBase` from
  `flext-meltano`, which provides the public Singer runtime via MRO. The package overrides only WMS-specific sink
  creation; every other concern (buffering, batch lifecycle, connection management) is inherited.
- **One canonical service path**: the service facade in `api.py` delegates sink creation to
  `FlextTargetOracleWmsServiceRuntime` in `_utilities/service_runtime.py`, which bridges the meltano sink abstraction
  to the WMS `Target` runtime in `FlextTargetOracleWmsUtilitiesClient`. No parallel `simple_api` branch.
- **WMS client utilities**: `FlextTargetOracleWmsUtilitiesClient` provides nested `CatalogManager`, `StreamProcessor`,
  and `Target` classes that handle SCHEMA/RECORD/STATE message dispatch, schema-to-table mapping, and data
  transformation through `flext-oracle-wms`.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_meltano`.
- **Result contracts**: fallible paths return `r[T]`; WMS API concerns stay inside `flext-oracle-wms`, never in direct
  third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free workspace Make verb).
  Singer behavior is exercised through the target CLI and sink flow.
- Pre-merge verification: `make check` (lint + typing + security gates) from the workspace root or
  `make -C flext-target-oracle-wms check` for this package only.

## Resources

- [Project README](../../flext-target-oracle-wms/README.md)
- [Project docs portal](../../flext-target-oracle-wms/docs/index.md)
- Related projects: `flext-oracle-wms`, `flext-db-oracle`, `flext-meltano`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
