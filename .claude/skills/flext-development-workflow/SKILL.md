---
name: flext-development-workflow
description: Verified development workflow including toolchain, testing, and CI/CD for the FLEXT monorepo
---

# FLEXT Development Workflow

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment


> **Source of truth**: Verified from `base.mk`, `pyproject.toml`, `.pre-commit-config.yaml`,
> and actual project structure on 2026-02-17.

## Workspace Setup

### Prerequisites

- Python 3.13+ (required, verified in `pyproject.toml` and `ruff-shared.toml`)
- Poetry (package management)
- Git with submodule support (30 submodules)

### Initial Setup

```bash
# Clone with submodules
git clone --recursive <repo-url>
cd flext

# Create workspace-level virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install all dependencies
make setup  # Runs: poetry install --with dev,test + pre-commit install
```

### Key Principle: Single Shared .venv

All subprojects share ONE virtual environment at `flext/.venv/`.
The `base.mk` enforces this:

```makefile
WORKSPACE_VENV := $(WORKSPACE_ROOT)/.venv
export VIRTUAL_ENV := $(WORKSPACE_VENV)
export PATH := $(WORKSPACE_VENV)/bin:$(PATH)
```

If a local `.venv/` exists inside a subproject, the build warns you:

```
WARNING: Local .venv found! Run 'make clean-local-venv' to use workspace venv
```

---

## Day-to-Day Development Loop

### 1. Start Working on a Subproject

```bash
cd flext-core   # or flext-auth, flext-cli, etc.
make check      # Verify baseline (lint + type-check)
```

### 2. Edit Code

Follow the rules in these skill documents:

- **Architecture**: `flext-architecture-layers/SKILL.md`
- **Imports**: `flext-import-rules/SKILL.md`
- **Types**: `flext-strict-typing/SKILL.md`

### 3. Quick Feedback Loop

```bash
make check      # lint + type-check (fast, ~5-10 seconds)
make test-fast  # tests without coverage (faster)
```

### 4. Pre-Commit Validation

```bash
make validate   # Full gate: lint + format + type + complexity + docstrings + security + tests
```

---

## Toolchain Details

### Ruff (Linting + Formatting)

- Config: `ruff-shared.toml` at workspace root
- Each project's `pyproject.toml` extends it: `extend = "../ruff-shared.toml"`
- Zero tolerance: ANY lint error fails the build
- Preview mode enabled for latest rules
- Auto-fix available: `make fix`
- Line length: 88 characters
- Quote style: double
- Indent: spaces
- Line ending: LF

Key Ruff categories enabled:

```
A, ANN, ARG, ASYNC, B, BLE, C4, C90, COM, D, DJ, DTZ, E, EM, ERA, EXE, F,
FA, FBT, FIX, FLY, FURB, G, I, ICN, INP, INT, ISC, LOG, N, NPY, PERF, PGH,
PIE, PL, PT, PTH, PYI, Q, RET, RSE, RUF, S, SIM, SLF, SLOT, T10, T20, TC,
TCH, TD, TID, TRY, UP, W, YTT
```

### Pyrefly (Type Checking)

- Config: `pyproject.toml` section `[tool.pyrefly]`
- Run: `make type-check` or `make tc`
- Zero tolerance: ANY type error fails the build

### Pytest (Testing)

- Config: `pyproject.toml` section `[tool.pytest.ini_options]`
- Run: `make test` (with coverage) or `make test-fast` (without)
- Coverage minimum: 80% (configurable per project via `MIN_COVERAGE`)
- Timeout: configurable per test
- Markers: `unit`, `integration`

### Additional Quality Tools

| Tool | Purpose | Make Target |
| --- | --- | --- |
| Radon | Cyclomatic complexity + maintainability | `make complexity` |
| Interrogate | Docstring coverage (min 80%) | `make docstring-check` |
| Vulture | Dead code detection | `make dead-code` |
| Complexipy | Cognitive complexity (max 15) | `make cognitive-complexity` |
| Codespell | Spell checking | `make spell-check` |
| Bandit | Security scanning | `make security` |
| deptry | Dependency analysis | `make deps` |

---

## PYTHONPATH Auto-Discovery

`base.mk` automatically builds PYTHONPATH with all project source dirs:

```makefile
FLEXT_PYTHONPATH := $(CURDIR)/src:$(WORKSPACE_ROOT)/flext-core/src:
    $(WORKSPACE_ROOT)/flext-cli/src:$(WORKSPACE_ROOT)/flext-ldif/src:
    $(WORKSPACE_ROOT)/flext-ldap/src:$(WORKSPACE_ROOT)/flext-api/src:
    $(WORKSPACE_ROOT)/flext-auth/src:...
```

This means you can run tests or scripts from any subproject and cross-project
imports will resolve correctly.

---

## Testing Conventions

### Test File Structure

```
flext-core/
  tests/
    unit/
      test_constants.py
      test_typings.py
      test_models.py
      test_result.py
      ...
    integration/
      test_dispatcher_integration.py
      ...
    conftest.py
```

### Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<method_name>_<scenario>` or `test_<behavior>`

### Test Execution

```bash
# All tests
make test

# Fast (no coverage)
make test-fast

# Unit only
make test-unit

# Integration only
make test-integration

# Specific file
poetry run pytest tests/unit/test_models.py -v --timeout=120

# Specific test
poetry run pytest tests/unit/test_models.py -k "test_entity_creation" -v
```

---

## Working with Multiple Projects

### Workspace-Level Commands (from root Makefile)

```bash
# Run across all FLEXT projects
make check-all        # lint + type-check for each project
make test-all         # test all projects

# Target specific project
make PROJECT=flext-auth check
make PROJECT=flext-auth test
```

### Cross-Project Impact Analysis

When modifying `flext-core`, identify affected projects:

```bash
# Find all consumers of a specific module/class
grep -rn "from flext_core.CHANGED_MODULE" --include='*.py' flext-*/src/

# Find all consumers of a specific class
grep -rn "FlextModels" --include='*.py' flext-*/src/ | grep -v __pycache__
```

---

## Pre-Commit Hooks

Configured in `.pre-commit-config.yaml`:

- Ruff (lint + format)
- Various file-level checks (trailing whitespace, end-of-file, etc.)

Run manually:

```bash
poetry run pre-commit run --all-files
```

---

## Docstring Convention

The project uses Google-style docstrings (enforced by Ruff `D` rules):

```python
def process_command(
    self,
    command: m.Cqrs.Command,
    *,
    timeout: float = 30.0,
) -> FlextResult[bool]:
    """Process a CQRS command through the dispatcher.

    Args:
        command: The command to process.
        timeout: Maximum execution time in seconds.

    Returns:
        FlextResult[bool]: Success result or error details.

    Raises:
        e.DispatchError: If command routing fails.
    """
```

The `"""` docstring goes on the first line if single-line, otherwise multi-line
as shown above.

---

## File Header Convention

Every Python source file has this header:

```python
"""Short description of the module.

Optional longer description with architectural context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# ... imports ...
```

---

## Version Management

- Version defined in `__version__.py` in each package
- Poetry manages versions in `pyproject.toml`
- Subprojects pin `flext-core` as a dependency

---

## Branching and Git Workflow

- Main branch: `main`
- Feature branches: `feature/<description>`
- The 30 submodules each have their own Git repositories
- Workspace-level `.gitmodules` tracks them all
