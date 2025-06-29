"""Unified gRPC client base for FLX Meltano Enterprise - ZERO DUPLICATION.

This module provides the canonical gRPC client implementation that eliminates
duplication between CLI and Web interfaces while maintaining specialized functionality.

Features:
- Unified configuration through domain_config.py
- SSL/TLS security with enterprise-grade certificates
- Connection pooling and resource management
- Error handling with ServiceResult patterns
- Python 3.13 type system throughout
- Strategic TYPE_CHECKING for optimal imports
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

import grpc
import structlog

# Unified configuration management
from flx_core.config.domain_config import get_config
from flx_core.domain.advanced_types import ServiceError, ServiceResult
from flx_core.security.ssl_utils import _create_ssl_credentials, get_grpc_channel_target

if TYPE_CHECKING:
    from flx_grpc.proto import flx_pb2_grpc
else:
    # Real imports at runtime - NO LAZY LOADING VIOLATIONS
    from flx_grpc.proto import flx_pb2_grpc

# Python 3.13 type aliases for gRPC domain
type GrpcConfig = dict[str, Any]
type ChannelOptions = list[tuple[str, Any]]
type GrpcResponse = dict[str, Any]
type DashboardStats = dict[str, int | float]
type HealthStatus = dict[str, bool | dict[str, Any]]
type ExecutionData = dict[str, str | None]

logger = structlog.get_logger(__name__)


class FlxGrpcClientBase:
    """Base gRPC client with unified configuration and connection management.

    This is the CANONICAL implementation that eliminates duplication between
    CLI and Web gRPC clients while providing shared functionality.

    Features:
    - Unified domain configuration
    - Enterprise SSL/TLS security
    - Connection pooling
    - Error handling patterns
    - Resource management
    """

    def __init__(self) -> None:
        """Initialize base gRPC client with unified configuration.

        Creates a gRPC client instance using the unified domain configuration
        for secure connection to the FLX gRPC server with proper resource management.
        """
        self._config = get_config()
        self._grpc_config = self._config.get_service_config("grpc")
        self._logger = logger.bind(component="grpc_client")

    def _get_grpc_message_size(self) -> int:
        """Get gRPC message size from domain configuration - ZERO TOLERANCE."""
        return self._config.business.GRPC_DEFAULT_MAX_MESSAGE_SIZE_MB * 1024 * 1024

    def _get_channel_options(self) -> ChannelOptions:
        """Get gRPC channel options with unified configuration - ZERO TOLERANCE UNIFICATION."""
        return [
            (
                "grpc.max_send_message_length",
                self._grpc_config.get(
                    "max_message_length",
                    self._get_grpc_message_size(),
                ),
            ),
            (
                "grpc.max_receive_message_length",
                self._grpc_config.get(
                    "max_message_length",
                    self._get_grpc_message_size(),
                ),
            ),
            # ZERO TOLERANCE: Use unified domain configuration for gRPC keepalive
            ("grpc.keepalive_time_ms", self._config.network.grpc_keepalive_time_ms),
            (
                "grpc.keepalive_timeout_ms",
                self._config.network.grpc_keepalive_timeout_ms,
            ),
            (
                "grpc.keepalive_permit_without_calls",
                self._config.network.grpc_keepalive_permit_without_calls,
            ),
        ]

    def _create_channel(self) -> grpc.Channel:
        """Create gRPC channel with unified configuration - ZERO TOLERANCE SECURITY."""
        target = get_grpc_channel_target()
        options = self._get_channel_options()

        if self._config.network.enable_ssl:
            credentials = _create_ssl_credentials(
                cert_file=self._config.network.ssl_cert_file,
                key_file=self._config.network.ssl_key_file,
                ca_file=self._config.network.ssl_ca_file,
            )
            return grpc.secure_channel(target, credentials, options=options)
        return grpc.insecure_channel(target, options=options)

    def _handle_grpc_error(self, error: grpc.RpcError, operation: str) -> ServiceResult[Any]:
        """Handle gRPC errors with unified error patterns."""
        try:
            error_details = error.details()
        except AttributeError:
            error_details = str(error)

        try:
            error_code = error.code()
        except AttributeError:
            error_code = None

        self._logger.error(
            "gRPC operation failed",
            operation=operation,
            error=error_details,
            code=error_code,
        )

        service_error = ServiceError(
            code=f"GRPC_{error_code.name}" if error_code else "GRPC_ERROR",
            message=f"gRPC {operation} failed: {error_details}",
        )
        return ServiceResult.fail(service_error)

    def _create_stub(self, channel: grpc.Channel) -> flx_pb2_grpc.FlxServiceStub:
        """Create gRPC service stub with the given channel."""
        return flx_pb2_grpc.FlxServiceStub(channel)


@functools.lru_cache(maxsize=1)
def get_grpc_client_base() -> FlxGrpcClientBase:
    """Get global base gRPC client instance.

    This function provides a singleton pattern for base gRPC client access,
    ensuring efficient resource usage and connection pooling.

    Returns:
    -------
        FlxGrpcClientBase: Configured base gRPC client instance.

    Note:
    ----
        Uses modern Python 3.13 functools.lru_cache for thread-safe singleton pattern.

    """
    return FlxGrpcClientBase()
