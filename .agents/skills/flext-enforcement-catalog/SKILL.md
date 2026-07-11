---
name: flext-enforcement-catalog
description: 'Use this skill for the canonical index of enforcement rules. flext-core
  c.ENFORCEMENT_CATALOG holds ONLY runtime/beartype rows; ALL static-code rules are declarative
  DATA in flext-infra/config/*.yaml (Pydantic-2 validated), evaluated by the shared rope-semantic
  engine (ast/ast-grep/get_ast banned). Use when adding, retiring, or cross-referencing any
  enforcement rule. DO NOT USE FOR: questions unrelated to flext-enforcement-catalog or creating
  projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# FLEXT Enforcement Catalog

**UTILITY SKILL**

## USE FOR

- Requests about flext enforcement catalog.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to flext-enforcement-catalog.
- creating projects or architecture from scratch.

## Workflow

1. Understand.
2. Execute.
3. Validate.

## Critical rules

- Prefer canonical sources.
- Require evidence.
- **ADR-005 static rules (planned, `mro-wkii.4` / `mro-wkii.4.8`):**
  `no-large-literal-in-constants`, `config-only-under-config-dir`, `template-not-inlined`,
  `config-requires-schema`, `config-settings-not-mixed` — declared as DATA in
  `flext-infra/config/enforcement/*.yaml` (Pydantic-2 validated, loaded via
  `u.Cli.config_load_dir`), NOT registered as Python rows in flext-core.
- **flext-core catalog = runtime/beartype residue ONLY; flext-infra/config = 100% of static rules as
  data** (memory:adr005-p3-core-runtime-only-split, memory:adr005-p3-rules-as-data-law).
- **Static analysis is rope-semantic ONLY; `ast` / `ast-grep` / `PyModule.get_ast()` are banned**
  (memory:adr005-p3-single-rope-loop).
  Canonical: `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
