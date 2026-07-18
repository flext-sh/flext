---
name: flext-pydantic-models
description: 'Use this skill for declaration-only Pydantic v2 models, boundary-once
  validation, canonical protocol interfaces, and direct source-object reuse in FLEXT.
  DO NOT USE FOR: unrelated questions or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Pydantic V2 — Canonical Models and Boundary Adapters

<!-- mro-wkii.17 (agent: codex) — keep Pydantic guidance on one identity-preserving boundary path. -->

**UTILITY SKILL**

## USE FOR

- Requests about lib pydantic v2.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-pydantic-v2.
- creating projects or architecture from scratch.

## Workflow

1. Find the canonical source model and protocol before declaring a local contract.
2. Reuse them directly when the domain semantics are unchanged.
3. If a domain delta justifies a model, declare fields only with `ConfigDict` and immutable defaults.
4. Validate exactly once at the true external ingress boundary through the owning `flext-cli` adapter.
5. Pass the same validated instance through `p.*` contracts and serialize only at the true external egress.

## Critical rules

- Prefer canonical sources.
- Models contain no custom methods, validators, computed fields, serializers, or private state.
- `u`/`services`/`api` signatures and collaborator/DI fields use the owning `p.*` protocol (imported at runtime, forward `u → p`); data/payload and nested/composed fields are concrete `m.*` (ADR-011). `m.*` constructs the canonical boundary object and is passed through `p.*` unchanged.
- Internal layers pass the original validated model object through `p.*` protocols.
- Internal `model_dump`/`model_validate` roundtrips and TypeAdapter copies are forbidden.
- `dict`, JSON-shaped objects, `TypedDict`, dataclass, and duplicate DTO contracts are forbidden.
- Serialization belongs only to a true external egress adapter.
- Duplicate loaders, writers, renderers, convenience APIs, and compatibility branches are forbidden.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
