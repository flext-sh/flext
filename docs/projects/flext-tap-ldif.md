# FLEXT Tap LDIF

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & patterns](#architecture-patterns)
- [Quality & operations](#quality-operations)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Tap LDIF (v1.0.0 release prep) is the Singer tap responsible for extracting LDAP/LDIF data for the FLEXT data mesh. It implements Singer protocols, cleans LDIF via flext-ldif parsers, and complies with the workspace zero-tolerance standards.

## Status & health

- **Version**: 1.0.0 (Release Preparation)
- **Python**: 3.13+
- **Status**: production-ready extraction flows with Strong gating (90%+ coverage, zero tech debt). Documentation is still being expanded but the project is stable.
- **Coverage**: 90%+ (see `reports/coverage-scan-*` & README badges)
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + dbt/test + coverage + docstring checks) is the enforced pre-merge command; `make lint`, `make type-check`, `make security`, `make test`, and other quality scripts all report clean results.
- **Dependencies**: `flext-core`, `flext-ldif`, `flext-meltano`, Singer SDK, `dbt`, `dbt-core`, `dbt-postgres`, instrumentation via `flext-observability`
- **Zero tolerance**: Forbidden direct imports of singer-sdk, ldap3, or flext-ldif internals; use the standard flext adapters, always return `r[T]`, never rely on exception-based flows, and keep config in Pydantic models.

## Quick start

```bash
git clone https://github.com/flext-sh/flext-tap-ldif.git
cd flext-tap-ldif
poetry install
make setup
make check
make validate
```

```bash
tap-ldif --config config.json --discover > catalog.json
tap-ldif --config config.json --catalog catalog.json --state state.json
```

## Architecture & patterns

- **Clean Architecture**: domain, application, infrastructure, and protocol layers enforce one-way dependencies with short alias imports (`r`, `t`, `m`).
- **Core components**: `FlextTapLdif` (Singer tap), `LDIFEntriesStream` (Singer stream), `TapLdifConfig` (Pydantic config), `FlextLdifProcessorWrapper`, `exception` hierarchy, watchers, and CLI/hot reload helpers.
- **Infrastructure reuse**: reuses `flext-ldif` for LDIF parsing/validation, `flext-meltano` for Singer orchestration, and `flext-core` for r, container, and logging patterns.
- **Configuration**: rich config options (file/directory/batch/perf settings, filters, encoding, strict parsing) defined in docs and enforced through typed Pydantic models.

## Quality & operations

- **Validation commands**: `make lint`, `make type-check`, `make security`, `make test`, `make coverage-html`, `make validate`, and Singer-specific commands (discover, run, sync, validate-config).
- **Testing**: 90%+ coverage across unit, integration, e2e Singer streams, plus Docker-backed LDIF tests; specialized commands like `make ldif-validate`, `make ldif-parse`, `make ldif-test`, `pytest -m singer` keep the spec satisfied.
- **Quality policy**: zero Ruff/Pyrefly errors, zero type ignores, zero direct Singer or LDIF parsing outside mandated adapters, and pre-commit hooks enforce the gating pipeline.

## Resources & references

- [Project README](../../flext-tap-ldif/README.md)
- [AGENTS guide](../../flext-tap-ldif/AGENTS.md) with zero tolerance rules and command checklists
- `docs/` (architecture, API reference, configuration, testing, troubleshooting, examples)
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`
- Related projects: `flext-ldif`, `flext-dbt-ldif`, `flext-target-ldif`, `flext-meltano`, `flext-core`, `flext-observability`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-tap-ldif/issues>
- Discussions: <https://github.com/flext-sh/flext-tap-ldif/discussions>
- Follow `docs/standards/README.md`, workspace `AGENTS.md`, and the portal checklist before editing docs or code so the ecosystem stays synchronized.
