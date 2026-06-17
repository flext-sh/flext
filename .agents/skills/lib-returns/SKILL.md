---
name: lib-returns
description: 'Use this skill to r railway composition built on dry-python/returns.
  Use when implementing result-flow operations, error recovery chains, or converting
  between container types. DO NOT USE FOR: questions unrelated to lib-returns creating
  projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Returns — r Railway Composition

**UTILITY SKILL**

## USE FOR

- Requests about lib returns.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to lib-returns.
- creating projects or architecture from scratch.


## Workflow

1. Import `r` from `flext_core`
2. Create results via `r[T].ok(value)` or `r[T].fail("error")`
3. Compose with `.map()` → `.flat_map()` → `.lash()` chains


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
