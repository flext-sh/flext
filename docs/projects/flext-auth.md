# FLEXT Auth

FLEXT Auth is the multi-provider authentication and authorization service of the FLEXT platform. It exposes a registry-
centric facade (`FlextAuth` / `auth`) backed by provider services for JWT, OAuth2, OIDC, SAML, API key, basic auth,
client certificates, LDAP, and Kerberos, all behind the same `r[T]` validation pipeline. Package description: "FLEXT
Auth — Enterprise Authentication & Authorization Service".

## Status & health

- **Version**: 0.20.0-dev (current development cycle)
- **Python**: 3.13+ only
- **Quality gate**: `make check PROJECT=flext-auth` (Ruff + type checks) and `make val` for the full pipeline
- **Depends on**: `flext-core` (facades, result contract, container)

### Quality signals

- Provider orchestration goes through `FlextAuthRegistry`; the facade never imports provider internals directly
- Strict typing per workspace policy: no `Any`, no `cast` shortcuts
- Every public operation returns `r[T]`; failures carry context instead of raising
- Facets `c`/`t`/`p`/`m` stay declaration-only (root `AGENTS.md` U17)

## Quick start

```bash
make setup
make check PROJECT=flext-auth
```

```python
from flext_auth import FlextAuth

auth = FlextAuth.quick_start(create_admin_user=False)

created = auth.register_user(
    username="demo", email="demo@example.com", password="secure123"
)
assert created.is_success

session = auth.authenticate_user("demo", "secure123")
assert session.is_success
```

`FlextAuth.quick_start()` builds the facade with the built-in provider set; `FlextAuth.fetch_global()` returns the
process-wide singleton (`auth` alias). Providers implement the provider mixin/protocol and are registered through
`FlextAuthRegistry`.

## Architecture & modules

`src/flext_auth/` follows the FLEXT tiered layout:

- **Foundation**: `constants.py`, `typings.py`, `protocols.py` (+ `_constants/`, `_protocols/`) — auth constants (roles,
  token settings), type aliases, and provider protocols.
- **Domain**: `models.py` (`_models/`) — Pydantic v2 models for identities, tokens, and sessions.
- **Providers**: `providers/` — `jwt.py` + `jwt_token_validator.py`, `oauth2.py` (+ `oauth2_config.py`,
  `oauth2_introspection.py`, `oauth2_tokens.py`), `oidc.py`, `saml.py`, `apikey.py`, `basic.py`, `certificate.py`,
  `ldap.py`, `kerberos.py` (+ `kerberos_support.py`), `rfc.py`, and the shared `mixin.py`.
- **Services**: `services/` — `auth_service.py` (`authenticate`, `authenticate_user`, `register_user`, `create_token`),
  `identity_service.py`, `provider_service.py`, `session_service.py`, `token_service.py`.
- **Registry & entry point**: `registry.py` (`_registry/`) holds `FlextAuthRegistry`; `api.py` defines `FlextAuth` as
  the MRO facade over the application service; `__init__.py` exports the facade, providers, services, and the standard
  aliases plus `config`/`settings`.

### Key architectural patterns

- **Registry-first**: providers declare capabilities and resolve through `FlextAuthRegistry`; adding a provider means
  implementing the mixin and registering it — no facade changes.
- **Service decomposition**: identity, session, token, and provider concerns are separate services composed into the
  facade via MRO.
- **Railway discipline**: authentication, registration, and token issuance all return `r[T]`, chaining via
  `.map`/`.flat_map`.
- **Config/settings SSOT**: token expiry and session lifetimes come from the validated `settings` singleton
  (`settings.Auth.*`), never from ad-hoc reads.

## Testing & quality

- `make check PROJECT=flext-auth`: Ruff linting plus type checks
- `make test PROJECT=flext-auth`: pytest suite (latest evidence under `reports/pytest/`)
- `make val`: full pipeline; see `reports/coverage-scan-*` for the current coverage snapshot
- Tests target the public facade and exported models only, per workspace testing law (U16)

## Resources

- [Project README](../../flext-auth/README.md) (auto-generated module map and operation flow)
- [Workspace AGENTS.md](../../AGENTS.md) — layering and zero-tolerance rules
- `flext-auth/docs/api-reference/` — generated API documentation
- Related projects: `flext-core`, `flext-ldap` (LDAP provider backend), `flext-grpc`
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-auth/issues>
- Follow the workspace `AGENTS.md` before proposing doc or code changes so this page stays aligned with the engineering
  portal.
