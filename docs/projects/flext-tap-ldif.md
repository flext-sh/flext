# FLEXT Tap LDIF

FLEXT Tap LDIF (`flext-tap-ldif`) is the Singer tap that extracts records from LDIF files into the FLEXT data mesh.
Parsing and validation of the LDIF format are delegated to `flext-ldif`; Singer orchestration (discovery, catalog,
state, sync) is built on `flext-meltano`, and every fallible operation returns `r[T]`.

## Status & health

- **Version**: 0.12.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_tap_ldif` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-tap-ldif/` at the workspace root

### Quality signals

- Gates run through the workspace Make contract: `make check PROJECT=flext-tap-ldif`, `make test PROJECT=flext-tap-
  ldif`, `make val`.
- Strict typing per workspace `AGENTS.md`: no `Any`/`object`, Pydantic 2-way models, `r[T]` on every fallible path.
- No coverage or test-count metrics are asserted here; the gates above produce the authoritative numbers.

## Quick start

Console entry points: `tap-ldif` and `flext-tap-ldif` (plus `tap-ldif-legacy` for the legacy tap entry).

```bash
tap-ldif --config settings.json --discover > catalog.json
tap-ldif --config settings.json --catalog catalog.json --state state.json
```

Programmatically:

```python
from flext_tap_ldif import FlextTapLdif, FlextTapLdifService, FlextTapLdifSettings

settings = FlextTapLdifSettings()  # namespaced under settings.TapLdif.*
exit_code = FlextTapLdifService().cli_main()
```

The `settings.TapLdif.*` group carries `file_path` / `directory_path`, `file_pattern`, `encoding`, `strict_parsing`, and
`max_file_size_mb` (validated Pydantic fields).

## Architecture & modules

Source lives under `flext-tap-ldif/src/flext_tap_ldif/`:

- `tap.py` — `FlextTapLdif`, the Singer tap (extends `m.Meltano.SingerTapBase`); `discover_streams()` returns the LDIF
  entries stream with its JSON schema.
- `api.py` — `FlextTapLdifService` (a `FlextMeltanoTapServiceBase`), exported as the operational alias `tap_ldif`.
- `cli.py` — `FlextTapLdifCli` and the `main()` entry point, which route execution through the service facade.
- `_models/` — declaration-only Pydantic models: `entry`, `record`, `batch`, `file`, `file_metadata`, `file_stream`, and
  `settings`.
- `config/tap-ldif.yaml` — execution parametrization (SSOT per ADR-005).
- Canonical facet facades: `c`, `m`, `p`, `t`, `u`, plus `settings` (`FlextTapLdifSettings`); operational aliases `d`,
  `e`, `h`, `r`, `s`, `x` come from the parent chain (`flext_ldif`).

### Key architectural patterns

- Tap, service, and CLI each have a single canonical owner; the CLI never duplicates logic — it delegates to the service
  facade.
- LDIF syntax handling is never reimplemented: all parsing/validation flows through `flext-ldif`.
- Owned payloads (entries, records, batches, file metadata) are Pydantic models under `_models/`; settings/config are
  the only parametrization source (`settings.TapLdif.*`, validated once at singleton construction).

## Testing & quality

- Scoped suites run via `make check PROJECT=flext-tap-ldif` and `make test PROJECT=flext-tap-ldif`; full workspace
  validation is `make val`.
- Tests assert the public surface only (tap discovery, CLI exit codes, exported models) per the workspace testing law.

## Resources

- [Project README](../../flext-tap-ldif/README.md)
- Source: `flext-tap-ldif/src/flext_tap_ldif/`
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-ldif`, `flext-dbt-ldif`, `flext-target-ldif`, `flext-meltano`, `flext-core`, `flext-
  observability`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
