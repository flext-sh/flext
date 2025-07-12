# FLEXT Pydantic Standardization Guide

## Overview

This guide helps migrate all FLEXT modules to use centralized Pydantic models from `flext-core`, eliminating duplication and ensuring consistency.

## Core Principles

1. **Single Source of Truth**: All Pydantic base classes and shared models live in `flext-core`
2. **No Duplication**: Never create duplicate models - import from `flext-core` instead
3. **Clear Separation**:
   - `flext-core`: Base classes, shared models, configuration
   - `flext-observability`: Logging, monitoring, tracing
   - `flext-cli`: CLI interfaces and commands
   - Other modules: Domain-specific models only

## Base Classes

### Domain Models

```python
# Before
from pydantic import BaseModel

class MyDomainModel(BaseModel):
    ...

# After
from flext_core import DomainBaseModel

class MyDomainModel(DomainBaseModel):
    ...
```

### Value Objects

```python
# Before
from pydantic import BaseModel

class UserId(BaseModel):
    value: UUID
    model_config = ConfigDict(frozen=True)

# After
from flext_core import DomainValueObject

class UserId(DomainValueObject):
    value: UUID
```

### Entities

```python
# Before
class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime
    ...

# After
from flext_core import DomainEntity

class User(DomainEntity[UUID]):
    # id, created_at, updated_at already included
    username: str
    email: str
```

### API Models

```python
# Before
class UserResponse(BaseModel):
    success: bool
    data: dict

# After
from flext_core import APIResponse

class UserResponse(APIResponse):
    data: dict
    # success, message, timestamp already included
```

## Common Migration Patterns

### 1. Fix Import Paths

```python
# Old patterns to replace
from flx_core.domain.pydantic_base import DomainBaseModel  # Wrong
from flext_core.domain.pydantic_base import DomainBaseModel  # Correct

# Direct imports
from flext_core import (
    DomainBaseModel,
    APIBaseModel,
    DomainEntity,
    DomainValueObject,
)
```

### 2. Use Shared Models

Instead of creating duplicate models, use shared ones:

```python
# Before (in flext-api)
class HealthResponse(BaseModel):
    status: str
    components: list[dict]

# After
from flext_core import SystemHealth, ComponentHealth
# Use directly, no need to redefine
```

### 3. Remove Local Fallbacks

```python
# Remove this pattern
try:
    from flext_core import DomainBaseModel
except ImportError:
    from pydantic import BaseModel as DomainBaseModel  # NO!
```

## Module-Specific Guidelines

### flext-api

- Use `APIBaseModel` for all request/response models
- Import `UserInfo`, `AuthToken`, `ErrorResponse` from flext-core
- Remove duplicate `APIResponse`, `HealthResponse` definitions

### flext-auth

- Already uses flext-core base classes ✓
- Continue using `Entity`, `ValueObject` for domain models

### flext-cli

- Replace direct `BaseModel` with `APIBaseModel` for API client models
- Import `PipelineConfig` from flext-core instead of redefining

### flext-ldap

- Replace `BaseModel` with `APIBaseModel`
- Use shared `LDAPEntry`, `LDAPScope` from flext-core

### flext-plugin

- Import `PluginType`, `PluginMetadata` from flext-core
- Remove local definitions

### flext-observability

- Keep logging/monitoring specific models
- Import `LogLevel`, `ComponentHealth` from flext-core
- Remove duplicate base imports

## Configuration Models

Use the appropriate base class:

```python
# For settings from environment
from flext_core import BaseSettings

class AppSettings(BaseSettings):
    database_url: str
    redis_url: str

# For API configuration
from flext_core import APIBaseModel

class ServiceConfig(APIBaseModel):
    timeout: int = 30
    retries: int = 3
```

## Testing

After migration, ensure:

1. All imports resolve correctly
2. No circular dependencies
3. Type checking passes: `make type-check`
4. Tests pass: `make test`

## Checklist

For each module:

- [ ] Replace all direct `pydantic.BaseModel` imports
- [ ] Use appropriate base class from flext-core
- [ ] Remove duplicate model definitions
- [ ] Update import paths from `flx_core` to `flext_core`
- [ ] Remove local fallback imports
- [ ] Run type checking and tests
- [ ] Update module documentation

## Common Issues

### Import Errors

```python
# If you see:
ImportError: cannot import name 'DomainBaseModel' from 'flext_core.domain.pydantic_base'

# Solution:
pip install -e ../flext-core  # Install flext-core in development mode
```

### Circular Dependencies

```python
# Avoid:
# In flext-core
from flext_auth import User  # NO!

# Instead:
# Define shared interfaces in flext-core
# Let other modules implement them
```

### Type Conflicts

```python
# If Pipeline is defined in multiple places:
# 1. Rename local versions (e.g., PipelineCLI)
# 2. Or use the shared version from flext-core
```

## Benefits

1. **Consistency**: All models follow same patterns
2. **Maintenance**: Update in one place affects all modules
3. **Type Safety**: Better IDE support and type checking
4. **Performance**: Shared model validation logic
5. **Documentation**: Single source of truth for API contracts
