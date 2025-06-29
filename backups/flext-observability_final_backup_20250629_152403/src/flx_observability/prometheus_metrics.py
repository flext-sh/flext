"""Custom Prometheus metrics and collectors for enterprise monitoring.

This module provides specialized Prometheus metrics collectors for business-specific
monitoring, custom gauges, histograms, and integration with the FLX platform.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Self

from flx_core.config.domain_config import get_config

# ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus and psutil import management
from flx_core.utils.import_fallback_patterns import (
    get_prometheus_components,
    get_psutil_module,
)
from pydantic import BaseModel, Field

from flx_observability.structured_logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

# Import Prometheus components using centralized pattern
PROMETHEUS_AVAILABLE, prometheus_components = get_prometheus_components()

# Extract components for backward compatibility
if PROMETHEUS_AVAILABLE:
    Counter = prometheus_components.get("Counter")
    Gauge = prometheus_components.get("Gauge")
    Histogram = prometheus_components.get("Histogram")
    Summary = prometheus_components.get("Summary")
    Info = prometheus_components.get("Info")
    Enum = prometheus_components.get("Enum")
    CollectorRegistry = prometheus_components.get("CollectorRegistry")
    REGISTRY = prometheus_components.get("REGISTRY")
    generate_latest = prometheus_components.get("generate_latest")
    CONTENT_TYPE_LATEST = prometheus_components.get("CONTENT_TYPE_LATEST")
    CounterMetricFamily = prometheus_components.get("CounterMetricFamily")
    GaugeMetricFamily = prometheus_components.get("GaugeMetricFamily")
    HistogramMetricFamily = prometheus_components.get("HistogramMetricFamily")
    Collector = prometheus_components.get("Collector")
else:
    # Define fallback stubs for when Prometheus is not available
    Counter = Gauge = Histogram = Summary = Info = Enum = None
    CollectorRegistry = REGISTRY = generate_latest = CONTENT_TYPE_LATEST = None
    CounterMetricFamily = GaugeMetricFamily = HistogramMetricFamily = Collector = None


class MetricValue(BaseModel):
    """Represents a metric value with metadata."""

    value: float = Field(description="Metric value")
    labels: dict[str, str] = Field(default_factory=dict, description="Metric labels")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp",
    )
    help_text: str = Field(default="", description="Help text for the metric")


@dataclass
class BusinessMetric:
    """Business-specific metric definition."""

    name: str
    metric_type: str  # counter, gauge, histogram, summary
    help_text: str
    labels: list[str]
    value_extractor: Callable[[], float | dict[str, float]]
    enabled: bool = True


class FlxBusinessMetricsCollector(Collector):
    """Custom Prometheus collector for FLX business metrics.

    Collects business-specific metrics like:
    - Pipeline execution success rates
    - Data processing volumes
    - User activity metrics
    - System health indicators
    """

    def __init__(self) -> None:
        """Initialize business metrics collector."""
        self.logger = get_logger("metrics.business")
        self._metrics: dict[str, BusinessMetric] = {}
        self._last_collection = datetime.now(UTC)
        self._collection_lock = threading.RLock()

        # Register default business metrics
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register default business metrics."""
        # Pipeline metrics
        self.add_metric(
            BusinessMetric(
                name="flx_pipeline_executions_total",
                metric_type="counter",
                help_text="Total number of pipeline executions",
                labels=["pipeline_id", "status", "environment"],
                value_extractor=self._get_pipeline_execution_counts,
            ),
        )

        self.add_metric(
            BusinessMetric(
                name="flx_pipeline_duration_seconds",
                metric_type="histogram",
                help_text="Pipeline execution duration in seconds",
                labels=["pipeline_id", "environment"],
                value_extractor=self._get_pipeline_durations,
            ),
        )

        # Data processing metrics
        self.add_metric(
            BusinessMetric(
                name="flx_data_records_processed_total",
                metric_type="counter",
                help_text="Total number of data records processed",
                labels=["source", "destination", "pipeline_id"],
                value_extractor=self._get_data_processing_counts,
            ),
        )

        self.add_metric(
            BusinessMetric(
                name="flx_data_processing_errors_total",
                metric_type="counter",
                help_text="Total number of data processing errors",
                labels=["error_type", "source", "pipeline_id"],
                value_extractor=self._get_data_processing_errors,
            ),
        )

        # User activity metrics
        self.add_metric(
            BusinessMetric(
                name="flx_active_users_current",
                metric_type="gauge",
                help_text="Current number of active users",
                labels=["user_type"],
                value_extractor=self._get_active_users,
            ),
        )

        # System health metrics
        self.add_metric(
            BusinessMetric(
                name="flx_system_health_score",
                metric_type="gauge",
                help_text="Overall system health score (0-100)",
                labels=["component"],
                value_extractor=self._get_system_health_scores,
            ),
        )

    def add_metric(self, metric: BusinessMetric) -> None:
        """Add a custom business metric."""
        with self._collection_lock:
            self._metrics[metric.name] = metric
            self.logger.info(f"Registered business metric: {metric.name}")

    def remove_metric(self, name: str) -> bool:
        """Remove a business metric."""
        with self._collection_lock:
            if name in self._metrics:
                del self._metrics[name]
                self.logger.info(f"Removed business metric: {name}")
                return True
            return False

    def collect(self):
        """Collect all registered business metrics."""
        with self._collection_lock:
            collection_start = time.time()

            for metric_name, metric in self._metrics.items():
                if not metric.enabled:
                    continue

                try:
                    # Extract metric values
                    values = metric.value_extractor()

                    if metric.metric_type == "counter":
                        yield self._create_counter_metric(metric, values)
                    elif metric.metric_type == "gauge":
                        yield self._create_gauge_metric(metric, values)
                    elif metric.metric_type == "histogram":
                        yield self._create_histogram_metric(metric, values)

                except Exception as e:
                    self.logger.exception(
                        f"Failed to collect metric {metric_name}: {e}",
                    )
                    continue

            collection_duration = time.time() - collection_start
            self.logger.debug(
                f"Business metrics collection completed in {collection_duration:.3f}s",
            )

            self._last_collection = datetime.now(UTC)

    def _create_counter_metric(
        self, metric: BusinessMetric, values: dict[str, float] | float
    ):
        """Create a counter metric family."""
        counter_family = CounterMetricFamily(
            metric.name,
            metric.help_text,
            labels=metric.labels,
        )

        if isinstance(values, dict):
            for label_values, value in values.items():
                if isinstance(label_values, str):
                    label_values = [label_values]
                counter_family.add_metric(label_values, value)
        else:
            counter_family.add_metric([], values)

        return counter_family

    def _create_gauge_metric(
        self, metric: BusinessMetric, values: dict[str, float] | float
    ):
        """Create a gauge metric family."""
        gauge_family = GaugeMetricFamily(
            metric.name,
            metric.help_text,
            labels=metric.labels,
        )

        if isinstance(values, dict):
            for label_values, value in values.items():
                if isinstance(label_values, str):
                    label_values = [label_values]
                gauge_family.add_metric(label_values, value)
        else:
            gauge_family.add_metric([], values)

        return gauge_family

    def _create_histogram_metric(
        self, metric: BusinessMetric, values: dict[str, list[float]] | list[float]
    ):
        """Create a histogram metric family."""
        histogram_family = HistogramMetricFamily(
            metric.name,
            metric.help_text,
            labels=metric.labels,
        )

        # Define histogram buckets
        buckets = [
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
            float("inf"),
        ]

        if isinstance(values, dict):
            for label_values, data_points in values.items():
                if isinstance(label_values, str):
                    label_values = [label_values]

                # Calculate histogram buckets
                bucket_counts = [0] * len(buckets)
                len(data_points)
                total_sum = sum(data_points)

                for data_point in data_points:
                    for i, bucket_upper_bound in enumerate(buckets):
                        if data_point <= bucket_upper_bound:
                            bucket_counts[i] += 1

                # Add cumulative counts
                for i in range(1, len(bucket_counts)):
                    bucket_counts[i] += bucket_counts[i - 1]

                histogram_family.add_metric(
                    label_values,
                    buckets=list(zip(map(str, buckets), bucket_counts, strict=False)),
                    sum_value=total_sum,
                )

        return histogram_family

    def _get_pipeline_execution_counts(self) -> dict[str, float]:
        """Get pipeline execution counts by status."""
        # This would integrate with actual pipeline execution tracking
        # For now, return mock data
        return {
            ("pipeline_1", "success", "production"): 150.0,
            ("pipeline_1", "failed", "production"): 5.0,
            ("pipeline_2", "success", "production"): 200.0,
            ("pipeline_2", "failed", "production"): 2.0,
        }

    def _get_pipeline_durations(self) -> dict[str, list[float]]:
        """Get pipeline execution durations."""
        # Mock duration data
        return {
            ("pipeline_1", "production"): [1.2, 1.5, 1.8, 2.1, 1.9],
            ("pipeline_2", "production"): [0.8, 1.1, 0.9, 1.3, 1.0],
        }

    def _get_data_processing_counts(self) -> dict[str, float]:
        """Get data processing record counts."""
        return {
            ("source_db", "warehouse", "pipeline_1"): 50000.0,
            ("api_source", "warehouse", "pipeline_2"): 75000.0,
        }

    def _get_data_processing_errors(self) -> dict[str, float]:
        """Get data processing error counts."""
        return {
            ("validation_error", "source_db", "pipeline_1"): 15.0,
            ("connection_error", "api_source", "pipeline_2"): 3.0,
        }

    def _get_active_users(self) -> dict[str, float]:
        """Get current active user counts."""
        # This would integrate with authentication system
        return {
            ("admin",): 5.0,
            ("developer",): 12.0,
            ("analyst",): 25.0,
        }

    def _get_system_health_scores(self) -> dict[str, float]:
        """Get system health scores by component."""
        return {
            ("api",): 95.0,
            ("database",): 98.0,
            ("cache",): 92.0,
            ("queue",): 89.0,
        }


