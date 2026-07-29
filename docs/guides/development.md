# Development

The root development workflow is governed by `AGENTS.md`. Treat this guide as the operational summary, not as a parallel
policy source.

## Baseline Workflow

```bash
make workspace-check-changed
make test PROJECT=flext-infra MATCH=docs
make val
```

Use `PROJECT`, `PROJECTS`, `FILE`, `FILES`, `MATCH`, and `CHECK_GATES` instead of ad hoc shell loops. See [Make
Commands](make-commands.md) for the full command reference.

## Daily Sequence

1. Read the relevant local project files and existing docs before editing.
2. Make the smallest forward fix that keeps the architecture intact.
3. Run the relevant `make` targets immediately.
4. Keep generated docs and curated docs aligned before moving on.

## Workspace Structure

- `flext-*` directories are the governed FLEXT packages
- `docs/` is the curated root documentation portal
- each project owns its own `README.md`, `AGENTS.md`, and local `docs/`

## Documentation Workflow

Use the docs phases through the canonical entrypoint:

```bash
make docs DOCS_PHASE=generate PROJECT=flext-infra
make docs DOCS_PHASE=fix PROJECT=flext-infra FIX=1
make docs DOCS_PHASE=audit PROJECT=flext-infra
make docs DOCS_PHASE=build PROJECT=flext-infra
make docs DOCS_PHASE=validate PROJECT=flext-infra
```

## Rules That Matter Here

- workspace guidance stays in root `docs/`
- project implementation guidance stays local to each project
- generated API docs come from code, exports, and docstrings
- root docs do not document non-FLEXT projects

## Related Guides

- [Getting Started](getting-started.md)
- [Configuration](configuration.md)
- [Testing](testing.md)
- [Troubleshooting](troubleshooting.md)
