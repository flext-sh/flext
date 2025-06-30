# Legacy Integrations Reference Guide

## Overview

This document provides guidance for understanding and working with legacy integration examples, historical artifacts, and migration patterns from previous Oracle WMS integration projects.

## Related Documentation

- [Oracle Integration Guide](../integrations/oracle/) - Current Oracle integration patterns
- [Migration Strategies](../migration/) - Legacy to modern migration approaches
- [Reference Materials Overview](./index.md) - Complete reference index
- [Integration Patterns](../architecture/integration-patterns.md) - Modern integration architectures

## Legacy Integration Structure

The legacy integrations reference contains historical examples, mappings, packages, and documentation from previous integration versions:

### Integration Mappings (23D to 24D)

Examples of Oracle Inventory and WMS integration mappings between different system versions:

#### Inventory to WMS Mappings

- **Order Lock/Unlock Mappings (24.3.0)** - Order management integration patterns
- **Receipt Advice for ASN (23.4.0)** - Advanced Shipping Notice receipt processing
- **Receipt Advice for Purchase Orders and RMA (23.4.0)** - Purchase order and return merchandise authorization receipts
- **Receipt Advice for RMA as Inbound Shipment (23.4.0)** - Return processing patterns
- **Receipt Advice for Transfer Orders (23.4.0)** - Transfer order receipt handling
- **Shipment Request for Sales and Transfer Orders (24.3.0/24.4.0)** - Outbound shipment processing
- **Update Shipment Request (24.3.0/24.4.0)** - Shipment modification patterns

#### WMS to Inventory Mappings

- **Backorder to Shipment Line (23.4.0)** - Backorder processing integration
- **Inventory Transactions (24.4.0)** - Inventory movement tracking
- **Receipt Confirmation (24.4.0)** - Receipt confirmation processing for PO/RMA/TO/Supplier ASN
- **Shipment Confirmation for Sales Orders (23.4.0)** - Outbound confirmation patterns

## Usage Guidelines

### 1. Reference Purpose Only

These legacy integrations serve as:

- **Historical Reference** - Understanding previous implementation approaches
- **Migration Guidance** - Identifying patterns that need modernization
- **Comparison Base** - Evaluating improvements in current implementations
- **Knowledge Preservation** - Maintaining institutional knowledge

### 2. Migration Considerations

When working with legacy integrations:

#### ✅ **What to Extract**

- Business logic patterns and rules
- Data mapping requirements
- Integration flow concepts
- Error handling approaches

#### ❌ **What to Avoid**

- Direct copying of old code patterns
- Using outdated API versions
- Implementing deprecated integration methods
- Bypassing modern security requirements

### 3. Modernization Approach

#### Legacy Pattern Analysis

```yaml
# Example legacy pattern analysis
legacy_pattern:
  source: "inv.wms.receipt-advice-for-ASN-mapping-23.4.0"
  business_logic: "ASN receipt processing with inventory updates"
  modern_equivalent: "flext-http-oracle-wms receipt adapter with event sourcing"
  migration_complexity: "medium"
  modernization_notes:
    - "Replace direct API calls with adapter pattern"
    - "Add comprehensive error handling"
    - "Implement event-driven architecture"
    - "Add monitoring and observability"
```

#### Modern Implementation

```python
# Modern FLEXT implementation of legacy pattern
from flext.adapters.outbound.oracle import OracleWmsAdapter
from flext.core.events import DomainEvent
from flext.ports.inbound.receipt import ReceiptPort

class ModernReceiptProcessor(ReceiptPort):
    """Modern implementation of legacy ASN receipt processing."""

    def __init__(self, wms_adapter: OracleWmsAdapter):
        self.wms_adapter = wms_adapter

    async def process_asn_receipt(self, asn_data: dict) -> ReceiptConfirmation:
        """Process ASN receipt with modern patterns."""
        try:
            # Validate using domain rules
            receipt = self._validate_receipt_data(asn_data)

            # Process through adapter
            confirmation = await self.wms_adapter.confirm_receipt(receipt)

            # Emit domain event
            await self._emit_receipt_event(receipt, confirmation)

            return confirmation

        except Exception as e:
            # Modern error handling
            await self._handle_receipt_error(asn_data, e)
            raise
```

