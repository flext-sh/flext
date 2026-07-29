---
name: lib-pydantic-v2
description: 'Pydantic v2 model, validation, and serialization patterns used across FLEXT. Use when creating models, adding validators, using ConfigDict, TypeAdapter, or model_validate/model_dump.'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Pydantic V2 — Models, Validators, and Adapters

## Workflow

1. Find nearest existing model in the same subproject for pattern reference
2. Use `ConfigDict` (never `class Config:`) with explicit `extra=` and `validate_assignment=`
3. Add `u.Field(description=...)` on all public fields

## Enforced contracts

- Auto-fixable Pydantic v1 APIs: .dict(), parse_obj(), parse_raw(), .json().
- CRITICAL: model_rebuild() is strictly prohibited — resolve type references at definition time or use Protocols.
- Pydantic v1 from_orm() is banned.
- Pydantic v1 @validator decorator is banned.
- Pydantic v1 @root_validator decorator is banned.
