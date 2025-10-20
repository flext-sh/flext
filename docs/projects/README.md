# Project Documentation

## Table of Contents

- [Project Documentation](#project-documentation)
  - [Core Projects](#core-projects)
    - [🚀 [flext-core](./flext-core.md)](#-flext-coreflext-coremd)
    - [📄 [flext-ldif](./flext-ldif.md)](#-flext-ldifflext-ldifmd)
  - [Infrastructure Projects](#infrastructure-projects)
    - [🌐 [flext-api](./flext-api.md)](#-flext-apiflext-apimd)
    - [🔐 [flext-auth](./flext-auth.md)](#-flext-authflext-authmd)
    - [🗄️ [flext-ldap](./flext-ldap.md)](#-flext-ldapflext-ldapmd)
    - [🗃️ [flext-oracle](./flext-oracle.md)](#-flext-oracleflext-oraclemd)
    - [🔗 [flext-grpc](./flext-grpc.md)](#-flext-grpcflext-grpcmd)
  - [Domain Projects](#domain-projects)
    - [📦 [flext-meltano](./flext-meltano.md)](#-flext-meltanoflext-meltanomd)
    - [🔍 [flext-observability](./flext-observability.md)](#-flext-observabilityflext-observabilitymd)
    - [✨ [flext-quality](./flext-quality.md)](#-flext-qualityflext-qualitymd)
  - [Specialized Projects](#specialized-projects)
    - [🎯 [flext-plugin](./flext-plugin.md)](#-flext-pluginflext-pluginmd)
    - [🧪 [flext-tests](./flext-tests.md)](#-flext-testsflext-testsmd)
    - [🏭 [flext-cli](./flext-cli.md)](#-flext-cliflext-climd)
  - [Integration Guidelines](#integration-guidelines)
    - [Project Dependencies](#project-dependencies)
    - [Development Workflow](#development-workflow)
    - [Release Process](#release-process)
  - [Getting Started with Projects](#getting-started-with-projects)
    - [Using flext-core](#using-flext-core)
- [Set up dependency injection](#set-up-dependency-injection)
- [Use railway-oriented programming](#use-railway-oriented-programming)
  - [Using flext-ldif](#using-flext-ldif)
- [Parse LDIF content](#parse-ldif-content)
- [Migrate between servers](#migrate-between-servers)
  - [Project Standards](#project-standards)
  - [Contributing to Projects](#contributing-to-projects)

Detailed documentation for each FLEXT project and library.

## Core Projects

### 🚀 [flext-core](./flext-core.md)

The foundation framework providing core patterns, abstractions, and utilities for the entire FLEXT ecosystem.

**Key Features:**

- Dependency injection with FlextContainer
- CQRS pattern with FlextDispatcher
- Railway-oriented programming with FlextResult
- Domain event system with FlextBus
- Structured logging with FlextLogger

### 📄 [flext-ldif](./flext-ldif.md)

RFC-compliant LDIF processing library with enterprise-grade patterns and server-specific quirks handling.

**Key Features:**

- Unified FlextLdif facade
- RFC 2849/4512 compliant parsing and writing
- Server-specific quirks system (OID, OUD, OpenLDAP, etc.)
- Generic migration pipeline for server transitions
- Type-safe Pydantic v2 models

## Infrastructure Projects

### 🌐 [flext-api](./flext-api.md)

REST API framework with OpenAPI/Swagger support and flext-core integration.

### 🔐 [flext-auth](./flext-auth.md)

Authentication and authorization services with JWT and LDAP integration.

### 🗄️ [flext-ldap](./flext-ldap.md)

LDAP client operations and management with connection pooling and failover.

### 🗃️ [flext-oracle](./flext-oracle.md)

Oracle database integration with advanced query building and transaction management.

### 🔗 [flext-grpc](./flext-grpc.md)

gRPC services framework with protocol buffer generation and service discovery.

## Domain Projects

### 📦 [flext-meltano](./flext-meltano.md)

Meltano integration for data pipeline orchestration and plugin management.

### 🔍 [flext-observability](./flext-observability.md)

Monitoring, logging, and observability services with metrics collection.

### ✨ [flext-quality](./flext-quality.md)

Code quality tools, linting, and static analysis integration.

## Specialized Projects

### 🎯 [flext-plugin](./flext-plugin.md)

Plugin architecture and discovery system for extending FLEXT functionality.

### 🧪 [flext-tests](./flext-tests.md)

Testing utilities and fixtures for comprehensive test coverage.

### 🏭 [flext-cli](./flext-cli.md)

Command-line interface framework for building CLI applications.

## Integration Guidelines

### Project Dependencies

```
flext-core (foundation)
├── flext-ldif (domain)
├── flext-ldap (domain)
├── flext-oracle (infrastructure)
├── flext-api (infrastructure)
└── flext-auth (infrastructure)
```

### Development Workflow

1. **Core Development**: Changes to flext-core require updates across all projects
2. **Domain Libraries**: Can be developed independently but must maintain API compatibility
3. **Infrastructure Libraries**: Depend on domain libraries for business logic
4. **Testing**: All projects must maintain 100% test coverage

### Release Process

- **Semantic Versioning**: All projects follow semver conventions
- **Changelog Management**: Automated changelog generation from commit messages
- **Dependency Updates**: Coordinated updates across the ecosystem
- **Documentation Updates**: Automatic API documentation generation

## Getting Started with Projects

### Using flext-core

```python
from flext_core import FlextBus
from flext_core import FlextConfig
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import FlextHandlers
from flext_core import FlextLogger
from flext_core import FlextMixins
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import FlextProtocols
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import FlextTypes
from flext_core import FlextUtilities

# Set up dependency injection
container = FlextContainer()

# Use railway-oriented programming
result = some_operation()
if result.is_success:
    data = result.unwrap()
else:
    error = result.failure()
```

### Using flext-ldif

```python
from flext_ldif import FlextLdif

ldif = FlextLdif()

# Parse LDIF content
result = ldif.parse("dn: cn=test,dc=example,dc=com\ncn: test\n")
if result.is_success:
    entries = result.unwrap()

# Migrate between servers
migration_result = ldif.migrate(
    input_dir=Path("data/input"),
    output_dir=Path("data/output"),
    from_server="oid",
    to_server="oud"
)
```

## Project Standards

- **Single Responsibility**: Each project has a clear, focused purpose
- **API Consistency**: All projects expose similar facade patterns
- **Documentation**: Comprehensive README and API documentation for each project
- **Testing**: Full test coverage with integration and E2E tests
- **CI/CD**: Automated testing and deployment pipelines

## Contributing to Projects

Each project maintains its own:

- Issue tracker for bug reports and feature requests
- Development guidelines and contribution processes
- Release schedule and versioning strategy
- Documentation updates and maintenance

See each project's individual documentation for specific contribution guidelines.
