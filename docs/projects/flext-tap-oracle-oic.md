# FLEXT Tap Oracle OIC

FLEXT Tap Oracle OIC is the Singer tap that extracts integrations, connections, packages, and related entities from
Oracle Integration Cloud (OIC). It composes the FLEXT facades with `flext-oracle-oic` (OIC connectivity) and `flext-
meltano` (Singer tap base) behind `r[T]` contracts and the canonical `c/m/p/t/u` facade layout.

## Status & health

- **Version**: 0.20.0-dev (current development cycle)
- **Python**: 3.13+
- **Status**: Active development on the `0.20.0-dev` branch; the package builds and exports its full public surface.
- **Description** (from `pyproject.toml`): "FLEXT Tap Oracle OIC - Singer Tap for Oracle Integration Cloud"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-meltano`, `flext-oracle-oic`
- **Console scripts**: `tap-oracle-oic` and `flext-tap-oracle-oic` (both bound to
  `flext_tap_oracle_oic.tap:TapOracleOic.cli`)

### Quality signals

- Quality gates run through the workspace Make contract: `make check PROJECT=flext-tap-oracle-oic`, `make test
  PROJECT=flext-tap-oracle-oic`, and `make val`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

```bash
cd flext-tap-oracle-oic
poetry install
make check PROJECT=flext-tap-oracle-oic
```

Singer discovery and sync through the console script:

```bash
tap-oracle-oic --config settings.json --discover > catalog.json
tap-oracle-oic --config settings.json --catalog catalog.json --state state.json
```

Programmatic use via the public facade:

```python
from flext_tap_oracle_oic import FlextTapOracleOicService, tap_oracle_oic

# tap_oracle_oic is the operational alias for FlextTapOracleOicService
service = tap_oracle_oic()
```

## Architecture & modules

```text
src/flext_tap_oracle_oic/
├── api.py           # FlextTapOracleOicService (tap_oracle_oic alias)
├── cli.py           # FlextTapOracleOicCli + main entry point
├── tap.py           # FlextTapOracleOic, FlextTapOracleOicClient, FlextOracleOicAuthenticator
├── tap_streams.py   # FlextTapOracleOicPaginator
├── _settings.py     # FlextTapOracleOicSettings + settings singleton
├── config/          # Execution parametrization (YAML)
├── _models/         # Private models incl. stream definitions (ALL_STREAMS)
├── constants.py     # c facade
├── models.py        # m facade
├── protocols.py     # p facade
├── typings.py       # t facade
└── utilities.py     # u facade
```

### Key architectural patterns

- **Meltano tap service**: `FlextTapOracleOicService` extends `FlextMeltanoTapServiceBase`, which provides CLI dispatch
  (`cli_main`), catalog discovery (`run_discover`), sync execution (`run_sync`), and connection lifecycle via MRO. This
  tap overrides `create_tap_instance` to raise `TypeError` on purpose: it dispatches through the CLI instead of a
  `singer_sdk.Tap` instance.
- **Dynamic stream discovery**: `FlextTapOracleOic.discover_oic_streams()` builds stream instances from `ALL_STREAMS`,
  the stream-name → stream-class mapping in `_models/streams.py`. The mapping currently covers integrations,
  connections, packages, lookups, libraries, certificates, adapters, projects, executions, and metrics.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_oracle_oic`.
- **Result contracts**: fallible paths return `r[T]`; HTTP concerns stay inside `flext-oracle-oic` and `flext-meltano`,
  never in direct third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test PROJECT=flext-tap-oracle-oic`; Singer behavior is
  exercised through the tap CLI and discovery flow.
- Pre-merge verification: `make check PROJECT=flext-tap-oracle-oic` (lint + typing + security selectors) and `make val`.

## Resources

- [Project README](../../flext-tap-oracle-oic/README.md)
- [Project docs portal](../../flext-tap-oracle-oic/docs/index.md)
- Related projects: `flext-oracle-oic`, `flext-meltano`, `flext-target-oracle-oic`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-tap-oracle-oic/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-oracle-oic/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
