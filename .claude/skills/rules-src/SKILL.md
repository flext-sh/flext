---
name: rules-src
description: Rules for shared source modules under top-level `src/`. Use when editing common source code that impacts multiple packages or utilities.
---

# Rules Src

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


## Scope

- `src/flext/`
- `src/.coverage`

## References

- `src/flext/`
- `flext-core/docs/architecture/clean-architecture.md`
- `Makefile`

## Rules

- Keep source changes aligned with architecture boundaries.
- Avoid package-internal imports that bypass public contracts.
- Keep typing explicit for public/module-level APIs.
- Preserve deterministic behavior and avoid hidden side effects.

## Instructions

- Inspect nearest existing module pattern before changing logic.
- Keep imports and exports explicit.
- Update related tests/docs when shared source behavior changes.

```bash
ls -la src
```

## Workflow

1. Identify the shared source module being changed.
2. Apply scoped edits with explicit contract impact.
3. Verify no boundary violations in imports.
4. Run relevant checks for affected packages.

## Examples

Good:

```python
from flext_core import r
```

Why good: uses stable public boundary from shared source logic.

Bad:

```python
from flext_core._utilities import *
```

Why bad: private/wildcard import makes source behavior fragile and hard to analyze.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates for import validation
- `make check PROJECT=flext-core CHECK_GATES=lint,type` — focused import checks

File checks:

- `ls -la src`
- `rg -n "from flext_core\._|import \*" --glob "**/*.py" src flext-* flext-core/src || true`
- `rg -n "TODO|FIXME" src || true`
