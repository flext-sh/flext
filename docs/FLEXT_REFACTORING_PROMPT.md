# FLEXT Ecosystem Refactoring Agent — IMPLEMENTATION GUIDE (UPDATED 2025-01-18)

**Enterprise-Grade LLM Agent Instructions for FLEXT Architecture Implementation**

**AUTHORITY**: This document provides detailed implementation guidance based on workspace standards defined in [CLAUDE.md](CLAUDE.md).

**PREREQUISITE**: Virtual environment must be activated: `source ~/flext/.venv/bin/activate`
**Do not change this path. Do not export PYTHONPATH. Do not prefix commands with `env`.**

---

## 🎯 Mission Statement (Non-Negotiable)

Read calmly, act meticulously, and execute via a continuously updated **TODO Plan**.
**Goal:** Full compliance with FLEXT architectural standards as defined in [CLAUDE.md](CLAUDE.md) with **zero** regressions and **zero** issues in **Ruff**, **Mypy (strict)**, **Pyright**, and **Pytest**.

**CRITICAL: FOLLOW CLAUDE.md WORKSPACE STANDARDS EXACTLY**

Based on workspace standards in [CLAUDE.md](CLAUDE.md) and the proven flext-core foundation (version 0.9.0), you MUST:

- **FOLLOW all absolute prohibitions** as defined in CLAUDE.md
- **USE ONLY flext-core foundation** - production-ready with 75%+ coverage
- **IMPLEMENT unified class pattern** exactly as specified in CLAUDE.md
- **USE FlextResult pattern** everywhere for error handling (see CLAUDE.md examples)
- **APPLY dependency injection** via FlextContainer as specified in CLAUDE.md
- **INHERIT from proven base classes** per CLAUDE.md architectural principles
- **MAINTAIN 75% minimum coverage** (proven achievable), 100% aspirational
- **USE root-level imports** only as defined in CLAUDE.md import strategy
- **VALIDATE with quality gates** after EVERY edit using make commands from CLAUDE.md
- **USE MCP servers** (serena, sequential-thinking, context7) as specified in CLAUDE.md
- **NEVER** violate zero-tolerance policies defined in CLAUDE.md

---

## 🔧 Environment Assumptions (Strict)

- Active venv: **`~/flext/.venv`**. Do **not** alter it.
- **No** use of `PYTHONPATH`.
- **No** use of `env` prefixes in commands.
- Commands below rely on PATH resolution inside the activated venv.

---

## 📋 Mandatory TODO Plan

```
Phase X: [Description]
□ Task 1: [Specific action + exact validation command(s)]
□ Task 2: [Specific action + exact validation command(s)]
□ Task 3: [Specific action + exact validation command(s)]
Status: [In Progress/Completed]
Validation: [make validate/make check/make test: PASS|FAIL]
```

---

## 🏗️ flext-core Foundation Architecture (PROVEN PATTERNS)

### ✅ ESTABLISHED Module Organization (REPLICATE EXACTLY)

**flext-core has established this proven layered structure - COPY TO ALL PROJECTS:**

```
src/project_namespace/
├── Foundation Layer (Core Patterns)
│   ├── __version__.py         # Version information
│   ├── result.py              # FlextResult[T] railway pattern with map/flat_map
│   ├── container.py           # Dependency injection container with FlextResult
│   ├── exceptions.py          # Exception hierarchy with error codes and metrics
│   ├── constants.py           # FlextConstants, enums, error codes, performance metrics
│   ├── typings.py
│   └── protocols.py           # Interface definitions and contracts
│
├── Domain Layer (DDD Patterns)
│   ├── models.py              # Pydantic models and JSON schemas
│   ├── service.py     # Domain service patterns and operations
│   └── root_models.py         # RootModel patterns for validation
│
├── Application Layer (CQRS/Handlers)
│   ├── cqrs.py                # FlextCqrs pattern and CQRS foundation
│   ├── handlers.py            # FlextHandlers command/query abstraction
│   ├── bus.py                 # FlextBus command routing implementation
│   ├── handlers.py            # Handler implementations and registry
│   ├── validation.py          # Validation framework with predicates
│   ├── payload.py             # Message/event patterns for integration
│   └── guards.py
│
├── Infrastructure Layer (Cross-cutting)
│   ├── config.py              # Configuration management with Pydantic Settings
│   ├── loggings.py            # Structured logging with structlog integration
│   ├── observability.py       # Metrics, tracing, monitoring abstractions
│   └── context.py             # Request/operation context management
│
├── Support Modules (Utilities & Extensions)
│   ├── mixins.py              # Reusable behavior patterns
│   ├── utilities.py           # Helper functions, generators, type guards
│   ├── fields.py              # Field validation and metadata
│   ├── services.py            # Service layer abstractions
│   ├── delegation_system.py   # Mixin delegation patterns
│   ├── schema_processing.py   # Schema validation and processing
│   ├── type_adapters.py
│   └── legacy.py              # Backward compatibility layer
└── __init__.py                # Wildcard imports with __all__ aggregation
```

