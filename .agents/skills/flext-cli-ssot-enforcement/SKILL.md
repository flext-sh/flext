---
name: flext-cli-ssot-enforcement
description: 'Use this skill to use ALWAYS when working in any flext workspace project
  to ensure flext-cli SSOT for CLI domain (typer/click/rich/tabulate/process-exec/json/yaml/csv/toml/prompts/output)
  is not violated. Auto-fail violations. DO NOT USE FOR: questions unrelated to flext-cli-ssot-enforcement
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# flext-cli SSOT enforcement

**UTILITY SKILL**

## USE FOR

- Requests about flext cli ssot enforcement.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-cli-ssot-enforcement.
- creating projects or architecture from scratch.

## Workflow

1. Understand.
2. Execute.
3. Validate.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- **ADR-005:** `flext-cli` is the SSOT owner of the universal file/output/CLI/
  formatting engine **and** of config/template/schema routines —
  `u.Cli.render_template` (Jinja2), `u.Cli.config_load`/`config_load_dir`
  (multi-format, YAML default, env-override + merge), `u.Cli.yaml_validate_schema`
  (JSON Schema). Consumers must route these through `u.Cli.*`, never re-implement
  yaml/toml/json/jinja2/jsonschema locally.
  Canonical: `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
