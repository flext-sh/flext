---
name: scripts-infra
description: 'Use this skill to core infrastructure services — validation, inventory,
  scanning, and skill orchestration. Use when using flext_infra.core or editing scripts/lib/,
  scripts/core/, scripts/settings/, scripts/makefiles/, or scripts/common.py. DO NOT
  USE FOR: questions unrelated to scripts-infra creating projects or architecture
  from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Infra

**UTILITY SKILL**

## USE FOR

- Requests about scripts infra.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to scripts-infra.
- creating projects or architecture from scratch.

## Workflow

1. Identify the shared lib or infra file to modify.
2. Check which scripts source/import it via `rg 'source.*common.sh' scripts/` or `rg 'from.*core.*import' scripts/`.
3. Apply minimal change.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
