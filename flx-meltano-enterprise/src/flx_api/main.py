"""
FLX REST API main application.

FastAPI-based REST API providing modern async interface to FLX platform.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from flx_api import __version__
from flx_api.config import api_settings
from flx_api.routers import monitoring, pipelines, plugins, websocket
from flx_api.websocket.connection_manager import ConnectionManager

# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies



# Lazy import to avoid circular dependencies
settings = lazy_import("flx.config", "settings")

# Global connection manager
manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await manager.startup()
    yield
    # Shutdown
    await manager.shutdown()


# Create FastAPI app
app = FastAPI(
    title="FLX Platform API",
    description="Enterprise Data Platform REST API",
    version=__version__,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(
    pipelines.router,
    prefix="/api/v1/pipelines",
    tags=["pipelines"],
)

app.include_router(
    plugins.router,
    prefix="/api/v1/plugins",
    tags=["plugins"],
)

app.include_router(
    monitoring.router,
    prefix="/api/v1/monitoring",
    tags=["monitoring"],
)

# WebSocket endpoint
app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "FLX Platform API",
        "version": __version__,
        "docs": "/api/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "flx-api",
        "version": __version__,
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # TODO: Check gRPC connection
    return {
        "status": "ready",
        "service": "flx-api",
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The path {request.url.path} was not found",
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        },
    )


def start():
    """Start the API server."""
    uvicorn.run(
        "flx_api.main:app",
        host="0.0.0.0",
        port=api_settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        access_log=True,
    )


if __name__ == "__main__":
    start()
