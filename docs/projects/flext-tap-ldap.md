# FLEXT Tap LDAP

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & patterns](#architecture-patterns)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Tap LDAP v1.0.0 (release preparation) is the Singer tap that streams LDAP directory and LDIF data into the FLEXT data mesh. It combines stringent flext-core, flext-ldap, and flext-meltano integrations with Clean Architecture and Singer compliance so every extraction workflow is reusable and testable.

## Status & health

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+
- **Tests**: ~339+ unit/integration/e2e methods; the README reports 90%+ coverage and all suites pass in the blocked validation pipeline
- **Quality gates**: `make check`, `make test`, and `make val` are the current project gates; use `make check CHECK_GATES=...` when you need a narrower lint, type, or security pass
- **Dependencies**: `flext-core`, `flext-cli`, `flext-ldap`, `flext-meltano`, Singer SDK, `dbt`/Meltano workflows
- **Zero tolerance**: no direct `singer-sdk`, `ldap3`, or Click/Rich imports; everything flows through the mandated projects and returns `r[T]`

## Quick start

```bash
poetry add flext-tap-ldap
# or for development
git clone https://github.com/flext-sh/flext-tap-ldap.git
cd flext-tap-ldap
make setup
make check
make test
make val
```

```bash
tap-ldap --config settings.json --discover > catalog.json
tap-ldap --config settings.json --catalog catalog.json --state state.json
```

Configuration reference and example JSON live under `docs/` and the README (host, bind credentials, LDIF toggles, custom streams, page sizing, etc.).

## Architecture & patterns

- **Clean Architecture**: Domain (`domain/`), application (`application/`), infrastructure (`infrastructure/`), and protocol (`streams.py`, `ldif_stream.py`) layers; only lower tiers import via short aliases (`m`, `u`, `r`).
- **Singer streams**: Users, Groups, OrganizationalUnits, Schema, Custom, LDIF, and LDIFAnalysis streams all implement Singer tap contracts while converting LDAP/LDIF entries through `r` orchestrators.
- **Configuration models**: `settings.py` exposes Pydantic `FlextTapLdapSettings` with strict validation, including LDAP connection settings, LDIF toggles, Melro (Meltano) integration, and security tokens.
- **Zero tolerance governance**: `AGENTS.md` enforces mandatory usage of `flext-ldap`, `flext-meltano`, `flext-core`, and `flext-cli`; forbids direct `ldap3`, `singer-sdk`, `click`, `rich`, `Any`, `cast`, or `TYPE_CHECKING`.

## Quality & operations

- **Validation pipeline**: `make check`, `make test`, and `make val` are the current standard gates; use `CHECK_GATES=` selectors on `make check` when you need a narrower lint, type, or security run.
- **Testing organization**: `tests/e2e/ldif`, `tests/test_client.py`, `tests/test_streams.py`, `tests/test_tap.py`, integration groups, and Docker-based LDAP testing (`make ldap-test`) support 90% coverage.
- **Singer commands**: `make discover`, `make catalog`, `make run`, `make sync`, and `make validate-config` align with the tap-specific flows defined in `custom.mk`.
- **LDAP helpers**: `make ldap-test`, `make ldap-discover`, `make ldap-query`, plus Docker Compose `openldap` for local integration.

## Resources & references

- [Project README](../../flext-tap-ldap/README.md) for narrative, features, and configuration
- [Project AGENTS.md](../../flext-tap-ldap/AGENTS.md) for zero-tolerance policies and command conventions
- `flext-tap-ldap/docs/` (getting started, configuration, architecture, API reference, testing, troubleshooting, examples)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` (alignment with make val when unblocked)
- Related projects: `flext-ldap`, `flext-ldif`, `flext-meltano`, `flext-core`, `flext-cli`, `flext-observability`, plus matching targets like `flext-target-ldap`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-tap-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-ldap/discussions>
- Follow `docs/standards/README.md`, this project’s `AGENTS.md`, and the portal index checklist before editing docs or code to keep the ecosystem synchronized.
