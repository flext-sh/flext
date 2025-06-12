# Oracle WMS Comprehensive Integration Guide

> **Function**: Complete Oracle WMS integration guide with validated code examples | **Audience**: Integration developers, WMS implementers | **Status**: ✅ VALIDATED

[![Oracle WMS](https://img.shields.io/badge/oracle-wms-red.svg)](./index.md)
[![Validated](https://img.shields.io/badge/code-validated-green.svg)](../../../flx_http_oracle_wms/)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Complete Oracle Warehouse Management System (WMS) integration guide validated against actual FLX implementation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: Oracle WMS Integration Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[WMS INTEGRATION]** → [WMS CLI Guide](./oracle-wms-cli-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Oracle Integration Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Oracle WMS](../../../flx_http_oracle_wms/)
- **🔗 Related**: [Oracle Authentication](./oracle-authentication-unified-guide.md), [WMS CLI Guide](./oracle-wms-cli-guide.md)

---

## 📋 **Overview**

This guide provides comprehensive Oracle WMS integration using the FLX framework. It covers the actual `WmsClient` implementation, authentication, REST API operations, and practical examples validated against production systems.

### **Prerequisites**

- [Oracle Authentication Guide](./oracle-authentication-unified-guide.md) - Authentication setup and configuration
- [Getting Started](../../getting-started/index.md) - FLX Framework basics
- [HTTP Integration Patterns](../development/http-integration-patterns.md) - HTTP client patterns

### **What You'll Learn**

- How to use the `WmsClient` class for Oracle WMS integration
- Authentication and configuration patterns
- REST API operations with real examples
- Error handling and troubleshooting
- Advanced integration patterns

---

## 🔧 **WmsClient Implementation**

### **Real Implementation Overview**

**Source**: `/flx_http_oracle_wms/src/flx_http_oracle_wms/wms_client.py` (validated)

The Oracle WMS integration uses the `WmsClient` class, not "OracleWmsRestAdapter":

```python
from flx_http_oracle_wms.wms_client import WmsClient
from flx_http_oracle_wms.config import WmsConfig

# Real WMS client implementation (validated)
config = WmsConfig(
    base_url="https://your-wms-instance.oraclecloud.com",
    username="your_username",
    password="your_password",
    facility="DC01",
    company="COMPANY",
    user_language="en"
)

wms_client = WmsClient(config)
```

### **Configuration Management**

**Source**: `/flx_http_oracle_wms/src/flx_http_oracle_wms/config.py` (validated)

```python
from flx_http_oracle_wms.config import WmsConfig

# Production configuration
config = WmsConfig(
    base_url="https://your-wms.oraclecloud.com",
    username="api_user",
    password="secure_password", 
    facility="DC01",
    company="YOUR_COMPANY",
    user_language="en",
    
    # Optional configuration
    session_timeout=3600,
    max_retries=3,
    request_timeout=300.0
)

# Configuration from environment variables
config = WmsConfig.from_env()

# Get WMS headers (validated method)
headers = config.get_wms_headers()
# Returns: {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     'wms-username': 'api_user',
#     'wms-facility': 'DC01',
#     'wms-company': 'YOUR_COMPANY'
# }
```

---

## 🚀 **Basic Operations**

### **Client Lifecycle Management**

```python
async def wms_integration_example():
    """Complete WMS integration example."""
    
    # Initialize client
    config = WmsConfig.from_env()
    wms_client = WmsClient(config)
    
    try:
        # Start client and discover endpoints
        await wms_client.start()
        
        # Perform WMS operations
        entities = await wms_client.get_entities()
        print(f"Available entities: {entities}")
        
        # Get specific entity data
        orders = await wms_client.get_entity_data("order_hdr", limit=10)
        print(f"Found {len(orders)} orders")
        
    finally:
        # Always clean up
        await wms_client.stop()

# Using context manager (recommended)
async def context_manager_example():
    """WMS client with context manager."""
    config = WmsConfig.from_env()
    
    async with WmsClient(config) as wms:
        entities = await wms.get_entities()
        orders = await wms.get_entity_data("order_hdr")
        return orders
```

### **Entity Discovery and Schema**

**Validated methods from real implementation**:

```python
async def discover_wms_structure():
    """Discover WMS entities and schemas."""
    
    async with WmsClient(config) as wms:
        # Discover available entities (validated method)
        entities = await wms.get_entities()
        print("Available entities:")
        for entity in entities:
            print(f"  - {entity}")
        
        # Get entity schema (validated method)
        order_schema = await wms.get_entity_schema("order_hdr")
        print(f"Order header fields: {order_schema.keys()}")
        
        # Get entity metadata
        inventory_schema = await wms.get_entity_schema("inventory")
        print(f"Inventory fields: {list(inventory_schema.keys())[:10]}...")
```

### **Data Retrieval Operations**

```python
async def retrieve_wms_data():
    """Retrieve data from WMS entities."""
    
    async with WmsClient(config) as wms:
        # Get entity data with pagination (validated method)
        orders = await wms.get_entity_data(
            entity_name="order_hdr",
            limit=100,
            offset=0
        )
        
        # Get specific record by ID
        order_id = orders[0].get("order_id") if orders else None
        if order_id:
            order_detail = await wms.get_entity_record(
                entity_name="order_hdr",
                record_id=order_id
            )
            print(f"Order detail: {order_detail}")
        
        # Get inventory data
        inventory = await wms.get_entity_data(
            entity_name="inventory",
            limit=50
        )
        print(f"Retrieved {len(inventory)} inventory records")
```

---

## 📝 **CRUD Operations**

### **Create Operations**

```python
async def create_wms_records():
    """Create new records in WMS."""
    
    async with WmsClient(config) as wms:
        # Create new order header
        new_order = {
            "order_number": "ORD-2025-001",
            "customer_id": "CUST001",
            "order_type": "OUTBOUND",
            "priority": "HIGH",
            "expected_ship_date": "2025-01-15T10:00:00Z"
        }
        
        created_order = await wms.create_record(
            entity_name="order_hdr",
            data=new_order
        )
        print(f"Created order: {created_order}")
        
        # Create order line
        order_line = {
            "order_id": created_order["order_id"],
            "item_id": "ITEM001",
            "quantity": 10,
            "unit_of_measure": "EA"
        }
        
        created_line = await wms.create_record(
            entity_name="order_line",
            data=order_line
        )
        print(f"Created order line: {created_line}")
```

### **Update Operations**

```python
async def update_wms_records():
    """Update existing WMS records."""
    
    async with WmsClient(config) as wms:
        # Update order status
        order_id = "12345"
        update_data = {
            "status": "PROCESSING",
            "priority": "URGENT",
            "notes": "Rush order - expedite processing"
        }
        
        updated_order = await wms.update_record(
            entity_name="order_hdr",
            record_id=order_id,
            data=update_data
        )
        print(f"Updated order: {updated_order}")
```

### **Delete Operations**

```python
async def delete_wms_records():
    """Delete WMS records."""
    
    async with WmsClient(config) as wms:
        # Delete order line
        order_line_id = "67890"
        success = await wms.delete_record(
            entity_name="order_line",
            record_id=order_line_id
        )
        
        if success:
            print(f"Successfully deleted order line {order_line_id}")
        else:
            print(f"Failed to delete order line {order_line_id}")
```

---

## 🔍 **Advanced Query Operations**

### **Filtering and Search**

```python
async def advanced_queries():
    """Advanced WMS query operations."""
    
    async with WmsClient(config) as wms:
        # Filter by date range
        recent_orders = await wms.get_entity_data(
            entity_name="order_hdr",
            filters={
                "created_date__gte": "2025-01-01T00:00:00Z",
                "created_date__lte": "2025-01-31T23:59:59Z",
                "status": "ACTIVE"
            },
            limit=100
        )
        
        # Filter by multiple values
        priority_orders = await wms.get_entity_data(
            entity_name="order_hdr",
            filters={
                "priority__in": ["HIGH", "URGENT"],
                "facility": config.facility
            }
        )
        
        # Search with sorting
        sorted_inventory = await wms.get_entity_data(
            entity_name="inventory",
            filters={"quantity__gt": 0},
            sort_by="item_id",
            sort_order="asc",
            limit=200
        )
```

### **Batch Operations**

```python
async def batch_operations():
    """Efficient batch operations."""
    
    async with WmsClient(config) as wms:
        # Batch create multiple orders
        orders_data = [
            {
                "order_number": f"BATCH-{i:04d}",
                "customer_id": f"CUST{i:03d}",
                "order_type": "OUTBOUND"
            }
            for i in range(1, 11)
        ]
        
        created_orders = await wms.batch_create(
            entity_name="order_hdr",
            data_list=orders_data
        )
        print(f"Created {len(created_orders)} orders in batch")
        
        # Batch update
        update_data = {"status": "READY"}
        order_ids = [order["order_id"] for order in created_orders]
        
        updated_count = await wms.batch_update(
            entity_name="order_hdr",
            record_ids=order_ids,
            data=update_data
        )
        print(f"Updated {updated_count} orders")
```

---

## 🏥 **Health Monitoring and Diagnostics**

### **Health Checks**

```python
async def monitor_wms_health():
    """Monitor WMS client health."""
    
    async with WmsClient(config) as wms:
        # Check WMS health
        health = await wms.health_check()
        print(f"WMS Health: {health}")
        
        # Get API information
        api_info = await wms.get_api_info()
        print(f"API Version: {api_info.get('version')}")
        print(f"Available endpoints: {api_info.get('endpoints', [])}")
        
        # Connection diagnostics
        diagnostics = await wms.get_diagnostics()
        print(f"Connection status: {diagnostics}")
```

### **Performance Monitoring**

```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def timed_operation(operation_name: str):
    """Time WMS operations for performance monitoring."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        print(f"{operation_name} took {duration:.2f} seconds")

async def performance_monitoring():
    """Monitor WMS operation performance."""
    
    async with WmsClient(config) as wms:
        # Time entity discovery
        async with timed_operation("Entity discovery"):
            entities = await wms.get_entities()
        
        # Time data retrieval
        async with timed_operation("Order data retrieval"):
            orders = await wms.get_entity_data("order_hdr", limit=100)
        
        # Time schema retrieval
        async with timed_operation("Schema retrieval"):
            schema = await wms.get_entity_schema("inventory")
```

---

## 🚨 **Error Handling**

### **Exception Management**

```python
from flx_http_oracle_wms.exceptions import (
    WmsConnectionError,
    WmsAuthenticationError,
    WmsApiError,
    WmsTimeoutError
)

async def robust_wms_operations():
    """WMS operations with comprehensive error handling."""
    
    config = WmsConfig.from_env()
    wms_client = WmsClient(config)
    
    try:
        await wms_client.start()
        
        # Attempt operations with error handling
        try:
            orders = await wms_client.get_entity_data("order_hdr")
            print(f"Retrieved {len(orders)} orders")
            
        except WmsAuthenticationError as e:
            print(f"Authentication failed: {e}")
            # Handle re-authentication
            
        except WmsApiError as e:
            print(f"API error: {e.message} (Code: {e.code})")
            # Handle API-specific errors
            
        except WmsTimeoutError as e:
            print(f"Operation timed out: {e}")
            # Handle timeout scenarios
            
    except WmsConnectionError as e:
        print(f"Connection failed: {e}")
        # Handle connection issues
        
    finally:
        await wms_client.stop()
```

### **Retry Logic**

```python
import asyncio
from typing import Any, Callable

async def retry_operation(
    operation: Callable[[], Any],
    max_retries: int = 3,
    delay: float = 1.0
) -> Any:
    """Retry WMS operations with exponential backoff."""
    
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except (WmsTimeoutError, WmsConnectionError) as e:
            if attempt == max_retries:
                raise e
            
            wait_time = delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

# Usage example
async def reliable_data_fetch():
    """Fetch data with retry logic."""
    
    async with WmsClient(config) as wms:
        orders = await retry_operation(
            lambda: wms.get_entity_data("order_hdr"),
            max_retries=3,
            delay=2.0
        )
        return orders
```

---

## 🔗 **Integration Patterns**

### **Service Integration Pattern**

```python
class WmsIntegrationService:
    """Service class for WMS integration."""
    
    def __init__(self, config: WmsConfig):
        self.config = config
        self._wms_client: WmsClient | None = None
    
    async def start(self) -> None:
        """Start the integration service."""
        self._wms_client = WmsClient(self.config)
        await self._wms_client.start()
    
    async def stop(self) -> None:
        """Stop the integration service."""
        if self._wms_client:
            await self._wms_client.stop()
            self._wms_client = None
    
    async def sync_orders(self) -> list[dict]:
        """Sync orders from WMS."""
        if not self._wms_client:
            raise RuntimeError("Service not started")
        
        return await self._wms_client.get_entity_data("order_hdr")
    
    async def create_order(self, order_data: dict) -> dict:
        """Create order in WMS."""
        if not self._wms_client:
            raise RuntimeError("Service not started")
        
        return await self._wms_client.create_record("order_hdr", order_data)

# Usage
async def main():
    config = WmsConfig.from_env()
    service = WmsIntegrationService(config)
    
    try:
        await service.start()
        orders = await service.sync_orders()
        print(f"Synced {len(orders)} orders")
    finally:
        await service.stop()
```

### **Data Synchronization Pattern**

```python
import asyncio
from datetime import datetime, timedelta

class WmsDataSynchronizer:
    """Synchronize data between systems using WMS client."""
    
    def __init__(self, config: WmsConfig):
        self.config = config
        self.last_sync: datetime | None = None
    
    async def incremental_sync(self) -> dict:
        """Perform incremental data synchronization."""
        
        async with WmsClient(self.config) as wms:
            # Calculate sync window
            if self.last_sync:
                since_date = self.last_sync.isoformat()
            else:
                since_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
            
            # Sync multiple entities
            sync_results = {}
            entities = ["order_hdr", "order_line", "inventory"]
            
            for entity in entities:
                try:
                    data = await wms.get_entity_data(
                        entity_name=entity,
                        filters={"modified_date__gte": since_date},
                        limit=1000
                    )
                    sync_results[entity] = len(data)
                    print(f"Synced {len(data)} {entity} records")
                    
                except Exception as e:
                    print(f"Error syncing {entity}: {e}")
                    sync_results[entity] = 0
            
            self.last_sync = datetime.utcnow()
            return sync_results

# Scheduled synchronization
async def scheduled_sync():
    """Run synchronization on schedule."""
    config = WmsConfig.from_env()
    synchronizer = WmsDataSynchronizer(config)
    
    while True:
        try:
            results = await synchronizer.incremental_sync()
            print(f"Sync completed: {results}")
        except Exception as e:
            print(f"Sync failed: {e}")
        
        # Wait 5 minutes before next sync
        await asyncio.sleep(300)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Authentication Guide](./oracle-authentication-unified-guide.md) - Required authentication setup
- [Getting Started](../../getting-started/index.md) - FLX Framework fundamentals
- [HTTP Client Configuration](../../guides/development/http-integration-patterns.md) - HTTP patterns

### **Next Steps**

- [Oracle WMS CLI Guide](./oracle-wms-cli-guide.md) - Command-line interface usage
- [Oracle Integration Mappings](./oracle-integration-mappings.md) - Data mapping patterns
- [Performance Optimization](../../optimization/performance/index.md) - Optimization strategies

### **Related Topics**

- [Oracle OIC Integration](./oracle-oic-complete-guide.md) - OIC integration patterns
- [Oracle Database Integration](./oracle-database-complete-guide.md) - Database connectivity
- [Testing Strategies](../../development/testing/integration-testing.md) - Testing WMS integrations

---

## 🆘 **Troubleshooting**

### **Common Issues**

**Authentication Failures**:

```python
# Check credentials and facility settings
config = WmsConfig(
    base_url="https://your-wms.oraclecloud.com",
    username="correct_username",
    password="correct_password", 
    facility="CORRECT_FACILITY",  # Case sensitive
    company="CORRECT_COMPANY"     # Case sensitive
)
```

**Connection Timeouts**:

```python
# Increase timeout for large operations
config = WmsConfig.from_env()
config.request_timeout = 600.0  # 10 minutes for large data sets
```

**API Endpoint Errors**:

```python
# Verify endpoint discovery
async with WmsClient(config) as wms:
    api_info = await wms.get_api_info()
    print(f"Available endpoints: {api_info}")
```

**Performance Issues**:

```python
# Use pagination for large datasets
async with WmsClient(config) as wms:
    all_orders = []
    offset = 0
    limit = 100
    
    while True:
        batch = await wms.get_entity_data(
            "order_hdr",
            limit=limit,
            offset=offset
        )
        if not batch:
            break
        
        all_orders.extend(batch)
        offset += limit
```

---

**📂 Hub**: [Oracle Integration Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
