<!-- TOC START -->

- [Workspace Setup](#workspace-setup)
  - [Prerequisites](#prerequisites)
  - [Initial Setup](#initial-setup)
  - [Key Principle: Single Shared .venv](#key-principle-single-shared-venv)
- [Day-to-Day Development Loop](#day-to-day-development-loop)
  - [1. Start Working on a Subproject](#1-start-working-on-a-subproject)
  - [2. Edit Code](#2-edit-code)
  - [3. Quick Feedback Loop](#3-quick-feedback-loop)
  - [4. Pre-Commit Validation](#4-pre-commit-validation)
- [Toolchain Details](#toolchain-details)
  - [Ruff (Linting + Formatting)](#ruff-linting-formatting)
  - [Pyrefly (Type Checking)](#pyrefly-type-checking)
  - [Pytest (Testing)](#pytest-testing)
  - [Additional Quality Tools](#additional-quality-tools)
- [PYTHONPATH Auto-Discovery](#pythonpath-auto-discovery)
- [Testing Conventions](#testing-conventions)
  - [Test File Structure](#test-file-structure)
  - [Naming Convention](#naming-convention)
  - [Test Execution](#test-execution)
- [Working with Multiple Projects](#working-with-multiple-projects)
  - [Workspace-Level Commands (from root Makefile)](#workspace-level-commands-from-root-makefile)
  - [Cross-Project Impact Analysis](#cross-project-impact-analysis)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [Docstring Convention](#docstring-convention)
- [File Header Convention](#file-header-convention)
- [Version Management](#version-management)
- [Branching and Git Workflow](#branching-and-git-workflow)
<!-- TOC END -->

---

name: flext-development-workflow
description: Verified development workflow including toolchain, testing, and CI/CD for the FLEXT monorepo

---

# FLEXT Development Workflow

**Reviewed**: 2026-02-19 | **Scope**: Coverage source-of-truth migration to pyproject.toml

> **Source of truth**: Verified from `base.mk`, `pyproject.toml`, `.pre-commit-config.yaml`,
> and actual project structure on 2026-02-19.

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

# Install workspace + selected project dependencies
make setup
# Optional scope:
# make setup PROJECT=flext-core
# make setup PROJECTS="flext-core flext-api"

# After setup: upgrade deps and refresh dependency report (or DEPS_REPORT=0 to skip report)
make upgrade

# Typings: stub supply-chain + typing report (optional PROJECT=, PROJECTS=, DEPS_REPORT=0)
make typings
```

### Key Principle: Single Shared .venv

All subprojects share ONE virtual environment at `flext/.venv/`.
The `base.mk` enforces this:

```makefile
WORKSPACE_VENV := $(WORKSPACE_ROOT)/.venv
export VIRTUAL_ENV := $(WORKSPACE_VENV)
export PATH := $(WORKSPACE_VENV)/bin:$(PATH)
```

If a local `.venv/` exists inside a subproject, workspace enforcement removes it automatically during standardized make verb execution.

---

## Day-to-Day Development Loop

### 1. Start Working on a Subproject

```bash
make PROJECT=flext-core check
```

### 2. Edit Code

Follow the rules in these skill documents:

- **Architecture**: `flext-architecture-layers/SKILL.md`
- **Imports**: `flext-import-rules/SKILL.md`
- **Types**: `flext-strict-typing/SKILL.md`
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.

### 3. Quick Feedback Loop

```bash
make check
make test
# Optional focused run:
# make test PYTEST_ARGS="-k unit"
```

### 4. Pre-Commit Validation

```bash
make validate   # Extended non-lint validation (optional FIX=1)
```

---

## Toolchain Details

### Ruff (Linting + Formatting)

- Config: `ruff-shared.toml` at workspace root
- Each project's `pyproject.toml` extends it: `extend = "../ruff-shared.toml"`
- Zero tolerance: lint/type/security failures fail `make check`
- Preview mode enabled for latest rules
- Auto-fix path: `make validate FIX=1`
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
- Run through standardized gate: `make check`
- Zero tolerance: ANY type error fails the build

### Pytest (Testing)

- Config: `pyproject.toml` section `[tool.pytest.ini_options]`
- Coverage config: `pyproject.toml` section `[tool.coverage]` (source of truth for `run.source` and `report.fail_under`)
- Run: `make test`
- Coverage threshold: per-project via `pyproject.toml` `[tool.coverage.report] fail_under`
- No `--cov*` flags in pytest addopts — coverage is owned by `[tool.coverage]` only
- Optional selector: `PYTEST_ARGS="-k <expr>"`
- Markers: `unit`, `integration`

### Additional Quality Tools

These tools run behind standardized verbs:

- `make check`: ruff + format check + pyrefly + bandit
- `make validate`: radon + interrogate (with optional `FIX=1`)
- `make security`: explicit bandit gate

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

# Focused selection through pytest arguments
make test PYTEST_ARGS="-k unit"

# Specific file (scoped project)
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_models.py -v --timeout=120"

# Specific test selector (scoped project)
make PROJECT=flext-core test PYTEST_ARGS="tests/unit/test_models.py -k test_entity_creation -v"
```

---

## Working with Multiple Projects

### Workspace-Level Commands (from root Makefile)

```bash
# Default scope: all discovered projects
make check
make test
make validate

# Target a single project
make PROJECT=flext-auth check
make PROJECT=flext-auth test

# Target multiple projects
make PROJECTS="flext-core flext-api" validate FIX=1

# Pass pytest selectors to project tests
make PROJECT=flext-auth test PYTEST_ARGS="-k unit"
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
