# FLEXT API

<!-- TOC START -->

- [Status & metrics](#status-metrics)
- [Quick start](#quick-start)
- [Architecture & modules](#architecture-modules)
- [Key features](#key-features)
- [Testing & quality](#testing-quality)
- [Resources](#resources)
- [Support & contribution](#support-contribution)
<!-- TOC END -->

FLEXT API provides the HTTP client foundation, FastAPI application factory, and reusable transports that wire the FLEXT ecosystem into REST, GraphQL, WebSocket, and SSE surfaces.

## Status & metrics

- **Version**: 0.9.9
- **Python**: 3.13+
- **Coverage**: 100% test pass rate (see `reports/coverage-scan-*` for the reporting snapshot)
- **Type safety**: Pyrefly strict mode passes, MyPy strict mode passes, Ruff reports zero violations
- **Quality gate**: `make validate` (includes lint, type-check, security, coverage, docstring checks)

## Quick start

```bash
# From source (recommended for development):
git clone https://github.com/flext-sh/flext-api.git
cd flext-api
poetry install

# Or install when the package is published:
pip install flext-api
```

```python
from flext_api import FlextApiClient, FlextApiSettings

config = FlextApiSettings(base_url="https://api.example.com")
client = FlextApiClient(config)
result = client.get("/users")
if result.is_success():
    print(f"Found {len(result.unwrap())} users")
else:
    print(f"HTTP error: {result.unwrap_failure()}" )
```

Use `FlextApi().create_fastapi_app(...)` to bootstrap FastAPI servers with the same configuration patterns.

## Architecture & modules

```
src/flext_api/
├── api.py                # Public API exports & helpers
├── app.py                # FastAPI application factory
├── client.py             # FlextApiClient implementation
├── config.py             # FlextApiSettings and validation
├── protocols.py          # Protocol definitions reused by transports
├── transports.py         # Reusable transport layer (GraphQL, HTTP, WebSocket, SSE)
├── models.py             # Pydantic models and schema helpers
├── utilities.py          # HTTP utilities (401 handling, logging hooks)
├── schema/               # OpenAPI, JSON Schema, AsyncAPI helpers
└── protocol_impls/       # Pluggable protocol implementations
```

The package applies Clean Architecture: core client/server code sits in `client.py` and `app.py`, configuration lives in `config.py`, transports and middleware are pluggable, and protocol implementations (GraphQL, WebSocket) live under `protocol_impls/`.

## Key features

- **Unified HTTP client**: FlextResult-friendly client that wraps `httpx` and automatically logs, retries, and validates responses.
- **FastAPI integration**: `FlextApi.create_fastapi_app` builds a server that wires configuration, middlewares, routers, and error handling with `FlextResult`.
- **Protocol support**: Built-in GraphQL, SSE, and WebSocket helpers plus plugin hooks for other transports.
- **Configuration-driven**: `FlextApiSettings` extends Pydantic v2 models with environment validation and feature flags.
- **Documentation-first**: `docs/api-reference/`, `docs/guides`, and OpenAPI/AsyncAPI helpers keep the surface documented and consistent.

## Testing & quality

- `make check` runs Ruff + Pyrefly
- `make test` executes the `pytest` suite and generates coverage reports
- `make validate` (lint + type-check + security + tests) is the pre-merge gate
- Continuous integration publishes `reports/lint-output/*`, `reports/pytest/*`, and `reports/coverage-scan-*` so the portal can link to living artifacts.

## Resources

- [Project README](../../flext-api/README.md)
- `docs/guides/getting-started.md`, `docs/guides/configuration.md`, `docs/guides/http-client.md`, `docs/guides/testing.md`, `docs/guides/troubleshooting.md`
- `docs/architecture/overview.md` and `docs/api-reference/` inside the project repository
- [CLAUDE.md](../../flext-api/CLAUDE.md) for per-project governance and multi-agent coordination

## Support & contribution

- GitHub issues: <https://github.com/flext-sh/flext-api/issues>
- Discussions: <https://github.com/flext-sh/flext-api/discussions>
- Use `reports/` artifacts to prove the quality gate before proposing doc changes.
