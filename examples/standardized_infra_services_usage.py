"""Example usage of standardized infrastructure services.

Demonstrates how to use the new standardized service interfaces in applications.
"""

import asyncio
from typing import Any, Dict, Optional

from flx.infra.cache.standardized_cache_service import StandardizedCacheService
from flx.infra.http.standardized_client_service import StandardizedHttpClientService
from flx.infra.services.base import service_registry


class Application:
    """Example application using standardized services."""
    
    def __init__(self):
        self.cache_service: Optional[StandardizedCacheService] = None
        self.http_service: Optional[StandardizedHttpClientService] = None
    
    async def setup_services(self):
        """Set up infrastructure services."""
        # Configure cache service
        cache_config = {
            "backend": "memory",
            "ttl": 3600,  # 1 hour default TTL
            "max_size": 1000
        }
        self.cache_service = StandardizedCacheService(cache_config)
        service_registry.register("cache", self.cache_service)
        
        # Configure HTTP client service
        http_config = {
            "base_url": "https://jsonplaceholder.typicode.com",
            "timeout": 30,
            "max_retries": 3,
            "headers": {
                "User-Agent": "FLX-Example/1.0",
                "Accept": "application/json"
            }
        }
        self.http_service = StandardizedHttpClientService(http_config)
        service_registry.register("http", self.http_service)
        
        # Start all services
        await service_registry.start_all()
        print("✓ All services started successfully")
        
        # Check health
        health_status = await service_registry.health_check_all()
        for service_name, status in health_status.items():
            print(f"  - {service_name}: {status['status']}")
    
    async def fetch_user_with_cache(self, user_id: int) -> Dict[str, Any]:
        """Fetch user data with caching."""
        cache_key = f"user_{user_id}"
        
        # Check cache first
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            print(f"Cache hit for user {user_id}")
            return cached_data
        
        print(f"Cache miss for user {user_id}, fetching from API...")
        
        # Fetch from API
        user_data = await self.http_service.get(f"/users/{user_id}")
        
        # Cache the response
        await self.cache_service.set(cache_key, user_data, ttl=300)  # Cache for 5 minutes
        
        return user_data
    
    async def fetch_posts_for_user(self, user_id: int) -> list:
        """Fetch posts for a user with caching."""
        cache_key = f"user_posts_{user_id}"
        
        # Check cache
        cached_posts = await self.cache_service.get(cache_key)
        if cached_posts:
            print(f"Cache hit for posts of user {user_id}")
            return cached_posts
        
        print(f"Cache miss for posts of user {user_id}, fetching from API...")
        
        # Fetch from API
        posts = await self.http_service.get("/posts", params={"userId": user_id})
        
        # Cache the response
        await self.cache_service.set(cache_key, posts, ttl=600)  # Cache for 10 minutes
        
        return posts
    
    async def cleanup(self):
        """Clean up services."""
        await service_registry.cleanup_all()
        print("✓ All services cleaned up")


async def example_basic_usage():
    """Basic usage example."""
    print("\n=== Basic Service Usage Example ===\n")
    
    # Create and configure services
    cache = StandardizedCacheService({"backend": "memory"})
    http = StandardizedHttpClientService({
        "base_url": "https://api.github.com",
        "headers": {"Accept": "application/vnd.github.v3+json"}
    })
    
    # Use services with context manager
    async with cache.context(), http.context():
        # Services are automatically started
        print("Services started")
        
        # Use cache
        await cache.set("key1", {"data": "value1"})
        value = await cache.get("key1")
        print(f"Cache get: {value}")
        
        # Use HTTP client (commented out to avoid actual API calls)
        # response = await http.get("/users/github")
        # print(f"HTTP response: {response}")
    
    # Services are automatically stopped
    print("Services stopped")


async def example_with_registry():
    """Example using service registry."""
    print("\n=== Service Registry Example ===\n")
    
    # Create services
    cache = StandardizedCacheService()
    http = StandardizedHttpClientService()
    
    # Register services
    service_registry.register("app_cache", cache)
    service_registry.register("app_http", http)
    
    try:
        # Start all services
        await service_registry.start_all()
        
        # Use services
        cache_service = service_registry.get("app_cache")
        await cache_service.set("test", "data")
        
        # Health check all services
        health_status = await service_registry.health_check_all()
        for name, status in health_status.items():
            print(f"{name}: {status['status']}")
    
    finally:
        # Cleanup all services
        await service_registry.cleanup_all()


