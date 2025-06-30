# Installation Guide - Getting Started

> **Function**: Complete environment setup and dependency installation | **Audience**: New developers, system REDACTED_LDAP_BIND_PASSWORDistrators | **Status**: Stable

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Complete installation instructions for FLEXT Framework and its ecosystem based on current project structure**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Getting Started](./index.md) → **📄 Current**: Installation Guide

### **📍 Learning Path Position**

```
[Start Here] → **[INSTALLATION GUIDE]** → [Quickstart](./quickstart.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Getting Started Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Next Step**: [Quickstart Guide](./quickstart.md)

---

## 📋 **Overview**

FLEXT Framework is distributed as part of the PyAuto monorepo, providing a complete hexagonal architecture implementation with Oracle integration capabilities. This guide covers installation from local development to production deployment.

## Prerequisites

### System Requirements

- **Python 3.13+** (Required for modern type features and performance)
- **Git** (For repository cloning and version control)
- **Make** (For build automation and workspace management)

### Optional Components

- **Docker** (For containerized development and deployment)
- **Redis** (For caching infrastructure and session management)
- **PostgreSQL** (For relational database integration)
- **Oracle Client** (For Oracle database and WMS/OIC adapters)

---

## Quick Installation

For immediate setup of the complete FLEXT development environment:

**⚠️ Repository URL**: The actual repository location should be provided by your organization - this is a private monorepo.

```bash
# Clone the PyAuto monorepo (replace with actual repository URL)
git clone <REPOSITORY_URL> pyauto
cd pyauto

# Setup complete development environment
make setup

# Verify installation
python -c "import flext; print(f'FLEXT {flext.__version__} installed successfully')"
```

**✅ Validated**: Installation commands verified against actual `/home/marlonsc/pyauto/Makefile` - `make setup` target exists and calls `venv-setup`.

---

## Detailed Installation Methods

### Method 1: Complete Workspace Setup (Recommended)

**Best for**: Full development environment with all Oracle adapters

```bash
# Clone the monorepo (replace with actual repository URL)
git clone <REPOSITORY_URL> pyauto
cd pyauto

# Setup shared virtual environment and all dependencies
make setup

# Verify installation with tests
make test PROJECT=flext
```

**✅ Validated**: Commands verified against actual Makefile targets.

### Method 2: FLEXT Framework Only

**Best for**: Core framework development without Oracle adapters

```bash
# Clone and navigate to FLEXT
git clone https://github.com/datacosmos-br/pyauto.git
cd pyauto/flext

# Create dedicated virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[dev,test,docs]"
```

### Method 3: Poetry Alternative

**Best for**: Poetry-based workflows

```bash
cd pyauto/flext
poetry install --extras "dev test docs"
poetry shell
```

---

## Project Structure Understanding

The PyAuto workspace implements a monorepo structure with shared virtual environment:

```
pyauto/
├── .venv/                       # Shared virtual environment
├── flext/                         # Core FLEXT Framework
│   ├── src/flext/                # Framework source (core, ports, adapters)
│   ├── tests/                  # Comprehensive test suite
│   ├── pyproject.toml          # Framework dependencies
│   └── mypy.ini                # Type checking configuration
├── flext_database_oracle/        # Oracle Database adapter
├── flext_http_oracle_wms/        # Oracle WMS HTTP adapter
├── flext_http_oracle_oic/        # Oracle OIC HTTP adapter
├── docs/                       # Documentation hub
├── examples/                   # Usage examples and patterns
├── scripts/                    # Shared utilities and tools
├── Makefile                    # Workspace automation
└── pyproject.toml              # Workspace configuration
```

---

## Development Environment Configuration

### Essential Workspace Commands

```bash
# Always activate virtual environment first
source .venv/bin/activate

# Core development workflow
make test                        # Run all tests
make test PROJECT=flext            # Test specific project
make test-cov                    # Run tests with coverage
make lint                        # Run linting checks
make format                      # Format code with Black
make build PROJECT=flext           # Build project packages

# Dependency management
make sync-dependencies           # Sync versions across projects
make venv-install-dev            # Install development dependencies
```

### Type Checking Configuration

FLEXT Framework uses strict type checking with Python 3.13+ features:

```bash
# Run mypy on FLEXT framework
.venv/bin/python -m mypy flext/src/

# Configuration files:
# - flext/mypy.ini (standalone configuration)
# - flext/pyproject.toml (comprehensive project config)
```

---

## Oracle Integration Setup

### Oracle Client Prerequisites

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install libaio1 libaio-dev
```

**macOS:**

```bash
brew install oracle-instantclient
```

**Windows:**
Download Oracle Instant Client from Oracle website and configure PATH.

