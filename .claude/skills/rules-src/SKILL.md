---

name: rules-src
description: Rules for shared source modules under top-level `src/`. Use when editing common source code that impacts multiple packages or utilities.
triggers:
  - editing shared source modules under top-level src/
  - modifying common source code that impacts multiple packages
  - adding utilities or helpers to the shared src/ layer
  - reviewing cross-package source dependencies

---

<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

# Rules Src

**Reviewed**: 2026-04-06 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `src/flext/`
- `src/.coverage`

## References

- `AGENTS.md` — canonical governance source
- `.claude/skills/flext-mro-namespace-rules/SKILL.md`
- `src/flext/`
- `flext-core/docs/architecture/clean-architecture.md`
- `Makefile`

## Rules

- Keep source changes aligned with architecture boundaries.
- Avoid package-internal imports that bypass public contracts.
- Keep typing explicit for public/module-level APIs.
- Preserve deterministic behavior and avoid hidden side effects.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `inline imports`, and `cast()`.
- **AXIOMATIC**: `Any`, `t.RecursiveContainer`, and `Mapping[str, Any]` are TOTALLY FORBIDDEN in ALL type annotations, function signatures, return types, and examples. Use `t.*` contracts from `typings.py` exclusively. `None` in type unions only when business-required. Every change MUST pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors. Linter suppressions are FORBIDDEN without real internet citations, business necessity, and per-line scope.
- **AXIOMATIC**: Compatibility wrappers (`def old(): return new()`), non-business validation fallbacks, legacy code maintenance, and `OldName = NewName` compatibility aliases are TOTALLY FORBIDDEN. Legacy code is DELETED and replaced with canonical patterns on contact. No grace period.
- **AXIOMATIC**: Every module MUST organize domain logic into a single nested class hierarchy using MRO inheritance from Pydantic v2 `BaseModel` (or FLEXT base models). Loose functions and standalone classes without MRO lineage are FORBIDDEN.
- **AXIOMATIC**: Public facade roots own exactly one local domain namespace. Private `_models/*` and `_utilities/*` classes belong in the facade MRO list, not in manual nested wrapper classes. Keep organic paths such as `u.Infra.*` and `m.TargetOracle.*`.
- **AXIOMATIC**: ALL code MUST follow "Pydantic v2 way" EXTENSIVELY. `Field()` with `description`/`title`/`examples`/`json_schema_extra` for ALL declarations. Minimize custom validators — prefer built-in constraints. `*Config` classes FORBIDDEN (use `BaseSettings`/`ConfigDict`). FORBIDDEN in models: init helpers, unnecessary `@property`, public `get_*`/`set_*`/`is_*` accessors, wrappers. USE: `@computed_field`, `model_post_init`, `PrivateAttr`. Enums/Literals from `c.*`, settings from `s.*`. Internal state via `PrivateAttr`. `models.py`/`_models/` for models ONLY. Use `success`/`failure` for result outcomes and central `m.*State`/`m.*Status` carriers for runtime state.
- **AXIOMATIC**: Tests MUST follow the EXACT SAME rules as production code — no "test-only" relaxation.
- **AXIOMATIC - Library Abstraction Boundaries (SUPREME LAW)**: Libraries abstracted by flext-core (`rich`, `dependency_injector`, `structlog`, `returns`, `orjson`, `pyyaml`) MUST NOT be imported directly in any `src/` code outside `flext-core/src/`. Use public abstractions instead: `m.*` (models), `c.*` (constants), `t.*` (types), `p.*` (protocols), `u.*` (utilities), `r[T]` (results). This applies to imports, type annotations, and constants equally.

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
from flext_core import r, p
```

Why good: uses stable public boundary from shared source logic.

Good (Library Abstraction):

```python
# In flext-cli/src/flext_cli/settings.py
from flext_core import m, c, t


class FlextCliSettings(m.Settings):
    """Extend FlextSettings from flext-core."""

    default_timeout: int = c.Cli.DEFAULT_TIMEOUT_SECONDS
    log_level: str = c.Cli.DEFAULT_LOG_LEVEL
```

Why good: Uses public abstractions (`m.Settings`, `c.Cli`) instead of importing pydantic/typing directly.

Bad (Library Abstraction Violation):

```python
# ❌ FORBIDDEN in flext-cli/src/
from pydantic import BaseModel, Field
from dependency_injector import containers


class CliSettings(BaseModel):
    """DO NOT DO THIS IN CONSUMING PROJECTS."""

    ...
```

Why bad: Bypasses flext-core's pydantic abstraction. Should use `m.Settings` from flext-core instead, giving flext-core full control over pydantic version, configuration, and validation rules.

Bad (Invalid Import):

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

Library abstraction boundary checks (audit for violations):

```bash
# Find forbidden pydantic imports in non-core flext projects
rg -n "from pydantic import|import pydantic" --glob "**/*.py" flext-cli flext-ldap flext-observability || echo "✓ No direct pydantic imports found"

# Find forbidden dependency_injector imports outside flext-core
rg -n "from dependency_injector import|import dependency_injector" --glob "**/*.py" flext-cli flext-ldap flext-observability || echo "✓ No direct dependency_injector imports found"

# Find forbidden structlog imports outside flext-core  
rg -n "from structlog import|import structlog" --glob "**/*.py" flext-cli flext-ldap flext-observability || echo "✓ No direct structlog imports found"
```