### ✅ PROVEN Quality Standards (FROM CLAUDE.md)

**Use quality standards as defined in [CLAUDE.md](CLAUDE.md) - APPLY TO ALL PROJECTS:**

```bash
# MANDATORY commands from CLAUDE.md that MUST work in ALL projects:
make validate              # Complete pipeline (lint + type + security + test)
make check                 # Quick validation (lint + type-check only)
make test                  # 75% minimum coverage (proven achievable)
make lint                  # Ruff linting (ZERO tolerance)
make type-check            # MyPy/PyRight validation
make format                # Auto-format
```

**See [CLAUDE.md](CLAUDE.md) for comprehensive validation script and detailed quality gate requirements.**

### ✅ PROVEN Error Handling Pattern (FROM CLAUDE.md)

**Use FlextResult pattern as defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) Section "FlextResult Pattern (MANDATORY)" for:**

- Complete FlextResult usage examples
- Railway-oriented programming patterns
- Safe error handling without try/except fallbacks
- Integration with unified class pattern

**Reference implementation:**

```python
# See CLAUDE.md for complete examples
from flext_core import FlextResult

# Follow CLAUDE.md patterns exactly for all business operations
```

### ✅ PROVEN Dependency Injection Pattern (FROM CLAUDE.md)

**Use dependency injection as defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) Section "Core Architectural Principles" for:**

- FlextContainer.get_global() usage patterns
- Dependency injection in unified class pattern
- Integration with domain services

**Reference implementation:**

```python
# See CLAUDE.md for complete dependency injection examples
from flext_core import FlextContainer

# Follow CLAUDE.md unified class pattern with dependency injection
```

### ✅ PROVEN Domain Modeling Pattern (FROM CLAUDE.md)

**Use domain modeling as defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) Section "Python 3.13 + Pydantic Patterns" for:**

- FlextModel usage with Pydantic v2 integration
- Advanced type safety patterns
- Protocol-based design patterns
- SOLID principles implementation

**Reference implementation:**

```python
# See CLAUDE.md for complete domain modeling examples
from flext_core import FlextModels

# Follow CLAUDE.md patterns for entity and value object design
```

---

## 🏗️ Systematic Refactoring Framework (BASED ON flext-core SUCCESS)

### Phase 1 — flext-core Integration Analysis (MANDATORY first)

1. **Study flext-core patterns FIRST (proven working):**

```bash
# Read successful implementation patterns
cat ~/flext/flext-core/src/flext_core/__init__.py
cat ~/flext/flext-core/src/flext_core/result.py
cat ~/flext/flext-core/src/flext_core/container.py
cat ~/flext/flext-core/Makefile

# Test actual API signatures (don't assume)
python -c "from flext_core import FlextResult; help(FlextResult)"
python -c "from flext_core import get_flext_container; help(get_flext_container)"
python -c "from flext_core import FlextModels.Entity, FlextValueObject; print('DDD patterns available')"
```

2. **Map current project vs flext-core standards:**

