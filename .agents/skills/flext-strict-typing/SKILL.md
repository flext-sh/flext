---
name: flext-strict-typing
description: 'Use this skill to defines and enforces the FLEXT type hierarchy: t.*
  contracts, PEP 695 type aliases, r[T] result containers, and isinstance/TypeGuard
  narrowing. Use when writing type annotations, fixing pyrefly or pyright errors,
  working with t.JsonValue or t.Scalar, enforcing no-Any. DO NOT USE FOR: questions
  unrelated to flext-strict-typing creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Strict Typing Rules

**UTILITY SKILL**

## USE FOR

- Requests about flext strict typing.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-strict-typing.
- creating projects or architecture from scratch.


## Workflow

1. Detect typing violations from gates and structural search.
2. Map each violation to canonical `t.*` and `r` patterns.
3. Apply fixes in shared-core-first order when contracts are reused.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
## References

- [references/type-rules-detail.md](references/type-rules-detail.md)
