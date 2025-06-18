"""
gRPC interceptors for monitoring and tracing.

Provides interceptors for collecting metrics and distributed tracing
information from gRPC requests.
"""

import time
from typing import Any, Callable, Optional

import grpc
import structlog
from grpc.aio import ServerInterceptor

from flx.monitoring.metrics import (
    grpc_active_requests,
    grpc_request_duration_seconds,
    grpc_requests_total,
)
from flx.monitoring.tracing import get_current_span

logger = structlog.get_logger()


class MetricsInterceptor(ServerInterceptor):
    """Interceptor for collecting gRPC metrics."""

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
        """Intercept gRPC calls to collect metrics."""
        method = handler_call_details.method

        # Increment active requests
        grpc_active_requests.labels(method=method).inc()

        # Start timer
        start_time = time.time()

        try:
            # Call handler
            response = await continuation(handler_call_details)

            # Record success
            grpc_requests_total.labels(method=method, status="success").inc()

            return response

        except Exception as e:
            # Record failure
            grpc_requests_total.labels(method=method, status="failure").inc()

            # Log error
            logger.error(
                "gRPC request failed",
                method=method,
                error=str(e),
            )

            raise

        finally:
            # Record duration
            duration = time.time() - start_time
            grpc_request_duration_seconds.labels(method=method).observe(duration)

            # Decrement active requests
            grpc_active_requests.labels(method=method).dec()


class TracingInterceptor(ServerInterceptor):
    """Interceptor for distributed tracing."""

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
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

            return response

        except Exception as e:
            if span:
                span.set_attribute("rpc.grpc.status_code", "ERROR")
                span.record_exception(e)

            raise


class AuthenticationInterceptor(ServerInterceptor):
    """Interceptor for authentication and authorization."""

    def __init__(self, auth_service: Optional[Any] = None):
        """Initialize with optional auth service."""
        self.auth_service = auth_service
        self.logger = logger.bind(component="auth_interceptor")

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
        """Intercept gRPC calls to verify authentication."""
        # Skip auth for health check and reflection
        if handler_call_details.method in [
            "/grpc.health.v1.Health/Check",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ]:
            return await continuation(handler_call_details)

        # Extract authorization header
        auth_token = None
        if handler_call_details.invocation_metadata:
            for key, value in handler_call_details.invocation_metadata:
                if key == "authorization":
                    auth_token = value
                    break

        # Verify token if auth service is available
        if self.auth_service and not auth_token:
            self.logger.warning(
                "Missing authorization token",
                method=handler_call_details.method,
            )

            # Return unauthenticated error
            context = grpc.aio.ServicerContext()
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Missing authorization token",
            )

        # TODO: Verify token with auth service
        # For now, just pass through

        return await continuation(handler_call_details)


class RateLimitingInterceptor(ServerInterceptor):
    """Interceptor for rate limiting."""

    def __init__(self, rate_limiter: Optional[Any] = None):
        """Initialize with optional rate limiter."""
        self.rate_limiter = rate_limiter
        self.logger = logger.bind(component="rate_limit_interceptor")

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Any:
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
            allowed = await self.rate_limiter.check_rate_limit(
                client_id,
                handler_call_details.method,
            )

            if not allowed:
                self.logger.warning(
                    "Rate limit exceeded",
                    client_id=client_id,
                    method=handler_call_details.method,
                )

                # Return resource exhausted error
                context = grpc.aio.ServicerContext()
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    "Rate limit exceeded",
                )

        return await continuation(handler_call_details)
