---
name: scripts-validation
description: 'Use this skill to validation services — policy gates, automated checks,
  declarative rope-based enforcement, and workspace validation. Use when using flext_infra.check
  or editing scripts/validation/. DO NOT USE FOR: questions unrelated to scripts-validation
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Scripts Validation

**UTILITY SKILL**

## USE FOR

- Requests about scripts validation.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to scripts-validation.
- creating projects or architecture from scratch.

## Workflow

1. Identify the static validation invariant to enforce.
2. Declare the rule as DATA in `flext-infra/config/enforcement/*.yaml` (Pydantic-2 validated);
NEVER as Python rule logic and NEVER as an ast-grep rule file (LAW1).
3. The rule is evaluated by the shared rope-semantic engine (`ctx.rope_project`);
`ast`, `ast-grep`, and `PyModule.get_ast()` are forbidden (LAW2).

## Critical rules

- Prefer canonical sources.
- Require evidence.
- Static enforcement rules are 100% config DATA (`flext-infra/config/*.yaml`), never Python code
  or ast-grep rule files (LAW1; memory:adr005-p3-rules-as-data-law).
- Static analysis is rope-semantic ONLY; `ast`, `ast-grep`, and `PyModule.get_ast()` are banned
  (LAW2; memory:adr005-p3-single-rope-loop). Canonical: `docs/architecture/adr/005-...md`.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
