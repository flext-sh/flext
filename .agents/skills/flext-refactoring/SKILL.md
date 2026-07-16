---
name: flext-refactoring
description: 'Use this skill to step-by-step refactoring workflow with quality gates,
  make targets, and commit discipline for the FLEXT monorepo. Use when refactoring
  a module, extracting mixins, decomposing classes exceeding the 200-line cap, migrating
  legacy patterns to current MRO/facade. DO NOT USE FOR: questions unrelated to flext-refactoring-workflow
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.1.0
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
6. For a workspace, open one Rope project over the manifest and index every
   FLEXT technology member. Project-only mode is valid only when no workspace
   manifest/root can be discovered.
7. Emit every codegen, Rope, template, and safe ast-grep change into one ordered
   patch plan in a temporary worktree. Validate preimages, collisions, imports,
   breakage, four type/lint gates, and pytest before apply; the next run must be
   empty.

## Critical rules

- Prefer canonical sources.
- Require evidence.
<!-- mro-wkii.17.26 (agent: codex) — standardize safe decompositions around one facade and no parallel paths. -->
- Decompose long modules universally as `<layer>/<domain>.py` (thin
  MRO/composition facade) plus `<layer>/_<domain>/*.py` (small responsibility
  mixins). Use Rope-semantic dependency/SCC evidence and `rg`/`sg` textual
  proof. Generate every internal `__init__.py` at arbitrary depth with explicit
  relative same-name re-exports of direct sibling symbols and a deterministic
  literal tuple `__all__`, including an empty tuple when no direct symbol exists;
  never flatten descendants or emit a docstring-only initializer. Reserve PEP 562
  lazy exports for the production package root. Never retain the former module
  as a wrapper or compatibility path.
- Static enforcement of refactor invariants is config DATA in `flext-infra/config/*.yaml` over the
  rope-semantic fact base (LAW1); this workflow never adds detector code or `ast`/`get_ast`-based checks (LAW2).
<!-- mro-wkii.17.26 (agent: codex) — bind ast-grep automation to the canonical cooperative catalog. -->
- `~/.ai-hub/ast-grep-rules` is the cooperative SSOT for structural sensors and
  proven-safe codemods. Each rule requires valid/invalid fixtures, cardinality,
  deterministic preview, and idempotence. Ast-grep never owns semantic truth;
  Rope facts and the conform transaction accept or reject its proposed edits.
- Never run broad `ruff --fix`, regex rewrites, or Python AST rewrites after a
  codemod. Formatting is a separate explicit planned change; semantic movement
  remains Rope-owned.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
