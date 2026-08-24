---
name: scripts-dependencies
description: 'Use this skill to dependency management — analysis, consolidation, discovery,
  caching, and synchronization. Use when editing scripts/dependencies/ or using flext_infra.deps.
  DO NOT USE FOR: questions unrelated to scripts-dependencies creating projects or
  architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Scripts Dependencies

**UTILITY SKILL**

## USE FOR

- Requests about scripts dependencies.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to scripts-dependencies.
- creating projects or architecture from scratch.

## Workflow

1. Identify the dependency concern (missing, outdated, conflicting).
2. Create or modify the script under `scripts/dependencies/`.
3. Test with `--help` and dry-run mode.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
