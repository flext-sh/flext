---
name: flext-config-settings
description: 'Use this skill to pydantic ConfigDict and singleton settings patterns
  across FLEXT subprojects. Use when editing settings.py models, env bindings, or
  configuration validation behavior. DO NOT USE FOR: questions unrelated to lib-pydantic-settings
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Lib Pydantic Settings

**UTILITY SKILL**

## USE FOR

- Requests about lib pydantic settings.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to lib-pydantic-settings.
- creating projects or architecture from scratch.

## Workflow

1. Inherit `FlextSettings` — never `FlextSettings`/`BaseSettings`/`BaseModel`.
2. Define `model_config = m.SettingsConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
3. Declare ONLY project-specific fields (rule-3 isolation; redeclare root-like

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
