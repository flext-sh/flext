# Cache Infrastructure - Infrastructure

> **Function**: Distributed caching patterns and implementation | **Audience**: Backend developers, performance engineers | **Status**: Stable

[![Infrastructure](https://img.shields.io/badge/layer-infrastructure-blue.svg)](./index.md)
[![Cache](https://img.shields.io/badge/component-cache-orange.svg)](../api-reference/infrastructure/cache.md)
[![Production](https://img.shields.io/badge/status-production_ready-green.svg)](../deployment/production/cache-deployment.md)

**High-performance caching infrastructure with Redis and memory backends for the FLEXT Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Infrastructure Hub](./index.md) → **📄 Current**: Cache Infrastructure

### **📍 Learning Path Position**

```
[Service Patterns](./service-patterns.md) → **[Cache Infrastructure]** → [Messaging Infrastructure](./messaging-infrastructure.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Infrastructure Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Performance Optimization](../optimization/performance/caching-strategies.md)

---

## 📋 **Overview**

The FLEXT cache infrastructure provides a unified caching layer with multiple backend support, designed for high-performance distributed applications. It implements cache-aside, write-through, and write-behind patterns with automatic failover.

### **Key Features**

- **Multi-tier caching**: Memory (L1) and Redis (L2) with automatic promotion
- **Backend flexibility**: Redis, in-memory, or test engine modes
- **Pattern support**: Cache-aside, write-through, write-behind
- **Automatic failover**: Graceful degradation when Redis unavailable
- **TTL management**: Configurable time-to-live with automatic cleanup

### **Prerequisites**

- Python 3.13+ with async support
- Redis 6.0+ (for distributed caching)
- Understanding of caching patterns
- Basic knowledge of FLEXT infrastructure services

---

## 📚 **Architecture**

### **Cache Service Hierarchy**

Based on actual implementation in `/flext/src/flext/infra/cache/`:

```python
from flext.infra.cache import CacheService
from flext.infra.services.base import BaseInfraService

class CacheService(BaseInfraService):
    """Unified cache service with multiple backend support."""

    def __init__(self, backend: str = "memory", redis_url: str = None):
        super().__init__("cache")
        self._backend = backend
        self._redis_url = redis_url
        self._memory_cache = {}
        self._redis_client = None
```

### **Backend Selection**

The cache service automatically selects the appropriate backend:

1. **Redis Backend**: For distributed, persistent caching
2. **Memory Backend**: For single-instance, fast caching
3. **Test Engine**: For unit testing without external dependencies

---

## 🔧 **Implementation**

### **Basic Usage**

```python
from flext.infra.cache import CacheService

# Initialize cache service
cache = CacheService(backend="redis", redis_url="redis://localhost:6379")
await cache.connect()

# Basic operations
await cache.set("user:123", {"name": "John", "email": "john@example.com"}, ttl=3600)
user = await cache.get("user:123")
await cache.delete("user:123")

# Pattern-based operations
await cache.delete_pattern("user:*")
keys = await cache.keys("session:*")
```

### **Cache Patterns**

#### **Cache-Aside Pattern**

```python
async def get_user(user_id: str) -> User:
    # Try cache first
    cached = await cache.get(f"user:{user_id}")
    if cached:
        return User.model_validate(cached)

    # Load from database
    user = await db.get_user(user_id)

    # Cache for next time
    await cache.set(f"user:{user_id}", user.model_dump(), ttl=3600)
    return user
```

#### **Write-Through Pattern**

```python
async def update_user(user_id: str, data: dict) -> User:
    # Update cache and database atomically
    user = User.model_validate(data)

    async with db.transaction():
        await db.update_user(user_id, user)
        await cache.set(f"user:{user_id}", user.model_dump(), ttl=3600)

    return user
```

#### **Write-Behind Pattern**

```python
async def record_event(event: Event) -> None:
    # Write to cache immediately
    await cache.set(f"event:{event.id}", event.model_dump(), ttl=300)

    # Queue for eventual database write
    await queue.publish("process_events", event.id)
```

### **Advanced Features**

#### **Multi-Tier Caching**

```python
class MultiTierCache(CacheService):
    """L1 (memory) + L2 (Redis) cache implementation."""

    async def get(self, key: str) -> Any:
        # Check L1 (memory)
        if key in self._memory_cache:
            return self._memory_cache[key]

        # Check L2 (Redis)
        value = await self._redis_client.get(key)
        if value:
            # Promote to L1
            self._memory_cache[key] = value
            return value

        return None
```

#### **Cache Warming**

```python
async def warm_cache(keys: List[str]) -> None:
    """Pre-load frequently accessed data."""
    for key in keys:
        data = await load_from_source(key)
        await cache.set(key, data, ttl=7200)
```

---

## 🏭 **Production Deployment**

### **Redis Configuration**

```yaml
# config/cache.yaml
cache:
  backend: redis
  redis:
    url: redis://redis-cluster:6379
    max_connections: 100
    socket_keepalive: true
    socket_keepalive_options:
      TCP_KEEPIDLE: 120
      TCP_KEEPINTVL: 30
      TCP_KEEPCNT: 3
  memory:
    max_size: 1000
    ttl_check_interval: 60
```

### **High Availability Setup**

```python
# Redis Sentinel configuration
cache = CacheService(
    backend="redis",
    redis_url="redis://sentinel-1:26379,sentinel-2:26379,sentinel-3:26379",
    redis_options={
        "service_name": "mymaster",
        "sentinel_kwargs": {"password": "sentinel_pass"}
    }
)
```

### **Monitoring**

```python
# Cache metrics
metrics = await cache.get_metrics()
print(f"Hit rate: {metrics.hit_rate:.2%}")
print(f"Memory usage: {metrics.memory_usage_mb:.2f} MB")
print(f"Evictions: {metrics.evictions}")
```

---

## 🧪 **Testing**

### **Unit Testing with Test Engine**

```python
import pytest
from flext.infra.cache import CacheService

@pytest.fixture
async def cache():
    cache = CacheService(use_test_engine=True)
    await cache.connect()
    yield cache
    await cache.disconnect()

async def test_cache_operations(cache):
    await cache.set("key", "value")
    assert await cache.get("key") == "value"

    await cache.delete("key")
    assert await cache.get("key") is None
```

### **Integration Testing**

```python
@pytest.mark.integration
async def test_redis_failover():
    cache = CacheService(backend="redis", redis_url="redis://localhost:6379")

    # Test normal operation
    await cache.set("test", "value")

    # Simulate Redis failure
    await cache._redis_client.close()

    # Should fallback gracefully
    result = await cache.get("test")  # Returns None, doesn't crash
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Service Patterns](./service-patterns.md) - Understanding base infrastructure services
- [Redis Installation](../getting-started/setup/redis-setup.md) - Setting up Redis

### **Next Steps**

- [Performance Tuning](../optimization/performance/cache-tuning.md) - Optimizing cache performance
- [Monitoring Setup](../deployment/monitoring/cache-metrics.md) - Cache monitoring

### **Related Topics**

- [Database Infrastructure](./database-infrastructure.md) - Persistent storage patterns
- [Session Management](../guides/authentication/session-management.md) - Using cache for sessions

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Redis Connection Failures**

```python
# Issue: Cannot connect to Redis
# Solution: Check connection and add retry logic
cache = CacheService(
    backend="redis",
    redis_url="redis://localhost:6379",
    connection_retry_attempts=3,
    connection_retry_delay=1.0
)
```

#### **Memory Exhaustion**

```python
# Issue: Memory cache growing unbounded
# Solution: Set size limits and TTL
cache = CacheService(
    backend="memory",
    max_memory_mb=100,
    default_ttl=3600,
    eviction_policy="lru"
)
```

#### **Cache Stampede**

```python
# Issue: Multiple requests rebuilding same cache entry
# Solution: Use cache locks
async def get_with_lock(key: str):
    lock_key = f"lock:{key}"
    if await cache.set_nx(lock_key, "1", ttl=10):
        try:
            value = await expensive_operation()
            await cache.set(key, value)
            return value
        finally:
            await cache.delete(lock_key)
    else:
        # Wait for other process to populate cache
        await asyncio.sleep(0.1)
        return await cache.get(key)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Infrastructure Hub](./index.md) - Infrastructure architecture and service patterns understanding
- [Service Patterns](./service-patterns.md) - Base service patterns and configuration needed

### **Next Steps**

- [Messaging Infrastructure](./messaging-infrastructure.md) - Implement message queuing alongside caching
- [Performance Optimization](../optimization/performance/index.md) - Apply caching strategies for optimal performance

### **Related Topics**

- [Database Infrastructure](../guides/oracle/database-complete-guide.md) - Database caching and connection pooling
- [Development Testing](../development/testing/index.md) - Testing strategies for cache infrastructure
- [Production Deployment](../deployment/index.md) - Production configuration and monitoring for cache systems

---

**📂 Hub**: [Infrastructure Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
