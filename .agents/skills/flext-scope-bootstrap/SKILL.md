---
name: flext-scope-bootstrap
description: 'Use this skill to use when Scope is missing, stale, or must be bootstrapped
  correctly in the FLEXT monorepo. Covers repo-root vs workspace-root initialization,
  official Scope config artifacts, validation with status/index, and mandatory reindex
  triggers after structural work. DO NOT USE FOR: questions unrelated to flext-scope-bootstrap
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# FLEXT Scope Bootstrap

**UTILITY SKILL**

## USE FOR

- Requests about flext scope bootstrap.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-scope-bootstrap.
- creating projects or architecture from scratch.

## Workflow

1. Pick the correct root: repo root for local work, workspace root for multi-repo work.
2. Bootstrap missing or invalid Scope config with `scope init` or `scope workspace init`.
3. Run `scope status`.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
