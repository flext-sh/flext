"""Example demonstrating advanced infrastructure service features.

Shows integration of error handling, resource management, and resilience patterns.
"""

import asyncio
import random
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from flx.infra.services.base import BaseInfraService
from flx.infra.services.errors import (
    ErrorCategory, ErrorContext, ErrorSeverity,
    ExponentialBackoffRetry, InfrastructureError, error_handler
)
from flx.infra.services.resources import (
    ResourceFactory, ResourcePool, ResourceValidator, resource_manager
)
from flx.infra.services.resilience import (
    CircuitBreakerConfig, BulkheadConfig, RateLimiterConfig,
    resilience_manager, circuit_breaker, rate_limited
)


# Example: Advanced Database Service with all features

class DatabaseConnection:
    """Mock database connection."""
    
    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.is_alive = True
        self.query_count = 0
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """Execute query."""
        if not self.is_alive:
            raise ConnectionError("Connection is dead")
        
        self.query_count += 1
        
        # Simulate query execution
        await asyncio.sleep(0.1)
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise ConnectionError("Query execution failed")
        
        return {"result": f"Result for: {query}", "rows": random.randint(0, 100)}
    
    async def ping(self) -> bool:
        """Check if connection is alive."""
        return self.is_alive
    
    async def close(self) -> None:
        """Close connection."""
        self.is_alive = False


