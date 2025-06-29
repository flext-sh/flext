"""Enterprise gRPC interceptors for monitoring and observability.

This module provides comprehensive gRPC interceptors for monitoring RPC calls,
performance metrics, security events, and integration with observability systems.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import grpc
from flx_core.config.domain_config import get_domain_constants

# ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus import management
from flx_core.utils.import_fallback_patterns import get_prometheus_components
from pydantic import BaseModel, Field

from flx_observability.structured_logging import audit_logger, get_logger

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class GrpcCallMetrics(BaseModel):
    """Comprehensive gRPC call metrics for monitoring and analytics."""

    call_id: str = Field(description="Unique call identifier")
    correlation_id: str = Field(description="Correlation ID for distributed tracing")
    service_name: str = Field(description="gRPC service name")
    method_name: str = Field(description="gRPC method name")
    full_method: str = Field(description="Full method name (service/method)")
    client_address: str | None = Field(default=None, description="Client address")
    user_id: str | None = Field(default=None, description="Authenticated user ID")
    request_size: int | None = Field(default=None, description="Request size in bytes")
    response_size: int | None = Field(
        default=None,
        description="Response size in bytes",
    )
    start_time: float = Field(description="Call start timestamp")
    end_time: float | None = Field(default=None, description="Call end timestamp")
    duration_ms: float | None = Field(
        default=None,
        description="Call duration in milliseconds",
    )
    status_code: grpc.StatusCode | None = Field(
        default=None,
        description="gRPC status code",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if call failed",
    )
    metadata: dict[str, str] = Field(
        default_factory=dict,
        description="Request metadata",
    )

    @property
    def is_success(self) -> bool:
        """Check if call was successful."""
        return self.status_code == grpc.StatusCode.OK

    @property
    def is_client_error(self) -> bool:
        """Check if call had client error."""
        return self.status_code in {
            grpc.StatusCode.INVALID_ARGUMENT,
            grpc.StatusCode.NOT_FOUND,
            grpc.StatusCode.ALREADY_EXISTS,
            grpc.StatusCode.PERMISSION_DENIED,
            grpc.StatusCode.UNAUTHENTICATED,
        }

    @property
    def is_server_error(self) -> bool:
        """Check if call had server error."""
        return self.status_code in {
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.UNIMPLEMENTED,
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DATA_LOSS,
        }

    def finish(
        self,
        status_code: grpc.StatusCode,
        response_size: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Mark call as finished and calculate metrics."""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status_code = status_code
        self.response_size = response_size
        self.error_message = error_message


