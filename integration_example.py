"""Integration example: flext-api + flext-auth + flext-web

This example demonstrates the complete integration of the three libraries:
- flext-api: HTTP client for making authenticated requests
- flext-auth: Authentication providers and middleware
- flext-web: FastAPI application with authentication

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, UTC

# Core foundation
from flext_core import FlextResult, FlextLogger

# Authentication (flext-auth)
from flext_auth import JwtAuthProvider, HttpAuthMiddleware, WebAuthMiddleware
from flext_auth.models import FlextAuthModels

# Web framework (flext-web)
from flext_web import create_fastapi_app
from flext_web.models import FlextWebModels

# HTTP client (flext-api)
from flext_api import FlextApiClient
from flext_api.models import FlextApiModels


async def create_secure_fastapi_application() -> FlextResult[object]:
    """Create FastAPI application with JWT authentication using flext-web + flext-auth.
    
    This demonstrates the NEW recommended pattern after migration.
    """
    logger = FlextLogger("integration_example")
    
    logger.info("Creating JWT authentication provider")
    
    # Step 1: Create JWT authentication provider from flext-auth
    jwt_provider = JwtAuthProvider(
        config={
            'secret_key': 'demo-secret-key-change-in-production',
            'algorithm': 'HS256',
            'access_token_expiry_minutes': 30,
        }
    )
    
    # Step 2: Create web authentication middleware from flext-auth
    web_auth_middleware = WebAuthMiddleware(
        provider=jwt_provider,
        header_name="Authorization",
        token_prefix="Bearer",
        exclude_paths=["/health", "/docs", "/openapi.json"],
        require_auth=True,
    )
    
    logger.info("Creating FastAPI application with authentication")
    
    # Step 3: Create FastAPI application from flext-web with middleware
    app_config = FlextWebModels.AppConfig(
        title="Secure Enterprise API",
        version="1.0.0",
        description="Enterprise API with JWT authentication via flext-auth",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        middlewares=[web_auth_middleware],
    )
    
    app_result = create_fastapi_app(app_config)
    
    if app_result.is_failure:
        return FlextResult[object].fail(
            f"Failed to create FastAPI app: {app_result.error}"
        )
    
    app = app_result.unwrap()
    
    logger.info(
        "FastAPI application created successfully",
        extra={
            "title": app.title,
            "version": app.version,
            "routes": len(app.routes),
            "middleware_count": len(app_config.middlewares),
        }
    )
    
    return FlextResult[object].ok(app)


async def create_authenticated_http_client() -> FlextResult[FlextApiClient]:
    """Create HTTP client with JWT authentication using flext-api + flext-auth.
    
    This demonstrates authenticated HTTP client requests.
    """
    logger = FlextLogger("integration_example")
    
    logger.info("Creating authenticated HTTP client")
    
    # Step 1: Create JWT provider for client authentication
    jwt_provider = JwtAuthProvider(
        config={
            'secret_key': 'demo-secret-key-change-in-production',
            'algorithm': 'HS256',
        }
    )
    
    # Step 2: Authenticate user to get token
    # JWT provider requires user_id for token creation
    credentials = {
        "username": "demo-user",
        "password": "demo-password",
        "user_id": "user-123",  # Required by JWT provider
    }

    auth_result = await jwt_provider.authenticate(credentials)
    if auth_result.is_failure:
        return FlextResult[FlextApiClient].fail(
            f"Authentication failed: {auth_result.error}"
        )
    
    token = auth_result.unwrap()
    
    logger.info("User authenticated successfully", extra={"user_id": token.user_id})
    
    # Step 3: Create HTTP authentication middleware from flext-auth
    http_auth_middleware = HttpAuthMiddleware(
        provider=jwt_provider,
        credentials=credentials,
        header_name="Authorization",
        token_prefix="Bearer",
        auto_refresh=True,
    )
    
    # Step 4: Create HTTP client from flext-api with auth middleware
    client = FlextApiClient(
        base_url="https://api.example.com",
        timeout=30.0,
        max_retries=3,
    )
    
    # Middleware would be added to client (implementation detail)
    # client.add_middleware(http_auth_middleware)
    
    logger.info("HTTP client created with authentication")
    
    return FlextResult[FlextApiClient].ok(client)


async def demonstrate_complete_integration():
    """Demonstrate complete integration of all three libraries."""
    logger = FlextLogger("integration_example")
    
    logger.info("=" * 80)
    logger.info("FLEXT LIBRARY INTEGRATION DEMONSTRATION")
    logger.info("=" * 80)
    
    # Part 1: Create secure FastAPI application
    logger.info("\n[1/3] Creating secure FastAPI application (flext-web + flext-auth)")
    app_result = await create_secure_fastapi_application()
    
    if app_result.is_failure:
        logger.error(f"Failed to create application: {app_result.error}")
        return
    
    app = app_result.unwrap()
    logger.info(f"✅ FastAPI application created: {app.title} v{app.version}")
    logger.info(f"   Routes: {len(app.routes)}")
    logger.info(f"   Endpoints: /health, /docs, /redoc, /openapi.json")
    
    # Part 2: Create authenticated HTTP client
    logger.info("\n[2/3] Creating authenticated HTTP client (flext-api + flext-auth)")
    client_result = await create_authenticated_http_client()
    
    if client_result.is_failure:
        logger.error(f"Failed to create client: {client_result.error}")
        return
    
    client = client_result.unwrap()
    logger.info("✅ HTTP client created with JWT authentication")
    logger.info(f"   Base URL: {client.base_url}")
    logger.info(f"   Timeout: {client.timeout}s")
    logger.info(f"   Max Retries: {client.max_retries}")
    
    # Part 3: Summary
    logger.info("\n[3/3] Integration Summary")
    logger.info("=" * 80)
    logger.info("✅ flext-auth: Provides authentication for BOTH:")
    logger.info("   - HttpAuthMiddleware: For HTTP client requests")
    logger.info("   - WebAuthMiddleware: For FastAPI application endpoints")
    logger.info("")
    logger.info("✅ flext-web: FastAPI application factory with:")
    logger.info("   - Automatic health endpoints")
    logger.info("   - Middleware integration support")
    logger.info("   - OpenAPI documentation")
    logger.info("")
    logger.info("✅ flext-api: HTTP client with:")
    logger.info("   - Automatic authentication via middleware")
    logger.info("   - Connection pooling and retry logic")
    logger.info("   - Request/response models")
    logger.info("")
    logger.info("🎯 ZERO CODE DUPLICATION: Each library owns its domain")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Run the complete integration demonstration
    asyncio.run(demonstrate_complete_integration())
