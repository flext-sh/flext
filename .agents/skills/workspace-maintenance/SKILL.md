---
name: workspace-maintenance
description: 'Guidance for workspace-wide maintenance tasks across all FLEXT submodules. Covers hygiene checks, dependabot settings standardization, Poetry health validation, and security enforcement automation.'
license: MIT
metadata:
  version: 1.0.0
---
# Workspace Maintenance

## Workflow

1. Identify the maintenance concern (hygiene, dependabot, poetry, security).
2. Run standard gates first: `make check` and `make val`.
3. For cross-workspace tooling distribution, use `make workspaces WHAT=status` and `make workspaces WHAT=distribute APPLY=1` from `~/.ai-hub`.
4. Run specific maintenance checker with `--help` first, then default (dry-run) mode.

## Enforced contracts

- Workspace maintenance scripts must declare Owner-Skill marker.

## Resources

- [`rules/require-owner-skill-marker.yml`](rules/require-owner-skill-marker.yml)
