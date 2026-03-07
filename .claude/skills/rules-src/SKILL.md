<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

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

- `AGENTS.md` — canonical governance source
- `src/flext/`
- `flext-core/docs/architecture/clean-architecture.md`
- `Makefile`

## Rules

- Keep source changes aligned with architecture boundaries.
- Avoid package-internal imports that bypass public contracts.
- Keep typing explicit for public/module-level APIs.
- Preserve deterministic behavior and avoid hidden side effects.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `inline imports`, and `cast()`.
- **AXIOMATIC**: `Any`, `object`, and `dict[str, Any]` are TOTALLY FORBIDDEN in ALL type annotations, function signatures, return types, and examples. Use `t.*` contracts from `typings.py` exclusively. `None` in type unions only when business-required. Every change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. Linter suppressions are FORBIDDEN without real internet citations, business necessity, and per-line scope.
- **AXIOMATIC**: Compatibility wrappers (`def old(): return new()`), non-business validation fallbacks, legacy code maintenance, and `OldName = NewName` compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED and replaced with canonical patterns on contact. No grace period.
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions and standalone classes without MRO lineage are FORBIDDEN.
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY. `Field()` with `description`/`title`/`examples`/`json_schema_extra` for ALL declarations. Minimize custom validators — prefer built-in constraints. `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). FORBIDDEN in models: init helpers, unnecessary `@property`, simple getters/setters, wrappers. USE: `@computed_field`, `model_post_init`, `PrivateAttr`. Enums/Literals from `c.*`, config from `s.*`. Internal state via `PrivateAttr`. `models.py`/`_models/` for models ONLY.
- **AXIOMATIC**: Tests MUST follow the EXACT SAME rules as production code — no "test-only" relaxation.

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
from flext_core import *
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