```bash
find src/ -name "*.py" -exec head -20 {} \;
grep -r "class.*Base\|class.*Abstract" src/ --include="*.py"
grep -r "from flext_core import" src/ --include="*.py" | wc -l  # Should be > 0
grep -r "FlextResult" src/ --include="*.py" | wc -l           # Should be > 0
```

### Phase 2 — Foundation Layer Implementation (CRITICAL)

**MANDATORY: Implement Foundation Layer first (proven order from flext-core)**

1. **result.py - FlextResult Pattern (TOP PRIORITY)**

```python
# ✅ CORRECT - Import and use flext-core FlextResult everywhere
from flext_core import FlextResult

# Replace ALL exception raising with FlextResult patterns
def operation() -> FlextResult[str]:
    try:
        # Business logic here
        return FlextResult[None].ok("success")
    except Exception as e:
        return FlextResult[None].fail(str(e))
```

2. **constants.py - Use FlextConstants**

```python
# ✅ CORRECT - Inherit from flext-core constants
from flext_core import FlextConstants

class ProjectConstants(FlextConstants):
    """Project constants inheriting from flext-core."""

    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3

    # Access parent constants
    @property
    def validation_rules(self):
        return self.Validation  # From FlextConstants
```

3. **exceptions.py - Use FlextExceptions**

```python
# ✅ CORRECT - Inherit from flext-core exceptions
from flext_core import FlextExceptions

class ProjectExceptions(FlextExceptions.Error):
    """Project exceptions inheriting from flext-core."""

    class ConfigurationError(FlextExceptions.Error):
        """Configuration specific error."""
        pass

    class ConnectionError(FlextExceptions.Error):
        """Connection specific error."""
        pass
```

### Phase 3 — Domain Layer Implementation (PROVEN PATTERNS)

1. **models.py - Use FlextModels (Pydantic-based)**

```python
# ✅ CORRECT - flext-core proven Pydantic integration
from flext_core import FlextModels
from pydantic import Field

class UserModel(FlextModels):
    """User model with flext-core validation."""

    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=18, le=120)

    # Use Pydantic v2 configuration
    model_config = {
        'str_strip_whitespace': True,
        'validate_assignment': True,
        'extra': 'forbid'
    }
```

2. **service.py - Use FlextService**

```python
# ✅ CORRECT - flext-core proven service patterns
from flext_core import FlextService, FlextResult

class UserService(FlextService[FlextResult[UserModel]]):
    """User service using flext-core foundation."""

    def __init__(self):
        super().__init__()
        self._container = get_flext_container()
        self._logger = FlextLogger(__name__)

    def create_user(self, data: dict) -> FlextResult[UserModel]:
        """Create user with proper error handling."""
        try:
            user = UserModel.model_validate(data)
            return FlextResult[UserModel].ok(user)
        except ValidationError as e:
            return FlextResult[UserModel].fail(f"Validation failed: {e}")
```

### Phase 4 — Application Layer Implementation (PROVEN HANDLERS)

```python
# ✅ CORRECT - flext-core proven handler patterns
from flext_core import FlextProcessors, FlextResult

class ProjectHandlers(FlextProcessors):
    """Project handlers using flext-core foundation."""

    def handle_user_creation(self, command: dict) -> FlextResult[dict]:
        """Handle user creation command."""
        return (
            self._validate_command(command)
            .flat_map(self._create_user)
            .map(self._format_response)
        )
```

### Phase 5 — Infrastructure Integration (PROVEN INFRASTRUCTURE)

```python
# ✅ CORRECT - flext-core proven infrastructure patterns
from flext_core import FlextLogger, get_flext_container

class ProjectInfrastructure:
    """Infrastructure using flext-core utilities."""

    def __init__(self):
        self._logger = FlextLogger(__name__)      # Use flext-core logging
        self._container = get_flext_container()   # Use flext-core DI

    def setup_services(self):
        """Setup services using dependency injection."""
        self._container.register("user_service", UserService())
        self._logger.info("Services registered successfully")
```

---

## 🛡️ Quality Gates (PROVEN FROM flext-core)

**CRITICAL: Use quality gates as defined in [CLAUDE.md](CLAUDE.md)**