## Legacy Integration Categories

### 1. Order Management Integrations

Historical patterns for order processing, modifications, and lifecycle management:

- **Order Lock/Unlock** - Order reservation and release patterns
- **Order Updates** - Order modification and amendment flows
- **Order Status Tracking** - Status synchronization between systems

### 2. Receipt Processing Integrations

Legacy patterns for inbound processing and receipt confirmation:

- **ASN Receipt Processing** - Advanced shipping notice handling
- **Purchase Order Receipts** - Procurement receipt workflows
- **Return Merchandise Authorization** - Return processing patterns
- **Transfer Order Receipts** - Inter-location transfer handling

### 3. Shipment Processing Integrations

Historical outbound processing and shipment management:

- **Sales Order Shipments** - Customer order fulfillment
- **Transfer Order Shipments** - Inter-location transfers
- **Shipment Confirmations** - Outbound confirmation workflows
- **Backorder Management** - Partial shipment handling

### 4. Inventory Synchronization

Legacy patterns for inventory data synchronization:

- **Inventory Transactions** - Movement tracking and recording
- **Stock Level Updates** - Real-time inventory synchronization
- **Adjustment Processing** - Inventory correction workflows

## Migration Strategy

### Phase 1: Analysis and Planning

1. **Pattern Identification** - Catalog existing integration patterns
2. **Business Rule Extraction** - Document core business logic
3. **Data Flow Mapping** - Understand data transformation requirements
4. **Dependency Analysis** - Identify system dependencies and constraints

### Phase 2: Modern Architecture Design

1. **Hexagonal Architecture Application** - Design ports and adapters
2. **Event-Driven Patterns** - Implement asynchronous processing
3. **Error Handling Strategy** - Comprehensive error management
4. **Monitoring and Observability** - Add health checks and metrics

### Phase 3: Incremental Migration

1. **Adapter Implementation** - Build modern adapters for legacy systems
2. **Parallel Processing** - Run legacy and modern systems in parallel
3. **Data Validation** - Ensure consistency between old and new systems
4. **Gradual Cutover** - Phase out legacy integrations

### Phase 4: Optimization and Enhancement

1. **Performance Tuning** - Optimize modern implementations
2. **Feature Enhancement** - Add capabilities not present in legacy systems
3. **Documentation Update** - Document new patterns and approaches
4. **Team Training** - Ensure team understands modern patterns

## Best Practices for Legacy Reference

### Documentation and Analysis

```markdown
# Legacy Integration Analysis Template

## Integration Overview

- **Legacy System**: Oracle WMS 23.4.0
- **Integration Type**: Receipt Advice for ASN
- **Business Purpose**: Process advanced shipping notices
- **Data Volume**: ~1000 transactions/day

## Business Logic Analysis

- **Core Rules**: [Document key business rules]
- **Data Transformations**: [Map data conversions]
- **Error Scenarios**: [Catalog error conditions]
- **Performance Requirements**: [Note timing constraints]

## Modernization Plan

- **Target Architecture**: FLEXT Hexagonal with Oracle adapters
- **Implementation Approach**: Event-driven with async processing
- **Migration Complexity**: Medium (requires data mapping updates)
- **Risk Assessment**: Low (well-understood business logic)
```

### Code Pattern Extraction

```python
# Template for extracting patterns from legacy code
class LegacyPatternExtractor:
    """Extract and document patterns from legacy integrations."""

    def analyze_integration(self, legacy_file_path: str) -> IntegrationAnalysis:
        """Analyze legacy integration for modernization."""
        return IntegrationAnalysis(
            business_logic=self._extract_business_rules(legacy_file_path),
            data_mappings=self._extract_data_mappings(legacy_file_path),
            error_handling=self._analyze_error_patterns(legacy_file_path),
            performance_characteristics=self._assess_performance(legacy_file_path)
        )

    def generate_modern_implementation(self, analysis: IntegrationAnalysis) -> str:
        """Generate modern FLEXT implementation based on analysis."""
        return self._template_generator.create_flext_adapter(
            business_logic=analysis.business_logic,
            port_interfaces=self._design_ports(analysis),
            adapter_implementation=self._design_adapters(analysis)
        )
```

