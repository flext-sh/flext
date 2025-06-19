# 🎯 FLX Code Quality Guide

> **Function**: Code quality standards and static analysis for FLX development | **Audience**: Developers, code reviewers, team leads | **Status**: Production-Ready

[![Quality](https://img.shields.io/badge/quality-standards-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-green.svg)](../../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Comprehensive code quality standards, static analysis tools, and best practices for maintaining high-quality code in FLX hexagonal architecture projects**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Section**: [Guides](./index.md) → **📄 Current**: Code Quality Guide

### **📍 Learning Path Position**

```
[Development Hub](../index.md) → [Guides](./index.md) → **[Code Quality Guide]** → [Development Workflow](./development-workflow.md)
```

Essential code quality standards and tooling guide for maintaining professional-grade code in FLX framework development.

## Code Quality Philosophy

FLX code quality embodies:

- **Readability First**: Code is written to be read by humans
- **Consistency**: Uniform style and patterns across the codebase
- **Type Safety**: Comprehensive type hints and static analysis
- **Automated Quality**: Tools enforce standards automatically
- **Documentation**: Code is self-documenting with clear intent

## Quality Tools Stack

### Core Quality Tools

```bash
# Install development quality tools
pip install --upgrade \
    black \              # Code formatting
    ruff \               # Fast linting and import sorting
    mypy \               # Static type checking
    pytest \             # Testing framework
    pytest-cov \         # Coverage reporting
    pre-commit \         # Git hooks for quality enforcement
    bandit \             # Security vulnerability scanning
    safety \             # Dependency security checking
```

### Tool Configuration

#### Black Configuration (`pyproject.toml`)

```toml
[tool.black]
line-length = 100
target-version = ['py313']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

#### Ruff Configuration (`pyproject.toml`)

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "C90",    # mccabe complexity
    "T20",    # flake8-print
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
]
ignore = [
    "E501",   # line too long (handled by black)
    "B008",   # do not perform function calls in argument defaults
    "C901",   # too complex (handled by specific complexity limits)
]
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".mypy_cache",
    ".pants.d",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "venv",
]

[tool.ruff.mccabe]
max-complexity = 10

[tool.ruff.isort]
known-first-party = ["flx"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

#### MyPy Configuration (`pyproject.toml`)

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
show_error_codes = true
namespace_packages = true
explicit_package_bases = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_incomplete_defs = false

[[tool.mypy.overrides]]
module = "flx.core.*"
strict = true
disallow_any_generics = true
disallow_subclassing_any = true

[[tool.mypy.overrides]]
module = "flx.adapters.*"
warn_return_any = true
disallow_untyped_calls = true
```

#### pytest Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov=flx",
    "--cov-report=term-missing",
    "--cov-report=html:reports/coverage",
    "--cov-report=xml:reports/coverage.xml",
    "--cov-fail-under=90",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "e2e: marks tests as end-to-end tests",
]
filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]
```

## Code Style Standards

### Python Style Guidelines

#### Function and Method Design

```python
# ✅ Good: Clear, single responsibility
async def create_user(
    username: str,
    email: Email,
    *,
    user_repo: UserRepository,
    event_bus: EventBus,
    logger: FlxLogger
) -> CreateUserResult:
    """Create a new user with validation and event publishing.

    Args:
        username: Unique username for the user
        email: Validated email address
        user_repo: Repository for user persistence
        event_bus: Event bus for publishing domain events
        logger: Logger for operation tracking

    Returns:
        Result containing user ID and success status

    Raises:
        ValidationError: If username or email is invalid
        DuplicateUserError: If username already exists
    """
    if await user_repo.exists_by_username(username):
        raise DuplicateUserError(f"Username '{username}' already exists")

    user = User(username=username, email=email)
    await user_repo.save(user)

    await event_bus.publish(UserCreatedEvent(
        user_id=user.id,
        username=username,
        email=email.value
    ))

    logger.info("User created", extra={
        "user_id": str(user.id),
        "username": username
    })

    return CreateUserResult(success=True, user_id=user.id)

# ❌ Bad: Too many responsibilities, unclear parameters
def process_user_data(data, db, events, log):
    # Multiple responsibilities in one function
    # Unclear parameter types
    # No documentation
    pass
