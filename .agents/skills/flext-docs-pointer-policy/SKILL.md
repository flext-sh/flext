---
name: flext-docs-pointer-policy
description: 'Guidance for creating or editing documentation across AGENTS.md, skills, README files, or agent configs. Enforces the one-root-source policy: single authoritative document with lightweight pointers everywhere else. No duplication of governance across files.'
license: MIT
metadata:
  version: 1.0.0
---
# Flext Docs Pointer Policy

## Workflow

1. **Pre-scan**: inventory pointer files and identify drift from canonical wording.
2. **Remediation**: update references and remove duplicated policy content.
3. **Propagation**: when AGENTS or a core skill/prompt becomes stricter, update remaining pointers in the same cycle.

## Contracts

- Pointer files must reference the canonical 'AGENTS.md' policy.
- Pointer files must not reference legacy canonical names.
- Pointer files should not duplicate full policy or architecture content.
