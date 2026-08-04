# FLEXT LDIF

FLEXT LDIF is the enterprise LDIF processing library of the FLEXT platform. It provides RFC-based LDIF parsing and
writing, a registry of server-specific dialect handlers (RFC, OID, OUD, OpenLDAP, Active Directory, 389 DS, Apache DS,
Novell, Tivoli, and a relaxed mode), and migration/conversion pipelines that move entries between server dialects
through a normalized RFC representation.

## Status & health

- **Version**: 0.12.0-dev
- **Python**: 3.13+ only
- **Project class**: domain (consumes `flext-core` and `flext-cli`)
- **Facade**: `from flext_ldif import ldif` — the process-wide `FlextLdif` singleton
- **Short aliases**: `c`, `m`, `p`, `r`, `t`, `u` plus operational `s`, `d`, `e`, `h`, `x`, and `settings`

### Quality signals

- Lint, type-check, security, and tests run through the canonical `make` verbs; current status is produced by the gates,
  not restated here.
- Run `make check PROJECT=flext-ldif` (lint + type-check) and `make check` for the full gate chain.

## Quick start

```bash
pip install flext-ldif
```

```python
from pathlib import Path

from flext_ldif import FlextLdifParser, ldif

parser = FlextLdifParser()
result = parser.parse_ldif_file(Path("directory.ldif"))
if result.success:
    u.Cli.print(f"Parsed {len(result.value.entries)} entries")
else:
    u.Cli.print(f"Parse failed: {result.error}")

migration = ldif.migrate(
    input_dir=Path("input"),
    output_dir=Path("output"),
    source_server="rfc",
    target_server="oid",
)
```

`FlextLdifParser.parse_ldif(...)` accepts either a string or a `Path` and returns `r[m.Ldif.ParseResponse]`;
`ldif.migrate(...)` builds a `FlextLdifMigrationPipeline` and executes it, returning
`r[m.Ldif.MigrationPipelineResult]`. Every fallible operation returns `r[T]`, so parsing, validation, filtering, and
migration compose with the same railway discipline.

## Architecture & modules

- **Facade**: `api.py` defines `FlextLdif`, composed by MRO over the service layer, and publishes the `ldif` singleton
  via `FlextLdif.fetch_global()`.
- **Service layer** (`services/`): `parser`, `writer`, `validation`, `entries`, `filters`, `categorization`,
  `statistics`, `analysis`, `detector`, `transformers`, `acl`, `processing`, `pipeline`, and the
  `conversion*`/`migration` services for server-to-server transforms.
- **Server registry** (`servers/`): one dialect module per server family (`rfc`, `relaxed`, `oid`, `oud`, `openldap`,
  `openldap1`, `ad`, `ds389`, `apache`, `novell`, `tivoli`) over a shared `base`, resolved by priority through the
  registry.
- **Private facets**: `_constants`, `_models`, `_protocols`, `_typings`, `_utilities` back the public `c/m/p/t/u`
  facades; execution parametrization lives in `config/ldif.yaml`, consumed through the SSOT `settings` access form.

### Key architectural patterns

- **RFC-first normalization**: dialect handlers convert entries to and from the RFC representation, so any N×N server
  conversion routes through a single canonical form.
- **Registry dispatch**: `ldif.resolve_server_bundle(...)`, `ldif.list_registered_servers()`, and
  `ldif.summarize_registry()` expose the registered dialects at runtime.
- **Pipeline composition**: `ldif.processing_pipeline(...)` and `ldif.migration_pipeline(...)` return configured
  pipeline objects executed via `.execute()`.
- **Pydantic 2-way models**: parse responses, migration results, and options are `m.Ldif.*` models that round-trip
  through `model_validate` / `model_dump`.

## Testing & quality

- `make check PROJECT=flext-ldif` — Ruff + type-check on the project lane.
- `make test PROJECT=flext-ldif` — unit and integration suites through the shared `flext-tests` helpers.
- `make check` — full workspace validation chain (lint, types, security, tests, docs).
- Typing is strict (no `Any`/`object`); all owned payloads are `m.Ldif.*` Pydantic models and all fallible paths return
  `r[T]`.

## Resources

- [Project README](../../flext-ldif/README.md)
- [Project catalog](generated/catalog.md) entry and generated API reference under `docs/api-reference/generated/flext-
  ldif.md`
- Project documentation under `flext-ldif/docs/` (getting started, API reference, architecture, guides)
- Related projects: `flext-core`, `flext-cli`, `flext-ldap`, `flext-tap-ldif`, `flext-target-ldif`, `flext-dbt-ldif`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-ldif/issues>
- Discussions: <https://github.com/flext-sh/flext-ldif/discussions>
- Follow the workspace `AGENTS.md` and the project's own `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the portal.
