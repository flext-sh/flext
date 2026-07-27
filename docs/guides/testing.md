# Testing

The workspace test taxonomy is standardized. Root guidance stays short; project-specific test details stay local to each
project.

## Canonical Test Layout

Use these directories when the project owns tests:

- `tests/unit`
- `tests/integration`
- `tests/architecture`
- `tests/performance`
- `tests/fixtures`

## Common Commands

```bash
make test PROJECT=flext-infra
make test PROJECT=flext-infra MATCH=docs
make check PROJECT=flext-infra
make val
```

## Docs Pipeline Validation

Use the docs phases directly when you are changing documentation tooling or generated docs:

```bash
make docs DOCS_PHASE=generate PROJECT=flext-infra
make docs DOCS_PHASE=fix PROJECT=flext-infra FIX=1
make docs DOCS_PHASE=audit PROJECT=flext-infra
make docs DOCS_PHASE=build PROJECT=flext-infra
make docs DOCS_PHASE=validate PROJECT=flext-infra
```

## Expectations

- generated API docs must come from public exports and docstrings
- root docs must stay FLEXT-only
- lint and type gates stay clean after each docs-tooling change

## Related Guides

- [Make Commands](make-commands.md)
- [Development](development.md)
- [Configuration](configuration.md)
- [Troubleshooting](troubleshooting.md)
