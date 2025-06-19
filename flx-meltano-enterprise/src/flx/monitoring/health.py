"""
Health checking system for FLX platform.

Provides comprehensive health checks for all platform components including
database, cache, message queue, and external services.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import asyncpg
import redis.asyncio as redis
import structlog
from aio_pika import connect_robust

# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies



# Lazy import to avoid circular dependencies
settings = lazy_import("flx.config", "settings")

logger = structlog.get_logger()


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component."""

    name: str
    status: HealthStatus
    message: str
    metadata: dict[str, Any]
    checked_at: datetime
    response_time_ms: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
            "checked_at": self.checked_at.isoformat(),
            "response_time_ms": self.response_time_ms,
        }


class HealthChecker:
    """Manages health checks for all platform components."""

    def __init__(self) -> None:
        """Initialize health checker."""
        self.logger = logger.bind(component="health_checker")
        self._checks: dict[str, ComponentHealth] = {}
        self._redis_client: Optional[redis.Redis] = None
        self._db_pool: Optional[asyncpg.Pool] = None

    async def initialize(self) -> None:
        """Initialize health checker resources."""
        self.logger.info("Initializing health checker")

        # Initialize Redis client
        try:
            self._redis_client = await redis.from_url(
                settings.redis_url,
                decode_responses=settings.redis_decode_responses,
                max_connections=10,
            )
        except Exception as e:
            self.logger.error("Failed to initialize Redis client", error=str(e))

        # Initialize database pool
        try:
            self._db_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=5,
                command_timeout=10,
            )
        except Exception as e:
            self.logger.error("Failed to initialize database pool", error=str(e))

    async def cleanup(self) -> None:
        """Cleanup health checker resources."""
        self.logger.info("Cleaning up health checker")

        if self._redis_client:
            await self._redis_client.close()

        if self._db_pool:
            await self._db_pool.close()

    async def check_all(self) -> dict[str, ComponentHealth]:
        """Run all health checks."""
        self.logger.debug("Running all health checks")

        # Run checks concurrently
        tasks = [
            self._check_database(),
            self._check_redis(),
            self._check_rabbitmq(),
            self._check_meltano(),
            self._check_disk_space(),
            self._check_memory(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, ComponentHealth):
                self._checks[result.name] = result
            elif isinstance(result, Exception):
                self.logger.error("Health check failed", error=str(result))

        return self._checks

    async def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self._checks:
            return HealthStatus.UNHEALTHY

        statuses = [check.status for check in self._checks.values()]

        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED

    async def _check_database(self) -> ComponentHealth:
        """Check database health."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self._db_pool:
                raise Exception("Database pool not initialized")

            async with self._db_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")

                if result != 1:
                    raise Exception("Unexpected query result")

            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database is responsive",
                metadata={
                    "pool_size": self._db_pool.get_size(),
                    "pool_free": self._db_pool.get_idle_size(),
                },
                checked_at=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )

        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                metadata={},
                checked_at=datetime.now(timezone.utc),
            )

    async def _check_redis(self) -> ComponentHealth:
        """Check Redis health."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self._redis_client:
                raise Exception("Redis client not initialized")

            # Ping Redis
            await self._redis_client.ping()

            # Get info
            info = await self._redis_client.info()

            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis is responsive",
                metadata={
                    "version": info.get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                },
                checked_at=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )

        except Exception as e:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis check failed: {str(e)}",
                metadata={},
                checked_at=datetime.now(timezone.utc),
            )

    async def _check_rabbitmq(self) -> ComponentHealth:
        """Check RabbitMQ health."""
        if not settings.amqp_url:
            return ComponentHealth(
                name="rabbitmq",
                status=HealthStatus.HEALTHY,
                message="RabbitMQ not configured",
                metadata={"configured": False},
                checked_at=datetime.now(timezone.utc),
            )

        start_time = asyncio.get_event_loop().time()

        try:
            # Try to connect
            connection = await connect_robust(
                settings.amqp_url,
                timeout=5,
            )

            # Get channel
            await connection.channel()

            # Close connection
            await connection.close()

            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="rabbitmq",
                status=HealthStatus.HEALTHY,
                message="RabbitMQ is responsive",
                metadata={"configured": True},
                checked_at=datetime.now(timezone.utc),
                response_time_ms=response_time,
            )

        except Exception as e:
            return ComponentHealth(
                name="rabbitmq",
                status=HealthStatus.UNHEALTHY,
                message=f"RabbitMQ check failed: {str(e)}",
                metadata={"configured": True},
                checked_at=datetime.now(timezone.utc),
            )

    async def _check_meltano(self) -> ComponentHealth:
        """Check Meltano installation."""
        try:
            # Run meltano version command
            process = await asyncio.create_subprocess_exec(
                "meltano",
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                version = stdout.decode().strip()

                return ComponentHealth(
                    name="meltano",
                    status=HealthStatus.HEALTHY,
                    message="Meltano is installed",
                    metadata={"version": version},
                    checked_at=datetime.now(timezone.utc),
                )
            else:
                raise Exception(f"Meltano command failed: {stderr.decode()}")

        except Exception as e:
            return ComponentHealth(
                name="meltano",
                status=HealthStatus.UNHEALTHY,
                message=f"Meltano check failed: {str(e)}",
                metadata={},
                checked_at=datetime.now(timezone.utc),
            )

    async def _check_disk_space(self) -> ComponentHealth:
        """Check available disk space."""
        try:
            import shutil

            # Check disk usage
            usage = shutil.disk_usage("/")

            # Calculate percentage
            used_percent = (usage.used / usage.total) * 100

            # Determine status
            if used_percent < 80:
                status = HealthStatus.HEALTHY
                message = "Sufficient disk space available"
            elif used_percent < 90:
                status = HealthStatus.DEGRADED
                message = "Disk space is running low"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Critical: Disk space almost full"

            return ComponentHealth(
                name="disk_space",
                status=status,
                message=message,
                metadata={
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "used_percent": round(used_percent, 2),
                },
                checked_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            return ComponentHealth(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {str(e)}",
                metadata={},
                checked_at=datetime.now(timezone.utc),
            )

    async def _check_memory(self) -> ComponentHealth:
        """Check available memory."""
        try:
            import psutil

            # Get memory info
            memory = psutil.virtual_memory()

            # Determine status
            if memory.percent < 80:
                status = HealthStatus.HEALTHY
                message = "Sufficient memory available"
            elif memory.percent < 90:
                status = HealthStatus.DEGRADED
                message = "Memory usage is high"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Critical: Memory almost exhausted"

            return ComponentHealth(
                name="memory",
                status=status,
                message=message,
                metadata={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": round(memory.percent, 2),
                },
                checked_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            return ComponentHealth(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                metadata={},
                checked_at=datetime.now(timezone.utc),
            )