## Common Legacy Patterns and Modern Equivalents

### Legacy Direct API Calls

```xml
<!-- Legacy SOAP/XML pattern -->
<soap:Envelope>
    <soap:Body>
        <ReceiptAdvice>
            <ASNNumber>ASN-001</ASNNumber>
            <Items>
                <Item>
                    <SKU>ITEM-001</SKU>
                    <Quantity>100</Quantity>
                </Item>
            </Items>
        </ReceiptAdvice>
    </soap:Body>
</soap:Envelope>
```

```python
# Modern FLEXT pattern
from flext.core.domain.value_objects import ASNNumber, SKU, Quantity
from flext.core.entities import ReceiptAdvice, ReceiptItem

# Type-safe value objects
asn_number = ASNNumber("ASN-001")
items = [ReceiptItem(sku=SKU("ITEM-001"), quantity=Quantity(100))]

# Domain entity
receipt_advice = ReceiptAdvice(asn_number=asn_number, items=items)

# Modern adapter call
confirmation = await oracle_adapter.process_receipt_advice(receipt_advice)
```

### Legacy Error Handling

```java
// Legacy try-catch pattern
try {
    processReceipt(receiptData);
} catch (Exception e) {
    log.error("Receipt processing failed: " + e.getMessage());
    // Often missing proper error recovery
}
```

```python
# Modern comprehensive error handling
from flext.core.exceptions import ReceiptProcessingError, ValidationError
from flext.infra.observability import MetricsCollector

async def process_receipt(self, receipt_data: dict) -> ReceiptConfirmation:
    """Process receipt with comprehensive error handling."""
    try:
        # Validate input
        receipt = self._validate_receipt(receipt_data)

        # Process through adapter
        confirmation = await self.adapter.process_receipt(receipt)

        # Record success metrics
        self.metrics.increment("receipts_processed_success")

        return confirmation

    except ValidationError as e:
        # Handle validation errors
        self.logger.warning("Receipt validation failed: %s", str(e))
        self.metrics.increment("receipts_validation_errors")
        raise ReceiptProcessingError(f"Invalid receipt data: {str(e)}") from e

    except OracleApiError as e:
        # Handle Oracle API errors
        self.logger.error("Oracle API error: %s", str(e))
        self.metrics.increment("oracle_api_errors")

        # Implement retry logic
        if e.is_retryable():
            await self._schedule_retry(receipt_data)

        raise ReceiptProcessingError(f"Oracle API failure: {str(e)}") from e

    except Exception as e:
        # Handle unexpected errors
        self.logger.exception("Unexpected error processing receipt")
        self.metrics.increment("receipts_unexpected_errors")
        raise
```

## Governance and Maintenance

### Reference Material Management

- **Clear Labeling** - All legacy materials clearly marked with versions and dates
- **Migration Status** - Track which patterns have been modernized
- **Relevance Assessment** - Regular review of continued relevance
- **Access Control** - Appropriate access restrictions for historical materials

### Knowledge Transfer

- **Documentation Standards** - Consistent documentation of legacy patterns
- **Training Materials** - Educational content for understanding legacy patterns
- **Expert Consultation** - Access to team members familiar with legacy systems
- **Best Practices** - Guidelines for working with legacy references

## See Also

- [Oracle WMS Integration Guide](../integrations/oracle/wms-integration.md) - Modern Oracle WMS integration
- [Migration Planning Guide](../migration/planning-guide.md) - Systematic migration approaches
- [Integration Testing](../development/integration-testing.md) - Testing legacy and modern integrations
- [Architecture Decision Records](../architecture/decisions/) - Design decisions for modernization

---

**Last Updated**: January 2025
**Status**: Reference Material
**Purpose**: Legacy Analysis and Migration Planning
**Scope**: Oracle WMS Integration Patterns
