"""Enterprise monitoring middleware for FastAPI and gRPC applications.

This module provides comprehensive middleware for monitoring HTTP requests, gRPC calls,
performance metrics, security events, and integration with observability systems.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from flx_core.config.domain_config import get_config, get_domain_constants

# ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus import management
from flx_core.utils.import_fallback_patterns import get_prometheus_components
from pydantic import BaseModel, Field

from flx_observability.structured_logging import (
    LoggingMiddleware,
    StructuredLogger,
    audit_logger,
    get_logger,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import Request, Response


class RequestMetrics(BaseModel):
    """Comprehensive request metrics for monitoring and analytics."""

    request_id: str = Field(description="Unique request identifier")
    correlation_id: str = Field(description="Correlation ID for distributed tracing")
    method: str = Field(description="HTTP method")
    path: str = Field(description="Request path")
    query_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Query parameters",
    )
    headers: dict[str, str] = Field(default_factory=dict, description="Request headers")
    user_id: str | None = Field(default=None, description="Authenticated user ID")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="User agent string")
    start_time: float = Field(description="Request start timestamp")
    end_time: float | None = Field(default=None, description="Request end timestamp")
    duration_ms: float | None = Field(
        default=None,
        description="Request duration in milliseconds",
    )
    status_code: int | None = Field(default=None, description="HTTP status code")
    response_size: int | None = Field(
        default=None,
        description="Response size in bytes",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if request failed",
    )
    rate_limit_hit: bool = Field(
        default=False,
        description="Whether rate limit was hit",
    )
    cache_hit: bool = Field(
        default=False,
        description="Whether response was served from cache",
    )

    @property
    def is_success(self) -> bool:
        """Check if request was successful."""
        return self.status_code is not None and 200 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        """Check if request had client error."""
        return self.status_code is not None and 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if request had server error."""
        return self.status_code is not None and 500 <= self.status_code < 600

    def finish(
        self, status_code: int, response_size: int = 0, error_message: str | None = None
    ) -> None:
        """Mark request as finished and calculate metrics."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status_code = status_code
        self.response_size = response_size
        self.error_message = error_message


@dataclass
class RateLimitInfo:
    """Rate limiting information for monitoring."""

    enabled: bool = False
    requests_per_minute: int = 0
    current_count: int = 0
    window_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    remaining_requests: int = 0
    reset_time: datetime = field(default_factory=lambda: datetime.now(UTC))


class SecurityEventDetector:
    """Detects and logs security events from request patterns."""

    def __init__(self) -> None:
        """Initialize security event detector."""
        self.logger = get_logger("security.detector")
        self.failed_attempts: dict[str, list[datetime]] = defaultdict(list)
        self.blocked_ips: set[str] = set()
        self.suspicious_patterns: dict[str, int] = defaultdict(int)

    def analyze_request(self, metrics: RequestMetrics) -> list[str]:
        """Analyze request for security events and return detected events."""
        events = []

        # Check for brute force attacks
        if metrics.is_client_error and metrics.status_code == 401:
            events.extend(self._check_brute_force(metrics))

        # Check for suspicious patterns
        if self._is_suspicious_path(metrics.path):
            events.append("suspicious_path_access")

        # Check for rate limit violations
        if metrics.rate_limit_hit:
            events.append("rate_limit_violation")

        # Check for SQL injection patterns
        if self._check_sql_injection(metrics):
            events.append("sql_injection_attempt")

        # Check for XSS patterns
        if self._check_xss_attempt(metrics):
            events.append("xss_attempt")

        return events

    def _check_brute_force(self, metrics: RequestMetrics) -> list[str]:
        """Check for brute force attack patterns."""
        events = []

        if not metrics.ip_address:
            return events

        # Track failed attempts per IP
        now = datetime.now(UTC)
        ip_attempts = self.failed_attempts[metrics.ip_address]

        # Remove old attempts (older than 5 minutes)
        cutoff = now.timestamp() - 300  # 5 minutes
        ip_attempts[:] = [
            attempt for attempt in ip_attempts if attempt.timestamp() > cutoff
        ]

        # Add current attempt
        ip_attempts.append(now)

        # Check if threshold exceeded
        constants = get_domain_constants()
        threshold = getattr(constants, "BRUTE_FORCE_THRESHOLD", 5)

        if len(ip_attempts) >= threshold:
            events.append("brute_force_attack")
            self.blocked_ips.add(metrics.ip_address)

            audit_logger.log_security_event(
                event_type="brute_force_attack",
                severity="high",
                description=f"Brute force attack detected from {metrics.ip_address}",
                user_id=metrics.user_id,
                ip_address=metrics.ip_address,
            )

        return events

    def _is_suspicious_path(self, path: str) -> bool:
        """Check if path contains suspicious patterns."""
        suspicious_patterns = [
            "/.env",
            "/wp-admin",
            "/admin",
            "/config",
            "/backup",
            "/.git",
            "/database",
            "/phpMyAdmin",
            "/etc/passwd",
            "../",
            "..\\",
            "<script",
            "javascript:",
            "eval(",
        ]

        path_lower = path.lower()
        return any(pattern in path_lower for pattern in suspicious_patterns)

    def _check_sql_injection(self, metrics: RequestMetrics) -> bool:
        """Check for SQL injection patterns in query parameters."""
        sql_patterns = [
            "union select",
            "drop table",
            "delete from",
            "insert into",
            "update set",
            "or 1=1",
            "and 1=1",
            "'=0--",
            "xp_cmdshell",
        ]

        # Check query parameters
        for value in metrics.query_params.values():
            if isinstance(value, str):
                value_lower = value.lower()
                if any(pattern in value_lower for pattern in sql_patterns):
                    return True

        return False

    def _check_xss_attempt(self, metrics: RequestMetrics) -> bool:
        """Check for XSS attempt patterns."""
        xss_patterns = [
            "<script",
            "javascript:",
            "onerror=",
            "onload=",
            "onclick=",
            "alert(",
            "document.cookie",
            "window.location",
            "eval(",
        ]

        # Check query parameters
        for value in metrics.query_params.values():
            if isinstance(value, str):
                value_lower = value.lower()
                if any(pattern in value_lower for pattern in xss_patterns):
                    return True

        return False

    def is_blocked_ip(self, ip_address: str) -> bool:
        """Check if IP address is blocked."""
        return ip_address in self.blocked_ips


class EnterpriseMonitoringMiddleware:
    """Enterprise-grade monitoring middleware for FastAPI applications.

    Provides comprehensive monitoring including:
    - Request/response metrics and logging
    - Performance tracking with percentiles
    - Security event detection and alerting
    - Rate limiting integration
    - Custom business metrics
    - Integration with observability systems
    """

    def __init__(
        self,
        app_name: str,
        enable_security_detection: bool = True,
        enable_rate_limiting: bool = False,
        enable_prometheus: bool = True,
        sensitive_headers: list[str] | None = None,
    ) -> None:
        """Initialize enterprise monitoring middleware.

        Args:
        ----
            app_name: Application name for monitoring context
            enable_security_detection: Enable security event detection
            enable_rate_limiting: Enable rate limiting integration
            enable_prometheus: Enable Prometheus metrics collection
            sensitive_headers: List of sensitive headers to exclude from logs

        """
        self.app_name = app_name
        self.enable_security_detection = enable_security_detection
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_prometheus = enable_prometheus
        self.sensitive_headers = sensitive_headers or [
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token",
        ]

        # Initialize components
        self.logger = get_logger(f"middleware.{app_name}")
        self.base_middleware = LoggingMiddleware(app_name)

        if enable_security_detection:
            self.security_detector = SecurityEventDetector()
        else:
            self.security_detector = None

        # Performance tracking
        self.request_counts: dict[str, int] = defaultdict(int)
        self.response_times: dict[str, list[float]] = defaultdict(list)
        self.error_counts: dict[str, int] = defaultdict(int)

        # Initialize Prometheus metrics if enabled
        if enable_prometheus:
            self._init_prometheus_metrics()

    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics collectors."""
        # ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus import management
        prometheus_available, prometheus_components = get_prometheus_components()

        if prometheus_available:
            Counter = prometheus_components.get("Counter")
            Histogram = prometheus_components.get("Histogram")
            Gauge = prometheus_components.get("Gauge")
            Info = prometheus_components.get("Info")

            if Counter and Histogram and Gauge and Info:
                # Request metrics
                self.request_counter = Counter(
                    "http_requests_total",
                    "Total HTTP requests",
                    ["method", "endpoint", "status"],
                )

                self.request_duration = Histogram(
                    "http_request_duration_seconds",
                    "HTTP request duration",
                    ["method", "endpoint"],
                )

                self.request_size = Histogram(
                    "http_request_size_bytes",
                    "HTTP request size",
                    ["method", "endpoint"],
                )

                self.response_size = Histogram(
                    "http_response_size_bytes",
                    "HTTP response size",
                    ["method", "endpoint"],
                )

                # Security metrics
                self.security_events = Counter(
                    "security_events_total",
                    "Total security events detected",
                    ["event_type", "severity"],
                )

                # Application metrics
                self.active_requests = Gauge(
                    "http_requests_active",
                    "Number of active HTTP requests",
                )

                self.app_info = Info(
                    "app_info",
                    "Application information",
                )

                # Set application info
                config = get_config()
                self.app_info.info(
                    {
                        "name": self.app_name,
                        "version": getattr(config, "version", "1.0.0"),
                        "environment": getattr(config, "environment", "development"),
                    },
                )
            else:
                self.logger.warning(
                    "Some Prometheus components not available, metrics disabled",
                )
                self.enable_prometheus = False
        else:
            self.logger.warning("Prometheus client not available, metrics disabled")
            self.enable_prometheus = False

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive monitoring."""
        # Create request metrics
        metrics = self._create_request_metrics(request)

        # Security check
        if self.security_detector and self.security_detector.is_blocked_ip(
            metrics.ip_address or "",
        ):
            return self._create_blocked_response()

        # Update active requests counter
        if self.enable_prometheus:
            self.active_requests.inc()

        try:
            # Enhanced logging context
            enhanced_logger = self.logger.with_context(
                request_id=metrics.request_id,
                correlation_id=metrics.correlation_id,
                user_id=metrics.user_id,
                ip_address=metrics.ip_address,
            )

            enhanced_logger.info(
                "Request started",
                method=metrics.method,
                path=metrics.path,
                user_agent=metrics.user_agent,
            )

            # Process request with performance tracking
            with enhanced_logger.performance_context(
                f"request_{metrics.method}_{metrics.path}",
            ):
                response = await call_next(request)

                # Extract response information
                response_size = 0
                if hasattr(response, "body"):
                    response_size = len(response.body) if response.body else 0

                # Finish metrics
                metrics.finish(
                    status_code=response.status_code,
                    response_size=response_size,
                )

                # Log completion
                enhanced_logger.info(
                    "Request completed",
                    status_code=metrics.status_code,
                    duration_ms=metrics.duration_ms,
                    response_size=metrics.response_size,
                )

                # Security analysis
                if self.security_detector:
                    security_events = self.security_detector.analyze_request(metrics)
                    if security_events:
                        enhanced_logger.warning(
                            "Security events detected",
                            events=security_events,
                            ip_address=metrics.ip_address,
                        )

                        # Update Prometheus security metrics
                        if self.enable_prometheus:
                            for event in security_events:
                                self.security_events.labels(
                                    event_type=event,
                                    severity="medium",
                                ).inc()

                # Update metrics
                self._update_metrics(metrics)

                return response

        except Exception as e:
            # Handle request failure
            metrics.finish(
                status_code=500,
                error_message=str(e),
            )

            enhanced_logger.exception(
                "Request failed",
                error=str(e),
                duration_ms=metrics.duration_ms,
            )

            # Update error metrics
            if self.enable_prometheus:
                self.request_counter.labels(
                    method=metrics.method,
                    endpoint=self._sanitize_path(metrics.path),
                    status="500",
                ).inc()

            self._update_metrics(metrics)
            raise

        finally:
            # Update active requests counter
            if self.enable_prometheus:
                self.active_requests.dec()

    def _create_request_metrics(self, request: Request) -> RequestMetrics:
        """Create comprehensive request metrics."""
        # Extract client information
        ip_address = self._extract_client_ip(request)
        user_agent = request.headers.get("user-agent")

        # Create filtered headers (exclude sensitive)
        filtered_headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in self.sensitive_headers
        }

        # Extract query parameters
        query_params = dict(request.query_params) if request.query_params else {}

        # Generate IDs
        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))

        return RequestMetrics(
            request_id=request_id,
            correlation_id=correlation_id,
            method=request.method,
            path=str(request.url.path),
            query_params=query_params,
            headers=filtered_headers,
            ip_address=ip_address,
            user_agent=user_agent,
            start_time=time.time(),
        )

    def _extract_client_ip(self, request: Request) -> str | None:
        """Extract client IP address from request headers."""
        # Check common headers for client IP
        ip_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-client-ip",
            "cf-connecting-ip",  # Cloudflare
            "x-forwarded",
            "forwarded-for",
            "forwarded",
        ]

        for header in ip_headers:
            ip = request.headers.get(header)
            if ip:
                # Take first IP if comma-separated
                return ip.split(",")[0].strip()

        # Fallback to client host
        if hasattr(request.client, "host"):
            return request.client.host

        return None

    def _sanitize_path(self, path: str) -> str:
        """Sanitize path for metrics to avoid high cardinality."""
        # Replace IDs and UUIDs with placeholders
        import re

        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            f"/{uuid}",
            path,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs
        return re.sub(r"/\d+", "/{id}", path)

    def _update_metrics(self, metrics: RequestMetrics) -> None:
        """Update internal and Prometheus metrics."""
        # Update internal metrics
        endpoint = self._sanitize_path(metrics.path)
        key = f"{metrics.method}:{endpoint}"

        self.request_counts[key] += 1

        if metrics.duration_ms is not None:
            self.response_times[key].append(metrics.duration_ms)

            # Keep only last 1000 response times per endpoint
            if len(self.response_times[key]) > 1000:
                self.response_times[key] = self.response_times[key][-1000:]

        if not metrics.is_success:
            self.error_counts[key] += 1

        # Update Prometheus metrics
        if self.enable_prometheus:
            self.request_counter.labels(
                method=metrics.method,
                endpoint=endpoint,
                status=str(metrics.status_code or "unknown"),
            ).inc()

            if metrics.duration_ms is not None:
                self.request_duration.labels(
                    method=metrics.method,
                    endpoint=endpoint,
                ).observe(metrics.duration_ms / 1000)  # Convert to seconds

            if metrics.response_size is not None:
                self.response_size.labels(
                    method=metrics.method,
                    endpoint=endpoint,
                ).observe(metrics.response_size)

    def _create_blocked_response(self) -> Response:
        """Create response for blocked requests."""
        from fastapi import Response

        return Response(
            content={"error": "Access denied", "code": "IP_BLOCKED"},
            status_code=403,
            media_type="application/json",
        )

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary."""
        summary = {
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "endpoints": {},
        }

        for endpoint, count in self.request_counts.items():
            response_times = self.response_times.get(endpoint, [])
            error_count = self.error_counts.get(endpoint, 0)

            endpoint_metrics = {
                "request_count": count,
                "error_count": error_count,
                "error_rate": error_count / count if count > 0 else 0,
            }

            if response_times:
                response_times.sort()
                n = len(response_times)
                endpoint_metrics.update(
                    {
                        "avg_response_time": sum(response_times) / n,
                        "p50_response_time": response_times[int(n * 0.5)],
                        "p95_response_time": response_times[int(n * 0.95)],
                        "p99_response_time": response_times[int(n * 0.99)],
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                    },
                )

            summary["endpoints"][endpoint] = endpoint_metrics

        return summary


