# FLEXT Oracle OIC

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture snapshot](#architecture-snapshot)
- [Quality & compliance](#quality-compliance)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Oracle OIC v0.9.9 is the Oracle Integration Cloud (OIC) client library for the FLEXT ecosystem. It implements OAuth2/IDCS authentication, integration pattern execution, and enterprise-grade connectors using FlextService-inspired architecture, yet remains in early development while the compliance refactor finishes.

## Status & metrics

- **Version**: 0.9.9 (early development / 1.0.0 prep)
- **Python support**: 3.13+
- **Tests**: 21% unit coverage today; integration/contract suites pending completion once FlextService refactor lands
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstrings) is blocked until FlextCore imports are refactored; lint/type/security currently green
- **Type safety**: Pyrefly strict mode + MyPy strict mode with zero `Any`/`cast`/`# type: ignore` enforced via the project CLAUDE
- **Security**: SaaS credential management, token lifecycle, circuit breaker/ retry patterns requiring completion

## Quick start

```bash
git clone https://github.com/flext-sh/flext-oracle-oic.git
cd flext-oracle-oic
poetry install --with dev,test
make setup
```

```python
from flext_oracle_oic import (
    OracleOicExtensionSettings,
    FlextOracleOicConnectionSettings,
    FlextOracleOicAuthSettings,
)

settings = OracleOicExtensionSettings(
    connection=FlextOracleOicConnectionSettings(
        base_url="https://instance.integration.ocp.oraclecloud.com",
        api_version="v1"
    ),
    auth=FlextOracleOicAuthSettings(
        oauth_client_id="id",
        oauth_client_secret="secret",
        oauth_token_url="https://idcs.identity.oraclecloud.com/oauth2/v1/token",
    ),
)

# Production-ready service is still in refactor; current helpers expose configuration
```

## Architecture snapshot

- **FlextService compliance**: currently partial (`FlextResult` 65% coverage, `FlextService` and `FlextContainer` still pending). Refactor plan enforces single-service-per-module discipline and removes direct `httpx`/`typer` dependencies.
- **Modules**: `services/` (integration patterns, retries), `auth/` (OAuth2/IDCS flows), `cli/` (pending `flext-cli` wiring), `api.py` facade, `constants/`, `typings/`, `protocols/` for short alias discipline.
- **Integration points**: depends on `flext-core`, `flext-api`, `flext-cli`, and supplies functionality to `flext-tap-oracle-oic`/`flext-target-oracle-oic` and other Oracle flavor packages.

## Quality & compliance

- `make lint`, `make type-check`, `make security` pass; `make validate` currently blocked by the outstanding FlextCore refactor.
- Project CLAUDE enforces zero `Any`, zero `cast`, zero `TYPE_CHECKING`, pure FlextResult flows, and forbids direct `httpx`/`typer` usage outside the designated adapters.
- Coverage target is 70%+ with contract/integration suites; currently at 21% while the team adds tests for OAuth2 flows, circuit breakers, and service helpers.
- Security posture highlights OAuth2 Gen3 compliance, encrypted secrets storage, and safe token lifecycle helpers.

## Resources & references

- [Project README](../../flext-oracle-oic/README.md)
- [Project CLAUDE](../../flext-oracle-oic/CLAUDE.md) for zero-tolerance rules and quality checkpoints
- `docs/` folder for getting-started, architecture, API reference, configuration, and roadmap notes
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` (once `make validate` finishes)
- Related projects: `flext-core`, `flext-api`, `flext-cli`, `flext-tap-oracle-oic`, `flext-target-oracle-oic`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-oracle-oic/issues>
- Discussions: <https://github.com/flext-sh/flext-oracle-oic/discussions>
- Follow `docs/standards/README.md` and this project’s CLAUDE before editing code or docs so the portal entry stays accurate.
