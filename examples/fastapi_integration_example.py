"""Example of using FastAPI to replace custom API implementations.

Shows how to leverage FastAPI's features for automatic validation,
documentation, and dependency injection.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any

import sentry_sdk
import structlog
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from flx.infra.database.optimized_repository import (
    DatabaseService,
    OptimizedDatabaseConfig,
)
from prometheus_client import make_asgi_app
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from flx.infra.services.optimized_base import (
    OptimizedCacheService,
    OptimizedHttpClientService,
)

# Configure logging
logger = structlog.get_logger(__name__)


# Pydantic models for validation
class UserCreate(BaseModel):
    """User creation model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """User update model."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """User response model."""

    id: str
    email: str
    username: str
    full_name: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Pagination parameters."""

    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    services: dict[str, dict[str, Any]]


# Dependency injection setup
class Dependencies:
    """Application dependencies."""

    def __init__(self) -> None:
        self.db_service: DatabaseService | None = None
        self.cache_service: OptimizedCacheService | None = None
        self.http_service: OptimizedHttpClientService | None = None

    async def initialize(self) -> None:
        """Initialize all services."""
        # Database
        db_config = OptimizedDatabaseConfig(
            database_url="postgresql+asyncpg://localhost/flx_db",
        )
        self.db_service = DatabaseService(db_config)
        await self.db_service.initialize()

        # Cache
        self.cache_service = OptimizedCacheService()
        await self.cache_service.connect()

        # HTTP Client
        self.http_service = OptimizedHttpClientService()
        await self.http_service.connect()

    async def cleanup(self) -> None:
        """Cleanup all services."""
        if self.db_service:
            await self.db_service.close()
        if self.cache_service:
            await self.cache_service.disconnect()
        if self.http_service:
            await self.http_service.disconnect()


# Global dependencies instance
deps = Dependencies()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("application_starting")
    await deps.initialize()
    logger.info("application_started")

    yield

    # Shutdown
    logger.info("application_stopping")
    await deps.cleanup()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title="FLX API",
    description="FLX Infrastructure Services API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Sentry middleware
app.add_middleware(SentryAsgiMiddleware)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# Dependency functions
async def get_db_service() -> DatabaseService:
    """Get database service dependency."""
    if not deps.db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    return deps.db_service


async def get_cache_service() -> OptimizedCacheService:
    """Get cache service dependency."""
    if not deps.cache_service:
        raise HTTPException(status_code=503, detail="Cache service unavailable")
    return deps.cache_service


