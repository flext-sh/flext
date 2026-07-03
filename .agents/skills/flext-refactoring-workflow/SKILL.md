---
name: flext-refactoring-workflow
description: 'Use this skill to step-by-step refactoring workflow with quality gates,
  make targets, and commit discipline for the FLEXT monorepo. Use when refactoring
  a module, extracting mixins, decomposing classes exceeding the 200-line cap, migrating
  legacy patterns to current MRO/facade. DO NOT USE FOR: questions unrelated to flext-refactoring-workflow
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Refactoring Workflow

**UTILITY SKILL**

## USE FOR

- Requests about flext refactoring workflow.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-refactoring-workflow.
- creating projects or architecture from scratch.

## Workflow

1. Baseline: run the 3 pre-edit commands from `AGENTS.md` §0.0.
2. Blast radius: use `scope`/`sg`/`grep` to map callers before first edit.
3. Deletion pass: remove wrappers, compat aliases, dead code, duplicated fields/methods first.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
