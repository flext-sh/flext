---
name: pydantic-v2-patterns
description: 'Use this skill for advanced declaration-only Pydantic v2 composition
  in FLEXT: strict frozen models, Annotated constraints, model unions, protocol
  interfaces, MRO reuse, and boundary-once validation. DO NOT USE FOR: unrelated
  questions or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Pydantic v2 Patterns

**UTILITY SKILL**

<!-- mro-wkii.17 (agent: codex) — keep only declaration patterns compatible with direct protocol flow. -->

## USE FOR

- Requests about pydantic v2 patterns.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to pydantic-v2-patterns.
- creating projects or architecture from scratch.

## Workflow

1. Read `pydantic-v2-governance` HARD Rules Checklist and Forbidden Structures.
2. Read `lib-pydantic-v2` for API policy deltas.
3. Reuse the source model/protocol directly when semantics are unchanged.
4. Select only field declarations, immutable constraints, and discriminated model unions.

## Critical rules

- Prefer canonical sources.
- Models contain fields only; behavior and serialization adapters live outside them.
- Internal interfaces pass canonical model objects directly through protocols.
- No TypeAdapter reconstruction, dump/revalidate roundtrip, or duplicate DTO.
- No custom validator, local upstream alias, name-only subclass, or parallel convenience API.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.

## References

- [references/patterns-detail.md](references/patterns-detail.md)
