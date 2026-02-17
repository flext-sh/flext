---
name: flext-refactoring-workflow
description: Refactoring workflow focused on low-risk, evidence-backed changes.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/context/core/agent-patterns.md`
- `/home/marlonsc/flext/docs/planning/phase1_detailed_plan.md`
- `/home/marlonsc/flext/docs/planning/phases7_9_completion.md`

## Enforced Rules

- Guideline: split refactors into independent steps with explicit validation after each step.
- Guideline: preserve behavior while reducing ambiguity and duplication.

## Guidance

- Use phase-plan style checklists for non-trivial refactors.
- Keep file-level rationale in commit-ready notes for review traceability.

## Examples

- Plan documents in `docs/planning/` show good task/checklist/validation formatting to mirror.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-refactoring-workflow/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-refactoring-workflow/SKILL.md`
