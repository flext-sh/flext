# FLEXT Tap LDAP

FLEXT Tap LDAP (`flext-tap-ldap`) is the Singer tap that extracts LDAP directory entries — and, optionally, LDIF files —
into the FLEXT data mesh. It is built on `flext-ldap` for directory connectivity and `flext-meltano` for the Singer tap
contract, so discovery, catalog, and sync flows follow the Singer specification while every fallible operation returns
`r[T]`.

## Status & health

- **Version**: 0.12.0-dev (monorepo development cycle)
- **Python**: 3.13+
- **Package**: `flext_tap_ldap` (namespace package, `py.typed` shipped)
- **Location in this repo**: `flext-tap-ldap/` at the workspace root

### Quality signals

- Gates run through the workspace Make contract: `make check PROJECT=flext-tap-ldap`, `make test PROJECT=flext-tap-
  ldap`, `make check`.
- Strict typing per workspace `AGENTS.md`: no `Any`/`object`, Pydantic 2-way models, `r[T]` on every fallible path; LDAP
  access goes through `flext-ldap`, Singer orchestration through `flext-meltano`.
- No coverage or test-count metrics are asserted here; the gates above produce the authoritative numbers.

## Quick start

Console entry points: `tap-ldap` and `flext-tap-ldap`.

```bash
tap-ldap --config settings.json --discover > catalog.json
tap-ldap --config settings.json --catalog catalog.json --state state.json
```

Programmatically:

```python
from flext_tap_ldap import FlextTapLdapSettings, FlextTapLdapTap

settings = FlextTapLdapSettings()  # namespaced under settings.TapLdap.*
tap = FlextTapLdapTap()
streams = tap.discover_streams()
```

The `settings.TapLdap.*` group carries `host`, `port`, `use_ssl`, `timeout`, and `page_size` (validated Pydantic
fields).

## Architecture & modules

Source lives under `flext-tap-ldap/src/flext_tap_ldap/`:

- `tap.py` — `FlextTapLdapTap`, the Singer tap (built on `FlextMeltanoAbstractions`). `discover_streams()` yields the
  LDAP streams plus the LDIF streams; `execute()` runs the tap and returns a `p.Result`.
- `streams.py` — `FlextTapLdapStreams`, a unified namespace of nested stream classes: `UsersStream`, `GroupsStream`,
  `OrganizationalUnitsStream`, `SchemaStream`, over the shared `LDAPBaseStream` (paged LDAP reads through `flext-ldap`).
- `ldif_streams.py` — `FlextTapLdapLdifStreams` with `LdifStream` and `LdifAnalysisStream` for LDIF file extraction.
- `client.py` — `FlextTapLdapClient`, the directory client wrapper.
- `api.py` — `FlextTapLdapService` (a `FlextMeltanoTapServiceBase`), exported as the operational alias `tap_ldap`.
- `config/` — execution parametrization (SSOT per ADR-005).
- Canonical facet facades: `c`, `m`, `p`, `t`, `u`, plus `settings` (`FlextTapLdapSettings`); operational aliases `d`,
  `e`, `h`, `r`, `s`, `x` come from the parent chain (`flext_ldap`).

### Key architectural patterns

- One tap class and one service facade per package, composed by MRO over `flext-meltano` bases; streams are nested
  inside a single streams namespace per responsibility.
- Settings/config are the only parametrization source: `settings.TapLdap.*` is validated once at singleton construction.
- LDAP protocol access is never direct — it flows through `flext-ldap`; Singer protocol types come from `flext-meltano`
  models.

## Testing & quality

- Scoped suites run via `make check PROJECT=flext-tap-ldap` and `make test PROJECT=flext-tap-ldap`; full workspace
  validation is `make check`.
- Tests assert the public surface only (tap discovery/execution, exported models, stream behavior) per the workspace
  testing law.

## Resources

- [Project README](../../flext-tap-ldap/README.md)
- Source: `flext-tap-ldap/src/flext_tap_ldap/`
- Workspace governance: [AGENTS.md](../../AGENTS.md), [GOVERNANCE.md](../GOVERNANCE.md)
- Related packages: `flext-ldap`, `flext-ldif`, `flext-meltano`, `flext-core`, `flext-cli`, `flext-target-ldap`

## Support & issues

- Issues: <https://github.com/flext-sh/flext/issues>
- Follow the workspace `AGENTS.md` and the project README before editing code or docs so this page stays accurate.
