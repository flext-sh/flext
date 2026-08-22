---
name: pydantic-v2-governance
description: 'Use this skill for declaration-only Pydantic v2 models, protocol-based
  interfaces, boundary-once validation, and direct source-object reuse across FLEXT.
  DO NOT USE FOR: questions unrelated to Pydantic governance or architecture from
  scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Pydantic v2 Governance

**UTILITY SKILL**

<!-- mro-wkii.17 (agent: codex) — bind interfaces to protocols and preserve canonical model identity. -->

## USE FOR

- Requests about pydantic v2 governance.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to pydantic-v2-governance.
- creating projects or architecture from scratch.

## Workflow

1. Read the live U14, U17, U18, and U19 rules in `AGENTS.md`.
2. Find the canonical source `m.*` model and `p.*` protocol before declaring anything.
3. Read `lib-pydantic-v2` for boundary API rules.
4. Read `pydantic-v2-patterns` for declaration-only composition patterns.

## Critical rules

- Prefer canonical sources.
- Validate exactly once at a true external boundary.
- Pass the original validated model instance through protocol contracts.
- Annotate `u`/`services`/`api` signatures (params and returns) and collaborator/DI fields with the owning `p.*` protocol, imported at runtime (ADR-011). Data/payload fields — including nested and composed (`list`/`dict` of models) — are concrete `m.*`, never a bare protocol (a protocol-typed data field cannot deserialize a dict or serialize). Never gate an annotation name under `TYPE_CHECKING`.
- Never use internal dump/revalidate roundtrips or model-less payload contracts.
- Redeclare only for a documented domain semantic change.
- Do not create local aliases, wrapper APIs, or parallel execution branches for an unchanged upstream contract.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.

## References

- [references/governance-patterns.md](references/governance-patterns.md)
