# API Reference

**Reviewed**: 2026-02-17 | **Scope**: Documentation alignment and link consistency


## Table of Contents

- [API Reference](#api-reference)
  - [Core Components](#core-components)
    - [🚀 flext-core](#-flext-core)
    - [📄 flext-ldif](#-flext-ldif)
- [Parse LDIF content](#parse-ldif-content)
- [Write LDIF content](#write-ldif-content)
- [Migrate between LDAP servers](#migrate-between-ldap-servers)
  - [🌐 flext-api](#-flext-api)
  - [🔐 flext-auth](#-flext-auth)
  - [🗄️ flext-ldap](#-flext-ldap)
  - [🗃️ flext-oracle](#-flext-oracle)
  - [Architecture Patterns](#architecture-patterns)
    - [Dependency Injection](#dependency-injection)
    - [Railway-Oriented Programming](#railway-oriented-programming)
    - [CQRS Pattern](#cqrs-pattern)
  - [Configuration](#configuration)
  - [Error Handling](#error-handling)
  - [Logging](#logging)

Complete API documentation for the FLEXT ecosystem.

## Core Components

### 🚀 flext-core

The foundation framework providing core patterns and utilities.

**Key Classes:**

- `FlextContainer` - Dependency injection container
- `FlextDispatcher` - CQRS command/query dispatcher
- `FlextRegistry` - Service registration system
- `FlextResult` - Railway-oriented error handling
- `FlextBus` - Domain event system

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
- `FlextLdifSettings` - Configuration management
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
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

container = FlextContainer()
container.register(FlextLdif, FlextLdif())

service = container.resolve(FlextLdif)
```

### Railway-Oriented Programming

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

def process_data(data: str) -> FlextResult[List[Entry], Exception]:
    try:
        # Processing logic
        return FlextResult.success(entries)
    except Exception as e:
        return FlextResult.failure(e)
```

### CQRS Pattern

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

dispatcher = FlextDispatcher()
dispatcher.register_handler(CreateEntryCommand, CreateEntryHandler)

result = dispatcher.dispatch(CreateEntryCommand(data))
```

## Configuration

All FLEXT libraries support configuration through Pydantic models:

```python
from flext_ldif import FlextLdifSettings

config = FlextLdifSettings(
    default_encoding="utf-8",
    strict_validation=True,
    servers_enabled=True
)
```

## Error Handling

Unified error handling across all libraries:

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

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
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

logger = FlextLogger.get_logger(__name__)
logger.info("Operation completed", extra={"entries_count": len(entries)})
```
