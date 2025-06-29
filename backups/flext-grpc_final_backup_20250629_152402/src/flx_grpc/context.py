"""REAL gRPC context management with user propagation using Python 3.13.

This module implements secure user context propagation through gRPC calls,
eliminating the security vulnerability of missing user context.
"""

from __future__ import annotations

import contextvars
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING

import grpc
from flx_auth.repositories import InMemoryRoleRepository, RoleRepositoryInterface
from flx_core.domain.pydantic_base import DomainBaseModel
from pydantic import Field

if TYPE_CHECKING:
    from uuid import UUID

    from flx_auth.models import User
    from flx_core.domain.advanced_types import MetadataDict

# Python 3.13 type aliases - with strict validation
type ContextValue = str | int | bool | float | None
type GrpcMetadata = dict[str, str]
type GrpcMethod = Callable[
    ...,
    Awaitable,
]  # Generic simplified for Pydantic compatibility
type GrpcMethodDecorator = Callable[[GrpcMethod], GrpcMethod]

# Context variables for thread-safe user propagation
current_user: contextvars.ContextVar[User | None] = contextvars.ContextVar(
    "current_user",
    default=None,
)

current_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_request_id",
    default=None,
)

current_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_trace_id",
    default=None,
)


class GrpcRequestContext(DomainBaseModel):
    """Complete gRPC request context with user information."""

    user: User | None = Field(
        default=None,
        description="Authenticated user for this request",
    )
    request_id: str | None = Field(
        default=None,
        description="Unique request identifier for tracing",
    )
    trace_id: str | None = Field(
        default=None,
        description="Distributed trace identifier",
    )
    method: str | None = Field(default=None, description="gRPC method being called")
    peer: str | None = Field(default=None, description="Client peer address")
    metadata: MetadataDict = Field(
        default_factory=dict,
        description="Additional request metadata",
    )

    @property
    def is_authenticated(self) -> bool:
        """Check if request has authenticated user."""
        return self.user is not None

    @property
    def user_id(self) -> UUID | None:
        """Get authenticated user ID.

        Extracts the unique user identifier from the authenticated user object
        for authorization checks and audit logging purposes.

        Returns:
        -------
            UUID of the authenticated user if available, None otherwise.

        Note:
        ----
            Essential for authorization and audit trail functionality.

        """
        return self.user.user_id if self.user else None

    @property
    def username(self) -> str | None:
        """Get authenticated username.

        Retrieves the username of the authenticated user if available,
        providing a string identifier for logging and audit purposes.

        Returns:
        -------
            str | None: Username if user is authenticated, None otherwise.

        Note:
        ----
            Provides secure user identification for authentication and authorization.

        """
        return self.user.username if self.user else None

    def to_dict(self) -> MetadataDict:
        """Convert context to dictionary for logging."""
        return {
            "user_id": str(self.user_id) if self.user_id else None,
            "username": self.username,
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "method": self.method,
            "peer": self.peer,
            "is_authenticated": self.is_authenticated,
        }


class GrpcContextManager:
    """Manages gRPC context propagation and access."""

    @staticmethod
    def set_user(user: User) -> None:
        """Set current user in gRPC request context.

        Stores the authenticated user in thread-local context variables
        for access throughout the request processing lifecycle.

        Args:
        ----
            user: Authenticated user object to store in context.

        Note:
        ----
            Provides user context propagation for security and auditing.

        """
        current_user.set(user)

    @staticmethod
    def get_user() -> User | None:
        """Get current user from context."""
        return current_user.get()

    @staticmethod
    def set_request_id(request_id: str) -> None:
        """Set current request ID for tracking and correlation.

        Stores unique request identifier in context for request tracing
        and correlation across distributed systems.

        Args:
        ----
            request_id: Unique identifier for the current request.

        Note:
        ----
            Enables request tracking and distributed tracing.

        """
        current_request_id.set(request_id)

    @staticmethod
    def get_request_id() -> str | None:
        """Get current request ID from context.

        Retrieves the unique request identifier from thread-local context
        for request correlation and logging purposes.

        Returns:
        -------
            str | None: Current request ID or None if not set.

        Note:
        ----
            Provides request tracking and correlation capabilities.

        """
        return current_request_id.get()

    @staticmethod
    def set_trace_id(trace_id: str) -> None:
        """Set current trace ID for distributed tracing.

        Stores distributed tracing identifier in context for correlation
        across service boundaries and monitoring systems.

        Args:
        ----
            trace_id: Distributed trace identifier.

        Note:
        ----
            Provides distributed tracing and observability.

        """
        current_trace_id.set(trace_id)

    @staticmethod
    def get_trace_id() -> str | None:
        """Get current trace ID from context.

        Retrieves the distributed trace identifier from thread-local context
        for correlation with monitoring and observability systems.

        Returns:
        -------
            str | None: Current trace ID or None if not set.

        Note:
        ----
            Provides distributed tracing and correlation capabilities.

        """
        return current_trace_id.get()

    @staticmethod
    def get_context() -> GrpcRequestContext:
        """Get complete request context information.

        Retrieves all context information (user, request ID, trace ID)
        in a single context object for comprehensive request tracking.

        Returns:
        -------
            GrpcRequestContext: Complete request context information.

        Note:
        ----
            Provides request context aggregation for monitoring.

        """
        return GrpcRequestContext(
            user=current_user.get(),
            request_id=current_request_id.get(),
            trace_id=current_trace_id.get(),
        )

    @staticmethod
    def clear_context() -> None:
        """Clear all context variables for cleanup.

        Resets all thread-local context variables (user, request ID, trace ID)
        to None for context cleanup and isolation between requests.

        Note:
        ----
            Provides context cleanup for proper request isolation.

        """
        current_user.set(None)
        current_request_id.set(None)
        current_trace_id.set(None)


