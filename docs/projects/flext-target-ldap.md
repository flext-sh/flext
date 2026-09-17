# FLEXT Target LDAP

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

FLEXT Target LDAP (`flext-target-ldap`) is the Singer target that loads records into LDAP directories. It consumes
Singer JSONL messages on stdin, resolves distinguished names, and writes entries through `flext-ldap`, composing the
FLEXT facades with `flext-meltano` (Singer target base) behind `r[T]` contracts. The package is a thin driver (ADR-006):
all Singer runtime plumbing comes from `flext-meltano`'s public `FlextMeltanoTargetServiceBase` and `FlextMeltanoTargetAbstractions`;
this package owns only the LDAP-specific sink and DN-construction logic.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_ldap` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-ldap/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target for LDAP directory loading"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldap`, `flext-meltano`
- **Console scripts**: `flext-target-ldap` (bound to `flext_target_ldap.target:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`, `make check`, `make test`.
  From the workspace root these fan out across every declared member; from within `flext-target-ldap/` they apply to
  this package only.
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
make -C flext-target-ldap check
make -C flext-target-ldap test
```

The target consumes Singer JSONL on stdin and echoes STATE lines to stdout. Run it from a Singer pipeline (for example
via Meltano) or programmatically:

```python

# target_ldap is the operational alias for FlextTargetLdap;
# config_class is FlextTargetLdapSettings.
# FlextTargetLdap.run_cli(settings_path) reads Singer JSONL from stdin.
```
## Architecture & modules

```text
src/flext_target_ldap/
├── api.py                # FlextTargetLdap target (target_ldap alias) + run_cli
├── target.py             # CLI entry point → FlextTargetLdap.run_cli()
├── application/          # FlextTargetLdapOrchestrator
├── _settings.py          # FlextTargetLdapSettings + settings singleton
├── config/               # Execution parametrization (YAML)
├── _constants/           # Private constants
├── _models/              # Private models incl. FlextTargetLdapSink
├── _utilities/           # Private utilities (client, etc.)
├── singer/               # Singer message parsing helpers
├── patterns/             # Processing patterns
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Thin-driver contract (ADR-006)**: `FlextTargetLdap` extends `FlextMeltanoTargetAbstractions` from `flext-meltano`,
  which provides the public Singer runtime. The package overrides only LDAP-specific sink selection and DN construction;
  every other concern (buffering, batch lifecycle, STATE/RECORD/SCHEMA dispatch) is inherited via MRO.
- **Singer target contract**: `FlextTargetLdap` binds `config_class = FlextTargetLdapSettings` and processes
  SCHEMA/RECORD/STATE messages through `run_cli` (bound as the `cli` class attribute), reading JSONL from stdin.
- **Orchestration**: `FlextTargetLdapOrchestrator` in `application/orchestrator.py` coordinates the load flow;
  sink classes in `_models/sinks.py` model sink state.
- **DN construction**: record messages are normalized into LDAP distinguished names before being handed to the `flext-
  ldap` client.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_ldap`.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free workspace Make verb).
  Singer behavior is exercised through the stdin JSONL contract.
- Pre-merge verification: `make check` (lint + typing + security gates) from the workspace root or
  `make -C flext-target-ldap check` for this package only.

## Resources

- [Project README](https://github.com/flext-sh/flext-target-ldap/blob/0.12.0-dev/README.md)
- [Project docs portal](https://github.com/flext-sh/flext-target-ldap/tree/0.12.0-dev/docs)
- Related projects: `flext-ldap`, `flext-ldif`, `flext-tap-ldap`, `flext-meltano`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-target-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-target-ldap/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
