"""
Metrics collection system for FLX platform.

Provides Prometheus metrics for monitoring platform performance,
resource usage, and business metrics.
"""

import time
from functools import wraps
from typing import Any, Callable

import psutil
import structlog
from prometheus_client import Counter, Gauge, Histogram, Info

from flx.config import settings

logger = structlog.get_logger()

# System metrics
system_info = Info(
    "flx_system",
    "FLX system information",
)

uptime_seconds = Gauge(
    "flx_uptime_seconds",
    "System uptime in seconds",
)

# Resource metrics
cpu_usage_percent = Gauge(
    "flx_cpu_usage_percent",
    "CPU usage percentage",
    ["core"],
)

memory_usage_bytes = Gauge(
    "flx_memory_usage_bytes",
    "Memory usage in bytes",
    ["type"],  # total, available, used, percent
)

disk_usage_bytes = Gauge(
    "flx_disk_usage_bytes",
    "Disk usage in bytes",
    ["mount", "type"],  # type: total, used, free
)

# gRPC metrics
grpc_requests_total = Counter(
    "flx_grpc_requests_total",
    "Total gRPC requests",
    ["method", "status"],
)

grpc_request_duration_seconds = Histogram(
    "flx_grpc_request_duration_seconds",
    "gRPC request duration",
    ["method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

grpc_active_requests = Gauge(
    "flx_grpc_active_requests",
    "Number of active gRPC requests",
    ["method"],
)

# Pipeline metrics
pipeline_runs_total = Counter(
    "flx_pipeline_runs_total",
    "Total number of pipeline runs",
    ["pipeline", "status"],
)

pipeline_duration_seconds = Histogram(
    "flx_pipeline_duration_seconds",
    "Pipeline execution duration in seconds",
    ["pipeline"],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, 600.0, 1800.0, 3600.0),
)

active_pipelines = Gauge(
    "flx_active_pipelines",
    "Number of currently active pipelines",
)

pipeline_records_processed = Counter(
    "flx_pipeline_records_processed_total",
    "Total records processed by pipelines",
    ["pipeline", "operation"],  # operation: extracted, loaded
)

# Event bus metrics
events_published_total = Counter(
    "flx_events_published_total",
    "Total events published",
    ["event_type"],
)

events_processed_total = Counter(
    "flx_events_processed_total",
    "Total events processed",
    ["event_type", "status"],  # status: success, failure
)

event_processing_duration_seconds = Histogram(
    "flx_event_processing_duration_seconds",
    "Event processing duration",
    ["event_type"],
)

# Database metrics
database_connections_active = Gauge(
    "flx_database_connections_active",
    "Active database connections",
)

database_connections_idle = Gauge(
    "flx_database_connections_idle",
    "Idle database connections",
)

database_query_duration_seconds = Histogram(
    "flx_database_query_duration_seconds",
    "Database query duration",
    ["operation"],  # select, insert, update, delete
)

# Cache metrics
cache_hits_total = Counter(
    "flx_cache_hits_total",
    "Total cache hits",
    ["cache_name"],
)

cache_misses_total = Counter(
    "flx_cache_misses_total",
    "Total cache misses",
    ["cache_name"],
)

cache_size_bytes = Gauge(
    "flx_cache_size_bytes",
    "Cache size in bytes",
    ["cache_name"],
)


class MetricsCollector:
    """Collects and exposes metrics for the FLX platform."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.logger = logger.bind(component="metrics_collector")
        self._start_time = time.time()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize metrics with system information."""
        if self._initialized:
            return

        # Set system info
        system_info.info(
            {
                "version": "2.0.0",
                "environment": settings.environment,
                "python_version": f"{psutil.PYTHON_VERSION}",
                "platform": psutil.PLATFORM,
            }
        )

        self._initialized = True
        self.logger.info("Metrics collector initialized")

    async def collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        try:
            # Uptime
            uptime_seconds.set(time.time() - self._start_time)

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            for i, percent in enumerate(cpu_percent):
                cpu_usage_percent.labels(core=str(i)).set(percent)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage_bytes.labels(type="total").set(memory.total)
            memory_usage_bytes.labels(type="available").set(memory.available)
            memory_usage_bytes.labels(type="used").set(memory.used)
            memory_usage_bytes.labels(type="percent").set(memory.percent)

            # Disk usage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage_bytes.labels(
                        mount=partition.mountpoint, type="total"
                    ).set(usage.total)
                    disk_usage_bytes.labels(
                        mount=partition.mountpoint, type="used"
                    ).set(usage.used)
                    disk_usage_bytes.labels(
                        mount=partition.mountpoint, type="free"
                    ).set(usage.free)
                except PermissionError:
                    # Some mount points may not be accessible
                    pass

        except Exception as e:
            self.logger.error("Failed to collect system metrics", error=str(e))

    def track_pipeline_execution(self, pipeline_name: str) -> Callable:
        """Decorator to track pipeline execution metrics."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                active_pipelines.inc()
                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)
                    pipeline_runs_total.labels(
                        pipeline=pipeline_name, status="success"
                    ).inc()
                    return result
                except Exception:
                    pipeline_runs_total.labels(
                        pipeline=pipeline_name, status="failure"
                    ).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    pipeline_duration_seconds.labels(pipeline=pipeline_name).observe(
                        duration
                    )
                    active_pipelines.dec()

            return wrapper

        return decorator

    def track_grpc_request(self, method: str) -> Callable:
        """Decorator to track gRPC request metrics."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                grpc_active_requests.labels(method=method).inc()
                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)
                    grpc_requests_total.labels(method=method, status="success").inc()
                    return result
                except Exception:
                    grpc_requests_total.labels(method=method, status="failure").inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    grpc_request_duration_seconds.labels(method=method).observe(
                        duration
                    )
                    grpc_active_requests.labels(method=method).dec()

            return wrapper

        return decorator

    def track_event_processing(self, event_type: str) -> Callable:
        """Decorator to track event processing metrics."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()

                try:
                    result = await func(*args, **kwargs)
                    events_processed_total.labels(
                        event_type=event_type, status="success"
                    ).inc()
                    return result
                except Exception:
                    events_processed_total.labels(
                        event_type=event_type, status="failure"
                    ).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    event_processing_duration_seconds.labels(
                        event_type=event_type
                    ).observe(duration)

            return wrapper

        return decorator

    @staticmethod
    def record_pipeline_records(pipeline: str, operation: str, count: int) -> None:
        """Record number of records processed."""
        pipeline_records_processed.labels(pipeline=pipeline, operation=operation).inc(
            count
        )

    @staticmethod
    def record_event_published(event_type: str) -> None:
        """Record event publication."""
        events_published_total.labels(event_type=event_type).inc()

    @staticmethod
    def record_cache_hit(cache_name: str) -> None:
        """Record cache hit."""
        cache_hits_total.labels(cache_name=cache_name).inc()

    @staticmethod
    def record_cache_miss(cache_name: str) -> None:
        """Record cache miss."""
        cache_misses_total.labels(cache_name=cache_name).inc()

    @staticmethod
    def set_cache_size(cache_name: str, size_bytes: int) -> None:
        """Set cache size."""
        cache_size_bytes.labels(cache_name=cache_name).set(size_bytes)

    @staticmethod
    def set_database_connections(active: int, idle: int) -> None:
        """Set database connection counts."""
        database_connections_active.set(active)
        database_connections_idle.set(idle)

    @staticmethod
    def record_database_query(operation: str, duration: float) -> None:
        """Record database query metrics."""
        database_query_duration_seconds.labels(operation=operation).observe(duration)
