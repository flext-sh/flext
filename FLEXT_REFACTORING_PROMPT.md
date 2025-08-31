# FLEXT Ecosystem Refactoring Agent — STRICT FULL PROMPT (UPDATED 2025-01-27)

**Enterprise-Grade LLM Agent Instructions for FLEXT Architecture Compliance**
**This prompt assumes the virtual environment is already activated:**
`source ~/flext/.venv/bin/activate`
**Do not change this path. Do not export PYTHONPATH. Do not prefix commands with `env`.**

---

## 🎯 Mission Statement (Non-Negotiable)

Read calmly, act meticulously, and execute via a continuously updated **TODO Plan**.
**Goal:** 100% compliance with FLEXT architectural standards with **zero** regressions and **zero** issues in **Ruff**, **Mypy (strict)**, **Pyright**, and **Pytest**.

**CRITICAL: FLEXT-CORE IS NOW THE PROVEN FOUNDATION - REPLICATE ITS PATTERNS EVERYWHERE**

Based on the current state of flext-core (version 0.9.0), you MUST:

* **REPLICATE flext-core patterns** exactly as implemented and proven working
* **USE ONLY flext-core foundation** - it is now production-ready with 75%+ coverage
* **FOLLOW the Clean Architecture layers** as established in flext-core
* **IMPLEMENT FlextResult railway pattern** everywhere for error handling
* **USE dependency injection patterns** via get_flext_container()
* **INHERIT from proven base classes** (FlextModels.Entity, FlextValueObject, FlextDomainService)
* **APPLY strict type safety** with MyPy strict mode and Python 3.13+
* **MAINTAIN 75%+ test coverage** as proven achievable in flext-core
* **FOLLOW PEP8 naming** and **layered module organization**
* **USE root-level imports** only (outside same project) - `from flext_core import X`
* **VALIDATE with quality gates** after EVERY edit using make commands
* **NEVER** change `pyproject.toml`, lint configs, or use ignore statements
* **NEVER** break public APIs; maintain backward compatibility
* **FIX ROOT CAUSES**, not symptoms - follow flext-core debugging patterns

---

## 🔧 Environment Assumptions (Strict)

* Active venv: **`~/flext/.venv`**. Do **not** alter it.
* **No** use of `PYTHONPATH`.
* **No** use of `env` prefixes in commands.
* Commands below rely on PATH resolution inside the activated venv.

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
│   ├── typings.py             # Type definitions and aliases (T, U, V, etc.)
│   └── protocols.py           # Interface definitions and contracts
│
├── Domain Layer (DDD Patterns)
│   ├── models.py              # Pydantic models and JSON schemas
│   ├── domain_services.py     # Domain service patterns and operations
│   └── root_models.py         # RootModel patterns for validation
│
├── Application Layer (CQRS/Handlers)
│   ├── commands.py            # FlextCommands pattern and CQRS foundation
│   ├── handlers.py            # Handler implementations and registry
│   ├── validation.py          # Validation framework with predicates
│   ├── payload.py             # Message/event patterns for integration
│   └── guards.py              # Type guards and validation decorators
│
├── Infrastructure Layer (Cross-cutting)
│   ├── config.py              # Configuration management with Pydantic Settings
│   ├── loggings.py            # Structured logging with structlog integration
│   ├── observability.py       # Metrics, tracing, monitoring abstractions
│   └── context.py             # Request/operation context management
│
├── Support Modules (Utilities & Extensions)
│   ├── mixins.py              # Reusable behavior patterns
│   ├── decorators.py          # Enterprise decorator patterns
│   ├── utilities.py           # Helper functions, generators, type guards
│   ├── fields.py              # Field validation and metadata
│   ├── services.py            # Service layer abstractions
│   ├── delegation_system.py   # Mixin delegation patterns
│   ├── schema_processing.py   # Schema validation and processing
│   ├── type_adapters.py       # Type adaptation utilities
│   └── legacy.py              # Backward compatibility layer
└── __init__.py                # Wildcard imports with __all__ aggregation
```

### ✅ PROVEN Quality Standards (ENFORCE EVERYWHERE)

**flext-core has proven these standards work - APPLY TO ALL PROJECTS:**

```bash
# MANDATORY commands that MUST work in ALL projects:
make setup                 # Complete dev environment setup
make validate              # ALL quality gates (lint + type + security + test)
make check                 # Quick validation (lint + type-check only)
make test                  # 75%+ coverage requirement (PROVEN achievable)
make lint                  # Ruff linting - ZERO errors
make type-check            # MyPy strict mode - ZERO errors  
make format                # Auto-format code (79 char line limit)
make security              # Bandit + pip-audit scanning
```

### ✅ PROVEN Error Handling Pattern (MANDATORY EVERYWHERE)

**flext-core has established FlextResult as the foundation - USE EVERYWHERE:**

```python
# ✅ CORRECT - Proven pattern from flext-core
from flext_core import FlextResult

