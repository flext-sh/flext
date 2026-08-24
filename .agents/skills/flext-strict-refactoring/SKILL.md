---
name: flext-strict-refactoring
description: 'Use this skill to strict cleanup rules for removing duplicated policy,
  stale guidance, and weak refactor prompts across FLEXT governance surfaces. Use
  when editing AGENTS.md, pointer docs, or meta-skills so startup law stays short,
  hard, and aligned with canonical execution rules. DO NOT USE FOR: questions unrelated
  to flext-strict-refactoring creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Flext Strict Refactoring

**UTILITY SKILL**

## USE FOR

- Requests about flext strict refactoring.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-strict-refactoring.
- creating projects or architecture from scratch.

## Workflow

1. Run `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`.
2. Read `AGENTS.md` §0 and isolate the exact recurring failure.
3. Patch `AGENTS.md` first only if the law changes.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
