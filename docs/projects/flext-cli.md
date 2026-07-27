# FLEXT CLI

FLEXT CLI is the command-line foundation of the FLEXT platform. It wraps Click, Rich, and Tabulate behind the FLEXT
facade/alias discipline so every downstream project shares the same CLI contracts, file helpers, prompt/format
utilities, and `r[T]` error handling. Package description: "FLEXT CLI — Developer Command Line Interface".

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+ only
- **Quality gate**: `make check PROJECT=flext-cli` (Ruff + type checks) and `make val` for the full pipeline
- **Depends on**: `flext-core` (facades, result contract, container)

### Quality signals

- Direct framework imports are confined to designated modules; consumers only see the `cli` facade
- Strict typing per workspace policy: no `Any`, no `cast` shortcuts
- Every fallible helper returns `r[T]`; callers branch on `.is_success`/`.is_failure`
- Facets `c`/`t`/`p`/`m` stay declaration-only (root `AGENTS.md` U17)

## Quick start

```bash
pip install flext-cli
```

Run the installed command's help first to discover the public commands exposed
by the current package build:

```bash
python -m flext_cli --help
```

Programmatic examples belong to the public API reference and must be generated
from the installed facade; this page intentionally does not advertise an
unverified convenience method.

## Architecture & modules

`src/flext_cli/` follows the FLEXT tiered layout:

- **Foundation**: `constants.py`, `typings.py`, `protocols.py` (+ `_constants/`, `_typings/`, `_protocols/`) — CLI-
  specific constants, type aliases, and protocols.
- **Domain**: `models.py` (`_models/`) — Pydantic v2 models for CLI payloads.
- **Services**: `services/` — `cli.py` (command definitions), `cmd.py` (command execution), `cli_params.py` (shared
  parameters), `file_tools.py` (JSON/YAML/CSV read/write, atomic writes), `formatters.py` (Rich-safe printing, panels,
  rules), `output.py`, `pipeline.py`, `prompts.py`, `rules.py`, `runtime.py`, `tables.py`.
- **Entry point**: `api.py` defines `FlextCli` as an MRO composition of `FlextCliAuth`, `FlextCliCli`, `FlextCliCmd`,
  `FlextCliCommonParams`, `FlextCliFileTools`, `FlextCliFormatters`, `FlextCliOutput`, `FlextCliPipeline`,
  `FlextCliPrompts`, `FlextCliRules`, `FlextCliRuntime`, and `FlextCliTables`; `__init__.py` exports it plus the
  standard aliases (`c`, `m`, `t`, `p`, `u`, `r`, `s`, `e`, `x`, `d`, `h`) and `config`/`settings`.

### Key architectural patterns

- **MRO facade**: one `FlextCli` class composed from service mixins — no standalone helpers, no proxy objects.
- **Framework containment**: Click/Rich/Tabulate are imported only inside the designated service modules; everything
  downstream consumes `cli.*`.
- **Railway discipline**: file tools and command services return `r[T]`, so CLI flows chain `.map`/`.flat_map` instead
  of try/except.
- **Config/settings SSOT**: runtime values come only from the validated `config`/`settings` singletons.

## Testing & quality

- `make check PROJECT=flext-cli`: Ruff linting plus type checks
- `make test PROJECT=flext-cli`: pytest suite (latest evidence under `reports/pytest/`)
- `make val`: full pipeline; see `reports/coverage-scan-*` for the current coverage snapshot
- Tests target the public `cli` facade surface only, per workspace testing law (U16)

## Resources

- [Project README](../../flext-cli/README.md) (auto-generated module map and operation flow)
- [Workspace AGENTS.md](../../AGENTS.md) — layering and zero-tolerance rules
- `flext-cli/docs/api-reference/` — generated API documentation
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-cli/issues>
- Follow the workspace `AGENTS.md` before proposing doc or code changes so this page stays aligned with the engineering
  portal.
