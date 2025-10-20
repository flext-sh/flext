# Architecture Overview

## Table of Contents

- [Architecture Overview](#architecture-overview)
  - [System Architecture](#system-architecture)
    - [Core Principles](#core-principles)
    - [Architecture Layers](#architecture-layers)
  - [flext-core Architecture](#flext-core-architecture)
    - [Core Components](#core-components)
      - [FlextContainer (Dependency Injection)](#flextcontainer-dependency-injection)
      - [FlextDispatcher (CQRS)](#flextdispatcher-cqrs)
- [Dispatch commands and queries](#dispatch-commands-and-queries) - [FlextResult (Railway-Oriented Programming)](#flextresult-railway-oriented-programming)
- [Compose operations](#compose-operations) - [FlextBus (Domain Events)](#flextbus-domain-events)
- [Emit events](#emit-events)
  - [Project Structure](#project-structure)
    - [Monorepo Organization](#monorepo-organization)
    - [Package Structure](#package-structure)
  - [Integration Patterns](#integration-patterns)
    - [Cross-Project Dependencies](#cross-project-dependencies)
    - [Import Strategy](#import-strategy)
- [In flext-ldif](#in-flext-ldif)
- [In flext-oracle](#in-flext-oracle)
  - [Deployment Architecture](#deployment-architecture)
    - [Container Strategy](#container-strategy)
    - [Service Architecture](#service-architecture)
  - [Quality Assurance](#quality-assurance)
    - [Testing Strategy](#testing-strategy)
    - [Code Quality](#code-quality)
  - [Security Architecture](#security-architecture)
  - [Performance Considerations](#performance-considerations)

## System Architecture

FLEXT is built on a clean architecture foundation with flext-core providing the core patterns and abstractions.

### Core Principles

- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **SOLID Principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **CQRS Pattern**: Command Query Responsibility Segregation for complex business logic
- **Railway-Oriented Programming**: Functional error handling with happy/sad path composition
- **Dependency Injection**: FlextContainer for managing component dependencies

### Architecture Layers

```
┌─────────────────────────────────────┐
│         Application Layer           │
│   - Use Cases & Application Services│
│   - Command/Query Handlers         │
│   - Application Pipelines          │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│           Domain Layer              │
│   - Business Logic & Rules         │
│   - Domain Models & Value Objects  │
│   - Domain Services                │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│     Infrastructure Layer           │
│   - External Services (DB, LDAP)   │
│   - File System, Network I/O       │
│   - Third-party Integrations       │
└─────────────────┬───────────────────┘
                  │
┌─────────────────────────────────────┐
│           Core Layer               │
│   - flext-core Framework          │
│   - Common Patterns & Abstractions │
│   - Cross-cutting Concerns         │
└─────────────────────────────────────┘
```

## flext-core Architecture

### Core Components

#### FlextContainer (Dependency Injection)

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

container = FlextContainer()
container.register(IFooService, FooService())
container.register(IBarService, BarService())

foo_service = container.resolve(IFooService)
```

#### FlextDispatcher (CQRS)

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

dispatcher = FlextDispatcher()
dispatcher.register_handler(CreateUserCommand, CreateUserHandler)
dispatcher.register_handler(GetUserQuery, GetUserHandler)

# Dispatch commands and queries
result = dispatcher.dispatch(CreateUserCommand(user_data))
user = dispatcher.dispatch(GetUserQuery(user_id))
```

#### FlextResult (Railway-Oriented Programming)

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

def divide(a: float, b: float) -> FlextResult[float, str]:
    if b == 0:
        return FlextResult.failure("Cannot divide by zero")

    return FlextResult.success(a / b)

# Compose operations
result = (FlextResult.success(10)
          .bind(lambda x: divide(x, 2))
          .bind(lambda x: divide(x, 3)))

if result.is_success:
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.failure()}")
```

#### FlextBus (Domain Events)

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

bus = FlextBus()
bus.subscribe(UserCreatedEvent, UserCreatedHandler)

# Emit events
bus.emit(UserCreatedEvent(user_id="123", email="user@example.com"))
```

## Project Structure

### Monorepo Organization

```
flext/
├── flext-core/           # Core framework
│   ├── src/flext_core/   # Core abstractions
│   └── tests/
├── flext-ldif/           # LDIF processing
│   ├── src/flext_ldif/   # LDIF-specific code
│   └── tests/
├── flext-api/            # REST API framework
├── flext-auth/           # Authentication
├── flext-ldap/           # LDAP operations
├── flext-oracle/         # Oracle integration
└── docs/                 # Documentation
```

### Package Structure

Each flext-\* project follows this structure:

```
flext-ldif/
├── src/flext_ldif/
│   ├── __init__.py       # Public API
│   ├── api.py            # Main facade
│   ├── models.py         # Pydantic models
│   ├── config.py         # Configuration
│   ├── constants.py      # Constants
│   ├── exceptions.py     # Domain exceptions
│   ├── typings.py        # Type definitions
│   └── ...
├── tests/
├── docs/
├── examples/
└── pyproject.toml
```

## Integration Patterns

### Cross-Project Dependencies

- **flext-core** is the foundation - all projects depend on it
- **Domain libraries** (flext-ldif, flext-ldap) are independent
- **Infrastructure libraries** (flext-oracle, flext-api) may depend on domain libraries

### Import Strategy

```python
# In flext-ldif
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

# In flext-oracle
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
from flext_ldif import FlextLdifModels  # If needed
```

## Deployment Architecture

### Container Strategy

- Each flext-\* project is a separate Python package
- Published to PyPI for easy installation
- Docker images for containerized deployments

### Service Architecture

- **CLI Tools**: Command-line interfaces for operations
- **API Services**: REST/gRPC services for integration
- **Batch Processors**: Background job processing
- **Event-Driven**: Asynchronous processing with domain events

## Quality Assurance

### Testing Strategy

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **E2E Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

### Code Quality

- **Linting**: Ruff for code style and error detection
- **Type Checking**: Pyright/mypy for static type analysis
- **Coverage**: 100% test coverage requirement
- **Documentation**: Docstring validation and coverage

## Security Architecture

- **Input Validation**: Pydantic models for all inputs
- **Authentication**: JWT and LDAP integration
- **Authorization**: Role-based access control
- **Audit Logging**: Comprehensive security event logging
- **Data Protection**: Encryption at rest and in transit

## Performance Considerations

- **Async/Await**: Full async support for I/O operations
- **Connection Pooling**: Database and LDAP connection reuse
- **Caching**: Intelligent caching strategies
- **Batch Processing**: Efficient bulk operations
- **Monitoring**: Performance metrics and alerting
