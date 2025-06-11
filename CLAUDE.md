# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Note**: This file has been migrated to the documentation structure.
> For current development guidelines, see [Development Standards](docs/development/standardization-plan.md)

## Project Overview

PyAuto is a Python automation workspace implementing enterprise-grade integrations with Oracle systems (WMS, Database, LDAP, OIC) using Hexagonal Architecture. The core framework is called FLX.

## High-Level Architecture

### Hexagonal Architecture Pattern
- **Inbound Ports**: CLI, HTTP API, gRPC interfaces
- **Outbound Ports**: Database, HTTP clients, file systems, message queues
- **Domain Layer**: Business logic isolated from infrastructure
- **Plugin System**: Bidirectional adapters that can act as inbound or outbound
- **Clear separation** between domain logic and infrastructure concerns

### Key Components
1. **FLX Framework** (`/flx/`) - Core hexagonal architecture implementation
2. **Oracle Adapters** (`/flx-*-oracle-*/`) - Specialized Oracle integration libraries
3. **Legacy Projects** (`/dc-oracle-*/`) - Older Oracle clients being migrated
4. **Implementation Projects** (`/projeto-*/`) - Real-world implementations

## Essential Commands

### Development Environment
```bash
# Always activate virtual environment first
source .venv/bin/activate

# Initial setup
make setup              # Complete dev environment setup
make venv-install-dev   # Install all dev dependencies
```

### Common Development Tasks
```bash
# Testing
make test                        # Run all tests
make test PROJECT=flx            # Test specific project
make test-cov                    # Run tests with coverage
make test k="test_name"          # Run specific test

# Code Quality
make lint                        # Run linting checks
make fix                         # Auto-fix code issues
make format                      # Format with Black

# Type Checking
.venv/bin/python -m mypy flx/src/  # Run mypy on flx

# Building
make build PROJECT=flx           # Build specific project
```

### Dependency Management
```bash
make sync-dependencies           # Sync versions across projects
make update                      # Update dependencies
make install-all PROJECT=flx     # Install all dependencies for a project
```

### Project Management
```bash
make list-projects               # List all projects
make status                      # Show workspace status
make clean                       # Clean build artifacts
```

## Project Structure

The workspace uses a monorepo structure with multiple related projects:
- Each project has its own `pyproject.toml`
- Dependencies are synchronized across projects
- Shared scripts in `/scripts/`
- Test files follow pattern: `test_*.py`

## Type Checking Configuration

Multiple mypy configurations exist:
- `flx/mypy.ini` - Standalone config with strict settings
- `flx/pyproject.toml` - Most comprehensive, uses Python 3.13
- `flx/setup.cfg` - Older config using Python 3.10

When fixing mypy issues, use the pyproject.toml settings as the reference.

## Testing Patterns

- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- End-to-end tests: `tests/e2e/`
- Always use pytest
- Coverage reports in `reports/coverage/`

## Important Notes

1. **Python Version**: 3.13+ required
2. **Virtual Environment**: Always use `.venv` in the workspace root
3. **Strict Typing**: Project uses strict mypy configuration
4. **Code Style**: Black formatting, Ruff linting
5. **Architecture**: Follow hexagonal architecture patterns
6. **Plugin Development**: Plugins can be bidirectional (inbound/outbound)