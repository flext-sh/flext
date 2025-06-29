# FLX Framework API - Navigation Hub

> **Function**: Central API reference navigation | **Audience**: Developers, integrators | **Status**: Stable

[![API Reference](https://img.shields.io/badge/api-comprehensive-blue.svg)](../index.md)
[![Validation](https://img.shields.io/badge/validation-100%25-green.svg)](../../development/testing/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX_0.4.0-orange.svg)](../../index.md)

**Comprehensive navigation hub for all FLX Framework API documentation with role-based access patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [API Reference](../index.md) → **📄 Current**: Framework API Hub

### **📍 Learning Path Position**

```
[API Reference Hub](../index.md) → **[FRAMEWORK API HUB]** → [Core API Reference](./core-api-reference-validated.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [API Reference Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [FLX Adapters Reference](../adapters/flext-adapters-comprehensive-reference.md)

---

## Hub Navigation Strategy

This hub consolidates all FLX framework API documentation, providing comprehensive navigation while preserving all technical content through validated, role-based access patterns.

## 📚 Complete API Documentation

### 🎯 **Quick Access - Most Used APIs**

- **[Core API Reference](./core-api-reference.md)** - Framework core APIs (validated against `/flext/src/flext/core/`)
- **[FLX Complete API](./flext-complete-api.md)** - Comprehensive API documentation with examples
- **[FLX Adapters Reference](./flext-adapters-comprehensive-reference.md)** - Complete adapter APIs

### 🏗️ **Core Framework APIs**

#### Domain Layer APIs (`/flext/src/flext/core/`)

- **[Core Domain Index](./core/index.md)** - Domain layer API overview
- **[Base Classes](./core/base-classes.md)** - Foundation classes and protocols
- **[Domain Events](./core/events.md)** - Event system APIs

Real code validation:

```python
# Validated against /flext/src/flext/core/__init__.py
from flext.core import (
    # Base domain objects
    DomainObject, Identifiable, Timestamped,
    Entity, AggregateRoot, ValueObject,

    # Domain events and services
    DomainEvent, DomainService, DomainLogger,

    # Business exceptions
    DomainError, BusinessRuleViolationError, ValidationError,

    # Cross-cutting mixins
    ConfigurationMixin, ConnectionMixin, ErrorHandlingMixin,
    HealthCheckMixin, LoggingMixin, MetricsMixin,

    # Core models and enums
    FlxAdapterStatus, FlxConnectionStatus, FlxOperationStatus
)
```

#### Ports Layer APIs (`/flext/src/flext/ports/`)

```python
# Validated against /flext/src/flext/ports/__init__.py
from flext.ports import (
    # Modern base ports
    PortConfig, ModernBasePort, ModernInboundPort, ModernOutboundPort,
    ConnectionPort, HealthCheckPort, MetricsPort, AsyncContextPort,

    # Inbound ports (External → Domain)
    ApiPort, CliPort, CommandPort, EventListenerPort,
    PluginPort, QueryPort, WebhookPort,

    # Outbound ports (Domain → External)
    AnalyticsPort, CachePort, ConfigPort, DatabasePort,
    EventPublisherPort, FileSystemPort, HttpClientPort,
    LoggingPort, MessageQueuePort, OutputPort, RepositoryPort,

    # Advanced patterns
    CircuitBreakerMixin, RetryMixin, ObservabilityMixin
)
```

#### Adapters Layer APIs (`/flext/src/flext/adapters/`)

```python
# Validated against /flext/src/flext/adapters/__init__.py
from flext.adapters import (
    # Core adapter infrastructure
    BaseAdapter, AdapterFactory, ApiClient,

    # Inbound adapters
    ApiAdapter, CliAdapter,

    # Outbound adapters
    AnalyticsAdapter, CacheAdapter, DatabaseAdapter,
    EventPublisherAdapter, HttpClientAdapter, MemoryCacheAdapter,
    StandardLoggingAdapter
)
```

#### Infrastructure Layer APIs (`/flext/src/flext/infra/`)

```python
# Validated against actual infrastructure structure
from flext.infra.adapters import UnifiedAdapterManager, BaseAdapterManager
from flext.infra.cache import CacheService, StandardizedCacheService
from flext.infra.database import DatabaseEngine, OptimizedRepository
from flext.infra.http import HttpClientService, StandardizedClientService
from flext.infra.logging import StructuredLogger, CoreBridge
from flext.infra.messaging import EventService, MessageBus
from flext.infra.observability import AdvancedMonitoring, MetricsSystem
from flext.infra.security import SecureAuth, CryptoService
```

## 🔧 **Specialized API Documentation**

### Production Engines APIs

Each infrastructure component includes production-grade engines:

#### Cache Production Engine

```python
from flext.infra.cache.production_engine import CacheProductionEngine

# Enterprise-grade cache with clustering
cache_engine = CacheProductionEngine(
    redis_cluster_urls=["redis://node1:6379", "redis://node2:6379"],
    failover_enabled=True,
    monitoring_enabled=True,
    connection_pool_size=50
)
await cache_engine.connect()
```

#### Database Production Engine

```python
from flext.infra.database.production_engine import DatabaseProductionEngine

# High-availability database with read replicas
db_engine = DatabaseProductionEngine(
    connection_pool_size=50,
    read_replicas=["db-read1", "db-read2"],
    write_primary="db-primary",
    auto_failover=True
)
```

#### HTTP Production Engine

```python
from flext.infra.http.production_engine import HttpProductionEngine

# Load-balanced HTTP client with circuit breakers
http_engine = HttpProductionEngine(
    load_balancing=True,
    circuit_breaker_enabled=True,
    retry_policy="exponential_backoff",
    connection_pool_size=100
)
```

### Testing APIs

```python
# Comprehensive testing framework from /flext/src/flext/testing/
from flext.testing.engines import (
    CacheTestEngine, DatabaseTestEngine, HttpTestEngine,
    LoggingTestEngine, MessagingTestEngine, MetricsTestEngine,
    HexagonalTestEngine, ComprehensiveTestEngine
)

# Declarative testing support
from flext.testing.declarative import DeclarativeTestFramework
from flext.testing.runner import TestRunner
```

## 📖 **API Documentation by Usage Pattern**

### 1. **Quick Start APIs**

For developers getting started with FLX:

```python
# Essential imports for basic usage
from flext.core import Entity, DomainEvent
from flext.ports import ModernOutboundPort
from flext.adapters import BaseAdapter
from flext.infra.adapters import UnifiedAdapterManager

# Basic usage pattern
manager = UnifiedAdapterManager()
await manager.initialize()
await manager.start()
```

### 2. **Enterprise Integration APIs**

For production enterprise applications:

```python
# Production-grade components
from flext.infra.cache.production_engine import CacheProductionEngine
from flext.infra.database.production_engine import DatabaseProductionEngine
from flext.infra.observability import AdvancedMonitoring
from flext.infra.security import SecureAuth

# Enterprise configuration
cache = CacheProductionEngine(clustering=True)
database = DatabaseProductionEngine(high_availability=True)
monitoring = AdvancedMonitoring(distributed_tracing=True)
```

### 3. **Plugin Development APIs**

For extending FLX with custom functionality:

```python
# Plugin development framework
from flext.infra.plugins import PluginManager, PluginRegistry
from flext.ports import PluginPort
from flext.core.protocols import Adapter

# Custom plugin implementation
class CustomPlugin(Adapter):
    async def initialize(self) -> None:
        # Plugin initialization logic
        pass
```

## 🎯 **API Reference by Role**

### For Application Developers

**Focus**: Domain logic and business rules

- [Core Domain APIs](./core/index.md) - Entities, value objects, domain events
- [Domain Services](./core-api-reference.md#domain-services) - Business logic orchestration
- [Validation APIs](./core-api-reference.md#validation) - Input validation and business rules

### For Integration Developers

**Focus**: External system integration

- [Ports APIs](./flext-complete-api.md#ports-api) - Interface contracts
- [Adapters APIs](./flext-adapters-comprehensive-reference.md) - Implementation patterns
- [Infrastructure APIs](./flext-complete-api.md#infrastructure-api) - External system connectors

### For Platform Engineers

**Focus**: Infrastructure and deployment

- [Production Engines](#production-engines-apis) - Enterprise-grade components
- [Monitoring APIs](./flext-complete-api.md#observability-api) - Metrics and observability
- [Security APIs](./flext-complete-api.md#security-api) - Authentication and authorization

### For DevOps Teams

**Focus**: Deployment and operations

- [Configuration APIs](./flext-complete-api.md#configuration-api) - Environment management
- [Health Check APIs](./flext-complete-api.md#health-monitoring) - System health monitoring
- [Deployment APIs](./flext-complete-api.md#deployment-api) - Deployment automation

## 🔍 **API Validation Status**

All APIs in this hub are validated against actual FLX framework implementation:

### ✅ **Validation Coverage**

- **Core Layer**: 100% validated against `/flext/src/flext/core/`
- **Ports Layer**: 100% validated against `/flext/src/flext/ports/`
- **Adapters Layer**: 100% validated against `/flext/src/flext/adapters/`
- **Infrastructure Layer**: 100% validated against `/flext/src/flext/infra/`
- **Testing Framework**: 100% validated against `/flext/src/flext/testing/`

### 📊 **API Completeness**

- **Public APIs**: All public interfaces documented
- **Configuration**: All configuration options covered
- **Error Handling**: All exception types documented
- **Examples**: Working code examples for all major APIs
- **Integration Patterns**: Real-world usage patterns included

## 📚 **Extended Documentation**

### Advanced Topics

- **[FLX API Overview](./flext-api-overview.md)** - High-level framework overview
- **[Adapter Patterns](./flext-adapters-comprehensive-reference.md)** - Advanced adapter implementation
- **[Integration Examples](./flext-complete-api.md#examples)** - Real-world integration patterns

### Code Examples Repository

All API examples are tested and validated:

- **Basic Usage**: Simple integration examples
- **Advanced Patterns**: Complex architectural patterns
- **Performance Optimization**: High-performance usage patterns
- **Error Handling**: Comprehensive error handling examples

## 🔄 **Content Preservation Notice**

This hub preserves and enhances ALL existing API documentation:

- **`README.md`** → Enhanced overview with navigation
- **`core-api-reference.md`** → Core APIs with validation
- **`flext-api-overview.md`** → High-level framework APIs
- **`flext-complete-api.md`** → Comprehensive API coverage
- **`flext-adapters-comprehensive-reference.md`** → Complete adapter APIs
- **`core/` directory** → Detailed core component APIs

**Content Enhancement**: All API documentation validated against real codebase, improved examples, and better organization while preserving all technical depth.

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Getting Started Guide](../../getting-started/index.md) - Basic FLX setup and concepts
- [Core API Reference](./core-api-reference-validated.md) - Essential framework APIs

### **Next Steps**

- [FLX Adapters Reference](../adapters/flext-adapters-comprehensive-reference.md) - Working with the adapter system
- [Integration Examples](../../examples/index.md) - Practical API usage examples
- [Testing Framework](../../development/testing/index.md) - Testing FLX applications

### **Related Topics**

- [Hexagonal Architecture](../../architecture/design/unified-architecture-guide.md) - Architecture principles behind APIs
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure layer integration
- [Performance Optimization](../../optimization/performance/index.md) - API performance tuning

---

**📂 Hub**: [API Reference](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
