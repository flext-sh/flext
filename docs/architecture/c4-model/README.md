# FLEXT C4 Model Architecture Documentation

This directory contains the C4 model diagrams for the FLEXT Enterprise Data Integration Platform, providing a comprehensive view of the system architecture at different levels of detail.

## 📋 C4 Model Levels

### 1. [System Context Diagram](./system-context.md)

**Level 1** - Shows FLEXT in the context of its environment, external systems, and users.

### 2. [Container Diagram](./container-diagram.md)

**Level 2** - Shows the high-level shape of the FLEXT architecture and how responsibilities are distributed across containers.

### 3. [Component Diagrams](./component-diagrams.md)

**Level 3** - Shows how each container is made up of components and their relationships.

### 4. [Code Diagrams](./code-diagrams.md)

**Level 4** - Shows how components are implemented in code (UML class diagrams, entity relationship diagrams, etc.).

## 🎯 FLEXT Architecture Overview

FLEXT is an enterprise-grade data integration platform built with:

- **Clean Architecture** principles with clear layer separation
- **Domain-Driven Design** patterns for business logic modeling
- **Railway-Oriented Programming** for error handling
- **CQRS** and **Event Sourcing** for data processing
- **Dependency Injection** for loose coupling
- **Microservices** architecture with Go and Python components

## 🏗️ Key Architectural Patterns

### Foundation Layer (flext-core)

- **FlextCore.Result[T]** - Railway pattern for error handling
- **FlextCore.Container** - Dependency injection container
- **FlextCore.Models** - DDD patterns (Entity, Value, AggregateRoot)
- **FlextCore.Logger** - Structured logging with context propagation

### Application Layer

- **flext-api** - REST API framework with OpenAPI support
- **flext-auth** - Authentication and authorization services
- **flext-web** - Web application framework
- **flext-cli** - Command-line interface utilities

### Infrastructure Layer

- **flext-ldap** - LDAP client operations
- **flext-ldif** - LDIF processing (RFC 2849/4512 compliant)
- **flext-oracle-\*** - Oracle database integrations
- **flext-grpc** - gRPC services framework

### Data Integration Layer (Singer Platform)

- **Taps** (5): Data extraction from various sources
- **Targets** (5): Data loading to various destinations
- **DBT Transformations** (4): Data transformation pipelines

### Runtime Layer

- **FlexCore** - Go-based runtime container (port 8080)
- **FLEXT Service** - Python-based plugin execution (port 8081)

## 📊 Architecture Quality Attributes

- **Scalability**: Horizontal scaling through microservices
- **Reliability**: Railway pattern for error handling
- **Maintainability**: Clean Architecture with clear boundaries
- **Testability**: Dependency injection and comprehensive testing
- **Security**: Authentication, authorization, and secure communication
- **Performance**: Optimized Go runtime with Python business logic

## 🔗 Related Documentation

- [Arc42 Architecture Documentation](../arc42/README.md)
- [Architecture Decision Records](../adr/README.md)
- [Deployment Architecture](../deployment/README.md)
- [Security Architecture](../security/README.md)
- [Data Architecture](../data/README.md)

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0  
**Maintainer**: FLEXT Architecture Team
