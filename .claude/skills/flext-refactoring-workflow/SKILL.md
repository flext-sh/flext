---
name: flext-refactoring-workflow
description: Step-by-step refactoring process with verified quality gates and Make targets
---

# FLEXT Refactoring Workflow

> **Source of truth**: Verified from `base.mk` (shared Makefile), `ruff-shared.toml`,
> and actual `pyproject.toml` configurations across the monorepo.

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
   cd flext-core  # or whichever project
   make check     # = lint + type-check (via flext-quality or fallback)
   ```

4. **Run `make test-fast` first** - Confirm tests pass before changes.

   ```bash
   make test-fast  # = pytest -q --tb=short (no coverage)
   ```

---

## Refactoring Steps

### Step 1: Analyze Before Editing

- Read the FULL file(s) to be refactored
- Map the import graph - what imports this file? What does it import?
- Use `grep -rn "from flext_core.MODULE import" --include='*.py' src/` to find consumers
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

# Or specifically:
make lint       # ruff check . --quiet
make type-check # pyrefly check src/ --config pyproject.toml
```

### Step 4: Run Tests

```bash
# Fast test (no coverage)
make test-fast

# Full test with coverage (must pass MIN_COVERAGE=80)
make test

# Specific test file:
poetry run pytest tests/unit/test_MODULE.py -q --timeout=120

# Specific test with verbose output:
poetry run pytest tests/unit/test_MODULE.py -v -k "test_specific_case" --timeout=120
```

### Step 5: Extended Validation (before commits)

```bash
# Full validation: lint + format + type-check + complexity + docstrings + security + test
make validate

# Complete validation (includes dead-code, cognitive-complexity, spell-check):
make validate-full
```

---

## Make Targets Quick Reference (from base.mk)

| Target | Alias | What It Does |
| --- | --- | --- |
| `make help` | | Show all available commands |
| `make lint` | `make l` | `ruff check . --quiet` (ZERO tolerance) |
| `make format` | `make f` | `ruff format . --quiet` |
| `make fix` | | `ruff check --fix . --quiet` (auto-fix) |
| `make type-check` | `make tc` | `pyrefly check src/` |
| `make check` | | `lint + type-check` (quick gate) |
| `make test` | `make t` | `pytest` with coverage (min 80%) |
| `make test-fast` | | `pytest` without coverage |
| `make test-unit` | | Tests marked `not integration` |
| `make test-integration` | | Tests marked `integration` |
| `make validate` | `make v` | Full gate: lint+format+type+complexity+docstrings+security+test |
| `make validate-full` | `make vf` | Full + dead-code + cognitive-complexity + spell-check |
| `make complexity` | `make cx` | Radon CC+MI analysis |
| `make docstring-check` | `make dc` | Interrogate (min 80%) |
| `make dead-code` | `make dd` | Vulture (min-confidence 80) |
| `make cognitive-complexity` | `make cc` | Complexipy (max 15) |
| `make spell-check` | `make sp` | Codespell |
| `make security` | | Bandit security scan |
| `make deps` | `make dp` | Dependency analysis (deptry) |
| `make clean` | `make c` | Clean build artifacts |
| `make setup` | `make s` | Install dev+test deps |

---

## Quality Gate Thresholds (from base.mk)

| Metric | Threshold | Config Source |
| --- | --- | --- |
| Coverage | >= 80% (`MIN_COVERAGE`) | `base.mk` line 14, overridable per project |
| Docstring coverage | >= 80% (`DOCSTRING_MIN`) | `base.mk` line 15 |
| Cognitive complexity | <= 15 | `base.mk` line 182 |
| Complexity | <= 10 (`COMPLEXITY_MAX`) | `base.mk` line 16 |
| Dead code confidence | >= 80% | `base.mk` line 174 |
| Line length | 88 chars | `ruff-shared.toml` line 19 |
| Python version | 3.13 | `ruff-shared.toml` line 24 |

---

## Common Refactoring Patterns

### Pattern A: Replacing dict with ConfigMap

```python
# Before
from typing import Any
def configure(self, config: dict[str, Any]) -> None: ...

# After
from flext_core.typings import t
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

---

## Cross-Project Refactoring

When a change in `flext-core` affects subprojects:

```bash
# 1. Fix flext-core first
cd flext-core && make check && make test-fast

# 2. Check each dependent project
cd ../flext-auth && make check && make test-fast
cd ../flext-cli && make check && make test-fast
cd ../flext-ldap && make check && make test-fast

# 3. Workspace-level validation
cd .. && make check-all  # Or: make PROJECT=flext-auth check
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
# See the exact error with explanation:
ruff check src/flext_core/MODULE.py --select RULE_CODE

# Auto-fix what can be fixed:
make fix

# For format issues:
make format
```

### Type Check Errors (pyrefly)

```bash
# Run type-check with full output:
poetry run pyrefly check src/flext_core/ --config pyproject.toml

# For specific file:
poetry run pyrefly check src/flext_core/MODULE.py --config pyproject.toml
```

### Test Failures

```bash
# Run specific failing test with full output:
poetry run pytest tests/unit/test_MODULE.py -v -k "test_name" --timeout=120 -s

# With traceback:
poetry run pytest tests/unit/test_MODULE.py --tb=long -v
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
