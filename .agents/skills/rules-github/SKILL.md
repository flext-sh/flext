---
name: rules-github
description: 'Rules for GitHub automation files in `.github/`, including workflows, templates, and dependency policy. Use when editing CI/CD or repo automation settings.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules GitHub

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

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — verify CI workflow references match real scripts
- `make check PROJECT=flext-core` — verify CI-referenced gates work

File checks:

- `ls -la .github/workflows`
- `rg -n "^name:|^on:|^jobs:" .github/workflows/*.yml`
- `rg -n "Canonical source|AGENTS.md" .github/copilot-instructions.md`
- `rg -n "TODO|FIXME" .github || true`