class DatabaseConnectionFactory(ResourceFactory[DatabaseConnection]):
    """Factory for database connections."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._created_count = 0
    
    async def create(self) -> DatabaseConnection:
        """Create new database connection."""
        self._created_count += 1
        connection_id = f"conn_{self._created_count}"
        
        # Simulate connection establishment
        await asyncio.sleep(0.2)
        
        # Simulate occasional connection failures
        if random.random() < 0.05:  # 5% failure rate
            raise ConnectionError("Failed to establish database connection")
        
        print(f"Created database connection: {connection_id}")
        return DatabaseConnection(connection_id)
    
    async def destroy(self, resource: DatabaseConnection) -> None:
        """Destroy database connection."""
        print(f"Closing database connection: {resource.connection_id}")
        await resource.close()


class DatabaseConnectionValidator(ResourceValidator[DatabaseConnection]):
    """Validator for database connections."""
    
    async def validate(self, resource: DatabaseConnection) -> bool:
        """Validate connection is still alive."""
        try:
            return await resource.ping()
        except Exception:
            return False


class AdvancedDatabaseService(BaseInfraService):
    """Advanced database service with all infrastructure features."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("advanced_database", config)
        
        # Configuration
        self._database_url = self._config.get("database_url", "postgresql://localhost/test")
        self._pool_size = self._config.get("pool_size", 10)
        self._max_retries = self._config.get("max_retries", 3)
        
        # Resource pool
        self._connection_pool: Optional[ResourcePool[DatabaseConnection]] = None
        
        # Setup error recovery
        self._setup_error_handling()
        
        # Setup resilience
        self._setup_resilience()
    
    def _setup_error_handling(self) -> None:
        """Configure error handling."""
        # Add retry strategy for connection errors
        error_handler.register_strategy(
            ExponentialBackoffRetry(base_delay=0.5, max_delay=10.0),
            [ErrorCategory.CONNECTION, ErrorCategory.NETWORK]
        )
        
        # Add error listener for monitoring
        error_handler.add_error_listener(self._on_error)
    
    def _setup_resilience(self) -> None:
        """Configure resilience patterns."""
        # Circuit breaker for database operations
        resilience_manager.get_circuit_breaker(
            f"{self._service_name}_operations",
            CircuitBreakerConfig(
                failure_threshold=5,
                timeout=30.0,
                error_types={ConnectionError, TimeoutError}
            )
        )
        
        # Bulkhead for connection isolation
        resilience_manager.get_bulkhead(
            f"{self._service_name}_connections",
            BulkheadConfig(
                max_concurrent=self._pool_size,
                max_queue_size=20
            )
        )
        
        # Rate limiter for query operations
        resilience_manager.get_rate_limiter(
            f"{self._service_name}_queries",
            RateLimiterConfig(
                max_requests=1000,
                time_window=60.0,
                burst_size=1200
            )
        )
    
    def _on_error(self, error: InfrastructureError) -> None:
        """Handle infrastructure errors."""
        self._logger.error(
            f"Infrastructure error in {error.context.service_name}: "
            f"{error} (severity: {error.context.severity.value})"
        )
    
    # Lifecycle Implementation
    
    async def _do_initialize(self) -> None:
        """Initialize database service."""
        # Create connection pool
        factory = DatabaseConnectionFactory(self._database_url)
        validator = DatabaseConnectionValidator()
        
        self._connection_pool = ResourcePool(
            factory=factory,
            min_size=2,
            max_size=self._pool_size,
            max_idle_time=300.0,  # 5 minutes
            max_lifetime=3600.0,  # 1 hour
            validator=validator
        )
        
        # Register with resource manager
        resource_manager.register_pool(
            f"{self._service_name}_pool",
            self._connection_pool
        )
    
    async def _do_start(self) -> None:
        """Start database service."""
        # Initialize connection pool
        await self._connection_pool.initialize()
        self._logger.info(f"Database service started with pool size {self._pool_size}")
    
    async def _do_stop(self) -> None:
        """Stop database service."""
        # Pool cleanup is handled by resource manager
        pass
    
    async def _do_cleanup(self) -> None:
        """Clean up database resources."""
        # Close connection pool
        if self._connection_pool:
            await self._connection_pool.close()
    
    async def _do_connect(self) -> None:
        """Connect to database."""
        # Test connection by acquiring and releasing
        if self._test_engine:
            return
        
        async with self._connection_pool.acquire_context() as conn:
            await conn.ping()
    
    async def _do_disconnect(self) -> None:
        """Disconnect from database."""
        # No specific disconnection needed
        pass
    
    # Database Operations
    
    @circuit_breaker("database_operations")
    @rate_limited("database_queries")
    async def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute database query with full resilience."""
        if not self._connected:
            raise RuntimeError("Database service not connected")
        
        # Create error context
        context = ErrorContext(
            service_name=self._service_name,
            operation="execute_query",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONNECTION,
            max_retries=self._max_retries
        )
        
        # Define operation
        async def _execute():
            # Acquire connection from pool
            async with self._connection_pool.acquire_context(timeout=5.0) as conn:
                # Use bulkhead for isolation
                bulkhead = resilience_manager.get_bulkhead(
                    f"{self._service_name}_connections"
                )
                async with bulkhead.acquire():
                    # Record start time for adaptive timeout
                    start_time = asyncio.get_event_loop().time()
                    
                    try:
                        result = await conn.execute(query)
                        
                        # Record success for adaptive strategy
                        strategy = resilience_manager.get_adaptive_strategy(
                            self._service_name
                        )
                        response_time = asyncio.get_event_loop().time() - start_time
                        await strategy.record_result(True, response_time)
                        
                        return result
                        
                    except Exception as e:
                        # Record failure
                        strategy = resilience_manager.get_adaptive_strategy(
                            self._service_name
                        )
                        response_time = asyncio.get_event_loop().time() - start_time
                        await strategy.record_result(False, response_time)
                        raise
        
        # Execute with error handling
        try:
            return await _execute()
        except Exception as e:
            # Handle with error recovery
            return await error_handler.handle_error(
                e, context, _execute
            )
    
    async def execute_transaction(
        self,
        queries: list[str]
    ) -> list[Dict[str, Any]]:
        """Execute multiple queries in a transaction."""
        if not self._connected:
            raise RuntimeError("Database service not connected")
        
        results = []
        
        # Acquire connection for entire transaction
        async with self._connection_pool.acquire_context(timeout=10.0) as conn:
            try:
                for query in queries:
                    result = await conn.execute(query)
                    results.append(result)
                
                # Simulate commit
                await asyncio.sleep(0.05)
                return results
                
            except Exception as e:
                # Simulate rollback
                await asyncio.sleep(0.05)
                raise InfrastructureError(
                    "Transaction failed",
                    ErrorContext(
                        service_name=self._service_name,
                        operation="execute_transaction",
                        severity=ErrorSeverity.HIGH,
                        category=ErrorCategory.CONNECTION
                    ),
                    cause=e
                )
    
    # Health Check Implementation
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform database-specific health check."""
        details = await super()._perform_health_check()
        
        # Add pool metrics
        if self._connection_pool:
            pool_metrics = self._connection_pool.get_metrics()
            details["pool"] = pool_metrics
        
        # Add resilience metrics
        resilience_stats = resilience_manager.get_all_stats()
        details["resilience"] = {
            "circuit_breaker": resilience_stats["circuit_breakers"].get(
                "database_operations", {}
            ),
            "rate_limiter": resilience_stats["rate_limiters"].get(
                "database_queries", {}
            )
        }
        
        # Test database connectivity
        try:
            await self.execute_query("SELECT 1")
            details["connectivity"] = "healthy"
        except Exception as e:
            details["connectivity"] = f"unhealthy: {str(e)}"
        
        return details


# Example usage

