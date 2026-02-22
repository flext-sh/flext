# Scripts Directory - DEPRECATED

This directory is **deprecated** and no longer packaged as part of the root `flext` package.

## Status

- **Removal Date**: Scheduled for v0.13.0
- **Current Status**: Maintained for backward compatibility only
- **Migration Path**: Scripts have been moved to individual project packages

## What Changed

As of v0.12.0:
- The `{from = ".", include = "scripts"}` entry was removed from `tool.poetry.packages` in `pyproject.toml`
- Scripts are no longer distributed as part of the root workspace package
- Individual projects now maintain their own utility scripts

## For Users

If you depend on scripts from this directory:
1. Check the relevant project's `scripts/` subdirectory
2. Import utilities directly from project packages (e.g., `flext_infra`, `flext_quality`)
3. Use the Makefile targets instead of direct script invocation

## For Developers

- Do not add new scripts to this directory
- Maintain existing scripts only for backward compatibility
- Move new utilities to appropriate project packages
