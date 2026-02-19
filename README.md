# FLEXT - Enterprise Data Integration Platform

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**FLEXT** is a comprehensive, enterprise-grade data integration platform built with Python 3.13+ and modern architectural patterns.

**Reviewed**: 2026-02-17 | **Version**: 0.10.0-dev

Part of the [FLEXT](https://github.com/flext-sh/flext) ecosystem.

## 🚀 Key Features

- **Unified API**: Single facade pattern across all libraries with `flext-core` integration.
- **Type Safety**: Full Pydantic v2 integration with comprehensive validation and strict type checking.
- **Enterprise Patterns**: Implements CQRS, Railway-oriented programming, and Dependency Injection.
- **Extensible Architecture**: Plugin system built on robust `flext-core` abstractions.
- **RFC Compliant**: Full RFC 2849/4512 LDIF processing capabilities with quirk handling.
- **Production Ready**: Comprehensive testing, monitoring, and structured logging.

## 📦 Ecosystem Overview

FLEXT is composed of specialized libraries designed to work together or independently.

| Library | Description |
| ------- | ----------- |
| **[flext-core](flext-core/)** | Core framework providing base patterns, dependency injection, and error handling. |
| **[flext-api](flext-api/)** | REST API framework with OpenAPI support and unified HTTP clients. |
| **[flext-auth](flext-auth/)** | Authentication and authorization services supporting multiple providers. |
| **[flext-ldif](flext-ldif/)** | High-performance, RFC-compliant LDIF processing and migration engine. |
| **[flext-ldap](flext-ldap/)** | Universal LDAP client operations and directory management. |
| **[flext-oracle](flext-db-oracle/)** | Enterprise Oracle database integration with SQLAlchemy 2.0. |
| **[flext-grpc](flext-grpc/)** | gRPC services framework for high-performance microservices. |
| **[flext-meltano](flext-meltano/)** | Meltano integration for ELT pipelines and Singer taps/targets. |
| **[flext-web](flext-web/)** | Web application patterns and dashboarding components. |

## 🏗️ Architecture

FLEXT is built on a clean architecture foundation:

- **Clean Architecture**: Clear separation of concerns with dependency inversion.
- **CQRS Pattern**: Command Query Responsibility Segregation for complex business logic.
- **Railway-Oriented Programming**: Functional error handling returning `FlextResult[T]`.
- **Dependency Injection**: `FlextContainer` for managing component lifecycles.

```
┌─────────────────────────────────────┐
│         Application Layer           │
│   - Use Cases & Application Services│
│   - Command/Query Handlers          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│           Domain Layer              │
│   - Business Logic & Rules          │
│   - Domain Models & Value Objects   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│     Infrastructure Layer            │
│   - External Services (DB, LDAP)    │
│   - File System, Network I/O        │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│           Core Layer                │
│   - flext-core Framework            │
│   - Common Patterns & Abstractions  │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

## Installation

Install the core framework:

```bash
pip install flext-core
```

Install specific capabilities as needed:

```bash
pip install flext-ldif flext-api flext-auth
```

## Usage

### Basic Usage: LDIF Processing

```python
from flext_ldif import FlextLdif

# Initialize LDIF API
ldif = FlextLdif()

# Parse LDIF content
ldif_content = """dn: cn=test,dc=example,dc=com
cn: test
sn: user
objectClass: inetOrgPerson"""

result = ldif.parse(ldif_content)
if result.is_success:
    entries = result.unwrap()
    print(f"Successfully parsed {len(entries)} LDIF entries")
```

### Railway-Oriented Error Handling

FLEXT uses `FlextResult` for consistent error handling across the ecosystem.

```python
from flext_core import FlextResult

def process_data(data: str) -> FlextResult[str]:
    if not data:
        return FlextResult.failure("Data cannot be empty")
    
    # Process data...
    return FlextResult.success("processed data")

# Usage
result = process_data("input")
if result.is_success:
    print(result.unwrap())
else:
    print(f"Error: {result.error}")
```

## 🛠️ Development

All development and maintenance run via Make from the repository root. No ad-hoc script invocations as the primary workflow.

### Prerequisites

- Python 3.13+
- Poetry (for dependency management)
- Git

### Workflow (Make)

```bash
# Clone with submodules
git clone --recursive https://github.com/flext-sh/flext.git
cd flext

# Setup: single workspace .venv, all projects (optional: PROJECT= or PROJECTS=)
make setup

# Upgrade deps + dependency report (use DEPS_REPORT=0 to skip report)
make upgrade

# Quality gates
make check
make test
make validate

# Typings: stub supply-chain + typing report (optional: PROJECT=, DEPS_REPORT=0)
make typings
```

Run **make help** for all verbs and parameters (e.g. `PROJECT=flext-core`, `FAIL_FAST=1`, `FIX=1`). See [CLAUDE.md](CLAUDE.md) for the full automation contract and standard places.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details on the development workflow, coding standards, and submission process.

## 📄 License

FLEXT is released under the MIT License. See [LICENSE](LICENSE) for details.