### ✅ Development Commands (FROM CLAUDE.md)

**Use the exact commands specified in [CLAUDE.md](CLAUDE.md) Section "Universal Quality Commands":**

```bash
# MANDATORY commands from CLAUDE.md:
make validate              # Complete validation pipeline
make check                 # Quick validation (lint + type)
make test                  # Real tests with 75% minimum coverage
make lint                  # Ruff linting (ZERO tolerance)
make type-check            # MyPy/PyRight validation
make format                # Auto-format
```

**See [CLAUDE.md](CLAUDE.md) for comprehensive validation script and testing strategy.**

### ✅ Testing Standards (FROM CLAUDE.md)

**Use testing strategy as defined in [CLAUDE.md](CLAUDE.md) Section "Testing Strategy (75% MINIMUM COVERAGE)":**

```bash
# MANDATORY testing from CLAUDE.md:
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=75
pytest -m "not mock" -v    # Functional tests preferred

# See CLAUDE.md for complete testing strategy
```

### ✅ Type Safety Standards (FROM CLAUDE.md)

**Use type safety standards as defined in [CLAUDE.md](CLAUDE.md) Section "Required Standards":**

```bash
# ZERO errors in src/ as specified in CLAUDE.md:
make type-check            # MyPy + PyRight validation
make lint                  # Ruff linting (ZERO tolerance)

# See CLAUDE.md for comprehensive validation script
```

---

## 🏗️ Project Structure Standardization (BASED ON flext-core SUCCESS)

### ✅ MANDATORY Makefile (COPY from flext-core)

```makefile
# ✅ COPY this successful Makefile pattern from flext-core
PROJECT_NAME := project-name
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests
MIN_COVERAGE := 75

# Quality Gates (PROVEN EFFECTIVE)
.PHONY: validate
validate: lint type-check security test

.PHONY: check
check: lint type-check

.PHONY: lint
lint:
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR)

.PHONY: type-check
type-check:
	$(POETRY) run mypy $(SRC_DIR) --strict

.PHONY: test
test:
	$(POETRY) run pytest $(TESTS_DIR) --cov=$(PROJECT_NAME) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

.PHONY: security
security:
	$(POETRY) run bandit -r $(SRC_DIR)
	$(POETRY) run pip-audit
```

### ✅ MANDATORY pyproject.toml (BASED ON flext-core SUCCESS)

```toml
# ✅ Copy successful configuration patterns from flext-core
[build-system]
build-backend = "poetry.core.masonry.api"
requires = ["poetry-core>=1.9.0"]

[project]
name = "project-name"
version = "0.1.0"
description = "Project description following FLEXT patterns"
requires-python = ">=3.13,<3.14"
dependencies = [
    "flext-core>=0.9.0",  # MANDATORY dependency
    "pydantic>=2.11.7",
    "structlog>=25.4.0",
]

[tool.mypy]
# ✅ PROVEN mypy configuration from flext-core
strict = true
python_version = "3.13"
show_error_codes = true
show_error_context = true
mypy_path = ["src"]
files = ["src"]
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
# ✅ PROVEN pytest configuration from flext-core
addopts = ["--maxfail=1000000", "--strict-config", "--strict-markers", "--tb=short", "-ra"]
testpaths = ["tests"]
minversion = "8.0"
```

### ✅ MANDATORY **init**.py Pattern (PROVEN from flext-core)

```python
# ✅ COPY this successful pattern from flext-core
"""Project Name - Description following FLEXT patterns.

This module provides functionality following FLEXT architectural patterns
with proper layered imports and zero circular dependencies.
"""

from __future__ import annotations

# Foundation Layer - Import first (proven order)
from project_name.__version__ import *
from project_name.constants import *
from project_name.typings import *
from project_name.result import *
from project_name.exceptions import *
from project_name.protocols import *

# Domain Layer - Depends only on Foundation
from project_name.models import *
from project_name.service import *

# Application Layer - Depends on Domain + Foundation
from project_name.commands import *
from project_name.handlers import *
from project_name.validation import *

# Infrastructure Layer - Depends on all above
from project_name.config import *
from project_name.container import *
from project_name.loggings import *

# Support Layer - Last
from project_name.utilities import *
from project_name.mixins import *
from project_name.decorators import *

# Aggregate __all__ exports (proven pattern)
import project_name.constants as _constants
import project_name.models as _models
# ... other imports

__all__: FlextTypes.Core.StringList = []
for module in [_constants, _models]:  # Add all modules
    if hasattr(module, "__all__"):
        __all__.extend(module.__all__)

__all__ = sorted(set(__all__))  # Remove duplicates and sort
```

