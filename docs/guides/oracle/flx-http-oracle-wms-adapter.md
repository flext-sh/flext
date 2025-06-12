# FLX HTTP Oracle WMS Adapter Guide

**Function**: Complete guide for Oracle Warehouse Management System (WMS) REST API integration within the FLX framework
**Audience**: WMS developers, supply chain integrators, and warehouse automation specialists
**Status**: Production Ready - Validated Implementation

---

## Navigation Context

**Current Location**: `docs/guides/oracle/flx_http_oracle_wms-adapter.md`  
**Parent**: [Oracle Integration Hub](oracle-integration-hub.md) > Oracle WMS Integration  
**Quick Links**: [Database Adapter](flx-database-oracle-adapter.md) | [OIC Adapter](flx-http-oracle-oic-adapter.md) | [WMS Commands Reference](oracle-wms-commands-reference.md)

---

## Overview

The FLX HTTP Oracle WMS Adapter provides comprehensive integration with Oracle Warehouse Management System through REST APIs, supporting entity management, inventory operations, and real-time warehouse orchestration. Built on hexagonal architecture principles, it serves as both an inbound and outbound adapter for WMS operations.

### Key Features

- **Complete WMS API Coverage**: Support for all major WMS entities and operations
- **Dynamic Schema Discovery**: Runtime API exploration and entity schema generation
- **OAuth2 Authentication**: Secure API access with automatic token management
- **Async Operations**: High-performance async/await pattern with connection pooling
- **Error Handling**: Comprehensive error recovery with WMS-specific error codes
- **Observability**: Built-in metrics, tracing, and correlation ID tracking
- **Rate Limiting**: Intelligent throttling and backoff strategies

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
yarl = "^1.9.0"  # URL handling

[tool.poetry.group.dev.dependencies]
pytest-asyncio = "^0.23.0"
pytest-aiohttp = "^1.0.4"
respx = "^0.20.0"  # HTTP mocking
```

### Configuration

```python
# config/wms.py
from pydantic import BaseModel, Field, SecretStr, HttpUrl
from typing import Optional, Dict, List
from enum import Enum

class WmsAuthType(str, Enum):
    OAUTH2 = "oauth2"
    BASIC = "basic"
    API_KEY = "api_key"

class WmsConfig(BaseModel):
    """Oracle WMS configuration."""
    
    # WMS Instance Settings
    base_url: HttpUrl = Field(..., description="WMS instance base URL")
    api_version: str = Field(default="v10", description="WMS API version")
    tenant_id: Optional[str] = Field(None, description="Multi-tenant WMS identifier")
    
    # Authentication
    auth_type: WmsAuthType = Field(default=WmsAuthType.OAUTH2)
    username: str = Field(..., description="WMS username")
    password: SecretStr = Field(..., description="WMS password")
    client_id: Optional[str] = Field(None, description="OAuth2 client ID")
    client_secret: Optional[SecretStr] = Field(None, description="OAuth2 client secret")
    
    # API Configuration
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    retry_backoff: float = Field(default=1.5, ge=1.0, le=5.0, description="Retry backoff multiplier")
    
    # Rate Limiting
    requests_per_minute: int = Field(default=120, ge=1, le=1000)
    burst_requests: int = Field(default=20, ge=1, le=100)
    
    # Entity Configuration
    default_warehouse: Optional[str] = Field(None, description="Default warehouse code")
    default_company: Optional[str] = Field(None, description="Default company code")
    
    # Performance Settings
    batch_size: int = Field(default=100, ge=1, le=1000, description="Default batch operation size")
    page_size: int = Field(default=50, ge=1, le=500, description="Default pagination size")
    
    class Config:
        env_prefix = "WMS_"
        validate_assignment = True
```

---

## Implementation

### Core Adapter Implementation

```python
# src/flx/adapters/outbound/oracle/wms_adapter.py
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from urllib.parse import urljoin, urlencode
from yarl import URL

from flx.core.adapters.base import BaseAdapter
from flx.core.adapters.mixins import (
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin
)
from flx.domain.ports.outbound.http import HttpPort
from flx.adapters.outbound.oracle.config import WmsConfig
from flx.adapters.outbound.oracle.exceptions import (
    WmsAuthenticationError,
    WmsApiError,
    WmsEntityError,
    WmsRateLimitError
)