```

#### Class Design Patterns

```python
# ✅ Good: Single responsibility, clear interfaces
class UserService:
    """Application service for user management operations."""

    def __init__(
        self,
        *,
        user_repo: UserRepository,
        event_bus: EventBus,
        logger: FlxLogger
    ) -> None:
        self._user_repo = user_repo
        self._event_bus = event_bus
        self._logger = logger

    async def register_user(
        self,
        registration_data: UserRegistrationData
    ) -> UserRegistrationResult:
        """Register a new user with complete validation."""
        try:
            # Validation
            await self._validate_registration_data(registration_data)

            # Business logic
            user = await self._create_user_entity(registration_data)

            # Persistence
            await self._user_repo.save(user)

            # Events
            await self._publish_user_created_event(user)

            return UserRegistrationResult.success(user.id)

        except Exception as e:
            self._logger.error("User registration failed", exc_info=e, extra={
                "username": registration_data.username
            })
            return UserRegistrationResult.failure(str(e))

# ❌ Bad: Multiple responsibilities, unclear dependencies
class UserManager:
    def __init__(self, db_connection, email_service, cache):
        # Direct dependencies instead of abstractions
        # No type hints
        pass

    def do_user_stuff(self, user_data):
        # Unclear method name and purpose
        # No error handling
        # Mixed concerns
        pass
```

### Type Hints and Annotations

#### Comprehensive Type Annotations

```python
from typing import (
    Optional, List, Dict, Any, Union, Callable, Awaitable,
    TypeVar, Generic, Protocol, runtime_checkable
)
from collections.abc import Sequence, Mapping
from datetime import datetime
from uuid import UUID

T = TypeVar('T')
EntityId = TypeVar('EntityId', bound=UUID)

# ✅ Good: Comprehensive type annotations
@runtime_checkable
class Repository(Protocol[T]):
    """Repository protocol with generic type support."""

    async def save(self, entity: T) -> None:
        """Save entity to storage."""
        ...

    async def find_by_id(self, entity_id: EntityId) -> Optional[T]:
        """Find entity by ID."""
        ...

    async def find_all(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Sequence[T]:
        """Find all entities with optional pagination."""
        ...

class UserRepository(Repository[User]):
    """User-specific repository with additional methods."""

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by unique username."""
        ...

    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email address."""
        ...

# ✅ Good: Complex type annotations
SearchFilters = Dict[str, Union[str, int, bool, List[str]]]
EventHandler = Callable[[DomainEvent], Awaitable[None]]
ConfigValue = Union[str, int, bool, float, List[Any], Dict[str, Any]]

class EventBus:
    """Type-safe event bus implementation."""

    def __init__(self) -> None:
        self._handlers: Dict[type[DomainEvent], List[EventHandler]] = {}

    async def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler
    ) -> None:
        """Subscribe handler to specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish event to all registered handlers."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)

# ❌ Bad: Missing or unclear type annotations
class BadEventBus:
    def __init__(self):  # No return type annotation
        self.handlers = {}  # No type hints

    def subscribe(self, event_type, handler):  # No parameter types
        # Implementation without types
        pass

    def publish(self, event):  # No return type
        # Implementation without types
        pass
```

### Error Handling Patterns

#### Comprehensive Error Handling

```python
# ✅ Good: Specific exception types and proper handling
class UserServiceError(Exception):
    """Base exception for user service errors."""
    pass

class UserNotFoundError(UserServiceError):
    """Raised when user cannot be found."""
    pass

class DuplicateUserError(UserServiceError):
    """Raised when attempting to create duplicate user."""
    pass

class UserValidationError(UserServiceError):
    """Raised when user data validation fails."""
    pass

class UserService:
    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID with proper error handling."""
        try:
            user = await self._user_repo.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError(f"User with ID {user_id} not found")
            return user

        except RepositoryError as e:
            # Log infrastructure error but don't expose details
            self._logger.error("Repository error retrieving user", exc_info=e, extra={
                "user_id": str(user_id)
            })
            raise UserServiceError("Failed to retrieve user") from e

        except Exception as e:
            # Catch unexpected errors
            self._logger.error("Unexpected error retrieving user", exc_info=e, extra={
                "user_id": str(user_id)
            })
            raise UserServiceError("Unexpected error occurred") from e

