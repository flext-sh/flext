# FLX Framework Troubleshooting and Debugging Guide

> **Comprehensive troubleshooting strategies for FLX hexagonal architecture framework**

This guide provides comprehensive troubleshooting strategies for common issues in the FLX hexagonal architecture framework, debugging techniques, and solutions for typical problems encountered during development and deployment.

**Related Documentation**:

- **[Testing Strategies](TESTING_HEXAGONAL_ARCHITECTURE.md)** - Testing methodologies for troubleshooting
- **[Development Standards](standardization-plan.md)** - Code standards and conventions
- **[Infrastructure Architecture](../architecture/INFRASTRUCTURE_ARCHITECTURE.md)** - System architecture overview

## Table of Contents

1. [Common Issues and Quick Fixes](#common-issues-and-quick-fixes)
2. [Adapter Connection Problems](#adapter-connection-problems)
3. [Plugin System Issues](#plugin-system-issues)
4. [Configuration Problems](#configuration-problems)
5. [Database and Session Issues](#database-and-session-issues)
6. [Performance and Memory Issues](#performance-and-memory-issues)
7. [Debugging Techniques](#debugging-techniques)
8. [Logging and Monitoring](#logging-and-monitoring)
9. [Testing and Development Issues](#testing-and-development-issues)
10. [Production Deployment Issues](#production-deployment-issues)

## Common Issues and Quick Fixes

### Import Errors

**Problem**: `ModuleNotFoundError` or import-related errors

```bash
# Error examples
ModuleNotFoundError: No module named 'flx.core'
ImportError: cannot import name 'BaseAdapter' from 'flx.adapters'
ImportError: attempted relative import with no known parent package
```

**Diagnosis Steps**:

```bash
# 1. Verify installation
pip list | grep flx

# 2. Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# 3. Verify current working directory
pwd
ls -la

# 4. Check virtual environment
which python
pip show flx

# 5. Test specific import
python -c "import flx; print(flx.__file__)"

# 6. Check for __pycache__ conflicts
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

**Common Scenarios and Solutions**:

```bash
# Scenario 1: Development installation
cd /path/to/flx
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Scenario 2: Package conflicts
pip uninstall flx -y
pip cache purge
pip install -e ".[dev]"

# Scenario 3: PYTHONPATH issues
export PYTHONPATH="/path/to/flx/src:$PYTHONPATH"

# Scenario 4: IDE-specific issues (PyCharm, VSCode)
# Mark src/ as sources root in IDE settings
# Restart language server: Ctrl+Shift+P -> "Python: Restart Language Server"

# Scenario 5: Relative import errors in tests
# Run tests from project root:
python -m pytest tests/
# Not: cd tests && python -m pytest

# Scenario 6: Missing __init__.py files
find src/ -type d -name "flx" -exec touch {}/__init__.py \;
find src/ -type d -path "*/flx/*" -exec touch {}/__init__.py \;
```

**Environment Validation Script**:

```python
#!/usr/bin/env python3
"""Validate FLX development environment setup."""

import sys
import subprocess
from pathlib import Path

def check_environment():
    issues = []

    # Check Python version
    if sys.version_info < (3, 13):
        issues.append(f"Python 3.13+ required, found {sys.version}")

    # Check virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        issues.append("Not in a virtual environment")

    # Check FLX installation
    try:
        import flx
        print(f"✓ FLX installed at: {flx.__file__}")
    except ImportError as e:
        issues.append(f"FLX not importable: {e}")

    # Check development dependencies
    dev_deps = ['pytest', 'mypy', 'black', 'ruff']
    for dep in dev_deps:
        try:
            __import__(dep)
            print(f"✓ {dep} available")
        except ImportError:
            issues.append(f"Missing development dependency: {dep}")

    # Check project structure
    expected_dirs = ['src/flx', 'tests', 'docs']
    for dir_path in expected_dirs:
        if not Path(dir_path).exists():
            issues.append(f"Missing directory: {dir_path}")

    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ Environment is properly configured")
        return True

if __name__ == "__main__":
    sys.exit(0 if check_environment() else 1)
```

### Configuration Loading Issues

**Problem**: Configuration not loading or invalid values

```python
# Error examples
ConfigurationError: Required configuration key 'database.url' not found
ValueError: Invalid configuration format
FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'
yaml.scanner.ScannerError: while parsing a block mapping
PermissionError: [Errno 13] Permission denied: 'config/production.yaml'
```

**Comprehensive Diagnosis**:

```python
#!/usr/bin/env python3
"""Configuration troubleshooting script for FLX framework."""

import os
import yaml
from pathlib import Path
from flx.infra.config.adapter import ConfigAdapter
from flx.infra.config.hierarchical import ConfigManager

def diagnose_config_issues():
    """Run comprehensive configuration diagnostics."""

    print("🔍 FLX Configuration Diagnostics")
    print("=" * 50)

    # 1. Check environment variables
    print("\n1. Environment Variables:")
    flx_vars = {k: v for k, v in os.environ.items() if k.startswith('FLX_')}
    if flx_vars:
        for key, value in flx_vars.items():
            # Mask potentially sensitive values
            masked_value = value if 'password' not in key.lower() and 'secret' not in key.lower() else '*' * len(value)
            print(f"   {key} = {masked_value}")
    else:
        print("   No FLX_* environment variables found")

    # 2. Check configuration files
    print("\n2. Configuration Files:")
    config_patterns = [
        "config.yaml", "config.yml",
        "config/base.yaml", "config/development.yaml", "config/production.yaml",
        ".flx.yaml", "flx.config.yaml"
    ]

    found_configs = []
    for pattern in config_patterns:
        path = Path(pattern)
        if path.exists():
            found_configs.append(path)
            print(f"   ✓ Found: {path} ({path.stat().st_size} bytes)")

            # Check permissions
            if not os.access(path, os.R_OK):
                print(f"   ❌ Permission denied: {path}")

            # Validate YAML syntax
            try:
                with open(path, 'r') as f:
                    yaml.safe_load(f)
                print(f"   ✓ Valid YAML: {path}")
            except yaml.YAMLError as e:
                print(f"   ❌ Invalid YAML: {path} - {e}")
            except Exception as e:
                print(f"   ❌ Read error: {path} - {e}")
        else:
            print(f"   - Not found: {pattern}")

    # 3. Test configuration loading
    print("\n3. Configuration Loading Test:")
    try:
        config_manager = ConfigManager()
        print(f"   ✓ ConfigManager created")
        print(f"   Profile: {config_manager.profile}")
        print(f"   Config path: {config_manager.config_path}")

        config_adapter = ConfigAdapter(config_manager=config_manager)
        print(f"   ✓ ConfigAdapter created")

        # Test basic operations
        all_config = config_adapter.get_all()
        print(f"   ✓ Configuration loaded: {len(all_config)} sections")

        for section in all_config.keys():
            print(f"   - Section: {section}")

    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()

    # 4. Specific value checks
    print("\n4. Common Configuration Checks:")
    common_keys = [
        "database.url", "database.pool_size",
        "logging.level", "logging.format",
        "server.host", "server.port",
        "cache.type", "cache.url"
    ]

    try:
        config = ConfigAdapter()
        for key in common_keys:
            value = config.get(key)
            if value is not None:
                print(f"   ✓ {key} = {value}")
            else:
                print(f"   - {key} = <not set>")
    except Exception as e:
        print(f"   ❌ Cannot check configuration values: {e}")

if __name__ == "__main__":
    diagnose_config_issues()
```

**Environment Variable Naming Conventions**:

```bash
# Correct environment variable patterns
export FLX_DATABASE__URL="postgresql://localhost/db"        # database.url
export FLX_DATABASE__POOL_SIZE="10"                        # database.pool_size
export FLX_LOGGING__LEVEL="INFO"                           # logging.level
export FLX_CACHE__REDIS__HOST="localhost"                  # cache.redis.host
export FLX_FEATURE_FLAGS__NEW_UI="true"                    # feature_flags.new_ui

# Incorrect patterns (won't work)
export FLX_DATABASE_URL="postgresql://localhost/db"        # Missing double underscore
export FLX_database__url="postgresql://localhost/db"       # Wrong case
export DATABASE_URL="postgresql://localhost/db"            # Missing FLX_ prefix
```

## Adapter Connection Problems

### Database Connection Failures

**Symptoms**:

```python
ConnectionError: Failed to connect to database
sqlalchemy.exc.OperationalError: Connection timeout
asyncpg.exceptions.InvalidPasswordError: Invalid credentials
```

**Debugging Steps**:

```python
# Test basic connectivity
import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

async def test_db_connection():
    try:
        engine = create_async_engine("postgresql://user:pass@localhost/db")
        async with engine.begin() as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            print("Database connection successful:", result.scalar())
    except Exception as e:
        print(f"Connection failed: {e}")

asyncio.run(test_db_connection())
```

**Common Solutions**:

```python
# 1. Check connection string format
# ✅ Correct
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/dbname"

# ❌ Incorrect - missing async driver
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"

# 2. Test with different timeout settings
engine = create_async_engine(
    DATABASE_URL,
    pool_timeout=30,
    pool_recycle=3600,
    echo=True  # Enable SQL logging
)
```

## Cross-References

### Related Documentation

- **[Testing Strategies](TESTING_HEXAGONAL_ARCHITECTURE.md)** - Testing methodologies and patterns
- **[Development Standards](standardization-plan.md)** - Code standards and tool configuration
- **[Infrastructure Architecture](../architecture/INFRASTRUCTURE_ARCHITECTURE.md)** - System architecture overview
- **[Scripts Organization](scripts-organization-guide.md)** - Script management patterns

### Integration Points

- **Development Environment**: Setup validation and environment checks
- **Testing Framework**: Mock configuration and test environment setup
- **Production Deployment**: Health monitoring and deployment validation
- **Debugging Tools**: Interactive debugging and logging configuration

---

_This troubleshooting guide provides comprehensive coverage of common issues and debugging strategies for the FLX hexagonal architecture framework. Use it as a reference when encountering problems during development, testing, or production deployment._
