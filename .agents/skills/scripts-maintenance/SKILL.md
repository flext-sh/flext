---
name: scripts-maintenance
description: 'Use this skill to maintenance services — health checks, workspace status,
  git cleanup, and operational tooling. Use when using flext_infra.maintenance or
  editing scripts/maintenance/ or scripts/git/. DO NOT USE FOR: questions unrelated
  to scripts-maintenance creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Scripts Maintenance

**UTILITY SKILL**

## USE FOR

- Requests about scripts maintenance.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to scripts-maintenance.
- creating projects or architecture from scratch.

## Workflow

1. Identify the maintenance concern.
2. Create or modify the script under `scripts/maintenance/` or `scripts/git/`.
3. Test with `--help` and `--dry-run` first.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.

## Governance

- `docs/GOVERNANCE.md` — controls, ADR routing, canonical workflow.
- `docs/architecture/adr/003-workspace-tooling-hub-distribution.md` — the ADR governing workspace maintenance, health-check, and operational tooling distribution this skill operates within.