# ❌ Bad: Generic exceptions and poor error handling
class BadUserService:
    def get_user(self, user_id):
        try:
            user = self.repo.find(user_id)
            return user
        except:  # Bare except clause
            pass  # Silencing errors
        return None  # Unclear return value
```

## Static Analysis Integration

### Pre-commit Hooks Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3.13

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.284
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        exclude: ^tests/

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, ., -f, json, -o, reports/bandit.json]
        exclude: ^tests/

  - repo: https://github.com/Lucas-C/pre-commit-hooks-safety
    rev: v1.3.2
    hooks:
      - id: python-safety-dependencies-check
```

### Continuous Integration Quality Gates

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.13"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Code formatting check
        run: black --check .

      - name: Linting
        run: ruff check .

      - name: Type checking
        run: mypy src/

      - name: Security check
        run: |
          bandit -r . -f json -o reports/bandit.json
          safety check

      - name: Run tests with coverage
        run: pytest --cov-fail-under=90

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: reports/coverage.xml
```

## Code Review Standards

### Review Checklist

#### Architecture and Design

- [ ] **Hexagonal Architecture**: Follows ports and adapters pattern
- [ ] **Single Responsibility**: Each class/function has one clear purpose
- [ ] **Dependency Inversion**: Depends on abstractions, not implementations
- [ ] **Interface Segregation**: Interfaces are focused and cohesive
- [ ] **Open/Closed Principle**: Open for extension, closed for modification

#### Code Quality

- [ ] **Type Annotations**: All functions have complete type hints
- [ ] **Error Handling**: Appropriate exception types and handling
- [ ] **Documentation**: Clear docstrings for public interfaces
- [ ] **Naming**: Self-documenting variable and function names
- [ ] **Complexity**: Functions are focused and not overly complex

#### Testing

- [ ] **Test Coverage**: New code has >90% test coverage
- [ ] **Test Quality**: Tests are meaningful and test behavior
- [ ] **Test Independence**: Tests don't depend on each other
- [ ] **Test Naming**: Test names clearly describe scenarios
- [ ] **Integration Tests**: Complex interactions are integration tested

#### Performance and Security

- [ ] **Performance**: No obvious performance issues
- [ ] **Memory Usage**: Proper resource management
- [ ] **Security**: No security vulnerabilities
- [ ] **Data Validation**: Input validation and sanitization
- [ ] **Logging**: Appropriate logging without sensitive data

### Review Guidelines

```python
# ✅ Good: Code ready for review
class UserRegistrationService:
    """Service for handling user registration workflows.

    This service orchestrates the complete user registration process,
    including validation, persistence, and event publishing.
    """

    def __init__(
        self,
        *,
        user_repo: UserRepository,
        email_service: EmailService,
        event_bus: EventBus,
        logger: FlxLogger
    ) -> None:
        """Initialize the registration service.

        Args:
            user_repo: Repository for user persistence
            email_service: Service for sending emails
            event_bus: Event bus for domain events
            logger: Logger for operation tracking
        """
        self._user_repo = user_repo
        self._email_service = email_service
        self._event_bus = event_bus
        self._logger = logger

    async def register_user(
        self,
        registration_data: UserRegistrationData
    ) -> UserRegistrationResult:
        """Register a new user with complete validation and notification.

        Args:
            registration_data: Validated registration data

        Returns:
            Registration result with success status and user ID

        Raises:
            DuplicateUserError: If username or email already exists
            ValidationError: If registration data is invalid
            RegistrationError: If registration process fails
        """
        try:
            # Validate uniqueness
            await self._validate_user_uniqueness(registration_data)

            # Create user entity
            user = User(
                username=registration_data.username,
                email=registration_data.email,
                profile=registration_data.profile
            )

            # Persist user
            await self._user_repo.save(user)

            # Send welcome email
            await self._email_service.send_welcome_email(user)

            # Publish event
            await self._event_bus.publish(UserRegisteredEvent(
                user_id=user.id,
                username=user.username,
                email=user.email.value
            ))

            self._logger.info("User registered successfully", extra={
                "user_id": str(user.id),
                "username": user.username
            })

            return UserRegistrationResult.success(user.id)

        except (DuplicateUserError, ValidationError):
            # Re-raise domain errors
            raise

        except Exception as e:
            self._logger.error("User registration failed", exc_info=e, extra={
                "username": registration_data.username
            })
            raise RegistrationError("Registration process failed") from e

    async def _validate_user_uniqueness(
        self,
        registration_data: UserRegistrationData
    ) -> None:
        """Validate that username and email are unique."""
        if await self._user_repo.exists_by_username(registration_data.username):
            raise DuplicateUserError(f"Username '{registration_data.username}' already exists")

        if await self._user_repo.exists_by_email(registration_data.email):
            raise DuplicateUserError(f"Email '{registration_data.email}' already exists")

