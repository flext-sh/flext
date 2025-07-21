# CLAUDE.PYTEST-STANDARDIZATION.md

This file documents the systematic pytest standardization methodology being applied across all FLEXT projects to ensure future Claude Code sessions can continue and maintain this work.

## Current Status

**Target**: Complete pytest standardization across 33+ FLEXT projects following professional best practices
**Progress**: 70% complete - Core projects standardized, remaining projects in progress
**Critical Rule**: 100% functionality - NO fallbacks, NO mocks in production, NO silencing failures

## Systematic Methodology

### Phase 1: Investigation and Analysis ✅ COMPLETED

1. **Project Structure Analysis**

   ```bash
   find . -name "tests" -type d | wc -l    # Count test directories
   find . -name "conftest.py" | head -10   # Analyze existing configurations
   find . -name "test_*.py" | wc -l        # Count test files
   ```

2. **Pattern Recognition**
   - Standard test structures: `tests/{unit,integration,e2e,fixtures}/`
   - Common conftest.py patterns across projects
   - Existing pytest markers and fixtures

### Phase 2: Core Infrastructure ✅ COMPLETED

1. **Workspace-Level Configuration**
   - `/home/marlonsc/flext/tests/conftest.py` - Master configuration
   - Standardized pytest markers: unit, integration, e2e, smoke, slow
   - DI container fixtures for consistent testing

2. **Project-Level Templates**
   - Created standardized conftest.py templates for different project types
   - Established consistent directory structure
   - Implemented proper test isolation patterns

### Phase 3: Project-by-Project Standardization 🔄 IN PROGRESS

#### ✅ COMPLETED PROJECTS

- **flext-core**: Complete standardization, all linting fixed
- **flext-api**: Complete standardization, all linting fixed  
- **flext-auth**: Complete standardization, all linting fixed
- **flext-grpc**: Complete standardization, all linting fixed
- **flext-web**: Complete standardization, all linting fixed
- **flext-cli**: Complete standardization, all linting fixed

#### 🔄 CURRENTLY WORKING ON

- **flext-plugin**: 90% complete - final linting issues being resolved

#### ⏳ REMAINING PROJECTS

- flext-observability
- flext-meltano  
- flext-oracle-wms
- flext-tap-oracle
- flext-dbt-oracle
- All Singer/Meltano projects
- Legacy projects

## Critical Quality Standards Applied

### ZERO TOLERANCE VIOLATIONS

Based on extensive work across projects, these patterns are absolutely forbidden:

1. **Logging Anti-patterns**:

   ```python
   # ❌ FORBIDDEN - Found in multiple projects
   logger.error("Error: %s", e, exc_info=True)
   
   # ✅ REQUIRED - Systematic fix applied
   logger.exception("Error: %s", e)
   ```

2. **Async Sleep Loops**:

   ```python
   # ❌ FORBIDDEN (ASYNC110) - Found in flext-plugin
   while self._is_running:
       await asyncio.sleep(1)
   
   # ✅ REQUIRED - Fixed with event-based approach
   stop_event = asyncio.Event()
   await asyncio.wait_for(stop_event.wait(), timeout=1.0)
   ```

3. **Mock/Fake Code in Production**:

   ```python
   # ❌ FORBIDDEN - Removed from flext-api, flext-auth
   def fallback_service():
       return {"mock": "data"}
   
   # ✅ REQUIRED - Use real implementations
   from actual_service import get_real_data
   ```

4. **Missing Type Annotations**:

   ```python
   # ❌ FORBIDDEN - Systematic fix across all projects
   @pytest.fixture
   def mock_service():
   
   # ✅ REQUIRED - All fixtures must be typed
   @pytest.fixture
   def mock_service() -> MockServiceType:
   ```

5. **Code Duplication**:

   ```python
   # ❌ FORBIDDEN - Found LDAP client duplication
   # flext-tap-ldap AND flext-ldap both had LDAP clients
   
   # ✅ REQUIRED - Eliminated duplication
   # Unified LDAP client in flext-ldap, others import it
   ```

## Standardized Project Structure

### Required Directory Structure

```
project-name/
├── src/project_name/          # Source code
├── tests/                     # Tests ONLY here
│   ├── unit/                  # Fast, isolated tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   ├── fixtures/              # Test data and fixtures
│   └── conftest.py           # Pytest configuration
├── pyproject.toml            # Poetry + tool configuration
├── Makefile                  # Standardized commands
└── README.md                 # Project documentation
```

### Required conftest.py Template

```python
"""Test configuration for [PROJECT_NAME]."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Generator
from pathlib import Path

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None, None, None]:
    """Set test environment variables."""
    original_env = os.environ.get("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "test"
    
    yield
    
    if original_env is not None:
        os.environ["ENVIRONMENT"] = original_env
    else:
        os.environ.pop("ENVIRONMENT", None)

# Project-specific fixtures based on type:
# - API projects: FastAPI test client
# - Database projects: Test database fixtures  
# - LDAP projects: Mock LDAP connection
# - Plugin projects: Plugin manager fixtures
```

## Systematic Linting Fix Process

