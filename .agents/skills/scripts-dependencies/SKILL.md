---
name: scripts-dependencies
description: 'Guidance for dependency management — analysis, consolidation, discovery, caching, and synchronization. Use when editing scripts/dependencies/ or using flext_infra.deps.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Dependencies

## Workflow

1. Identify the dependency concern (missing, outdated, conflicting).
2. Create or modify the script under `scripts/dependencies/`.
3. Test with `--help` and dry-run mode.

## Enforced contracts

- Every dependency script must declare Owner-Skill marker.
- Dependency scripts should include a module docstring.

## Resources

- [`rules/require-docstring.yml`](rules/require-docstring.yml)
- [`rules/require-owner-skill-marker.yml`](rules/require-owner-skill-marker.yml)
