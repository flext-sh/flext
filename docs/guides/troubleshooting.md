# Troubleshooting

Use this page for workspace-level diagnostics. If the failure is project-specific, continue in that project’s local docs
and tests.

## Quick Checks

```bash
make check CHANGED_ONLY=1
make val VALIDATE_SCOPE=workspace
make docs DOCS_PHASE=build PROJECT=flext-infra
```

## Common Docs Failures

### MkDocs strict build fails

Typical causes:

- broken internal links
- root docs referencing excluded files
- stale generated files that were not regenerated

Run:

```bash
make docs DOCS_PHASE=fix PROJECT=flext-infra FIX=1
make docs DOCS_PHASE=audit PROJECT=flext-infra
make docs DOCS_PHASE=build PROJECT=flext-infra
```

### Generated API docs are wrong

Do not patch the generated Markdown first. Check:

1. `pyproject.toml`
2. `[tool.flext.docs]`
3. `src/<package>/__init__.py`
4. module and symbol docstrings

### Root docs mention non-FLEXT projects

That is a root portal scope violation. Root docs must stay FLEXT-only.

### Audit flags stale architecture symbols

Fix the forward-guidance document unless the file is an explicit migration or baseline exception.

## Common Metadata Problems

- missing `[project]` name, version, description, or urls
- wrong `tool.flext.docs.package_name`
- wrong `tool.flext.docs.project_class`
- unnecessary data duplicated in `docs/docs_config.json`

## When to Edit JSON Policy

Edit `docs/docs_config.json` only when the value cannot be derived from project metadata, paths, or code.

## Related Guides

- [Configuration](configuration.md)
- [Testing](testing.md)
- [Development](development.md)
