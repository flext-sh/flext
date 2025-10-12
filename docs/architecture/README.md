# Architecture Overview

## System Architecture

FLEXT is built on a clean architecture foundation with flext-core providing the core patterns and abstractions.

### Core Principles

- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **SOLID Principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **CQRS Pattern**: Command Query Responsibility Segregation for complex business logic
- **Railway-Oriented Programming**: Functional error handling with happy/sad path composition
- **Dependency Injection**: FlextCore.Container for managing component dependencies

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

#### FlextCore.Container (Dependency Injection)

```python
from flext_core import FlextCore

container = FlextCore.Container()
container.register(IFooService, FooService())
container.register(IBarService, BarService())

foo_service = container.resolve(IFooService)
```

#### FlextCore.Dispatcher (CQRS)

```python
from flext_core import FlextCore

dispatcher = FlextCore.Dispatcher()
dispatcher.register_handler(CreateUserCommand, CreateUserHandler)
dispatcher.register_handler(GetUserQuery, GetUserHandler)

# Dispatch commands and queries
result = dispatcher.dispatch(CreateUserCommand(user_data))
user = dispatcher.dispatch(GetUserQuery(user_id))
```

#### FlextCore.Result (Railway-Oriented Programming)

```python
from flext_core import FlextCore

def divide(a: float, b: float) -> FlextCore.Result[float, str]:
    if b == 0:
        return FlextCore.Result.failure("Cannot divide by zero")

    return FlextCore.Result.success(a / b)

# Compose operations
result = (FlextCore.Result.success(10)
          .bind(lambda x: divide(x, 2))
          .bind(lambda x: divide(x, 3)))

if result.is_success:
    print(f"Result: {result.unwrap()}")
else:
    print(f"Error: {result.failure()}")
```

#### FlextCore.Bus (Domain Events)

```python
from flext_core import FlextCore

bus = FlextCore.Bus()
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
from flext_core import FlextCore

# In flext-oracle
from flext_core import FlextCore
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
