"""
FastAPI dependencies for dependency injection.
"""

from typing import Optional
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies


import grpc
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from flx_api.config import api_settings
from jose import JWTError, jwt

# Lazy import to avoid circular dependencies
settings = lazy_import('flx.config', 'settings')
# Lazy import to avoid circular dependencies
flx_pb2_grpc = lazy_import('flx.grpc.proto', 'flx_pb2_grpc')

# Security scheme
security = HTTPBearer()


async def get_grpc_channel():
    """Get gRPC channel."""
    channel = grpc.aio.insecure_channel(
        f"{settings.grpc_host}:{settings.grpc_port}",
        options=[
            ("grpc.max_send_message_length", settings.grpc_max_message_length),
            ("grpc.max_receive_message_length", settings.grpc_max_message_length),
        ],
    )
    try:
        yield channel
    finally:
        await channel.close()


async def get_grpc_stub(
    channel: grpc.aio.Channel = Depends(get_grpc_channel),
) -> flx_pb2_grpc.FlxServiceStub:
    """Get gRPC service stub."""
    return flx_pb2_grpc.FlxServiceStub(channel)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            api_settings.jwt_secret,
            algorithms=[api_settings.jwt_algorithm],
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": user_id,
            "org": payload.get("org"),
            "roles": payload.get("roles", []),
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self._requests = {}

    async def check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit."""
        # TODO: Implement proper rate limiting with Redis
        return True


# Global rate limiter
rate_limiter = RateLimiter()


async def check_rate_limit(
    user: dict = Depends(get_current_user),
) -> None:
    """Check rate limit for current user."""
    if not api_settings.rate_limit_enabled:
        return

    key = f"user:{user['id']}"
    allowed = await rate_limiter.check_rate_limit(key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
