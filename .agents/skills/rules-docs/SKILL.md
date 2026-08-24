---
name: rules-docs
description: 'Use this skill to rules for documentation under `docs/` to keep architecture
  and project guides aligned with current code and policy. Use when editing docs pages
  or docs structure. DO NOT USE FOR: questions unrelated to rules-docs creating projects
  or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---

# Rules Docs

**UTILITY SKILL**

## USE FOR

- Requests about rules docs.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to rules-docs.
- creating projects or architecture from scratch.

## Workflow

1. **Pre-scan**: identify affected docs pages and ownership boundaries.
2. **Remediation**: update content with concrete source anchors and canonical governance references.
3. **Verification**: validate links/paths and remove stale references.

## Critical rules

- Prefer canonical sources.
- Require evidence before claiming success.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
- Missing context → state assumptions.

## References

<!-- mro-lo34 (agent: kimi) — canonical ADR refs added per docs-renaissance S1. -->
- `docs/GOVERNANCE.md` — controls, ADR routing, canonical workflow
- `docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md` — template/config/schema SSOT the docs engine renders through
- `make docs DOCS_PHASE=<generate|fix|audit|build|validate>` — flext-infra docs engine entrypoint
