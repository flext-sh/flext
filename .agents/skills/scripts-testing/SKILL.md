---
name: scripts-testing
description: 'Guidance for testing scripts — pytest runners, test analysis, quality gates, stress tests, and distributed testing. Use when editing scripts/testing/. Use canonical Make verbs.'
license: MIT
metadata:
  version: 1.0.0
---
# Scripts Testing

## Workflow

1. Identify the testing scope (unit, integration, stress, e2e).
2. Create or modify the script under `scripts/testing/`.
3. Test locally with `--help` first.

## Enforced contracts

- Every testing script must declare Owner-Skill marker.
- Testing shell scripts should include a portable shebang.

## Resources

- [`rules/require-owner-skill-marker.yml`](rules/require-owner-skill-marker.yml)
- [`rules/require-shebang-in-sh.yml`](rules/require-shebang-in-sh.yml)
