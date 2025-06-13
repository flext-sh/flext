# Architecture Standards - PyAuto

Hexagonal architecture guidelines and standards for PyAuto enterprise development.

## 🏗️ HEXAGONAL ARCHITECTURE PRINCIPLES

### Core Architecture Layers

```
┌─────────────────────────────────────┐
│          Application Layer          │  ← Business logic, commands, queries
├─────────────────────────────────────┤
│            Domain Layer             │  ← Entities, value objects, domain services
├─────────────────────────────────────┤
│         Infrastructure Layer        │  ← External systems, databases, APIs
└─────────────────────────────────────┘
          ↑                    ↑
    Inbound Ports         Outbound Ports
    (API, CLI, Web)       (DB, HTTP, Cache)
```

### Dependency Direction

**MANDATORY**: Dependencies ALWAYS point inward
- Infrastructure → Application → Domain
- **NEVER**: Domain → Infrastructure
- **NEVER**: Application → Infrastructure (use ports)

## 📋 LAYER RESPONSIBILITIES

### Domain Layer (`flx/core/domain/`)

**CONTAINS**:
- Entities (business objects with identity)
- Value Objects (immutable data structures)
- Domain Services (business logic)
- Domain Events
- Domain Exceptions

**FORBIDDEN**:
- External dependencies (databases, HTTP, etc.)
- Infrastructure imports
- Framework-specific code

```python
# ✅ CORRECT: Pure domain entity
class User(Entity):
    def __init__(self, user_id: UserId, email: Email):
        self.id = user_id
        self.email = email
    
    def change_email(self, new_email: Email) -> None:
        # Business logic here
        self.email = new_email

# ❌ WRONG: Domain importing infrastructure
from requests import get  # FORBIDDEN in domain
```

### Application Layer (`flx/application/`)

**CONTAINS**:
- Commands and Command Handlers
- Queries and Query Handlers
- Application Services
- Port Definitions (interfaces)
- Use Cases

**FORBIDDEN**:
- Direct infrastructure dependencies
- Framework-specific implementations

```python
# ✅ CORRECT: Application service using ports
class UserService:
    def __init__(self, user_repo: UserRepositoryPort):
        self.user_repo = user_repo  # Port, not implementation
    
    async def get_user(self, user_id: str) -> User:
        return await self.user_repo.get_by_id(user_id)

# ❌ WRONG: Application directly using infrastructure
from sqlalchemy import create_engine  # FORBIDDEN in application
```

### Infrastructure Layer (`flx/infra/`)

**CONTAINS**:
- Database implementations
- HTTP clients
- Cache implementations
- External service adapters
- Framework integrations

**ALLOWED**:
- External dependencies
- Framework-specific code
- Implementation details

```python
# ✅ CORRECT: Infrastructure implementing ports
class SqlUserRepository(UserRepositoryPort):
    def __init__(self, db_engine: DatabaseEngine):
        self.db = db_engine
    
    async def get_by_id(self, user_id: str) -> User:
        # Database-specific implementation
        pass
```

## 🔌 PORTS AND ADAPTERS

### Inbound Ports (Primary Adapters)

**Purpose**: Allow external actors to interact with application

```python
# Port definition (in application layer)
class UserManagementPort(Protocol):
    async def create_user(self, command: CreateUserCommand) -> User:
        ...

# Adapter implementation (in infrastructure)
class RestApiAdapter:
    def __init__(self, user_service: UserManagementPort):
        self.user_service = user_service
    
    @app.post("/users")
    async def create_user_endpoint(self, request: CreateUserRequest):
        command = CreateUserCommand(...)
        return await self.user_service.create_user(command)
```

### Outbound Ports (Secondary Adapters)

**Purpose**: Allow application to interact with external systems

```python
# Port definition (in application layer)
class UserRepositoryPort(Protocol):
    async def save(self, user: User) -> None:
        ...
    
    async def get_by_id(self, user_id: str) -> User:
        ...

# Adapter implementation (in infrastructure)
class DatabaseUserRepository(UserRepositoryPort):
    async def save(self, user: User) -> None:
        # Database-specific implementation
        pass
```

## 🚨 ARCHITECTURAL VIOLATIONS - PREVENTION

### Common Violations and Fixes

#### 1. Domain Layer Importing Infrastructure

```python
# ❌ VIOLATION
from flx.infra.database import DatabaseEngine  # Domain importing infra

# ✅ CORRECT
from flx.ports.outbound import DatabasePort  # Domain using port
```

#### 2. Application Layer Direct Infrastructure Usage

```python
# ❌ VIOLATION
from sqlalchemy import create_engine
engine = create_engine(url)  # Direct infrastructure usage

# ✅ CORRECT
def __init__(self, db_port: DatabasePort):
    self.db = db_port  # Using port interface
```

#### 3. Circular Dependencies Between Layers

```python
# ❌ VIOLATION
# domain/user.py
from flx.application.services import UserService  # Domain → Application

# ✅ CORRECT
# Use domain events instead
class User(Entity):
    def change_email(self, new_email: Email) -> None:
        self.email = new_email
        self.record_event(UserEmailChanged(self.id, new_email))
```