# ❌ Bad: Code not ready for review
class UserStuff:
    def __init__(self, repo, email, events):  # No type hints
        self.repo = repo
        self.email = email
        self.events = events

    def register(self, data):  # No documentation, unclear parameters
        # No error handling
        user = self.repo.create(data)
        self.email.send(user.email, "welcome")
        self.events.publish("user_created", user)
        return user.id
```

## Quality Metrics and Monitoring

### Code Quality Metrics

```python
# Quality metrics configuration
QUALITY_THRESHOLDS = {
    'test_coverage': 90.0,          # Minimum test coverage percentage
    'type_coverage': 95.0,          # Minimum type annotation coverage
    'cyclomatic_complexity': 10,    # Maximum cyclomatic complexity
    'cognitive_complexity': 15,     # Maximum cognitive complexity
    'duplicate_code': 5.0,          # Maximum duplicate code percentage
    'maintainability_index': 70,    # Minimum maintainability index
    'technical_debt_ratio': 5.0,    # Maximum technical debt ratio
}

# Automated quality measurement
def measure_code_quality(project_path: Path) -> QualityReport:
    """Measure comprehensive code quality metrics."""
    return QualityReport(
        test_coverage=measure_test_coverage(project_path),
        type_coverage=measure_type_coverage(project_path),
        complexity=measure_complexity(project_path),
        duplication=measure_duplication(project_path),
        maintainability=measure_maintainability(project_path),
        security_issues=scan_security_issues(project_path),
        performance_issues=scan_performance_issues(project_path)
    )
```

### Quality Dashboard Integration

```python
# Quality reporting for dashboards
class QualityReporter:
    """Generate quality reports for monitoring dashboards."""

    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'project': 'flx-framework',
            'metrics': {
                'test_coverage': self._calculate_test_coverage(),
                'type_coverage': self._calculate_type_coverage(),
                'code_quality_score': self._calculate_quality_score(),
                'security_score': self._calculate_security_score(),
                'maintainability_score': self._calculate_maintainability_score()
            },
            'violations': {
                'critical': self._get_critical_violations(),
                'major': self._get_major_violations(),
                'minor': self._get_minor_violations()
            },
            'trends': {
                'coverage_trend': self._get_coverage_trend(),
                'quality_trend': self._get_quality_trend(),
                'velocity_trend': self._get_velocity_trend()
            }
        }
```

## Troubleshooting Code Quality Issues

### Common Quality Issues

#### MyPy Type Checking Problems

```python
# Problem: Generic type issues
class BadRepository:
    def save(self, entity):  # ❌ Missing type annotations
        pass

    def find_all(self):  # ❌ Missing return type
        return []

# Solution: Proper generic typing
from typing import TypeVar, Generic, List, Optional

T = TypeVar('T')

class Repository(Generic[T]):
    async def save(self, entity: T) -> None:
        """Save entity to storage."""
        pass

    async def find_all(self) -> List[T]:
        """Find all entities."""
        return []

    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        return None
```

#### Import Organization Issues

```python
# Problem: Disorganized imports
import os
from flx.core import Entity
import sys
from typing import List
from flx.adapters import DatabaseAdapter
import asyncio

# Solution: Organized imports (handled by ruff)
import asyncio
import os
import sys
from typing import List

from flx.adapters import DatabaseAdapter
from flx.core import Entity
```

#### Complexity Issues

```python
# Problem: High cyclomatic complexity
def process_user_data(user_data):  # ❌ Complexity > 10
    if user_data.get('active'):
        if user_data.get('verified'):
            if user_data.get('premium'):
                if user_data.get('region') == 'US':
                    # Complex nested logic
                    pass
                elif user_data.get('region') == 'EU':
                    # More complex logic
                    pass
                # ... more conditions
    # ... more nested conditions