async def get_pagination(
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip"),
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(limit=limit, offset=offset)


# Cache decorator
import hashlib
import json
from functools import wraps


def cached(ttl: int = 300):
    """Cache decorator for endpoints."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache service from dependencies
            cache = await get_cache_service()

            # Generate cache key
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": str(sorted(kwargs.items())),
            }
            cache_key = hashlib.md5(
                json.dumps(key_data).encode(),
            ).hexdigest()

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value:
                logger.debug("cache_hit", key=cache_key)
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            await cache.set(cache_key, result, ttl=ttl)
            logger.debug("cache_set", key=cache_key, ttl=ttl)

            return result

        return wrapper

    return decorator


# API Endpoints


@app.get("/health", response_model=HealthResponse)
async def health_check(
    db: Annotated[DatabaseService, Depends(get_db_service)],
    cache: Annotated[OptimizedCacheService, Depends(get_cache_service)],
    http: Annotated[OptimizedHttpClientService, Depends(get_http_service)],
):
    """Health check endpoint."""
    services = {}

    # Check database
    services["database"] = await db.manager.health_check()

    # Check cache
    services["cache"] = await cache.health_check()

    # Check HTTP client
    services["http"] = await http.health_check()

    # Overall status
    all_healthy = all(s.get("status") == "healthy" for s in services.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.utcnow(),
        services=services,
    )


@app.post("/api/v1/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: Annotated[DatabaseService, Depends(get_db_service)],
):
    """Create new user."""
    try:
        # Check if user exists
        existing = await db.users.find_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists",
            )

        # Create user
        user = await db.users.create(**user_data.model_dump())

        logger.info("user_created", user_id=user.id, email=user.email)
        return UserResponse.model_validate(user)

    except Exception as e:
        logger.exception("user_creation_failed", error=str(e))
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.get("/api/v1/users", response_model=list[UserResponse])
@cached(ttl=60)  # Cache for 1 minute
async def list_users(
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    db: Annotated[DatabaseService, Depends(get_db_service)],
    is_active: Annotated[
        bool | None, Query(description="Filter by active status")
    ] = None,
):
    """List users with pagination."""
    if is_active is not None:
        users = await db.users.find_by(
            is_active=is_active,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    else:
        users = await db.users.get_all(
            limit=pagination.limit,
            offset=pagination.offset,
        )

    return [UserResponse.model_validate(user) for user in users]


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: Annotated[str, Path(description="User ID")] = ...,
    db: DatabaseService = Depends(get_db_service),
    cache: OptimizedCacheService = Depends(get_cache_service),
):
    """Get user by ID."""
    # Try cache first
    cache_key = f"user:{user_id}"
    cached_user = await cache.get(cache_key)

    if cached_user:
        return UserResponse(**cached_user)

    # Get from database
    user = await db.users.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Cache for future requests
    user_dict = UserResponse.model_validate(user).model_dump()
    await cache.set(cache_key, user_dict, ttl=300)

    return UserResponse.model_validate(user)


@app.patch("/api/v1/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: Annotated[str, Path(description="User ID")] = ...,
    user_update: Annotated[UserUpdate, Body()] = ...,
    db: DatabaseService = Depends(get_db_service),
    cache: OptimizedCacheService = Depends(get_cache_service),
):
    """Update user."""
    # Update in database
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    user = await db.users.update(user_id, **update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Invalidate cache
    cache_key = f"user:{user_id}"
    await cache.delete(cache_key)

    logger.info("user_updated", user_id=user_id, fields=list(update_data.keys()))
    return UserResponse.model_validate(user)


@app.delete("/api/v1/users/{user_id}", status_code=204)
async def delete_user(
    user_id: Annotated[str, Path(description="User ID")] = ...,
    db: DatabaseService = Depends(get_db_service),
    cache: OptimizedCacheService = Depends(get_cache_service),
) -> None:
    """Delete user."""
    # Delete from database
    deleted = await db.users.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    # Invalidate cache
    cache_key = f"user:{user_id}"
    await cache.delete(cache_key)

    logger.info("user_deleted", user_id=user_id)


# Batch operations endpoint
class BatchUserCreate(BaseModel):
    """Batch user creation request."""

    users: list[UserCreate] = Field(..., min_length=1, max_length=1000)


class BatchUserResponse(BaseModel):
    """Batch operation response."""

    created: int
    failed: int
    errors: list[dict[str, str]]


@app.post("/api/v1/users/batch", response_model=BatchUserResponse)
async def create_users_batch(
    batch: BatchUserCreate,
    db: Annotated[DatabaseService, Depends(get_db_service)],
):
    """Create multiple users in batch."""
    created = 0
    failed = 0
    errors = []

    # Process in transaction
    async with db.transaction():
        for user_data in batch.users:
            try:
                # Check if exists
                existing = await db.users.find_by_email(user_data.email)
                if existing:
                    failed += 1
                    errors.append(
                        {
                            "email": user_data.email,
                            "error": "Already exists",
                        }
                    )
                    continue

                # Create user
                await db.users.create(**user_data.model_dump())
                created += 1

            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "email": user_data.email,
                        "error": str(e),
                    }
                )

    logger.info(
        "batch_user_creation",
        total=len(batch.users),
        created=created,
        failed=failed,
    )

    return BatchUserResponse(
        created=created,
        failed=failed,
        errors=errors,
    )


# WebSocket example for real-time updates

from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """WebSocket connection manager."""

    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connections."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection might be closed
                pass


manager = ConnectionManager()


@app.websocket("/ws/users")
async def websocket_endpoint(
    websocket: WebSocket,
    db: DatabaseService = Depends(get_db_service),
) -> None:
    """WebSocket endpoint for real-time user updates."""
    await manager.connect(websocket)

    try:
        while True:
            # Wait for messages
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "subscribe":
                await websocket.send_json(
                    {
                        "type": "subscribed",
                        "message": "Subscribed to user updates",
                    }
                )

            # In a real app, you'd have background tasks that broadcast updates
            # when users are created/updated/deleted

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    sentry_sdk.capture_exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        },
    )
