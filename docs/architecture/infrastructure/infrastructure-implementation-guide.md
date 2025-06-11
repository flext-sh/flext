# Infrastructure Implementation Guide - Architecture

> **Function**: Complete infrastructure layer implementation guide validated against real source code | **Audience**: Architects, Infrastructure engineers, DevOps teams | **Status**: ✅ VALIDATED

[![Infrastructure](https://img.shields.io/badge/layer-infrastructure-blue.svg)](./index.md)
[![Validated](https://img.shields.io/badge/source-validated-orange.svg)](../../../flx/src/flx/infra/)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../index.md)

**Comprehensive infrastructure layer implementation guide validated against actual production code in `/flx/src/flx/infra/`**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture](../index.md) → **📄 Current**: Infrastructure Implementation Guide

### **📍 Learning Path Position**

```
[Architecture Hub](../index.md) → **[INFRASTRUCTURE IMPLEMENTATION]** → [Adapters Implementation](../adapters/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Architecture Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Infrastructure](../../../flx/src/flx/infra/)
- **🔗 Related**: [Ports Hub](../ports/index.md), [Adapters Hub](../adapters/index.md)

---

## 🏗️ **Infrastructure Architecture Overview**

### Hexagonal Architecture Implementation

FLX infrastructure follows strict hexagonal architecture with clear layer separation:

```
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                            │
│         Business Logic, Entities, Domain Events             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     PORTS LAYER                             │
│    Abstract interfaces (inbound/outbound protocols)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTERS LAYER                           │
│  Implement ports and delegate to infrastructure services    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                        │
│        Concrete external system implementations             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Services  │    Cache    │  Database   │    HTTP     │  │
│  │   Registry  │   Service   │   Engine    │   Client    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SYSTEMS                          │
│        Redis, PostgreSQL, HTTP APIs, Message Queues        │
└─────────────────────────────────────────────────────────────┘
```

### Infrastructure Layer Responsibilities

**✅ What Infrastructure Services DO:**

1. **Concrete External System Integration**: Direct communication with databases, APIs, message queues
2. **Connection Management**: Pool management, lifecycle, health monitoring
3. **Protocol Implementation**: HTTP, Redis, PostgreSQL, message broker protocols
4. **Resource Management**: Memory, connections, file handles
5. **Test Engine Support**: In-memory implementations for testing
6. **Production Features**: Clustering, failover, scaling, monitoring

**❌ What Infrastructure Services DO NOT:**

1. **Business Logic**: Domain rules belong in domain layer
2. **Port Implementation**: Adapters implement ports, not infrastructure
3. **Validation/Transformation**: Adapter responsibility, not infrastructure
4. **Domain Knowledge**: Infrastructure is domain-agnostic

---

## 🔧 **Current Infrastructure Components**

### **Validated Infrastructure Structure** (from `/flx/src/flx/infra/`)

#### **1. Service Management (`/services/`)**

**Real Implementation**:

```python
from flx.infra.services.base import BaseInfraService, ServiceRegistry
from flx.infra.services.registry import service_registry

# Service lifecycle management (validated against actual code)
class InfrastructureService(BaseInfraService):
    async def _do_initialize(self) -> None:
        """Service-specific initialization."""
        pass
    
    async def _do_connect(self) -> None:
        """Establish connections."""
        pass
    
    async def _do_start(self) -> None:
        """Start service operations."""
        pass

# Global service registry (validated pattern)
service_registry.register("cache", cache_service)
service_registry.register("database", database_service)
await service_registry.start_all()
```

**Validated Files**:

- `base.py` - BaseInfraService with lifecycle management
- `registry.py` - Global service registry
- `protocols.py` - Service interface protocols
- `resilience.py` - Service resilience patterns

#### **2. Cache Infrastructure (`/cache/`)**

**Real Implementation**:

```python
from flx.infra.cache.cache_service import CacheService
from flx.infra.cache.production_engine import CacheProductionEngine

# Production cache with Redis cluster (validated implementation)
cache = CacheService(
    backend="redis",
    redis_url="redis://localhost:6379",
    key_prefix="flx:",
    default_ttl=3600,
    max_connections=10,
    enable_compression=True,
    enable_pipeline=True,
    memory_fallback=True
)

# Advanced operations (validated methods)
await cache.batch_get(["key1", "key2", "key3"])
await cache.batch_set({"key1": "value1", "key2": "value2"})
await cache.invalidate_pattern("user:*")

# Production engine with clustering (validated)
production_cache = CacheProductionEngine(
    cluster_nodes=["redis://node1:6379", "redis://node2:6379"],
    enable_tls=True,
    health_check_interval=30.0
)
```

**Validated Files**:

- `cache_service.py` - Main cache implementation with Redis/memory fallback
- `production_engine.py` - Enterprise cache with clustering and HA
- `standardized_cache_service.py` - Standardized interface

#### **3. Database Infrastructure (`/database/`)**

**Real Implementation**:

```python
from flx.infra.database.engine import DatabaseEngine
from flx.infra.database.repository import Repository
from flx.infra.database.session import SessionManager

# Database engine with connection pooling (validated implementation)
db_engine = DatabaseEngine(
    url="postgresql+asyncpg://user:pass@host:5432/db",
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    is_async=True
)

# Repository pattern (validated implementation)
class UserRepository(Repository):
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one({"email": email})

# Session management (validated pattern)
async with SessionManager() as session:
    user = await user_repository.create(session, user_data)
```

**Validated Files**:

- `engine.py` - Async database engine with SQLAlchemy
- `repository.py` - Base repository with CRUD operations
- `optimized_repository.py` - Performance-optimized repository
- `session.py` - Session and transaction management
- `production_engine.py` - Production database with read replicas

#### **4. HTTP Client Infrastructure (`/http/`)**

**Real Implementation**:

```python
from flx.infra.http.client_service import HttpClientService
from flx.infra.http.production_engine import HttpProductionEngine

# HTTP client with advanced features (validated implementation)
http_client = HttpClientService(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    verify_ssl=True,
    pool_connections=10,
    pool_maxsize=20,
    auth_token="bearer_token"
)

# Real HTTP operations (validated methods)
response = await http_client.get("/users", params={"limit": 10})
result = await http_client.post("/orders", json={"item": "product"})

# File operations (validated methods)
await http_client.download("/files/report.pdf", "local_report.pdf")
await http_client.upload("/upload", "local_file.txt", field_name="document")

# Authentication (validated methods)
http_client.set_bearer_token("new_token")
http_client.set_basic_auth("username", "password")
```

**Validated Files**:

- `client_service.py` - HTTP client with authentication and file operations
- `production_engine.py` - Production HTTP with advanced features
- `standardized_client_service.py` - Standardized HTTP interface

#### **5. Messaging Infrastructure (`/messaging/`)**

**Real Implementation**:

```python
from flx.infra.messaging.bus import AsyncMessageBus
from flx.infra.messaging.event_service import EventService

# Message bus with Redis backend (validated implementation)
message_bus = AsyncMessageBus(
    broker_type="redis",
    redis_url="redis://localhost:6379/0"
)

# Domain-driven design integration (validated pattern)
from lato import Command, Event, Query

class CreateOrderCommand(Command):
    customer_id: str
    items: list[dict]

result = await message_bus.send_command(
    CreateOrderCommand(customer_id="123", items=[{"id": 1, "qty": 2}])
)

# Event handling (validated pattern)
@message_bus.handler("UserCreatedEvent")
async def handle_user_created(event_data: dict):
    await email_service.send_welcome_email(event_data["email"])
```

**Validated Files**:

- `bus.py` - Async message bus with Dramatiq integration
- `event_service.py` - Event handling and publishing
- `brokers.py` - Message broker implementations
- `handlers.py` - Message handler patterns
- `production_engine.py` - Production messaging with clustering

#### **6. Configuration Management (`/config/`)**

**Real Implementation**:

```python
from flx.infra.config.hierarchical import ConfigManager, load_config

# Hierarchical configuration (validated implementation)
config = ConfigManager(
    config_path=Path("config.yaml"),
    profile="production",  # or "development", "staging", "test"
    env_prefix="FLX_"
)

# Configuration access (validated patterns)
database_url = config.get("database.url")
redis_config = config.get_section("cache.redis")
oracle_settings = config.get_section("oracle")

# Environment variable overrides (validated pattern)
# FLX_DATABASE_URL -> database.url
# FLX_HTTP_TIMEOUT -> http.timeout
```

**Validated Files**:

- `hierarchical.py` - Hierarchical configuration with environment overrides
- `backends.py` - Configuration backend implementations
- `adapter.py` - Configuration adapter patterns
- `settings.py` - Application settings management

#### **7. Observability Infrastructure (`/observability/`)**

**Real Implementation**:

```python
from flx.infra.observability.metrics_system import MetricsCollector, get_metrics_collector
from flx.infra.observability.health import HealthCheck, CompositeHealthCheck

# Metrics collection (validated implementation)
collector = get_metrics_collector("production")

collector.counter(
    "adapter_operations_total",
    value=1.0,
    labels={"adapter": "wms_client", "operation": "get_orders", "status": "success"}
)

collector.histogram(
    "adapter_operation_duration_ms",
    value=245.5,
    labels={"adapter": "http_client", "operation": "post"}
)

# Health monitoring (validated implementation)
class DatabaseHealthCheck(HealthCheck):
    async def check(self) -> HealthCheckResult:
        async with self.db.get_session() as session:
            await session.execute("SELECT 1")
        return HealthCheckResult(
            name="database",
            status=HealthStatus.HEALTHY,
            details={"connection": "active"}
        )

system_health = CompositeHealthCheck("flx_system", [
    DatabaseHealthCheck(database_engine),
    CacheHealthCheck(cache_service)
])
```

**Advanced Observability Features** (VALIDATED against real implementation):

```python
# REAL Production-Grade Health Check Aggregation
class CompositeHealthCheck(HealthCheck):
    """Composite health check that aggregates multiple individual checks."""
    
    async def check(self) -> HealthCheckResult:
        """Execute all child health checks concurrently and aggregate results."""
        results = await asyncio.gather(
            *[check.check() for check in self.checks],
            return_exceptions=True,
        )
        
        # Sophisticated status aggregation using Python 3.13 match
        match (all_healthy, degraded):
            case (True, False): status = HealthStatus.HEALTHY
            case (False, _): status = HealthStatus.UNHEALTHY
            case _: status = HealthStatus.DEGRADED
        
        return HealthCheckResult(name=self.name, status=status, details=details)

# REAL Distributed Tracing with Context Propagation
class TraceContext(BaseModel):
    """Trace context for distributed tracing with automatic propagation."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: str | None = None
    baggage: dict[str, str] = Field(default_factory=dict)

# Context variable for automatic trace propagation across async boundaries
_trace_context: ContextVar[TraceContext | None] = ContextVar("trace_context", default=None)
```

**Validated Files**:

- `metrics_system.py` - Comprehensive metrics collection with MetricsRegistry
- `health.py` - Health check system with composite patterns and async aggregation
- `analytics_service.py` - Advanced analytics and event tracking
- `tracing.py` - Distributed tracing with context propagation and span lifecycle
- `production_engine.py` - Production monitoring features with enterprise-grade capabilities

#### **8. Security Infrastructure (`/security/`)**

**Real Implementation**:

```python
from flx.infra.security.auth import AuthProvider, MultiAuthProvider
from flx.infra.security.crypto import CryptoService

# Authentication provider (validated implementation)
auth_provider = AuthProvider()

context = await auth_provider.authenticate({
    "username": "user@company.com",
    "password": "secure_password"
})

# Multi-provider authentication (validated pattern)
multi_auth = MultiAuthProvider({
    "basic": AuthProvider(),
    "oauth2": OAuth2Provider(),
    "jwt": JWTProvider()
})

# Cryptography services (validated implementation)
crypto = CryptoService()
encrypted = await crypto.encrypt_sensitive_data({"password": "secret"})
decrypted = await crypto.decrypt_sensitive_data(encrypted)
```

**Validated Files**:

- `auth.py` - Authentication provider implementations
- `crypto.py` - Cryptographic services
- `tokens.py` - Token management and validation
- `secure_auth.py` - Enhanced security features
- `production_engine.py` - Production security features

#### **9. Resilience Infrastructure (`/resilience/`)**

**Real Implementation**:

```python
from flx.infra.resilience.circuit_breaker import CircuitBreaker, circuit_breaker

# Circuit breaker decorator (validated implementation)
@circuit_breaker(
    failure_threshold=5,
    recovery_timeout=60.0,
    expected_exception=ConnectionError
)
async def unreliable_oracle_call():
    return await oracle_client.get_data()

# Manual circuit breaker (validated pattern)
breaker = CircuitBreaker(config=CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30.0,
    half_open_max_calls=3
))

result = await breaker.call(risky_operation, param1, param2)
```

**Validated Files**:

- `circuit_breaker.py` - Circuit breaker with Python 3.13 match statements
- `retry.py` - Retry logic with exponential backoff

---

## 🎯 **Implementation Patterns**

### **Correct Infrastructure Service Pattern**

**✅ CORRECT: Infrastructure Service Implementation**

```python
from flx.infra.services.base import BaseInfraService

class CacheService(BaseInfraService):
    def __init__(self, redis_url: str, use_test_engine: bool = False):
        super().__init__("cache", {"redis_url": redis_url})
        self.redis_url = redis_url
        self.use_test_engine = use_test_engine
        self._redis_client: redis.Redis | None = None

    async def _do_connect(self) -> None:
        """Establish Redis connection."""
        if self.use_test_engine:
            self._redis_client = InMemoryTestEngine()
        else:
            self._redis_client = redis.from_url(self.redis_url)

    async def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self._redis_client:
            raise FlxConnectionError("Cache not connected")
        return await self._redis_client.get(key)

    async def health_check(self) -> dict[str, Any]:
        """Check cache health."""
        try:
            await self._redis_client.ping()
            return {"status": "healthy", "connection": "active"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

### **Service Registration Pattern**

**✅ CORRECT: Service Registry Usage**

```python
from flx.infra.services.registry import service_registry

# Register services
service_registry.register("cache", cache_service)
service_registry.register("database", database_service)
service_registry.register("http", http_service)

# Lifecycle management
await service_registry.start_all()
health_status = await service_registry.health_check_all()
await service_registry.stop_all()
```

### **Production Engine Pattern**

**✅ CORRECT: Production Engine Implementation**

```python
class CacheProductionEngine:
    """Production-grade cache with clustering and HA."""
    
    def __init__(self, cluster_nodes: list[str], enable_tls: bool = True):
        self.cluster_nodes = cluster_nodes
        self.enable_tls = enable_tls
        self._cluster: redis.RedisCluster | None = None

    async def connect(self) -> None:
        self._cluster = redis.RedisCluster(
            startup_nodes=self.cluster_nodes,
            ssl=self.enable_tls,
            health_check_interval=30
        )

    async def get_cluster_info(self) -> dict[str, Any]:
        """Get cluster status and metrics."""
        return await self._cluster.cluster_info()
```

---

## 🧪 **Testing Infrastructure**

### **Test Engine Support**

All infrastructure services support test engines for development and testing:

```python
# Production
cache_service = CacheService(redis_url="redis://localhost:6379")

# Testing
cache_service = CacheService(use_test_engine=True)

# Both provide identical interface
await cache_service.connect()
await cache_service.set("key", "value")
result = await cache_service.get("key")
```

### **Test Engine Features**

✅ **In-Memory Implementations**: Fast test engines without external dependencies  
✅ **Interface Compatibility**: Exact same API as production services  
✅ **Failure Simulation**: Test engines can simulate various failure scenarios  
✅ **Performance Testing**: Load testing capabilities with timing  
✅ **Isolation**: Each test gets clean test engine instance  

---

## 📊 **Production Features**

### **Enterprise Grade Infrastructure**

#### **High Availability**

- **Connection Pooling**: Optimized connection management
- **Clustering Support**: Redis clusters, database read replicas
- **Automatic Failover**: Service failover and recovery
- **Health Monitoring**: Continuous health checking

#### **Performance Optimization**

- **Async Operations**: Non-blocking I/O throughout
- **Batch Operations**: Bulk database and cache operations
- **Connection Reuse**: HTTP connection pooling
- **Resource Management**: Proper lifecycle management

#### **Security Features**

- **TLS Encryption**: All production connections encrypted
- **Authentication**: Multi-provider authentication system
- **Token Management**: Secure token generation and validation
- **Access Control**: Role-based access control (RBAC)

#### **Observability**

- **Metrics Collection**: Comprehensive performance metrics
- **Health Checks**: System and component health monitoring
- **Distributed Tracing**: Request tracing across services
- **Analytics**: Real-time performance analytics

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../index.md) - Understanding hexagonal architecture principles
- [Ports Hub](../ports/index.md) - Port interfaces that infrastructure serves

### **Next Steps**

- [Adapters Implementation](../adapters/index.md) - How adapters use infrastructure services
- [Application Layer](../layers/application-layer.md) - Orchestration layer above infrastructure

### **Related Topics**

- [Core Domain Layer](../layers/core-domain-layer.md) - Domain layer that infrastructure supports
- [Testing Infrastructure](../../development/testing/infrastructure-testing.md) - Testing infrastructure services
- [Production Deployment](../../deployment/infrastructure/index.md) - Deploying infrastructure services

---

## 🆘 **Troubleshooting**

### **Common Infrastructure Issues**

**Connection Failures**:

```python
# Check service health
health = await service_registry.health_check_all()
for service_name, result in health.items():
    if not result.healthy:
        print(f"{service_name}: {result.message}")
```

**Performance Issues**:

```python
# Monitor service metrics
from flx.infra.observability.metrics_system import get_metrics_collector
collector = get_metrics_collector()
metrics = collector.get_all_metrics()
```

**Configuration Problems**:

```python
# Validate configuration
from flx.infra.config.hierarchical import load_config
config = load_config()
# Configuration automatically validated against schema
```

---

**📂 Hub**: [Architecture Hub](../index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
