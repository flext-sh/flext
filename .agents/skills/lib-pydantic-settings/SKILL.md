---
name: lib-pydantic-settings
description: 'Pydantic ConfigDict and singleton settings patterns across FLEXT subprojects. Use when editing settings.py models, env bindings, or configuration validation behavior.'
license: MIT
metadata:
  version: 1.0.0
---
# Lib Pydantic Settings

## Workflow

1. Inherit `FlextSettingsBase` — never `FlextSettings`/`BaseSettings`/`BaseModel`.
2. Define `model_config = m.SettingsConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
3. Declare ONLY project-specific fields (rule-3 isolation; redeclare root-like

## Enforced contracts

- Legacy Pydantic class Config is banned in settings modules.
- Settings modules should define env_prefix explicitly.

## Resources

- [`rules/legacy-config-fix.yml`](rules/legacy-config-fix.yml)
- [`rules/legacy-config.yml`](rules/legacy-config.yml)
- [`rules/require-env-prefix.yml`](rules/require-env-prefix.yml)
