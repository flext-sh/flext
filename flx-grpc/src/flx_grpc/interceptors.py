"""gRPC interceptors for monitoring and tracing.

Provides interceptors for collecting metrics and distributed tracing
information from gRPC requests.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    # gRPC service handler return type
    ServiceHandler = Callable[..., Awaitable[Any]]

import grpc
import structlog
from flx_observability.tracing import get_current_span
from grpc.aio import ServerInterceptor

if TYPE_CHECKING:
    from flx_auth.service import AuthenticationService
    from flx_core.security.rate_limiting import TokenBucketLimiter
    from flx_observability.metrics import MetricsCollector

logger = structlog.get_logger()


class MetricsInterceptor(ServerInterceptor):
    """gRPC server interceptor for metrics collection.

    Intercepts gRPC service calls to collect performance metrics,
    request counts, duration, and success/failure rates for enterprise monitoring.

    Attributes:
    ----------
        metrics_collector: Optional metrics collector for data aggregation.
        logger: Structured logger for component-specific logging.

    Methods:
    -------
        intercept_service(): Intercepts and instruments gRPC calls.

    Examples:
    --------
        Basic usage with metrics collector:

        ```python
        metrics = MetricsCollector()
        interceptor = MetricsInterceptor(metrics)
        server.add_interceptor(interceptor)
        ```

    Note:
    ----
        Implements enterprise monitoring patterns with Prometheus-compatible metrics.

    """

    def __init__(self, metrics_collector: MetricsCollector | None = None) -> None:
        """Initialize with optional metrics collector."""
        self.metrics_collector = metrics_collector
        self.logger = logger.bind(component="metrics_interceptor")

    async def intercept_service(
        self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails
    ) -> ServiceHandler:
        """Intercept gRPC calls to collect metrics."""
        method = handler_call_details.method

        # Skip metrics collection if no collector provided
        if not self.metrics_collector:
            return await continuation(handler_call_details)

        # Increment active requests
        self.metrics_collector.grpc_active_requests.labels(method=method).inc()

        # Start timer
        start_time = time.time()

        try:
            # Call handler
            response = await continuation(handler_call_details)

            # Record success
            self.metrics_collector.grpc_requests_total.labels(
                method=method,
                status="success",
            ).inc()

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC request failures
            # Record failure
            self.metrics_collector.grpc_requests_total.labels(
                method=method,
                status="failure",
            ).inc()

            # Log error
            self.logger.exception(
                "gRPC request failed",
                method=method,
                error=str(e),
            )

            raise
        else:
            return response
        finally:
            # Record duration
            duration = time.time() - start_time
            self.metrics_collector.grpc_request_duration_seconds.labels(
                method=method,
            ).observe(duration)

            # Decrement active requests
            self.metrics_collector.grpc_active_requests.labels(method=method).dec()


class TracingInterceptor(ServerInterceptor):
    """gRPC server interceptor for distributed tracing.

    Intercepts gRPC service calls to add distributed tracing information,
    span attributes, and request metadata for enterprise observability.

    Methods:
    -------
        intercept_service(): Intercepts calls to add tracing information.

    Examples:
    --------
        Basic usage for distributed tracing:

        ```python
        interceptor = TracingInterceptor()
        server.add_interceptor(interceptor)
        ```

    Note:
    ----
        Integrates with OpenTelemetry for enterprise-grade distributed tracing.

    """

    async def intercept_service(
        self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails
    ) -> ServiceHandler:
        """Intercept gRPC calls to add tracing information."""
        # Get current span if tracing is active
        span = get_current_span()

        if span:
            # Add gRPC metadata to span
            span.set_attribute("rpc.system", "grpc")
            span.set_attribute("rpc.method", handler_call_details.method)

            # Extract metadata if available
            if handler_call_details.invocation_metadata:
                for key, value in handler_call_details.invocation_metadata:
                    if key == "user-agent":
                        span.set_attribute("rpc.user_agent", value)

        try:
            # Call handler
            response = await continuation(handler_call_details)

            if span:
                span.set_attribute("rpc.grpc.status_code", "OK")

        except (
            ValueError,
            TypeError,
            RuntimeError,
            OSError,
            TimeoutError,
            ConnectionError,
            ImportError,
            grpc.RpcError,
        ) as e:
            # ZERO TOLERANCE - Specific exception types for gRPC tracing failures
            if span:
                span.set_attribute("rpc.grpc.status_code", "ERROR")
                span.record_exception(e)

            raise
        else:
            return response


class AuthenticationInterceptor(ServerInterceptor):
    """gRPC server interceptor for authentication verification.

    Intercepts gRPC service calls to verify authentication tokens
    and enforce security policies for enterprise access control.

    Attributes:
    ----------
        auth_service: Optional authentication service for token verification.
        logger: Structured logger for security event logging.

    Methods:
    -------
        intercept_service(): Intercepts calls to verify authentication.

    Examples:
    --------
        Basic usage with authentication service:

        ```python
        auth_service = AuthenticationService()
        interceptor = AuthenticationInterceptor(auth_service)
        server.add_interceptor(interceptor)
        ```

    Note:
    ----
        Implements enterprise security patterns with JWT token validation.

    """

    def __init__(self, auth_service: AuthenticationService | None = None) -> None:
        """Initialize with optional auth service."""
        self.auth_service = auth_service
        self.logger = logger.bind(component="auth_interceptor")

    async def intercept_service(
        self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails
    ) -> ServiceHandler:
        """Intercept gRPC calls to verify authentication."""
        # Skip auth for health check and reflection
        if handler_call_details.method in {
            "/grpc.health.v1.Health/Check",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        }:
            return await continuation(handler_call_details)

        # Extract authorization header
        auth_token = None
        if handler_call_details.invocation_metadata:
            for key, value in handler_call_details.invocation_metadata:
                if key == "authorization":
                    auth_token = value
                    break

        # Verify token if auth service is available
        if self.auth_service:
            if not auth_token:
                self.logger.warning(
                    "Missing authorization token",
                    method=handler_call_details.method,
                )
                # Create proper context and abort
                await self._abort_unauthenticated("Missing authorization token")

            # Extract bearer token
            if auth_token.startswith("Bearer "):
                token = auth_token[7:]
            else:
                await self._abort_unauthenticated("Invalid authorization format")

            try:
                # Verify token and get user
                user = await self.auth_service.verify_access_token(token)

                # Log successful authentication
                self.logger.info(
                    "Request authenticated",
                    method=handler_call_details.method,
                    user_id=str(user.user_id),
                    username=user.username,
                )

                # Add authenticated user to gRPC metadata for downstream handlers
                # Create enhanced metadata with user information for enterprise audit trails
                metadata_list = list(handler_call_details.invocation_metadata or [])
                metadata_list.extend(
                    [
                        ("x-user-id", str(user.user_id)),
                        ("x-username", user.username),
                        ("x-auth-method", "jwt_token"),
                        ("x-auth-timestamp", datetime.now(UTC).isoformat()),
                    ],
                )

                # Update handler call details with authenticated metadata
                handler_call_details = handler_call_details._replace(
                    invocation_metadata=tuple(metadata_list),
                )

            except (
                ValueError,
                TypeError,
                RuntimeError,
                ImportError,
                KeyError,
                AttributeError,
            ) as e:
                self.logger.warning(
                    "Token verification failed",
                    method=handler_call_details.method,
                    error=str(e),
                )
                await self._abort_unauthenticated("Invalid or expired token")

        return await continuation(handler_call_details)

    async def _abort_unauthenticated(self, message: str) -> None:
        """Abort with unauthenticated status."""
        context = grpc.aio.ServicerContext()
        await context.abort(
            grpc.StatusCode.UNAUTHENTICATED,
            message,
        )


class RateLimitingInterceptor(ServerInterceptor):
    """gRPC server interceptor for IP-based rate limiting.

    Intercepts gRPC calls to enforce rate limits based on client IP,
    preventing abuse and ensuring fair resource usage.

    Attributes:
    ----------
        rate_limiter: Rate limiter instance for tracking requests.
        logger: Structured logger for component-specific logging.

    Methods:
    -------
        intercept_service(): Intercepts calls to apply rate limiting.

    Examples:
    --------
        Basic usage with default rate limiter:

        ```python
        rate_limiter = TokenBucketLimiter(requests_per_minute=100)
        interceptor = RateLimitingInterceptor(rate_limiter)
        server.add_interceptor(interceptor)
        ```

    Note:
    ----
        Implements enterprise-grade rate limiting to protect against abuse.

    """

    def __init__(self, rate_limiter: TokenBucketLimiter | None = None) -> None:
        """Initialize with a rate limiter instance."""
        self.rate_limiter = rate_limiter
        self.logger = logger.bind(component="rate_limiter_interceptor")

    async def intercept_service(
        self, continuation: Callable, handler_call_details: grpc.HandlerCallDetails
    ) -> ServiceHandler:
        """Intercept gRPC calls to apply rate limiting."""
        # Skip rate limiting for health check
        if handler_call_details.method == "/grpc.health.v1.Health/Check":
            return await continuation(handler_call_details)

        # Extract client identifier (IP or user ID)
        client_id = "unknown"
        if handler_call_details.invocation_metadata:
            for key, value in handler_call_details.invocation_metadata:
                if key == "x-forwarded-for":
                    client_id = value.split(",")[0].strip()
                    break

        # Check rate limit if rate limiter is available
        if self.rate_limiter:
            allowed = self.rate_limiter.allow(client_id)

            if not allowed:
                self.logger.warning(
                    "Rate limit exceeded",
                    client_id=client_id,
                    method=handler_call_details.method,
                )

                # Return resource exhausted error
                context = grpc.aio.ServicerContext()
                await context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    "Rate limit exceeded",
                )

        return await continuation(handler_call_details)
