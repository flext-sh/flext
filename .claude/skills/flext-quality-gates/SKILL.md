---
name: flext-quality-gates
description: Quality gate checklist for code, docs, and rule updates in this workspace.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/context/core/agent-patterns.md`
- `/home/marlonsc/flext/context/development/testing-patterns.md`
- `/home/marlonsc/flext/flext-quality/docs/TESTING_WARNING_SYSTEM.md`

## Enforced Rules

- Guideline: every meaningful change should have explicit verification evidence.
- Guideline: avoid declaring completion without command output or file-based proof.

## Guidance

- For docs/rules updates, verify structure consistency with `rg` checks and path existence checks.
- For code updates, run diagnostics/tests/build relevant to modified scope.

## Examples

- Testing warning system doc provides scenario-driven checklist style that can be reused for quality reviews.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-quality-gates/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-quality-gates/SKILL.md`
