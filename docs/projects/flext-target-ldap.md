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

FLEXT Target LDAP (`flext-target-ldap`) is the Singer target that loads records into
LDAP directories. It consumes Singer JSONL messages on stdin, resolves distinguished
names, and writes entries through `flext-ldap`, composing the FLEXT facades with
`flext-meltano` behind `r[T]` contracts. It is a thin driver (ADR-006, amended
2026-10-25): `FlextTargetLdap` subclasses `FlextMeltanoTargetServiceBase` and declares
only `target_name` and `sink_factory`.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_ldap` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-ldap/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target for LDAP directory loading"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldap`, `flext-meltano`
- **Console scripts**: `flext-target-ldap` (bound to `flext_target_ldap.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`,
  `make check`, `make test`. From the workspace root these fan out across every declared
  member; from within `flext-target-ldap/` they apply to this package only.
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
make -C flext-target-ldap check
make -C flext-target-ldap test
```

The target consumes Singer JSONL on stdin through the `flext-meltano` router. Run it
from a Singer pipeline (for example via Meltano) or programmatically:

```python
# FlextTargetLdap().cli_main() drains Singer JSONL from stdin and returns 0;
# any failed message raises SystemExit(1).
```

## Architecture & modules

```text
src/flext_target_ldap/
├── api.py                # FlextTargetLdap: target_name + sink_factory binding
├── cli.py                # console entry point → FlextTargetLdap().cli_main()
├── services/client.py    # FlextTargetLdapClient: concrete flext-ldap adapter
├── services/sinks.py     # FlextTargetLdapSinks: profile-driven sink + create_sink
├── _settings.py          # FlextTargetLdapSettings + settings singleton
├── config/               # Stream entry profiles (YAML business rules)
├── _constants/           # Private constants
├── _models/              # Private models incl. stream entry profiles
├── _protocols/           # p.TargetLdap.Directory and sink contracts
├── _utilities/           # u.TargetLdap: profile, entry and value mapping
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Thin driver (ADR-006)**: `FlextTargetLdap` declares `target_name` and binds
  `sink_factory` to `FlextTargetLdapSinks.create_sink` with the concrete directory
  client. The base provides `cli_main`, SCHEMA/RECORD/STATE dispatch through
  `u.Meltano.process_stdin`, the sink registry, and flushing.
- **Directory injection**: sinks consume the `p.TargetLdap.Directory` protocol
  (add, modify, delete). `api.py` is the only module that names
  `FlextTargetLdapClient` (operator order 2026-10-25, tracker key
  `operator-order-2026-10-25-servers-di-never-registry`).
- **One profile-driven sink**: every stream uses the same sink class. The stream's
  entry profile in `config/target-ldap.yaml` declares the RDN attribute, identity
  fields, object classes, and field mapping; undeclared streams use the declared
  default profile.
- **Write semantics**: an explicit `dn` wins; the sink adds the entry, modifies it on a
  DN repeated in the run, and deletes it when `_sdc_deleted_at` is set. A failed add is
  modified only when `update_existing_entries` is true.
- **Failure behavior (changed 2026-10-25)**: a RECORD without `stream`, a line that is
  not valid JSON, and a RECORD whose `record` is not a mapping all fail. Failures
  surface as `r.fail` through the base drain and `cli_main` exits with status 1. STATE
  flushes every sink. Blank lines and non-object JSON lines are skipped by the
  `flext-meltano` router. The console script reads no configuration-file argument.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`,
  `p`, `t`, `u`, and `settings`, plus `d/e/h/r/s/x` re-exported from `flext_ldap`.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free
  workspace Make verb). Singer behavior is exercised through the stdin JSONL contract.
- Pre-merge verification: `make check` (lint + typing + security gates) from the
  workspace root or `make -C flext-target-ldap check` for this package only.

## Resources

- [Project README](https://github.com/flext-sh/flext-target-ldap/blob/0.12.0-dev/README.md)
- [Project docs portal](https://github.com/flext-sh/flext-target-ldap/tree/0.12.0-dev/docs)
- Related projects: `flext-ldap`, `flext-ldif`, `flext-tap-ldap`, `flext-meltano`,
  `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-target-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-target-ldap/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or
  code.
