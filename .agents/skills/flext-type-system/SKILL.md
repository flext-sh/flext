---
name: flext-type-system
description: 'Use this skill to canonical FLEXT type-system map for aliases, generics,
  result interplay, and settings contracts. Use when changing shared typing primitives.
  **Reviewed**: 2026-04-20 | **Scope**: Type-system map — aliases, generics, result
  interplay, settings contracts, p.* protocols. DO NOT USE FOR: questions unrelated
  to flext-type-system creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Type System

**UTILITY SKILL**

## USE FOR

- Requests about flext type system.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-type-system.
- creating projects or architecture from scratch.

## Workflow

1. Locate existing alias/type-var nearest to intended change.
2. Extend or refine canonical alias in `typings.py`.
3. Validate impacted consumers in result/settings/protocol modules.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- **ADR-005:** config carries typed contracts — `p.Config*` protocols,
  `m.Config*` frozen Pydantic v2 records (config + schema-ref), and `t.Config*`
  aliases originate in `flext-core` (runtime-minimal) and are amplified by
  `flext-cli`. Type config payloads against these contracts, never `Any`/dict.
  Canonical: `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
