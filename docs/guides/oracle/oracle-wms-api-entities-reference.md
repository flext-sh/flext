# Oracle WMS API Entities Reference

**Date**: January 2025
**Status**: Complete Entity Reference
**Version**: v10

## Overview

This document provides a complete reference of Oracle WMS LogFire API entities. These are the available API endpoints for production and test environments.

## API Base URLs

### Production Environment

```
https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/
```

### Test Environment

```
https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/
```

## Available Entities

The following entities are available through the WMS LogFire API v10:

### Core Operations

- **action_code** - Action codes for operations
- **active_location** - Active location management
- **allocation** - Inventory allocation operations
- **appointment** - Dock appointment management
- **asset** - Asset tracking and management

### Inventory Management

- **inventory** - Inventory operations
- **inventory_attribute** - Inventory attributes
- **inventory_history** - Inventory transaction history
- **inventory_lock** - Inventory locking operations
- **inventory_status** - Inventory status management

### Order Management

- **order_hdr** - Order header information
- **order_dtl** - Order detail information
- **order_status** - Order status tracking
- **order_type** - Order type configuration
- **order_lock** - Order locking operations

### Shipment Operations

- **ib_shipment** - Inbound shipment management
- **ib_shipment_dtl** - Inbound shipment details
- **ib_shipment_status** - Inbound shipment status
- **ib_shipment_type** - Inbound shipment types

### Item Management

- **item** - Item master data
- **item_barcode** - Item barcode management
- **item_characteristics** - Item characteristics
- **item_facility** - Item facility configuration
- **item_metrics** - Item performance metrics

### Warehouse Operations

- **location** - Location management
- **location_type** - Location type configuration
- **task** - Task management
- **task_status** - Task status tracking
- **wave** - Wave planning and execution

### Complete Entity List

Below is the complete list of all available entities:

```json
{
  "action_code": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/action_code",
  "active_location": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/active_location",
  "aiml_model_training_hdr": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/aiml_model_training_hdr",
  "aiml_order_cycle_time": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/aiml_order_cycle_time",
  "aiml_prediction_order_cycle_time": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/aiml_prediction_order_cycle_time",
  "aiml_prediction_run": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/aiml_prediction_run",
  "allocation": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/allocation",
  "allocation_distribution_mode": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/allocation_distribution_mode",
  "allocation_status": "https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/allocation_status"
}
```

_Note: The complete entity list contains over 200 entities. For the full list, please refer to the production API discovery endpoint._

## Usage Examples

### Get Entity Information

```bash
GET https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/inventory
```

### Filter Entity Data

```bash
GET https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/inventory?facility=DC1
```

## Authentication

All API calls require proper authentication. Refer to the Oracle WMS REST API Authentication Guide for details on:

- OAuth token management
- API key configuration
- Security headers

## Related Documentation

- [Oracle WMS REST API Guide](oracle-wms-rest-api-guide.md)
- [Oracle WMS Integration Patterns](oracle-wms-integration-guide.md)
- [Oracle WMS Authentication Setup](oracle-sso-authentication-setup.md)

## Entity Categories

### AI/ML Entities

- aiml_model_training_hdr
- aiml_order_cycle_time
- aiml_prediction_order_cycle_time
- aiml_prediction_run

### Inventory Entities

- inventory
- inventory_attribute
- inventory_history
- inventory_lock
- inventory_status

### Order Processing

- order_hdr
- order_dtl
- order_status
- order_type
- order_lock
- order_instruction

### Shipping & Receiving

- ib_shipment
- ib_shipment_dtl
- ib_shipment_status
- ob_stop
- ob_stop_dtl

### Task Management

- task
- task_dtl
- task_status
- task_activity

### Wave Management

- wave
- wave_status
- wave_stage
- wave_template

### Location Management

- location
- location_type
- location_size_type
- active_location

This reference provides the foundation for integrating with Oracle WMS through the LogFire API v10.
