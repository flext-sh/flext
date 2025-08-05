# FLEXT Documentation

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-01-08

## Overview

FLEXT is an enterprise-grade data integration control panel that orchestrates, monitors, and manages distributed data pipelines. Built with a hybrid Go/Python architecture implementing Clean Architecture, DDD, and CQRS patterns.

## 🚀 Quick Start

- **New Developers**: [Getting Started Guide](./guides/getting-started/README.md)
- **Quick Reference**: [Patterns & API Quick Reference](./quick-reference.md)
- **Architecture Overview**: [System Architecture](./architecture/overview.md)
- **Python-Go Integration**: [Integration Architecture](./architecture/python-go-integration.md)

## 📚 Documentation Index

### [Architecture](./architecture/README.md)

System design, patterns, and technical architecture documentation.

- [Overview](./architecture/overview.md) - High-level architecture
- [Clean Architecture](./architecture/clean-architecture.md) - Design principles
- [Ecosystem](./architecture/ecosystem.md) - Complete ecosystem
- [Services](./architecture/services.md) - Service design
- [Python-Go Integration](./architecture/python-go-integration.md) - Go-Python integration patterns
- [Integration](./architecture/integration.md) - Integration patterns
- [Package Structure](./architecture/pkg-structure.md) - Go package organization
- [Workspace](./architecture/workspace.md) - Workspace organization

### [Patterns](./patterns/README.md)

Semantic patterns and coding standards for the FLEXT ecosystem.

- [Foundation](./patterns/foundation.md) - Core patterns
- [Type System](./patterns/types.md) - Type architecture
- [Configuration](./patterns/config-cli.md) - Config & CLI
- [Error Handling](./patterns/error-observability.md) - Errors & observability
- [Constants](./patterns/constants.md) - Semantic constants
- [Utilities](./patterns/utilities.md) - Helper patterns

### [API Reference](./api/README.md)

Complete API documentation and contracts.

- [REST API](./api/contracts.md) - RESTful endpoints
- [OpenAPI Specs](./api/openapi/) - Machine-readable specifications

### [User Guides](./guides/README.md)

Step-by-step guides for common tasks.

- [Getting Started](./guides/getting-started/README.md) - First-time setup
- [Configuration](./guides/configuration/README.md) - Configuration management
- [Deployment](./guides/deployment/README.md) - Deployment options
- [Troubleshooting](./guides/troubleshooting/README.md) - Problem resolution

### [Standards](./standards/README.md)

Coding standards and best practices.

- [Documentation](./standards/documentation.md) - Documentation standards
- [Python](./standards/python.md) - Python coding standards
- [PEP Semantic](./standards/pep-semantic.md) - PEP compliance matrix

### [Development](./development/README.md)

Development planning and status.

- [Implementation Plan](./development/implementation-plan.md) - Roadmap
- [Documentation Status](./development/documentation-status.md) - Current status

## 🏗️ Technology Stack

- **Go 1.24+**: Control plane and orchestration
- **Python 3.13+**: Data processing (Singer SDK, Meltano, DBT)
- **PostgreSQL 15**: Primary data store
- **Redis 7**: Caching and message broker
- **Docker**: Containerization

## 🌐 Ecosystem Components

### Core Services

- **FLEXT Control Panel** (`flext-sh/flext`) - Port 8081
- **FlexCore Runtime** (`flext-sh/flexcore`) - Port 8080

### Library Ecosystem (33 Projects)

- **Foundation**: flext-core, flext-observability
- **Singer Taps/Targets**: LDAP, LDIF, Oracle, Oracle-OIC, Oracle-WMS
- **DBT Projects**: LDAP, LDIF, Oracle, Oracle-WMS
- **Infrastructure**: DB-Oracle, LDAP, LDIF, Oracle-WMS, gRPC
- **Application Services**: API, Auth, Web, CLI, Meltano, Plugin, Quality

## 🔗 Integration Architecture

### Python-Go Integration

FLEXT implements a hybrid architecture where Go services orchestrate Python libraries:

- **Go Control Plane**: Service orchestration, API management, workflow coordination
- **Python Ecosystem**: Data processing, ETL operations, domain-specific logic
- **Integration Patterns**: gRPC, HTTP/REST, subprocess execution
- **Service Coordination**: Distributed tracing, load balancing, failover

### Key Integration Points

- **gRPC Services**: High-performance service-to-service communication
- **REST APIs**: External API exposure with Go as gateway
- **Subprocess Execution**: Direct Python script execution from Go
- **Event Coordination**: Distributed event streaming across services

## 📋 Contributing

1. Fork the repository
2. Create feature branch: `feat/your-feature`
3. Follow [coding standards](./standards/README.md)
4. Submit pull request with clear description

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions)
- **Development**: See [CLAUDE.md](../CLAUDE.md) for AI guidance

---

**Maintainers**: FLEXT Development Team | **License**: MIT
