---
name: scripts-architecture
description: 'Guidance for architecture services — import analysis, violation detection, code reorganization, dead code scanning, and cross-project testing. Use when using flext_infra or editing scripts/architecture/ or scripts/analysis/.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Architecture

## Workflow

1. Identify the architecture invariant to enforce or analyze.
2. Create or modify the script under `scripts/architecture/`.
3. Test with `--help` and a dry-run mode first.

## Enforced contracts

- Direct Singer/Meltano imports banned.
- Direct database library imports banned.
- Direct HTTP client imports banned.
- Direct CLI library imports banned.
- Projects should import flext_core.
- Singer projects should avoid direct singer_sdk imports in leaf modules.
- Singer projects should avoid direct Singer message construction in leaf modules.
