---
name: rules-github
description: 'Use this skill to rules for GitHub automation files in `.github/`, including
  workflows, templates, and dependency policy. Use when editing CI/CD or repo automation
  settings. DO NOT USE FOR: questions unrelated to rules-github creating projects
  or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Rules GitHub

**UTILITY SKILL**

## Rules

- Keep workflow triggers explicit (`on:` paths/branches/events).
- Keep job names meaningful and aligned with reported checks.
- Keep policy pointer files concise and linked to canonical source.
- Update docs/policy references when workflow names change.

## Instructions

- Validate workflow syntax and key blocks (`name`, `on`, `jobs`).
- Keep secrets/environment references scoped and explicit.
- For documentation workflows, ensure path filters match docs locations.

## Workflow

1. Select workflow/template to change.
2. Update trigger and job blocks intentionally.
3. Validate consistency with project Makefile/gates.

## Examples

Good:

Why good: explicit workflow identity and trigger event.

Bad:

Why bad: overly broad trigger often causes unnecessary CI load and unclear intent.

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — verify CI workflow references match real scripts
- `make check PROJECT=flext-core` — verify CI-referenced gates work

File checks:

- `ls -la .github/workflows`
- `rg -n "^name:|^on:|^jobs:" .github/workflows/*.yml`
- `rg -n "Canonical source|AGENTS.md" .github/copilot-instructions.md`
- `rg -n "TODO|FIXME" .github || true`

## USE FOR

- Requests about rules github.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to rules-github.
- creating projects or architecture from scratch.

## Critical rules

- Prefer canonical sources.
- Require evidence before claiming success.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
- Missing context → state assumptions.
