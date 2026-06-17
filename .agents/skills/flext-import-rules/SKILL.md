---
name: flext-import-rules
description: 'Use this skill to enforces import ordering, alias conventions, and abstraction
  boundaries for the FLEXT 33-project monorepo (PEP 623, TYPE_CHECKING rules, no bare
  pydantic/structlog in consumers). Use when adding imports to any Python file, resolving
  circular imports, auditing import. DO NOT USE FOR: questions unrelated to flext-import-rules
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Import Rules

**UTILITY SKILL**

## USE FOR

- Requests about flext import rules.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-import-rules.
- creating projects or architecture from scratch.


## Workflow

1. Inventory current import style and violations.
2. Apply canonical import form aligned with module tier.
3. Fix cross-project inheritance/import boundaries.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
## References

- [references/import-rules-detail.md](references/import-rules-detail.md)