def business_operation(data: dict) -> FlextResult[ProcessedData]:
    """MANDATORY: All business operations must return FlextResult."""
    if not data:
        return FlextResult[None].fail("Data required", error_code="VALIDATION_ERROR")

    # Railway-oriented composition (PROVEN PATTERN)
    return (
        validate_data(data)
        .flat_map(lambda d: process_data(d))      # Chain operations
        .map(lambda d: enrich_data(d))            # Transform success
        .map_error(lambda e: f"Processing failed: {e}")  # Handle errors
    )

# Consumption pattern
result = business_operation(data)
if result.success:
    processed = result.unwrap()  # Safe unwrap after success check
else:
    logger.error(f"Operation failed: {result.error}")
```

### ✅ PROVEN Dependency Injection Pattern (MANDATORY)

**flext-core has established the container pattern - USE EVERYWHERE:**

```python
# ✅ CORRECT - Proven pattern from flext-core
from flext_core import get_flext_container

# Registration (typically in application startup)
container = get_flext_container()
container.register("database", DatabaseService())
container.register_factory("logger", lambda: create_logger())

# Consumption (in business logic)
def service_operation() -> FlextResult[Data]:
    db_result = container.get("database")
    if db_result.failure:
        return FlextResult[None].fail("Database service unavailable")
    
    db = db_result.unwrap()
    return db.fetch_data()
```

### ✅ PROVEN Domain Modeling Pattern (MANDATORY)

**flext-core has proven DDD patterns work - REPLICATE EVERYWHERE:**

```python
# ✅ CORRECT - Proven patterns from flext-core
from flext_core import FlextModels

class Email(FlextValueObject):
    """Value objects are immutable and compared by value."""
    address: str

    def validate_business_rules(self) -> FlextResult[None]:
        if "@" not in self.address:
            return FlextResult[None].fail("Invalid email")
        return FlextResult[None].ok(None)

class User(FlextModels.Entity):
    """Entities have identity and lifecycle."""
    name: str
    email: Email

    def activate(self) -> FlextResult[None]:
        """Business logic returns FlextResult."""
        if self.is_active:
            return FlextResult[None].fail("Already active")
        self.is_active = True
        return FlextResult[None].ok(None)

class UserAggregate(FlextModels.AggregateRoot):
    """Aggregate roots enforce consistency boundaries."""
    user: User

    def register_user(self, data: dict) -> FlextResult[User]:
        # Domain events are automatically tracked
        return self.create_user(data)
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

2. **domain_services.py - Use FlextDomainService**

```python
# ✅ CORRECT - flext-core proven service patterns
from flext_core import FlextDomainService, FlextResult

class UserService(FlextDomainService[FlextResult[UserModel]]):
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
from flext_core import FlextHandlers, FlextResult

class ProjectHandlers(FlextHandlers):
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

**CRITICAL: Use the SAME quality gates that made flext-core successful**

### ✅ Development Commands (EXACTLY as in flext-core)

```bash
# ✅ PROVEN commands from successful flext-core implementation
make setup                 # Complete dev environment setup
make validate              # Run ALL quality gates (lint + type + security + test)
make check                 # Quick validation (lint + type-check only)
make lint                  # Ruff linting - ZERO tolerance
make type-check            # MyPy strict mode - ZERO tolerance
make test                  # 75%+ coverage (proven achievable)
make security              # Bandit + pip-audit scanning
make format                # Auto-format code (79 char limit)
make clean                 # Clean build artifacts
make docs                  # Build documentation
make build                 # Build package

# Single letter aliases (proven useful)
make t                     # test
make l                     # lint  
make f                     # format
make tc                    # type-check
make v                     # validate
```

### ✅ Testing Standards (PROVEN EFFECTIVE)

```bash
# ✅ PROVEN testing approaches from flext-core
make test-unit             # Unit tests only
make test-integration      # Integration tests only
make test-fast             # Tests without coverage
make coverage-html         # HTML coverage report

# Advanced testing (proven patterns)
poetry run pytest tests/unit/ -m "not slow" --tb=short -q
poetry run pytest tests/unit/ --cov=src/project_name --cov-report=term-missing
poetry run pytest --lf --ff -x  # Last failed with fail-fast
```

### ✅ Type Safety Standards (ZERO TOLERANCE PROVEN)

```bash
# ✅ PROVEN type safety from flext-core (ZERO errors)
mypy src/ --strict --show-error-codes         # Must be 0 errors
pyright src/ --level error                    # Must be 0 errors
ruff check src/ tests/ examples/ scripts/     # Must be 0 errors
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

### ✅ MANDATORY __init__.py Pattern (PROVEN from flext-core)

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
from project_name.domain_services import *

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

__all__: list[str] = []
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

1. **__version__.py** (Simple start)
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

