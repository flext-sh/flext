"""Example usage of standardized infrastructure services.

Demonstrates how to use the new standardized service interfaces in applications.
"""

import asyncio
from typing import Any

from flx.infra.cache.standardized_cache_service import StandardizedCacheService
from flx.infra.http.standardized_client_service import StandardizedHttpClientService
from flx.infra.services.base import service_registry


class Application:
    """Example application using standardized services."""

    def __init__(self) -> None:
        self.cache_service: StandardizedCacheService | None = None
        self.http_service: StandardizedHttpClientService | None = None

    async def setup_services(self) -> None:
        """Set up infrastructure services."""
        # Configure cache service
        cache_config = {
            "backend": "memory",
            "ttl": 3600,  # 1 hour default TTL
            "max_size": 1000,
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
                "Accept": "application/json",
            },
        }
        self.http_service = StandardizedHttpClientService(http_config)
        service_registry.register("http", self.http_service)

        # Start all services
        await service_registry.start_all()

        # Check health
        health_status = await service_registry.health_check_all()
        for _service_name, _status in health_status.items():
            pass

    async def fetch_user_with_cache(self, user_id: int) -> dict[str, Any]:
        """Fetch user data with caching."""
        cache_key = f"user_{user_id}"

        # Check cache first
        cached_data = await self.cache_service.get(cache_key)
        if cached_data:
            return cached_data

        # Fetch from API
        user_data = await self.http_service.get(f"/users/{user_id}")

        # Cache the response
        await self.cache_service.set(
            cache_key,
            user_data,
            ttl=300,
        )  # Cache for 5 minutes

        return user_data

    async def fetch_posts_for_user(self, user_id: int) -> list:
        """Fetch posts for a user with caching."""
        cache_key = f"user_posts_{user_id}"

        # Check cache
        cached_posts = await self.cache_service.get(cache_key)
        if cached_posts:
            return cached_posts

        # Fetch from API
        posts = await self.http_service.get("/posts", params={"userId": user_id})

        # Cache the response
        # Cache for 10 minutes
        await self.cache_service.set(cache_key, posts, ttl=600)

        return posts

    async def cleanup(self) -> None:
        """Clean up services."""
        await service_registry.cleanup_all()


async def example_basic_usage() -> None:
    """Basic usage example."""
    # Create and configure services
    cache = StandardizedCacheService({"backend": "memory"})
    http = StandardizedHttpClientService(
        {
            "base_url": "https://api.github.com",
            "headers": {"Accept": "application/vnd.github.v3+json"},
        },
    )

    # Use services with context manager
    async with cache.context(), http.context():
        # Services are automatically started

        # Use cache
        await cache.set("key1", {"data": "value1"})
        await cache.get("key1")

        # Use HTTP client (commented out to avoid actual API calls)
        # response = await http.get("/users/github")
        # print(f"HTTP response: {response}")

    # Services are automatically stopped


async def example_with_registry() -> None:
    """Example using service registry."""
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
        for _name, _status in health_status.items():
            pass

    finally:
        # Cleanup all services
        await service_registry.cleanup_all()


async def example_with_configuration() -> None:
    """Example with dynamic configuration."""
    # Create service with initial config
    cache = StandardizedCacheService(
        {
            "backend": "memory",
            "ttl": 60,
            "max_size": 100,
        },
    )

    await cache.start()

    try:
        # Use with initial config
        await cache.set("key1", "value1")  # Uses 60s TTL

        # Update configuration
        cache.configure({"ttl": 300})  # Change default TTL to 5 minutes

        # New entries use updated config
        await cache.set("key2", "value2")  # Uses 300s TTL

    finally:
        await cache.cleanup()


async def example_with_test_engine() -> None:
    """Example using test engine for testing."""

    # Mock test engine
    class MockCacheEngine:
        def __init__(self) -> None:
            self.data = {}

        def get(self, key) -> Any:
            return self.data.get(key)

        def set(self, key, value, ttl=None) -> None:
            self.data[key] = value

        def exists(self, key) -> Any:
            return key in self.data

    # Create service and set test engine
    cache = StandardizedCacheService()
    test_engine = MockCacheEngine()
    cache.set_test_engine(test_engine)

    await cache.start()

    try:
        # Operations will use test engine
        await cache.set("test_key", "test_value", ttl=60)
        await cache.get("test_key")

    finally:
        await cache.cleanup()


async def example_error_handling() -> None:
    """Example with error handling."""
    # Create service with invalid config
    try:
        cache = StandardizedCacheService(
            {
                "backend": "unsupported_backend",
            },
        )
        await cache.start()
    except ValueError:
        pass

    # Use service when not connected
    cache = StandardizedCacheService()
    try:
        await cache.get("key")  # Will fail - not connected
    except RuntimeError:
        pass

    # Proper usage
    await cache.start()
    await cache.set("key", "value")  # Works now
    await cache.cleanup()


async def example_metrics_and_monitoring() -> None:
    """Example with metrics and monitoring."""
    # Create HTTP service
    http = StandardizedHttpClientService(
        {
            "base_url": "https://httpbin.org",
            "max_retries": 2,
        },
    )

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
        for _key, _value in metrics.items():
            pass

        # Health check
        await http.health_check()

    finally:
        await http.cleanup()


async def main() -> None:
    """Run all examples."""
    # Basic examples
    await example_basic_usage()
    await example_with_registry()
    await example_with_configuration()
    await example_with_test_engine()
    await example_error_handling()
    await example_metrics_and_monitoring()

    # Application example
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

    finally:
        await app.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
