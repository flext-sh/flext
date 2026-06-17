---
name: scripts-architecture
description: 'Use this skill to architecture services — import analysis, violation
  detection, code reorganization, dead code scanning, and cross-project testing. Use
  when using flext_infra or editing scripts/architecture/ or scripts/analysis/. DO
  NOT USE FOR: questions unrelated to scripts-architecture creating projects or architecture
  from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Architecture

**UTILITY SKILL**

## USE FOR

- Requests about scripts architecture.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to scripts-architecture.
- creating projects or architecture from scratch.


## Workflow

1. Identify the architecture invariant to enforce or analyze.
2. Create or modify the script under `scripts/architecture/`.
3. Test with `--help` and a dry-run mode first.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
