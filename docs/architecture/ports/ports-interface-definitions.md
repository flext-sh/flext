# 🔌 Ports Interface Definitions

> **Document Type**: Interface Reference | **Audience**: Framework developers, system architects | **Scope**: Complete port contracts catalog

[![Ports](https://img.shields.io/badge/layer-ports-yellow.svg)](./index.md)
[![Hexagonal](https://img.shields.io/badge/pattern-hexagonal-blue.svg)](../index.md)
[![Validated](https://img.shields.io/badge/source-validated-green.svg)](../../reference/specifications/flext-framework-technical-specification.md)

**Complete reference for all port interfaces that define contracts between domain and infrastructure layers**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture Hub](../index.md) → **📂 Sub-Hub**: [Ports Hub](./index.md) → **📄 Current**: Interface Definitions

### **📍 Learning Path Position**

```
[Ports Hub](./index.md) → **[Interface Definitions]** → [Implementation Guide](./port-implementation-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Ports Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Hexagonal Architecture](../hexagonal-architecture-hub.md)

---

## 📋 **Overview**

Port interfaces define the **contracts** between the domain layer and external systems. They represent **what** the domain needs without specifying **how** it's implemented, following the Dependency Inversion Principle.

### **Architecture Principles**

- **Domain-Driven Contracts**: Ports express domain requirements, not technical details
- **Technology Agnostic**: No infrastructure specifics in port definitions
- **Testability First**: All ports must be easily mockable
- **Clear Boundaries**: Strict separation between domain and infrastructure

### **Prerequisites**

- Understanding of [Hexagonal Architecture](../hexagonal-architecture-hub.md)
- Knowledge of Python protocols and abstract base classes
- Familiarity with [Core Domain Layer](../core-domain-layer.md)

---

## 📚 **Port Categories**

Based on actual implementation in `/flext/src/flext/ports/`:

### **📥 Inbound Ports (Driving Side)**

Inbound ports are implemented by adapters and called by external systems:

#### **Command Port**

```python
from typing import Protocol
from flext.domain.commands import Command

class CommandPort(Protocol):
    """Port for executing domain commands."""

    async def execute(self, command: Command) -> Any:
        """Execute a domain command."""
        ...

    async def execute_batch(self, commands: List[Command]) -> List[Any]:
        """Execute multiple commands in batch."""
        ...
```

#### **Query Port**

```python
from typing import Protocol, TypeVar, Generic
from flext.domain.queries import Query

TQuery = TypeVar('TQuery', bound=Query)
TResult = TypeVar('TResult')

class QueryPort(Protocol, Generic[TQuery, TResult]):
    """Port for executing domain queries."""

    async def execute(self, query: TQuery) -> TResult:
        """Execute a domain query."""
        ...
```

#### **API Port**

```python
from typing import Protocol, Dict, Any
from flext.core.types import RequestContext, ResponseContext

class ApiPort(Protocol):
    """Port for HTTP API operations."""

    async def handle_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Any,
        context: RequestContext
    ) -> ResponseContext:
        """Handle incoming HTTP request."""
        ...
```

#### **CLI Port**

```python
from typing import Protocol, List

class CliPort(Protocol):
    """Port for command-line interface operations."""

    async def execute_command(
        self,
        command: str,
        args: List[str],
        options: Dict[str, Any]
    ) -> int:
        """Execute CLI command and return exit code."""
        ...

    def get_help(self, command: str) -> str:
        """Get help text for command."""
        ...
```

### **📤 Outbound Ports (Driven Side)**

Outbound ports are called by the domain and implemented by adapters:

#### **Repository Port**

```python
from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic
from flext.domain.entities import Entity

T = TypeVar('T', bound=Entity)

class RepositoryPort(ABC, Generic[T]):
    """Base repository port for entity persistence."""

    @abstractmethod
    async def save(self, entity: T) -> None:
        """Persist an entity."""
        pass

    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    async def find_all(self) -> List[T]:
        """Retrieve all entities."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str) -> None:
        """Delete an entity."""
        pass
```

#### **Event Publisher Port**

```python
from abc import ABC, abstractmethod
from typing import List
from flext.domain.events import DomainEvent

class EventPublisherPort(ABC):
    """Port for publishing domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a single event."""
        pass

    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events atomically."""
        pass
```

#### **Cache Port**

```python
from abc import ABC, abstractmethod
from typing import Optional, Any

class CachePort(ABC):
    """Port for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove from cache."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cached data."""
        pass
```

#### **HTTP Client Port**

```python
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class HttpClientPort(ABC):
    """Port for HTTP communications."""

    @abstractmethod
    async def get(self, url: str, headers: Optional[Dict] = None) -> Dict:
        """Execute GET request."""
        pass

    @abstractmethod
    async def post(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Dict:
        """Execute POST request."""
        pass

    @abstractmethod
    async def put(self, url: str, data: Dict, headers: Optional[Dict] = None) -> Dict:
        """Execute PUT request."""
        pass

    @abstractmethod
    async def delete(self, url: str, headers: Optional[Dict] = None) -> Dict:
        """Execute DELETE request."""
        pass
```

#### **Configuration Port**

```python
from abc import ABC, abstractmethod
from typing import Any, Optional

class ConfigPort(ABC):
    """Port for configuration access."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass

    @abstractmethod
    def get_required(self, key: str) -> Any:
        """Get required configuration value."""
        pass

    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        pass
```

#### **Database Port**

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class DatabasePort(ABC):
    """Port for database operations."""

    @abstractmethod
    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Execute SQL query."""
        pass

    @abstractmethod
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> int:
        """Execute SQL command, return affected rows."""
        pass

    @abstractmethod
    async def begin_transaction(self) -> Any:
        """Begin database transaction."""
        pass

    @abstractmethod
    async def commit_transaction(self, transaction: Any) -> None:
        """Commit database transaction."""
        pass

    @abstractmethod
    async def rollback_transaction(self, transaction: Any) -> None:
        """Rollback database transaction."""
        pass
```

---

## 🔧 **Design Patterns**

### **Protocol-Based Design (Recommended)**

Using Python protocols for structural typing:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class UserRepositoryProtocol(Protocol):
    """Protocol for user repository operations."""

    async def save_user(self, user: User) -> None: ...
    async def find_user_by_email(self, email: str) -> Optional[User]: ...
    async def user_exists(self, email: str) -> bool: ...
```

### **Generic Ports**

Creating reusable port patterns:

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')
K = TypeVar('K')

class QueryPort(ABC, Generic[T, K]):
    """Generic query port for read operations."""

    @abstractmethod
    async def find_by_criteria(self, criteria: K) -> List[T]:
        """Find entities matching criteria."""
        pass

    @abstractmethod
    async def count_by_criteria(self, criteria: K) -> int:
        """Count entities matching criteria."""
        pass
```

### **Composite Ports**

Combining multiple port interfaces:

```python
class UserServicePort(UserRepositoryPort, EventPublisherPort, CachePort):
    """Composite port combining multiple capabilities."""
    pass
```

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Architecture Hub](../index.md) - Essential hexagonal architecture patterns for understanding port definitions
- [Getting Started](../../getting-started/index.md) - Framework installation and basic concepts required for port implementation
- [FLX Framework Technical Specification](../../reference/specifications/flext-framework-technical-specification.md) - Core framework architecture underlying port contracts

### **➡️ Next Steps**

- [Inbound Ports](./inbound-ports.md) - Detailed implementation patterns for inbound port contracts
- [Adapter Implementation](../adapters/index.md) - Implementing port contracts with concrete adapters
- [Development Hub](../../development/index.md) - Development practices for implementing and testing ports

### **🔗 Related Sections**

- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for port interfaces and implementations
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating port patterns in practice
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure services implementing these port contracts
- [Domain Patterns](../patterns/index.md) - Domain-driven design patterns utilizing port abstractions

---

## 🆘 **Common Anti-Patterns**

### **Infrastructure Leakage**

```python
# ❌ Wrong: Infrastructure details in port
class UserRepositoryPort(ABC):
    @abstractmethod
    async def find_by_sql(self, sql: str) -> List[User]:
        pass

# ✅ Correct: Domain-focused interface
class UserRepositoryPort(ABC):
    @abstractmethod
    async def find_active_users(self) -> List[User]:
        pass
```

### **Overly Complex Ports**

```python
# ❌ Wrong: Too many responsibilities
class MegaPort(ABC):
    async def save_user(self, user: User) -> None: pass
    async def send_email(self, email: str) -> None: pass
    async def log_event(self, event: str) -> None: pass

# ✅ Correct: Single responsibility
class UserRepositoryPort(ABC):
    async def save_user(self, user: User) -> None: pass

class NotificationPort(ABC):
    async def send_email(self, email: str) -> None: pass
```

---

---

**📂 Architecture**: [Ports Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
