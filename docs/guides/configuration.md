# Configuration

<!-- TOC START -->
- [Source of Truth Order](#source-of-truth-order)
- [Root Policy File](#root-policy-file)
- [Project Metadata](#project-metadata)
- [`tool.flext.docs`](#toolflextdocs)
- [Docs Generation Contract](#docs-generation-contract)
- [Validation](#validation)
<!-- TOC END -->

The docs pipeline should read as much as possible from `pyproject.toml`. Root JSON policy exists only for values that
cannot be inferred from project metadata.

## Source of Truth Order

1. project `pyproject.toml`
2. `[tool.flext.docs]` inside each project `pyproject.toml`
3. minimal root policy in `docs/docs_config.json`

If a value can be derived from `pyproject.toml`, it should not be duplicated in JSON.

## Root Policy File

`docs/docs_config.json` is intentionally small. It currently centralizes only:

- root scope exclusions
- placeholder audit terms
- stale forward-guidance symbols
- stale-symbol exempt paths for migration and baseline docs

## Project Metadata

Project docs automation should prefer these values from `pyproject.toml`:

- `[project].name`
- `[project].description`
- `[project].version`
- `[project].urls`
- wheel package paths under the build backend

## `tool.flext.docs`

Use `[tool.flext.docs]` only for metadata that is specific to the docs pipeline and cannot be safely inferred:

```toml
[tool.flext.docs]
project_class = "platform"
site_title = "FLEXT API"
package_name = "flext_api"
exclude_docs = ["references/**"]
module_include = ["flext_api.api"]
module_exclude = ["flext_api._internal"]
```

Typical fields:

- `project_class`
- `site_title`
- `package_name`
- `enabled`
- `exclude_docs`
- `module_include`
- `module_exclude`

## Docs Generation Contract

- generated API pages come from public exports and docstrings
- mkdocs settings is generated from project metadata plus minimal docs overrides
- curated guides must not duplicate generated API descriptions

## Validation

```bash
make docs DOCS_PHASE=generate PROJECT=flext-infra
make docs DOCS_PHASE=validate PROJECT=flext-infra
```

Use [Troubleshooting](troubleshooting.md) when a project is missing package metadata or generated pages do not match the
code.
