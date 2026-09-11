# API Reference

<!-- TOC START -->
- [SSOT Rule](#ssot-rule)
- [Root Outputs](#root-outputs)
- [Project Outputs](#project-outputs)
<!-- TOC END -->

FLEXT API documentation is code-driven.

## SSOT Rule

Generated API reference comes from:

1. `pyproject.toml`
2. `src/<package>/__init__.py`
3. exported public symbols
4. module, class, and function docstrings

If the generated API output is wrong, fix the code, the exports, or the docstrings. Do not write duplicate API prose at
the root.

## Root Outputs

- [Workspace API overview](generated/overview.md)

## Project Outputs

Each FLEXT project owns its detailed generated API reference in its local tree:

- `docs/api-reference/generated/overview.md`
- `docs/api-reference/generated/public-api.md`
- `docs/api-reference/generated/modules/*.md`

The root portal keeps the workspace summary; the detailed API surface lives with each project.
