# FLEXT Target LDAP

FLEXT Target LDAP is the Singer target that loads records into LDAP directories. It consumes Singer JSONL messages on
stdin, resolves distinguished names, and writes entries through `flext-ldap`, composing the FLEXT facades with `flext-
meltano` (Singer target base) behind `r[T]` contracts.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Status**: Active development on the `0.12.0-dev` branch; the package builds and exports its full public surface.
- **Description** (from `pyproject.toml`): "FLEXT Target for LDAP directory loading"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldap`, `flext-meltano`

### Quality signals

- Quality gates run through the workspace Make contract: `make check PROJECT=flext-target-ldap`, `make test
  PROJECT=flext-target-ldap`, and `make check`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

```bash
cd flext-target-ldap
poetry install
make check PROJECT=flext-target-ldap
```

The target consumes Singer JSONL on stdin and echoes STATE lines to stdout. Run it from a Singer pipeline (for example
via Meltano) or programmatically:

```python
from flext_target_ldap import FlextTargetLdap, target_ldap

# target_ldap is the operational alias for FlextTargetLdap;
# config_class is FlextTargetLdapSettings.
# FlextTargetLdap.run_cli(settings_path) reads Singer JSONL from stdin.
```

## Architecture & modules

```text
src/flext_target_ldap/
├── api.py                # FlextTargetLdap target (target_ldap alias) + run_cli
├── target.py             # Target wiring
├── application/          # FlextTargetLdapOrchestrator
├── _settings.py          # FlextTargetLdapSettings + settings singleton
├── config/               # Execution parametrization (YAML)
├── _constants/           # Private constants
├── _models/              # Private models incl. FlextTargetLdapSink
├── _utilities/           # Private utilities
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Singer target contract**: `FlextTargetLdap` binds `config_class = FlextTargetLdapSettings`, resolves sinks per
  stream via `get_sink_class`, and processes SCHEMA/RECORD/STATE messages through `run_cli` (bound as the `cli` class
  attribute).
- **Orchestration**: `FlextTargetLdapOrchestrator` in `application/orchestrator.py` coordinates the load flow;
  `FlextTargetLdapSink` in `_models/sinks.py` models sink state.
- **DN construction**: record messages are normalized into LDAP distinguished names before being handed to the `flext-
  ldap` client.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_ldap`.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test PROJECT=flext-target-ldap`; Singer behavior is
  exercised through the stdin JSONL contract.
- Pre-merge verification: `make check PROJECT=flext-target-ldap` (lint + typing + security selectors) and `make check`.

## Resources

- [Project README](../../flext-target-ldap/README.md)
- [Project docs portal](../../flext-target-ldap/docs/index.md)
- Related projects: `flext-ldap`, `flext-ldif`, `flext-tap-ldap`, `flext-meltano`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-target-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-target-ldap/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
