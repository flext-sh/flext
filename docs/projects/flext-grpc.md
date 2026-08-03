# FLEXT gRPC

FLEXT gRPC is the gRPC communication foundation of the FLEXT platform. It wraps grpcio/protobuf concerns behind typed
Pydantic models and the `r[T]` contract, and exposes a single `FlextGrpc` facade (`grpc` alias) for building servers,
clients, channels, and services with validated inputs. Package description: "FLEXT gRPC — High-Performance gRPC
Services".

## Status & health

- **Version**: 0.20.0-dev (current development cycle)
- **Python**: 3.13+ only
- **Quality gate**: `make check PROJECT=flext-grpc` (Ruff + type checks) and `make val` for the full pipeline
- **Depends on**: `flext-core` (facades, result contract, container)

### Quality signals

- grpcio/protobuf imports are contained behind the facade and utilities; consumers work with typed models only
- Strict typing per workspace policy: no `Any`, no `cast` shortcuts
- Every public operation returns `r[T]` with consistent error handling
- Facets `c`/`t`/`p`/`m` stay declaration-only (root `AGENTS.md` U17)

## Quick start

```bash
pip install flext-grpc
```

```python
from flext_grpc import grpc

setup = grpc.create_complete_setup(
    host="127.0.0.1", port=50051, service_name="Greeter", methods=["SayHello"]
)
assert setup.is_success

server = setup.value.server
client = setup.value.client
```

The facade also exposes granular builders — `create_server`, `create_client`, `create_channel`, `create_service` — plus
`parse_address` and `validate_target` helpers; all return `r[T]`.

## Architecture & modules

`src/flext_grpc/` follows the FLEXT tiered layout:

- **Foundation**: `constants.py`, `typings.py`, `protocols.py` — network/service defaults, type aliases, and gRPC
  protocols; `errors.py` carries the error taxonomy.
- **Domain**: `models.py` — Pydantic v2 models for servers, clients, channels, services, and the `CompleteSetup`
  aggregate.
- **Services**: `services/` — `api_runtime.py` (facade runtime behavior), `server.py`, `client.py`,
  `connection_pool.py`, `stream.py`, `metrics.py`.
- **Proto**: `proto/stubs.py` — protobuf stub integration.
- **Entry point**: `api.py` defines `FlextGrpc` as the MRO composition of `FlextGrpcApiRuntime`, `FlextGrpcServer`,
  `FlextGrpcClient`, `FlextGrpcConnectionPool`, `FlextGrpcStream`, and `FlextGrpcMetrics`; `grpc =
  FlextGrpc.fetch_global()` is the shared singleton; `__init__.py` exports the facade plus the standard aliases and
  `config`/`settings`.

### Key architectural patterns

- **Functional composition**: `create_complete_setup` chains `create_server` → `create_client` → `create_service`,
  short-circuiting on the first failed result.
- **Typed boundaries**: raw grpcio objects never cross the public surface; validated `m.Grpc.*` models do.
- **MRO facade**: server/client/pool/stream/metrics capabilities compose into one `FlextGrpc` class — no standalone
  helpers.
- **Config/settings SSOT**: host, port, and worker defaults come from `c.Grpc.*` constants and the validated `settings`
  singleton.

## Testing & quality

- `make check PROJECT=flext-grpc`: Ruff linting plus type checks
- `make test PROJECT=flext-grpc`: pytest suite (latest evidence under `reports/pytest/`)
- `make val`: full pipeline; see `reports/coverage-scan-*` for the current coverage snapshot
- Tests target the public facade and exported models only, per workspace testing law (U16)

## Resources

- [Project README](../../flext-grpc/README.md) (auto-generated module map and operation flow)
- [Workspace AGENTS.md](../../AGENTS.md) — layering and zero-tolerance rules
- `flext-grpc/docs/api-reference/` — generated API documentation
- Related projects: `flext-core`, `flext-cli`, `flext-auth`
- Reports: `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-grpc/issues>
- Follow the workspace `AGENTS.md` before proposing doc or code changes so this page stays aligned with the engineering
  portal.