---

## 🔄 Implementation Workflow (BASED ON flext-core SUCCESS)

### Phase 1: Environment Setup (EXACTLY as flext-core)

```bash
# ✅ COPY successful setup from flext-core
mkdir -p project-name/{src/project_name,tests/{unit,integration,e2e},examples,scripts}
cd project-name

# Create pyproject.toml (copy from flext-core with adaptations)
# Create Makefile (copy from flext-core with project name changes)
# Create .gitignore, .pre-commit-config.yaml, etc.

# Setup development environment
poetry install
poetry run pre-commit install
make setup
```

### Phase 2: Foundation Implementation (PROVEN ORDER)

1. \***\*version**.py\*\* (Simple start)

```python
"""Version information."""
__version__ = "0.1.0"
__all__ = ["__version__"]
```

2. **constants.py** (flext-core inheritance)

```python
from flext_core import FlextConstants

class ProjectConstants(FlextConstants):
    """Project constants."""
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3

__all__ = ["ProjectConstants"]
```

3. **result.py** (Core pattern)

```python
# Re-export flext-core result (don't reimplement)
from flext_core import FlextResult

__all__ = ["FlextResult"]
```

4. **Validate after each module**:

```bash
make check          # Quick validation
python -c "from project_name.constants import ProjectConstants; print('✅ Constants work')"
```

### Phase 3: Domain Layer (PROVEN DDD PATTERNS)

1. **models.py** (Pydantic + flext-core)

```python
from flext_core import FlextModels
from pydantic import Field

class ProjectModel(FlextModels):
    """Project model following flext-core patterns."""

    name: str = Field(..., min_length=1)
    description: str = Field(default="")

__all__ = ["ProjectModel"]
```

2. **service.py** (Business logic)

```python
from flext_core import FlextService, FlextResult

class ProjectService(FlextService[FlextResult[ProjectModel]]):
    """Project service following flext-core patterns."""

    def create_project(self, data: dict) -> FlextResult[ProjectModel]:
        """Create project with validation."""
        try:
            model = ProjectModel.model_validate(data)
            return FlextResult[ProjectModel].ok(model)
        except ValidationError as e:
            return FlextResult[ProjectModel].fail(str(e))

__all__ = ["ProjectService"]
```

### Phase 4: Continuous Validation (PROVEN EFFECTIVE)

**After EVERY module addition:**

```bash
make validate       # Complete validation
make test          # Run tests
python -c "import project_name; print('✅ Imports work')"

# Specific validations
ruff check src/     # 0 errors
mypy src/ --strict  # 0 errors
pytest tests/ -v    # All pass
```

---

## 🚫 ABSOLUTE PROHIBITIONS (LEARNED FROM flext-core SUCCESS)

### ❌ ABSOLUTE PROHIBITIONS (FROM CLAUDE.md)

**Follow all zero-tolerance policies defined in [CLAUDE.md](CLAUDE.md) Section "ABSOLUTE PROHIBITIONS":**

**See [CLAUDE.md](CLAUDE.md) for complete list of:**

- CLI project violations (forbidden imports)
- Code quality violations (multiple classes, helper functions, try/except fallbacks)
- Type safety violations (# type: ignore, object types)

### ❌ Configuration Modifications (FORBIDDEN)

**Per [CLAUDE.md](CLAUDE.md) anti-duplication enforcement - DO NOT:**

- Modify pyproject.toml, Makefile, or linting configurations
- Create local implementations of flext-core functionality
- Relax quality standards below CLAUDE.md requirements

### ❌ Pattern Violations (ZERO TOLERANCE)

**Strictly follow [CLAUDE.md](CLAUDE.md) patterns:**

- Unified class pattern (single class per module)
- FlextResult error handling (no try/except fallbacks)
- Root-level imports only
- MCP server usage for all operations

---

## 🏆 Success Criteria (PROVEN ACHIEVABLE)

### ✅ Quality Metrics (FROM CLAUDE.md)

**Follow quality standards defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) Section "Required Standards" for:**

