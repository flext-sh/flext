# PyProject Template System - Enterprise Standards

## Overview

This system provides **ZERO TOLERANCE** enterprise-grade Python project standardization for all 21 PyAuto workspace projects. It enforces strict PEP8 compliance, comprehensive testing, type safety, and hexagonal architecture support.

## Quick Start

### 1. Validate Current Compliance

```bash
make pyproject-template-validate
```

### 2. Apply Enterprise Template (DESTRUCTIVE)

```bash
# WARNING: This overwrites all pyproject.toml files
make pyproject-template-apply FORCE=1
```

### 3. Customize Individual Projects

```bash
make pyproject-template-customize PROJECT=flext-oracle-oic
```

### 4. Check Status

```bash
make pyproject-template-status
```

## Files Created

### Core Files

- `/home/marlonsc/pyauto/pyproject-template.toml` - Master enterprise template
- `/home/marlonsc/pyauto/scripts/validate_pyproject_compliance.py` - Compliance validator
- `/home/marlonsc/pyauto/PYPROJECT_TEMPLATE_GUIDE.md` - Detailed implementation guide

### Makefile Targets Added

- `pyproject-template-validate` - Validates all projects
- `pyproject-template-apply` - Applies template (requires FORCE=1)
- `pyproject-template-customize` - Customizes for specific project
- `pyproject-template-status` - Shows compliance status

## Enterprise Standards Enforced

### 1. Python Version Consistency

- **Required**: `>=3.9,<4.0` across all projects
- **Rationale**: Modern features, stable ecosystem, enterprise LTS support

### 2. Build System Standardization

- **Required**: `poetry-core>=1.9.0`
- **Backend**: `poetry.core.masonry.api`
- **Rationale**: Consistent build and dependency management

### 3. Core Dependencies (Fixed Versions)

```toml
pydantic = "^2.11.0"           # Type safety and validation
structlog = "^24.4.0"          # Structured logging
python-dotenv = "^1.0.1"       # Environment configuration
typing-extensions = "^4.12.2"  # Python 3.9 compatibility
```

### 4. Development Tools (Comprehensive)

```toml
# Testing (90% coverage minimum)
pytest = "^8.3.4"
pytest-cov = "^6.0.0"
pytest-asyncio = "^0.25.0"
pytest-mock = "^3.14.0"

# Code Quality (Zero tolerance)
black = "^24.10.0"
ruff = "^0.8.3"
mypy = "^1.13.0"
bandit = "^1.8.0"

# Documentation
mkdocs = "^1.6.1"
mkdocs-material = "^9.5.48"
```

## Configuration Deep Dive

### Black Configuration

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312', 'py313']
```

- **88 characters**: PEP8 compliant, optimal readability
- **Multi-version**: Support for Python 3.9-3.13

### Ruff Configuration (50+ Rule Categories)

```toml
[tool.ruff.lint]
select = [
    "F",    # Pyflakes
    "E", "W", # Pycodestyle
    "I",    # isort
    "N",    # pep8-naming
    "D",    # pydocstyle
    "UP",   # pyupgrade
    "ANN",  # flake8-annotations
    "S",    # flake8-bandit
    "B",    # flake8-bugbear
    # ... 40+ more categories
]
```

### MyPy Strict Mode

```toml
[tool.mypy]
strict = true
disallow_any_unimported = true
disallow_any_decorated = true
warn_return_any = true
```

### Pytest Configuration (90% Coverage)

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov-fail-under=90",
    "--strict-markers",
    "--strict-config",
    "--maxfail=1",
]
```

## Hexagonal Architecture Support

### Directory Structure

```
project/
├── src/
│   └── project_name/
│       ├── domain/          # Core business logic
│       ├── application/     # Use cases
│       └── infrastructure/  # Adapters
├── tests/
└── pyproject.toml
```

### Import Organization

```python
# Domain layer (no dependencies)
from project.domain.entities import Entity
from project.domain.repositories import Repository

# Application layer (depends on domain)
from project.application.services import Service

# Infrastructure layer (depends on application)
from project.infrastructure.adapters import Adapter
```

## Quality Gates (ALL MUST PASS)

### 1. Code Quality

