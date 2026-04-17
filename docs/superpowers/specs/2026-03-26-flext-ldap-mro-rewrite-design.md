# ldap MRO Rewrite — Design Spec

**Date**: 2026-03-26
**Scope**: flext-ldap + all 4 production consumers (flext-tap-ldap, flext-target-ldap, flext-dbt-ldap, algar-oud-mig)
**Pattern**: cli MRO composition (Option C)

## Goal

Rewrite ldap from constructor-injection to MRO-based composition. Services become mixins on a single class. Consumers instantiate `ldap()` with zero ceremony. All code passes ruff, pyrefly, pytest with zero errors.

## Architecture

### New MRO Chain

```python
class ldap(
    FlextLdapConnection,  # connect(), disconnect(), is_connected, detect_server_type()
    FlextLdapOperations,  # add(), delete(), modify(), search(), upsert(), batch_upsert()
    FlextLdapSync,  # sync_phase_entries(), sync_multiple_phases()
):
    """MRO facade for all LDAP operations."""

    @override
    def execute(self) -> p.Result[m.Ldap.SearchResult]: ...
```

### Service Mixin Design

Each mixin inherits from `FlextLdapServiceBase`:

**FlextLdapConnection** (services/connection.py):

- u.PrivateAttr: `_adapter: FlextLdapLdap3Adapter`, `_ldif: ldif`
- Lazy adapter init on first `connect()` call
- Properties: `is_connected`, `adapter`
- Methods: `connect()`, `disconnect()`, `detect_server_type()`
- Server detection absorbed from detection.py

**FlextLdapOperations** (services/operations.py):

- u.PrivateAttr: `_upsert_handler`
- Accesses adapter via `self._adapter` (shared MRO)
- Methods: `add()`, `delete()`, `modify()`, `search()`, `upsert()`, `batch_upsert()`
- Inner classes: `EntryComparison`, `_UpsertHandler` (unchanged)

**FlextLdapSync** (new file or absorbed into api.py):

- No state — uses `self.search()`, `self.batch_upsert()` from Operations mixin
- Methods: `sync_phase_entries()`, `sync_multiple_phases()`
- Callback helpers: `FlextLdapSyncCallbacks` (inner class)

### Consumer Usage

```python
from flext_ldap import ldap as ldap, c, m, t, p, u

client = ldap()
with client:
    client.connect(m.Ldap.ConnectionSettings(host="ldap.example.com"))
    result = client.search(m.Ldap.SearchOptions(base_dn="dc=example,dc=com"))
```

## Bug Fixes (root cause)

| Bug                                             | Fix                                               |
| ----------------------------------------------- | ------------------------------------------------- |
| `u.Ldif.norm_string` (doesn't exist)            | `u.Ldif.norm()` in operations.py:1223, api.py:583 |
| `parser.parse_ldap3_results` (missing)          | Find correct method or implement on adapter       |
| `MULTI_PHASE_CALLBACK_PARAM_COUNT` not exported | Move to `c.Ldap.*` constants (SSOT)               |

## Files Changed

### flext-ldap/src/

- `api.py` — MRO facade (rewrite)
- `base.py` — FlextLdapServiceBase (unchanged or minimal)
- `services/connection.py` — MRO mixin (rewrite from standalone service)
- `services/operations.py` — MRO mixin (rewrite from standalone, fix norm_string)
- `services/sync.py` → `.bak` (absorbed into api.py or new sync mixin)
- `services/detection.py` → absorbed into connection.py
- `__init__.py` — Update exports (remove FlextLdapConnection/Operations from public)
- `constants.py` — Add callback param count constants to c.Ldap

### flext-ldap/tests/

- All unit tests updated to `ldap()` pattern
- Remove ceremony (no more separate connection/operations creation)
- Fix test_api.py imports
- Fix test_operations.py norm_string failure

### Consumers (4 production)

- `flext-tap-ldap/src/flext_tap_ldap/client.py`
- `flext-target-ldap/src/flext_target_ldap/client.py`
- `flext-target-ldap/src/flext_target_ldap/target_client.py`
- `flext-dbt-ldap/src/flext_dbt_ldap/dbt_client.py`
- `algar-oud-mig/` — update to ldap() direct usage

## Quality Gates

Per every file edit:

1. `ruff check` — 0 errors
2. `pyrefly check` — 0 errors
3. `pytest` (affected tests) — 0 failures

## Out of Scope

- ldif MRO rewrite (separate phase)
- flext-core changes
- New features on ldap
