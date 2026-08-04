# Testing

<!-- TOC START -->
- [Canonical Test Layout](#canonical-test-layout)
- [Common Commands](#common-commands)
- [Docs Pipeline Validation](#docs-pipeline-validation)
- [Expectations](#expectations)
- [Related Guides](#related-guides)
<!-- TOC END -->

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
make test CI=Y PROJECT=flext-infra
make test WHAT=cache-status PROJECT=flext-infra
make test WHAT=cache-clear APPLY=Y PROJECT=flext-infra
make check PROJECT=flext-infra
make check
```

`make test` always uses pytest-testmon. Without `CI=Y` it also writes
`coverage.xml`. With `CI=Y` coverage is disabled. Use `WHAT=cache-*` to inspect,
clear (`APPLY=Y`), or checkpoint the local `.testmondata` cache.

## Docs Pipeline Validation

Use the docs phases directly when you are changing documentation tooling or generated docs:

```bash
make docs WHAT=generate PROJECT=flext-infra
make docs WHAT=fix PROJECT=flext-infra APPLY=Y
make docs WHAT=audit PROJECT=flext-infra
make docs WHAT=build PROJECT=flext-infra
make docs WHAT=validate PROJECT=flext-infra
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
