---
name: rules-flext-core
description: 'Guidance for authoritative rules for `flext-core` architecture, typing, result flow, DI, and logging boundaries. Use when modifying files under `flext-core/`.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Flext Core

## Workflow

1. Classify touched files by architecture layer.
2. Apply minimal change aligned with local pattern.
3. Verify imports/exports and boundary integrity.

## Enforced contracts

- Python modules should enable postponed annotation evaluation.
- Service boundaries should prefer r-based result flow.
- Standardize test helper aliases to tm/tt/u/c/p naming.
- Subproject constants.py should import FlextConstants from flext_core.

## Resources

- [`rules/require-flext-constants-import.yml`](rules/require-flext-constants-import.yml)
- [`rules/require-flext-result-pattern.yml`](rules/require-flext-result-pattern.yml)
- [`rules/require-future-annotations.yml`](rules/require-future-annotations.yml)
- [`rules/test-alias-fix.yml`](rules/test-alias-fix.yml)