async def example_with_configuration():
    """Example with dynamic configuration."""
    print("\n=== Dynamic Configuration Example ===\n")
    
    # Create service with initial config
    cache = StandardizedCacheService({
        "backend": "memory",
        "ttl": 60,
        "max_size": 100
    })
    
    await cache.start()
    
    try:
        # Use with initial config
        await cache.set("key1", "value1")  # Uses 60s TTL
        
        # Update configuration
        cache.configure({"ttl": 300})  # Change default TTL to 5 minutes
        
        # New entries use updated config
        await cache.set("key2", "value2")  # Uses 300s TTL
        
        print(f"Current config: {cache.get_configuration()}")
    
    finally:
        await cache.cleanup()


async def example_with_test_engine():
    """Example using test engine for testing."""
    print("\n=== Test Engine Example ===\n")
    
    # Mock test engine
    class MockCacheEngine:
        def __init__(self):
            self.data = {}
        
        def get(self, key):
            print(f"MockEngine: Getting {key}")
            return self.data.get(key)
        
        def set(self, key, value, ttl=None):
            print(f"MockEngine: Setting {key} = {value} (ttl={ttl})")
            self.data[key] = value
        
        def exists(self, key):
            return key in self.data
    
    # Create service and set test engine
    cache = StandardizedCacheService()
    test_engine = MockCacheEngine()
    cache.set_test_engine(test_engine)
    
    await cache.start()
    
    try:
        # Operations will use test engine
        await cache.set("test_key", "test_value", ttl=60)
        value = await cache.get("test_key")
        print(f"Retrieved: {value}")
    
    finally:
        await cache.cleanup()


async def example_error_handling():
    """Example with error handling."""
    print("\n=== Error Handling Example ===\n")
    
    # Create service with invalid config
    try:
        cache = StandardizedCacheService({
            "backend": "unsupported_backend"
        })
        await cache.start()
    except ValueError as e:
        print(f"Configuration error: {e}")
    
    # Use service when not connected
    cache = StandardizedCacheService()
    try:
        await cache.get("key")  # Will fail - not connected
    except RuntimeError as e:
        print(f"Runtime error: {e}")
    
    # Proper usage
    await cache.start()
    await cache.set("key", "value")  # Works now
    await cache.cleanup()


async def example_metrics_and_monitoring():
    """Example with metrics and monitoring."""
    print("\n=== Metrics and Monitoring Example ===\n")
    
    # Create HTTP service
    http = StandardizedHttpClientService({
        "base_url": "https://httpbin.org",
        "max_retries": 2
    })
    
    await http.start()
    
    try:
        # Make some requests (using httpbin for testing)
        # Commented out to avoid actual API calls
        # await http.get("/status/200")  # Success
        # await http.get("/status/500")  # Server error (will retry)
        
        # Simulate requests for metrics
        http._metrics["total_requests"] = 5
        http._metrics["successful_requests"] = 4
        http._metrics["failed_requests"] = 1
        http._metrics["total_retries"] = 2
        http._metrics["average_response_time"] = 0.250
        
        # Get metrics
        metrics = await http.get_metrics()
        print("HTTP Client Metrics:")
        for key, value in metrics.items():
            print(f"  - {key}: {value}")
        
        # Health check
        health = await http.health_check()
        print(f"\nHealth Status: {health['status']}")
        print(f"Metrics from health: {health['details']['metrics']}")
    
    finally:
        await http.cleanup()


async def main():
    """Run all examples."""
    # Basic examples
    await example_basic_usage()
    await example_with_registry()
    await example_with_configuration()
    await example_with_test_engine()
    await example_error_handling()
    await example_metrics_and_monitoring()
    
    # Application example
    print("\n=== Application Example ===\n")
    app = Application()
    
    try:
        await app.setup_services()
        
        # Fetch user data (with caching)
        # Commented out to avoid actual API calls
        # user = await app.fetch_user_with_cache(1)
        # print(f"User: {user}")
        
        # Fetch again (should hit cache)
        # user = await app.fetch_user_with_cache(1)
        
        # Fetch posts
        # posts = await app.fetch_posts_for_user(1)
        # print(f"Posts count: {len(posts)}")
        
        print("Application example completed (API calls commented out)")
    
    finally:
        await app.cleanup()


if __name__ == "__main__":
    asyncio.run(main())