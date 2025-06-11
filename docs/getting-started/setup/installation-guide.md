# Installation Guide - Getting Started

> **Function**: Complete environment setup and dependency installation | **Audience**: New developers, system administrators | **Status**: Stable

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Complete installation instructions for FLX Framework and its ecosystem based on current project structure**

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

FLX Framework is distributed as part of the PyAuto monorepo, providing a complete hexagonal architecture implementation with Oracle integration capabilities. This guide covers installation from local development to production deployment.

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

For immediate setup of the complete FLX development environment:

**⚠️ Repository URL**: The actual repository location should be provided by your organization - this is a private monorepo.

```bash
# Clone the PyAuto monorepo (replace with actual repository URL)
git clone <REPOSITORY_URL> pyauto
cd pyauto

# Setup complete development environment
make setup

# Verify installation
python -c "import flx; print(f'FLX {flx.__version__} installed successfully')"
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
make test PROJECT=flx
```

**✅ Validated**: Commands verified against actual Makefile targets.

### Method 2: FLX Framework Only

**Best for**: Core framework development without Oracle adapters

```bash
# Clone and navigate to FLX
git clone https://github.com/datacosmos-br/pyauto.git
cd pyauto/flx

# Create dedicated virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Install in development mode with all extras
pip install -e ".[dev,test,docs]"
```

### Method 3: Poetry Alternative

**Best for**: Poetry-based workflows

```bash
cd pyauto/flx
poetry install --extras "dev test docs"
poetry shell
```

---

## Project Structure Understanding

The PyAuto workspace implements a monorepo structure with shared virtual environment:

```
pyauto/
├── .venv/                       # Shared virtual environment
├── flx/                         # Core FLX Framework
│   ├── src/flx/                # Framework source (core, ports, adapters)
│   ├── tests/                  # Comprehensive test suite
│   ├── pyproject.toml          # Framework dependencies
│   └── mypy.ini                # Type checking configuration
├── flx-database-oracle/        # Oracle Database adapter
├── flx-http-oracle-wms/        # Oracle WMS HTTP adapter
├── flx-http-oracle-oic/        # Oracle OIC HTTP adapter
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
make test PROJECT=flx            # Test specific project
make test-cov                    # Run tests with coverage
make lint                        # Run linting checks
make format                      # Format code with Black
make build PROJECT=flx           # Build project packages

# Dependency management
make sync-dependencies           # Sync versions across projects
make venv-install-dev            # Install development dependencies
```

### Type Checking Configuration

FLX Framework uses strict type checking with Python 3.13+ features:

```bash
# Run mypy on FLX framework
.venv/bin/python -m mypy flx/src/

# Configuration files:
# - flx/mypy.ini (standalone configuration)
# - flx/pyproject.toml (comprehensive project config)
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
cd flx-database-oracle
pip install -e .

# WMS HTTP adapter  
cd ../flx-http-oracle-wms
pip install -e .

# OIC HTTP adapter
cd ../flx-http-oracle-oic
pip install -e .
```

---

## Configuration Management

### Environment Configuration

```bash
# Copy example configuration
cp flx/config.example.yaml flx/config.yaml

# Edit configuration
vim flx/config.yaml
```

Example configuration structure:

```yaml
# flx/config.yaml
database:
  url: "postgresql://localhost/flx_dev"
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
# Core FLX settings
FLX_LOG_LEVEL=INFO
FLX_LOG_FORMAT=structured
FLX_DEBUG=false

# Cache configuration
FLX_CACHE_BACKEND=redis
FLX_CACHE_URL=redis://localhost:6379

# Database configuration
FLX_DATABASE_URL=postgresql://localhost/flx_dev

# Oracle integration
ORACLE_CLIENT_PATH=/opt/oracle/instantclient
ORACLE_TNS_ADMIN=/opt/oracle/network/admin
```

---

## Installation Verification

### Verification Script

Create and run this verification script:

```python
#!/usr/bin/env python3
"""FLX Installation Verification Script"""

def verify_installation():
    try:
        # Core framework imports
        import flx
        from flx.core import Entity, AggregateRoot, DomainEvent
        from flx.ports import ModernBasePort, CliPort
        from flx.adapters.inbound.cli import CliAdapter
        
        print(f"✅ FLX {flx.__version__} - Core framework installed")
        
        # Test entity system
        class TestEntity(Entity):
            name: str = "test"
        
        entity = TestEntity()
        print(f"✅ Entity system functional - ID: {entity.id}")
        
        # Test Oracle adapters (if available)
        try:
            import flx_database_oracle
            print("✅ Oracle Database adapter available")
        except ImportError:
            print("ℹ️  Oracle Database adapter not installed")
        
        try:
            import flx_http_oracle_wms
            print("✅ Oracle WMS adapter available")
        except ImportError:
            print("ℹ️  Oracle WMS adapter not installed")
        
        try:
            import flx_http_oracle_oic
            print("✅ Oracle OIC adapter available")
        except ImportError:
            print("ℹ️  Oracle OIC adapter not installed")
        
        print("\n🎉 FLX Framework successfully installed and verified!")
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
make test PROJECT=flx

# Test with coverage reporting
make test-cov PROJECT=flx

# Test specific functionality
make test k="test_entity"

# Test Oracle adapters (if installed)
make test PROJECT=flx-database-oracle
make test PROJECT=flx-http-oracle-wms
make test PROJECT=flx-http-oracle-oic
```

Expected output:

```
===== test session starts =====
platform linux -- Python 3.13.x
collected 150+ items

flx/tests/test_core/ ........... [ 25%]
flx/tests/test_ports/ .......... [ 50%]
flx/tests/test_adapters/ ....... [ 75%]
flx/tests/test_infra/ .......... [100%]

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
cd flx
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

- [Quickstart Guide](./quickstart.md) - Build your first FLX application
- [Framework Overview](./flx-framework-overview.md) - Core concepts and architecture

### **Related Topics**

- [Development Standards](../development/index.md) - Code quality and development workflow
- [Architecture Guide](../architecture/index.md) - Hexagonal architecture implementation
- [Oracle Integration](../guides/oracle/index.md) - Oracle adapter configuration and usage

---

**📂 Hub**: [Getting Started Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
