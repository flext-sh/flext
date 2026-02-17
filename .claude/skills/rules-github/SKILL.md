---
name: rules-github
description: Rules for GitHub automation files in `.github/`, including workflows, templates, and dependency policy. Use when editing CI/CD or repo automation config.
---

# Rules GitHub

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope
- `.github/workflows/`
- `.github/copilot-instructions.md`
- `.github/dependabot.yml`

## References
- `.github/workflows/flx_comprehensive_tests.yml`
- `.github/workflows/docs_maintenance.yml`
- `.github/dependabot.yml`
- `AGENTS.md`

## Rules
- Keep workflow triggers explicit (`on:` paths/branches/events).
- Keep job names meaningful and aligned with reported checks.
- Keep policy pointer files concise and linked to canonical source.
- Update docs/policy references when workflow names change.

## Instructions
- Validate workflow syntax and key blocks (`name`, `on`, `jobs`).
- Keep secrets/environment references scoped and explicit.
- For documentation workflows, ensure path filters match docs locations.

```bash
ls -la .github/workflows
```

## Workflow
1. Select workflow/template to change.
2. Update trigger and job blocks intentionally.
3. Validate consistency with project Makefile/gates.
4. Recheck dependent docs or pointer files.

## Examples
Good:

```yaml
name: FLEXT Comprehensive Tests
on:
  pull_request:
```

Why good: explicit workflow identity and trigger event.

Bad:

```yaml
on: [push]
```

Why bad: overly broad trigger often causes unnecessary CI load and unclear intent.

## Verification
- `ls -la .github/workflows`
- `rg -n "^name:|^on:|^jobs:" .github/workflows/*.yml`
- `rg -n "Canonical source|CLAUDE.md" .github/copilot-instructions.md`
- `rg -n "TODO|FIXME" .github || true`
