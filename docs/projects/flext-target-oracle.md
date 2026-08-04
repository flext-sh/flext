# FLEXT Target Oracle

FLEXT Target Oracle is the Singer target that loads data into Oracle databases. It composes the FLEXT facades with
`flext-db-oracle` (Oracle connectivity) and `flext-meltano` (Singer target base) behind `r[T]` contracts and the
canonical `c/m/p/t/u` facade layout.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Status**: Active development on the `0.12.0-dev` branch; the package builds and exports its full public surface.
- **Description** (from `pyproject.toml`): "FLEXT Target Oracle - Singer Target for Oracle Database Data Loading"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-db-oracle`, `flext-meltano`
- **Console scripts**: `target-oracle` and `flext-target-oracle` (both bound to `flext_target_oracle.cli:main`)

### Quality signals

- Quality gates run through the workspace Make contract: `make check PROJECT=flext-target-oracle`, `make test
  PROJECT=flext-target-oracle`, and `make check`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

```bash
cd flext-target-oracle
poetry install
make check PROJECT=flext-target-oracle
```

Pipe Singer JSONL into the target through the console script:

```bash
tap-oracle --config tap.json | target-oracle --config target.json
```

Programmatic use via the public facade:

```python
from flext_target_oracle import FlextTargetOracleService, target_oracle

# target_oracle is the operational alias for FlextTargetOracleService.
# The service exposes create_sink, run_about, run_load, and run_validate;
# each command verb takes its typed command model and returns p.Result[str].
service = target_oracle()
```

## Architecture & modules

```text
src/flext_target_oracle/
├── api.py        # FlextTargetOracleService (target_oracle alias)
├── cli.py        # FlextTargetOracleCli + main entry point
├── _settings.py  # FlextTargetOracleSettings + settings singleton
├── config/       # Execution parametrization (YAML)
├── _constants/   # Private constants
├── _models/      # Private models
├── _protocols/   # Private protocols
├── _typings/     # Private typings
├── _utilities/   # Private utilities
├── constants.py  # c facade
├── models.py     # m facade
├── protocols.py  # p facade
├── typings.py    # t facade
└── utilities.py  # u facade (also exports FlextTargetOracle)
```

### Key architectural patterns

- **Meltano target service**: `FlextTargetOracleService` extends `FlextMeltanoTargetServiceBase` and implements
  `create_sink`, plus the operational verbs `run_about`, `run_load`, and `run_validate` that the CLI dispatches.
- **CLI composition**: `FlextTargetOracleCli.run_cli` parses arguments and returns `p.Result[str]`, with
  `finalize_cli_result` mapping the result to the process exit code.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_db_oracle`.
- **Result contracts**: fallible paths return `r[T]`; Oracle driver concerns stay inside `flext-db-oracle`, never in
  direct third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test PROJECT=flext-target-oracle`; Singer behavior is
  exercised through the CLI and sink flow.
- Pre-merge verification: `make check PROJECT=flext-target-oracle` (lint + typing + security selectors) and `make check`.

## Resources

- [Project README](../../flext-target-oracle/README.md)
- [Project docs portal](../../flext-target-oracle/docs/index.md)
- Related projects: `flext-db-oracle`, `flext-meltano`, `flext-tap-oracle`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-target-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-target-oracle/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
