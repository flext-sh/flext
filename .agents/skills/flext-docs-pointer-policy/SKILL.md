---
name: flext-docs-pointer-policy
description: 'Use this skill to use when creating or editing documentation across
  AGENTS.md, skills, README files, or agent configs. Enforces the one-root-source
  policy: single authoritative document with lightweight pointers everywhere else.
  No duplication of governance across files. DO NOT USE FOR: questions unrelated to
  flext-docs-pointer-policy creating projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Docs Pointer Policy

**UTILITY SKILL**

## USE FOR

- Requests about flext docs pointer policy.
- Workflows described in this skill.
- Operator tasks within this scope.


## DO NOT USE FOR

- questions unrelated to flext-docs-pointer-policy.
- creating projects or architecture from scratch.


## Workflow

1. **Pre-scan**: inventory pointer files and identify drift from canonical wording.
2. **Remediation**: update references and remove duplicated policy content.
3. **Propagation**: when AGENTS or a core skill/prompt becomes stricter, update remaining pointers in the same cycle.


## Critical rules

- Prefer canonical sources.
- Require evidence.


## Example

**Input:** a request.
**Output:** a concise response.


## Troubleshooting

- Unclear scope → ask.
