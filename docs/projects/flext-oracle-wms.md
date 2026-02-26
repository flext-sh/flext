# FLEXT Oracle WMS

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture & compliance snapshot](#architecture-compliance-snapshot)
- [Key features & blockers](#key-features-blockers)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Oracle WMS (v0.9.9 RC) is the Oracle Warehouse Management System integration framework that stands ready to join the FLEXT ecosystem once the compliance refactor finishes. It already defines the full LGF v10/legacy API catalog, configuration helpers, and instrumentation wiring, but connectivity validation, OAuth2 authentication, and Flext-compliant imports are still outstanding.

## Status & metrics

- **Version**: 0.9.9 RC (Phase 1 modernization) with 1.0.0 release preparation in progress
- **Python**: 3.13+ only
- **Tests**: ~481 functions across ~40 files; they currently rely on fake URLs and expect connectivity failures, so the Pryfly/pytest pipeline is noted as blocked until FlextCore integration happens
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks) is marked as blocked because of structural compliance issues (HTTPX imports, class architecture, lack of flext-auth/flext-cli integration)
- **Coverage**: Architecture target is 90%+, but the current reporting reflects the blocking issues described in the README
- **Type safety**: Pyrefly/MyPy strict modes run clean; zero `Any`, no `cast`, no `# type: ignore`; FlextResult flows saturate every layer
- **Security**: Bandit/pip-audit gates are defined but deferred until the FlextCore import cleanup completes

## Quick start

```bash
git clone https://github.com/flext-sh/flext-oracle-wms.git
cd flext-oracle-wms
poetry install
make setup
make validate  # currently blocked (see README for the required FlextCore refactoring)
```

```python
from flext_oracle_wms import FlextOracleWmsClient, FlextOracleWmsClientSettings

settings = FlextOracleWmsClientSettings.for_testing()
with FlextOracleWmsClient(settings) as client:
    result = client.test_connection()
    if result.is_failure:
        print("Expected failure due to test URL")
```

Replace the `for_testing()` helpers with real Oracle WMS Cloud credentials once the compliance phase replaces the fake URLs and adds OAuth2 support.

## Architecture & compliance snapshot

- **Layered modules**: `constants.py`, `typings.py`, `protocols.py` define the foundation; `api.py` exposes `FlextOracleWms` services; `services/`, `integration/`, `auth/`, and `cli/` map to the Flext tiers.
- **API catalog**: 25+ endpoints (setup, automation, data extract, entity management) already defined, including the 2025 LGF v10 APIs for entity extracts, bulk updates, and object store exports.
- **Compliance gaps**: README calls out httpx -> flext-api migration needs, consolidation from 133 classes to unified classes per module, flext-auth/flext-cli integration, and OAuth2 authentication coverage.
- **FlextResult discipline**: every operation returns `FlextResult`, and the README explicitly forbids exception-based error handling, `Any`, or type ignores.

## Key features & blockers

- **Oracle WMS framework**: configuration scaffolding, entity discovery, data extraction, automation operations, and staging/transit endpoints already have typed definitions.
- **Testing structure**: 25+ API tests, entity discovery validations, authentication checks, and Docker-based workloads exist but currently expect connectivity failures; real Oracle WMS credentials and OAuth2 flows remain to be wired.
- **Roadmap**: Phase 1 (foundation compliance) covers httpx migration, class consolidation, flext-auth integration; Phase 2 covers adding missing LGF v10 APIs, establishing real Oracle WMS connectivity, and validating modern operations.
- **Enterprise configuration**: environment variables (`FLEXT_ORACLE_WMS_BASE_URL`, credentials, auth method, timeouts, caches) plus programmatic helpers highlight how deployments should behave once the blocked quality pipeline reopens.

## Resources & references

- [Project README](../../flext-oracle-wms/README.md)
- [Project CLAUDE](../../flext-oracle-wms/CLAUDE.md) for zero-tolerance error handling, FlextResult promises, and command guidance
- `docs/` folder inside the project for architectural overviews, guides, and roadmap notes
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` once `make validate` finishes
- Related projects: `flext-core`, `flext-api`, `flext-auth`, `flext-cli`, `flext-db-oracle`, `flext-tap-oracle-wms`, `flext-target-oracle-wms`, `flext-dbt-oracle-wms`

## Support & contributions

- Issues: <https://github.com/flext-sh/flext-oracle-wms/issues>
- Discussions: <https://github.com/flext-sh/flext-oracle-wms/discussions>
- Follow `docs/standards/README.md`, this project’s CLAUDE file, and the portal checklist before editing docs or tests so the brief stays accurate.
