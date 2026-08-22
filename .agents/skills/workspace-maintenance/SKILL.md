---
name: workspace-maintenance
description: 'Use this skill to use when running workspace-wide maintenance tasks
  across all FLEXT submodules. Covers hygiene checks, dependabot settings standardization,
  Poetry health validation, and security enforcement automation. DO NOT USE FOR: questions
  unrelated to workspace-maintenance creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.1.0
---
# Workspace Maintenance

**UTILITY SKILL**

## USE FOR

- Requests about workspace maintenance.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to workspace-maintenance.
- creating projects or architecture from scratch.

## Workflow

<!-- mro-wkii.17.26 (agent: codex) — make workspace discovery and transactions explicit. -->
1. Discover the workspace root and load its declared project manifest.
2. Include every declared FLEXT-technology member and open one shared Rope
   semantic index. Use project mode only when workspace discovery proves that
   the project is standalone.
3. Establish a merge-clean, importable, four-lint, pytest-green baseline.
4. Run maintenance through `flext-infra conform` in a temporary worktree:
   dry-run, inspect the patch/cardinality, patch-check, import/breakage checks,
   full scoped gates, then explicit apply.
5. For structural sensors/codemods, consume the versioned cooperative catalog
   at `~/.ai-hub/ast-grep-rules`; reconcile its proposals against Rope facts.
6. For cross-workspace tooling distribution, use `make workspaces WHAT=status`
   and the documented apply verb from `~/.ai-hub` only after dry-run proof.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- Writers are deterministic and serialized; read-only analysis may parallelize
  only where the dependency/SCC plan proves independence.
- A transaction is accepted only when its immediate second run plans no changes.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
