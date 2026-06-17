---
name: flext-automation-skill-pattern
description: 'Use this skill to canonical pattern for creating reusable automation
  skills with script-first validation, baseline/strict enforcement modes, and companion
  docs. Use when building new automation skills that must be repeatable across the
  FLEXT repo, or when standardizing. DO NOT USE FOR: questions unrelated to flext-automation-skill-pattern
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Automation Skill Pattern

**UTILITY SKILL**

## USE FOR

- Requests about flext automation skill pattern.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-automation-skill-pattern.
- creating projects or architecture from scratch.


## Workflow

1. Define the invariant (policy or quality behavior).
2. Create `rules.yml` with detection rules (ast-grep, ripgrep, or custom).
3. Run standardized gate on target project with `make val PROJECT=<name>`.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
