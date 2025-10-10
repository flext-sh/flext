# Core Components Diagram

## Overview

Detailed view of FLEXT core components and their relationships:

```plantuml
@startuml FLEXT Core Components
!include <C4/C4_Component>

Container_Boundary(core, "FLEXT Core Library") {

    Component(result, "FlextResult[T]", "Railway Pattern", "Monadic error handling with composition")
    Component(container, "FlextContainer", "DI Container", "Dependency injection and service management")
    Component(models, "FlextModels", "DDD Patterns", "Entity, Value, AggregateRoot patterns")
    Component(logger, "FlextLogger", "Structured Logging", "Context-aware logging with propagation")

    Component(dispatcher, "FlextDispatcher", "CQRS Dispatcher", "Command and query dispatching")
    Component(bus, "FlextBus", "Event Bus", "Domain event publishing and subscription")
    Component(config, "FlextConfig", "Configuration", "Environment-aware configuration management")
}

Container_Boundary(domain, "Domain Services") {

    Component(ldap_client, "LDAP Client", "Directory Operations", "LDAP protocol implementation")
    Component(ldif_parser, "LDIF Parser", "File Processing", "RFC 2849/4512 LDIF processing")
    Component(oracle_client, "Oracle Client", "Database Operations", "Oracle JDBC integration")
    Component(api_framework, "API Framework", "REST Services", "FastAPI-based REST framework")
}

Container_Boundary(infrastructure, "Infrastructure Services") {

    Component(file_system, "File System", "I/O Operations", "File and directory operations")
    Component(network, "Network Client", "HTTP Operations", "HTTP client with retry logic")
    Component(cache, "Cache Manager", "Caching", "Redis and in-memory caching")
    Component(security, "Security Manager", "Authentication", "JWT and RBAC implementation")
}

Rel(result, container, "Used by", "Error handling")
Rel(container, models, "Injects", "Service dependencies")
Rel(models, logger, "Logs", "Domain events")

Rel(dispatcher, bus, "Publishes", "Domain events")
Rel(bus, logger, "Logs", "Event processing")

Rel(domain, core, "Depends on", "Foundation patterns")
Rel(infrastructure, core, "Depends on", "Foundation patterns")

@enduml
```

## Component Details

### Core Components

#### FlextResult[T]
- **Pattern**: Railway-oriented programming
- **Purpose**: Type-safe error handling with composition
- **Usage**: All operations that can fail return FlextResult[T]

#### FlextContainer
- **Pattern**: Dependency injection container
- **Purpose**: Service registration and resolution
- **Usage**: Global singleton for dependency management

#### FlextModels
- **Pattern**: Domain-Driven Design
- **Purpose**: Entity, Value, and AggregateRoot patterns
- **Usage**: Business domain modeling

#### FlextLogger
- **Pattern**: Structured logging
- **Purpose**: Context-aware logging with propagation
- **Usage**: Consistent logging across all components

### Domain Components

#### LDAP Client
- **Protocol**: LDAP v3 (RFC 4511)
- **Purpose**: Directory operations and authentication
- **Features**: Connection pooling, server-specific quirks

#### LDIF Parser
- **Standard**: RFC 2849/4512
- **Purpose**: LDIF file processing and migration
- **Features**: Schema parsing, entry validation, server quirks

#### Oracle Client
- **Protocol**: JDBC/OCI
- **Purpose**: Oracle database operations
- **Features**: Connection pooling, transaction management

#### API Framework
- **Technology**: FastAPI
- **Purpose**: REST API development
- **Features**: OpenAPI documentation, validation, middleware

---

**Generated:** 2025-10-10 15:19:05
**Version:** 0.9.0
