---
name: flext-agent-strict-rules
description: 'Use this skill to mandatory runtime alias and typing discipline for
  all coding agents. Use when writing or reviewing FLEXT code to enforce alias-only
  access (c/m/r/t/u/p), isinstance/TypeGuard narrowing (never type()), centralized
  Pydantic v2 models over polymorphic functions, and. DO NOT USE FOR: questions unrelated
  to flext-agent-strict-rules creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Agent Strict Rules

**UTILITY SKILL**

## USE FOR

- Requests about flext agent strict rules.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-agent-strict-rules.
- creating projects or architecture from scratch.


## Workflow

1. Identify which operational cluster (1–5 above) applies to the change.
2. Apply the canonical pattern without introducing compatibility layers.
3. Update all impacted call sites/contracts via `ast-grep` (`AGENTS.md` §3.5).


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