### 1. Run Quality Checks

```bash
cd /home/marlonsc/flext/[project-name]
make lint                    # Identify all violations
make type-check             # Find type issues
make test                   # Ensure tests pass
```

### 2. Fix Categories Systematically

#### A. Import and Type Issues

- Add missing type annotations
- Fix import ordering
- Add `from __future__ import annotations`
- Proper TYPE_CHECKING imports

#### B. Logging Issues

- Replace `logger.error(..., exc_info=True)` with `logger.exception(...)`
- Ensure all exception variables are in scope

#### C. Async Issues  

- Replace sleep loops with event-based patterns
- Fix async/await usage

#### D. Security Issues

- Replace hardcoded `/tmp/` paths with pathlib
- Fix insecure temporary file usage

#### E. Code Quality

- Add ClassVar annotations for mutable class attributes
- Fix missing docstrings in public packages
- Remove unused imports

### 3. Verify Fixes

```bash
make check                  # Must pass with ZERO violations
make test                   # All tests must pass
```

## Project-Specific Patterns

### API Projects (flext-api, flext-grpc)

```python
# conftest.py additions
@pytest.fixture
def api_client() -> TestClient:
    """Create FastAPI test client."""
    return TestClient(app)

@pytest.fixture  
def auth_headers() -> dict[str, str]:
    """Create authentication headers."""
    return {"Authorization": "Bearer test-token"}
```

### Database Projects (flext-oracle-wms, flext-dbt-oracle)

```python
# conftest.py additions
@pytest.fixture
def test_db_config() -> dict[str, Any]:
    """Test database configuration."""
    return {
        "host": "localhost",
        "port": 5432,
        "database": "test_db"
    }
```

### LDAP Projects (flext-tap-ldap, flext-ldap)

```python
# conftest.py additions
@pytest.fixture
def mock_ldap_connection() -> MockLDAPConnection:
    """Mock LDAP connection for testing."""
    return MockLDAPConnection(test_data=LDAP_TEST_DATA)
```

### Plugin Projects (flext-plugin)

```python
# conftest.py additions
@pytest.fixture
def plugin_manager() -> PluginManager:
    """Plugin manager for testing."""
    return PluginManager(config=test_config)
```

## Critical Success Factors

### ✅ MANDATORY REQUIREMENTS

1. **100% Functionality**: Everything must work without warnings
2. **No Fallbacks**: Always use original libraries, never create alternatives
3. **No Mocks in Production**: Remove all mock/fake implementations from src/
4. **No Silencing Failures**: Fix the root cause, don't suppress errors
5. **Complete Testing**: All tests must pass, no skips allowed

### ⚠️ RED FLAGS TO WATCH FOR

1. **ImportError with fallbacks**: Often legitimate optional dependencies
2. **Mock classes in src/**: These must be removed or moved to tests/
3. **print() statements in tests**: Replace with proper assertions
4. **Hardcoded paths**: Use pathlib.Path consistently
5. **Missing type annotations**: Add them systematically

## Continuation Protocol for Future Sessions

### When Resuming This Work

1. **Check Current Status**:

   ```bash
   cd /home/marlonsc/flext
   find . -name "make" -exec {} lint \; 2>&1 | grep -E "error|failed" | wc -l
   ```

2. **Identify Next Project**:
   - Check TodoWrite tool for current task
   - Look at git status for projects with changes
   - Start with projects that have the most violations

3. **Apply Systematic Process**:
   - Read project structure first
   - Run `make lint` to identify issues
   - Fix category by category (imports → types → logging → async → security)
   - Verify with `make check`
   - Move to next project

4. **Update Progress**:
   - Mark completed projects in this file
   - Update TodoWrite with current status
   - Document any new patterns discovered

## Tools and Commands

### Quality Verification

```bash
# Individual project
make check                  # Must pass 100%
make lint                   # Zero violations
make type-check            # Zero type errors
make test                  # All tests pass

# Workspace-wide
cd /home/marlonsc/flext
for dir in flext-*/; do
    echo "=== $dir ==="
    cd "$dir" && make lint && cd ..
done
```

### Pattern Detection

```bash
# Find potential issues across projects
rg "logger\.error.*exc_info" --type py
rg "await asyncio\.sleep.*while" --type py  
rg "except.*as e:" -A 5 --type py | rg "f.*{e}"
```

## Key Lessons Learned

1. **Read Before Writing**: Always read files before modifying them
2. **Understand Context**: Check surrounding code for patterns
3. **Verify Tools Work**: Use Read/Bash tools to confirm changes
4. **No Assumptions**: If uncertain, investigate with tools
5. **Systematic Approach**: Fix categories of issues together
6. **Test Everything**: Run quality checks after each fix

## Success Metrics

- **Linting**: Zero violations across all projects
- **Type Checking**: 100% type coverage
- **Testing**: 85%+ coverage, all tests passing
- **Security**: Clean security scans
- **Documentation**: All public APIs documented

This methodology ensures consistent, professional pytest standards across the entire FLEXT platform while maintaining 100% functionality and eliminating technical debt.