### Oracle Adapter Installation

```bash
# Activate workspace environment
source .venv/bin/activate

# Database adapter
cd flext-database-oracle
pip install -e .

# WMS HTTP adapter
cd ../flext_http_oracle_wms
pip install -e .

# OIC HTTP adapter
cd ../flext_http_oracle_oic
pip install -e .
```

---

## Configuration Management

### Environment Configuration

```bash
# Copy example configuration
cp flext/config.example.yaml flext/config.yaml

# Edit configuration
vim flext/config.yaml
```

Example configuration structure:

```yaml
# flext/config.yaml
database:
  url: "postgresql://localhost/flext_dev"
  pool_size: 5

cache:
  redis_url: "redis://localhost:6379"
  ttl: 3600

logging:
  level: "INFO"
  format: "structured"

testing:
  use_test_engines: true
```

### Environment Variables

Create `.env` file in project root:

```bash
# Core FLEXT settings
FLX_LOG_LEVEL=INFO
FLX_LOG_FORMAT=structured
FLX_DEBUG=false

# Cache configuration
FLX_CACHE_BACKEND=redis
FLX_CACHE_URL=redis://localhost:6379

# Database configuration
FLX_DATABASE_URL=postgresql://localhost/flext_dev

# Oracle integration
ORACLE_CLIENT_PATH=/opt/oracle/instantclient
ORACLE_TNS_ADMIN=/opt/oracle/network/REDACTED_LDAP_BIND_PASSWORD
```

---

## Installation Verification

### Verification Script

Create and run this verification script:

```python
#!/usr/bin/env python3
"""FLEXT Installation Verification Script"""

def verify_installation():
    try:
        # Core framework imports
        import flext
        from flext.core import Entity, AggregateRoot, DomainEvent
        from flext.ports import ModernBasePort, CliPort
        from flext.adapters.inbound.cli import CliAdapter

        print(f"✅ FLEXT {flext.__version__} - Core framework installed")

        # Test entity system
        class TestEntity(Entity):
            name: str = "test"

        entity = TestEntity()
        print(f"✅ Entity system functional - ID: {entity.id}")

        # Test Oracle adapters (if available)
        try:
            import flext_database_oracle
            print("✅ Oracle Database adapter available")
        except ImportError:
            print("ℹ️  Oracle Database adapter not installed")

        try:
            import flext_http_oracle_wms
            print("✅ Oracle WMS adapter available")
        except ImportError:
            print("ℹ️  Oracle WMS adapter not installed")

        try:
            import flext_http_oracle_oic
            print("✅ Oracle OIC adapter available")
        except ImportError:
            print("ℹ️  Oracle OIC adapter not installed")

        print("\n🎉 FLEXT Framework successfully installed and verified!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    verify_installation()
```

### Test Suite Execution

```bash
# Test core framework
make test PROJECT=flext

# Test with coverage reporting
make test-cov PROJECT=flext

# Test specific functionality
make test k="test_entity"

# Test Oracle adapters (if installed)
make test PROJECT=flext-database-oracle
make test PROJECT=flext-http-oracle-wms
make test PROJECT=flext-http-oracle-oic
```

Expected output:

```
===== test session starts =====
platform linux -- Python 3.13.x
collected 150+ items

flext/tests/test_core/ ........... [ 25%]
flext/tests/test_ports/ .......... [ 50%]
flext/tests/test_adapters/ ....... [ 75%]
flext/tests/test_infra/ .......... [100%]

===== 150+ passed in 5.23s =====
```

---

## 🆘 **Troubleshooting**

### Python Version Issues

```bash
# Error: Python 3.13+ required
pyenv install 3.13.0
pyenv local 3.13.0
python --version  # Should show 3.13.x
```

### Virtual Environment Problems

```bash
# Recreate environment
rm -rf .venv
make setup
source .venv/bin/activate
```

### Import Errors

```bash
# Install in development mode
cd flext
pip install -e .
# Or use workspace setup
make venv-install-dev
```

### Oracle Client Issues

```bash
# Set environment variables
export ORACLE_HOME=/usr/lib/oracle/21/client64
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Documentation Root](../index.md) - Framework overview and architecture introduction

### **Next Steps**

- [Quickstart Guide](./quickstart.md) - Build your first FLEXT application
- [Framework Overview](./flext-framework-overview.md) - Core concepts and architecture

### **Related Topics**

- [Development Standards](../development/index.md) - Code quality and development workflow
- [Architecture Guide](../architecture/index.md) - Hexagonal architecture implementation
- [Oracle Integration](../guides/oracle/index.md) - Oracle adapter configuration and usage

---

**📂 Hub**: [Getting Started Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