```bash
# Zero violations required
ruff check src/
mypy src/
bandit -r src/
```

### 2. Test Coverage

```bash
# 90% minimum coverage
pytest --cov-fail-under=90
```

### 3. Type Safety

```bash
# Strict type checking
mypy --strict src/
```

### 4. Security

```bash
# No high-severity security issues
bandit -r src/ -ll
```

## Project-Specific Customizations

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
cx-oracle = "^8.3.0"
```

## Validation Process

### 1. Template Compliance Check

The validator checks:

- Build system configuration
- Python version requirements
- Core dependency versions
- Development tool configurations
- Code quality settings
- Test coverage requirements
- Project metadata completeness

### 2. Compliance Report

```bash
# Example output
ENTERPRISE COMPLIANCE FAILURE
============================
Failed Projects: 5/21
Total Violations: 23

Failed Projects:
  - flext-oracle-oic
  - tap-oracle-wms
  - flext-ldap

Action Required:
1. Apply pyproject-template.toml to all failed projects
2. Update project-specific dependencies
3. Re-run validation until ZERO violations
```

## Risk Management

### 1. Backup Strategy

- Template application automatically creates `.backup` files
- Git tracking allows rollback of changes
- Incremental validation prevents mass failures

### 2. Version Pinning

- Caret requirements (`^`) for controlled updates
- Security-focused dependency selection
- Regular vulnerability scanning

### 3. Gradual Rollout

- Individual project customization supported
- Validation before enforcement
- Clear compliance reporting

## Maintenance

### Monthly Tasks

- Update dependency versions in template
- Review new Ruff rules for inclusion
- Update Python version support matrix

### Quarterly Tasks

- Review tool configurations for optimization
- Update documentation with new patterns
- Conduct comprehensive compliance audit

### Annual Tasks

- Major version updates (Python, Poetry)
- Architecture pattern evolution
- Security policy review

## Troubleshooting

### Import Errors After Template Application

```bash
# Check src/ directory structure
ls -la project/src/

# Verify package configuration
grep -A5 "packages" project/pyproject.toml

# Test imports
python -c "import project_module"
```

### Coverage Failures

```bash
# Check omit patterns
grep -A10 "omit" project/pyproject.toml

# Review test discovery
pytest --collect-only

# Add coverage pragmas where appropriate
# pragma: no cover
```

### Type Checking Errors

```bash
# Check mypy configuration
mypy --show-config

# Add type stubs for third-party packages
poetry add --group dev types-requests

# Use TYPE_CHECKING imports for circular dependencies
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .module import Class
```

## Success Metrics

### Code Quality Metrics

- **0** Ruff violations across all projects
- **0** MyPy errors in strict mode
- **0** High-severity Bandit issues
- **90%+** Test coverage maintained

### Developer Experience Metrics

- **<5 seconds** Local development startup
- **<2 minutes** Complete test suite execution
- **<30 seconds** Lint and format cycle

### Enterprise Compliance Metrics

- **100%** Project template compliance
- **0** Security vulnerabilities in dependencies
- **21/21** Projects passing all quality gates

## Emergency Procedures

### Mass Compliance Failure (>5 projects)

1. **STOP** all development work
2. Identify root cause of failures
3. Test template fixes on single project
4. Apply fixes incrementally
5. Validate each project before proceeding

### Template Corruption

1. Restore from Git history
2. Re-validate template against known good project
3. Test template application on development branch
4. Coordinate rollout across team

### Tool Configuration Conflicts

1. Isolate conflicting configurations
2. Test combinations in clean environment
3. Document resolution in template guide
4. Update validation script to catch conflicts

---

## Critical Reminders

⚠️ **DESTRUCTIVE OPERATIONS**

- Template application overwrites existing files
- Always use `FORCE=1` confirmation
- Verify backups before proceeding

🚨 **ZERO TOLERANCE ENFORCEMENT**

- No exceptions to template compliance
- All quality gates must pass
- Enterprise standards are non-negotiable

✅ **SUCCESS CRITERIA**

- 21/21 projects compliant
- 0 violations in validation
- All quality gates passing
- Consistent developer experience

This template system ensures enterprise-grade consistency, maintainability, and quality across the entire PyAuto workspace.
