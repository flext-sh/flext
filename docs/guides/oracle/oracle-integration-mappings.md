# Oracle Integration Mappings Reference

> **Cross-References:**
>
> - [Oracle Integration Comprehensive Guide](../guides/oracle-integration-comprehensive-guide.md) - Complete Oracle integration guide
> - [WMS Integration Guide](../guides/oracle-wms-integration.md) - WMS-specific integration patterns
> - [API Reference](../api-reference/core-api-reference.md) - FLX framework API

## Overview

This document provides reference information for Oracle Cloud WMS and Inventory Management integration mappings. The mappings define data transformation between different Oracle Cloud versions and external systems.

> **⚠️ Legacy Content**: This reference contains historical integration mappings from previous implementations. Use current FLX framework patterns for new integrations.

## Integration Architecture

### Supported Oracle Versions

- **Oracle Cloud WMS 23.1.x** - Legacy version mappings
- **Oracle Cloud WMS 23.4.x** - Stable release mappings
- **Oracle Cloud WMS 24.3.x** - Current release mappings
- **Oracle Cloud WMS 24.4.x** - Latest release mappings

### Integration Types

#### Inbound Integrations (Inventory → WMS)

1. **Order Lock/Unlock Mappings**

   - Purpose: Control order processing state in WMS
   - Versions: 23.1.0, 24.3.0
   - Format: REST API calls with JSON payload

2. **Receipt Advice Mappings**

   - **ASN (Advanced Shipping Notice)**: 23.1.0, 23.4.0
   - **Purchase Orders**: 23.1.0, 23.4.0
   - **RMA (Return Merchandise Authorization)**: 23.1.0, 23.4.0
   - **Transfer Orders**: 23.1.0, 23.4.0

3. **Shipment Request Mappings**
   - **Sales Orders**: 23.1.0, 24.3.0, 24.4.0
   - **Transfer Orders**: 23.1.0, 24.3.0, 24.4.0
   - **Update Requests**: 23.1.0, 24.3.0, 24.4.0

#### Outbound Integrations (WMS → Inventory)

1. **Backorder Mappings**

   - Purpose: Report unavailable items to Inventory Management
   - Versions: 23.1.0, 23.4.0
   - Target: Shipment line allocation

2. **Inventory Transaction Mappings**

   - Purpose: Real-time inventory updates
   - Versions: 23.1.0, 24.4.0
   - Frequency: Real-time or batch

3. **Receipt Confirmation Mappings**

   - **Purchase Orders**: 23.1.0, 24.4.0
   - **RMA Processing**: 23.1.0, 24.4.0
   - **Transfer Orders**: 23.1.0, 24.4.0
   - **Supplier ASN**: 23.1.0, 24.4.0

4. **Shipment Confirmation Mappings**
   - Purpose: Confirm completed shipments
   - Versions: 23.1.0, 23.4.0
   - Target: Sales order fulfillment

## Mapping Categories

### Current Implementation (FLX Framework)

For new integrations, use the FLX framework patterns:

```python
from flx.adapters.oracle.wms import WMSIntegrationAdapter
from flx.adapters.oracle.inventory import InventoryAdapter

class OrderLockIntegration:
    def __init__(self):
        self.wms_adapter = WMSIntegrationAdapter()
        self.inventory_adapter = InventoryAdapter()

    async def lock_order(self, order_id: str) -> bool:
        """Lock order in WMS system."""
        lock_request = {
            "order_id": order_id,
            "lock_action": "LOCK",
            "timestamp": datetime.utcnow().isoformat()
        }

        response = await self.wms_adapter.post("/orders/lock", data=lock_request)
        return response.status_code == 200
```

### Legacy Mapping Structure

#### File Naming Convention

Legacy mappings follow this pattern:

- `[source].[target].[operation]-mapping-[version].md`
- Example: `inv.wms.receipt-advice-for-ASN-mapping-23.4.0.md`

Where:

- **source**: `inv` (Inventory), `wms` (WMS)
- **target**: `wms` (WMS), `inv` (Inventory)
- **operation**: Specific integration operation
- **version**: Oracle Cloud version