# Solution: Decomposed functions
def process_user_data(user_data: UserData) -> ProcessingResult:
    """Process user data with decomposed logic."""
    if not user_data.is_active:
        return ProcessingResult.inactive_user()

    if not user_data.is_verified:
        return ProcessingResult.unverified_user()

    return _process_verified_user(user_data)

def _process_verified_user(user_data: UserData) -> ProcessingResult:
    """Process verified user based on subscription and region."""
    if user_data.is_premium:
        return _process_premium_user(user_data)

    return _process_standard_user(user_data)

def _process_premium_user(user_data: UserData) -> ProcessingResult:
    """Process premium user with region-specific logic."""
    processor = get_regional_processor(user_data.region)
    return processor.process_premium_user(user_data)
```

### Quality Tool Integration Issues

#### Pre-commit Hook Failures

```bash
# Problem: Pre-commit hooks failing
# Solution: Fix common issues

# 1. Fix formatting issues
black .

# 2. Fix linting issues
ruff --fix .

# 3. Fix type checking issues
mypy --show-error-codes src/

# 4. Update dependencies
pre-commit autoupdate

# 5. Run all hooks manually
pre-commit run --all-files
```

#### CI/CD Quality Gate Failures

```bash
# Problem: Quality gates failing in CI
# Solution: Local quality validation

# 1. Run complete quality check locally
make quality-check

# 2. Check coverage requirements
pytest --cov=flx --cov-fail-under=90

# 3. Validate security
bandit -r . -f json
safety check

# 4. Check for large files or sensitive data
git diff --name-only --diff-filter=A | xargs ls -la
```

## Best Practices Summary

### Development Workflow

1. **Pre-commit Hooks**: Always use pre-commit hooks for quality enforcement
2. **Regular Quality Checks**: Run quality tools frequently during development
3. **Code Reviews**: Thorough code reviews focusing on quality standards
4. **Automated Testing**: Comprehensive test coverage with quality gates
5. **Documentation**: Keep code self-documenting with clear intent

### Quality Standards

1. **Type Safety**: Complete type annotations for all public interfaces
2. **Error Handling**: Specific exception types and proper error propagation
3. **Code Organization**: Clear module structure and import organization
4. **Complexity Management**: Keep functions focused and complexity low
5. **Security Awareness**: Regular security scanning and vulnerability assessment

### Tool Integration

1. **IDE Integration**: Configure IDE with quality tools for immediate feedback
2. **CI/CD Pipeline**: Automated quality gates in build pipeline
3. **Quality Metrics**: Regular monitoring of quality metrics and trends
4. **Team Standards**: Consistent tool configuration across team members
5. **Continuous Improvement**: Regular review and update of quality standards

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Development Standards**](../standards/python-modernization-guide.md) - Python modernization standards and tooling setup required for effective code quality
- [**Development Hub**](../index.md) - Development ecosystem overview and tool integration for comprehensive development workflow
- [**Testing Foundation**](../testing/index.md) - Testing framework understanding essential for quality assurance and coverage requirements

### **➡️ Implementation Next Steps**

- [**Development Workflow**](./development-workflow.md) - Development process integration with quality gates and review cycles
- [**Testing Guidelines**](../testing/testing-comprehensive-guide.md) - Testing practices that support and validate code quality standards
- [**CLI Development Guide**](../tools/cli-development-guide.md) - Command-line tool development with quality integration

### **🔗 Related Implementation Topics**

- [**Pre-commit Hook Setup**](../tools/github-workflow-setup.md) - Git hook configuration and CI/CD pipeline integration for automated quality enforcement
- [**Security Standards**](../../security/architecture/security-architecture.md) - Security-focused code quality standards and vulnerability scanning integration
- [**Performance Optimization**](../../optimization/performance/optimization-guide.md) - Performance-aware code quality standards and profiling integration
- [**Documentation Standards**](../standards/documentation-standards.md) - Documentation quality standards that complement code quality requirements
- [**Architecture Validation**](../../architecture/design/unified-architecture-guide.md) - Architecture compliance checking and boundary validation in code quality processes
- [**API Reference Quality**](../../api-reference/core-api-reference.md) - API documentation standards and automated documentation quality checking

---

**📂 Content Document** | **🏠 Parent**: [Development Guides](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
