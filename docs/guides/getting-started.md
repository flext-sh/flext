# Getting Started

<!-- TOC START -->
- [Prerequisites](#prerequisites)
- [Bootstrap the Workspace](#bootstrap-the-workspace)
- [Navigate the Root Portal](#navigate-the-root-portal)
- [Work on One Project](#work-on-one-project)
- [Documentation Model](#documentation-model)
- [Next Steps](#next-steps)
<!-- TOC END -->

Use the root portal for workspace-level guidance only. Package-specific implementation details stay in each `flext-*`
project.

## Prerequisites

- Python `3.13+`
- workspace `.venv`
- `make`

## Bootstrap the Workspace

```bash
make boot APPLY=Y
make val
```

`make boot APPLY=Y` installs the selected projects into the shared workspace environment and then runs validation.

## Navigate the Root Portal

- [Architecture baseline](../architecture/baseline-v0.13.0.md)
- [ADR index](../architecture/adr/README.md)
- [Migration guide](migration-to-v0.13.0.md)
- [Project catalog](../projects/generated/catalog.md)
- [Workspace API overview](../api-reference/generated/overview.md)

## Work on One Project

Use the standard workspace selectors instead of ad hoc commands:

```bash
make check PROJECT=flext-infra
make test PROJECT=flext-infra MATCH=docs
make docs DOCS_PHASE=audit PROJECT=flext-infra
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
