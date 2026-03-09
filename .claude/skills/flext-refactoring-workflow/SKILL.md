<!-- TOC START -->

- [Pre-Refactoring Checklist](#pre-refactoring-checklist)
- [Refactoring Steps](#refactoring-steps)
  - [Step 1: Analyze Before Editing](#step-1-analyze-before-editing)
  - [Step 2: Make Changes in Tier Order (Bottom-Up)](#step-2-make-changes-in-tier-order-bottom-up)
  - [Step 3: Validate After Each File](#step-3-validate-after-each-file)
  - [Step 4: Run Tests](#step-4-run-tests)
  - [Step 5: Extended Validation (before commits)](#step-5-extended-validation-before-commits)
- [Make Targets Quick Reference (from base.mk)](#make-targets-quick-reference-from-basemk)
- [Quality Gate Thresholds](#quality-gate-thresholds)
- [Common Refactoring Patterns](#common-refactoring-patterns)
  - [Pattern A: Replacing dict with ConfigMap](#pattern-a-replacing-dict-with-configmap)
  - [Pattern B: Removing Legacy Aliases](#pattern-b-removing-legacy-aliases)
  - [Pattern C: Moving Private to Facade](#pattern-c-moving-private-to-facade)
  - [Pattern D: Extracting Large Methods](#pattern-d-extracting-large-methods)
- [Cross-Project Refactoring](#cross-project-refactoring)
  - [Finding cross-project consumers](#finding-cross-project-consumers)
- [Error Handling During Refactoring](#error-handling-during-refactoring)
  - [Ruff Errors](#ruff-errors)
  - [Type Check Errors (pyrefly)](#type-check-errors-pyrefly)
  - [Test Failures](#test-failures)
- [CRITICAL RULES](#critical-rules)
<!-- TOC END -->

---

name: flext-refactoring-workflow
description: Step-by-step refactoring process with verified quality gates and Make targets

---

# FLEXT Refactoring Workflow

**Reviewed**: 2026-02-19 | **Scope**: Coverage source-of-truth migration to pyproject.toml

> **Source of truth**: Verified from `base.mk` (shared Makefile), `ruff-shared.toml`,
> and actual `pyproject.toml` configurations across the monorepo on 2026-02-19.

- `AGENTS.md` — canonical governance source

## Scope

- End-to-end refactoring execution flow for FLEXT projects.
- Tier-ordered change sequencing, gate discipline, and cross-project impact handling.

## References

- `AGENTS.md`
- `base.mk`
- `Makefile`
- `ruff-shared.toml`
- `pyproject.toml`

## Rules

- Refactor in dependency-tier order; never break architecture directionality.
- Validate continuously with standardized make gates.
- Use structural search/replace tooling for code-pattern migrations.
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`.

## Instructions

- Baseline current state before edits with `make check` and `make test`.
- Apply smallest safe batch per file/tier and verify immediately.
- Expand validation scope whenever shared contracts/types are touched.

## Workflow

1. Baseline and dependency map.
2. Refactor bottom-up by tier.
3. Validate after each edited file.
4. Run tests and extended validation.
5. Execute cross-project verification for shared changes.

## Examples

```bash
# Baseline + focused refactor cycle
make PROJECT=flext-core check
make PROJECT=flext-core test

# Validate dependent projects when shared APIs change
make PROJECTS="flext-core flext-auth flext-cli" check
```

## Verification

- `make check`
- `make test`
- `make validate`
- `make PROJECT=<name> check`
- `make PROJECTS="proj-a proj-b" check`

## Pre-Refactoring Checklist

Before touching any code:

1. **Read relevant skill documents** - At minimum:
   - `flext-architecture-layers/SKILL.md` (tier rules)
   - `flext-import-rules/SKILL.md` (import patterns)
   - `flext-strict-typing/SKILL.md` (type hierarchy)

2. **Identify the affected scope** - Which modules/files will be changed?
   Check the tier level to understand what depends on them.

3. **Run `make check` first** - Establish the current baseline state.

   ```bash
   make PROJECT=flext-core check
   ```

4. **Run `make test` first** - Confirm tests pass before changes.

   ```bash
   make test
   ```

---

## Refactoring Steps

### Step 1: Analyze Before Editing

- Read the FULL file(s) to be refactored
- Map the import graph - what imports this file? What does it import?
# QS|- Use `sg --pattern 'from flext_core.$MOD import $$$' --lang python` (ast-grep MCP: `mcp_ast_grep_search`) to find all consumers — NEVER `grep -rn` for code structure
- Identify the tier of the module being refactored

### Step 2: Make Changes in Tier Order (Bottom-Up)

Always refactor bottom-up through the tiers:

```
Tier 0  -> constants.py, typings.py            (change first)
Tier 1  -> runtime.py                          (then this)
Tier 2  -> protocols.py                        (then this)
Tier 3  -> _models/*.py, models.py             (then this)
Tier 4  -> _utilities/*.py, utilities.py,
           exceptions.py, result.py, settings.py
Tier 5  -> loggings.py, context.py, container.py,
           handlers.py, mixins.py, decorators.py
Tier 6  -> dispatcher.py, registry.py, service.py  (change last)
```

If refactoring affects types/aliases in `typings.py`:

1. Update `typings.py` first
2. Update all consumers in order up the tiers
3. Check subprojects last (`flext-auth`, `flext-cli`, etc.)

### Step 3: Validate After Each File

After modifying any file, run the quick check:

```bash
# Quick validation (lint + type-check)
make check

# Keep the standardized surface:
make check
```

### Step 4: Run Tests

```bash
# Full test with coverage (threshold from pyproject.toml [tool.coverage.report] fail_under)
make test

# Specific test file:
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_MODULE.py -q --timeout=120"

# Specific test with verbose output:
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_MODULE.py -v -k test_specific_case --timeout=120"
```

### Step 5: Extended Validation (before commits)

```bash
# Full validation: lint + format + type-check + complexity + docstrings + security + test
make validate

# Optional auto-fix before validate:
make validate FIX=1
```

---

## Make Targets Quick Reference (from base.mk)

| Target          | What It Does                                               |
| --------------- | ---------------------------------------------------------- |
| `make help`     | Show available standardized commands                       |
| `make setup`    | Install dependencies and hooks                             |
| `make check`    | Fast quality gate (ruff + format check + pyrefly + bandit) |
| `make security` | Security scan gate                                         |
| `make format`   | Code formatting                                            |
| `make docs`     | Build docs                                                 |
| `make test`     | Pytest with coverage gate                                  |
| `make validate` | Extended non-lint validation (`FIX=1` optional)            |
| `make clean`    | Clean artifacts                                            |

---

## Quality Gate Thresholds

| Metric               | Threshold                | Config Source                                        |
| -------------------- | ------------------------ | ---------------------------------------------------- |
| Coverage             | Per-project `fail_under` | `pyproject.toml` `[tool.coverage.report] fail_under` |
| Docstring coverage   | >= 80% (`DOCSTRING_MIN`) | `base.mk` variable `DOCSTRING_MIN`                   |
| Cognitive complexity | <= 15                    | `base.mk` complexipy gate parameters                 |
| Complexity           | <= 10 (`COMPLEXITY_MAX`) | `base.mk` variable `COMPLEXITY_MAX`                  |
| Dead code confidence | >= 80%                   | `base.mk` vulture gate parameters                    |
| Line length          | 88 chars                 | `ruff-shared.toml` `line-length` setting             |
| Python version       | 3.13                     | `ruff-shared.toml` `target-version` setting          |

---

## Common Refactoring Patterns

### Pattern A: Replacing dict with ConfigMap

```python
# Before (FORBIDDEN — `Any` and `dict[str, Any]` are axiomatic violations)
from typing import Any  # ← FORBIDDEN import


def configure(self, config: dict[str, Any]) -> None: ...  # ← FORBIDDEN type


# After
from flext_core import t


def configure(self, config: t.ConfigMap) -> None: ...
```

### Pattern B: Removing Legacy Aliases

1. Find all usages: `grep -rn "OLD_ALIAS" --include='*.py' .`
2. Replace with new form
3. Run `make check` after each file
4. Remove the alias definition last

### Pattern C: Moving Private to Facade

If a class from `_models/base.py` needs to be publicly accessible:

1. Add the class to the facade in `models.py`
2. Update `FlextModels` class to expose it
3. Update consumers to import via `m.ClassName`
4. Never expose `_models/*.py` directly to subprojects

### Pattern D: Extracting Large Methods

When a method exceeds the cognitive complexity threshold (15):

1. Identify independent sub-operations
2. Extract to private methods with descriptive names
3. Keep the original method as orchestrator
4. Each extracted method should have its own type hints

### Pattern E: Dead Wrapper Module Purge

When entire operation modules are unreferenced and duplicate behavior from a canonical facade:

1. Verify zero inbound references with repo-wide search.
2. Delete the module(s) outright (do not keep compatibility wrappers).
3. Re-run project gates.
4. Record deletion in the ledger/evidence file.

### Pattern F: Compatibility Alias Elimination

When public surfaces expose `*API = *` aliases or free-function wrappers that only instantiate a facade:

1. Remove alias and wrapper functions.
2. Export only the canonical class/module surface.
3. Rewrite all tests and call sites to direct method calls.
4. Re-run project gates and document any pre-existing unrelated failures.

---

## Cross-Project Refactoring

When a change in `flext-core` affects subprojects:

```bash
# 1. Fix flext-core first
make PROJECT=flext-core check
make PROJECT=flext-core test

# 2. Check each dependent project
make PROJECT=flext-auth check
make PROJECT=flext-auth test
make PROJECT=flext-cli check
make PROJECT=flext-cli test
make PROJECT=flext-ldap check
make PROJECT=flext-ldap test

# 3. Workspace-level validation
make PROJECTS="flext-core flext-auth flext-cli flext-ldap" check
```

### Finding cross-project consumers

```bash
# From workspace root:
grep -rn "from flext_core.MODULE" --include='*.py' flext-*/src/
```

---

## Error Handling During Refactoring

### Ruff Errors

```bash
# Re-run standardized fast gate:
make PROJECT=flext-core check

# Auto-fix path:
make validate FIX=1

# For format issues:
make format
```

### Type Check Errors (pyrefly)

```bash
# Run standardized validation gate:
make PROJECT=flext-core validate

# With auto-fix first:
make PROJECT=flext-core validate FIX=1
```

### Test Failures

```bash
# Run specific failing test with full output:
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_MODULE.py -v -k test_name --timeout=120 -s"

# With traceback:
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_MODULE.py --tb=long -v"
```

---

## CRITICAL RULES

1. **NEVER skip `make check`** after editing any file
2. **NEVER edit multiple tiers simultaneously** - go bottom-up
3. **NEVER remove a public API** without checking all consumers first
4. **NEVER introduce `Any`** - use the type hierarchy from `flext-strict-typing`
5. **NEVER use relative imports** - the codebase uses zero relative imports
6. **ALWAYS run tests** before declaring refactoring complete
7. **ALWAYS preserve the facade pattern** - `_models/` and `_utilities/` are private
# KA|8. **NEVER use `sed`, `awk`, `find`, or custom scripts to transform code** — use `mcp_ast_grep_replace` (MCP) or `sg --rewrite` (CLI) for ALL structural code changes. `grep`/`ripgrep` for plain-text only. `find` TOTALLY FORBIDDEN for code location. Writing a one-off fix script is an EXTREME FAULT.
# NB|9. **ast-grep is the SOLE code search and replace tool** — MCP `mcp_ast_grep_search` first, CLI `sg` as fallback. Workflow: search → replace atomically → verify with `make check`.
