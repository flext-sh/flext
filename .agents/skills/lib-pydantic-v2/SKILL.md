---
name: lib-pydantic-v2
description: 'Use this skill to pydantic v2 model, validation, and serialization patterns
  used across FLEXT. Use when creating models, adding validators, using ConfigDict,
  TypeAdapter, or model_validate/model_dump. DO NOT USE FOR: questions unrelated to
  lib-pydantic-v2 creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Pydantic V2 — Models, Validators, and Adapters

**UTILITY SKILL**

## USE FOR

- Requests about lib pydantic v2.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-pydantic-v2.
- creating projects or architecture from scratch.

## Workflow

1. Find nearest existing model in the same subproject for pattern reference
2. Use `ConfigDict` (never `class Config:`) with explicit `extra=` and `validate_assignment=`
3. Add `u.Field(description=...)` on all public fields

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
