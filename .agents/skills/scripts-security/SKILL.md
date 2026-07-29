---
name: scripts-security
description: 'Use when editing security automation for secret handling, vault operations, dependency auditing, credential-safe output, or canonical security Make gates.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Security

## Workflow

1. Identify the security concern to address.
2. Create or modify the script under `scripts/security/`.
3. Ensure the script extends `_base_security_script.py` if applicable.

## Enforced contracts

- Every security script must declare Owner-Skill marker.
- Security scripts should include a module docstring.

## Resources

- [`rules/require-docstring.yml`](rules/require-docstring.yml)
- [`rules/require-owner-skill-marker.yml`](rules/require-owner-skill-marker.yml)
