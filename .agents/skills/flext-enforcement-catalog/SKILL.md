---
name: flext-enforcement-catalog
description: 'Use this skill to canonical index of cross-layer enforcement rules exposed
  as c.ENFORCEMENT_CATALOG (typed Pydantic SSOT in flext-core) and driven by the flext-tests
  pytest dispatcher. Use when adding, retiring, or cross-referencing any workspace
  enforcement rule, or when wiring a. DO NOT USE FOR: questions unrelated to flext-enforcement-catalog
  creating projects or architecture from scratch'
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
- **ADR-005 rules (planned, `mro-wkii.4`):** `no-large-literal-in-constants`,
  `config-only-under-config-dir`, `template-not-inlined`,
  `config-requires-schema`, `config-settings-not-mixed` — staged
  disabled→warn→error, registered in `c.ENFORCEMENT_CATALOG`.
  Canonical: `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
