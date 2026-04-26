---
name: flext-refactoring-workflow
description: Step-by-step refactoring workflow with quality gates, make targets, and commit discipline for the FLEXT monorepo. Use when refactoring a module, extracting mixins, decomposing classes exceeding the 200-line cap, migrating legacy patterns to current MRO/facade conventions, or cleaning up import boundary violations.

---

# FLEXT Refactoring Workflow

**Reviewed**: 2026-04-26 | **Scope**: Refactor flow under AGENTS.md §0.0 ZERO TOLERANCE TABLE.

## Hard Start Card (mandatory)

1. Smell first. `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
2. One offender + full caller chain only. No parallel edits.
3. Search before write. Reuse before create. Delete before extend.
4. Structural propagation uses `sg`; manual grep rewrites are invalid.
5. Pydantic2/Python3.13 first (`TypeAdapter`, `Annotated`, validators, `computed_field`, `TypeIs`, `Self`, `@override`, `match/case`).
6. Net LOC must be negative.
7. Validate now: `ruff` -> `pyrefly` -> focused `pytest` -> affected `make check`.
8. Shared contract changed = propagate now, not later.

## 20s Context Load (mandatory)

State these before first patch:

1. Selected offender and exact file:line pair.
2. SSOT primitive being reused.
3. First gate command after edit.
4. Propagation command for callers.

If any item is missing, do not edit.

## Recurrence Kill-Switches (mandatory)

- Syntax break after first patch: stop and restore a minimal clean file before continuing.
- Any new helper/proxy/wrapper/compat alias: delete immediately in the same cycle.
- Contract changed without caller propagation: task invalid.
- Refactor with non-negative LOC delta: task invalid.
- Smell run skipped before edit: task invalid.

## Execution Plan Floor

`SMELL -> SEARCH -> DELETE -> COLLAPSE -> REPLACE with Pydantic2/Py3.13 -> PROPAGATE -> VALIDATE`

## Optimization Loop (mandatory when debt remains)

1. `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
2. Choose one `src/` offender (randomized if needed).
3. Refactor offender + usage chain with MRO + Pydantic2/Python3.13 first.
4. Validate touched scope (`ruff`, `pyrefly`, focused `pytest`).
5. Repeat until the current lane has no high-value unresolved offenders.

> **READ FIRST**: `AGENTS.md` §0.0 (the 18-rule ZERO TOLERANCE TABLE). Every rule below is a SPECIALIZATION of that table. Conflict between this skill and §0.0 → §0.0 wins.

## Scope

- End-to-end refactoring under §0.0 (SEARCH → REUSE → DELETE → COMPOSE-VIA-MRO → USE-PYDANTIC2/PY3.13 → only-then-EDIT).
- Tier-ordered sequencing, gate discipline, cross-project propagation.

## References

- `AGENTS.md`
- `base.mk`
- `Makefile`
- `ruff-shared.toml`
- `pyproject.toml`
- `.agents/skills/flext-scope-bootstrap/SKILL.md`

## Rules (specialization of §0.0)

- §0.0#1 SEARCH FIRST: grep `flext-{core,cli,infra,tests}/src` BEFORE writing.
- §0.0#2 NET-LOC < 0: every task `(deleted - added) > 0`. Report `LOC delta: -X (+Y, -Z)` + pyrefly delta + enforcement-warning delta. Delta ≥ 0 = TASK REJECTED.
- §0.0#3 8× DUPLICATION GATE on any new mixin/helper. Cite the multiplier in the commit.
- §0.0#4 MRO mixin into lowest existing facade. Standalone classes outside facade-composed tree FORBIDDEN.
- §0.0#5 Pydantic 2 + Python 3.13 patterns BEFORE writing custom code (TypeAdapter, RootModel, computed_field, discriminated unions, Annotated[T, Field], model_validator, ConfigDict, type X = …, TypeIs, match/case, @override/@final/Self, generic params, `cached_property`). Any custom code that an existing P2/Py3.13 feature replaces = DELETE.
- §0.0#6 forbidden constructs (pass-through wrappers, compat aliases, Any, cast(), os.environ in src/, model_rebuild(), unjustified noqa/type:ignore, hasattr(_priv), get_*/set_*/is_* accessors).
- Refactor in dependency-tier order; never break architecture directionality.
- Structural propagation: `ast-grep` (sg) for rewrites, `scope` for blast radius, Serena for symbol-aware ops (after `serena project health-check`).
- Zero debt steady state: ruff/pyrefly/enforcement/pytest must be ZERO across affected projects before task is complete (pre-existing failures count).

## Instructions

- Baseline current state before edits with `make check` and `make test`.
- If Scope is missing, stale, or misconfigured, follow `flext-scope-bootstrap` before starting blast-radius analysis.
- Apply smallest safe batch per file/tier and verify immediately.
- Expand validation scope whenever shared contracts/types are touched.

## Workflow

1. Baseline: run the 3 pre-edit commands from `AGENTS.md` §0.0.
2. Blast radius: use `scope`/`sg`/`grep` to map callers before first edit.
3. Deletion pass: remove wrappers, compat aliases, dead code, duplicated fields/methods first.
4. Reduction pass: replace remaining custom code with Pydantic 2 / Python 3.13 primitives.
5. MRO pass: collapse surviving duplication into the lowest existing facade.
6. Validate after each edited file.
7. Run widened project gates for shared changes.
8. Commit immediately after green gates.

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
| `make boot`     | Install dependencies and hooks                             |
| `make check`    | Fast quality gate for the configured check selectors       |
| `make scan`     | Security scan gate                                         |
| `make fmt`      | Code formatting                                            |
| `make docs`     | Build docs                                                 |
| `make test`     | Pytest with coverage gate                                  |
| `make val`      | Extended non-lint validation (`FIX=1` optional)            |
| `make clean`    | Clean artifacts                                            |

`make audit` delegates to `FlextInfraEnforcementAuditor` (ENFORCE-039/041/043/044/054/055). Selectors: `PROJECTS=` (filter), `FIX=1` (apply rope auto-fix where supported), `GATES=docs` (route to `FlextInfraDocAuditor` python-codeblock parity per AGENTS.md §3.8). Rope-only: rewrites use `FlextInfraRefactorSafetyManager` `.bak` flow — never `git checkout`.

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