class GrpcSecurityAnalyzer:
    """Analyzes gRPC calls for security events and anomalies."""

    def __init__(self) -> None:
        """Initialize security analyzer."""
        self.logger = get_logger("grpc.security")
        self.call_patterns: dict[str, list[datetime]] = defaultdict(list)
        self.blocked_clients: set[str] = set()
        self.suspicious_methods: set[str] = {
            "/reflection.v1alpha.ServerReflection/ServerReflectionInfo",
            "/grpc.health.v1.Health/Check",
        }

    def analyze_call(self, metrics: GrpcCallMetrics) -> list[str]:
        """Analyze gRPC call for security events."""
        events = []

        # Check for rate limiting violations
        if self._check_rate_limit_violation(metrics):
            events.append("rate_limit_violation")

        # Check for authentication failures
        if metrics.status_code == grpc.StatusCode.UNAUTHENTICATED:
            events.extend(self._check_auth_failures(metrics))

        # Check for suspicious method calls
        if self._is_suspicious_method(metrics.full_method):
            events.append("suspicious_method_call")

        # Check for large payload attacks
        if self._check_large_payload(metrics):
            events.append("large_payload_attack")

        return events

    def _check_rate_limit_violation(self, metrics: GrpcCallMetrics) -> bool:
        """Check for rate limiting violations."""
        if not metrics.client_address:
            return False

        # Track calls per client
        now = datetime.now(UTC)
        client_calls = self.call_patterns[metrics.client_address]

        # Remove old calls (older than 1 minute)
        cutoff = now.timestamp() - 60
        client_calls[:] = [
            call_time for call_time in client_calls if call_time.timestamp() > cutoff
        ]

        # Add current call
        client_calls.append(now)

        # Check threshold
        rate_limit = 100  # calls per minute
        return len(client_calls) > rate_limit

    def _check_auth_failures(self, metrics: GrpcCallMetrics) -> list[str]:
        """Check for authentication failure patterns."""
        events = []

        if not metrics.client_address:
            return events

        # Similar to HTTP brute force detection
        now = datetime.now(UTC)
        failure_key = f"{metrics.client_address}:auth_failures"
        failures = self.call_patterns[failure_key]

        # Remove old failures
        cutoff = now.timestamp() - 300  # 5 minutes
        failures[:] = [failure for failure in failures if failure.timestamp() > cutoff]

        # Add current failure
        failures.append(now)

        # Check threshold
        if len(failures) >= 10:
            events.append("grpc_auth_brute_force")
            self.blocked_clients.add(metrics.client_address)

            audit_logger.log_security_event(
                event_type="grpc_auth_brute_force",
                severity="high",
                description=f"gRPC authentication brute force from {metrics.client_address}",
                ip_address=metrics.client_address,
            )

        return events

    def _is_suspicious_method(self, method: str) -> bool:
        """Check if method is suspicious."""
        return method in self.suspicious_methods

    def _check_large_payload(self, metrics: GrpcCallMetrics) -> bool:
        """Check for unusually large payloads."""
        constants = get_domain_constants()
        mb_to_bytes = int(
            constants.MEMORY_UNIT_CONVERSION * constants.MEMORY_UNIT_CONVERSION,
        )
        max_size = constants.GRPC_LARGE_PAYLOAD_THRESHOLD_MB * mb_to_bytes

        if metrics.request_size and metrics.request_size > max_size:
            return True

        return bool(metrics.response_size and metrics.response_size > max_size)

    def is_blocked_client(self, client_address: str) -> bool:
        """Check if client is blocked."""
        return client_address in self.blocked_clients


