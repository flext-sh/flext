# 🏢 Oracle WMS Complete Integration Guide

> **Function**: Complete Oracle WMS integration patterns and operations | **Audience**: WMS developers, integration engineers | **Status**: Production-Ready

[![Oracle WMS](https://img.shields.io/badge/Oracle-WMS-blue.svg)](./index.md)
[![Integration](https://img.shields.io/badge/integration-complete-green.svg)](./oracle-integration-comprehensive-guide.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Complete Oracle Warehouse Management System integration guide for FLX framework covering REST API integration, CLI operations, entity management, and hexagonal architecture patterns - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Section**: [Oracle](./index.md) → **📄 Current**: WMS Complete Guide

## Overview

Complete Oracle Warehouse Management System (WMS) integration guide for the FLX framework, covering REST API integration, CLI operations, entity management, and hexagonal architecture patterns.

## 🎯 Quick Navigation

- [**Getting Started**](#-getting-started) - Setup and basic operations
- [**REST API Integration**](#-rest-api-integration) - HTTP Oracle WMS client
- [**CLI Operations**](#-cli-operations) - Command-line interface
- [**Entity Reference**](#-entity-reference) - Complete API entities
- [**Advanced Operations**](#-advanced-operations) - High-performance features
- [**Architecture Integration**](#-architecture-integration) - FLX framework patterns

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Oracle WMS Cloud access
- FLX Framework installed

### Installation

```bash
# Install Oracle WMS adapter
pip install flext-http-oracle-wms

# Or install from source
cd flext-http-oracle-wms
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

### Environment Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Configure your WMS credentials:

```ini
# Oracle WMS Configuration
WMS_BASE_URL=https://your-wms-endpoint.com/services
WMS_USERNAME=your_username
WMS_PASSWORD=your_password

# Optional settings
WMS_FACILITY_ID=DC1
WMS_COMPANY_CODE=001
WMS_TIMEOUT=30
```

### Basic Connection Test

```bash
# Test connection
python -m flext_http_oracle_wms test-connection

# Show configuration
python -m flext_http_oracle_wms show-config

# Discover available operations
python -m flext_http_oracle_wms discover
```

## 🌐 REST API Integration

### FLX HTTP Oracle WMS Adapter

The `flext-http-oracle-wms` package provides a modern Python client for Oracle WMS operations with the following features:

- ✅ Pure Python implementation (no shell scripts)
- ✅ PEP8 compliant code style
- ✅ Automatic `.env` file loading
- ✅ Multiple output formats (table, json, yaml, csv)
- ✅ Async/await support
- ✅ Type hints throughout
- ✅ Comprehensive error handling

### Python API Usage

```python
from flext_http_oracle_wms import WmsService, WmsConfig

# Create service from environment
config = WmsConfig.from_env()
service = WmsService(config)

# Discover operations
operations = await service.discover_operations()

# Execute operation
result = await service.execute_operation(
    "getStockCount",
    {"warehouse": "WH01"}
)
```

### Hexagonal Architecture Integration

```python
from flext.core.entities import AggregateRoot
from flext.core.domain.value_objects import ValueObject

# Domain entity for WMS items
class WmsItem(AggregateRoot):
    item_id: str
    description: str
    quantity: int
    location: str
    status: str = "AVAILABLE"

    def allocate(self, quantity: int) -> None:
        if self.quantity < quantity:
            raise ValueError("Insufficient quantity")

        self.quantity -= quantity
        self.status = "ALLOCATED" if self.quantity == 0 else "PARTIAL"
        self.increment_version()

        # Add domain event
        self.add_event(DomainEvent(
            event_type="WmsItemAllocated",
            aggregate_id=self.entity_id,
            data={
                "item_id": self.item_id,
                "allocated_quantity": quantity,
                "remaining_quantity": self.quantity
            }
        ))

# Value object for WMS location
class WmsLocation(ValueObject):
    facility_id: str
    zone: str
    aisle: str
    shelf: str

    @property
    def full_location(self) -> str:
        return f"{self.facility_id}-{self.zone}-{self.aisle}-{self.shelf}"
```

## 🖥️ CLI Operations

### Command Structure

The WMS CLI follows a hierarchical command structure organized by action verbs:

```bash
# General pattern
python -m flext_http_oracle_wms [global_options] <command> [command_options]

# Alternative for legacy CLI
python -m src.gn_oic_wms_db.cli <category> <action> [options]
```

### Core WMS Operations

#### 1. Entity Management

**Object Inquiry**

```bash
# Query specific entities
flext-http-oracle-wms entity-query [entity] [key] [company_code] [facility_code]

# Example
flext-http-oracle-wms entity-query items ITEM001 001 DC1 --format-output table
```

**Entity Status**

```bash
# Get status information
flext-http-oracle-wms get-status [entity] [key] [company_code] [facility_code]
```

#### 2. LPN Operations

**Create LPN**

```bash
# Create License Plate Numbers
flext-http-oracle-wms create-lpn [lpn_nbr] [qty] [options...]

# Example with full parameters
flext-http-oracle-wms create-lpn LPN001 100 \
    --item-barcode ITEM001 \
    --company-code 001 \
    --facility-code DC1 \
    --batch-number BATCH001 \
    --expiry-date 2024-12-31
```

**Receive LPN**

```bash
# Receive LPNs with tracking information
flext-http-oracle-wms receive-lpn LPN001 \
    --company-code 001 \
    --facility-code DC1 \
    --rcvd-trailer-nbr TRAILER001 \
    --receiving-location DOCK01
```

#### 3. Outbound Operations

**Ship OBLPN**

```bash
# Ship outbound License Plate Numbers
flext-http-oracle-wms ship-oblpn OBLPN001 001 DC1 SHIP01 \
    --output-file-to-generate shipping_label.pdf
```

**Assign OBLPN to Load**

```bash
# Assign outbound LPNs to loads
flext-http-oracle-wms assign-oblpn-to-load LOAD001 OBLPN001 \
    --carrier-code UPS \
    --company-code 001 \
    --facility-code DC1 \
    --trailer-nbr TRAILER001
```

#### 4. Inventory Operations

**Update Active Inventory**

```bash
# Update inventory with comprehensive parameters
flext-http-oracle-wms update-inventory LOC001 ADJUST \
    --actual-qty 100 \
    --adjustment-qty 5 \
    --item-barcode ITEM001 \
    --company-code 001 \
    --facility-code DC1
```

#### 5. Sequence Management

**Get Next Numbers**

```bash
# Generate sequence numbers for various counters
flext-http-oracle-wms get-next-numbers LPN_SEQ \
    --company-code 001 \
    --facility-code DC1 \
    --count 10
```

### CLI Command Categories

#### 🔍 LIST - Discover and View

```bash
# List all available entities
python -m src.gn_oic_wms_db.cli control entities list

# List with filter
python -m src.gn_oic_wms_db.cli control entities list --filter order

# Show configuration
python -m src.gn_oic_wms_db.cli config show --detailed
```

#### 📝 REGISTER - Create and Configure

```bash
# Register single entity
python -m src.gn_oic_wms_db.cli control entities register item

# Register multiple entities
python -m src.gn_oic_wms_db.cli control entities register item order allocation

# Configure system
python -m src.gn_oic_wms_db.cli config setup --tables wms
```

#### 🔄 SYNCHRONIZE - Transfer Data

```bash
# Basic synchronization
python -m src.gn_oic_wms_db.cli sync all

# Advanced synchronization (RECOMMENDED)
python -m src.gn_oic_wms_db.cli sync enhanced --full-sync --max-workers 8

# Synchronization with comparison
python -m src.gn_oic_wms_db.cli sync enhanced --compare-totals
```

#### 📊 VERIFY - Monitor Status

```bash
# Entity status
python -m src.gn_oic_wms_db.cli control entities status --detailed

# Configuration validation
python -m src.gn_oic_wms_db.cli config validate --verbose

# Health check
python -m src.gn_oic_wms_db.cli config health
```

## 📋 Entity Reference

### API Base URLs

**Production Environment**

```
https://a29.wms.ocs.oraclecloud.com:443/raizen/wms/lgfapi/v10/entity/
```

**Test Environment**

```
https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/
```

### Core Entity Categories

#### Inventory Management

- **inventory** - Inventory operations
- **inventory_attribute** - Inventory attributes
- **inventory_history** - Inventory transaction history
- **inventory_lock** - Inventory locking operations
- **inventory_status** - Inventory status management

#### Order Management

- **order_hdr** - Order header information
- **order_dtl** - Order detail information
- **order_status** - Order status tracking
- **order_type** - Order type configuration
- **order_lock** - Order locking operations

#### Item Management

- **item** - Item master data
- **item_barcode** - Item barcode management
- **item_characteristics** - Item characteristics
- **item_facility** - Item facility configuration
- **item_metrics** - Item performance metrics

#### Warehouse Operations

- **location** - Location management
- **location_type** - Location type configuration
- **task** - Task management
- **task_status** - Task status tracking
- **wave** - Wave planning and execution

#### Shipment Operations

- **ib_shipment** - Inbound shipment management
- **ib_shipment_dtl** - Inbound shipment details
- **ib_shipment_status** - Inbound shipment status
- **ib_shipment_type** - Inbound shipment types

### Entity Usage Examples

```bash
# Get entity information
GET https://a29.wms.ocs.oraclecloud.com:443/raizen/wms/lgfapi/v10/entity/inventory

# Filter entity data
GET https://a29.wms.ocs.oraclecloud.com:443/raizen/wms/lgfapi/v10/entity/inventory?facility=DC1
```

## 🚀 Advanced Operations

### High-Speed Data Extraction

Extract large datasets efficiently using paged queries:

```bash
# High-speed extraction to JSON
flext-http-oracle-wms extract items items_data.json 001 DC1 \
    --high-speed --page-size 5000 --format-export json

# Extract to CSV with limit
flext-http-oracle-wms extract orders orders.csv 001 DC1 \
    --format-export csv --max-records 10000

# Extract to Parquet for big data
flext-http-oracle-wms extract transactions data.parquet 001 DC1 \
    --format-export parquet --high-speed
```

### Bulk Operations

Process multiple operations from JSON files:

```bash
# Bulk operations with JSON file
flext-http-oracle-wms bulk-operations bulk_lpn_create.json create_lpn \
    --batch-size 50 --continue-on-error
```

**Example JSON structure:**

```json
[
  {
    "lpn_nbr": "LPN001",
    "qty": 100,
    "item_barcode": "ITEM001",
    "company_code": "001",
    "facility_code": "DC1"
  },
  {
    "lpn_nbr": "LPN002",
    "qty": 200,
    "item_barcode": "ITEM002",
    "company_code": "001",
    "facility_code": "DC1"
  }
]
```

### Schema Management

```bash
# Get and validate schema
flext-http-oracle-wms get-schema items --save-schema --validate

# This creates: schemas/entities/items.json
```

### Output Formats

The CLI supports multiple output formats:

- **Table Format** (Default): Rich formatted tables with colors
- **JSON Format**: Structured JSON output
- **YAML Format**: Human-readable YAML
- **CSV Format**: Comma-separated values

```bash
# Different output formats
flext-http-oracle-wms --format-output table entity-query items ITEM001
flext-http-oracle-wms --format-output json entity-query items ITEM001
flext-http-oracle-wms --format-output yaml entity-query items ITEM001
flext-http-oracle-wms --format-output csv entity-query items ITEM001
```

## 🏗️ Architecture Integration

### Event-Driven Integration

```python
from flext.core.events import DomainEvent
from flext.application.services import ApplicationService

class OracleWmsIntegrationService(ApplicationService):
    def __init__(self, wms_client, db_repository):
        self.wms = wms_client
        self.db = db_repository

    async def handle_inventory_update(self, event: DomainEvent):
        """Handle inventory update across Oracle systems."""

        if event.event_type == "InventoryAdjusted":
            # 1. Update WMS
            await self.wms.update_inventory(
                item_id=event.data["item_id"],
                adjustment=event.data["adjustment"]
            )

            # 2. Record in database
            await self.db.save_inventory_transaction(
                event.data
            )
```

### Repository Pattern with Oracle

```python
from flext.infrastructure.database import DatabaseAdapter
from flext.adapters.outbound.database import OracleAdapter

class OracleWmsRepository:
    def __init__(self, db_adapter: DatabaseAdapter):
        self.db = db_adapter

    async def save_wms_transaction(self, transaction: WmsTransaction) -> None:
        """Save WMS transaction to Oracle database."""

        query = """
        INSERT INTO wms_transactions (
            transaction_id, item_id, quantity,
            transaction_type, created_at
        ) VALUES (
            :transaction_id, :item_id, :quantity,
            :transaction_type, :created_at
        )
        """

        await self.db.execute(query, {
            "transaction_id": transaction.transaction_id,
            "item_id": transaction.item_id,
            "quantity": transaction.quantity,
            "transaction_type": transaction.transaction_type,
            "created_at": transaction.created_at
        })
```

## 🔧 Recommended Workflows

### 1. Complete Initial Setup

```bash
# 1. Validate configuration
python -m src.gn_oic_wms_db.cli config validate --verbose

# 2. Configure tables
python -m src.gn_oic_wms_db.cli config setup

# 3. List available entities
python -m src.gn_oic_wms_db.cli control entities list

# 4. Register main entities
python -m src.gn_oic_wms_db.cli control entities register item order allocation order_dtl

# 5. Check status
python -m src.gn_oic_wms_db.cli control entities status --detailed
```

### 2. Daily Synchronization

```bash
# Incremental synchronization with threading
python -m src.gn_oic_wms_db.cli sync enhanced --compare-totals

# Check results
python -m src.gn_oic_wms_db.cli control status --detailed
```

### 3. Data Pipeline Integration

```bash
#!/bin/bash
# Extract all entity data for backup

entities=("items" "orders" "locations" "inventory")
for entity in "${entities[@]}"; do
    echo "Extracting ${entity}..."
    flext-http-oracle-wms extract "$entity" "backup/${entity}.parquet" 001 DC1 \
        --format-export parquet --high-speed
done
```

## 🚨 Error Handling

### Connection Errors

```bash
❌ Connection failed: Unable to connect to host your-wms-host.com
```

### Authentication Errors

```bash
❌ Discovery failed: Authentication failed - invalid credentials
```

### Validation Errors

```bash
❌ Schema missing fields: ['properties', 'type']
```

### API Errors

```bash
❌ Failed to create LPN: Invalid item barcode
```

## 🔍 Troubleshooting

### Debug Mode

```bash
# Enable detailed logging
flext-http-oracle-wms --debug --verbose test-connection
```

### Configuration Validation

```bash
# Test configuration and connection
flext-http-oracle-wms show-config --validate-connection
```

### Schema Issues

```bash
# Validate entity schemas
flext-http-oracle-wms get-schema [entity] --validate
```

## 📊 Performance Optimization

### High-Speed Extraction

- Use `--high-speed` for paged extraction
- Adjust `--page-size` based on memory and network
- Use Parquet format for large datasets

### Bulk Operations

- Process operations in batches
- Use `--continue-on-error` for resilient processing
- Monitor progress with verbose output

### Caching

- Schema validation caches schemas locally
- Use saved schemas for faster validation

## 🎓 Integration Examples

### Modern FLX 0.4.0+ Usage

```python
from flext.adapters.oracle.wms import WMSAdapter
from flext.core.application import Application

# Create application with WMS adapter
app = Application()

# Configure WMS adapter
wms_adapter = WMSAdapter(
    base_url=os.getenv("WMS_BASE_URL"),
    username=os.getenv("WMS_USERNAME"),
    password=os.getenv("WMS_PASSWORD")
)

# Register adapter
app.register_adapter("wms", wms_adapter)

# Use in domain services
async def process_inventory_adjustment(item_id: str, adjustment: int):
    wms = app.get_adapter("wms")

    # Update WMS inventory
    result = await wms.update_inventory(
        item_id=item_id,
        adjustment=adjustment
    )

    return result
```

## 📖 Related Documentation

- [Oracle Integration Hub](README.md) - Main Oracle documentation hub
- [Oracle OIC Integration](oic-complete-guide.md) - Oracle Integration Cloud
- [Oracle Database Integration](database-complete-guide.md) - Database connections
- [Oracle Authentication](authentication-complete-guide.md) - OAuth2 and JWT setup
- [FLX Architecture](../../architecture/infrastructure-architecture.md) - Framework architecture
- [Testing Oracle Integrations](../../development/testing/oracle-testing.md) - Testing strategies

## 🆘 Support

For additional support:

1. Use `--help` for command-specific help
2. Enable `--debug --verbose` for detailed logging
3. Validate configuration with `show-config --validate-connection`
4. Check schema validation for entity issues

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Oracle Integration Foundation**](./oracle-integration-comprehensive-guide.md) - Oracle integration architecture and authentication setup required for WMS implementation
- [**FLX Framework Installation**](../../getting-started/setup/installation-guide.md) - Framework setup and basic configuration required for WMS adapter installation
- [**Authentication Configuration**](./authentication-complete-guide.md) - OAuth2 and JWT setup essential for Oracle WMS Cloud access

### **➡️ Implementation Next Steps**

- [**Oracle Database Integration**](./database-complete-guide.md) - Database operations and transaction management complementing WMS workflows
- [**Oracle OIC Integration**](./oic-complete-guide.md) - Integration Cloud patterns for WMS orchestration and automation
- [**Production Deployment**](../../deployment/kubernetes-deployment.md) - Deploying WMS integrations in production environments

### **🔗 Related Implementation Topics**

- [**WMS Testing Strategies**](../../development/testing/hexagonal-testing-guide.md) - Testing frameworks and validation patterns for WMS operations and integration flows
- [**Infrastructure Service Patterns**](../../infrastructure/service-patterns.md) - Infrastructure services supporting WMS integration in production environments
- [**API Reference for WMS**](../../api-reference/core-api-reference.md) - Complete API documentation for WMS adapter classes and operation methods
- [**Real-World WMS Examples**](../../examples/oracle-integration-real-examples.md) - Production WMS integration examples with complete implementation patterns
- [**Security Implementation**](../../security/architecture/security-architecture.md) - Enterprise security patterns for WMS authentication and data protection
- [**Performance Optimization**](../../optimization/performance/optimization-guide.md) - WMS performance tuning, connection optimization, and batch processing strategies

---

**📂 Content Document** | **🏠 Parent**: [Oracle Guides Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

**Implementation Status**: ✅ **Production Ready**
**Documentation**: Complete WMS integration guide

_This comprehensive guide consolidates all Oracle WMS integration documentation for the FLX framework, providing complete implementation instructions, examples, and best practices._