#### Mapping Content Structure

Each mapping document contains:

1. **Integration Overview**

   - Business purpose and scope
   - Data flow direction
   - Frequency and timing

2. **Field Mappings**

   - Source field to target field mappings
   - Data transformations required
   - Validation rules

3. **API Specifications**

   - Endpoint URLs and methods
   - Request/response formats
   - Error handling patterns

4. **Business Rules**
   - Conditional logic
   - Default values
   - Exception handling

## Version Migration Guide

### From 23.x to 24.x

Key changes in Oracle Cloud WMS 24.x series:

1. **Enhanced Field Validation**

   - Stricter data type validation
   - Additional required fields
   - Updated field length limits

2. **API Endpoint Changes**

   - New REST endpoints for some operations
   - Deprecated SOAP endpoints
   - Enhanced authentication requirements

3. **New Integration Points**
   - Advanced inventory tracking
   - Enhanced shipment visibility
   - Improved error reporting

### Migration Strategy

1. **Assessment Phase**

   ```python
   # Check current mappings
   from flx.adapters.oracle.migration import MappingAnalyzer

   analyzer = MappingAnalyzer()
   compatibility = analyzer.check_version_compatibility(
       source_version="23.4.0",
       target_version="24.4.0"
   )
   ```

2. **Testing Phase**

   ```python
   # Test mapping compatibility
   from flx.testing.oracle import OracleIntegrationTester

   tester = OracleIntegrationTester()
   results = await tester.test_mapping_compatibility(
       mapping_file="inv.wms.receipt-advice-24.4.0.json"
   )
   ```

3. **Migration Phase**

   ```python
   # Execute migration
   from flx.adapters.oracle.migration import MappingMigrator

   migrator = MappingMigrator()
   await migrator.migrate_mappings(
       from_version="23.4.0",
       to_version="24.4.0",
       backup=True
   )
   ```

## Integration Patterns

### Modern FLX Patterns (Recommended)

#### Repository Pattern

```python
from flx.core.entities import AggregateRoot
from flx.adapters.oracle.repositories import OracleWMSRepository

class OrderAggregate(AggregateRoot):
    order_id: str
    status: str
    items: List[OrderItem]

    def lock_for_processing(self) -> None:
        if self.status == "LOCKED":
            raise ValueError("Order already locked")

        self.status = "LOCKED"
        self.add_event(DomainEvent(
            event_type="OrderLocked",
            aggregate_id=self.entity_id,
            data={"order_id": self.order_id}
        ))

class OrderRepository(OracleWMSRepository[OrderAggregate]):
    async def lock_order(self, order_id: str) -> None:
        order = await self.get_by_id(order_id)
        order.lock_for_processing()
        await self.save(order)
```

#### Event-Driven Integration

```python
from flx.core.events import DomainEvent
from flx.adapters.oracle.events import OracleEventHandler

class InventoryUpdatedHandler(OracleEventHandler):
    async def handle(self, event: DomainEvent) -> None:
        """Update WMS when inventory changes."""
        inventory_data = event.data

        await self.wms_adapter.update_inventory(
            item_id=inventory_data["item_id"],
            quantity=inventory_data["new_quantity"],
            location=inventory_data["location"]
        )
```

### Legacy Integration Patterns

#### Direct API Calls (Deprecated)

```python
# ❌ Legacy pattern - avoid for new implementations
import requests

def update_wms_inventory(item_id: str, quantity: int):
    response = requests.post(
        f"{WMS_BASE_URL}/inventory/update",
        json={"item_id": item_id, "quantity": quantity}
    )
    return response.status_code == 200
```

## Configuration Management

### Environment Configuration

