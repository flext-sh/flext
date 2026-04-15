---
name: rules-src
description: Rules for shared source modules under top-level `src/`. Use when editing common source code that impacts multiple packages or utilities.

---

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

- Keep source changes aligned with architecture boundaries (`AGENTS.md` §2).
- Avoid package-internal imports that bypass public contracts (`AGENTS.md` §4).
- Keep typing explicit for public/module-level APIs (`AGENTS.md` §3.2).
- Preserve deterministic behavior; no hidden side effects.
- Canonical governance lives in `AGENTS.md`:
  - §3.2 Types & Contracts — `t.*` aliases, no `Any`, no bare containers.
  - §3.1 Architecture & Code — single nested class hierarchy, MRO inheritance, Pydantic v2 way.
  - §2.2 Facades & Namespaces — one namespace branch per facade root.
  - §2.7 Library Abstraction Boundaries — no direct imports of core-abstracted libs outside `flext-core/src/`.
  - §3.6 Test Standardization — tests follow production rules without relaxation.

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
