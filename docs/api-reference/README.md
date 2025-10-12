# API Reference

Complete API documentation for the FLEXT ecosystem.

## Core Components

### 🚀 flext-core

The foundation framework providing core patterns and utilities.

**Key Classes:**

- `FlextCore.Container` - Dependency injection container
- `FlextCore.Dispatcher` - CQRS command/query dispatcher
- `FlextCore.Registry` - Service registration system
- `FlextCore.Result` - Railway-oriented error handling
- `FlextCore.Bus` - Domain event system

### 📄 flext-ldif

RFC-compliant LDIF processing with enterprise patterns.

**Main API:**

```python
from flext_ldif import FlextLdif

ldif = FlextLdif()

# Parse LDIF content
result = ldif.parse("dn: cn=test,dc=example,dc=com\ncn: test\n")
if result.is_success:
    entries = result.unwrap()

# Write LDIF content
write_result = ldif.write(entries)

# Migrate between LDAP servers
migration_result = ldif.migrate(
    input_dir=Path("data/oid"),
    output_dir=Path("data/oud"),
    from_server="oid",
    to_server="oud"
)
```

**Key Components:**

- `FlextLdif` - Main facade API
- `FlextLdifModels` - Pydantic models for LDIF entities
- `FlextLdifConfig` - Configuration management
- `FlextLdifMigrationPipeline` - Migration orchestration

### 🌐 flext-api

REST API framework with OpenAPI/Swagger support.

### 🔐 flext-auth

Authentication and authorization services.

### 🗄️ flext-ldap

LDAP client operations and management.

### 🗃️ flext-oracle

Oracle database integration and operations.

## Architecture Patterns

### Dependency Injection

```python
from flext_core import FlextCore

container = FlextCore.Container()
container.register(FlextLdif, FlextLdif())

service = container.resolve(FlextLdif)
```

### Railway-Oriented Programming

```python
from flext_core import FlextCore

def process_data(data: str) -> FlextCore.Result[List[Entry], Exception]:
    try:
        # Processing logic
        return FlextCore.Result.success(entries)
    except Exception as e:
        return FlextCore.Result.failure(e)
```

### CQRS Pattern

```python
from flext_core import FlextCore

dispatcher = FlextCore.Dispatcher()
dispatcher.register_handler(CreateEntryCommand, CreateEntryHandler)

result = dispatcher.dispatch(CreateEntryCommand(data))
```

## Configuration

All FLEXT libraries support configuration through Pydantic models:

```python
from flext_ldif import FlextLdifConfig

config = FlextLdifConfig(
    default_encoding="utf-8",
    strict_validation=True,
    server_quirks_enabled=True
)
```

## Error Handling

Unified error handling across all libraries:

```python
from flext_core import FlextCore

result = some_operation()
if result.is_failure:
    error = result.failure()
    logger.error(f"Operation failed: {error}")
else:
    data = result.success()
```

## Logging

Structured logging with flext-core:

```python
from flext_core import FlextCore

logger = FlextCore.Logger.get_logger(__name__)
logger.info("Operation completed", extra={"entries_count": len(entries)})
```
