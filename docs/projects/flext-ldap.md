# FLEXT LDAP

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

FLEXT LDAP is the directory-services library of the FLEXT platform. It wraps `ldap3`
behind typed Pydantic models and the `r[T]` contract, providing connection management,
CRUD/search operations, entry synchronization, and server-type detection through a
single `FlextLdap` facade (`ldap` alias). Package description: "Enterprise LDAP
Operations Library for FLEXT Framework".

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+ only
- **Quality gate**: selector-free root `make check`, `make test`, and `make build`
- **Depends on**: `flext-core`, `flext-ldif` (entry models and LDIF conversion)

### Quality signals

- `ldap3` imports are contained in the adapter layer; consumers work with `m.Ldap.*`
  models only
- Strict typing per workspace policy: no `Any`, no `cast` shortcuts
- Every public operation returns `r[T]` with consistent error handling
- Facets `c`/`t`/`p`/`m` stay declaration-only (root `AGENTS.md` U17)

## Quick start

```bash
pip install flext-ldap
```

```python
from flext_ldap import FlextLdap, m, settings

api = FlextLdap()
connection = m.Ldap.ConnectionConfig(
    host=settings.Ldap.host,
    port=settings.Ldap.port,
    use_ssl=settings.Ldap.use_ssl,
    use_tls=settings.Ldap.use_tls,
    bind_dn=settings.Ldap.bind_dn,
    bind_password=settings.Ldap.bind_password,
    timeout=settings.Ldap.timeout,
    auto_bind=settings.Ldap.auto_bind,
    auto_range=settings.Ldap.auto_range,
)

try:
    api.connect(connection).unwrap()
    options = m.Ldap.SearchOptions.base_scope(settings.Ldap.bind_dn)
    result = api.search(options).unwrap()
    for entry in result.entries:
        print(entry.dn)
finally:
    api.disconnect()
```

This requires a real directory, a nonempty configured bind DN, and authorization
to read that entry. Connection inputs come from typed `settings.Ldap`; the model
factory owns the base-scope request. No synthetic directory or silent success
branch replaces a real bind and search. Cleanup runs even on failure.

`ldap` is the process-wide `FlextLdap` singleton (`FlextLdap.fetch_global()`);
`m.Ldap.SearchOptions` defaults `scope` and `filter_str` to the constants in `c.Ldap`.
Use `FlextLdapEntryAdapter` to convert between `ldap3` entries and `flext-ldif` models.

## Architecture & modules

`src/flext_ldap/` follows the FLEXT tiered layout:

- **Foundation**: `constants.py`, `typings.py`, `protocols.py` — LDAP defaults (ports,
  scopes, filters), type aliases, and protocols.
- **Domain**: `models.py` (`_models/`) — Pydantic v2 models: `ConnectionConfig`,
  `SearchOptions`, `SearchResult`, and operation results.
- **Adapters**: `adapters/` — `ldap3.py` (`_ldap3/`) wraps the `ldap3` library;
  `entry.py` (`FlextLdapEntryAdapter`) converts entries to/from `flext-ldif` models.
- **Services**: `services/` — `connection.py` (connect/disconnect with optional retry
  and post-bind server detection), `operations.py` (`add`, `modify`, `delete`, `search`,
  `upsert`, `batch_upsert`), `detection.py` (`FlextLdapServerDetector`), `sync.py`
  (`FlextLdapSync`), `api_runtime.py`.
- **Entry point**: `api.py` defines
  `FlextLdap(FlextLdapConnection, FlextLdapSync, FlextLdapApiRuntime)` via MRO;
  `__init__.py` exports the facade plus the standard aliases and `config`/`settings`.

### Key architectural patterns

- **Adapter containment**: all `ldap3` interaction lives in `adapters/ldap3.py`; the
  rest of the package is transport- agnostic.
- **MRO facade**: connection lifecycle, sync, and runtime behavior compose into one
  `FlextLdap` class — no standalone helpers.
- **Server detection**: after a successful bind, `FlextLdapServerDetector` identifies
  the server type so operations can apply server-specific behavior.
- **Config/settings SSOT**: host/port defaults come from `FlextLdapSettings` (env prefix
  `FLEXT_LDAP_`) and `c.Ldap.*` constants.

## Testing & quality

- `make check`: lint, typing, security, and structural checks
- `make test`: pytest suite through the shared Testmon cache
- `make build`: package candidate; runtime proof remains separate
- Tests target the public facade and exported models only, per workspace testing law
  (U16)

## Resources

- [Project README](https://github.com/flext-sh/flext-ldap/blob/0.12.0-dev/README.md)
  (auto-generated module map and operation flow)
- [Workspace AGENTS.md](https://github.com/flext-sh/flext/blob/0.12.0-dev/AGENTS.md) —
  layering and zero-tolerance rules
- `flext-ldap/docs/api-reference/` — generated API documentation
- Related projects: `flext-core`, `flext-ldif`, `flext-auth` (LDAP auth provider)
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-ldap/issues>
- Follow the workspace `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the engineering portal.
