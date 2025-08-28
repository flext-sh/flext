# Package Structure Guide

This document describes the professional Go package structure implemented in FLEXT Control Panel, following Clean Architecture principles and Go community standards.

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Package Organization](#package-organization)
- [Layer Responsibilities](#layer-responsibilities)
- [Import Rules](#import-rules)
- [Development Guidelines](#development-guidelines)

## Overview

FLEXT Control Panel implements a professional `pkg/` directory structure that follows:

- **Go Community Standards**: Industry-standard package organization
- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **Domain-Driven Design**: Business domain modeling with bounded contexts
- **CQRS Patterns**: Command/query separation for scalability

```
pkg/                              # Public API following Go standards
├── adapters/                     # Interface Adapters Layer
├── application/                  # Application Business Logic
├── domain/                       # Domain Business Logic
├── infrastructure/               # Infrastructure Concerns
├── interfaces/                   # External Interfaces
└── utils/                        # Shared Utilities
```

## Design Principles

### 1. Dependency Inversion

Dependencies flow inward toward the domain layer:

```
interfaces/ → adapters/ → application/ → domain/
     ↓              ↓           ↓
infrastructure/ ────────────────┘
```

### 2. Bounded Contexts

Each domain area is organized as a bounded context:

```
pkg/domain/
├── pipeline/        # Pipeline management domain
├── plugin/          # Plugin management domain
├── singer/          # Singer tap/target domain
├── meltano/         # Meltano orchestration domain
└── dbt/             # DBT transformation domain
```

### 3. Layer Isolation

Each layer has specific responsibilities and can only depend on inner layers:

- **Interfaces**: External communication (REST, CLI, Web)
- **Adapters**: Interface implementations and external system integration
- **Application**: Business workflows and use cases
- **Domain**: Core business logic and rules
- **Infrastructure**: Technical implementation details

## Package Organization

### `/pkg/adapters/` - Interface Adapters Layer

Implements interfaces defined by the application layer and adapts external concerns.

```
adapters/
├── controllers/                 # HTTP Controllers
│   └── http/
│       ├── dto/                 # Data Transfer Objects
│       ├── pipeline_controller.go
│       ├── plugin_controller.go
│       └── presenter.go
├── gateways/                    # External System Gateways
│   ├── pipeline_repository.go
│   └── plugin_repository.go
└── presenters/                  # Response Presentation Logic
```

**Responsibilities:**

- HTTP request/response handling
- Data Transfer Object (DTO) definitions
- External system integration
- Response formatting and presentation

**Import Rules:**

- Can import from `application/` and `domain/`
- Can import from `infrastructure/` for implementations
- Cannot import from `interfaces/`

### `/pkg/application/` - Application Business Logic

Orchestrates business workflows and implements use cases.

```
application/
├── commands/                    # CQRS Commands (global)
├── queries/                     # CQRS Queries (global)
├── services/                    # Application Services (global)
├── dbt/                         # DBT Management
│   ├── create_project.go
│   ├── delete_project.go
│   └── ports.go
├── meltano/                     # Meltano Orchestration
│   └── services/
│       └── meltano_service.go
├── pipeline/                    # Pipeline Management
│   ├── commands/
│   ├── queries/
│   ├── services/
│   └── ports/
├── plugin/                      # Plugin Management
│   ├── commands/
│   ├── ports/
│   └── plugin_service.go
└── singer/                      # Singer Management
    ├── commands/
    ├── queries/
    ├── services/
    └── ports/
```

**Responsibilities:**

- Use case implementation
- Business workflow orchestration
- Command and query handling (CQRS)
- Application service coordination
- Port definitions (dependency inversion)

**Import Rules:**

- Can import from `domain/` only
- Cannot import from `adapters/`, `infrastructure/`, or `interfaces/`
- Defines ports (interfaces) that are implemented by outer layers

### `/pkg/domain/` - Domain Business Logic

Contains the core business logic and domain model.

```
domain/
├── entities/                    # Shared domain entities
├── events/                      # Shared domain events
├── repositories/                # Shared repository interfaces
├── services/                    # Shared domain services
├── dbt/                         # DBT Domain
│   ├── entities/
│   ├── events/
│   └── services/
├── meltano/                     # Meltano Domain
│   └── entities/
├── pipeline/                    # Pipeline Domain
│   ├── entities/
│   ├── events/
│   ├── repositories/
│   └── services/
├── plugin/                      # Plugin Domain
│   ├── entities/
│   ├── events/
│   └── repositories.go
├── singer/                      # Singer Domain
│   ├── entities/
│   └── services/
└── shared/                      # Shared domain concepts
    ├── entity.go
    └── events.go
```

**Responsibilities:**

- Business entities and value objects
- Domain events and business rules
- Repository interface definitions
- Domain service implementations
- Business logic validation

**Import Rules:**

- Cannot import from any other layers
- Only depends on Go standard library and basic utilities
- Defines interfaces that are implemented by outer layers

### `/pkg/infrastructure/` - Infrastructure Concerns

Implements technical concerns and external system integrations.

```
infrastructure/
├── database/                    # Database Access
│   └── migrations/              # Database migrations
├── http/                        # HTTP Infrastructure
├── messaging/                   # Message Bus
├── cache/                       # Caching Layer
├── logging/                     # Structured Logging
├── config/                      # Configuration Management
├── persistence/                 # Data Persistence
│   └── state_manager.go
└── [implementation-files]       # Various infrastructure implementations
```

**Responsibilities:**

- Database access and ORM configuration
- HTTP server and client implementations
- Message bus and event publishing
- Caching mechanisms
- Logging and monitoring
- Configuration management
- External API integrations

**Import Rules:**

- Can import from `domain/` and `application/` for interface implementations
- Can import from `adapters/` when needed
- Cannot import from `interfaces/`

### `/pkg/interfaces/` - External Interfaces

Defines external communication mechanisms and entry points.

```
interfaces/
├── api/                         # REST API Definitions
├── cli/                         # Command Line Interface
│   ├── cli.go
│   └── commands/
│       ├── dbt_commands.go
│       ├── pipeline_commands.go
│       ├── server_commands.go
│       ├── singer_commands.go
│       └── utility_commands.go
└── web/                         # Web Interface
```

**Responsibilities:**

- REST API route definitions
- CLI command implementations
- Web interface handlers
- External communication protocols
- User interaction logic

**Import Rules:**

- Can import from all other layers
- Primary entry points for external communication
- Coordinates between adapters and application layers

### `/pkg/utils/` - Shared Utilities

Contains shared utilities and cross-cutting concerns.

```
utils/
├── shared_kernel/               # DDD Shared Kernel
│   ├── aggregate_root.go
│   ├── base_entity.go
│   ├── domain_event.go
│   ├── errors.go
│   ├── patterns.go
│   ├── validator.go
│   └── [other-shared-utilities]
└── gopy/                        # Go-Python Integration
    └── meltano_adapter.go
```

**Responsibilities:**

- DDD shared kernel implementations
- Common utility functions
- Cross-cutting concerns
- Integration bridges (Go-Python)
- Shared patterns and abstractions

**Import Rules:**

- Can be imported by any layer
- Should have minimal dependencies
- Provides foundation for other packages

## Layer Responsibilities

### Domain Layer (Core)

**What it contains:**

- Business entities with behavior
- Domain events and business rules
- Repository and service interfaces
- Value objects and aggregates

**What it does NOT contain:**

- Infrastructure concerns
- Framework dependencies
- External system knowledge
- Implementation details

**Example Entity:**

```go
// pkg/domain/pipeline/entities/pipeline.go
package entities

import "github.com/flext-sh/flext/pkg/utils/shared_kernel"

type Pipeline struct {
    shared_kernel.BaseEntity
    Name        string
    Description string
    Status      PipelineStatus
    Steps       []PipelineStep
}

func (p *Pipeline) AddStep(step PipelineStep) error {
    // Business logic here
    p.RaiseEvent(NewStepAddedEvent(p.ID, step))
    return nil
}
```

### Application Layer

**What it contains:**

- Use case implementations
- Application services
- Command and query handlers
- Port definitions (interfaces)

**What it does NOT contain:**

- UI concerns
- Database implementation details
- External API implementations
- Infrastructure configuration

**Example Application Service:**

```go
// pkg/application/pipeline/services/pipeline_service.go
package services

type PipelineService struct {
    repo ports.PipelineRepository
    eventBus ports.EventBus
}

func (s *PipelineService) CreatePipeline(cmd CreatePipelineCommand) error {
    pipeline := entities.NewPipeline(cmd.Name, cmd.Description)

    if err := s.repo.Save(pipeline); err != nil {
        return err
    }

    return s.eventBus.Publish(pipeline.Events()...)
}
```

### Adapters Layer

**What it contains:**

- HTTP controllers and DTOs
- Repository implementations
- External system gateways
- Response presenters

**What it does NOT contain:**

- Business logic
- Domain rules
- Use case orchestration

**Example Controller:**

```go
// pkg/adapters/controllers/http/pipeline_controller.go
package http

type PipelineController struct {
    pipelineService *services.PipelineService
}

func (c *PipelineController) CreatePipeline(w http.ResponseWriter, r *http.Request) {
    var dto CreatePipelineDTO
    // Parse request, call service, format response
}
```

### Infrastructure Layer

**What it contains:**

- Database implementations
- HTTP server configuration
- Message bus implementations
- Caching mechanisms

**What it does NOT contain:**

- Business logic
- Use case workflows
- Domain rules

### Interfaces Layer

**What it contains:**

- REST API route definitions
- CLI command implementations
- Web interface handlers

**What it does NOT contain:**

- Business logic (delegates to application layer)
- Infrastructure concerns (uses adapters)

## Import Rules and Dependencies

### Allowed Dependencies

```
interfaces/ ──→ adapters/ ──→ application/ ──→ domain/
     │              │             │
     └──────────────┼─────────────┘
                    │
               infrastructure/
                    │
                 utils/ (can be imported by any layer)
```

### Forbidden Dependencies

❌ **Domain cannot import from any other layer**
❌ **Application cannot import from adapters, infrastructure, or interfaces**
❌ **Adapters cannot import from interfaces**
❌ **Circular dependencies between any packages**

### Import Examples

**✅ Correct Imports:**

```go
// pkg/application/pipeline/services/pipeline_service.go
import (
    "github.com/flext-sh/flext/pkg/domain/pipeline/entities"     // ✅ Application → Domain
    "github.com/flext-sh/flext/pkg/application/pipeline/ports"   // ✅ Same layer
    "github.com/flext-sh/flext/pkg/utils/shared_kernel"         // ✅ object layer → Utils
)
```

**❌ Incorrect Imports:**

```go
// pkg/domain/pipeline/entities/pipeline.go
import (
    "github.com/flext-sh/flext/pkg/infrastructure/database"     // ❌ Domain → Infrastructure
    "github.com/flext-sh/flext/pkg/adapters/controllers"       // ❌ Domain → Adapters
)
```

## Development Guidelines

### Creating New Features

1. **Start with Domain**: Define entities, events, and business rules
2. **Add Application Layer**: Create use cases and application services
3. **Implement Adapters**: Add controllers, repositories, and gateways
4. **Wire Infrastructure**: Implement databases, external APIs, etc.
5. **Expose Interfaces**: Add REST APIs, CLI commands, or web handlers

### Package Naming Conventions

- Use **lowercase** package names
- Use **singular nouns** for packages (e.g., `entity`, not `entities`)
- Be **descriptive** but **concise**
- Follow Go naming conventions

### File Organization

- **One concept per file** when possible
- Group related functionality in the same package
- Use **descriptive filenames** that match the primary type/function
- Keep files **focused and cohesive**

### Testing Strategy

```
pkg/domain/pipeline/entities/
├── pipeline.go
├── pipeline_test.go         # Unit tests for domain logic
├── pipeline_integration_test.go # Integration tests
└── testdata/                # Test data files
```

### Documentation Requirements

- **Package-level documentation** for each major package
- **Public API documentation** for all exported functions and types
- **Architecture Decision Records** for significant design choices
- **Example usage** in package documentation

## Migration from Internal Structure

The FLEXT Control Panel was migrated from an `internal/` structure to this professional `pkg/` structure:

### Before (internal/)

```
internal/
├── bounded_contexts/        # Mixed concerns
├── adapters/               # Unclear boundaries
├── infrastructure/         # Tightly coupled
└── usecases/              # Non-standard naming
```

### After (pkg/)

```
pkg/
├── domain/                 # Clear business logic
├── application/           # Clean use cases
├── adapters/              # Well-defined boundaries
├── infrastructure/        # Proper separation
└── interfaces/            # External communication
```

### Benefits Achieved

- **Professional Structure**: Follows Go community standards
- **Clear Dependencies**: Explicit dependency direction
- **Better Testability**: Each layer can be tested independently
- **Improved Maintainability**: Clear separation of concerns
- **Enhanced Reusability**: Packages can be reused across projects

---

**Version**: 0.9.0
**Last Updated**: 2025-08-02  
**Author**: FLEXT Development Team