## 🔧 DEPENDENCY INJECTION

### Factory Pattern for Adapter Creation

```python
from flx.infra.database import DatabaseEngine
from flx.infra.cache import RedisCache
from flx.adapters.outbound.database import DatabaseAdapter

def create_infrastructure_adapters(config: Config) -> dict[str, Any]:
    """Create infrastructure adapters with proper dependency injection."""
    
    # Create infrastructure components
    db_engine = DatabaseEngine(url=config.database_url)
    cache = RedisCache(url=config.redis_url)
    
    # Create adapters
    db_adapter = DatabaseAdapter(engine=db_engine)
    cache_adapter = CacheAdapter(cache=cache)
    
    return {
        "database": db_adapter,
        "cache": cache_adapter,
    }
```

### Bootstrap Integration

```python
class Bootstrap:
    def __init__(self):
        self.adapters: dict[str, BaseAdapter] = {}
    
    def register_adapter(self, name: str, adapter: BaseAdapter) -> None:
        """Register adapter with bootstrap."""
        self.adapters[name] = adapter
    
    def get_adapter(self, name: str) -> BaseAdapter:
        """Get registered adapter."""
        if name not in self.adapters:
            raise AdapterNotFoundError(f"Adapter {name} not registered")
        return self.adapters[name]
```

## 📋 ARCHITECTURAL VALIDATION

### Mandatory Architecture Checks

```python
#!/usr/bin/env python3
"""Architecture validation script - run before any commits."""

import ast
import os
from pathlib import Path

def check_layer_dependencies():
    """Verify no architectural boundary violations."""
    
    violations = []
    
    # Check domain layer doesn't import infrastructure
    domain_files = Path("flx/core/domain").rglob("*.py")
    for file_path in domain_files:
        with open(file_path) as f:
            content = f.read()
            
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "infra" in node.module:
                    violations.append(f"{file_path}: Domain importing infrastructure: {node.module}")
    
    return violations

# Run validation
violations = check_layer_dependencies()
if violations:
    print("❌ ARCHITECTURAL VIOLATIONS FOUND:")
    for violation in violations:
        print(f"  {violation}")
    exit(1)
else:
    print("✅ Architecture validation passed")
```

### Integration Testing for Architecture

```python
@pytest.mark.architecture
def test_domain_layer_independence():
    """Test that domain layer has no external dependencies."""
    
    # Domain should import only:
    # - Standard library
    # - Other domain modules
    # - typing modules
    
    allowed_imports = {
        "typing", "datetime", "uuid", "enum", "abc", 
        "dataclasses", "functools", "collections"
    }
    
    violations = check_domain_imports()
    assert not violations, f"Domain layer violations: {violations}"

@pytest.mark.architecture  
def test_application_uses_ports_only():
    """Test that application layer only uses port interfaces."""
    
    # Application should not import from infrastructure
    violations = check_application_imports()
    assert not violations, f"Application layer violations: {violations}"
```

## 🎯 CLEAN ARCHITECTURE BENEFITS

### Achieved Through Proper Implementation

1. **Testability**: Easy to test each layer in isolation
2. **Flexibility**: Can swap infrastructure without changing business logic
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Independent scaling of different layers
5. **Technology Independence**: Business logic not tied to frameworks

### Anti-Patterns to Avoid

```python
# ❌ ANTI-PATTERN: God object
class UserService:
    def create_user(self): pass
    def send_email(self): pass
    def log_action(self): pass
    def validate_payment(self): pass  # Too many responsibilities

# ✅ CORRECT: Single responsibility
class UserService:
    def __init__(self, user_repo: UserRepositoryPort, event_bus: EventBusPort):
        self.user_repo = user_repo
        self.event_bus = event_bus
    
    def create_user(self, command: CreateUserCommand) -> User:
        # Single responsibility: user creation
        pass
```

## 📊 ARCHITECTURE METRICS

### Quality Indicators

**Good Architecture Metrics:**
- Domain layer: 0 external dependencies
- Application layer: Only port dependencies
- Infrastructure layer: Can depend on anything
- Cyclomatic complexity < 10 per method
- Clear interface definitions

**Bad Architecture Metrics:**
- Circular dependencies between layers
- Domain importing infrastructure
- Application directly using databases/HTTP
- Large classes (>500 lines)
- Missing interface definitions

## ⚡ ARCHITECTURE ENFORCEMENT

### Pre-commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit
echo "Running architecture validation..."

python scripts/validate_architecture.py
if [ $? -ne 0 ]; then
    echo "❌ Architecture validation failed"
    exit 1
fi

echo "✅ Architecture validation passed"
```

### CI/CD Integration

```yaml
# .github/workflows/architecture.yml
name: Architecture Validation
on: [push, pull_request]

jobs:
  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Architecture
        run: python scripts/validate_architecture.py
```

---

*Hexagonal architecture is fundamental to PyAuto's maintainability and testability. Follow these standards exactly to ensure clean, scalable code.*