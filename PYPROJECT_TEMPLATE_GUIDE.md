# PyProject Template Guide - Enterprise Standards

## Overview

This template provides **ZERO TOLERANCE** enterprise-grade Python project configuration for all 21 PyAuto workspace projects. It enforces strict PEP8 compliance, comprehensive testing, and hexagonal architecture support.

## Template Application Process

### Step 1: Copy Template

```bash
cp pyproject-template.toml <project-dir>/pyproject.toml
```

### Step 2: Required Replacements

Replace these placeholders in the copied file:

- `PROJECT_NAME` → Actual project name (e.g., "flx-oracle-oic")
- `PROJECT_MODULE` → Python module name (e.g., "flx_oracle_oic")

### Step 3: Project-Specific Dependencies

Add project-specific dependencies in the `[tool.poetry.dependencies]` section:

```toml
# Example for Oracle OIC project
cx-oracle = "^8.3.0"
singer-sdk = "^0.40.0"
requests = "^2.32.3"
```

### Step 4: CLI Entry Points (if applicable)

Configure CLI scripts in `[tool.poetry.scripts]`:

```toml
[tool.poetry.scripts]
tap-oracle-oic = "tap_oracle_oic.cli:main"
```

## Configuration Standards Explained

### Python Version Strategy

- **Target**: `>=3.9,<4.0` (workspace alignment)
- **Rationale**: Modern features, stable ecosystem, enterprise support

### Core Dependencies (Fixed Versions)

- **pydantic**: `^2.11.0` (Type safety, validation)
- **structlog**: For structured logging
- **typing-extensions**: Python 3.9 compatibility

### Code Quality (ZERO TOLERANCE)

- **black**: 88 character line length, PEP8 strict
- **ruff**: 50+ rule categories enabled
- **mypy**: Strict mode, minimal Any usage
- **bandit**: Security scanning
- **vulture**: Dead code detection

### Testing Requirements (90% MINIMUM)

- **pytest**: Comprehensive test runner
- **coverage**: Branch coverage required
- **hypothesis**: Property-based testing
- **pytest-xdist**: Parallel execution

## Tool Configuration Deep Dive

### Ruff Configuration

```toml
# 50+ rule categories for comprehensive code quality
select = ["F", "E", "W", "I", "N", "D", "UP", "ANN", ...]
```

**Key Rules Enforced**:

- Import sorting and organization
- Docstring requirements (Google style)
- Type annotations mandatory
- Security checks (bandit integration)
- Performance optimizations
- Modern Python idioms

### MyPy Strict Configuration

```toml
strict = true
disallow_any_unimported = true
disallow_any_decorated = true
warn_return_any = true
```

**Zero Tolerance For**:

- Untyped functions
- `Any` types (except necessary cases)
- Missing return type annotations
- Implicit optional parameters

### Pytest Configuration

```toml
addopts = [
    "--cov-fail-under=90",
    "--maxfail=1",
    "--strict-markers",
    "--no-cov-on-fail"
]
```

**Enterprise Requirements**:

- 90% coverage minimum (fails below)
- Parallel test execution
- Strict marker validation
- Comprehensive reporting

## Hexagonal Architecture Support

### Import Structure

```python
# Domain layer (core business logic)
from project.domain.entities import Entity
from project.domain.repositories import Repository

# Application layer (use cases)
from project.application.services import Service
from project.application.handlers import Handler

# Infrastructure layer (adapters)
from project.infrastructure.adapters import Adapter
from project.infrastructure.repositories import ConcreteRepository
```

### Dependency Injection Ready

- Type annotations enforced
- Interface segregation supported
- Dependency inversion compliant

## Quality Gates (ALL MUST PASS)

### Pre-commit Checks

```bash
# Code formatting
black --check src/
ruff check src/

# Type checking
mypy src/

# Security scanning
bandit -r src/

# Dead code detection
vulture src/

# Test execution
pytest --cov-fail-under=90
```

### CI/CD Integration

Template supports automated quality gates:

- Commit hooks via pre-commit
- Version bumping via commitizen
- Documentation generation via mkdocs

## Risk-Averse Dependency Management

### Version Pinning Strategy

- **Core deps**: Caret requirements (^) for stability
- **Dev deps**: Caret requirements for latest features
- **Security deps**: Fixed for known vulnerabilities

### Dependency Categories

1. **Production**: Minimal, stable, well-tested
2. **Development**: Comprehensive tooling
3. **Type stubs**: Complete type coverage

## Common Customizations by Project Type

### Singer Tap Projects

```toml
[tool.poetry.dependencies]
singer-sdk = "^0.40.0"
requests = "^2.32.3"

[tool.poetry.scripts]
tap-project = "tap_project.cli:main"
```

### API Integration Projects

```toml
[tool.poetry.dependencies]
httpx = "^0.28.1"
pydantic = "^2.11.0"
structlog = "^24.4.0"
```

### Database Projects

```toml
[tool.poetry.dependencies]
sqlalchemy = "^2.0.36"
alembic = "^1.14.0"
cx-oracle = "^8.3.0"  # For Oracle projects
```

## Validation Commands

After applying template, run validation:

```bash
# Dependency validation
poetry check

# Import validation
python -c "import src.PROJECT_MODULE"

# Quality gates
make lint
make type-check
make test
```

## Template Maintenance

### Update Frequency

- **Monthly**: Dependency version updates
- **Quarterly**: Tool configuration refinements
- **Annually**: Python version strategy review

### Change Management

1. Test template changes on sample project
2. Validate against all 21 projects
3. Document breaking changes
4. Coordinate rollout across workspace

## Enforcement Mechanisms

### Automated Validation

- Pre-commit hooks prevent non-compliant commits
- CI/CD pipelines fail on quality gate violations
- Dependency scanning alerts on vulnerabilities

### Manual Review

- Code review checklists include template compliance
- Architecture reviews validate hexagonal patterns
- Security reviews validate bandit configurations

## Troubleshooting Common Issues

### Import Errors

- Verify `src/` directory structure
- Check `packages` configuration in pyproject.toml
- Validate module name consistency

### Coverage Failures

- Review `omit` patterns in coverage configuration
- Add appropriate `# pragma: no cover` comments
- Ensure test discovery patterns match file structure

### Type Checking Errors

- Add missing type stubs to dev dependencies
- Configure overrides for third-party modules
- Use `TYPE_CHECKING` imports for circular dependencies

## Success Metrics

### Code Quality

- 0 ruff violations
- 0 mypy errors
- 0 bandit high-severity issues
- 90%+ test coverage

### Developer Experience

- Fast local development cycle
- Clear error messages
- Consistent tooling across projects

### Enterprise Compliance

- Security scanning integrated
- Dependency vulnerability monitoring
- Standardized project structure

---

**CRITICAL REMINDER**: This template enforces enterprise standards with ZERO TOLERANCE for deviations. All 21 projects must comply with these configurations to maintain workspace integrity and quality standards.