class EnterpriseGrpcInterceptor(grpc.ServerInterceptor):
    """Enterprise-grade gRPC server interceptor for comprehensive monitoring."""

    def __init__(
        self,
        service_name: str,
        enable_security_analysis: bool = True,
        enable_prometheus: bool = True,
        sensitive_metadata: list[str] | None = None,
    ) -> None:
        """Initialize gRPC interceptor.

        Args:
        ----
            service_name: Service name for monitoring context
            enable_security_analysis: Enable security event analysis
            enable_prometheus: Enable Prometheus metrics collection
            sensitive_metadata: List of sensitive metadata keys to exclude

        """
        self.service_name = service_name
        self.enable_security_analysis = enable_security_analysis
        self.enable_prometheus = enable_prometheus
        self.sensitive_metadata = sensitive_metadata or [
            "authorization",
            "x-api-key",
            "x-auth-token",
            "cookie",
        ]

        # Initialize components
        self.logger = get_logger(f"grpc.{service_name}")

        if enable_security_analysis:
            self.security_analyzer = GrpcSecurityAnalyzer()
        else:
            self.security_analyzer = None

        # Performance tracking
        self.call_counts: dict[str, int] = defaultdict(int)
        self.response_times: dict[str, list[float]] = defaultdict(list)
        self.error_counts: dict[str, int] = defaultdict(int)

        # Initialize Prometheus metrics
        if enable_prometheus:
            self._init_prometheus_metrics()

    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics for gRPC calls."""
        # ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus import management
        prometheus_available, prometheus_components = get_prometheus_components()

        if prometheus_available:
            Counter = prometheus_components.get("Counter")
            Histogram = prometheus_components.get("Histogram")
            Gauge = prometheus_components.get("Gauge")

            if Counter and Histogram and Gauge:
                # Call metrics
                self.call_counter = Counter(
                    "grpc_calls_total",
                    "Total gRPC calls",
                    ["service", "method", "status"],
                )

                self.call_duration = Histogram(
                    "grpc_call_duration_seconds",
                    "gRPC call duration",
                    ["service", "method"],
                )

                self.request_size = Histogram(
                    "grpc_request_size_bytes",
                    "gRPC request size",
                    ["service", "method"],
                )

                self.response_size = Histogram(
                    "grpc_response_size_bytes",
                    "gRPC response size",
                    ["service", "method"],
                )

                # Active calls
                self.active_calls = Gauge(
                    "grpc_calls_active",
                    "Number of active gRPC calls",
                    ["service"],
                )
            else:
                self.logger.warning(
                    "Some Prometheus components not available, metrics disabled",
                )
                self.enable_prometheus = False
        else:
            self.logger.warning("Prometheus client not available, metrics disabled")
            self.enable_prometheus = False

    def intercept_service(
        self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails
    ):
        """Intercept gRPC service calls for monitoring."""

        def monitor_wrapper(behavior: Callable):
            def monitored_behavior(
                request_iterator: Iterator, context: grpc.ServicerContext
            ):
                # Create call metrics
                metrics = self._create_call_metrics(handler_call_details, context)

                # Security check
                if self.security_analyzer and self.security_analyzer.is_blocked_client(
                    metrics.client_address or "",
                ):
                    context.abort(grpc.StatusCode.PERMISSION_DENIED, "Client blocked")

                # Update active calls
                if self.enable_prometheus:
                    self.active_calls.labels(service=self.service_name).inc()

                try:
                    # Enhanced logging
                    enhanced_logger = self.logger.with_context(
                        call_id=metrics.call_id,
                        correlation_id=metrics.correlation_id,
                        service=metrics.service_name,
                        method=metrics.method_name,
                        client_address=metrics.client_address,
                    )

                    enhanced_logger.info(
                        "gRPC call started",
                        full_method=metrics.full_method,
                        client_address=metrics.client_address,
                    )

                    # Process call with performance tracking
                    with enhanced_logger.performance_context(
                        f"grpc_{metrics.full_method}",
                    ):
                        # Handle streaming vs unary calls
                        if callable(behavior):
                            # Unary call
                            response = behavior(request_iterator, context)
                        else:
                            # Streaming call
                            response = behavior(request_iterator, context)

                        # Calculate response size if possible
                        response_size = 0
                        if hasattr(response, "ByteSize"):
                            response_size = response.ByteSize()
                        elif hasattr(response, "__sizeof__"):
                            response_size = response.__sizeof__()

                        # Finish metrics
                        metrics.finish(
                            status_code=grpc.StatusCode.OK,
                            response_size=response_size,
                        )

                        # Log completion
                        enhanced_logger.info(
                            "gRPC call completed",
                            status_code="OK",
                            duration_ms=metrics.duration_ms,
                            response_size=metrics.response_size,
                        )

                        # Security analysis
                        if self.security_analyzer:
                            security_events = self.security_analyzer.analyze_call(
                                metrics,
                            )
                            if security_events:
                                enhanced_logger.warning(
                                    "Security events detected in gRPC call",
                                    events=security_events,
                                    client_address=metrics.client_address,
                                )

                        # Update metrics
                        self._update_metrics(metrics)

                        return response

                except grpc.RpcError as e:
                    # Handle gRPC-specific errors
                    status_code = (
                        e.code() if hasattr(e, "code") else grpc.StatusCode.UNKNOWN
                    )
                    error_message = e.details() if hasattr(e, "details") else str(e)

                    metrics.finish(
                        status_code=status_code,
                        error_message=error_message,
                    )

                    enhanced_logger.exception(
                        "gRPC call failed",
                        status_code=status_code.name,
                        error=error_message,
                        duration_ms=metrics.duration_ms,
                    )

                    self._update_metrics(metrics)
                    raise

                except Exception as e:
                    # Handle general exceptions
                    metrics.finish(
                        status_code=grpc.StatusCode.INTERNAL,
                        error_message=str(e),
                    )

                    enhanced_logger.exception(
                        "gRPC call failed with exception",
                        error=str(e),
                        duration_ms=metrics.duration_ms,
                    )

                    self._update_metrics(metrics)
                    context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {e}")

                finally:
                    # Update active calls
                    if self.enable_prometheus:
                        self.active_calls.labels(service=self.service_name).dec()

            return monitored_behavior

        # Get the original handler
        handler = continuation(handler_call_details)

        # Wrap the handler behavior if it exists
        if handler and handler.unary_unary:
            handler = handler._replace(unary_unary=monitor_wrapper(handler.unary_unary))
        elif handler and handler.unary_stream:
            handler = handler._replace(
                unary_stream=monitor_wrapper(handler.unary_stream),
            )
        elif handler and handler.stream_unary:
            handler = handler._replace(
                stream_unary=monitor_wrapper(handler.stream_unary),
            )
        elif handler and handler.stream_stream:
            handler = handler._replace(
                stream_stream=monitor_wrapper(handler.stream_stream),
            )

        return handler

    def _create_call_metrics(
        self,
        handler_call_details: grpc.HandlerCallDetails,
        context: grpc.ServicerContext,
    ) -> GrpcCallMetrics:
        """Create comprehensive call metrics."""
        # Parse method information
        full_method = handler_call_details.method
        method_parts = full_method.split("/")
        service_name = method_parts[1] if len(method_parts) > 1 else "unknown"
        method_name = method_parts[2] if len(method_parts) > 2 else "unknown"

        # Extract client information
        peer = context.peer() if context else None
        client_address = peer.split(":")[0] if peer and ":" in peer else peer

        # Extract metadata
        metadata = dict(context.invocation_metadata()) if context else {}

        # Filter sensitive metadata
        filtered_metadata = {
            k: v
            for k, v in metadata.items()
            if k.lower() not in self.sensitive_metadata
        }

        # Generate IDs
        call_id = str(uuid.uuid4())
        correlation_id = metadata.get("x-correlation-id", str(uuid.uuid4()))

        return GrpcCallMetrics(
            call_id=call_id,
            correlation_id=correlation_id,
            service_name=service_name,
            method_name=method_name,
            full_method=full_method,
            client_address=client_address,
            metadata=filtered_metadata,
            start_time=time.time(),
        )

    def _update_metrics(self, metrics: GrpcCallMetrics) -> None:
        """Update internal and Prometheus metrics."""
        # Update internal metrics
        method_key = f"{metrics.service_name}.{metrics.method_name}"

        self.call_counts[method_key] += 1

        if metrics.duration_ms is not None:
            self.response_times[method_key].append(metrics.duration_ms)

            # Keep only last 1000 response times
            if len(self.response_times[method_key]) > 1000:
                self.response_times[method_key] = self.response_times[method_key][
                    -1000:
                ]

        if not metrics.is_success:
            self.error_counts[method_key] += 1

        # Update Prometheus metrics
        if self.enable_prometheus:
            self.call_counter.labels(
                service=metrics.service_name,
                method=metrics.method_name,
                status=metrics.status_code.name if metrics.status_code else "unknown",
            ).inc()

            if metrics.duration_ms is not None:
                self.call_duration.labels(
                    service=metrics.service_name,
                    method=metrics.method_name,
                ).observe(
                    metrics.duration_ms / 1000
                )  # Convert to seconds

            if metrics.request_size is not None:
                self.request_size.labels(
                    service=metrics.service_name,
                    method=metrics.method_name,
                ).observe(metrics.request_size)

            if metrics.response_size is not None:
                self.response_size.labels(
                    service=metrics.service_name,
                    method=metrics.method_name,
                ).observe(metrics.response_size)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary for gRPC calls."""
        summary = {
            "total_calls": sum(self.call_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "methods": {},
        }

        for method, count in self.call_counts.items():
            response_times = self.response_times.get(method, [])
            error_count = self.error_counts.get(method, 0)

            method_metrics = {
                "call_count": count,
                "error_count": error_count,
                "error_rate": error_count / count if count > 0 else 0,
            }

            if response_times:
                response_times.sort()
                n = len(response_times)
                method_metrics.update(
                    {
                        "avg_response_time": sum(response_times) / n,
                        "p50_response_time": response_times[int(n * 0.5)],
                        "p95_response_time": response_times[int(n * 0.95)],
                        "p99_response_time": response_times[int(n * 0.99)],
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                    },
                )

            summary["methods"][method] = method_metrics

        return summary


class GrpcClientInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
):
    """Enterprise gRPC client interceptor for outbound call monitoring."""

    def __init__(self, service_name: str, enable_prometheus: bool = True) -> None:
        """Initialize client interceptor.

        Args:
        ----
            service_name: Service name for monitoring context
            enable_prometheus: Enable Prometheus metrics collection

        """
        self.service_name = service_name
        self.enable_prometheus = enable_prometheus
        self.logger = get_logger(f"grpc.client.{service_name}")

        if enable_prometheus:
            self._init_prometheus_metrics()

    def _init_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics for client calls."""
        # ZERO TOLERANCE CONSOLIDATION: Use centralized Prometheus import management
        prometheus_available, prometheus_components = get_prometheus_components()

        if prometheus_available:
            Counter = prometheus_components.get("Counter")
            Histogram = prometheus_components.get("Histogram")

            if Counter and Histogram:
                self.client_call_counter = Counter(
                    "grpc_client_calls_total",
                    "Total gRPC client calls",
                    ["service", "method", "status"],
                )

                self.client_call_duration = Histogram(
                    "grpc_client_call_duration_seconds",
                    "gRPC client call duration",
                    ["service", "method"],
                )
            else:
                self.enable_prometheus = False
        else:
            self.enable_prometheus = False

    def intercept_unary_unary(
        self, continuation: object, client_call_details: object, request: object
    ):
        """Intercept unary-unary client calls."""
        start_time = time.time()
        call_id = str(uuid.uuid4())

        # Extract method information
        method = client_call_details.method
        method_parts = method.split("/")
        service = method_parts[1] if len(method_parts) > 1 else "unknown"
        method_name = method_parts[2] if len(method_parts) > 2 else "unknown"

        self.logger.info(
            "gRPC client call started",
            call_id=call_id,
            service=service,
            method=method_name,
            target=client_call_details.method,
        )

        try:
            # Make the call
            response = continuation(client_call_details, request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            self.logger.info(
                "gRPC client call completed",
                call_id=call_id,
                service=service,
                method=method_name,
                duration_ms=duration_ms,
                status="OK",
            )

            # Update metrics
            if self.enable_prometheus:
                self.client_call_counter.labels(
                    service=service,
                    method=method_name,
                    status="OK",
                ).inc()

                self.client_call_duration.labels(
                    service=service,
                    method=method_name,
                ).observe(duration_ms / 1000)

            return response

        except grpc.RpcError as e:
            duration_ms = (time.time() - start_time) * 1000
            status = e.code().name if hasattr(e, "code") else "UNKNOWN"

            self.logger.exception(
                "gRPC client call failed",
                call_id=call_id,
                service=service,
                method=method_name,
                duration_ms=duration_ms,
                status=status,
                error=str(e),
            )

            # Update metrics
            if self.enable_prometheus:
                self.client_call_counter.labels(
                    service=service,
                    method=method_name,
                    status=status,
                ).inc()

            raise
