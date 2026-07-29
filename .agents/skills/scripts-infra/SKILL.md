---
name: scripts-infra
description: 'Guidance for core infrastructure services — validation, inventory, scanning, and skill orchestration. Use when using flext_infra.core or editing scripts/lib/, scripts/core/, scripts/settings/, scripts/makefiles/, or scripts/common.py.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Infra

## Workflow

1. Identify the shared lib or infra file to modify.
2. Check which scripts source/import it via `rg 'source.*common.sh' scripts/` or `rg 'from.*core.*import' scripts/`.
3. Apply minimal change.

## Enforced contracts

- Every script must have Owner-Skill marker.
- Scripts should use portable shebang.
- Gate scripts should use standard exit codes (0/1/2/3).

## Resources

- [`rules/gate-contract-exit-codes.yml`](rules/gate-contract-exit-codes.yml)
- [`rules/owner-skill-marker.yml`](rules/owner-skill-marker.yml)
- [`rules/shebang-env-bash.yml`](rules/shebang-env-bash.yml)
