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
2. Blast radius: map callers with the rope-semantic model (`scope`/rope) before first edit; `grep`/`sg`
   are textual aids only, never the enforcement or semantic source of truth (LAW2: rope-only; `ast`/`get_ast` banned).
3. Define one thin domain facade and focused private implementation parts before moving code.
4. Deletion pass: remove wrappers, compat aliases, dead code, duplicated fields/methods first.
5. Cut over every consumer and delete the superseded path in the same green batch.

## Critical rules

- Prefer canonical sources.
- Require evidence.
<!-- mro-wkii.17.26 (agent: codex) — standardize safe decompositions around one facade and no parallel paths. -->
- Decompose long modules universally as `<layer>/<domain>.py` (thin
  MRO/composition facade) plus `<layer>/_<domain>/*.py` (small responsibility
  mixins). Use Rope-semantic dependency/SCC evidence and `rg`/`sg` textual
  proof, keep private `__init__.py` static/empty, and reserve generated PEP 562
  lazy exports for the production package root. Never retain the former module
  as a wrapper or compatibility path.
- Static enforcement of refactor invariants is config DATA in `flext-infra/config/*.yaml` over the
  rope-semantic fact base (LAW1); this workflow never adds detector code or `ast`/`get_ast`-based checks (LAW2).

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
