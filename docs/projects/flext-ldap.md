# FLEXT LDAP

<!-- TOC START -->

- [Status & signals](#status-signals)
- [Quick start](#quick-start)
- [Architecture highlights](#architecture-highlights)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT LDAP (v0.10.3) is the universal directory-services foundation that every FLEXT project uses for LDAP operations. It wraps `ldap3`, FlextResult, and the flext-ldif converters in a clean architecture stack so teams can rely on server-specific implementations (OpenLDAP, Oracle OID/OUD, Active Directory, generic LDAP) without copying code.

## Status & signals

- **Version**: 0.10.3 (production ready)
- **Python**: 3.13+ only
- **Tests**: ~80+ unit/integration/e2e suites (42% coverage target; all existing suites pass) plus Docker-backed LDAP scenarios
- **Quality gate**: `make validate` (ruff, pyrefly, Bandit, type checks, tests, coverage, docstring checks); zero Ruff/MyPy/Pyrefly errors documented
- **Security**: Bandit reports zero high/medium findings in `reports/lint-output/*`
- **Type discipline**: no `Any`, `cast`, `TYPE_CHECKING`, or `# type: ignore`; strict layering ensures lower tiers never import higher

## Quick start

```bash
poetry add flext-ldap          # install for production
pip install flext-ldap         # also supported
```

Development flow:

```bash
git clone https://github.com/flext-sh/flext-ldap.git
cd flext-ldap
make setup                    # install deps, pre-commit hooks
make validate                 # run lint/type/security/test pipeline
```

Python usage:

```python
from flext_ldap import m

api = FlextLdap()
result = api.search_entries(
    m.SearchOptions(
        base_dn="dc=example,dc=com",
        filter_str="(objectClass=person)",
        scope="subtree",
        attributes=["uid", "cn", "mail"],
    ),
)

if result.is_success:
    for entry in result.unwrap():
        print(entry.dn.value)
else:
    raise RuntimeError(f"LDAP search failed: {result.error}")
```

Use `FlextLdapEntryAdapter` when converting between `ldap3` and `flext-ldif`, and call server-specific operations (`flext_ldap.servers.OpenLDAP2Operations`, `.OracleOIDOperations`, etc.) for schema discovery or ACL management.

## Architecture highlights

- **Layered modules**: Tier 0 (`constants.py`, `protocols.py`, `typings.py`), Tier 1 (`models`, `domain`, `utilities`), Tier 2 (`clients`, `entry_adapter`, `quirks_integration`, `servers/*`), Tier 3 (`services`, `handlers`, `api`). Each tier only imports lower tiers per CLAUDE rules.
- **FlextXxx namespaces**: every module exposes a single namespace class (`FlextLdapClients`, `FlextLdapModels`, `FlextLdapServices`, etc.) with nested helpers for authentication, search, ACLs, schema, and conversions.
- **Server implementations**: production-ready adapters for OpenLDAP 2.x/1.x, Oracle OID/OUD, Active Directory, plus a generic fallback and detector; operation facades live under `servers/` and are wired through `api.py`.
- **Integration points**: `flext-core` (FlextResult, container, logger, short aliases), `flext-ldif` (entry models, quirks, adapters), `flext-auth` (LDAP authentication provider), `flext-meltano`/Singer taps for data export, `flext-oud-mig` for Oracle migrations.
- **Clean architecture**: application → domain → infrastructure → protocol layers enforced by documentation, with zero duplication and architecture-specific best practices in `AGENTS.md`.

## Quality & operations

- **Testing**: `make test`, `make test-unit`, `make test-integration` (Docker LDAP server `flext-ldap-test-server`), `make test-fast`, `pytest -m ldap`, etc.
- **Validation**: `make lint`, `make type-check`, `make security`, `make coverage-html`, `make validate` ensures zero Ruff/MyPy/Pyrefly failures and enforces 42% coverage target toward 100%.
- **Zero‑tolerance rules**: no `TYPE_CHECKING`, no `.py` fixtures, no root aliases; constants files only hold StrEnum/Final/Literal; `cast()` forbidden, short alias usage mandated via `ruff-shared.toml` (PYI042 ignored globally).
- **Docker helpers**: `make ldap-start/stop/health/reset` manage the osixia/openldap:1.5.0 container for integration runs.

## Resources & references

- [Project README](../../flext-ldap/README.md)
- [CLAUDE instructions](../../flext-ldap/AGENTS.md) detailing layering, import rules, and zero-tolerance policies
- `flext-ldap/docs/` (architecture, API reference, development, configuration, testing, troubleshooting, guides) for deep dives
- Reports: `reports/pytest/*`, `reports/lint-output/*`, `reports/coverage-scan-*`
- Related projects: `flext-core`, `flext-ldif`, `flext-auth`, `flext-meltano`, `flext-oud-mig`

## Support & contributions

- Issues: <https://github.com/flext-sh/flext-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-ldap/discussions>
- Follow `docs/standards/README.md` and this project’s CLAUDE when changing code or docs so the portal stays aligned.
