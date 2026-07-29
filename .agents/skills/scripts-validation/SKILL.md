---
name: scripts-validation
description: 'Guidance for validation services — policy gates, automated checks, ast-grep enforcement, and workspace validation. Use when using flext_infra.check or editing scripts/validation/.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Validation

## Workflow

1. Identify the validation invariant to enforce.
2. Add rules to the relevant skill's `rules.yml` (type: ast-grep or custom).
3. Place ast-grep rule files in the skill's `rules/` directory.

## Enforced contracts

- Bash scripts must use set -euo pipefail.
- Interactive prompts (read -p) are forbidden by default.
- Python scripts should have if __name__ == '__main__' guard.

## Resources

- [`rules/bash-strict-mode.yml`](rules/bash-strict-mode.yml)
- [`rules/no-interactive.yml`](rules/no-interactive.yml)
- [`rules/python-main-guard.yml`](rules/python-main-guard.yml)
