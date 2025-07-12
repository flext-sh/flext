# FLX Unified Architecture Migration Guide

## Overview

This guide helps developers migrate from the old FLX implementations to the new unified, consolidated architecture. The new architecture eliminates code duplication, improves performance, and provides production-ready engines while maintaining backward compatibility.

## Table of Contents

1. [Quick Migration Checklist](#quick-migration-checklist)
2. [Logging System Migration](#logging-system-migration)
3. [Cache System Migration](#cache-system-migration)
4. [Adapter Manager Migration](#adapter-manager-migration)
5. [Production Engines Migration](#production-engines-migration)
6. [Breaking Changes and Compatibility](#breaking-changes-and-compatibility)
7. [Performance Optimization Patterns](#performance-optimization-patterns)
8. [Complete Migration Examples](#complete-migration-examples)

## Quick Migration Checklist

### ✅ High Priority (Breaking Changes)

- [ ] Update logging calls that use `extra=` parameter
- [ ] Migrate from deprecated managers to `UnifiedAdapterManager`
- [ ] Update cache imports to use consolidated `CacheService`
- [ ] Switch to production engines for production deployments

### ✅ Medium Priority (Deprecation Warnings)

- [ ] Update import statements to use new unified modules
- [ ] Replace deprecated logger instances with new `FlxStandardLoggingService`
- [ ] Migrate custom cache implementations to unified patterns

### ✅ Low Priority (Optimization)

- [ ] Adopt new production engine configurations
- [ ] Update tests to use new test engines
- [ ] Implement new observability patterns

## Logging System Migration

### Old Pattern (DEPRECATED)

```python
# Multiple different logging implementations
from flx.infra.observability.logging import logger
from flx.infra.utils.logging import get_logger
from flx.infra.services.logging import FlxLogger

# Using extra parameter (causes MyPy errors)
logger.info("User created", extra={"user_id": 123, "email": "user@example.com"})
```

### New Pattern (RECOMMENDED)

```python
# Single unified logging service
from flx.infra.services.logging import FlxStandardLoggingService
from flx.core.logging_interface import LoggerProtocol

# Initialize logging service
logging_service = FlxStandardLoggingService()
logger = logging_service.get_logger("my_module")

# Use format strings instead of extra parameter
logger.info("User created - User ID: %s, Email: %s", 123, "user@example.com")

# For structured logging, use context
with logging_service.log_context(operation="user_creation"):
    logger.info("Operation started")
    # ... business logic ...
    logger.info("Operation completed successfully")
```

### Production Logging Configuration

```python
# For production deployments
from flx.infra.logging.production_engine import LoggingProductionEngine

# Initialize with production settings
logging_engine = LoggingProductionEngine(
    level="INFO",
    format="json",  # Structured JSON logging
    enable_correlation_id=True,
    enable_pii_filtering=True,
    buffer_size=1000,  # Async buffering
    flush_interval=5.0
)

logger = logging_engine.get_logger("production_app")
```

## Cache System Migration

### Old Pattern (DEPRECATED)

```python
# Multiple cache implementations
from flx.infra.cache.backends import RedisBackend
from flx.infra.cache.base import CacheBase

# Direct backend usage
cache = RedisBackend(url="redis://localhost:6379")
```

### New Pattern (RECOMMENDED)

```python
# Unified cache service
from flx.infra.cache.cache_service import CacheService

# For development/testing
cache_service = CacheService(
    backend="memory",  # In-memory cache
    ttl=300
)

# For production
from flx.infra.cache.production_engine import CacheProductionEngine

cache_engine = CacheProductionEngine(
    backend="redis",
    cluster_nodes=["redis1:6379", "redis2:6379", "redis3:6379"],
    enable_circuit_breaker=True,
    enable_metrics=True,
    ttl=300
)

# Consistent API across all implementations
await cache_service.set("key", "value")
value = await cache_service.get("key")
await cache_service.delete("key")
```

### Advanced Cache Patterns

```python
# Batch operations
await cache_service.set_many({"key1": "value1", "key2": "value2"})
values = await cache_service.get_many(["key1", "key2"])

# Atomic operations
await cache_service.increment("counter", delta=1)
new_value = await cache_service.decrement("counter", delta=1)

# Conditional operations
success = await cache_service.set_if_not_exists("lock_key", "lock_value")
```

## Adapter Manager Migration

### Old Pattern (DEPRECATED)

```python
# Multiple manager implementations
from flx.infra.adapters.manager import FlxAdapterManager
from flx.infra.messaging.adapter_manager import FlxMessagingAdapterManager

# Separate managers for different concerns
adapter_manager = FlxAdapterManager()
messaging_manager = FlxMessagingAdapterManager()
```

### New Pattern (RECOMMENDED)

```python
# Single unified manager
from flx.infra.adapters import UnifiedAdapterManager

# All functionality in one manager
manager = UnifiedAdapterManager(
    enable_messaging_features=True,
    enable_batch_operations=True,
    registry_capacity=1000
)

# Register adapters
manager.register("cache", cache_adapter)
manager.register("database", database_adapter)

# Lifecycle management
await manager.start_all()
# ... application runs ...
await manager.stop_all()
```

### Batch Operations

```python
# Efficient batch adapter operations
adapters = ["cache", "database", "http_client"]
results = await manager.start_batch(adapters)

# Check health of all adapters
health_status = await manager.health_check_all()
```

## Production Engines Migration

### HTTP Client Migration

#### Old Pattern

```python
# Direct aiohttp usage
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get("https://api.example.com/data") as response:
        data = await response.json()
```

#### New Pattern

```python
# Production HTTP engine with resilience patterns
from flx.infra.http.production_engine import HttpProductionEngine

http_engine = HttpProductionEngine(
    timeout=30.0,
    max_retries=3,
    circuit_breaker_threshold=5,
    pool_size=100,
    enable_ssl_verification=True
)

# Built-in retry and circuit breaking
response = await http_engine.get("https://api.example.com/data")
data = response.json()
```

### Database Migration

#### Old Pattern

```python
# Direct SQLAlchemy usage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///app.db")
Session = sessionmaker(bind=engine)
```

#### New Pattern

```python
# Production database engine
from flx.infra.database.engine import DatabaseEngine

db_engine = DatabaseEngine(
    url="postgresql://user:pass@localhost/db",
    pool_size=20,
    max_overflow=30,
    enable_connection_pooling=True,
    enable_health_checks=True
)

# Built-in operations with error handling
record = await db_engine.get_by_id("users", user_id)
success = await db_engine.save_record("users", user_data)
```

## Breaking Changes and Compatibility

### Breaking Changes

1. **Logging `extra=` parameter**: No longer supported in `FlxLogger.info()`

   ```python
   # BROKEN
   logger.info("Message", extra={"key": "value"})

   # FIXED
   logger.info("Message - Key: %s", "value")
   ```

2. **Cache backend direct imports**: Use unified service instead

   ```python
   # BROKEN
   from flx.infra.cache.backends import RedisBackend

   # FIXED
   from flx.infra.cache.cache_service import CacheService
   ```

3. **Multiple manager classes**: Use unified manager

   ```python
   # BROKEN
   from flx.infra.messaging.adapter_manager import FlxMessagingAdapterManager

   # FIXED
   from flx.infra.adapters import UnifiedAdapterManager
   ```

### Backward Compatibility

The following deprecated patterns still work but will issue warnings:

```python
# These imports work but are deprecated
from flx.infra.adapters.manager import FlxAdapterManager  # Warning issued
from flx.infra.cache.base import CacheBase  # Warning issued

# Migration path provided in warning messages
```

## Performance Optimization Patterns

### Connection Pooling

```python
# HTTP connection pooling
from flx.infra.http.production_engine import HttpProductionEngine

http_engine = HttpProductionEngine(
    pool_size=100,           # Connection pool size
    pool_maxsize=200,        # Maximum pool size
    pool_block=False,        # Non-blocking pool
    keepalive_timeout=30     # Keep connections alive
)
```

### Database Optimization

```python
# Database connection pooling and optimization
from flx.infra.database.engine import DatabaseEngine

db_engine = DatabaseEngine(
    url="postgresql://user:pass@localhost/db",
    pool_size=20,              # Base pool size
    max_overflow=30,           # Additional connections
    pool_timeout=30,           # Connection timeout
    pool_recycle=3600,         # Recycle connections hourly
    enable_connection_pooling=True
)
```

### Cache Optimization

```python
# Redis cluster with performance optimization
from flx.infra.cache.production_engine import CacheProductionEngine

cache_engine = CacheProductionEngine(
    backend="redis",
    cluster_nodes=["node1:6379", "node2:6379", "node3:6379"],
    connection_pool_size=50,   # Connection pooling
    retry_on_timeout=True,     # Automatic retry
    socket_keepalive=True,     # Keep sockets alive
    socket_keepalive_options={
        'TCP_KEEPINTVL': 1,
        'TCP_KEEPCNT': 3,
        'TCP_KEEPIDLE': 1,
    }
)
```

## Complete Migration Examples

### Example 1: Simple Web API Migration

#### Before (Old Pattern)

```python
# old_api.py
from flx.infra.cache.backends import RedisBackend
from flx.infra.adapters.manager import FlxAdapterManager
from flx.core.logging import get_logger

logger = get_logger(__name__)
cache = RedisBackend(url="redis://localhost:6379")
manager = FlxAdapterManager()

async def create_user(user_data: dict):
    logger.info("Creating user", extra={"user_id": user_data["id"]})
    # ... business logic ...
    await cache.set(f"user:{user_data['id']}", user_data)
    return user_data
```

#### After (New Pattern)

```python
# new_api.py
from flx.infra.cache.production_engine import CacheProductionEngine
from flx.infra.adapters import UnifiedAdapterManager
from flx.infra.services.logging import FlxStandardLoggingService

# Initialize services
logging_service = FlxStandardLoggingService()
logger = logging_service.get_logger(__name__)

cache_engine = CacheProductionEngine(
    backend="redis",
    cluster_nodes=["redis1:6379", "redis2:6379"],
    enable_circuit_breaker=True
)

manager = UnifiedAdapterManager()

async def create_user(user_data: dict):
    logger.info("Creating user - User ID: %s", user_data["id"])

    # Use production cache with automatic failover
    await cache_engine.set(f"user:{user_data['id']}", user_data)
    return user_data
```

### Example 2: Complete Application Migration

#### Before (Old Pattern)

```python
# old_app.py
from flx.infra.cache.base import CacheBase
from flx.infra.adapters.manager import FlxAdapterManager
from flx.infra.messaging.adapter_manager import FlxMessagingAdapterManager
from flx.core.logging import FlxLogger

class OldApplication:
    def __init__(self):
        self.cache = CacheBase()
        self.adapter_manager = FlxAdapterManager()
        self.messaging_manager = FlxMessagingAdapterManager()
        self.logger = FlxLogger()

    async def start(self):
        self.logger.info("Starting application", extra={"app": "old_app"})
        await self.adapter_manager.start_all()
        await self.messaging_manager.start_all()
```

#### After (New Pattern)

```python
# new_app.py
from flx.infra.cache.cache_service import CacheService
from flx.infra.adapters import UnifiedAdapterManager
from flx.infra.services.logging import FlxStandardLoggingService
from flx.infra.http.production_engine import HttpProductionEngine
from flx.infra.database.engine import DatabaseEngine

class NewApplication:
    def __init__(self):
        # Unified services
        self.logging_service = FlxStandardLoggingService()
        self.logger = self.logging_service.get_logger(__name__)

        # Production engines
        self.cache_service = CacheService(backend="redis")
        self.http_engine = HttpProductionEngine()
        self.db_engine = DatabaseEngine(url="postgresql://localhost/app")

        # Unified manager
        self.manager = UnifiedAdapterManager(
            enable_messaging_features=True,
            enable_batch_operations=True
        )

    async def start(self):
        self.logger.info("Starting application - App: %s", "new_app")

        # Register all engines with the manager
        self.manager.register("cache", self.cache_service)
        self.manager.register("http", self.http_engine)
        self.manager.register("database", self.db_engine)

        # Start all services efficiently
        await self.manager.start_all()

        # Verify health
        health = await self.manager.health_check_all()
        self.logger.info("Application health check - Status: %s", health)
```

## Validation and Testing

### Test Your Migration

1. **Run MyPy validation**:

   ```bash
   python -m mypy src/flx/ --config-file mypy.ini
   ```

2. **Check for deprecation warnings**:

   ```python
   import warnings
   warnings.simplefilter("always", DeprecationWarning)
   # Run your application code
   ```

3. **Performance benchmarking**:

   ```python
   from flx.testing.engines.comprehensive_test_engine import ComprehensiveTestEngine

   test_engine = ComprehensiveTestEngine()
   await test_engine.benchmark_cache_performance()
   await test_engine.benchmark_http_performance()
   ```

### Migration Validation Checklist

- [ ] All `extra=` logging calls replaced with format strings
- [ ] No MyPy errors in migrated code
- [ ] Deprecation warnings addressed
- [ ] Performance tests passing
- [ ] Health checks working for all engines
- [ ] Error handling patterns implemented
- [ ] Documentation updated

## Support and Troubleshooting

### Common Issues

1. **MyPy errors with `extra=`**: Replace with format strings
2. **Import errors**: Update to use unified modules
3. **Performance degradation**: Ensure production engines are used
4. **Connection issues**: Verify engine configurations

### Getting Help

- Check the [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- Review [Infrastructure Architecture](INFRASTRUCTURE_ARCHITECTURE.md)
- See [Testing Guide](TESTING_HEXAGONAL_ARCHITECTURE.md)

### Migration Timeline

**Phase 1 (Immediate)**: Fix breaking changes and MyPy errors
**Phase 2 (1-2 weeks)**: Migrate to unified services
**Phase 3 (1 month)**: Adopt production engines and optimization patterns

---

_This migration guide is part of the FLX unified architecture initiative. For questions or issues, refer to the project documentation or create an issue in the repository._
