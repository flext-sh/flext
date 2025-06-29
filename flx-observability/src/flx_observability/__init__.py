"""Monitoring components for FLX platform."""

from flx_observability.business_metrics import (
    AlertSeverity,
    BusinessAlert,
    BusinessMetric,
    BusinessMetricType,
    EnterpriseBusinessMetrics,
)
from flx_observability.error_patterns import (
    ErrorCategory,
    ErrorInstance,
    ErrorPattern,
    ErrorSeverity,
    ProductionErrorHandler,
    RecoveryAction,
)
from flx_observability.health import ComponentHealth, HealthChecker, HealthStatus
from flx_observability.metrics import MetricsCollector
from flx_observability.tracing import setup_tracing, trace_method

__all__ = [
    # Business metrics and alerting
    "AlertSeverity",
    "BusinessAlert",
    "BusinessMetric",
    "BusinessMetricType",
    # Health monitoring
    "ComponentHealth",
    "EnterpriseBusinessMetrics",
    # Error handling and recovery
    "ErrorCategory",
    "ErrorInstance",
    "ErrorPattern",
    "ErrorSeverity",
    "HealthChecker",
    "HealthStatus",
    # Metrics collection
    "MetricsCollector",
    "ProductionErrorHandler",
    "RecoveryAction",
    # Distributed tracing
    "setup_tracing",
    "trace_method",
]
