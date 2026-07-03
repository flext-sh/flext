---
name: flext-5agent-coordination
description: 'Use this skill to use when coordinating 5 parallel agents on flext-core
  or consumer project work. Covers execution ritual (11 Commandments), ownership matrix,
  phase sequencing, lint scoping, and git hygiene for zero-conflict parallel delivery.
  Authoritative source: AGENTS.md §10. DO NOT USE FOR: questions unrelated to flext-5agent-coordination
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# 5-Agent Parallel Execution Protocol

**UTILITY SKILL**

## USE FOR

- Requests about flext 5agent coordination.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-5agent-coordination.
- creating projects or architecture from scratch.

## Workflow

1. Agent 4 implements Wave 0: RuntimeResult.**slots**, `r[T].fail()`, p.Result
2. Agent 4 runs full lint: `cd flext-core && make check`
3. Agent 4 commits and pushes

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
