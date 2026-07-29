---
name: flext-scope-bootstrap
description: 'Use when the Scope code index is missing, points at the wrong Git root, returns stale symbols, or needs reindexing after structural workspace changes.'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Scope Bootstrap

## Workflow

1. Pick the correct root: repo root for local work, workspace root for multi-repo work.
2. Bootstrap missing or invalid Scope config with `scope init` or `scope workspace init`.
3. Run `scope status`.

## Contracts

- Initialize Scope at the Git workspace root, never inside a package by accident.
- Check status and configured roots before trusting search results.
- Reindex after file moves, symbol renames, generated-source changes, or dependency-boundary edits.
