# FLEXT Auth

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture snapshot](#architecture-snapshot)
- [Key features & challenges](#key-features-challenges)
- [Resources](#resources)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT Auth v2.0.0 is the generic, multi-provider authentication foundation for the FLEXT ecosystem. It exposes a registry-centric API (`FlextAuth`, `FlextAuthRegistry`, `FlextAuthBaseProvider`) that lets every project plug in JWT, OAuth2, OIDC, SAML, API key, LDAP, Kerberos, or custom transports behind the same validation pipeline.

## Status & metrics

- **Version**: 2.0.0 Foundation Complete (Dec 2025)
- **Python support**: 3.13+
- **Tests**: 558 tests in total; 228 passing (40.9%), 319 failing (57.2%), 11 errors (2.0%) [see `reports/pytest/` snapshots]
- **Coverage**: ~70% as captured in `reports/coverage-scan-*`
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks)
- **Type safety**: Pyrefly strict mode and MyPy strict mode run clean; no `Any`, no `cast`, no `# type:` ignores allowed
- **Security posture**: bcrypt (12 rounds) + JWT (HS256) plus planned phase 2 providers

## Quick start

```bash
cd flext-auth
poetry install
```

```python
from flext_auth import FlextAuth, FlextAuthModels

auth = FlextAuth.quick_start(create_REDACTED_LDAP_BIND_PASSWORD=False)

result = auth.register_user(
    username="demo",
    email="demo@example.com",
    password="secure123"
)

if result.is_success:
    session = auth.authenticate_user("demo", "secure123")
    assert session.is_success
```

For provider registration, import `FlextAuthRegistry` + `FlextAuthJwtProvider` or any custom provider that implements `FlextAuthBaseProvider` and pass it into `FlextAuth.with_provider` or `with_registry`.

## Architecture snapshot

- **Facade & registry**: `api.py` provides the sole `FlextAuth` entry point and delegates to `FlextAuthRegistry`/`FlextAuthBaseProvider` for every authentication flow.
- **Protocols**: `providers/base.py` defines `BaseProvider` mixin/protocol, and every transport resolves through the registry (JWT provider already production-ready, OAuth2/OIDC/SAML pending in later phases).
- **Transports**: `transports/http.py`, `transports/grpc.py`, `transports/websocket.py` layer the project on top of `flext-api`, `flext-grpc`, and websockets; new transports follow the same registry path.
- **Phased modules**: `providers/`, `protocol_handlers/`, `credentials/`, `tokens/`, and `sessions/` each implement one slice of the multi-phase roadmap while honoring the zero-tolerance rules from `AGENTS.md` (no direct provider imports, registry-only orchestration, FlextResult for failures).

## Key features & challenges

- **Provider extensibility**: register new providers and query their capabilities at runtime via `FlextAuthRegistry`.
- **Protocol handlers**: REST, SOAP, and GraphQL handlers live under `protocol_handlers/` with consistent error/result handling.
- **Multi-transport support**: HTTP (mandatory), gRPC (mandatory), WebSocket, plus future transports all reuse the same `FlextAuth` facade.
- **Railway discipline**: every public surface returns `FlextResult[T]` and chains via `.flat_map`/`.map`.
- **Quality signal**: currently ~40% tests passing, so every release cycle must prioritize the failing suites before expanding provider coverage.

## Resources

- [Project README](../../flext-auth/README.md)
- [CLAUDE instructions](../../flext-auth/AGENTS.md) (registry rules, zero tolerance constraints)
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for evidencing the mentioned gates
- `docs/getting-started.md`, `docs/api-reference.md`, and the project’s `docs/` folder for boarding guides and extension notes
- Related integration libraries: `flext-core`, `flext-api`, `flext-grpc`, `flext-ldap`, `flext-web`

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-auth/issues>
- Discussions: <https://github.com/flext-sh/flext-auth/discussions>
- Follow `docs/standards/README.md` and the project’s `CLAUDE` zero-tolerance checklist before editing source or docs to keep alignment with the portal.