2. **domain_services.py** (Business logic)
```python  
from flext_core import FlextDomainService, FlextResult

class ProjectService(FlextDomainService[FlextResult[ProjectModel]]):
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

### ❌ Configuration Modifications (NEVER ALLOWED)

**These files are PROVEN to work - DO NOT MODIFY:**
- `pyproject.toml` - Copy from flext-core with minimal changes
- Makefile - Copy from flext-core pattern exactly  
- Linting configurations - Use flext-core proven settings
- Test configurations - Use flext-core proven settings

### ❌ Local Implementations (FORBIDDEN)

**flext-core provides these - NEVER RECREATE LOCALLY:**
- FlextResult - Use from flext-core
- Dependency injection - Use get_flext_container()
- Logging - Use FlextLogger() from flext-core
- Base classes - Use FlextModels.Entity, FlextValueObject, FlextDomainService
- Validation - Use FlextModels with Pydantic
- Constants - Inherit from FlextConstants
- Exceptions - Inherit from FlextExceptions

### ❌ Quality Gate Bypassing (ZERO TOLERANCE)

**These practices are FORBIDDEN:**
- `# type: ignore` without specific justification
- `# noqa` without specific rule codes
- Relaxing mypy/ruff settings 
- Skipping test coverage requirements
- Using non-strict type checking

---

## 🏆 Success Criteria (PROVEN ACHIEVABLE)

### ✅ Quality Metrics (BASED ON flext-core SUCCESS)

**These standards are PROVEN achievable:**

```bash
# PEP8 Compliance (flext-core achieved 100%)
ruff check src/ tests/ examples/ scripts/  # 0 errors

# Type Safety (flext-core achieved 100% in src/)
mypy src/ --strict --show-error-codes      # 0 errors  
pyright src/ --level error                 # 0 errors

# Test Coverage (flext-core achieved 75%+)
pytest --cov=src/project_name --cov-report=term-missing --cov-fail-under=75

# Security (flext-core achieved 0 issues)
bandit -r src/                             # 0 high/medium issues
pip-audit                                  # 0 vulnerabilities
```

### ✅ Architecture Compliance (PROVEN PATTERNS)

```bash
# flext-core Integration (100% usage)
grep -r "from flext_core import" src/ | wc -l     # Should be > 10

# FlextResult Usage (100% error handling)  
grep -r "FlextResult\[" src/ | wc -l              # Should be > 5

# No Local Base Classes (0 violations)
grep -r "class.*Base.*ABC" src/ | wc -l           # Should be 0

# Pydantic Integration (100% models)
grep -r "FlextModels" src/ | wc -l                 # Should be > 0
```

### ✅ Development Experience (PROVEN WORKFLOW)

**These commands MUST work exactly as in flext-core:**

```bash
make setup         # Complete environment setup
make validate      # All quality gates pass
make check         # Quick validation passes  
make test          # 75%+ coverage achieved
make build         # Package builds successfully
make docs          # Documentation generates

# Import functionality (100% working)
python -c "import project_name; print(dir(project_name))"
python -c "from project_name import ProjectService; print('✅')"
```

---

## 🎯 CRITICAL SUCCESS FACTORS

**BASED ON flext-core's proven development experience:**

1. **Follow the proven order** - Foundation → Domain → Application → Infrastructure
2. **Validate continuously** - After every single module addition
3. **Use flext-core patterns** - Don't reinvent, replicate proven success
4. **Maintain quality gates** - Zero tolerance for regressions
5. **Copy successful configurations** - Makefile, pyproject.toml, etc.
6. **Inherit from flext-core** - Base classes, constants, exceptions
7. **Use dependency injection** - get_flext_container() everywhere
8. **Apply railway pattern** - FlextResult for all business operations
9. **Enforce type safety** - MyPy strict mode, Python 3.13+
10. **Achieve test coverage** - 75%+ is proven achievable

**VERIFICATION-FIRST DEVELOPMENT (CRITICAL LESSON from flext-core):**

**ALWAYS verify before asserting anything:**

```bash  
# Before claiming something works:
python -c "from project_name import ClassName; print('✅')"  # Test actual execution

# Before assuming imports exist:
cat src/project_name/__init__.py  # Check actual exports

# Before assuming API signatures:
python -c "from flext_core import FlextResult; help(FlextResult)"  # Verify methods
```

**NEVER assume based on:**
- File names or "logical" patterns
- What "should" work without testing
- Previous session memory

---

## 🚨 FINAL REMINDERS

**flext-core is now the PROVEN FOUNDATION with:**
- ✅ 75%+ test coverage achieved
- ✅ Zero ruff/mypy/pyright errors in src/
- ✅ Complete Clean Architecture implementation  
- ✅ Production-ready FlextResult railway pattern
- ✅ Proven dependency injection patterns
- ✅ Successful DDD implementation
- ✅ Working make commands for all quality gates

**YOUR MISSION: REPLICATE THIS SUCCESS IN ALL OTHER PROJECTS**

**ALWAYS:**
- Copy proven patterns from flext-core exactly
- Use flext-core as foundation dependency
- Follow the established layered architecture
- Maintain the proven quality standards
- Validate continuously with make commands

**NEVER:**
- Reinvent patterns that work in flext-core
- Relax quality standards below flext-core level
- Skip validation steps that ensured flext-core success
- Create local implementations of flext-core functionality

**The path to success is clear: Follow the flext-core blueprint exactly.**
