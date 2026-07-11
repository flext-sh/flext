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
2. If it is a static enforcement rule, declare it as Pydantic-2-validated DATA in
   `flext-infra/config/enforcement/*.yaml`, evaluated by the rope-semantic engine — never a bespoke
   detector script (LAW1). `scripts/architecture/` may retain only read-only analysis/reporting
   tooling, not rule logic.
3. Test with `--help` and a dry-run mode first.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