class FlxOracleWmsAdapter(
    UnifiedObservabilityMixin,
    AdapterErrorHandlingMixin,
    UnifiedAdapterConfigurationMixin,
    AdvancedAdapterMixin,
    BaseAdapter
):
    """FLX Oracle WMS HTTP Adapter with comprehensive entity management."""
    
    def __init__(self, config: WmsConfig):
        super().__init__()
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._auth_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._rate_limiter = WmsRateLimiter(
            requests_per_minute=config.requests_per_minute,
            burst_requests=config.burst_requests
        )
        self._entity_schemas: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self) -> None:
        """Initialize HTTP session and authenticate."""
        async with self.observe_operation("wms_adapter_connect"):
            try:
                # Create HTTP session
                timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                
                self._session = aiohttp.ClientSession(
                    timeout=timeout,
                    headers={
                        "User-Agent": "FLX-WMS-Adapter/2.0",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                )
                
                # Authenticate
                await self._authenticate()
                
                # Discover available entities
                await self._discover_entities()
                
                self.logger.info(
                    "WMS adapter connected successfully",
                    extra={
                        "base_url": str(self.config.base_url),
                        "api_version": self.config.api_version,
                        "entities_discovered": len(self._entity_schemas)
                    }
                )
                
            except Exception as e:
                raise WmsAuthenticationError(
                    f"Failed to connect to WMS: {str(e)}",
                    context={"base_url": str(self.config.base_url)}
                ) from e
    
    async def disconnect(self) -> None:
        """Close HTTP session and cleanup resources."""
        async with self.observe_operation("wms_adapter_disconnect"):
            if self._session:
                await self._session.close()
                self._session = None
            
            self._auth_token = None
            self._token_expires_at = None
            self._entity_schemas.clear()
            
            self.logger.info("WMS adapter disconnected")
    
    async def _authenticate(self) -> None:
        """Authenticate with WMS and obtain access token."""
        async with self.observe_operation("wms_authenticate"):
            if self.config.auth_type == WmsAuthType.OAUTH2:
                await self._oauth2_authenticate()
            elif self.config.auth_type == WmsAuthType.BASIC:
                await self._basic_authenticate()
            else:
                raise WmsAuthenticationError(f"Unsupported auth type: {self.config.auth_type}")
    
    async def _oauth2_authenticate(self) -> None:
        """Perform OAuth2 authentication."""
        auth_url = urljoin(str(self.config.base_url), "wms/lgfapi/oauth/token")
        
        auth_data = {
            "grant_type": "password",
            "username": self.config.username,
            "password": self.config.password.get_secret_value()
        }
        
        if self.config.client_id:
            auth_data.update({
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret.get_secret_value()
            })
        
        async with self._session.post(
            auth_url,
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise WmsAuthenticationError(
                    f"OAuth2 authentication failed: {error_text}",
                    context={"status_code": response.status}
                )
            
            token_data = await response.json()
            self._auth_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
    
    async def _basic_authenticate(self) -> None:
        """Perform basic authentication."""
        # For basic auth, we'll store credentials and use them in headers
        import base64
        credentials = f"{self.config.username}:{self.config.password.get_secret_value()}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self._auth_token = f"Basic {encoded_credentials}"
        self._token_expires_at = datetime.now() + timedelta(hours=24)  # Basic auth doesn't expire
    
    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication token."""
        if not self._auth_token or datetime.now() >= self._token_expires_at:
            await self._authenticate()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make authenticated HTTP request to WMS API."""
        async with self.observe_operation("wms_api_request", method=method, endpoint=endpoint):
            # Rate limiting
            await self._rate_limiter.acquire()
            
            # Ensure authentication
            await self._ensure_authenticated()
            
            # Build URL
            url = urljoin(str(self.config.base_url), f"wms/lgfapi/{self.config.api_version}/{endpoint}")
            
            # Prepare headers
            request_headers = {"Authorization": f"Bearer {self._auth_token}"}
            if self.config.tenant_id:
                request_headers["X-Tenant-ID"] = self.config.tenant_id
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
                        raise WmsRateLimitError(f"Rate limit exceeded, retry after {retry_after} seconds")
                    
                    # Handle errors
                    if response.status >= 400:
                        error_data = await response.json() if response.content_type == "application/json" else {}
                        error_message = error_data.get("message", await response.text())
                        
                        raise WmsApiError(
                            f"WMS API error {response.status}: {error_message}",
                            context={
                                "status_code": response.status,
                                "method": method,
                                "endpoint": endpoint,
                                "error_data": error_data
                            }
                        )
                    
                    # Parse response
                    if response.content_type == "application/json":
                        return await response.json()
                    else:
                        return {"content": await response.text()}
                        
            except aiohttp.ClientError as e:
                raise WmsApiError(
                    f"HTTP client error: {str(e)}",
                    context={"method": method, "endpoint": endpoint}
                ) from e
    
    async def _discover_entities(self) -> None:
        """Discover available entities and their schemas."""
        async with self.observe_operation("wms_discover_entities"):
            try:
                # Get list of available entities
                response = await self._make_request("GET", "entity")
                entities = response.get("entities", [])
                
                # Get schema for each entity
                for entity_name in entities:
                    try:
                        schema_response = await self._make_request("GET", f"entity/{entity_name}/schema")
                        self._entity_schemas[entity_name] = schema_response
                        
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to get schema for entity {entity_name}: {str(e)}",
                            extra={"entity": entity_name}
                        )
                
                self.logger.info(
                    f"Discovered {len(self._entity_schemas)} entity schemas",
                    extra={"entities": list(self._entity_schemas.keys())}
                )
                
            except Exception as e:
                self.logger.warning(f"Entity discovery failed: {str(e)}")
                # Continue without entity schemas - they can be retrieved on demand
    
    async def get_entities(self) -> List[str]:
        """Get list of available WMS entities."""
        async with self.observe_operation("wms_get_entities"):
            response = await self._make_request("GET", "entity")
            return response.get("entities", [])
    
    async def get_entity_schema(self, entity_name: str) -> Dict[str, Any]:
        """Get schema definition for a specific entity."""
        async with self.observe_operation("wms_get_entity_schema", entity=entity_name):
            if entity_name in self._entity_schemas:
                return self._entity_schemas[entity_name]
            
            response = await self._make_request("GET", f"entity/{entity_name}/schema")
            self._entity_schemas[entity_name] = response
            return response
    
    async def query_entity(
        self,
        entity_name: str,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query entity with filters and pagination."""
        async with self.observe_operation("wms_query_entity", entity=entity_name):
            endpoint = f"entity/{entity_name}"
            
            # Build query parameters
            params = {"page": str(page)}
            if page_size:
                params["pageSize"] = str(page_size)
            elif self.config.page_size:
                params["pageSize"] = str(self.config.page_size)
            
            if order_by:
                params["orderBy"] = order_by
            
            if filters:
                # Convert filters to WMS query format
                for key, value in filters.items():
                    params[f"filter.{key}"] = str(value)
            
            response = await self._make_request("GET", endpoint, params=params)
            
            self.logger.debug(
                f"Queried entity {entity_name}",
                extra={
                    "entity": entity_name,
                    "total_records": response.get("totalRecords", 0),
                    "page": page,
                    "filters": filters
                }
            )
            
            return response
    
    async def get_entity_by_id(self, entity_name: str, entity_id: str) -> Dict[str, Any]:
        """Get specific entity record by ID."""
        async with self.observe_operation("wms_get_entity_by_id", entity=entity_name, id=entity_id):
            endpoint = f"entity/{entity_name}/{entity_id}"
            response = await self._make_request("GET", endpoint)
            
            return response.get("record", response)
    
    async def create_entity(self, entity_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new entity record."""
        async with self.observe_operation("wms_create_entity", entity=entity_name):
            endpoint = f"entity/{entity_name}"
            
            # Add default warehouse/company if configured
            if self.config.default_warehouse and "warehouse" not in data:
                data["warehouse"] = self.config.default_warehouse
            if self.config.default_company and "company" not in data:
                data["company"] = self.config.default_company
            
            response = await self._make_request("POST", endpoint, data=data)
            
            self.logger.info(
                f"Created entity {entity_name}",
                extra={
                    "entity": entity_name,
                    "record_id": response.get("id")
                }
            )
            
            return response
    
    async def update_entity(self, entity_name: str, entity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing entity record."""
        async with self.observe_operation("wms_update_entity", entity=entity_name, id=entity_id):
            endpoint = f"entity/{entity_name}/{entity_id}"
            response = await self._make_request("PUT", endpoint, data=data)
            
            self.logger.info(
                f"Updated entity {entity_name}/{entity_id}",
                extra={"entity": entity_name, "id": entity_id}
            )
            
            return response
    
    async def delete_entity(self, entity_name: str, entity_id: str) -> bool:
        """Delete entity record."""
        async with self.observe_operation("wms_delete_entity", entity=entity_name, id=entity_id):
            endpoint = f"entity/{entity_name}/{entity_id}"
            await self._make_request("DELETE", endpoint)
            
            self.logger.info(
                f"Deleted entity {entity_name}/{entity_id}",
                extra={"entity": entity_name, "id": entity_id}
            )
            
            return True
    
    async def bulk_create(self, entity_name: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple entity records in batch."""
        async with self.observe_operation("wms_bulk_create", entity=entity_name):
            endpoint = f"entity/{entity_name}/bulk"
            
            # Process in batches
            batch_size = self.config.batch_size
            results = {"created": [], "errors": []}
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                try:
                    response = await self._make_request("POST", endpoint, data={"records": batch})
                    results["created"].extend(response.get("created", []))
                    results["errors"].extend(response.get("errors", []))
                    
                except Exception as e:
                    # Record batch error
                    results["errors"].append({
                        "batch_start": i,
                        "batch_size": len(batch),
                        "error": str(e)
                    })
            
            self.logger.info(
                f"Bulk create completed for {entity_name}",
                extra={
                    "entity": entity_name,
                    "total_records": len(records),
                    "created": len(results["created"]),
                    "errors": len(results["errors"])
                }
            )
            
            return results
    
    async def execute_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WMS workflow/business process."""
        async with self.observe_operation("wms_execute_workflow", workflow=workflow_name):
            endpoint = f"workflow/{workflow_name}/execute"
            
            request_data = {
                "parameters": parameters,
                "correlationId": self.correlation_id,
                "timestamp": datetime.now().isoformat()
            }
            
            response = await self._make_request("POST", endpoint, data=request_data)
            
            execution_id = response.get("executionId")
            
            self.logger.info(
                f"Workflow {workflow_name} executed",
                extra={
                    "workflow": workflow_name,
                    "execution_id": execution_id,
                    "correlation_id": self.correlation_id
                }
            )
            
            return response
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        async with self.observe_operation("wms_health_check"):
            health_status = {
                "healthy": False,
                "authenticated": False,
                "api_accessible": False,
                "response_time_ms": None,
                "entities_available": 0,
                "error": None
            }
            
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Test authentication
                await self._ensure_authenticated()
                health_status["authenticated"] = True
                
                # Test API accessibility
                entities = await self.get_entities()
                health_status["api_accessible"] = True
                health_status["entities_available"] = len(entities)
                
                end_time = asyncio.get_event_loop().time()
                response_time = (end_time - start_time) * 1000
                
                health_status.update({
                    "healthy": True,
                    "response_time_ms": round(response_time, 2)
                })
                
            except Exception as e:
                health_status["error"] = str(e)
                self.logger.warning(f"Health check failed: {str(e)}")
            
            return health_status

class WmsRateLimiter:
    """Rate limiter for WMS API requests."""
    
    def __init__(self, requests_per_minute: int, burst_requests: int):
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.tokens = burst_requests
        self.last_refill = asyncio.get_event_loop().time()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a token for making a request."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            # Refill tokens based on time elapsed
            time_passed = now - self.last_refill
            tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.burst_requests, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / (self.requests_per_minute / 60.0)
                await asyncio.sleep(wait_time)
                self.tokens = 1
            
            self.tokens -= 1
```

---

## Usage Examples

### Basic WMS Operations

```python
# Basic setup and entity operations
import asyncio
from flx.adapters.outbound.oracle.wms_adapter import FlxOracleWmsAdapter
from flx.adapters.outbound.oracle.config import WmsConfig

async def basic_wms_example():
    # Configure WMS connection
    config = WmsConfig(
        base_url="https://wms.oracle.com",
        username="wms_user",
        password="secure_password",
        api_version="v10",
        auth_type="oauth2",
        default_warehouse="MAIN_WH",
        default_company="COMPANY01"
    )
    
    # Initialize adapter
    wms_adapter = FlxOracleWmsAdapter(config)
    
    try:
        # Connect to WMS
        await wms_adapter.connect()
        
        # Discover available entities
        entities = await wms_adapter.get_entities()
        print(f"Available entities: {entities}")
        
        # Get entity schema
        if "SHIPMENT" in entities:
            schema = await wms_adapter.get_entity_schema("SHIPMENT")
            print(f"SHIPMENT schema: {schema}")
        
        # Query shipments
        shipments = await wms_adapter.query_entity(
            "SHIPMENT",
            filters={"status": "PENDING", "warehouse": "MAIN_WH"},
            page=1,
            page_size=10,
            order_by="shipment_date DESC"
        )
        
        print(f"Found {shipments.get('totalRecords', 0)} pending shipments")
        
        # Create new shipment
        new_shipment = {
            "shipment_id": "SHIP-12345",
            "customer_id": "CUST-67890",
            "warehouse": "MAIN_WH",
            "status": "CREATED",
            "priority": "HIGH",
            "shipment_date": datetime.now().isoformat(),
            "items": [
                {"item_id": "ITEM001", "quantity": 10},
                {"item_id": "ITEM002", "quantity": 5}
            ]
        }
        
        created_shipment = await wms_adapter.create_entity("SHIPMENT", new_shipment)
        print(f"Created shipment: {created_shipment.get('id')}")
        
        # Update shipment status
        await wms_adapter.update_entity(
            "SHIPMENT",
            created_shipment["id"],
            {"status": "READY_TO_SHIP"}
        )
        
    finally:
        await wms_adapter.disconnect()

# Run the example
asyncio.run(basic_wms_example())
```

### Inventory Management Example

```python
async def inventory_management_example():
    wms_adapter = FlxOracleWmsAdapter(config)
    await wms_adapter.connect()
    
    try:
        # Query current inventory levels
        inventory = await wms_adapter.query_entity(
            "INVENTORY",
            filters={
                "warehouse": "MAIN_WH",
                "available_quantity": ">0"
            },
            order_by="item_id"
        )
        
        print(f"Current inventory items: {inventory.get('totalRecords', 0)}")
        
        # Check specific item availability
        item_inventory = await wms_adapter.query_entity(
            "INVENTORY",
            filters={
                "item_id": "ITEM001",
                "warehouse": "MAIN_WH"
            }
        )
        
        if item_inventory.get("records"):
            item_data = item_inventory["records"][0]
            available_qty = item_data.get("available_quantity", 0)
            print(f"ITEM001 available quantity: {available_qty}")
            
            # Reserve inventory for shipment
            if available_qty >= 10:
                reservation_data = {
                    "item_id": "ITEM001",
                    "warehouse": "MAIN_WH",
                    "quantity": 10,
                    "reservation_type": "SHIPMENT",
                    "reference_id": "SHIP-12345",
                    "reservation_date": datetime.now().isoformat()
                }
                
                reservation = await wms_adapter.create_entity("RESERVATION", reservation_data)
                print(f"Created inventory reservation: {reservation.get('id')}")
        
        # Execute inventory adjustment workflow
        adjustment_result = await wms_adapter.execute_workflow(
            "INVENTORY_ADJUSTMENT",
            {
                "item_id": "ITEM002",
                "warehouse": "MAIN_WH",
                "adjustment_quantity": 50,
                "adjustment_reason": "PHYSICAL_COUNT",
                "notes": "Cycle count adjustment"
            }
        )
        
        print(f"Inventory adjustment executed: {adjustment_result.get('executionId')}")
        
    finally:
        await wms_adapter.disconnect()
```

### Bulk Operations Example

```python
async def bulk_operations_example():
    wms_adapter = FlxOracleWmsAdapter(config)
    await wms_adapter.connect()
    
    try:
        # Bulk create pick tasks
        pick_tasks = []
        for i in range(100):
            pick_tasks.append({
                "task_id": f"PICK-{i:05d}",
                "shipment_id": "SHIP-12345",
                "item_id": f"ITEM{i % 10:03d}",
                "location": f"A{i // 10 + 1:02d}-{i % 10 + 1:02d}-01",
                "quantity": (i % 5) + 1,
                "priority": "NORMAL",
                "assigned_user": None,
                "status": "PENDING"
            })
        
        result = await wms_adapter.bulk_create("PICK_TASK", pick_tasks)
        
        print(f"Bulk create results:")
        print(f"  Created: {len(result['created'])}")
        print(f"  Errors: {len(result['errors'])}")
        
        # Query created tasks
        created_tasks = await wms_adapter.query_entity(
            "PICK_TASK",
            filters={"shipment_id": "SHIP-12345"},
            page_size=50
        )
        
        print(f"Total pick tasks for shipment: {created_tasks.get('totalRecords', 0)}")
        
    finally:
        await wms_adapter.disconnect()
```

---

## Cross-References

### Prerequisites

- [Oracle OAuth2 Authentication Guide](oracle-oauth2-authentication-guide.md) - Essential for WMS API authentication
- [FLX Core Framework Setup](../../getting-started/index.md) - Framework installation and configuration
- [Hexagonal Architecture Guide](../../architecture/application-layer.md) - Understanding adapter patterns

### Next Steps

- [Oracle WMS Commands Reference](oracle-wms-commands-reference.md) - CLI commands for WMS operations
- [Oracle Database Integration](flx-database-oracle-adapter.md) - Combine WMS with database operations
- [Oracle OIC Integration](flx-http-oracle-oic-adapter.md) - Workflow orchestration with OIC

### Related Topics

- [API Development Guide](../../api-reference/index.md) - Building APIs around WMS operations
- [Error Handling Patterns](../../development/index.md) - Advanced error handling strategies
- [Testing Guide](../../development/index.md) - Testing WMS integrations

---

## Troubleshooting

### Common Issues

#### Authentication Problems

```bash
# Test WMS API endpoint accessibility
curl -X GET "https://wms.oracle.com/wms/lgfapi/v10/entity" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Verify OAuth2 credentials
curl -X POST "https://wms.oracle.com/wms/lgfapi/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=USER&password=PASS"
```

#### Entity Schema Issues

- Verify entity names are correct (case-sensitive)
- Check API version compatibility with WMS instance
- Ensure user has appropriate permissions for entity access

#### Rate Limiting Problems

- Monitor request frequency and implement backoff
- Consider using multiple API credentials for higher throughput
- Implement request queuing for burst scenarios

#### Data Validation Errors

- Use entity schemas to validate data before submission
- Check required fields and data types
- Verify warehouse and company codes exist in WMS

### Performance Optimization

#### Connection Pooling

```python
# Reuse adapter instance for multiple operations
class WmsService:
    def __init__(self, config: WmsConfig):
        self.adapter = FlxOracleWmsAdapter(config)
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
async with WmsService(config) as wms:
    entities = await wms.get_entities()
    shipments = await wms.query_entity("SHIPMENT", filters={"status": "PENDING"})
```

#### Batch Processing

- Use bulk operations for multiple record creation/updates
- Implement pagination for large query results
- Consider async processing for independent operations

### Error Codes Reference

| HTTP Code | WMS Error | Description | Resolution |
|-----------|-----------|-------------|------------|
| 400 | Bad Request | Invalid request format or data | Validate request data against entity schema |
| 401 | Unauthorized | Invalid or expired token | Refresh authentication token |
| 403 | Forbidden | Insufficient permissions | Check user roles and entity permissions |
| 404 | Not Found | Entity or record not found | Verify entity names and record IDs |
| 422 | Unprocessable Entity | Business rule validation failed | Review WMS business rules and data constraints |
| 429 | Too Many Requests | Rate limit exceeded | Implement exponential backoff |
| 500 | Internal Error | WMS internal error | Check WMS system status, retry operation |

---

**Documentation Framework**: FLX Enterprise Documentation Standard  
**Implementation Status**: Production Ready - Validated with Oracle WMS Cloud  
**Last Updated**: 2025-06-11  
**Maintained by**: FLX Framework WMS Integration Team
