---
name: flext-strict-refactoring
description: Strict refactor guardrails for removing ambiguous or contradictory documentation/policy text.
scope: /home/marlonsc/flext/
tags: [skills,workflow,patterns]
last_verified: 2026-02-17
---

## Applies To

- `/home/marlonsc/flext/`

## Sources

- `/home/marlonsc/flext/CLAUDE.md`
- `/home/marlonsc/flext/AGENTS.md`
- `/home/marlonsc/flext/context/core/error-handling.md`

## Enforced Rules

- Guideline: delete stale guidance instead of layering contradictory caveats on top.
- Guideline: preserve one canonical statement for each behavior and cross-reference from others.

## Guidance

- Use this skill when consolidating overlapping docs and policy files.
- After strict refactors, verify that references still point to valid files.

## Examples

- Single-source policy in root CLAUDE is the anchor for strict documentation refactors.

## Verification

- `rg -n "^##\s+Guidance$" .claude/skills/flext-strict-refactoring/SKILL.md`
- `rg -n "`/home/marlonsc/flext/" .claude/skills/flext-strict-refactoring/SKILL.md`
