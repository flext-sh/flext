---
name: readme-standardization
description: 'Use this skill to use when creating, updating, or auditing README.md
  files across the FLEXT ecosystem. Covers required sections, structure templates,
  badge standards, and tooling for consistent README generation and maintenance. DO
  NOT USE FOR: questions unrelated to readme-standardization creating projects or
  architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# README Standardization Skill

**UTILITY SKILL**

## USE FOR

- Requests about readme standardization.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to readme-standardization.
- creating projects or architecture from scratch.

## Workflow

1. Discover README drift from expected structure.
2. Confirm the project's parent MRO chain, abstracted libraries, and primary skills before drafting the Collection Rules section.
3. Apply safe automatic fixes via `make docs DOCS_PHASE=fix`, then manual content adjustments only where the auto-generator cannot derive content (purpose, onboarding narrative, operation flow).

## Critical rules

- Prefer canonical sources.
- Require evidence.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.

## References

<!-- mro-lo34 (agent: kimi) — canonical ADR refs added per docs-renaissance S1. -->
- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md` — READMEs are generated through the canonical template engine (SSOT)
- `make docs DOCS_PHASE=generate` — flext-infra engine regenerates project READMEs deterministically
- `docs/GOVERNANCE.md` — controls and ADR routing
