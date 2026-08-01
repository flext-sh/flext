---
name: pydantic-v2-patterns
description: 'Advanced Pydantic v2 implementation patterns for FLEXT — TypeAdapter caching, RootModel vs BaseModel, Annotated validators, discriminated unions, computed_field, PrivateAttr, facade-only imports. Use when implementing complex model hierarchies, chaining validators.'
license: MIT
metadata:
  version: 1.0.0
---
# Pydantic v2 Patterns

## Workflow

1. Read `pydantic-v2-governance` HARD Rules Checklist and Forbidden Structures.
2. Read `lib-pydantic-v2` for API policy deltas.
3. Select the needed pattern family (validators, computed fields, unions, serializers, strict mode, TypeAdapter, RootModel, Annotated).

## References

- [`references/patterns-detail.md`](references/patterns-detail.md)
