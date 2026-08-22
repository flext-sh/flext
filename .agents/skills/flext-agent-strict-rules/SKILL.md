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
   aliases. The ast-grep MCP may assist read-only navigation under the newest
   operator order, but Rope remains the static enforcement/fix authority;
   runtime `ast` and `get_ast` remain forbidden in the enforcement path.
4. Preserve facade order `c -> t -> p -> m -> u`: use the canonical upstream
   alias as the MRO base and define one nested project namespace per concern.
5. Reverse facade edges are FORBIDDEN entirely (ADR-011): never under runtime and
   never under `TYPE_CHECKING`. Every name in a runtime-evaluated annotation is a
   top-level runtime import (facades are forward: `m` imports `p,t,c`; `u` imports
   `m,p,t,c`). `TYPE_CHECKING` is reserved for the generated static-declaration
   half of the root PEP 562 lazy public export only.
6. Measure tool diagnostics against the canonical `flext-core`/`flext-cli`
   pattern. Keep only the closed, globally documented MRO/lazy incompatibility
   codes disabled and propagate them through the tooling SSOT.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- Apply supreme responsibility before every mutation: understand the complete
  contract, consumers, generated surfaces, blast radius, cutover and real gates.
- Never rush or produce partial, simplistic, opaque, fake, incomplete, or
  broken code/config/templates/docs/automation — not even as an intermediate.
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
