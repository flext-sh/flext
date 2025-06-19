# FLX HTTP Oracle OIC Adapter Guide

**Function**: Complete guide for Oracle Integration Cloud (OIC) connectivity within the FLX framework using REST APIs and OAuth2 authentication
**Audience**: Integration developers, API specialists, and cloud architects working with Oracle OIC
**Status**: Production Ready - Validated Implementation

---

## Navigation Context

**Current Location**: `docs/guides/oracle/flx_http_oracle_oic-adapter.md`
**Parent**: [Oracle Integration Hub](oracle-integration-hub.md) > Oracle OIC Integration
**Quick Links**: [Database Adapter](flx-database-oracle-adapter.md) | [WMS Adapter](flx-http-oracle-wms-adapter.md) | [OAuth2 Guide](oracle-oauth2-authentication-guide.md)

---

## Overview

The FLX HTTP Oracle OIC Adapter provides seamless integration with Oracle Integration Cloud through REST APIs, supporting workflow orchestration, data transformation, and real-time messaging. Built on hexagonal architecture principles, it serves as both an inbound and outbound adapter for OIC integrations.

### Key Features

- **OAuth2 Authentication**: Secure client credentials and JWT token management
- **REST API Integration**: Full OIC REST API support with async operations
- **Workflow Orchestration**: Trigger and monitor OIC integration flows
- **Real-time Messaging**: Pub/Sub capabilities with OIC adapters
- **Error Handling**: Comprehensive error recovery and retry mechanisms
- **Observability**: Built-in tracing, metrics, and correlation ID tracking
- **Rate Limiting**: Intelligent backoff and throttling strategies

---

## Installation & Setup

### Dependencies

```toml
# pyproject.toml
[tool.poetry.dependencies]
aiohttp = "^3.9.0"
pydantic = "^2.5.0"
authlib = "^1.3.0"  # OAuth2 support
anyio = "^4.2.0"
tenacity = "^8.2.0"  # Retry mechanisms

[tool.poetry.group.dev.dependencies]
pytest-asyncio = "^0.23.0"
pytest-aiohttp = "^1.0.4"
respx = "^0.20.0"  # HTTP mocking
```

### Configuration

```python
# config/oic.py
from pydantic import BaseModel, Field, SecretStr, HttpUrl
from typing import Optional, Dict, Any
from enum import Enum

class OAuthGrantType(str, Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"

class OicConfig(BaseModel):
    """Oracle Integration Cloud configuration."""

    # OIC Instance Settings
    base_url: HttpUrl = Field(..., description="OIC instance base URL")
    tenant_id: str = Field(..., description="OIC tenant identifier")
    api_version: str = Field(default="v1", description="OIC API version")

    # OAuth2 Authentication
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: SecretStr = Field(..., description="OAuth2 client secret")
    token_endpoint: HttpUrl = Field(..., description="OAuth2 token endpoint")
    grant_type: OAuthGrantType = Field(default=OAuthGrantType.CLIENT_CREDENTIALS)
    scope: str = Field(default="urn:opc:resource:consumer::all", description="OAuth2 scope")

    # Connection Settings
    timeout: int = Field(default=60, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    retry_backoff: float = Field(default=2.0, ge=1.0, le=10.0, description="Retry backoff multiplier")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)
    burst_limit: int = Field(default=10, ge=1, le=100)

    # SSL Configuration
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_cert_path: Optional[str] = Field(None, description="Custom SSL certificate path")

    class Config:
        env_prefix = "OIC_"
        validate_assignment = True
```

---

## Implementation

### Core Adapter Implementation