@asynccontextmanager
async def monitoring_context(
    operation_name: str,
    logger: StructuredLogger | None = None,
    metrics_tags: dict[str, str] | None = None,
):
    """Async context manager for operation monitoring with custom metrics.

    Args:
    ----
        operation_name: Name of the operation being monitored
        logger: Optional custom logger instance
        metrics_tags: Optional additional tags for metrics

    Yields:
    ------
        RequestMetrics: Metrics object for the operation

    """
    if logger is None:
        logger = get_logger("operation.monitor")

    # Create operation metrics
    start_time = time.time()
    operation_id = str(uuid.uuid4())

    logger.info(
        f"Operation started: {operation_name}",
        operation_id=operation_id,
        operation_name=operation_name,
        **(metrics_tags or {}),
    )

    try:
        # Yield a simple metrics object
        metrics = type(
            "OperationMetrics",
            (),
            {
                "operation_id": operation_id,
                "operation_name": operation_name,
                "start_time": start_time,
                "end_time": None,
                "duration_ms": None,
                "success": False,
            },
        )()

        yield metrics

        # Mark as successful
        metrics.success = True

    except Exception as e:
        logger.exception(
            f"Operation failed: {operation_name}",
            operation_id=operation_id,
            operation_name=operation_name,
            error=str(e),
            **(metrics_tags or {}),
        )
        raise

    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        metrics.end_time = end_time
        metrics.duration_ms = duration_ms

        logger.info(
            f"Operation completed: {operation_name}",
            operation_id=operation_id,
            operation_name=operation_name,
            duration_ms=duration_ms,
            success=getattr(metrics, "success", False),
            **(metrics_tags or {}),
        )
