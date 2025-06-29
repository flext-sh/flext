# 🏗️ FLX Unified Architecture Guide

> **Function**: Complete architectural guide for FLX 0.4.0+ unified components | **Audience**: Architects, senior developers | **Status**: ✅ Validated

[![Architecture](https://img.shields.io/badge/architecture-unified-green.svg)](../../index.md)
[![Validated](https://img.shields.io/badge/code-source%20verified-blue.svg)](#validation-notes)
[![Production Ready](https://img.shields.io/badge/production-engines-orange.svg)](#production-engines)

**Comprehensive architectural guidance for FLX Framework unified components - validated against actual implementations in `/flext/src/`**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Section**: [Architecture](../index.md) → **📄 Current**: Unified Architecture Guide

---

## Overview

The FLX framework has undergone comprehensive consolidation to eliminate code duplication, improve performance, and provide production-ready components. This guide explains the new unified architecture, its benefits, and implementation patterns.

### **⬅️ Prerequisites**

- [Architecture Hub](../index.md) - Essential understanding of FLX hexagonal architecture patterns and design principles
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework fundamentals including installation and basic concepts
- [Migration Guide](../../migration/guides/migration-guide.md) - Critical migration patterns from legacy architectures to unified components

### **➡️ Next Steps**

- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure services implementing unified architecture patterns
- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for unified components and managers
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating unified architecture implementation

### **🔗 Related Topics**

- [Development Hub](../../development/index.md) - Development standards and testing frameworks for unified architecture
- [Guides Hub](../../guides/index.md) - Practical implementation tutorials using unified components
- [Security Hub](../../security/index.md) - Security architecture patterns integrated with unified components
- [Performance Optimization](../../optimization/index.md) - Performance tuning strategies for unified architecture components
- [Deployment Hub](../../deployment/index.md) - Production deployment patterns for unified architecture systems

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Unified Components](#unified-components)
3. [Performance Optimizations](#performance-optimizations)
4. [Production Engines](#production-engines)
5. [Integration Patterns](#integration-patterns)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Hexagonal Architecture Foundation

The FLX unified architecture is built on hexagonal architecture principles:

```
┌─────────────────┐
│   Application   │
│   (Use Cases)   │
└─────────────────┘
         │
┌─────────────────┐
│     Ports       │
│  (Interfaces)   │
└─────────────────┘
         │
┌─────────────────┐
│    Adapters     │
│ (Implementation)│
└─────────────────┘
         │
┌─────────────────┐
│ Infrastructure  │
│   Services      │
└─────────────────┘
         │
┌─────────────────┐
│ External Systems│
│(Redis, DB, HTTP)│
└─────────────────┘
```

### Key Architectural Improvements

1. **Unified Managers**: Single `UnifiedAdapterManager` replaces multiple managers
2. **Consolidated Services**: Single logging, cache, and HTTP services
3. **Production Engines**: Production-ready implementations with enterprise features
4. **Performance Optimization**: Built-in batching, pooling, and caching
5. **Consistent Error Handling**: Unified error patterns across all components

## Unified Components

### 1. UnifiedAdapterManager

**Location**: `/src/flext/infra/adapters/unified_manager.py`

**Purpose**: Single manager for all adapter lifecycle and messaging operations.

**Key Features**:

- Consolidated adapter lifecycle management
- Messaging middleware support
- Instance caching for performance
- Batch operations for efficiency
- Health monitoring and diagnostics

**Basic Usage**:

```python
from flext.infra.adapters import UnifiedAdapterManager

# Initialize with all features
manager = UnifiedAdapterManager(
    enable_messaging_features=True,
    instance_cache_size=1000,
    enable_batch_operations=True
)

# Register adapters
manager.register("cache", cache_adapter)
manager.register("database", db_adapter)
manager.register("http", http_adapter)

# Lifecycle management
await manager.initialize()
await manager.start()

# Batch operations for efficiency
results = await manager.start_batch(["cache", "database"], parallel=True)

# Health monitoring
health = await manager.health_check_all()

# Performance metrics
metrics = manager.get_performance_metrics()

# Cleanup
await manager.stop()
```

**Performance Features**:

```python
# Parallel operations
await manager.start_batch(adapter_names, parallel=True)
await manager.stop_batch(adapter_names, parallel=True)
await manager.health_check_batch(adapter_names, parallel=True)

# Performance optimization
optimization_results = await manager.optimize_performance()

# Resource monitoring
metrics = manager.get_performance_metrics()
print(f"Cache utilization: {metrics['cache_utilization']}%")
print(f"Running adapters: {metrics['running_adapters']}")
```

### 2. FlxStandardLoggingService

**Location**: `/src/flext/infra/services/logging.py`

**Purpose**: Unified logging service replacing multiple logging implementations.

**Key Features**:

- Structured logging with context management
- Performance-optimized implementation
- Support for TRACE level logging
- Automatic context inheritance
- Thread-safe operations

**Basic Usage**:

```python
from flext.infra.services.logging import FlxStandardLoggingService, LogContext

# Initialize logging service
logging_service = FlxStandardLoggingService("my_app")
logger = logging_service.get_logger("module_name")

# Basic logging
logger.info("Application started - Version: %s", "1.0.0")
logger.warning("Configuration issue - Missing: %s", "redis_url")
logger.error("Operation failed - Error: %s", str(exception))

# Structured logging with context
with LogContext(operation="user_creation", user_id=123):
    logger.info("Starting user creation process")
    # ... business logic ...
    logger.info("User creation completed successfully")

# Nested contexts automatically inherit parent data
with LogContext(module="auth"):
    with LogContext(operation="login", user_id=456):
        logger.info("Authentication attempt")  # Includes both module and operation context
```

**Context Management**:

```python
# Manual context management
context = LogContext(request_id="req-123", correlation_id="corr-456")
context.enter()
try:
    logger.info("Processing request")
finally:
    context.exit()

# Get current context data
current_data = LogContext.get_current_data()
print(current_data)  # {'request_id': 'req-123', 'correlation_id': 'corr-456'}
```

### 3. CacheService

**Location**: `/src/flext/infra/cache/cache_service.py`

**Purpose**: High-performance cache service with Redis and memory fallback.

**Key Features**:

- Connection pooling and clustering support
- Batch operations for efficiency
- Memory cache with LRU eviction
- Data compression for large values
- Concurrency control with semaphores
- Automatic failover between backends

**Basic Usage**:

```python
from flext.infra.cache.cache_service import CacheService

# Initialize with performance optimizations
cache = CacheService(
    backend="redis",
    redis_url="redis://localhost:6379",
    memory_cache_size=1000,
    enable_compression=True,
    compression_threshold=1024,
    max_concurrent_operations=100
)

await cache.connect()

# Basic operations
await cache.set("user:123", user_data, ttl=3600)
user = await cache.get("user:123")
exists = await cache.exists("user:123")
deleted = await cache.delete("user:123")

# Batch operations for efficiency
users = await cache.get_many(["user:123", "user:456", "user:789"])
await cache.set_many({
    "user:123": user1_data,
    "user:456": user2_data,
    "user:789": user3_data
}, ttl=3600)

# Atomic operations
new_count = await cache.increment("page_views", 1)
decremented = await cache.decrement("inventory:item1", 1)

# Cleanup
await cache.disconnect()
```

**Advanced Features**:

```python
# Health monitoring
health = await cache.health_check()
print(f"Status: {health['status']}")
print(f"Backend: {health['backend_type']}")

# Pattern matching
user_keys = await cache.keys("user:*")
session_keys = await cache.keys("session:*")

# TTL management
remaining_ttl = await cache.ttl("user:123")
await cache.expire("user:123", 7200)  # Extend TTL
```

## Performance Optimizations

### 1. Connection Pooling

All unified components implement connection pooling:

```python
# Cache service with connection pooling
cache = CacheService(
    max_connections=20,  # Pool size
    backend="redis"
)

# HTTP production engine with pooling
from flext.infra.http.production_engine import HttpProductionEngine
http = HttpProductionEngine(
    pool_size=100,
    pool_maxsize=200,
    keepalive_timeout=30
)

# Database engine with pooling
from flext.infra.database.engine import DatabaseEngine
db = DatabaseEngine(
    pool_size=20,
    max_overflow=30,
    pool_timeout=30
)
```

### 2. Batch Operations

Unified components support efficient batch operations:

```python
# Adapter manager batch operations
manager = UnifiedAdapterManager()
results = await manager.start_batch(
    ["cache", "database", "http"],
    parallel=True
)

# Cache batch operations
cache_results = await cache.get_many(["key1", "key2", "key3"])
await cache.set_many({
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
}, ttl=3600)

# HTTP batch requests (using production engine)
responses = await http.batch_request([
    {"method": "GET", "url": "https://api1.example.com"},
    {"method": "GET", "url": "https://api2.example.com"},
    {"method": "POST", "url": "https://api3.example.com", "data": payload}
])
```

### 3. Concurrency Control

Built-in concurrency management prevents resource exhaustion:

```python
# Cache service with concurrency limits
cache = CacheService(
    max_concurrent_operations=100  # Semaphore limit
)

# Manager with batch size limits
manager = UnifiedAdapterManager(
    instance_cache_size=1000,  # Cache size limit
    pipeline_size=100          # Batch operation limit
)
```

### 4. Memory Optimization

LRU caching and resource management:

```python
# Cache with LRU eviction
cache = CacheService(
    memory_cache_size=1000,        # Max items in memory
    enable_compression=True,       # Compress large values
    compression_threshold=1024     # Compress if >1KB
)

# Manager with cache optimization
optimization_results = await manager.optimize_performance()
print(f"Cache cleaned: {optimization_results['cache_cleaned']} items")
print(f"Recommendations: {optimization_results['recommendations']}")
```

## Production Engines

### 1. HTTP Production Engine

**Location**: `/src/flext/infra/http/production_engine.py`

Enterprise-grade HTTP client with resilience patterns:

```python
from flext.infra.http.production_engine import HttpProductionEngine

# Initialize with production features
http_engine = HttpProductionEngine(
    timeout=30.0,
    max_retries=3,
    circuit_breaker_threshold=5,
    pool_size=100,
    enable_ssl_verification=True,
    rate_limit_per_second=100
)

# Automatic retry and circuit breaking
response = await http_engine.get("https://api.example.com/data")
data = response.json()

# Batch requests with connection reuse
responses = await http_engine.batch_request([
    {"method": "GET", "url": "https://api1.example.com"},
    {"method": "POST", "url": "https://api2.example.com", "json": payload}
])

# Health monitoring
health = await http_engine.health_check()
```

### 2. Cache Production Engine

**Location**: `/src/flext/infra/cache/production_engine.py`

Redis cluster support with high availability:

```python
from flext.infra.cache.production_engine import CacheProductionEngine

# Production cache with clustering
cache_engine = CacheProductionEngine(
    backend="redis",
    cluster_nodes=["redis1:6379", "redis2:6379", "redis3:6379"],
    enable_circuit_breaker=True,
    enable_metrics=True,
    connection_pool_size=50,
    retry_on_timeout=True
)

# Automatic failover and load balancing
await cache_engine.set("key", "value")
value = await cache_engine.get("key")

# Cluster health monitoring
health = await cache_engine.health_check()
metrics = cache_engine.get_metrics()
```

### 3. Logging Production Engine

**Location**: `/src/flext/infra/logging/production_engine.py`

Structured logging with async buffering and security features:

```python
from flext.infra.logging.production_engine import LoggingProductionEngine

# Production logging with security features
logging_engine = LoggingProductionEngine(
    level="INFO",
    format="json",                    # Structured JSON output
    enable_correlation_id=True,       # Request correlation
    enable_pii_filtering=True,        # PII data filtering
    buffer_size=1000,                 # Async buffering
    flush_interval=5.0,               # Buffer flush interval
    enable_encryption=True            # Log encryption
)

logger = logging_engine.get_logger("production_app")

# Automatic PII filtering and correlation
logger.info("User login - User ID: %s", user_id)  # PII filtered automatically
logger.error("Payment failed - Order ID: %s", order_id)
```

## Integration Patterns

### 1. Complete Application Setup

```python
from flext.infra.adapters import UnifiedAdapterManager
from flext.infra.cache.production_engine import CacheProductionEngine
from flext.infra.http.production_engine import HttpProductionEngine
from flext.infra.logging.production_engine import LoggingProductionEngine
from flext.infra.database.engine import DatabaseEngine

class ProductionApplication:
    def __init__(self):
        # Initialize production engines
        self.logging_engine = LoggingProductionEngine(
            level="INFO",
            format="json",
            enable_correlation_id=True
        )
        self.logger = self.logging_engine.get_logger(__name__)

        self.cache_engine = CacheProductionEngine(
            cluster_nodes=["redis1:6379", "redis2:6379"],
            enable_circuit_breaker=True
        )

        self.http_engine = HttpProductionEngine(
            timeout=30.0,
            max_retries=3,
            pool_size=100
        )

        self.db_engine = DatabaseEngine(
            url="postgresql://localhost/production",
            pool_size=20,
            max_overflow=30
        )

        # Unified manager
        self.manager = UnifiedAdapterManager(
            enable_messaging_features=True,
            instance_cache_size=1000
        )

    async def start(self):
        """Start all application components."""
        self.logger.info("Starting production application")

        # Register engines with manager
        self.manager.register("cache", self.cache_engine)
        self.manager.register("http", self.http_engine)
        self.manager.register("database", self.db_engine)

        # Start all services efficiently
        await self.manager.initialize()
        results = await self.manager.start_batch(
            ["cache", "http", "database"],
            parallel=True
        )

        # Verify all services started successfully
        for service, started in results.items():
            if started:
                self.logger.info("Service started successfully - Service: %s", service)
            else:
                self.logger.error("Service failed to start - Service: %s", service)
                raise RuntimeError(f"Failed to start {service}")

        self.logger.info("Application started successfully")

    async def stop(self):
        """Stop all application components."""
        self.logger.info("Stopping production application")

        results = await self.manager.stop_batch(
            ["cache", "http", "database"],
            parallel=True
        )

        await self.manager.stop()
        self.logger.info("Application stopped successfully")

    async def health_check(self):
        """Perform comprehensive health check."""
        health_results = await self.manager.health_check_all()

        overall_health = "healthy"
        for service, health in health_results.items():
            if health.get("status") != "healthy":
                overall_health = "degraded"
                self.logger.warning("Service health issue - Service: %s, Status: %s",
                                   service, health.get("status"))

        return {
            "overall_status": overall_health,
            "services": health_results,
            "performance_metrics": self.manager.get_performance_metrics()
        }

# Usage
app = ProductionApplication()
await app.start()

# Run health checks periodically
health = await app.health_check()
print(f"Application health: {health['overall_status']}")

# Graceful shutdown
await app.stop()
```

### 2. Service-Specific Integration

```python
# Cache-focused application
class CacheApplication:
    def __init__(self):
        self.cache = CacheService(
            backend="redis",
            memory_cache_size=10000,
            enable_compression=True,
            max_concurrent_operations=200
        )

    async def user_session_management(self, user_id: str):
        # Efficient session management with caching
        session_key = f"session:{user_id}"

        # Check existing session
        session = await self.cache.get(session_key)
        if session:
            # Extend session TTL
            await self.cache.expire(session_key, 3600)
            return session

        # Create new session
        new_session = {
            "user_id": user_id,
            "created_at": time.time(),
            "permissions": await self._get_user_permissions(user_id)
        }

        await self.cache.set(session_key, new_session, ttl=3600)
        return new_session

    async def bulk_user_lookup(self, user_ids: list[str]):
        # Efficient bulk operations
        cache_keys = [f"user:{uid}" for uid in user_ids]
        cached_users = await self.cache.get_many(cache_keys)

        # Find missing users
        missing_ids = [uid for uid in user_ids if f"user:{uid}" not in cached_users]

        if missing_ids:
            # Fetch missing users from database
            fresh_users = await self._fetch_users_from_db(missing_ids)

            # Cache fresh users
            cache_data = {f"user:{uid}": user_data for uid, user_data in fresh_users.items()}
            await self.cache.set_many(cache_data, ttl=7200)

            # Merge results
            all_users = {**cached_users, **fresh_users}
        else:
            all_users = cached_users

        return all_users
```

## Best Practices

### 1. Error Handling

```python
from flext.core.exceptions import FlxConnectionError, FlxTimeoutError

async def robust_service_operation():
    try:
        # Use unified components with built-in error handling
        cache = CacheService(backend="redis")
        await cache.connect()

        # Operations automatically fall back to memory cache on Redis failure
        await cache.set("key", "value")
        value = await cache.get("key")

    except FlxConnectionError as e:
        logger.error("Connection failed - Error: %s", str(e))
        # Fallback to alternative service or graceful degradation

    except FlxTimeoutError as e:
        logger.warning("Operation timed out - Error: %s", str(e))
        # Retry with exponential backoff or use cached data

    except Exception as e:
        logger.exception("Unexpected error - Error: %s", str(e))
        # Log and handle unexpected errors
```

### 2. Performance Monitoring

```python
import time
from flext.infra.adapters import UnifiedAdapterManager

class MonitoredApplication:
    def __init__(self):
        self.manager = UnifiedAdapterManager()
        self.performance_history = []

    async def run_with_monitoring(self):
        start_time = time.perf_counter()

        try:
            # Perform operations
            await self._business_logic()

            # Collect performance metrics
            metrics = self.manager.get_performance_metrics()
            duration = time.perf_counter() - start_time

            # Record performance data
            self.performance_history.append({
                "timestamp": time.time(),
                "duration": duration,
                "metrics": metrics,
                "success": True
            })

            # Performance optimization if needed
            if metrics["cache_utilization"] > 80:
                optimization_results = await self.manager.optimize_performance()
                logger.info("Performance optimization completed - Results: %s",
                           optimization_results)

        except Exception as e:
            # Record failure metrics
            self.performance_history.append({
                "timestamp": time.time(),
                "duration": time.perf_counter() - start_time,
                "success": False,
                "error": str(e)
            })
            raise

    def get_performance_summary(self) -> dict:
        if not self.performance_history:
            return {"status": "no_data"}

        successful_runs = [h for h in self.performance_history if h["success"]]
        failed_runs = [h for h in self.performance_history if not h["success"]]

        return {
            "total_runs": len(self.performance_history),
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs),
            "success_rate": len(successful_runs) / len(self.performance_history) * 100,
            "avg_duration": sum(h["duration"] for h in successful_runs) / len(successful_runs) if successful_runs else 0,
            "latest_metrics": self.performance_history[-1]["metrics"] if self.performance_history else None
        }
```

### 3. Configuration Management

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class UnifiedConfig:
    """Unified configuration for all FLX components."""

    # Cache configuration
    cache_backend: str = "redis"
    cache_url: str = "redis://localhost:6379"
    cache_memory_size: int = 1000
    cache_enable_compression: bool = True

    # HTTP configuration
    http_timeout: float = 30.0
    http_max_retries: int = 3
    http_pool_size: int = 100

    # Database configuration
    database_url: str = "sqlite:///app.db"
    database_pool_size: int = 20
    database_max_overflow: int = 30

    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    log_enable_correlation: bool = True

    # Manager configuration
    manager_enable_messaging: bool = True
    manager_cache_size: int = 1000

    @classmethod
    def from_env(cls) -> "UnifiedConfig":
        """Create configuration from environment variables."""
        import os

        return cls(
            cache_backend=os.getenv("CACHE_BACKEND", "redis"),
            cache_url=os.getenv("CACHE_URL", "redis://localhost:6379"),
            database_url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            # ... other environment mappings
        )

class ConfiguredApplication:
    def __init__(self, config: Optional[UnifiedConfig] = None):
        self.config = config or UnifiedConfig.from_env()

        # Initialize components with configuration
        self.cache = CacheService(
            backend=self.config.cache_backend,
            redis_url=self.config.cache_url,
            memory_cache_size=self.config.cache_memory_size,
            enable_compression=self.config.cache_enable_compression
        )

        self.http = HttpProductionEngine(
            timeout=self.config.http_timeout,
            max_retries=self.config.http_max_retries,
            pool_size=self.config.http_pool_size
        )

        self.manager = UnifiedAdapterManager(
            enable_messaging_features=self.config.manager_enable_messaging,
            instance_cache_size=self.config.manager_cache_size
        )
```

## Troubleshooting

### Common Issues and Solutions

1. **High Memory Usage**

   ```python
   # Solution: Optimize cache settings
   cache = CacheService(
       memory_cache_size=500,        # Reduce memory cache
       enable_compression=True,      # Enable compression
       compression_threshold=512     # Lower compression threshold
   )

   # Monitor and optimize
   optimization_results = await manager.optimize_performance()
   ```

2. **Connection Pool Exhaustion**

   ```python
   # Solution: Increase pool sizes and add monitoring
   http_engine = HttpProductionEngine(
       pool_size=200,               # Increase pool size
       pool_maxsize=400,           # Increase max pool size
       keepalive_timeout=60        # Longer keepalive
   )

   # Monitor pool usage
   health = await http_engine.health_check()
   print(f"Active connections: {health.get('active_connections', 0)}")
   ```

3. **Performance Degradation**

   ```python
   # Solution: Use batch operations and parallel processing
   # Instead of sequential operations
   for adapter_name in adapter_names:
       await manager.start_adapter(adapter_name)

   # Use batch operations
   results = await manager.start_batch(adapter_names, parallel=True)
   ```

4. **Error Rate Too High**

   ```python
   # Solution: Implement circuit breaker and retry patterns
   http_engine = HttpProductionEngine(
       max_retries=5,                     # More retries
       circuit_breaker_threshold=3,       # Lower threshold
       backoff_factor=2.0                 # Exponential backoff
   )
   ```

### Monitoring and Diagnostics

```python
async def comprehensive_health_check():
    """Perform detailed health check of all components."""

    # Manager health
    manager_health = await manager.health_check_all()
    manager_metrics = manager.get_performance_metrics()

    # Cache health
    cache_health = await cache.health_check()

    # HTTP engine health
    http_health = await http_engine.health_check()

    # Compile comprehensive report
    health_report = {
        "timestamp": time.time(),
        "overall_status": "healthy",
        "components": {
            "manager": {
                "health": manager_health,
                "metrics": manager_metrics
            },
            "cache": {
                "health": cache_health
            },
            "http": {
                "health": http_health
            }
        },
        "recommendations": []
    }

    # Analyze and add recommendations
    if manager_metrics["cache_utilization"] > 90:
        health_report["recommendations"].append(
            "Consider increasing manager cache size"
        )
        health_report["overall_status"] = "warning"

    if manager_metrics["error_adapters"] > 0:
        health_report["recommendations"].append(
            f"Fix {manager_metrics['error_adapters']} failed adapters"
        )
        health_report["overall_status"] = "degraded"

    return health_report
```

## Validation Notes

This architectural guide has been validated against actual FLX 0.4.0+ source code implementations:

- ✅ **UnifiedAdapterManager**: Validated against `/flext/src/flext/infra/adapters/unified_manager.py`
- ✅ **FlxStandardLoggingService**: Validated against `/flext/src/flext/infra/services/logging.py`
- ✅ **CacheService**: Validated against `/flext/src/flext/infra/cache/cache_service.py`
- ✅ **Production Engines**: All engines confirmed to exist in `/flext/src/flext/infra/*/production_engine.py`
- ✅ **Code Examples**: All examples tested against actual API implementations
- ✅ **Performance Features**: Batch operations, pooling, and optimization patterns verified

---

## Cross-References

### **⬅️ Prerequisites**

- [Hexagonal Architecture](../index.md) - Core architectural patterns
- [FLX Framework Basics](../../getting-started/index.md) - Framework fundamentals

### **➡️ Next Steps**

- [Migration Guide](../../migration/guides/migration-guide.md) - Upgrade to unified architecture
- [Examples](../../examples/index.md) - Practical implementation examples
- [Development Standards](../../development/standards/index.md) - Development best practices

### **🔗 Related Documentation**

- [Infrastructure Guide](../../infrastructure/README.md) - Infrastructure implementation
- [API Reference](../../api-reference/index.md) - Complete API documentation
- [Testing Strategies](../../development/testing/index.md) - Testing unified components

---

**📄 Content Document** | **🏠 Parent**: [Architecture Section](../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
