# Getting Started

Use the root portal for workspace-level guidance only. Package-specific
implementation details stay in each `flext-*` project.

## Prerequisites

- Python `3.13+`
- workspace `.venv`
- `make`

## Bootstrap the Workspace

```bash
make setup
make check
make test PROJECT=flext-core
```

`make setup` provisions the shared environment and governed gitlinks. It does
not take `APPLY=Y`. A member on the wrong branch fails closed without
destructive checkout/reset — switch the member yourself while keeping dirty
work, then re-run setup.

There is no `make val` verb; use `make check` / `make test`.

## Navigate the Root Portal

- [Architecture baseline](../architecture/baseline-v0.13.0.md)
- [ADR index](../architecture/adr/README.md)
- [Migration guide](migration-to-v0.13.0.md)
- [Project catalog](../projects/generated/catalog.md)
- [Workspace API overview](../api-reference/generated/overview.md)

## Work on One Project

```bash
make check PROJECT=flext-infra
make test PROJECT=flext-infra FILE=flext-infra/tests/unit/...
make docs WHAT=audit PROJECT=flext-infra
```

## Documentation Model

- curated workspace docs live under `docs/`
- generated API docs come from public exports and docstrings
- per-project documentation is owned by each project under its own `README.md` and `docs/`

## Next Steps

- Read [Make Commands](make-commands.md) for the full command reference
- Read [Development](development.md) for the daily workflow
- Read [Configuration](configuration.md) for `pyproject.toml` and docs metadata
- Read [Testing](testing.md) for quality gates and docs validation
