# FLEXT Target LDAP

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & patterns](#architecture-patterns)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Target LDAP (v1.0.0 release preparation) is the Singer target that loads LDAP/LDIF data into authoritative LDAP directories. It provides real-time loading, comprehensive authentication, retries, and performance tuning while absorbing the FlextResult and Clean Architecture practices.

## Status & health

- **Version**: 1.0.0 (Release Preparation)
- **Status**: Production ready—official docs confirm coverage and features—while developer docs are still expanding.
- **Coverage**: 90%+ (per the docs and coverage scan artifacts)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is expected before merging; the README highlights `make check`, `make lint`, `make type-check`, and `make security` as supporting commands.
- **Dependencies**: `flext-core`, `flext-ldif`, Singer SDK, `flext-cli`, `flext-observability`, and mission-critical connectors.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-target-ldap.git
cd flext-target-ldap
poetry install
make setup
make check
make validate
```

```bash
target-ldap --config config.json --state state.json --catalog catalog.json
```

## Architecture & patterns

- **Layered architecture**: architecture docs show Clean Architecture breakdown (overview, API reference, patterns) with one-way dependencies prominently enforced.
- **Core components**: target loader, authentication modules, Singer-compatible services, configuration models, and instrumentation hooking into flext-observability.
- **Design patterns**: documented patterns include command handlers, strategy/factory for connectors, and data transformers for LDAP attribute normalization.
- **Integration**: reuses flext-ldif for parsing/validation, flext-cli for CLI flows, flext-core for DI/FlextResult, and Singer protocols for compatibility with Meltano.

## Quality & operations

- **Validation commands**: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate`, `make check`, plus Singer-specific `make discover`, `make run`, and `make validate-config`.
- **Testing**: quick start docs emphasize testing strategies (unit/integration/troubleshooting modules) and Singer compliance; tests run under `pytest` with markers for integration and Singer.
- **Performance**: includes batch processing, connection pooling, retry logic, error recovery, and instrumentation for metrics/performance analysis.

## Resources & references

- [Project README](../../flext-target-ldap/README.md)
- [Project AGENTS.md](../../flext-target-ldap/AGENTS.md) for zero-tolerance rules, quality gating, and command checklists
- `docs/` (getting started, architecture, API reference, design patterns, development, testing, troubleshooting)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for QA evidence
- Related projects: `flext-ldif`, `flext-tap-ldap`, `flext-dbt-ldif`, `flext-core`, `flext-meltano`, `flext-observability`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-target-ldap/issues>
- Discussions: <https://github.com/flext-sh/flext-target-ldap/discussions>
- Follow `docs/standards/README.md` and this project’s `AGENTS.md` before editing docs or code so the portal stays accurate.