async def demonstrate_advanced_features():
    """Demonstrate advanced infrastructure features."""
    print("=== Advanced Infrastructure Services Demo ===\n")
    
    # Create service with configuration
    config = {
        "database_url": "postgresql://localhost/test",
        "pool_size": 5,
        "max_retries": 3
    }
    
    db_service = AdvancedDatabaseService(config)
    
    try:
        # Start service
        print("Starting database service...")
        await db_service.start()
        
        # Perform operations
        print("\n1. Normal query execution:")
        result = await db_service.execute_query("SELECT * FROM users")
        print(f"   Result: {result}")
        
        print("\n2. Transaction execution:")
        results = await db_service.execute_transaction([
            "INSERT INTO users (name) VALUES ('Alice')",
            "INSERT INTO users (name) VALUES ('Bob')",
            "UPDATE users SET active = true"
        ])
        print(f"   Transaction completed with {len(results)} operations")
        
        print("\n3. Simulating high load (rate limiting):")
        tasks = []
        for i in range(20):
            task = asyncio.create_task(
                db_service.execute_query(f"SELECT * FROM table_{i}")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if not isinstance(r, Exception))
        print(f"   Completed {successful}/20 queries (rate limited)")
        
        print("\n4. Health check:")
        health = await db_service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Pool utilization: {health['details']['pool']['utilization']:.1f}%")
        print(f"   Circuit breaker: {health['details']['resilience']['circuit_breaker']}")
        
        print("\n5. Resilience statistics:")
        stats = resilience_manager.get_all_stats()
        for component, data in stats.items():
            if data:  # Only show components with data
                print(f"\n   {component}:")
                for name, metrics in data.items():
                    print(f"     - {name}: {metrics}")
        
    finally:
        # Cleanup
        print("\nCleaning up...")
        await db_service.cleanup()
        await resource_manager.cleanup()


async def demonstrate_error_recovery():
    """Demonstrate error recovery features."""
    print("\n=== Error Recovery Demo ===\n")
    
    # Create a service that will experience failures
    class FlakeyService(BaseInfraService):
        def __init__(self):
            super().__init__("flakey_service")
            self._failure_count = 0
        
        async def _do_initialize(self): pass
        async def _do_start(self): pass
        async def _do_stop(self): pass
        async def _do_cleanup(self): pass
        async def _do_connect(self): pass
        async def _do_disconnect(self): pass
        
        async def unreliable_operation(self) -> str:
            """Operation that fails initially then succeeds."""
            self._failure_count += 1
            
            if self._failure_count <= 2:
                raise ConnectionError(f"Operation failed (attempt {self._failure_count})")
            
            return "Success after retries!"
    
    service = FlakeyService()
    await service.start()
    
    try:
        # Create error context
        context = ErrorContext(
            service_name="flakey_service",
            operation="unreliable_operation",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.CONNECTION,
            max_retries=3
        )
        
        # Execute with error recovery
        result = await error_handler.handle_error(
            ConnectionError("Initial failure"),
            context,
            service.unreliable_operation
        )
        
        print(f"Operation result: {result}")
        print(f"Total attempts: {service._failure_count}")
        
    finally:
        await service.cleanup()


async def demonstrate_resource_pooling():
    """Demonstrate resource pooling features."""
    print("\n=== Resource Pooling Demo ===\n")
    
    # Create mock resource
    class ExpensiveResource:
        counter = 0
        
        def __init__(self):
            ExpensiveResource.counter += 1
            self.id = ExpensiveResource.counter
            print(f"Created expensive resource #{self.id}")
        
        async def use(self) -> str:
            return f"Using resource #{self.id}"
        
        async def close(self) -> None:
            print(f"Closed expensive resource #{self.id}")
    
    # Create factory
    class ExpensiveResourceFactory(ResourceFactory[ExpensiveResource]):
        async def create(self) -> ExpensiveResource:
            await asyncio.sleep(0.1)  # Simulate expensive creation
            return ExpensiveResource()
        
        async def destroy(self, resource: ExpensiveResource) -> None:
            await resource.close()
    
    # Create pool
    pool = ResourcePool(
        factory=ExpensiveResourceFactory(),
        min_size=2,
        max_size=5,
        max_idle_time=10.0
    )
    
    await pool.initialize()
    
    try:
        print("Using resources from pool:")
        
        # Use resources concurrently
        async def use_resource(task_id: int):
            async with pool.acquire_context() as resource:
                result = await resource.use()
                print(f"  Task {task_id}: {result}")
                await asyncio.sleep(0.2)  # Simulate work
        
        # Run 10 tasks with only 5 max resources
        tasks = [use_resource(i) for i in range(10)]
        await asyncio.gather(*tasks)
        
        print(f"\nPool metrics: {pool.get_metrics()}")
        
    finally:
        await pool.close()


async def main():
    """Run all demonstrations."""
    await demonstrate_advanced_features()
    await demonstrate_error_recovery()
    await demonstrate_resource_pooling()


if __name__ == "__main__":
    asyncio.run(main())