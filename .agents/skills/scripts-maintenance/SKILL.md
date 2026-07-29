---
name: scripts-maintenance
description: 'Guidance for maintenance services — health checks, workspace status, git cleanup, and operational tooling. Use when using flext_infra.maintenance or editing scripts/maintenance/ or scripts/git/.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Maintenance

## Workflow

1. Identify the maintenance concern.
2. Create or modify the script under `scripts/maintenance/` or `scripts/git/`.
3. Test with `--help` and `--dry-run` first.

## Enforced contracts

- Every maintenance script must declare Owner-Skill marker.
- Maintenance scripts should include a module docstring.

## Resources

- [`rules/require-docstring.yml`](rules/require-docstring.yml)
- [`rules/require-owner-skill-marker.yml`](rules/require-owner-skill-marker.yml)