class AuthenticatedServicer:
    """Base class for servicers requiring authentication."""

    def require_authentication(self) -> User:
        """Require authenticated user or raise exception."""
        user = GrpcContextManager.get_user()
        if not user:
            raise grpc.RpcError(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentication required",
            )
        return user

    def get_context(self) -> GrpcRequestContext:
        """Get current request context with authentication.

        Retrieves the complete request context including authenticated user,
        request ID, and trace ID for enterprise request processing.

        Returns:
        -------
            GrpcRequestContext: Complete authenticated request context.

        Note:
        ----
            Provides request context with authentication validation.

        """
        return GrpcContextManager.get_context()

    def check_permission(self, permission: str) -> bool:
        """Check if current user has specific permission."""
        # This method is largely obsolete now that the decorator handles
        # this logic asynchronously. This is a simplified, synchronous
        # version for any legacy non-async uses.
        user = self.require_authentication()
        if permission == "special:legacy":
            return "admin" in user.roles
        return False

    def require_permission(self, permission: str) -> None:
        """Require specific permission or raise exception."""
        if not self.check_permission(permission):
            raise grpc.RpcError(
                grpc.StatusCode.PERMISSION_DENIED,
                f"Permission required: {permission}",
            )


def get_current_user() -> User | None:
    """Get current user from context."""
    return GrpcContextManager.get_user()


def require_current_user() -> User:
    """Require authenticated user."""
    user = GrpcContextManager.get_user()
    if not user:
        raise grpc.RpcError(
            grpc.StatusCode.UNAUTHENTICATED,
            "Authentication required",
        )
    return user


def get_request_context() -> GrpcRequestContext:
    """Get complete request context."""
    return GrpcContextManager.get_context()


class Authenticator:
    """Decorator class for authentication and permission checks."""

    def __init__(self, permission: str | None = None) -> None:
        """Initialize Authenticator with optional permission requirement.

        Args:
        ----
            permission: Optional permission string that must be present in user roles.

        """
        self.permission = permission
        self.role_repo: RoleRepositoryInterface = InMemoryRoleRepository()

    def __call__(self, func: GrpcMethod) -> GrpcMethod:
        """Apply authorization decorator to gRPC method."""

        @wraps(func)
        async def wrapper(*args: object, **kwargs: object) -> object:
            # First argument is always the servicer instance
            servicer_instance = args[0]
            if not isinstance(servicer_instance, AuthenticatedServicer):
                msg = "This decorator must be used on methods of a class that inherits from AuthenticatedServicer."
                raise TypeError(
                    (msg),
                )

            user = servicer_instance.require_authentication()

            if self.permission:
                # Use the repository to get full Role objects
                user_roles = await self.role_repo.find_by_names(user.roles)

                # Check permissions across all roles
                has_permission = any(self.permission in role.permissions for role in user_roles)

                if not has_permission:
                    # If permission is not found, deny access
                    raise grpc.RpcError(
                        grpc.StatusCode.PERMISSION_DENIED,
                        f"Permission required: {self.permission}",
                    )
            # If all checks pass, proceed with the original RPC method
            return await func(*args, **kwargs)

        return wrapper


# Re-alias for backward compatibility
requires_auth = Authenticator
requires_permission = Authenticator
