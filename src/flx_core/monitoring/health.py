"""Health monitoring system for FLX components.

This module provides comprehensive health checking capabilities for all FLX system
components including database, Redis, RabbitMQ, Meltano, disk space, and memory.
"""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from enum import Enum
from typing import TYPE_CHECKING, Any

import asyncpg
import psutil
import redis.asyncio as redis
import structlog
from aio_pika import connect_robust
from pydantic import BaseModel, ConfigDict

from flx_core.config import settings

if TYPE_CHECKING:
    pass

logger = structlog.get_logger()

# Constants for health thresholds
DISK_SPACE_WARNING_THRESHOLD = 80
DISK_SPACE_CRITICAL_THRESHOLD = 90
MEMORY_WARNING_THRESHOLD = 80
MEMORY_CRITICAL_THRESHOLD = 90
DATABASE_POOL_MIN_SIZE = 2
DATABASE_POOL_MAX_SIZE = 5
REDIS_MAX_CONNECTIONS = 10
RABBITMQ_CONNECTION_TIMEOUT = 5
DATABASE_QUERY_EXPECTED_RESULT = 1


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckError(Exception):
    """Base exception for health check operations."""


class DatabasePoolError(HealthCheckError):
    """Exception raised when database pool is not initialized."""


class UnexpectedQueryResultError(HealthCheckError):
    """Exception raised when database query returns unexpected result."""


class RedisConnectionError(HealthCheckError):
    """Exception raised when Redis client is not initialized."""


class MeltanoCommandError(HealthCheckError):
    """Exception raised when Meltano command fails."""


class ComponentHealth(BaseModel):
    """Health status of a single component."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
    )

    name: str
    healthy: bool
    status: HealthStatus
    message: str
    response_time_ms: float | None = None
    metadata: dict[str, Any] | None = None


class SystemHealth(BaseModel):
    """Overall system health status."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
    )

    healthy: bool
    status: HealthStatus
    components: dict[str, ComponentHealth]
    timestamp: float