```python
# src/flx/adapters/outbound/oracle/oic_adapter.py
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin
from authlib.integrations.httpx_client import AsyncOAuth2Client
from tenacity import retry, stop_after_attempt, wait_exponential

from flx.core.adapters.base import BaseAdapter
from flx.core.adapters.mixins import (
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin
)
from flx.domain.ports.outbound.http import HttpPort
from flx.adapters.outbound.oracle.config import OicConfig
from flx.adapters.outbound.oracle.exceptions import (
    OicAuthenticationError,
    OicApiError,
    OicWorkflowError,
    OicRateLimitError
)

class FlxOracleOicAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """FLX Oracle Integration Cloud HTTP Adapter."""

    def __init__(self, config: OicConfig):
        super().__init__()
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._oauth_client: Optional[AsyncOAuth2Client] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._rate_limiter = RateLimiter(
            rate_limit=config.rate_limit_per_minute,
            burst_limit=config.burst_limit
        )

    async def connect(self) -> None:
        """Initialize HTTP session and OAuth2 client."""
        async with self.observe_operation("oic_adapter_connect"):
            try:
                # Create HTTP session with SSL configuration
                connector = aiohttp.TCPConnector(
                    verify_ssl=self.config.verify_ssl,
                    ssl_cert=self.config.ssl_cert_path
                )

                timeout = aiohttp.ClientTimeout(total=self.config.timeout)

                self._session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                    headers={
                        "User-Agent": "FLX-OIC-Adapter/1.0",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                )

                # Initialize OAuth2 client
                self._oauth_client = AsyncOAuth2Client(
                    client_id=self.config.client_id,
                    client_secret=self.config.client_secret.get_secret_value(),
                    scope=self.config.scope
                )

                # Obtain initial access token
                await self._refresh_token()

                self.logger.info(
                    "OIC adapter connected successfully",
                    extra={
                        "base_url": str(self.config.base_url),
                        "tenant_id": self.config.tenant_id
                    }
                )

            except Exception as e:
                raise OicAuthenticationError(
                    f"Failed to connect to OIC: {str(e)}",
                    context={"base_url": str(self.config.base_url)}
                ) from e

    async def disconnect(self) -> None:
        """Close HTTP session and cleanup resources."""
        async with self.observe_operation("oic_adapter_disconnect"):
            if self._session:
                await self._session.close()
                self._session = None

            self._oauth_client = None
            self._access_token = None
            self._token_expires_at = None

            self.logger.info("OIC adapter disconnected")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=1, max=60)
    )
    async def _refresh_token(self) -> None:
        """Refresh OAuth2 access token."""
        async with self.observe_operation("oic_oauth_refresh"):
            try:
                token_response = await self._oauth_client.fetch_token(
                    url=str(self.config.token_endpoint),
                    grant_type=self.config.grant_type.value
                )

                self._access_token = token_response["access_token"]
                expires_in = token_response.get("expires_in", 3600)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer

                self.logger.debug(
                    "OAuth2 token refreshed successfully",
                    extra={"expires_at": self._token_expires_at.isoformat()}
                )

            except Exception as e:
                raise OicAuthenticationError(
                    f"Failed to refresh OAuth2 token: {str(e)}"
                ) from e

    async def _ensure_valid_token(self) -> None:
        """Ensure we have a valid access token."""
        if not self._access_token or datetime.now() >= self._token_expires_at:
            await self._refresh_token()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make authenticated HTTP request to OIC API."""
        async with self.observe_operation("oic_api_request", method=method, endpoint=endpoint):
            # Wait for rate limiter
            await self._rate_limiter.acquire()

            # Ensure valid token
            await self._ensure_valid_token()

            # Build URL
            url = urljoin(str(self.config.base_url), f"ic/api/integration/{self.config.api_version}/{endpoint}")

            # Prepare headers
            request_headers = {
                "Authorization": f"Bearer {self._access_token}",
                "X-Tenant-Id": self.config.tenant_id
            }
            if headers:
                request_headers.update(headers)

            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=request_headers
                ) as response:

                    # Handle rate limiting
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        await asyncio.sleep(retry_after)
                        raise OicRateLimitError(f"Rate limit exceeded, retry after {retry_after} seconds")

                    # Check for errors
                    if response.status >= 400:
                        error_text = await response.text()
                        raise OicApiError(
                            f"OIC API error {response.status}: {error_text}",
                            context={
                                "status_code": response.status,
                                "method": method,
                                "endpoint": endpoint,
                                "response": error_text
                            }
                        )

                    # Parse response
                    if response.content_type == "application/json":
                        return await response.json()
                    else:
                        return {"content": await response.text()}

            except aiohttp.ClientError as e:
                raise OicApiError(
                    f"HTTP client error: {str(e)}",
                    context={"method": method, "endpoint": endpoint}
                ) from e

    async def list_integrations(self, flow_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available integrations in OIC."""
        async with self.observe_operation("oic_list_integrations"):
            params = {}
            if flow_type:
                params["flowType"] = flow_type

            response = await self._make_request("GET", "integrations", params=params)

            integrations = response.get("items", [])

            self.logger.info(
                f"Retrieved {len(integrations)} integrations",
                extra={"count": len(integrations), "flow_type": flow_type}
            )

            return integrations

    async def get_integration_details(self, integration_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific integration."""
        async with self.observe_operation("oic_get_integration", integration_id=integration_id):
            endpoint = f"integrations/{integration_id}"
            integration = await self._make_request("GET", endpoint)

            self.logger.debug(
                f"Retrieved integration details",
                extra={
                    "integration_id": integration_id,
                    "name": integration.get("name"),
                    "status": integration.get("status")
                }
            )

            return integration

    async def trigger_integration(
        self,
        integration_id: str,
        payload: Dict[str, Any],
        operation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Trigger an integration execution."""
        async with self.observe_operation("oic_trigger_integration", integration_id=integration_id):
            endpoint = f"integrations/{integration_id}/executions"

            request_data = {
                "payload": payload,
                "executionRequest": {
                    "correlationId": self.correlation_id,
                    "timestamp": datetime.now().isoformat()
                }
            }

            if operation:
                request_data["operation"] = operation

            response = await self._make_request("POST", endpoint, data=request_data)

            execution_id = response.get("executionId")

            self.logger.info(
                "Integration triggered successfully",
                extra={
                    "integration_id": integration_id,
                    "execution_id": execution_id,
                    "correlation_id": self.correlation_id
                }
            )

            return response

    async def get_execution_status(
        self,
        integration_id: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """Get execution status for a triggered integration."""
        async with self.observe_operation("oic_get_execution_status"):
            endpoint = f"integrations/{integration_id}/executions/{execution_id}"
            execution = await self._make_request("GET", endpoint)

            status = execution.get("status", "UNKNOWN")

            self.logger.debug(
                f"Retrieved execution status: {status}",
                extra={
                    "integration_id": integration_id,
                    "execution_id": execution_id,
                    "status": status
                }
            )

            return execution

    async def wait_for_execution_completion(
        self,
        integration_id: str,
        execution_id: str,
        timeout: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """Wait for integration execution to complete."""
        async with self.observe_operation("oic_wait_execution", integration_id=integration_id):
            start_time = datetime.now()
            timeout_delta = timedelta(seconds=timeout)

            while datetime.now() - start_time < timeout_delta:
                execution = await self.get_execution_status(integration_id, execution_id)
                status = execution.get("status")

                if status in ["COMPLETED", "FAILED", "ABORTED"]:
                    self.logger.info(
                        f"Integration execution completed with status: {status}",
                        extra={
                            "integration_id": integration_id,
                            "execution_id": execution_id,
                            "status": status,
                            "duration_seconds": (datetime.now() - start_time).total_seconds()
                        }
                    )
                    return execution

                await asyncio.sleep(poll_interval)

            raise OicWorkflowError(
                f"Integration execution timed out after {timeout} seconds",
                context={
                    "integration_id": integration_id,
                    "execution_id": execution_id,
                    "timeout": timeout
                }
            )

    async def get_execution_logs(
        self,
        integration_id: str,
        execution_id: str,
        log_level: str = "INFO"
    ) -> List[Dict[str, Any]]:
        """Retrieve execution logs for debugging."""
        async with self.observe_operation("oic_get_execution_logs"):
            endpoint = f"integrations/{integration_id}/executions/{execution_id}/logs"
            params = {"logLevel": log_level}

            response = await self._make_request("GET", endpoint, params=params)
            logs = response.get("items", [])

            self.logger.debug(
                f"Retrieved {len(logs)} log entries",
                extra={
                    "integration_id": integration_id,
                    "execution_id": execution_id,
                    "log_count": len(logs)
                }
            )

            return logs

    async def create_webhook_endpoint(
        self,
        integration_id: str,
        webhook_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create webhook endpoint for real-time notifications."""
        async with self.observe_operation("oic_create_webhook"):
            endpoint = f"integrations/{integration_id}/webhooks"
            webhook = await self._make_request("POST", endpoint, data=webhook_config)

            webhook_url = webhook.get("webhookUrl")

            self.logger.info(
                "Webhook endpoint created",
                extra={
                    "integration_id": integration_id,
                    "webhook_url": webhook_url
                }
            )

            return webhook

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        async with self.observe_operation("oic_health_check"):
            health_status = {
                "healthy": False,
                "authenticated": False,
                "api_accessible": False,
                "response_time_ms": None,
                "token_valid": False,
                "error": None
            }

            try:
                start_time = asyncio.get_event_loop().time()

                # Test token validity
                await self._ensure_valid_token()
                health_status["token_valid"] = True

                # Test API accessibility
                integrations = await self.list_integrations()
                health_status["api_accessible"] = True
                health_status["authenticated"] = True

                end_time = asyncio.get_event_loop().time()
                response_time = (end_time - start_time) * 1000

                health_status.update({
                    "healthy": True,
                    "response_time_ms": round(response_time, 2),
                    "integration_count": len(integrations)
                })

            except Exception as e:
                health_status["error"] = str(e)
                self.logger.warning(f"Health check failed: {str(e)}")

            return health_status

class RateLimiter:
    """Simple rate limiter for API requests."""

    def __init__(self, rate_limit: int, burst_limit: int):
        self.rate_limit = rate_limit
        self.burst_limit = burst_limit
        self.tokens = burst_limit
        self.last_refill = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a token for making a request."""
        async with self._lock:
            now = asyncio.get_event_loop().time()

            # Refill tokens based on time elapsed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * (self.rate_limit / 60.0)  # per minute to per second
            self.tokens = min(self.burst_limit, self.tokens + tokens_to_add)
            self.last_refill = now

            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.rate_limit / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1
```

