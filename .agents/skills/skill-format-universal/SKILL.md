---
name: skill-format-universal
description: 'Canonical format for project SKILL.md files using Anthropic standards and FLEXT evidence. Use when creating or rewriting any skill.'
license: MIT
metadata:
  version: 1.0.0
---
# Skill Format Universal

## Required shape

```text
---
name: lowercase-kebab-case
description: One sentence stating the trigger and concrete scope.
license: MIT
metadata:
  version: 1.0.0
---
# Human-readable title

## Workflow
1. Inspect the canonical owner and inputs.
2. Apply the task-specific decision.
3. Run the exact validation that proves the outcome.
```

Add `Rules`, `Validation`, `Examples`, or `References` only when they carry
task-specific information. Link detailed material from `references/` instead of
copying it into `SKILL.md`.

## Quality bar

- Keep the trigger precise enough for automatic routing.
- Use imperative, executable steps and canonical repository commands.
- State exceptions beside the rule they qualify.
- Remove generic advice, placeholder examples, repeated governance, and empty sections.
- Keep all prose in English and verify every referenced path.
- Keep the manifest focused; move detailed explanations and catalogs to references.
- Keep `SKILL.md`, `rules.yml`, rule files, fixtures, and validation behavior synchronized.

## Validation

Skill directories remain declarative. Validate them through the canonical workspace
service and Make dispatcher:

```bash
make val VALIDATE_SCOPE=workspace
```

The canonical `flext-infra` skill validator owns YAML parsing, typed rule models,
catalog reconciliation, scan execution, reports, and stable exit semantics. Do not add
a skill-local CLI, parser, scanner, shell wrapper, or direct CI entry point.
