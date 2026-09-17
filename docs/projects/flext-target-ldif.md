# FLEXT Target LDIF

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

FLEXT Target LDIF (`flext-target-ldif`) is the Singer target that writes LDIF output. It composes the FLEXT facades with
`flext-ldif` (LDIF serialization) and `flext-meltano` (Singer target base) behind `r[T]` contracts and the canonical
`c/m/p/t/u` facade layout. The package is a thin driver (ADR-006): all Singer runtime plumbing comes from `flext-meltano`'s
public `FlextMeltanoTargetServiceBase` via MRO.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Package**: `flext_target_ldif` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-target-ldif/` at the workspace root
- **Description** (from `pyproject.toml`): "FLEXT Target LDIF - Singer Target for LDAP Data Interchange Format (LDIF) output"
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldif`, `flext-meltano`, `flext-observability`
- **Console scripts**: `flext-target-ldif` and `target-ldif` (both bound to `flext_target_ldif.cli:main`)

### Quality signals

- Quality gates run through the selector-free workspace Make contract: `make setup`, `make check`, `make test`.
  From the workspace root these fan out across every declared member; from within `flext-target-ldif/` they apply to
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
make -C flext-target-ldif check
make -C flext-target-ldif test
```

## Architecture & modules

```text
src/flext_target_ldif/
├── api.py                # FlextTargetLdifService(FlextMeltanoTargetServiceBase)
├── cli.py                # FlextTargetLdifCli + main entry point
├── target.py             # FlextTargetLdif — config merge, output-dir creation, sink selection
├── writer.py             # FlextTargetLdifWriter — LDIF serialization (delegates to flext-ldif)
├── errors.py             # FlextTargetLdifWriterError
├── _settings.py          # FlextTargetLdifSettings + settings singleton
├── config/               # Execution parametrization (YAML)
├── _utilities/           # Private utilities (service_runtime)
├── constants.py          # c facade
├── models.py             # m facade
├── protocols.py          # p facade
├── typings.py            # t facade
└── utilities.py          # u facade
```

### Key architectural patterns

- **Thin-driver contract (ADR-006)**: `FlextTargetLdifService` extends `FlextMeltanoTargetServiceBase` from
  `flext-meltano`, which provides the public Singer runtime via MRO. The package overrides only LDIF-specific sink
  creation; every other concern (buffering, batch lifecycle, STATE/RECORD/SCHEMA dispatch) is inherited.
- **LDIF writer**: `FlextTargetLdifWriter` in `writer.py` handles LDIF serialization, delegating to `flext-ldif`.
  The `FlextTargetLdifServiceRuntime` in `_utilities/service_runtime.py` bridges the meltano sink abstraction to the
  LDIF writer.
- **Config merge**: `FlextTargetLdif` in `target.py` merges default settings, creates output directories, and selects
  sinks. Merged settings persist on `self._config` so sink/config code always reads the resolved payload.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, and `settings`,
  plus `d/e/h/r/s/x` re-exported from `flext_ldif`.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test` (selector-free workspace Make verb).
  Singer behavior is exercised through the target CLI and sink flow.
- Pre-merge verification: `make check` (lint + typing + security gates) from the workspace root or
  `make -C flext-target-ldif check` for this package only.

## Resources

- [Project README](../../flext-target-ldif/README.md)
- [Project docs portal](../../flext-target-ldif/docs/index.md)
- Related projects: `flext-ldif`, `flext-meltano`, `flext-core`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