```yaml
# config/oracle-integration.yaml
oracle:
  wms:
    base_url: "https://wms.oracle.cloud"
    version: "24.4.0"
    authentication:
      type: "oauth2"
      client_id: "${WMS_CLIENT_ID}"
      client_secret: "${WMS_CLIENT_SECRET}"

  inventory:
    base_url: "https://inventory.oracle.cloud"
    version: "24.4.0"
    authentication:
      type: "oauth2"
      client_id: "${INV_CLIENT_ID}"
      client_secret: "${INV_CLIENT_SECRET}"

mappings:
  version: "24.4.0"
  validation_strict: true
  retry_policy:
    max_attempts: 3
    backoff_factor: 2
```

### Mapping Configuration

```python
from flx.adapters.oracle.config import OracleMappingConfig

config = OracleMappingConfig.load_from_file("mappings/24.4.0/config.yaml")

# Access mapping rules
receipt_advice_mapping = config.get_mapping(
    source="inventory",
    target="wms",
    operation="receipt_advice"
)
```

## Best Practices

### 1. Version Management

- Always specify Oracle Cloud version in mapping names
- Maintain backward compatibility for at least one major version
- Use semantic versioning for custom mapping extensions

### 2. Error Handling

```python
from flx.adapters.oracle.exceptions import OracleIntegrationError

try:
    await wms_adapter.send_receipt_advice(data)
except OracleIntegrationError as e:
    logger.error(f"Integration failed: {e.error_code} - {e.message}")
    # Implement retry or fallback logic
    await handle_integration_failure(e)
```

### 3. Data Validation

```python
from flx.adapters.oracle.validation import OracleDataValidator

validator = OracleDataValidator(version="24.4.0")
validation_result = validator.validate_receipt_advice(data)

if not validation_result.is_valid:
    raise ValueError(f"Validation errors: {validation_result.errors}")
```

### 4. Monitoring and Logging

```python
from flx.adapters.oracle.monitoring import OracleIntegrationMonitor

monitor = OracleIntegrationMonitor()

@monitor.track_integration("wms_receipt_advice")
async def send_receipt_advice(data: dict) -> bool:
    # Integration logic here
    pass
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**

   ```bash
   # Check OAuth token validity
   curl -H "Authorization: Bearer $TOKEN" \
        https://wms.oracle.cloud/api/health
   ```

2. **Mapping Version Conflicts**

   ```python
   # Verify mapping compatibility
   from flx.adapters.oracle.diagnostics import MappingDiagnostics

   diagnostics = MappingDiagnostics()
   issues = diagnostics.check_mapping_conflicts()
   ```

3. **Data Validation Errors**

   ```python
   # Enable detailed validation logging
   import logging
   logging.getLogger('flx.adapters.oracle.validation').setLevel(logging.DEBUG)
   ```

## Migration from Legacy Mappings

To migrate from legacy mappings to FLX framework:

1. **Analyze Current Mappings**

   ```bash
   python -m flx.tools.oracle.analyze_legacy_mappings \
       --input-dir /path/to/legacy/mappings \
       --output-report mapping_analysis.json
   ```

2. **Generate FLX Adapters**

   ```bash
   python -m flx.tools.oracle.generate_adapters \
       --mapping-analysis mapping_analysis.json \
       --output-dir src/adapters/oracle/
   ```

3. **Test Migration**

   ```bash
   python -m pytest tests/integration/oracle/ \
       --mapping-version 24.4.0 \
       --legacy-comparison
   ```

## Related Documentation

### Framework Integration

- [Oracle Integration Comprehensive Guide](../guides/oracle-integration-comprehensive-guide.md) - Complete integration setup
- [API Reference](../api-reference/core-api-reference.md) - FLX framework APIs

### Specific Integration Types

- [WMS Integration Guide](../guides/oracle-wms-integration.md) - WMS-specific patterns
- [JWT Service Guide](../guides/jwt-service-guide.md) - Authentication setup

### Development

- [Testing Hexagonal Architecture](../development/TESTING_HEXAGONAL_ARCHITECTURE.md) - Testing strategies
- [Configuration Management](../development/configuration-management.md) - Configuration patterns

---

**Mapping Status**: Reference and Historical
**Recommended Approach**: Use FLX framework for new integrations
**Legacy Support**: Available for migration and reference
