---
name: flext-architecture-layers
description: 'Use this skill to layer map and dependency-direction contract for flext-core.
  Use when adding modules, moving responsibilities, or reviewing imports. **Reviewed**:
  2026-04-06 | **Scope**: Added mandatory FlextMeltano composition rule, alias set,
  composition matrix, and. DO NOT USE FOR: questions unrelated to flext-architecture-layers
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Architecture Layers

**UTILITY SKILL**

## USE FOR

- Requests about flext architecture layers.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-architecture-layers.
- creating projects or architecture from scratch.

## Workflow

1. Assign each touched module to L0/L1/L2/L3 before editing.
2. **For cross-project changes**: Identify the correct domain project using the Selection Rule above. NEVER guess.
3. Inspect imports for outward dependencies.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- **ADR-005 (config SSOT) layering:** `flext-core` is runtime-minimal — stdlib
  only (`tomllib` + `string.Template`), **no Jinja2**, and **never imports
  `flext-cli`/`flext-infra` at runtime** (examples/scripts/tests only).
  `flext-cli` owns the universal template/config/schema engine
  (`u.Cli.render_template`, `config_load`, `yaml_validate_schema`) and amplifies the
  core contracts. `flext-infra` consumes cli and hosts enforcement. Direction:
  `flext-infra → flext-cli → flext-core`, no cycle.
  Canonical: `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
