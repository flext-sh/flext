---
name: flext-constants-discipline
description: 'Use this skill to canonical constants layout using StrEnum, IntEnum,
  Literal, frozenset, MappingProxyType, tuple and Final. Use when adding or refactoring
  any c.* constant across the workspace. DO NOT USE FOR: questions unrelated to flext-constants-discipline
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Constants Discipline

**UTILITY SKILL**

## USE FOR

- Requests about flext constants discipline.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-constants-discipline.
- creating projects or architecture from scratch.


## Workflow

1. Grep for raw module-scope collections in the target project:
2. For each hit, pick the canonical form from Rules.
3. Relocate into the `c.<Project>.<Category>` namespace.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
