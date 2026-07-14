---
name: flext-cli-ssot-enforcement
description: 'Use this skill to use ALWAYS when working in any flext workspace project
  to ensure flext-cli SSOT for CLI domain (typer/click/rich/tabulate/process-exec/json/yaml/csv/toml/prompts/output)
  is not violated. Auto-fail violations. DO NOT USE FOR: questions unrelated to flext-cli-ssot-enforcement
  creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.1.0
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

<!-- mro-wkii.17.26 (agent: codex) — define the reusable operational CLI kernel. -->
1. Validate external CLI/Make input exactly once into the owning request model.
2. Resolve a statically generated command binding to a typed handler.
3. Execute through the declared in-process or process adapter and preserve the
   same model/result object across internal layers.
4. Propagate `r[T]` failures unchanged; the terminal handler logs and renders an
   error exactly once at the outermost CLI boundary.
5. Validate native CLI and Make bindings against the same generated catalog.

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
- **ADR-007:** `flext-cli` owns the closed operational kernel for typed command
  catalogs, handlers, process streaming, cancellation, mutation plans, and
  terminal outcomes. Projects extend it with models, protocols, declarative
  specs, policies, and handlers; config never carries callables or dotted
  imports. `flext-infra` generates bindings and validates them but never owns
  runtime command behavior.
- Dry-run of a mutating command must produce a typed operation plan. Skipping
  the handler and returning success is forbidden.
- Require evidence from the public CLI/Make surface, exit code, emitted result,
  and exactly-once terminal logging.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