class CustomMetricsRegistry:
    """Registry for custom metrics with lifecycle management."""

    def __init__(self) -> None:
        """Initialize custom metrics registry."""
        self.logger = get_logger("metrics.registry")
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        self.collectors: dict[str, Collector] = {}
        self._initialized = False

        if PROMETHEUS_AVAILABLE:
            self._initialize_standard_metrics()
            self._initialize_business_collectors()

    def _initialize_standard_metrics(self) -> None:
        """Initialize standard platform metrics."""
        if not self.registry:
            return

        # Application info
        self.app_info = Info(
            "flx_app_info",
            "FLX application information",
            registry=self.registry,
        )
        config = get_config()
        self.app_info.info(
            {
                "version": getattr(config, "version", "1.0.0"),
                "environment": getattr(config, "environment", "development"),
                "deployment_date": datetime.now(UTC).isoformat(),
            },
        )

        # System metrics
        self.system_uptime = Gauge(
            "flx_system_uptime_seconds",
            "System uptime in seconds",
            registry=self.registry,
        )
        self.memory_usage = Gauge(
            "flx_memory_usage_bytes",
            "Memory usage in bytes",
            ["type"],
            registry=self.registry,
        )
        self.cpu_usage = Gauge(
            "flx_cpu_usage_percent",
            "CPU usage percentage",
            ["core"],
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits = Counter(
            "flx_cache_hits_total",
            "Total cache hits",
            ["cache_name"],
            registry=self.registry,
        )
        self.cache_misses = Counter(
            "flx_cache_misses_total",
            "Total cache misses",
            ["cache_name"],
            registry=self.registry,
        )
        self.cache_size = Gauge(
            "flx_cache_size_bytes",
            "Cache size in bytes",
            ["cache_name"],
            registry=self.registry,
        )

        # Database metrics
        self.db_connections_active = Gauge(
            "flx_db_connections_active",
            "Active database connections",
            registry=self.registry,
        )
        self.db_query_duration = Histogram(
            "flx_db_query_duration_seconds",
            "Database query duration",
            ["operation"],
            registry=self.registry,
        )
        self.db_errors = Counter(
            "flx_db_errors_total",
            "Database errors",
            ["error_type"],
            registry=self.registry,
        )

        # Queue metrics
        self.queue_size = Gauge(
            "flx_queue_size",
            "Queue size",
            ["queue_name"],
            registry=self.registry,
        )
        self.queue_processing_time = Histogram(
            "flx_queue_processing_seconds",
            "Queue processing time",
            ["queue_name"],
            registry=self.registry,
        )

        self.logger.info("Standard metrics initialized")

    def _initialize_business_collectors(self) -> None:
        """Initialize custom business metrics collectors."""
        if not self.registry:
            return

        # Register business metrics collector
        business_collector = FlxBusinessMetricsCollector()
        self.registry.register(business_collector)
        self.collectors["business"] = business_collector

        self.logger.info("Business metrics collectors initialized")

    def register_custom_metric(
        self,
        name: str,
        metric_type: str,
        help_text: str,
        labels: list[str] | None = None,
    ) -> Any:
        """Register a custom metric.

        Args:
        ----
            name: Metric name
            metric_type: Type of metric (counter, gauge, histogram, summary)
            help_text: Help text for the metric
            labels: Optional list of label names

        Returns:
        -------
            The created metric object

        """
        if not PROMETHEUS_AVAILABLE or not self.registry:
            self.logger.warning("Prometheus not available, metric not registered")
            return None

        labels = labels or []

        try:
            if metric_type == "counter":
                metric = Counter(name, help_text, labels, registry=self.registry)
            elif metric_type == "gauge":
                metric = Gauge(name, help_text, labels, registry=self.registry)
            elif metric_type == "histogram":
                metric = Histogram(name, help_text, labels, registry=self.registry)
            elif metric_type == "summary":
                metric = Summary(name, help_text, labels, registry=self.registry)
            else:
                msg = f"Unsupported metric type: {metric_type}"
                raise ValueError(msg)

            self.logger.info(f"Registered custom metric: {name} ({metric_type})")
            return metric

        except Exception as e:
            self.logger.exception(f"Failed to register metric {name}: {e}")
            return None

    def update_system_metrics(self) -> None:
        """Update system-level metrics."""
        if not PROMETHEUS_AVAILABLE:
            return

        # ZERO TOLERANCE CONSOLIDATION: Use centralized psutil import management
        psutil, psutil_available = get_psutil_module()

        if psutil and psutil_available:
            try:
                # Update memory metrics
                memory = psutil.virtual_memory()
                self.memory_usage.labels(type="used").set(memory.used)
                self.memory_usage.labels(type="available").set(memory.available)
                self.memory_usage.labels(type="total").set(memory.total)

                # Update CPU metrics
                cpu_percent = psutil.cpu_percent(percpu=True)
                for i, cpu in enumerate(cpu_percent):
                    self.cpu_usage.labels(core=str(i)).set(cpu)

            except (AttributeError, ValueError, TypeError) as e:
                self.logger.exception(
                    f"Failed to update system metrics with psutil: {e}",
                )
        else:
            self.logger.debug("psutil not available, system metrics not updated")

    def get_metrics_output(self) -> str:
        """Get Prometheus metrics output."""
        if not PROMETHEUS_AVAILABLE or not self.registry:
            return "# Prometheus not available\n"

        try:
            self.update_system_metrics()
            return generate_latest(self.registry).decode("utf-8")
        except Exception as e:
            self.logger.exception(f"Failed to generate metrics output: {e}")
            return f"# Error generating metrics: {e}\n"

    def get_content_type(self) -> str:
        """Get Prometheus content type."""
        return CONTENT_TYPE_LATEST if PROMETHEUS_AVAILABLE else "text/plain"


class MetricsManager:
    """Centralized metrics management for the FLX platform."""

    _instance: MetricsManager | None = None
    _lock = threading.Lock()

    def __new__(cls) -> Self:
        """Singleton pattern for metrics manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize metrics manager."""
        if hasattr(self, "_initialized"):
            return

        self.logger = get_logger("metrics.manager")
        self.registry = CustomMetricsRegistry()
        self._performance_data: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000),
        )
        self._business_metrics: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._initialized = True

        self.logger.info("Metrics manager initialized")

    def record_performance_metric(
        self, operation: str, duration_ms: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a performance metric.

        Args:
        ----
            operation: Operation name
            duration_ms: Duration in milliseconds
            tags: Optional tags for the metric

        """
        with self._lock:
            timestamp = datetime.now(UTC)

            # Store in local buffer
            self._performance_data[operation].append(
                {
                    "duration_ms": duration_ms,
                    "timestamp": timestamp,
                    "tags": tags or {},
                },
            )

            # Update Prometheus histogram if available
            if hasattr(self.registry, "queue_processing_time"):
                # Use appropriate metric based on operation type
                if "queue" in operation.lower():
                    self.registry.queue_processing_time.labels(
                        queue_name=operation,
                    ).observe(duration_ms / 1000)

    def record_business_metric(
        self, metric_name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Record a business metric.

        Args:
        ----
            metric_name: Name of the business metric
            value: Metric value
            labels: Optional labels for the metric

        """
        with self._lock:
            key = f"{metric_name}:{':'.join(sorted((labels or {}).items()))}"
            self._business_metrics[key] = {
                "value": value,
                "labels": labels or {},
                "timestamp": datetime.now(UTC),
            }

    def get_performance_summary(self, operation: str | None = None) -> dict[str, Any]:
        """Get performance metrics summary.

        Args:
        ----
            operation: Optional operation name to filter by

        Returns:
        -------
            Performance metrics summary

        """
        with self._lock:
            if operation:
                operations = {operation: self._performance_data.get(operation, deque())}
            else:
                operations = dict(self._performance_data)

            summary = {}

            for op_name, data_points in operations.items():
                if not data_points:
                    continue

                durations = [point["duration_ms"] for point in data_points]
                durations.sort()

                n = len(durations)
                summary[op_name] = {
                    "count": n,
                    "avg": sum(durations) / n,
                    "min": min(durations),
                    "max": max(durations),
                    "p50": durations[int(n * 0.5)] if n > 0 else 0,
                    "p95": durations[int(n * 0.95)] if n > 0 else 0,
                    "p99": durations[int(n * 0.99)] if n > 0 else 0,
                }

            return summary

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus-formatted metrics."""
        return self.registry.get_metrics_output()

    def get_metrics_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return self.registry.get_content_type()


# Global metrics manager instance
metrics_manager = MetricsManager()


def record_operation_duration(operation: str, duration_ms: float, **tags) -> None:
    """Convenience function to record operation duration.

    Args:
    ----
        operation: Operation name
        duration_ms: Duration in milliseconds
        **tags: Additional tags for the metric

    """
    metrics_manager.record_performance_metric(operation, duration_ms, tags)


def record_business_metric(name: str, value: float, **labels) -> None:
    """Convenience function to record business metric.

    Args:
    ----
        name: Metric name
        value: Metric value
        **labels: Labels for the metric

    """
    metrics_manager.record_business_metric(name, value, labels)


def get_metrics_endpoint_handler():
    """Get FastAPI handler for metrics endpoint.

    Returns
    -------
        FastAPI endpoint function for serving Prometheus metrics

    """

    async def metrics_endpoint():
        """Serve Prometheus metrics."""
        from fastapi import Response

        content = metrics_manager.get_prometheus_metrics()
        content_type = metrics_manager.get_metrics_content_type()

        return Response(content=content, media_type=content_type)

    return metrics_endpoint
