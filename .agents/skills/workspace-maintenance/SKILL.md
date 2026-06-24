---
name: workspace-maintenance
description: 'Use this skill to use when running workspace-wide maintenance tasks
  across all FLEXT submodules. Covers hygiene checks, dependabot settings standardization,
  Poetry health validation, and security enforcement automation. DO NOT USE FOR: questions
  unrelated to workspace-maintenance creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Workspace Maintenance

**UTILITY SKILL**

## USE FOR

- Requests about workspace maintenance.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to workspace-maintenance.
- creating projects or architecture from scratch.

## Workflow

1. Identify the maintenance concern (hygiene, dependabot, poetry, security).
2. Run standard gates first: `make check` and `make val`.
3. Run specific maintenance checker with `--help` first, then default (dry-run) mode.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
