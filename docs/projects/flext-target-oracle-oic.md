# FLEXT Target Oracle OIC

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

FLEXT Target Oracle OIC (`flext-target-oracle-oic`) is the Singer target that loads data
into Oracle Integration Cloud (OIC). It composes the FLEXT facades with
`flext-oracle-oic` (OIC connectivity) and `flext-meltano` (Singer target base) behind
`r[T]` contracts and the canonical `c/m/p/t/u` facade layout. The package is a thin
driver (ADR-006): all Singer runtime plumbing comes from `flext-meltano`'s public
`FlextMeltanoTargetServiceBase` via MRO; this package owns the named
OIC-stream-to-dedicated-sink mapping.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_oracle_oic` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-oracle-oic/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target Oracle OIC - Singer Target for
  Oracle Integration Cloud"
- **Dependencies**: `flext-api`, `flext-cli`, `flext-core`, `flext-db-oracle`,
  `flext-meltano`, `flext-observability`, `flext-oracle-oic`
- **Console scripts**: `flext-target-oracle-oic` and `target-oracle-oic` (both bound to
  `flext_target_oracle_oic.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`,
  `make check`, `make test`. From the workspace root these fan out across every declared
  member; from within `flext-target-oracle-oic/` they apply to this package only.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy,
  pyright); consult the gate output rather than static claims in this page.

## Quick start

Provision the environment and run gates from the workspace root:

```bash
make setup
make check
make test
```

To run gates for this package only, invoke the selector-free per-project Makefile:

```bash
make -C flext-target-oracle-oic check
make -C flext-target-oracle-oic test
```

## Architecture & modules

```text
src/flext_target_oracle_oic/
├── api.py                # FlextTargetOracleOicService(FlextMeltanoTargetServiceBase)
├── target.py             # FlextTargetOracleOic(FlextMeltanoTargetAbstractions) —
per-stream OIC sinks
├── cli.py                # FlextTargetOracleOicCli + main entry point
├── _settings.py          # FlextTargetOracleOicSettings + settings singleton
├── config/               # Execution parametrization (YAML)
├── _utilities/           # Private utilities (service_runtime)
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Thin-driver contract (ADR-006)**: `FlextTargetOracleOicService` extends
  `FlextMeltanoTargetServiceBase` from `flext-meltano`, which provides the public Singer
  runtime via MRO. The package overrides only OIC-specific sink creation; every other
  concern (buffering, batch lifecycle, connection management) is inherited.
- **Named stream sinks**: `FlextTargetOracleOic` in `target.py` maps named OIC streams
  (connections, integrations, packages, lookups) to dedicated sink classes
  (`FlextTargetOracleOicConnectionsSink`, `FlextTargetOracleOicIntegrationsSink`,
  `FlextTargetOracleOicPackagesSink`, `FlextTargetOracleOicLookupsSink`). The
  `FlextTargetOracleOicServiceRuntime` in `_utilities/service_runtime.py` bridges the
  meltano sink abstraction to the OIC sink classes.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`,
  `p`, `t`, `u`, and `settings`, plus `d/e/h/r/s/x` re-exported from `flext_oracle_oic`.
- **Result contracts**: fallible paths return `r[T]`; OIC API concerns stay inside
  `flext-oracle-oic`, never in direct third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free
  workspace Make verb). Singer behavior is exercised through the target CLI and sink
  flow.
- Pre-merge verification: `make check` (lint + typing + security gates) from the
  workspace root or `make -C flext-target-oracle-oic check` for this package only.

## Resources

- [Project README](https://github.com/flext-sh/flext-target-oracle-oic/blob/0.12.0-dev/README.md)
- [Project docs portal](https://github.com/flext-sh/flext-target-oracle-oic/tree/0.12.0-dev/docs)
- Related projects: `flext-oracle-oic`, `flext-meltano`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or
  code.