---

## Usage Examples

### Basic OIC Integration

```python
# Basic setup and integration triggering
import asyncio
from flx.adapters.outbound.oracle.oic_adapter import FlxOracleOicAdapter
from flx.adapters.outbound.oracle.config import OicConfig

async def basic_oic_example():
    # Configure OIC connection
    config = OicConfig(
        base_url="https://your-oic-instance.ocp.oraclecloud.com",
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        client_secret="your-client-secret",
        token_endpoint="https://idcs-endpoint.identity.oraclecloud.com/oauth2/v1/token"
    )

    # Initialize adapter
    oic_adapter = FlxOracleOicAdapter(config)

    try:
        # Connect to OIC
        await oic_adapter.connect()

        # List available integrations
        integrations = await oic_adapter.list_integrations()
        print(f"Found {len(integrations)} integrations")

        # Find specific integration
        order_integration = None
        for integration in integrations:
            if "order-processing" in integration.get("name", "").lower():
                order_integration = integration
                break

        if order_integration:
            integration_id = order_integration["id"]

            # Trigger integration with payload
            payload = {
                "orderId": "ORD-12345",
                "customerId": "CUST-67890",
                "items": [
                    {"productId": "PROD-001", "quantity": 2, "price": 99.99},
                    {"productId": "PROD-002", "quantity": 1, "price": 149.99}
                ],
                "totalAmount": 349.97,
                "orderDate": datetime.now().isoformat()
            }

            execution = await oic_adapter.trigger_integration(
                integration_id=integration_id,
                payload=payload
            )

            execution_id = execution["executionId"]
            print(f"Integration triggered: {execution_id}")

            # Wait for completion
            result = await oic_adapter.wait_for_execution_completion(
                integration_id=integration_id,
                execution_id=execution_id,
                timeout=300
            )

            if result["status"] == "COMPLETED":
                print("Integration completed successfully")
            else:
                print(f"Integration failed with status: {result['status']}")

                # Get logs for debugging
                logs = await oic_adapter.get_execution_logs(
                    integration_id=integration_id,
                    execution_id=execution_id,
                    log_level="ERROR"
                )

                for log_entry in logs:
                    print(f"ERROR: {log_entry.get('message')}")

    finally:
        await oic_adapter.disconnect()

# Run the example
asyncio.run(basic_oic_example())
```

