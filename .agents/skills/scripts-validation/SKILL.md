---
name: scripts-validation
description: 'Use this skill to validation services — policy gates, automated checks,
  ast-grep enforcement, and workspace validation. Use when using flext_infra.check
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

1. Identify the validation invariant to enforce.
2. Add rules to the relevant skill's `rules.yml` (type: ast-grep or custom).
3. Place ast-grep rule files in the skill's `rules/` directory.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