class HealthChecker:
    """Health checker for all system components."""

    def __init__(self) -> None:
        """Initialize the health checker."""
        self._db_pool: asyncpg.Pool[Any] | None = None
        self._redis_client: redis.Redis[str] | None = None

    async def initialize(self) -> None:
        """Initialize connections for health checking."""
        await self._initialize_database()
        await self._initialize_redis()

    async def _initialize_redis(self) -> None:
        """Initialize Redis connection for health checks."""
        if not settings.redis_url:
            logger.warning("Redis URL not configured, skipping Redis initialization")
            return

        try:
            self._redis_client = await redis.from_url(
                settings.redis_url,
                decode_responses=settings.redis_decode_responses,
                max_connections=REDIS_MAX_CONNECTIONS,
            )
            logger.info("Redis health checker initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Redis health checker", error=str(e))

    async def _initialize_database(self) -> None:
        """Initialize database connection pool for health checks."""
        try:
            self._db_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=DATABASE_POOL_MIN_SIZE,
                max_size=DATABASE_POOL_MAX_SIZE,
            )
            logger.info("Database health checker initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database health checker", error=str(e))

    async def check_all(self) -> SystemHealth:
        """Check health of all system components."""
        start_time = asyncio.get_event_loop().time()

        # Run all health checks concurrently
        health_checks = await asyncio.gather(
            self._check_database(),
            self._check_redis(),
            self._check_rabbitmq(),
            self._check_meltano(),
            self._check_disk_space(),
            self._check_memory(),
            return_exceptions=True,
        )

        # Process results
        components: dict[str, ComponentHealth] = {}
        for check_result in health_checks:
            if isinstance(check_result, ComponentHealth):
                components[check_result.name] = check_result
            elif isinstance(check_result, Exception):
                logger.error("Health check failed", error=str(check_result))
                # Create unhealthy component for failed check
                components["unknown"] = ComponentHealth(
                    name="unknown",
                    healthy=False,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check failed: {check_result}",
                )

        # Determine overall health
        overall_healthy = all(component.healthy for component in components.values())
        overall_status = HealthStatus.HEALTHY if overall_healthy else HealthStatus.UNHEALTHY

        return SystemHealth(
            healthy=overall_healthy,
            status=overall_status,
            components=components,
            timestamp=start_time,
        )

    async def _check_database(self) -> ComponentHealth:
        """Check database connectivity and responsiveness."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self._db_pool:
                raise DatabasePoolError("Database pool not initialized")

            async with self._db_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")

                if result != DATABASE_QUERY_EXPECTED_RESULT:
                    raise UnexpectedQueryResultError("Database query returned unexpected result")

            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="database",
                healthy=True,
                status=HealthStatus.HEALTHY,
                message="Database is responding normally",
                response_time_ms=response_time,
            )

        except (DatabasePoolError, UnexpectedQueryResultError) as e:
            return ComponentHealth(
                name="database",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )
        except (OSError, ConnectionError, asyncpg.PostgresError) as e:
            return ComponentHealth(
                name="database",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {e}",
            )

    async def _check_redis(self) -> ComponentHealth:
        """Check Redis connectivity and responsiveness."""
        start_time = asyncio.get_event_loop().time()

        try:
            if not self._redis_client:
                raise RedisConnectionError("Redis client not initialized")

            # Ping Redis
            await self._redis_client.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="redis",
                healthy=True,
                status=HealthStatus.HEALTHY,
                message="Redis is responding normally",
                response_time_ms=response_time,
            )

        except RedisConnectionError as e:
            return ComponentHealth(
                name="redis",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )
        except (OSError, ConnectionError, redis.RedisError) as e:
            return ComponentHealth(
                name="redis",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {e}",
            )

    async def _check_rabbitmq(self) -> ComponentHealth:
        """Check RabbitMQ connectivity and responsiveness."""
        if not settings.amqp_url:
            return ComponentHealth(
                name="rabbitmq",
                healthy=True,
                status=HealthStatus.HEALTHY,
                message="RabbitMQ not configured (optional service)",
            )

        start_time = asyncio.get_event_loop().time()

        try:
            # Try to connect
            connection = await connect_robust(
                settings.amqp_url,
                timeout=RABBITMQ_CONNECTION_TIMEOUT,
            )

            # Close connection immediately
            await connection.close()

            response_time = (asyncio.get_event_loop().time() - start_time) * 1000

            return ComponentHealth(
                name="rabbitmq",
                healthy=True,
                status=HealthStatus.HEALTHY,
                message="RabbitMQ is responding normally",
                response_time_ms=response_time,
            )

        except (OSError, ConnectionError, TimeoutError) as e:
            return ComponentHealth(
                name="rabbitmq",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"RabbitMQ connection failed: {e}",
            )

    async def _check_meltano(self) -> ComponentHealth:
        """Check Meltano availability and functionality."""
        try:
            # Run a simple Meltano command to check if it's working
            process = await asyncio.create_subprocess_exec(
                "meltano",
                "--version",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise MeltanoCommandError(f"Meltano command failed: {stderr.decode()}")

            return ComponentHealth(
                name="meltano",
                healthy=True,
                status=HealthStatus.HEALTHY,
                message=f"Meltano is working (version: {stdout.decode().strip()})",
            )

        except MeltanoCommandError:
            raise
        except (OSError, FileNotFoundError) as e:
            return ComponentHealth(
                name="meltano",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"Meltano not found or not executable: {e}",
            )

    async def _check_disk_space(self) -> ComponentHealth:
        """Check available disk space."""
        try:
            # Get disk usage for current directory
            usage = shutil.disk_usage(".")
            total = usage.total
            used = usage.used
            free = usage.free
            used_percent = (used / total) * 100

            # Determine status based on thresholds
            if used_percent < DISK_SPACE_WARNING_THRESHOLD:
                status = HealthStatus.HEALTHY
                message = "Sufficient disk space available"
            elif used_percent < DISK_SPACE_CRITICAL_THRESHOLD:
                status = HealthStatus.DEGRADED
                message = "Disk space is running low"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Disk space is critically low"

            return ComponentHealth(
                name="disk_space",
                healthy=status == HealthStatus.HEALTHY,
                status=status,
                message=message,
                metadata={
                    "total_bytes": total,
                    "used_bytes": used,
                    "free_bytes": free,
                    "used_percent": used_percent,
                },
            )

        except OSError as e:
            return ComponentHealth(
                name="disk_space",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {e}",
            )

    async def _check_memory(self) -> ComponentHealth:
        """Check system memory usage."""
        try:
            # Get memory usage
            memory = psutil.virtual_memory()

            # Determine status based on thresholds
            if memory.percent < MEMORY_WARNING_THRESHOLD:
                status = HealthStatus.HEALTHY
                message = "Sufficient memory available"
            elif memory.percent < MEMORY_CRITICAL_THRESHOLD:
                status = HealthStatus.DEGRADED
                message = "Memory usage is high"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Memory usage is critically high"

            return ComponentHealth(
                name="memory",
                healthy=status == HealthStatus.HEALTHY,
                status=status,
                message=message,
                metadata={
                    "total_bytes": memory.total,
                    "used_bytes": memory.used,
                    "available_bytes": memory.available,
                    "used_percent": memory.percent,
                },
            )

        except OSError as e:
            return ComponentHealth(
                name="memory",
                healthy=False,
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {e}",
            )

    async def close(self) -> None:
        """Close all connections and clean up resources."""
        if self._db_pool:
            await self._db_pool.close()

        if self._redis_client:
            await self._redis_client.close()


# Global health checker instance
health_checker = HealthChecker()