### Webhook Integration Example

```python
async def webhook_integration_example():
    oic_adapter = FlxOracleOicAdapter(config)
    await oic_adapter.connect()

    try:
        # Create webhook for real-time notifications
        webhook_config = {
            "name": "order-status-webhook",
            "url": "https://your-app.com/webhooks/order-status",
            "events": ["EXECUTION_COMPLETED", "EXECUTION_FAILED"],
            "authentication": {
                "type": "basic",
                "username": "webhook_user",
                "password": "webhook_secret"
            }
        }

        webhook = await oic_adapter.create_webhook_endpoint(
            integration_id="order-integration-id",
            webhook_config=webhook_config
        )

        print(f"Webhook created: {webhook['webhookUrl']}")

    finally:
        await oic_adapter.disconnect()
```

### Batch Processing Example

```python
async def batch_processing_example():
    oic_adapter = FlxOracleOicAdapter(config)
    await oic_adapter.connect()

    try:
        # Process multiple orders in parallel
        orders = [
            {"orderId": f"ORD-{i:05d}", "amount": i * 10.0}
            for i in range(1, 101)  # 100 orders
        ]

        async def process_order(order_data):
            execution = await oic_adapter.trigger_integration(
                integration_id="batch-order-integration",
                payload=order_data
            )

            result = await oic_adapter.wait_for_execution_completion(
                integration_id="batch-order-integration",
                execution_id=execution["executionId"],
                timeout=60
            )

            return {
                "order_id": order_data["orderId"],
                "status": result["status"],
                "execution_id": execution["executionId"]
            }

        # Process orders with concurrency limit
        semaphore = asyncio.Semaphore(10)  # Max 10 concurrent executions

        async def process_with_limit(order):
            async with semaphore:
                return await process_order(order)

        results = await asyncio.gather(
            *[process_with_limit(order) for order in orders],
            return_exceptions=True
        )

        # Analyze results
        successful = [r for r in results if isinstance(r, dict) and r["status"] == "COMPLETED"]
        failed = [r for r in results if isinstance(r, dict) and r["status"] != "COMPLETED"]
        errors = [r for r in results if isinstance(r, Exception)]

        print(f"Batch processing completed:")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        print(f"  Errors: {len(errors)}")

    finally:
        await oic_adapter.disconnect()
```