- Source quality requirements (ZERO errors in src/)
- Test coverage targets (75% minimum, 100% aspirational)
- CLI compliance requirements
- Unified class requirements
- Error handling requirements

```bash
# Use CLAUDE.md validation commands:
make validate      # Complete pipeline as defined in CLAUDE.md
make check         # Quick validation as defined in CLAUDE.md
make test          # 75% minimum coverage (proven achievable)
```

### ✅ Architecture Compliance (FROM CLAUDE.md)

**Follow architectural principles defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) for:**

- Anti-duplication enforcement patterns
- Violation detection commands
- Centralization requirements

### ✅ Development Experience (FROM CLAUDE.md)

**Use development workflow defined in [CLAUDE.md](CLAUDE.md):**

**See [CLAUDE.md](CLAUDE.md) Section "Universal Quality Commands" for complete command set.**

---

## 🎯 CRITICAL SUCCESS FACTORS

**BASED ON [CLAUDE.md](CLAUDE.md) workspace standards:**

1. **Follow CLAUDE.md absolutely** - All principles, patterns, and prohibitions
2. **Use MCP servers** - serena, sequential-thinking, context7 as specified
3. **Validate continuously** - After every change using CLAUDE.md quality gates
4. **Maintain zero tolerance** - For all violations defined in CLAUDE.md
5. **Reference authority** - CLAUDE.md for principles, this document for implementation
6. **Use unified patterns** - Single class per module as defined in CLAUDE.md
7. **Apply FlextResult everywhere** - As specified in CLAUDE.md error handling
8. **Enforce 75% minimum coverage** - With 100% aspirational target
9. **Use root-level imports only** - As defined in CLAUDE.md import strategy
10. **Coordinate with workspace** - Follow CLAUDE.md hierarchy and authority

**VERIFICATION-FIRST DEVELOPMENT (FROM CLAUDE.md):**

**ALWAYS verify using tools before asserting anything:**

```bash
# Use serena for code verification:
# Use sequential-thinking for problem decomposition
# Use context7 for library documentation
# Reference CLAUDE.md for all patterns and standards
```

**NEVER:**

- Assume patterns without checking CLAUDE.md
- Skip MCP server usage as specified in CLAUDE.md
- Violate zero-tolerance policies defined in CLAUDE.md

---

## 🚨 FINAL REMINDERS

**[CLAUDE.md](CLAUDE.md) is the WORKSPACE AUTHORITY with:**

- ✅ Complete architectural principles and patterns
- ✅ Zero-tolerance policies and quality standards
- ✅ MCP server integration requirements
- ✅ Unified class patterns and error handling
- ✅ Anti-duplication enforcement
- ✅ Comprehensive validation scripts

**YOUR MISSION: IMPLEMENT CLAUDE.md STANDARDS EXACTLY**

**ALWAYS:**

- Reference [CLAUDE.md](CLAUDE.md) for all architectural decisions
- Use MCP servers (serena, sequential-thinking, context7) as specified
- Follow unified class pattern and FlextResult error handling
- Maintain 75% minimum coverage with 100% aspirational target
- Validate with quality gates defined in CLAUDE.md

**NEVER:**

- Violate zero-tolerance policies defined in CLAUDE.md
- Skip MCP server usage requirements
- Create patterns not defined in CLAUDE.md
- Relax quality standards below CLAUDE.md requirements

**The path to success is clear: Follow [CLAUDE.md](CLAUDE.md) workspace standards exactly.**

**For questions about principles**: See [CLAUDE.md](CLAUDE.md)
**For implementation details**: Use this document with CLAUDE.md patterns
