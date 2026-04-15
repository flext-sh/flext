---

name: flext-import-rules
description: Enforces import ordering, alias conventions, and abstraction boundaries for the FLEXT 33-project monorepo (PEP 623, TYPE_CHECKING rules, no bare pydantic/structlog in consumers). Use when adding imports to any Python file, resolving circular imports, auditing import boundary violations, or checking whether a cross-project import is permitted by AGENTS.md §4.
triggers:
  - adding imports to any Python file
  - resolving circular imports
  - auditing import boundary violations
  - checking whether a cross-project import is permitted
  - adding TYPE_CHECKING guards
  - migrating bare pydantic/structlog imports to abstracted equivalents
  - writing or reviewing __init__.py exports
  - debugging import-order or abstraction boundary errors from ruff

---

<!-- TOC START -->

- [Rule 1: Always Use `from **future** import annotations

from collections.abc import Mapping, Sequence`](#rule-1-always-use-from-future-import-annotations)
- [Rule 2: Import Order (enforced by ruff `I` rules)](#rule-2-import-order-enforced-by-ruff-i-rules)
- [Rule 3: How to Import from flext-core (Inside flext-core)](#rule-3-how-to-import-from-flext-core-inside-flext-core)
  - [WITHIN flext-core, import via ABSOLUTE paths to submodules](#within-flext-core-import-via-absolute-paths-to-submodules)
  - [Exception: Docstrings use `from flext_core import ...` style for user-facing examples](#exception-docstrings-use-from-flextcore-import-style-for-user-facing-examples)
- [Rule 4: How to Import from flext-core (From Subprojects)](#rule-4-how-to-import-from-flext-core-from-subprojects)
  - [Pattern A: Import with alias (most common, used in 90%+ of files)](#pattern-a-import-with-alias-most-common-used-in-90-of-files)
  - [Pattern B: Import specific class from submodule (used for non-aliased classes)](#pattern-b-import-specific-class-from-submodule-used-for-non-aliased-classes)
  - [Pattern C: Import for extension/inheritance](#pattern-c-import-for-extensioninheritance)
  - [What is NEVER done in subprojects](#what-is-never-done-in-subprojects)
- [Rule 5: Tier Enforcement](#rule-5-tier-enforcement)
  - [Verified violations (these exist but should not be referenced as patterns)](#verified-violations-these-exist-but-should-not-be-referenced-as-patterns)
- [Rule 6: Private Module Convention](#rule-6-private-module-convention)
- [Rule 7: The Facade Alias Pattern](#rule-7-the-facade-alias-pattern)
- [Rule 8: TYPE_CHECKING Policy (Pragmatic Usage)](#rule-8-typechecking-policy-pragmatic-usage)
- [Rule 9: Ruff Configuration (from ruff-shared.toml)](#rule-9-ruff-configuration-from-ruff-sharedtoml)
- [Rule 10: What NOT to Do](#rule-10-what-not-to-do)
- [Rule 11: No Double-Assignment of Facade Aliases](#rule-11-no-double-assignment-of-facade-aliases)
- [Rule 12: Ecosystem MRO & Namespace Composition Architecture](#rule-12-ecosystem-mro--namespace-composition-architecture)
  - [L0 — Foundation](#l0--foundation)
  - [L1 — Domain Libraries](#l1--domain-libraries)
  - [L1 — Platform Libraries](#l1--platform-libraries)
  - [L2 — Integration Projects (Taps/Targets/dbt)](#l2--integration-projects-tapstargetsdbt)
  - [L2 — Custom Composition Projects](#l2--custom-composition-projects)
- [Rule 13: Library Abstraction Boundaries (SUPREME LAW)](#rule-13-library-abstraction-boundaries-supreme-law)
  - [What flext-core Abstracts](#what-flext-core-abstracts)
  - [Forbidden Imports (Outside flext-core src/)](#forbidden-imports-outside-flext-core-src)
  - [Valid Pattern (All Projects)](#valid-pattern-all-projects)
  - [Enforcement](#enforcement)
- [Verification](#verification)
<!-- TOC END -->

# FLEXT Import Rules

**Reviewed**: 2026-04-06 | **Scope**: Evidence-backed skill refresh and rule alignment

> **Verified from**: Static analysis of all `.py` files in `flext-core` and consuming
> projects (`flext-auth`, `flext-cli`, `flext-ldap`) on 2026-02-17.
> **Rule**: See `AGENTS.md` §4 Import Law for canonical aliases, import order, and prohibited import forms.

## Scope

- Import architecture and conventions for `flext-core` and all consuming projects.
- Canonical alias usage, tier-safe dependencies, and MRO-safe namespace composition.

## References

- `AGENTS.md`
- `.claude/skills/flext-architecture-layers/SKILL.md`
- `.claude/skills/flext-mro-namespace-rules/SKILL.md`
- `ruff-shared.toml`
- `flext-core/src/flext_core/`

## Rules

- Enforce import order: future, stdlib, third-party, first-party, local.
- Enforce architecture directionality and private-module boundaries.
- Use canonical aliases (`c`, `m`, `p`, `t`, `u`, `r`, `d`, `e`, `h`, `s`, `x`) at usage sites.
- In wrapper surfaces (`tests/`, `examples/`, `scripts/`), import canonical aliases from the local wrapper package (`from tests import c, m, p, t, u`, `from examples import c, m, t`, `from scripts import c, m, t, u`) — never from sibling projects.
- Keep same-project public facades isolated at runtime; only the `TYPE_CHECKING` matrix from `AGENTS.md` §4 allows same-project cross-facade type references.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, and `inline imports`. `cast()` is forbidden outside `flext-core` result internals.

## Instructions

- Apply import changes in dependency-tier order when refactoring shared modules.
- Validate both syntax and architectural intent after every import migration batch.
- Prefer public facades; avoid direct imports from private `_` modules in subprojects.

## Workflow

1. Inventory current import style and violations.
2. Apply canonical import form aligned with module tier.
3. Fix cross-project inheritance/import boundaries.
4. Re-run quality gates and targeted searches.

## Examples

```python
# Correct usage — always from root namespace
from flext_core import m, p, t

# Correct inheritance import by class name — also from root namespace
from flext_core import FlextProtocols
```


## Detailed Import Rules

Full import rule enforcement is in [references/import-rules-detail.md](references/import-rules-detail.md). Load it when you need rule-level detail on:
- `from __future__ import annotations` + `from collections.abc import Mapping, Sequence` requirements
- Import ordering (future / stdlib / third-party / first-party / local)
- Cross-project import rules and tier enforcement
- Facade alias patterns (`c`, `m`, `t`, `u`, `p`) and where each is sourced
- TYPE_CHECKING policy and lazy `__init__.py` loading
- Ruff import configuration and suppression rules
- MRO namespace composition patterns and circular import resolution