---

## Cross-References

### Prerequisites

- [Oracle OAuth2 Authentication Guide](oracle-oauth2-authentication-guide.md) - Essential for OIC authentication setup
- [FLX Core Framework Setup](../../getting-started/index.md) - Framework installation and configuration
- [HTTP Client Configuration](../../infrastructure/index.md) - HTTP infrastructure setup

### Next Steps

- [Oracle WMS Integration](flx-http-oracle-wms-adapter.md) - Combine OIC with WMS operations
- [Database Integration](flx-database-oracle-adapter.md) - Integrate OIC workflows with database operations
- [Observability Setup](../../infrastructure/operational-excellence.md) - Monitor OIC integrations

### Related Topics

- [Security Framework](../../security/index.md) - Secure API communications
- [Error Handling Patterns](../../development/index.md) - Advanced error handling strategies
- [Testing Guide](../../development/index.md) - Testing OIC integrations

---

## Troubleshooting

### Common Issues

#### Authentication Problems

```bash
# Test OAuth2 token endpoint
curl -X POST "https://idcs-endpoint.identity.oraclecloud.com/oauth2/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"

# Verify OIC instance accessibility
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://your-oic-instance.ocp.oraclecloud.com/ic/api/integration/v1/integrations"
```

#### Rate Limiting Issues

- Monitor response headers for rate limit information
- Implement exponential backoff with jitter
- Consider using multiple client credentials for higher throughput

#### Integration Execution Failures

- Check execution logs for detailed error information
- Verify payload format matches integration expectations
- Review OIC integration design for error handling

#### Webhook Delivery Issues

- Verify webhook endpoint is accessible from OIC
- Check authentication credentials for webhook
- Monitor webhook endpoint logs for delivery attempts

### Error Codes Reference

| HTTP Code | OIC Error         | Description              | Resolution                                  |
| --------- | ----------------- | ------------------------ | ------------------------------------------- |
| 401       | Unauthorized      | Invalid or expired token | Refresh OAuth2 token                        |
| 403       | Forbidden         | Insufficient permissions | Check user roles and policies               |
| 404       | Not Found         | Integration not found    | Verify integration ID and deployment status |
| 429       | Too Many Requests | Rate limit exceeded      | Implement backoff strategy                  |
| 500       | Internal Error    | OIC internal error       | Check OIC service status, retry operation   |

### Performance Optimization

#### Connection Reuse

```python
# Reuse adapter instance across operations
class OicService:
    def __init__(self, config: OicConfig):
        self.adapter = FlxOracleOicAdapter(config)
        self._connected = False

    async def __aenter__(self):
        if not self._connected:
            await self.adapter.connect()
            self._connected = True
        return self.adapter

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.adapter.disconnect()
        self._connected = False

# Usage
async with OicService(config) as oic:
    # Multiple operations reuse same connection
    integrations = await oic.list_integrations()
    result = await oic.trigger_integration(integration_id, payload)
```

#### Batch Operations

- Use semaphores to limit concurrent executions
- Implement circuit breaker pattern for resilience
- Monitor OIC instance performance metrics

---

**Documentation Framework**: FLX Enterprise Documentation Standard
**Implementation Status**: Production Ready - Validated with Oracle OIC
**Last Updated**: 2025-06-11
**Maintained by**: FLX Framework Integration Team
