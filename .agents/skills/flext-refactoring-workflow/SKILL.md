---
name: flext-refactoring-workflow
description: Step-by-step refactoring workflow with quality gates, make targets, and commit discipline for the FLEXT monorepo. Use when refactoring a module, extracting mixins, decomposing classes exceeding the 200-line cap, migrating legacy patterns to current MRO/facade conventions, or cleaning up import boundary violations.

---

# FLEXT Refactoring Workflow

**Reviewed**: 2026-04-20 | **Scope**: End-to-end refactoring with quality gates, tier-ordered sequencing, net-negative LOC delta gate, "more with less" north star

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
- `.agents/skills/flext-scope-bootstrap/SKILL.md`

## Rules

- Refactor in dependency-tier order; never break architecture directionality.
- Validate continuously with standardized make gates.
- Use structural search/replace tooling for code-pattern migrations.
- **Net-negative LOC delta gate**: every refactor task MUST produce a measurable reduction (LOC, number of aliases, `isinstance` checks, imports, utility wrappers, recursive unions). A task that adds code without removing more is a failed task; re-plan for reduction. Report per task:
  - `LOC delta: -X (+Y new, -Z removed)`
  - `Pyrefly delta: -A`
  - `Enforcement warnings: -B`
  - If the reported delta is ≥ 0, the task is rejected and re-planned for a net-negative outcome.
- **"More with less" north star**: every edit is an opportunity to remove, unify, or replace with a canonical contract. Cosmetic changes without reduction are FORBIDDEN.
- **Structural tooling is mandatory**: cross-file propagation requires `scope` for blast radius and `ast-grep` for structural rewrite. Serena should be used as well when project-aware symbol operations are available and correctly configured.
- **Serena health is part of refactor readiness**: before Serena-backed symbol/refactor work, the local project config must pass `serena project health-check`, and any non-source support trees that break symbol extraction must be excluded in `.serena/project.yml` rather than ignored informally.
- **Zero debt steady state**: `ruff`, `pyrefly`, enforcement checks, and `pytest` must be zero across all affected projects before a refactor task can be considered complete, even when failures predate the current batch.

## Instructions

- Baseline current state before edits with `make check` and `make test`.
- If Scope is missing, stale, or misconfigured, follow `flext-scope-bootstrap` before starting blast-radius analysis.
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
- `make val`
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
- Determine the correct Scope root before querying: repo root for repo-local work, workspace root for multi-repo work.
- If `.scope/config.toml` is missing in the repo root, run `scope init`. If `scope-workspace.toml` is required for the task and missing at the workspace root, run `scope workspace init` after member repositories are initialized.
- Run `scope status` first, then `scope index` for repo-local work or `scope workspace index` for multi-project work.
- If Serena is available, validate the local config with `serena project health-check`; if `.serena/project.yml` is missing, create it with `serena project create . --name flext --language python --index`; if health-check fails on synthetic/support trees, fix `.serena/project.yml` `ignored_paths` before proceeding.
- After the local config is healthy, activate/check the `flext` project before relying on Serena symbol operations.
- Use `scope refs <symbol>` / `scope callers <symbol>` to define blast radius before editing.
- Use `sg --pattern 'from flext_core.$MOD import $$$' --lang python` (ast-grep) to find all consumers — NEVER `grep -rn` for code structure
- Identify the tier of the module being refactored

### Step 1.1: AST-Grep Syntax Discipline

Use `ast-grep` structurally, not as a blind text replacer.

- Start with `sg --pattern '<pattern>' --lang python <path>` to inspect matches before any rewrite.
- Prefer patterns that encode syntax roles, for example:
  - `$NAME` for a single node
  - `$$$ARGS` for variadic argument lists
  - `$$$BODY` for repeated statements
- Narrow the path scope first; never run a broad workspace rewrite before blast-radius analysis.
- After confirming the match set, apply the smallest structural rewrite possible.
- Re-run `scope refs` or `scope callers` after the rewrite to confirm propagation is complete.
- Keep `sgconfig.yml` and `.ast-grep/` rules as references for syntax and testability.

Example audit flow:

```bash
scope refs FlextCoreModels.TargetOracle.ExecuteResult --workspace
sg --pattern 'ExecuteResult($$$ARGS)' --lang python flext-target-oracle/src flext-target-oracle/tests
sg --pattern 'ExecuteResult($$$ARGS)' --rewrite 'm.TargetOracle.ExecuteResult($$$ARGS)' --lang python flext-target-oracle/src flext-target-oracle/tests
scope refs FlextCoreModels.TargetOracle.ExecuteResult --workspace
```

### Step 2: Make Changes in Tier Order (Bottom-Up)

Always refactor bottom-up through the tiers:

```
Tier 0  -> constants.py, typings.py            (change first)
Tier 1  -> runtime.py                          (then this)
Tier 2  -> protocols.py                        (then this)
Tier 3  -> models/*.py, models.py             (then this)
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
# Full extended validation gate
make val

# Optional auto-fix before validation:
make val FIX=1
```

If a shared contract changed, widen validation until every affected project returns to zero `ruff`, `pyrefly`, enforcement, and `pytest` failures.

---

## Make Targets Quick Reference (from base.mk)

| Target          | What It Does                                               |
| --------------- | ---------------------------------------------------------- |
| `make help`     | Show available standardized commands                       |
| `make audit`    | SSOT enforcement audit (`GATES=docs` for mkdocs parity)    |
| `make boot`     | Install dependencies and hooks                             |
| `make check`    | Fast quality gate for the configured check selectors       |
| `make scan`     | Security scan gate                                         |
| `make fmt`      | Code formatting                                            |
| `make docs`     | Build docs                                                 |
| `make test`     | Pytest with coverage gate                                  |
| `make val`      | Extended non-lint validation (`FIX=1` optional)            |
| `make clean`    | Clean artifacts                                            |

`make audit` delegates to `FlextInfraEnforcementAuditor` (ENFORCE-039/041/043/044/054). Selectors: `PROJECTS=` (filter), `FIX=1` (apply rope auto-fix where supported), `GATES=docs` (route to `FlextInfraDocAuditor` python-codeblock parity per AGENTS.md §3.8). Rope-only: rewrites use `FlextInfraRefactorSafetyManager` `.bak` flow — never `git checkout`.

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

**FORBIDDEN**: `Mapping[str, Any]`, bare `Any`, untyped mappings. Use typed Pydantic models from `m.*` (e.g., `m.Value`). For mapping parameters use `m.ConfigMap`.

### Pattern B: Removing Legacy Aliases

1. Find all usages: `grep -rn "OLD_ALIAS" --include='*.py' .`
2. Replace with new form
3. Run `make check` after each file
4. Remove the alias definition last

### Pattern C: Moving Private to Facade

If a class from `models/base.py` needs to be publicly accessible:

1. Add the class to the facade in `models.py`
2. Update `FlextModels` class to expose it
3. Update consumers to import via `m.ClassName`
4. Never expose `models/*.py` directly to subprojects

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

### Pattern G: Facade Mirror Collapse

When a public module is an identical copy of its `_utilities/` counterpart (detected by `qlty smells --all` as `identical-code`):

1. Keep implementation in `_utilities/` (source of truth).
2. Replace public file with thin re-export stub:

```python
"""Re-export from internal module."""

from __future__ import annotations

from flext_core import m, u

__all__: list[str] = ["m", "u"]
```

1. Verify `__init__.py` lazy imports still resolve (chain: `__init__.py` → public module → `_utilities/`).
2. Run `ruff check src/`, `pyrefly check src/`, `pyright src/`.
3. Use `scope callers <Symbol>` to confirm no external breakage.

**Detection**: `qlty smells --all --sarif | jq '.runs[0].results[] | select(.ruleId == "qlty:identical-code")'`

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
make val FIX=1

# For format issues:
make fmt
```

### Type Check Errors (pyrefly)

```bash
# Run standardized validation gate:
make PROJECT=flext-core val

# With auto-fix first:
make PROJECT=flext-core val FIX=1
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
7. **ALWAYS preserve the facade pattern** - `models/` and `_utilities/` are private
8. **NEVER use `sed`, `awk`, `find`, or custom scripts to transform code** — use `sg --rewrite` (CLI) for ALL structural code changes. `grep`/`ripgrep` for plain-text only. `find` FORBIDDEN for code location. Writing a one-off fix script is an EXTREME FAULT.
9. **ast-grep is the SOLE code search and replace tool** — CLI `sg` as primary. Workflow: search → replace atomically → verify with `make check`.
