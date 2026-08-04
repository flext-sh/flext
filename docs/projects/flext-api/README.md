# FLEXT API

FLEXT API is the FLEXT platform's HTTP client layer: a typed REST client facade over `flext-web` with `r[T]` result
contracts, Pydantic-validated settings, and the canonical `c/m/p/t/u` facade layout.

## Status & health

- **Version**: 0.12.0-dev (current development cycle)
- **Python**: 3.13+
- **Project class**: `platform`
- **Status**: Active development on the `0.12.0-dev` branch; the package builds and exports its full public surface.
- **Description** (from `pyproject.toml`): "FLEXT API - High-Performance REST API with FastAPI"
- **Dependencies**: `flext-core`, `flext-web`

### Quality signals

- Quality gates run through the workspace Make contract: `make check PROJECT=flext-api`, `make test PROJECT=flext-api`,
  and `make check`.
- Lint, typing, and security verdicts are produced by the gates (ruff, pyrefly, mypy, pyright); consult the gate output
  rather than static claims in this page.

## Quick start

```bash
cd flext-api
poetry install
make check PROJECT=flext-api
```

Programmatic use via the public facade:

```python
from flext_api import FlextApi, api

# api is the global FlextApi instance (FlextApi.fetch_global()).
# Settings resolve from FlextApiSettings (env prefix FLEXT_API_).
result = api.get("https://api.example.com/users")
if result.success:
    response = result.unwrap()
else:
    u.Cli.print(result.error_message)
```

`FlextApi` exposes `get`, `post`, `put`, `patch`, `delete`, `request`, and `execute`; each returns
`p.Result[m.Api.HttpResponse]`. The underlying `FlextApiClient` is reachable through the `client` property.

## Architecture & modules

```text
src/flext_api/
├── api.py        # FlextApi facade + api global instance
├── base.py       # FlextApiServiceBase (s facade)
├── _settings.py  # FlextApiSettings + settings singleton (env prefix FLEXT_API_)
├── config/       # Execution parametrization (YAML)
├── _constants/   # Private constants
├── _models/      # Private models (m.Api.HttpRequest / HttpResponse)
├── _protocols/   # Private protocols
├── _typings/     # Private typings
├── _utilities/   # FlextApiClient, codecs, request utils, serializers
├── constants.py  # c facade
├── models.py     # m facade
├── protocols.py  # p facade
├── typings.py    # t facade
└── utilities.py  # u facade
```

### Key architectural patterns

- **Monadic HTTP flow**: each verb on `FlextApi` delegates to `_http_method`, which builds the request payload,
  validates it into `m.Api.HttpRequest`, and executes it via `flat_map` chaining — every step returns `p.Result`.
- **Service base**: `FlextApi` extends `FlextApiServiceBase[bool]` from `base.py`, which publishes the operational `s`
  alias.
- **Client composition**: `FlextApiClient` in `_utilities/client.py` composes codec and request mixins and performs the
  actual `request(HttpRequest) -> p.Result[HttpResponse]` call through `flext-web` transports.
- **Facade exports**: the package root lazily exports the canonical aliases `c`, `m`, `p`, `t`, `u`, `s`, and
  `settings`, plus `d/e/h/r/x` re-exported from `flext_web`.

## Testing & quality

- Tests live under the project `tests/` tree and run via `make test PROJECT=flext-api`.
- Pre-merge verification: `make check PROJECT=flext-api` (lint + typing + security selectors) and `make check`.

## Resources

- [Project README](../../../flext-api/README.md)
- [Project docs portal](../../../flext-api/docs/index.md)
- Related projects: `flext-web`, `flext-core`, `flext-grpc`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-api/issues>
- Discussions: <https://github.com/flext-sh/flext-api/discussions>
- Follow the workspace `AGENTS.md` and the project `AGENTS.md` before editing docs or code.
