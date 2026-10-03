# FLEXT Target Oracle

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

FLEXT Target Oracle (`flext-target-oracle`) is the Singer target that loads data into
Oracle databases. It composes the FLEXT facades with `flext-db-oracle` (Oracle
connectivity) and `flext-meltano` (Singer target base) behind `r[T]` contracts and the
canonical `c/m/p/t/u` facade layout. The package is a thin driver (ADR-006): all Singer
runtime plumbing comes from `flext-meltano`'s public `FlextMeltanoTargetServiceBase`;
this package owns the Oracle-specific loader pattern and CQRS command surfaces.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_oracle` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-oracle/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target Oracle - Singer Target for
  Oracle Database Data Loading"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-db-oracle`, `flext-meltano`
- **Console scripts**: `target-oracle` and `flext-target-oracle` (both bound to
  `flext_target_oracle.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`,
  `make check`, `make test`. From the workspace root these fan out across every declared
  member; from within `flext-target-oracle/` they apply to this package only.
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
make -C flext-target-oracle check
make -C flext-target-oracle test
```

Pipe Singer JSONL into the target through the console script:

```bash
tap-oracle --config tap.json | target-oracle --config target.json
```

Programmatic use via the public facade:

```python
from flext_target_oracle import target_oracle

# target_oracle is the operational alias for FlextTargetOracleService.
# The service exposes run_about, run_load, and run_validate;
# each command verb takes its typed command model and returns p.Result[str].
service = target_oracle()
```

## Architecture & modules

```text
src/flext_target_oracle/
├── api.py            # FlextTargetOracleService (target_oracle alias)
├── cli.py            # FlextTargetOracleCli + main entry point
├── _settings.py      # FlextTargetOracleSettings + settings singleton
├── config/           # Execution parametrization (YAML)
├── _constants/       # Private constants
├── _models/          # Private models (commands DTOs, singer messages, results)
├── _protocols/       # Private protocols
├── _typings/         # Private typings
├── _utilities/       # Private utilities (loader, client, errors, observability, services)
├── constants.py      # c facade
├── models.py         # m facade
├── protocols.py      # p facade
├── typings.py        # t facade
└── utilities.py      # u facade (also exports FlextTargetOracle)
```

### Key architectural patterns

- **Thin-driver contract (ADR-006)**: `FlextTargetOracleService` extends
  `FlextMeltanoTargetServiceBase` from `flext-meltano`, which provides the public Singer
  runtime via MRO. The package overrides only Oracle-specific command verbs; every other
  concern (buffering, batch lifecycle, connection management) is inherited.
- **CQRS loader pattern**: `create_sink` intentionally raises — this target uses a
  loader pattern via `FlextTargetOracleLoader` in `_utilities/loader.py`, which
  delegates Oracle access exclusively to `flext-db-oracle`. Command models in
  `_models/commands.py` are pure data; execution lives in the service and loader.
- **CLI composition**: `FlextTargetOracleCli.run_cli` parses arguments and returns
  `p.Result[str]`, with `finalize_cli_result` mapping the result to the process exit
  code.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`,
  `p`, `t`, `u`, and `settings`, plus `d/e/h/r/s/x` re-exported from `flext_db_oracle`.
- **Result contracts**: fallible paths return `r[T]`; Oracle driver concerns stay inside
  `flext-db-oracle`, never in direct third-party imports.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free
  workspace Make verb). Singer behavior is exercised through the CLI and sink flow.
- Pre-merge verification: `make check` (lint + typing + security gates) from the
  workspace root or `make -C flext-target-oracle check` for this package only.

## Resources

- [Project README](https://github.com/flext-sh/flext-target-oracle/blob/0.12.0-dev/README.md)
- [Project docs portal](https://github.com/flext-sh/flext-target-oracle/tree/0.12.0-dev/docs)
- Related projects: `flext-db-oracle`, `flext-meltano`, `flext-tap-oracle`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-target-oracle/issues>
- Discussions: <https://github.com/flext-sh/flext-target-oracle/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or
  code.
