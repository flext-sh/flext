# 🔧 FLX Technical Reference - Source Code Analysis

> **Navigation**: [Documentation Home](../index.md) → [API Reference Hub](./index.md) → FLX Technical Reference

**Comprehensive technical reference based on actual FLX Framework source code implementation and architecture patterns**

## 📋 **Table of Contents**

- [🏗️ Framework Architecture](#️-framework-architecture)
- [📦 Core Domain Layer](#-core-domain-layer)
- [🔌 Ports & Adapters](#-ports--adapters)
- [🏭 Infrastructure Services](#-infrastructure-services)
- [🧪 Testing Framework](#-testing-framework)
- [⚙️ Configuration Management](#️-configuration-management)
- [📊 Observability & Monitoring](#-observability--monitoring)

---

## 🏗️ Framework Architecture

### **Hexagonal Architecture Implementation**

FLX implements clean hexagonal architecture with strict layer separation:

```
┌─────────────────────────────────────────────────────────────┐
│                     External Systems                        │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Adapters  │ │  Services   │ │   Engines   │          │
│  │             │ │             │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Application │ │  Bootstrap  │ │  Container  │          │
│  │  Services   │ │             │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Entities   │ │   Events    │ │ Value Objs  │          │
│  │             │ │             │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### **Layer Responsibilities**

1. **Domain Layer** (`flx.core.*`)
   - Pure business logic and rules
   - Entities with identity and lifecycle
   - Domain events for communication
   - Value objects for immutable data

2. **Application Layer** (`flx.application.*`)
   - Use case orchestration
   - Application services coordination
   - Bootstrap and dependency injection
   - Service container management

3. **Infrastructure Layer** (`flx.infra.*`, `flx.adapters.*`)
   - External system integration
   - Database, cache, HTTP services
   - Security and authentication
   - Monitoring and observability

---

## 📦 Core Domain Layer

### **Entity Implementation**

Based on `flx/core/entities.py`, entities provide identity and lifecycle management:

```python
from flx.core.entities import Entity, AggregateRoot
from typing import Optional
from datetime import datetime

class User(Entity):
    """User entity with identity and lifecycle management."""
    
    username: str
    email: str
    created_at: Optional[datetime] = None
    
    def change_email(self, new_email: str) -> None:
        """Change user email with audit trail."""
        self.email = new_email
        self.touch()  # Updates timestamp automatically
    
    def model_post_init(self, __context):
        """Initialize entity after creation."""
        super().model_post_init(__context)
        if not self.created_at:
            self.created_at = datetime.utcnow()

class Order(AggregateRoot):
    """Order aggregate root with event emission."""
    
    customer_id: str
    status: str = "pending"
    total: float = 0.0
    
    def confirm(self) -> None:
        """Confirm order and emit domain event."""
        if self.status != "pending":
            raise ValueError("Order already confirmed")
        
        self.status = "confirmed"
        self.increment_version()  # Optimistic locking
        
        # Emit domain event
        self.add_event({
            "event_type": "order_confirmed",
            "order_id": self.id,
            "customer_id": self.customer_id,
            "total": self.total
        })
```

### **Key Entity Features**

- **Identity-based equality**: Two entities are equal if their IDs match
- **Optimistic locking**: Version field for concurrent modification detection
- **Audit trail**: Automatic timestamp tracking with `touch()` method
- **Domain events**: Event collection and emission through aggregate roots
- **Immutability controls**: Selective mutability within transaction boundaries

---

## 🔌 Ports & Adapters

### **Port Interfaces**

Based on `flx/ports/`, the framework defines clear contracts:

#### **Inbound Ports** - External actors driving the application

```python
# flx/ports/inbound/api.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class ApiPort(ABC):
    """Port for HTTP API operations."""
    
    @abstractmethod
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming HTTP request."""
        ...
    
    @abstractmethod
    async def authenticate_request(self, headers: Dict[str, str]) -> bool:
        """Authenticate incoming request."""
        ...

# flx/ports/inbound/cli.py
class CliPort(ABC):
    """Port for CLI operations."""
    
    @abstractmethod
    async def execute_command(self, command: str, args: Dict[str, Any]) -> Any:
        """Execute CLI command with arguments."""
        ...
```

#### **Outbound Ports** - Application driving external systems

```python
# flx/ports/outbound/database.py
from typing import Any, Dict, List, Optional

class DatabasePort(ABC):
    """Port for database operations."""
    
    @abstractmethod
    async def create(self, entity: Dict[str, Any]) -> str:
        """Create new entity and return ID."""
        ...
    
    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Find entity by ID."""
        ...
    
    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """Update entity data."""
        ...
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        ...

# flx/ports/outbound/cache.py
class CachePort(ABC):
    """Port for cache operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL."""
        ...
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...
```

### **Adapter Implementation**

Based on `flx/adapters/base.py`, all adapters follow consistent patterns:

```python
from flx.adapters.base import BaseAdapter
from flx.ports.outbound.cache import CachePort
from pydantic import Field
from typing import Any, Optional
import redis.asyncio as redis

class RedisAdapter(BaseAdapter, CachePort):
    """Redis cache adapter implementation."""
    
    # Configuration schema
    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: Optional[str] = Field(default=None, description="Redis password")
    
    def __init__(self, **data):
        super().__init__(**data)
        self._redis_client: Optional[redis.Redis] = None
    
    async def _connect(self) -> None:
        """Initialize Redis connection."""
        self._redis_client = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True
        )
        
        # Test connection
        await self._redis_client.ping()
        self.logger.info(f"Connected to Redis at {self.host}:{self.port}")
    
    async def _disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
            self.logger.info("Disconnected from Redis")
    
    async def _health_check(self) -> bool:
        """Check Redis connection health."""
        if not self._redis_client:
            return False
        
        try:
            await self._redis_client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False
    
    # Port interface implementation
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            value = await self._redis_client.get(key)
            return value
        except Exception as e:
            self.logger.error(f"Failed to get key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        if not self._redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            result = await self._redis_client.set(key, value, ex=ttl)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Failed to set key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        if not self._redis_client:
            raise RuntimeError("Redis client not connected")
        
        try:
            result = await self._redis_client.delete(key)
            return result > 0
        except Exception as e:
            self.logger.error(f"Failed to delete key {key}: {e}")
            return False
```

---

## 🏭 Infrastructure Services

### **Base Service Implementation**

Based on `flx/infra/services/base.py`, all infrastructure services extend `BaseInfraService`:

```python
from flx.infra.services.base import BaseInfraService
from typing import Any, Dict, Optional

class CacheService(BaseInfraService):
    """Cache infrastructure service with Redis and memory fallback."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("cache", config)
        self._redis_client = None
        self._memory_cache: Dict[str, Any] = {}
    
    async def start(self) -> None:
        """Start cache service."""
        await super().start()
        
        # Try to connect to Redis
        try:
            redis_config = self._config.get("redis", {})
            self._redis_client = await self._setup_redis(redis_config)
            self._logger.info("Cache service started with Redis backend")
        except Exception as e:
            self._logger.warning(f"Redis unavailable, using memory cache: {e}")
    
    async def stop(self) -> None:
        """Stop cache service."""
        if self._redis_client:
            await self._redis_client.close()
        self._memory_cache.clear()
        await super().stop()
    
    async def health_check(self) -> ServiceHealthStatus:
        """Check cache service health."""
        if self._redis_client:
            try:
                await self._redis_client.ping()
                return ServiceHealthStatus.HEALTHY
            except Exception:
                return ServiceHealthStatus.DEGRADED
        
        return ServiceHealthStatus.HEALTHY  # Memory cache always works
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._redis_client:
            try:
                return await self._redis_client.get(key)
            except Exception as e:
                self._logger.error(f"Redis get failed: {e}")
        
        return self._memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        success = False
        
        if self._redis_client:
            try:
                await self._redis_client.set(key, value, ex=ttl)
                success = True
            except Exception as e:
                self._logger.error(f"Redis set failed: {e}")
        
        # Always store in memory as fallback
        self._memory_cache[key] = value
        return success or True  # Memory cache always succeeds
```

### **Service Categories**

Based on the source code structure in `flx/infra/`:

1. **Cache Service** (`cache/cache_service.py`)
   - Redis with memory fallback
   - TTL support and eviction policies
   - Health monitoring and failover

2. **Database Service** (`database/engine.py`)
   - SQLAlchemy async engine
   - Connection pooling
   - Transaction management

3. **HTTP Client Service** (`http/client_service.py`)
   - HTTP/HTTPS client with retries
   - Authentication integration
   - Request/response logging

4. **Security Service** (`security/services.py`)
   - Authentication providers
   - JWT token management
   - Role-based authorization

5. **Observability Service** (`observability/metrics.py`)
   - Metrics collection
   - Health checks
   - Performance monitoring

---

## 🧪 Testing Framework

### **Declarative Testing Engine**

Based on `flx/testing/declarative.py`, FLX provides comprehensive testing:

```python
from flx.testing.declarative import (
    DeclarativeTestEngine,
    create_test_engine,
    run_full_test_suite
)

# Create test engine for adapter testing
test_engine = create_test_engine()

# Test cache adapter
cache_adapter = RedisAdapter(host="localhost", port=6379)

async def test_cache_operations():
    """Test cache adapter operations."""
    async with test_engine.test_adapter(cache_adapter) as adapter:
        # Test basic operations
        await adapter.set("test_key", "test_value")
        value = await adapter.get("test_key")
        assert value == "test_value"
        
        # Test TTL
        await adapter.set("ttl_key", "ttl_value", ttl=1)
        await asyncio.sleep(2)
        expired_value = await adapter.get("ttl_key")
        assert expired_value is None

# Run comprehensive test suite
results = await run_full_test_suite([cache_adapter])
```

### **Test Engine Features**

- **Adapter Testing**: Automated testing for all adapter implementations
- **Performance Metrics**: Latency, throughput, and resource usage
- **Health Monitoring**: Connection health and error rates
- **Coverage Analysis**: Test coverage reporting
- **Load Testing**: Concurrent operation testing

---

## ⚙️ Configuration Management

### **Hierarchical Configuration**

Based on `flx/infra/config/hierarchical.py`:

```python
from flx.infra.config.hierarchical import HierarchicalConfig
from pydantic import Field
from typing import Optional

class ApplicationConfig(HierarchicalConfig):
    """Application configuration with hierarchy."""
    
    # Database configuration
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=10, description="Connection pool size")
    
    # Cache configuration
    cache_backend: str = Field(default="redis", description="Cache backend type")
    cache_ttl: int = Field(default=3600, description="Default TTL in seconds")
    
    # Security configuration
    jwt_secret: str = Field(..., description="JWT signing secret")
    jwt_expiry: int = Field(default=3600, description="JWT expiry in seconds")
    
    # Observability configuration
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    log_level: str = Field(default="INFO", description="Logging level")

# Usage with environment variables and config files
config = ApplicationConfig(
    _env_file=".env",
    _env_prefix="APP_",
    _config_files=["config/base.yaml", "config/production.yaml"]
)
```

### **Configuration Sources**

1. **Environment Variables**: `APP_DATABASE_URL`, `APP_CACHE_BACKEND`
2. **Config Files**: YAML, JSON, TOML support
3. **Command Line**: Override via CLI arguments
4. **Default Values**: Sensible defaults for development

---

## 📊 Observability & Monitoring

### **Metrics Collection**

Based on `flx/infra/observability/metrics.py`:

```python
from flx.infra.observability.metrics import MetricsService
from flx.infra.observability.health import HealthService

class ObservabilityService(BaseInfraService):
    """Comprehensive observability service."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("observability", config)
        self.metrics = MetricsService()
        self.health = HealthService()
    
    async def record_operation(self, operation: str, duration: float, success: bool):
        """Record operation metrics."""
        await self.metrics.record_histogram(
            "operation_duration",
            duration,
            tags={"operation": operation, "success": str(success)}
        )
        
        await self.metrics.increment_counter(
            "operation_count",
            tags={"operation": operation, "result": "success" if success else "error"}
        )
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health."""
        return {
            "status": await self.health.get_overall_status(),
            "services": await self.health.get_service_statuses(),
            "metrics": await self.metrics.get_current_metrics(),
            "uptime": await self.health.get_uptime()
        }
```

### **Health Monitoring**

```python
from flx.infra.observability.health import HealthCheck, HealthStatus

class DatabaseHealthCheck(HealthCheck):
    """Database health check implementation."""
    
    def __init__(self, database_service):
        self.database_service = database_service
    
    async def check(self) -> HealthStatus:
        """Check database connectivity."""
        try:
            await self.database_service.execute("SELECT 1")
            return HealthStatus.HEALTHY
        except Exception as e:
            return HealthStatus.UNHEALTHY(f"Database error: {e}")

# Register health checks
health_service = HealthService()
health_service.register_check("database", DatabaseHealthCheck(db_service))
health_service.register_check("cache", CacheHealthCheck(cache_service))
health_service.register_check("http_client", HttpHealthCheck(http_service))
```

---

## 🔗 **Cross-References**

### **⬅️ Prerequisites**

- [Architecture Hub](../architecture/index.md) - Understanding hexagonal architecture patterns before diving into technical implementation
- [Getting Started Hub](../getting-started/index.md) - Basic FLX Framework installation and setup

### **➡️ Next Steps**

- [Core API Reference](./core-api-reference.md) - Detailed API documentation for core domain components
- [Infrastructure Services Guide](../infrastructure/index.md) - Comprehensive infrastructure implementation guides
- [Examples Hub](../examples/index.md) - Working code examples demonstrating these patterns

### **🔗 Related Topics**

- [Development Hub](../development/index.md) - Development tools and practices for implementing these patterns
- [Testing Guide](../guides/testing/index.md) - Testing strategies and frameworks
- [Security Architecture](../security/architecture/security-architecture.md) - Security implementation patterns
- [Oracle Integration](../guides/oracle/index.md) - Enterprise Oracle integration patterns

---

## 📊 **Document Information**

- **Status**: ✅ Complete
- **Last Updated**: June 11, 2025
- **Audience**: Framework developers, system architects
- **Complexity**: Advanced

---

**📂 Content Guide** | **🏠 Hub**: [API Reference](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
