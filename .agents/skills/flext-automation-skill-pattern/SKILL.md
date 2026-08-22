---
name: flext-automation-skill-pattern
description: 'Use this skill to canonical pattern for creating reusable automation
  skills whose invariants are declared as config data in flext-infra/config/*.yaml and enforced by
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
2. Declare the rule as Pydantic-2-validated DATA in `flext-infra/config/enforcement/*.yaml`
   (closed operator set over the rope-semantic fact base). Skills never own rule data or detector
   code; bespoke/custom detectors and ast-grep rule files are banned (LAW1/LAW2).
3. Run standardized gate on target project with `make val PROJECT=<name>`.

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
