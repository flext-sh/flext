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
3. Update every impacted caller through the Rope semantic fact base and public
   aliases. AST, `get_ast`, AST-grep, and parallel textual semantic engines are
   forbidden.
4. Preserve facade order `c -> t -> p -> m -> u`: use the canonical upstream
   alias as the MRO base and define one nested project namespace per concern.
5. Use `TYPE_CHECKING` only for a reverse facade edge, a proven runtime cycle,
   or the generated static declaration half of a PEP 562 lazy public export.
6. Measure tool diagnostics against the canonical `flext-core`/`flext-cli`
   pattern. Keep only the closed, globally documented MRO/lazy incompatibility
   codes disabled and propagate them through the tooling SSOT.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- MRO/OO and generated lazy public exports are mandatory in every project.
- Never change the architecture to satisfy a generic linter default.
- Never generalize an approved diagnostic exception or add a per-file ignore.
- Mypy `no-redef` stays globally disabled because facade modules intentionally
  rebind the exact upstream `c/t/p/m/u` alias to the composed local facade.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
