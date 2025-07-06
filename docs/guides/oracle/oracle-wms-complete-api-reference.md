# Oracle WMS Complete API Reference - Oracle Integration

> **Function**: Complete Oracle WMS API reference and implementation guide | **Audience**: Integration developers, API consumers | **Status**: Current

[![Oracle WMS](https://img.shields.io/badge/oracle-wms-red.svg)](./index.md)
[![API](https://img.shields.io/badge/reference-api-blue.svg)](../../api-reference/index.md)
[![Integration](https://img.shields.io/badge/integration-complete-green.svg)](./oracle-integration-hub.md)

**Comprehensive API reference for Oracle Warehouse Management System (WMS) with complete entity documentation, authentication patterns, and integration examples**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: WMS API Reference

### **📍 Learning Path Position**

```
[Oracle Integration Hub](./oracle-integration-hub.md) → **[WMS API REFERENCE]** → [WMS Operations Guide](./oracle-wms-operations-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Oracle Integration Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related API**: [API Reference Hub](../../api-reference/index.md)
- **🔗 Authentication**: [OAuth2 Guide](./oracle-oauth2-authentication-guide.md)

---

## 📋 Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Integration Categories](#integration-categories)
3. [OAuth 2.0 Authentication](#oauth-20-authentication)
4. [REST API Specifications](#rest-api-specifications)
5. [Complete Entity Reference](#complete-entity-reference)
6. [API Examples & Usage](#api-examples--usage)
7. [Data Extraction](#data-extraction)
8. [Error Handling](#error-handling)
9. [Integration Architecture](#integration-architecture)

---

## 🏗️ Overview & Architecture

### System Integration Overview

Oracle Warehouse Management Cloud (Release 25B) provides comprehensive integration capabilities for external systems, automated operations, and data exchange. This consolidated reference combines all API documentation into a single authoritative source.

### Hexagonal Architecture Integration

```
FLEXT Hexagonal Architecture - Actual Implementation
├── Domain Layer (WMS-agnostic)
│   ├── Entities (Items, Orders, Shipments, Inventory)
│   ├── Value Objects (WMS IDs, Status codes, Quantities)
│   └── Domain Events (Transaction events, Status changes)
├── Application Layer
│   ├── WMS Application Services
│   ├── Order Management Services
│   └── Inventory Management Services
├── Ports (Interfaces)
│   ├── Inbound: WMS REST APIs, SFTP interfaces
│   └── Outbound: WMS client adapters
└── Adapters (Infrastructure)
    ├── WmsClient (flext_http_oracle_wms.wms_client)
    ├── WmsConfig (flext_http_oracle_wms.config)
    └── HttpClientService (flext.infra.http.client_service)
```

**⚠️ Implementation Note**: The actual implementation uses `WmsClient` class from `/flext_http_oracle_wms/src/flext_http_oracle_wms/wms_client.py`, not the previously documented adapter names.

### Communication Protocols

The system supports multiple communication methods:

- **REST Web Services over HTTPS**: Primary integration method for real-time operations
- **Secure FTP (SFTP)**: File-based data exchange using external SFTP sites
- **SOAP APIs**: Specialized support for parcel carrier integrations

### Supported Data Formats

- **XML**: Structured data with XSD schema definitions
- **Delimited flat files**: Pipe-delimited and CSV formats
- **JSON**: For modern REST API implementations

### Production URLs

#### Production Environment

```
Base URL: https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/
Entity API: https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/
```

#### Test Environment

```
Base URL: https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/
Entity API: https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/
```

---

## 🔧 Integration Categories

### 1. Automation and Operations

#### MHE (Material Handling Equipment) Integration

- **Conveyor Systems**: Automated sorting and routing
- **RFID Integration**: Real-time tracking and location services
- **Voice Technology**: Hands-free warehouse operations
- **Task Automation**: External triggering of WMS operations

#### Integration Capabilities

- Standard Oracle WMS Cloud APIs for all MHE operations
- Real-time communication via REST web services
- Automated task creation and execution
- Route instruction generation

### 2. Parcel Carrier Integration

#### Supported Carriers

- **FedEx**: Direct web service integration
- **UPS**: Native web service support
- **ConnectShip**: Multi-carrier gateway for UPS, DHL GlobalMail

#### Integration Requirements

- Carrier account and credentials
- Oracle WMS Cloud configuration
- Label generation and tracking capabilities
- Rate calculation and service selection

### 3. Setup and Transactional Data

#### Master Data Integration

- **Items**: SKU definitions, barcodes, facility-specific properties
- **Locations**: Warehouse layout and storage definitions
- **Vendors**: Supplier information and business rules
- **Companies**: Customer and shipping destinations

#### Transactional Data

- **Purchase Orders**: Inbound planning and receiving
- **Orders**: Outbound fulfillment requests
- **Shipments**: Inbound and outbound logistics
- **Inventory**: Real-time stock movements and adjustments

#### Data Integration Methods

1. **Excel/Flat File Upload**: Via Input Interface screens
2. **REST Web Services**: Real-time XML payload processing
3. **SFTP File Transfer**: Batch processing from external sites

---

## 🔐 OAuth 2.0 Authentication

### Authentication Overview

Oracle WMS Cloud supports OAuth 2.0 Client Credentials flow for secure API access. This is the recommended authentication method for production integrations.

### Required Environment Variables

```bash
# IDCS Configuration
IDCS_URL=idcs-xxxx.identity.oraclecloud.com
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Resource Audiences (Critical - Format is important!)
RESOURCE_AUD=https://XXXX.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
API_AUD=https://XXXX.integration.ocp.oraclecloud.com:443/ic/api/

# WMS Instance URL
WMS_URL=https://ta29.wms.ocs.oraclecloud.com
```

### Authentication Implementation

```python
import requests
from base64 import b64encode

class WMSAuthenticator:
    def __init__(self, idcs_url: str, client_id: str, client_secret: str):
        self.idcs_url = idcs_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def get_access_token(self) -> str:
        \"\"\"Obtain OAuth2 access token using client credentials.\"\"\"

        # Prepare credentials
        credentials = f\"{self.client_id}:{self.client_secret}\"
        encoded_credentials = b64encode(credentials.encode()).decode()

        # Token request
        token_url = f\"https://{self.idcs_url}/oauth2/v1/token\"
        headers = {
            \"Authorization\": f\"Basic {encoded_credentials}\",
            \"Content-Type\": \"application/x-www-form-urlencoded\"
        }
        data = {
            \"grant_type\": \"client_credentials\",
            \"scope\": \"urn:opc:resource:consumer::all\"
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data[\"access_token\"]
        return self.access_token

    def get_auth_headers(self) -> dict:
        \"\"\"Get authorization headers for API requests.\"\"\"
        if not self.access_token:
            self.get_access_token()

        return {
            \"Authorization\": f\"Bearer {self.access_token}\",
            \"Content-Type\": \"application/json\"
        }
```

---

## 🌐 REST API Specifications

### HTTP Methods and Usage

#### RESTful Principles

- **GET**: Retrieve resources and collections
- **POST**: Create new resources
- **PATCH**: Update existing resources
- **DELETE**: Remove resources
- **HEAD**: Check resource existence

#### Data Input Methodology

**Supported Input Formats:**

- **JSON**: Primary format for modern integrations
- **XML**: Legacy support and carrier integrations
- **Form data**: Simple key-value pairs

**Encoding and Timezone:**

- **Character Encoding**: UTF-8
- **Timezone**: UTC (recommended) or local timezone with offset
- **Date Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)

### API Versioning and URLs

#### URL Structure

```
https://{host}/{tenant}/wms/lgfapi/v{version}/{module}/{resource}
```

#### Example URLs

```
# Entity operations
GET    /raizen_test/wms/lgfapi/v10/entity/order_hdr
POST   /raizen_test/wms/lgfapi/v10/entity/order_hdr
PATCH  /raizen_test/wms/lgfapi/v10/entity/order_hdr/{id}

# Data extraction
GET    /raizen_test/wms/lgfapi/v10/data_extract/inventory
POST   /raizen_test/wms/lgfapi/v10/data_extract/inventory/export
```

### Pagination and Filtering

#### Pagination Parameters

- **limit**: Number of records per page (default: 100, max: 1000)
- **offset**: Starting record number
- **page**: Page number (alternative to offset)

#### Filtering Options

```
# Basic filtering
GET /entity/inventory?item_id=ABC123

# Advanced filtering with operators
GET /entity/inventory?quantity__gt=100
GET /entity/inventory?last_updated__gte=2025-01-01

# Multiple conditions
GET /entity/inventory?item_id__in=ABC123,DEF456&facility_id=WH01
```

#### Available Filter Operators

- **\_\_gt**: Greater than
- **\_\_gte**: Greater than or equal
- **\_\_lt**: Less than
- **\_\_lte**: Less than or equal
- **\_\_in**: In list of values
- **\_\_contains**: String contains
- **\_\_icontains**: Case-insensitive contains
- **\_\_startswith**: String starts with
- **\_\_endswith**: String ends with

### Field Selection and Sorting

#### Field Selection

```
# Select specific fields
GET /entity/order_hdr?fields=order_id,order_status,created_date

# Exclude fields
GET /entity/order_hdr?exclude=detailed_description,comments
```

#### Sorting

```
# Single field sorting
GET /entity/order_hdr?ordering=created_date

# Multiple field sorting
GET /entity/order_hdr?ordering=priority,-created_date

# Descending order (prefix with -)
GET /entity/order_hdr?ordering=-last_updated
```

---

## 📊 Complete Entity Reference

### Core Operations Entities

#### Action Code

- **Endpoint**: `/entity/action_code`
- **Purpose**: Action codes for warehouse operations
- **Key Fields**: `action_code`, `description`, `module`

#### Active Location

- **Endpoint**: `/entity/active_location`
- **Purpose**: Track active warehouse locations
- **Key Fields**: `location_id`, `facility_id`, `active_flag`

#### Allocation

- **Endpoint**: `/entity/allocation`
- **Purpose**: Inventory allocation operations
- **Key Fields**: `allocation_id`, `order_id`, `item_id`, `quantity`

### Inventory Management Entities

#### Inventory

- **Endpoint**: `/entity/inventory`
- **Purpose**: Core inventory tracking
- **Key Fields**: `inventory_id`, `item_id`, `location_id`, `quantity`, `available_quantity`

#### Inventory Attribute

- **Endpoint**: `/entity/inventory_attribute`
- **Purpose**: Additional inventory attributes
- **Key Fields**: `inventory_id`, `attribute_name`, `attribute_value`

#### Inventory History

- **Endpoint**: `/entity/inventory_history`
- **Purpose**: Inventory transaction history
- **Key Fields**: `transaction_id`, `inventory_id`, `transaction_type`, `quantity_change`

#### Inventory Lock

- **Endpoint**: `/entity/inventory_lock`
- **Purpose**: Inventory locking operations
- **Key Fields**: `lock_id`, `inventory_id`, `lock_type`, `locked_quantity`

#### Inventory Status

- **Endpoint**: `/entity/inventory_status`
- **Purpose**: Inventory status management
- **Key Fields**: `status_id`, `status_code`, `description`

### Order Management Entities

#### Order Header (order_hdr)

- **Endpoint**: `/entity/order_hdr`
- **Purpose**: Order header information
- **Key Fields**: `order_id`, `order_number`, `order_type`, `customer_id`, `order_status`

#### Order Detail (order_dtl)

- **Endpoint**: `/entity/order_dtl`
- **Purpose**: Order line item details
- **Key Fields**: `order_dtl_id`, `order_id`, `item_id`, `quantity_ordered`, `quantity_allocated`

#### Order Status

- **Endpoint**: `/entity/order_status`
- **Purpose**: Order status tracking
- **Key Fields**: `status_id`, `order_id`, `status_code`, `status_date`

#### Order Type

- **Endpoint**: `/entity/order_type`
- **Purpose**: Order type configuration
- **Key Fields**: `order_type_id`, `description`, `default_priority`

#### Order Lock

- **Endpoint**: `/entity/order_lock`
- **Purpose**: Order locking operations
- **Key Fields**: `lock_id`, `order_id`, `lock_type`, `locked_by`

### Shipment Operations Entities

#### Inbound Shipment (ib_shipment)

- **Endpoint**: `/entity/ib_shipment`
- **Purpose**: Inbound shipment management
- **Key Fields**: `ib_shipment_id`, `shipment_number`, `vendor_id`, `facility_id`

#### Inbound Shipment Detail (ib_shipment_dtl)

- **Endpoint**: `/entity/ib_shipment_dtl`
- **Purpose**: Inbound shipment line details
- **Key Fields**: `ib_shipment_dtl_id`, `ib_shipment_id`, `item_id`, `quantity_expected`

#### Inbound Shipment Status

- **Endpoint**: `/entity/ib_shipment_status`
- **Purpose**: Inbound shipment status tracking
- **Key Fields**: `status_id`, `ib_shipment_id`, `status_code`

### Item Management Entities

#### Item

- **Endpoint**: `/entity/item`
- **Purpose**: Item master data
- **Key Fields**: `item_id`, `item_description`, `item_type`, `unit_of_measure`

#### Item Barcode

- **Endpoint**: `/entity/item_barcode`
- **Purpose**: Item barcode management
- **Key Fields**: `barcode_id`, `item_id`, `barcode`, `barcode_type`

#### Item Characteristics

- **Endpoint**: `/entity/item_characteristics`
- **Purpose**: Item characteristics and attributes
- **Key Fields**: `characteristic_id`, `item_id`, `characteristic_name`, `characteristic_value`

#### Item Facility

- **Endpoint**: `/entity/item_facility`
- **Purpose**: Item-facility specific configuration
- **Key Fields**: `item_facility_id`, `item_id`, `facility_id`, `active_flag`

### Warehouse Operations Entities

#### Location

- **Endpoint**: `/entity/location`
- **Purpose**: Warehouse location management
- **Key Fields**: `location_id`, `facility_id`, `location_type`, `active_flag`

#### Task

- **Endpoint**: `/entity/task`
- **Purpose**: Warehouse task management
- **Key Fields**: `task_id`, `task_type`, `assigned_user`, `task_status`

#### Wave

- **Endpoint**: `/entity/wave`
- **Purpose**: Wave planning and execution
- **Key Fields**: `wave_id`, `wave_number`, `wave_status`, `facility_id`

### Complete Alphabetical Entity List

```json
{
    \"action_code\": \"/entity/action_code\",
    \"active_location\": \"/entity/active_location\",
    \"aiml_model_training_hdr\": \"/entity/aiml_model_training_hdr\",
    \"aiml_order_cycle_time\": \"/entity/aiml_order_cycle_time\",
    \"aiml_prediction_order_cycle_time\": \"/entity/aiml_prediction_order_cycle_time\",
    \"aiml_prediction_run\": \"/entity/aiml_prediction_run\",
    \"allocation\": \"/entity/allocation\",
    \"appointment\": \"/entity/appointment\",
    \"asset\": \"/entity/asset\",
    \"asset_history\": \"/entity/asset_history\",
    \"asset_status\": \"/entity/asset_status\",
    \"asset_type\": \"/entity/asset_type\",
    \"batch_number\": \"/entity/batch_number\",
    \"billing_account\": \"/entity/billing_account\",
    \"bulk_change_eligible_group\": \"/entity/bulk_change_eligible_group\",
    \"business_partner\": \"/entity/business_partner\",
    \"company\": \"/entity/company\",
    \"container\": \"/entity/container\",
    \"container_history\": \"/entity/container_history\",
    \"container_status\": \"/entity/container_status\",
    \"container_type\": \"/entity/container_type\",
    \"cycle_count\": \"/entity/cycle_count\",
    \"cycle_count_batch\": \"/entity/cycle_count_batch\",
    \"cycle_count_dtl\": \"/entity/cycle_count_dtl\",
    \"facility\": \"/entity/facility\",
    \"iblpn\": \"/entity/iblpn\",
    \"iblpn_detail\": \"/entity/iblpn_detail\",
    \"iblpn_history\": \"/entity/iblpn_history\",
    \"ib_shipment\": \"/entity/ib_shipment\",
    \"ib_shipment_dtl\": \"/entity/ib_shipment_dtl\",
    \"item\": \"/entity/item\",
    \"item_barcode\": \"/entity/item_barcode\",
    \"item_characteristics\": \"/entity/item_characteristics\",
    \"item_facility\": \"/entity/item_facility\",
    \"item_metrics\": \"/entity/item_metrics\",
    \"inventory\": \"/entity/inventory\",
    \"inventory_attribute\": \"/entity/inventory_attribute\",
    \"inventory_history\": \"/entity/inventory_history\",
    \"inventory_lock\": \"/entity/inventory_lock\",
    \"inventory_status\": \"/entity/inventory_status\",
    \"load\": \"/entity/load\",
    \"location\": \"/entity/location\",
    \"location_type\": \"/entity/location_type\",
    \"oblpn\": \"/entity/oblpn\",
    \"oblpn_detail\": \"/entity/oblpn_detail\",
    \"oblpn_history\": \"/entity/oblpn_history\",
    \"order_hdr\": \"/entity/order_hdr\",
    \"order_dtl\": \"/entity/order_dtl\",
    \"order_lock\": \"/entity/order_lock\",
    \"order_status\": \"/entity/order_status\",
    \"order_type\": \"/entity/order_type\",
    \"task\": \"/entity/task\",
    \"task_history\": \"/entity/task_history\",
    \"task_status\": \"/entity/task_status\",
    \"task_type\": \"/entity/task_type\",
    \"wave\": \"/entity/wave\",
    \"wave_detail\": \"/entity/wave_detail\",
    \"wave_history\": \"/entity/wave_history\"
}
```

---

## 💡 API Examples & Usage

### Authentication Example

```python
# Get authentication token
authenticator = WMSAuthenticator(
    idcs_url=\"idcs-xxxx.identity.oraclecloud.com\",
    client_id=\"your_client_id\",
    client_secret=\"your_client_secret\"
)

auth_headers = authenticator.get_auth_headers()
```

### Basic CRUD Operations

#### Retrieve Orders

```python
import requests

# Get all orders
url = \"https://ta29.wms.ocs.oraclecloud.com:443/raizen_test/wms/lgfapi/v10/entity/order_hdr\"
response = requests.get(url, headers=auth_headers)
orders = response.json()

# Get specific order
order_url = f\"{url}/ORD123456\"
response = requests.get(order_url, headers=auth_headers)
order = response.json()

# Get orders with filtering
filtered_url = f\"{url}?order_status=OPEN&facility_id=WH01\"
response = requests.get(filtered_url, headers=auth_headers)
filtered_orders = response.json()
```

#### Create New Order

```python
# Create new order
new_order = {
    \"order_number\": \"ORD789012\",
    \"order_type\": \"SALES\",
    \"customer_id\": \"CUST001\",
    \"facility_id\": \"WH01\",
    \"order_status\": \"OPEN\",
    \"priority\": 5,
    \"order_date\": \"2025-01-10T10:00:00Z\"
}

response = requests.post(url, headers=auth_headers, json=new_order)
created_order = response.json()
```

#### Update Order

```python
# Update existing order
update_data = {
    \"order_status\": \"RELEASED\",
    \"priority\": 10
}

order_id = \"ORD123456\"
update_url = f\"{url}/{order_id}\"
response = requests.patch(update_url, headers=auth_headers, json=update_data)
```

### Advanced Filtering Examples

````python
# Complex filtering
complex_filter_url = f\"{base_url}/entity/inventory\" + \\\n    \"?item_id__in=ITEM001,ITEM002,ITEM003\" + \\\n    \"&quantity__gt=100\" + \\\n    \"&last_updated__gte=2025-01-01\" + \\\n    \"&facility_id=WH01\" + \\\n    \"&ordering=-last_updated\" + \\\n    \"&limit=50\"\n\nresponse = requests.get(complex_filter_url, headers=auth_headers)\ninventory_items = response.json()\n\n# Pagination example\ndef get_all_orders(base_url, headers):\n    all_orders = []\n    offset = 0\n    limit = 100\n    \n    while True:\n        url = f\"{base_url}/entity/order_hdr?limit={limit}&offset={offset}\"\n        response = requests.get(url, headers=headers)\n        data = response.json()\n        \n        orders = data.get('results', [])\n        if not orders:\n            break\n            \n        all_orders.extend(orders)\n        offset += limit\n        \n        # Check if we have more data\n        if len(orders) < limit:\n            break\n    \n    return all_orders\n```

### Batch Operations Example

```python
# Bulk order creation\nbulk_orders = [\n    {\n        \"order_number\": f\"BULK_{i:06d}\",\n        \"order_type\": \"SALES\",\n        \"customer_id\": \"CUST001\",\n        \"facility_id\": \"WH01\",\n        \"order_status\": \"OPEN\"\n    }\n    for i in range(1, 101)  # Create 100 orders\n]\n\n# Send in batches of 10\nbatch_size = 10\nfor i in range(0, len(bulk_orders), batch_size):\n    batch = bulk_orders[i:i + batch_size]\n    \n    for order in batch:\n        response = requests.post(\n            f\"{base_url}/entity/order_hdr\",\n            headers=auth_headers,\n            json=order\n        )\n        print(f\"Created order {order['order_number']}: {response.status_code}\")\n```

---

## 📤 Data Extraction

### Asynchronous Data Extract API

The Data Extract module provides capabilities to export large datasets to Object Storage (OCI, AWS S3, Google Cloud Storage, Azure Blob).

#### Extract Configuration

```python\nclass DataExtractManager:\n    def __init__(self, base_url: str, auth_headers: dict):\n        self.base_url = base_url\n        self.auth_headers = auth_headers\n    \n    def start_extraction(self, entity: str, config: dict) -> str:\n        \"\"\"Start asynchronous data extraction.\"\"\"\n        \n        extract_url = f\"{self.base_url}/data_extract/{entity}/export\"\n        \n        response = requests.post(\n            extract_url,\n            headers=self.auth_headers,\n            json=config\n        )\n        \n        response.raise_for_status()\n        result = response.json()\n        \n        return result['extraction_id']\n    \n    def check_status(self, extraction_id: str) -> dict:\n        \"\"\"Check extraction status.\"\"\"\n        \n        status_url = f\"{self.base_url}/data_extract/status/{extraction_id}\"\n        \n        response = requests.get(status_url, headers=self.auth_headers)\n        response.raise_for_status()\n        \n        return response.json()\n    \n    def download_results(self, extraction_id: str) -> str:\n        \"\"\"Get download URL for completed extraction.\"\"\"\n        \n        download_url = f\"{self.base_url}/data_extract/download/{extraction_id}\"\n        \n        response = requests.get(download_url, headers=self.auth_headers)\n        response.raise_for_status()\n        \n        result = response.json()\n        return result['download_url']\n\n# Usage example\nextract_config = {\n    \"format\": \"CSV\",  # CSV, JSON, Parquet\n    \"compression\": \"gzip\",\n    \"partition_size\": 10000,\n    \"filters\": {\n        \"facility_id\": \"WH01\",\n        \"last_updated__gte\": \"2025-01-01\"\n    },\n    \"fields\": [\"inventory_id\", \"item_id\", \"location_id\", \"quantity\"]\n}\n\nextract_manager = DataExtractManager(base_url, auth_headers)\n\n# Start extraction\nextraction_id = extract_manager.start_extraction(\"inventory\", extract_config)\n\n# Monitor progress\nimport time\nwhile True:\n    status = extract_manager.check_status(extraction_id)\n    \n    if status['status'] == 'COMPLETED':\n        download_url = extract_manager.download_results(extraction_id)\n        print(f\"Download ready: {download_url}\")\n        break\n    elif status['status'] == 'FAILED':\n        print(f\"Extraction failed: {status['error_message']}\")\n        break\n    else:\n        print(f\"Status: {status['status']}, Progress: {status['progress']}%\")\n        time.sleep(30)  # Wait 30 seconds before checking again\n```

### Supported Export Formats

#### CSV Format\n```json\n{\n    \"format\": \"CSV\",\n    \"compression\": \"gzip\",\n    \"delimiter\": \",\",\n    \"quote_char\": '\"',\n    \"include_header\": true\n}\n```\n\n#### JSON Format\n```json\n{\n    \"format\": \"JSON\",\n    \"compression\": \"gzip\",\n    \"json_format\": \"lines\"  # \"lines\" or \"array\"\n}\n```\n\n#### Parquet Format\n```json\n{\n    \"format\": \"PARQUET\",\n    \"compression\": \"snappy\",\n    \"partition_columns\": [\"facility_id\", \"item_type\"]\n}\n```\n\n---\n\n## ⚠️ Error Handling\n\n### HTTP Status Codes\n\n| Status Code | Meaning | Description |\n|-------------|---------|-------------|\n| **200** | OK | Request successful |\n| **201** | Created | Resource created successfully |\n| **204** | No Content | Request successful, no content returned |\n| **400** | Bad Request | Invalid request syntax or parameters |\n| **401** | Unauthorized | Authentication required or failed |\n| **403** | Forbidden | Insufficient permissions |\n| **404** | Not Found | Resource not found |\n| **409** | Conflict | Resource conflict (duplicate, constraint violation) |\n| **422** | Unprocessable Entity | Validation error |\n| **429** | Too Many Requests | Rate limit exceeded |\n| **500** | Internal Server Error | Server error |\n| **502** | Bad Gateway | Upstream server error |\n| **503** | Service Unavailable | Service temporarily unavailable |\n\n### Error Response Format\n\n```json\n{\n    \"error\": {\n        \"reference\": \"WMS-API-001\",\n        \"code\": \"VALIDATION_ERROR\",\n        \"message\": \"Invalid order status transition\",\n        \"details\": {\n            \"field\": \"order_status\",\n            \"current_value\": \"SHIPPED\",\n            \"attempted_value\": \"OPEN\",\n            \"valid_transitions\": [\"DELIVERED\", \"CANCELLED\"]\n        },\n        \"timestamp\": \"2025-01-10T14:30:00Z\",\n        \"request_id\": \"req_123456789\"\n    }\n}\n```\n\n### Common Error Scenarios\n\n#### Authentication Errors\n```python\ntry:\n    response = requests.get(url, headers=auth_headers)\n    response.raise_for_status()\nexcept requests.exceptions.HTTPError as e:\n    if e.response.status_code == 401:\n        # Token expired, refresh authentication\n        auth_headers = authenticator.get_auth_headers()\n        response = requests.get(url, headers=auth_headers)\n    else:\n        raise\n```\n\n#### Validation Errors\n```python\ndef handle_validation_error(error_response):\n    error_data = error_response.json().get('error', {})\n    \n    if error_data.get('code') == 'VALIDATION_ERROR':\n        details = error_data.get('details', {})\n        field = details.get('field')\n        message = details.get('message')\n        \n        print(f\"Validation error on field '{field}': {message}\")\n        \n        # Return corrected data or prompt user\n        return None\n    \n    raise Exception(f\"Unhandled error: {error_data}\")\n```\n\n#### Rate Limiting\n```python\nimport time\nfrom typing import Callable, Any\n\ndef with_retry(func: Callable, max_retries: int = 3, backoff_factor: float = 1.0) -> Any:\n    \"\"\"Execute function with exponential backoff retry.\"\"\"\n    \n    for attempt in range(max_retries + 1):\n        try:\n            return func()\n        except requests.exceptions.HTTPError as e:\n            if e.response.status_code == 429:  # Rate limited\n                if attempt < max_retries:\n                    wait_time = backoff_factor * (2 ** attempt)\n                    print(f\"Rate limited. Waiting {wait_time} seconds...\")\n                    time.sleep(wait_time)\n                    continue\n            raise\n    \n    raise Exception(f\"Failed after {max_retries} retries\")\n\n# Usage\nresult = with_retry(\n    lambda: requests.get(url, headers=auth_headers),\n    max_retries=5,\n    backoff_factor=1.5\n)\n```\n\n---\n\n## 🏗️ Integration Architecture\n\n### FLEXT Framework Integration Pattern\n\n```python\nfrom dataclasses import dataclass\nfrom typing import List, Optional, Dict, Any\nfrom abc import ABC, abstractmethod\n\n@dataclass\nclass WMSOrder:\n    \"\"\"Domain entity for WMS orders.\"\"\"\n    order_id: str\n    order_number: str\n    order_type: str\n    customer_id: str\n    facility_id: str\n    order_status: str\n    priority: int\n    order_date: str\n    items: List['WMSOrderItem'] = None\n\n@dataclass\nclass WMSOrderItem:\n    \"\"\"Domain entity for WMS order items.\"\"\"\n    order_dtl_id: str\n    item_id: str\n    quantity_ordered: int\n    quantity_allocated: int = 0\n    quantity_shipped: int = 0\n\nclass WMSRepository(ABC):\n    \"\"\"Abstract repository for WMS operations.\"\"\"\n    \n    @abstractmethod\n    async def get_order(self, order_id: str) -> Optional[WMSOrder]:\n        pass\n    \n    @abstractmethod\n    async def create_order(self, order: WMSOrder) -> WMSOrder:\n        pass\n    \n    @abstractmethod\n    async def update_order(self, order: WMSOrder) -> WMSOrder:\n        pass\n    \n    @abstractmethod\n    async def search_orders(self, criteria: Dict[str, Any]) -> List[WMSOrder]:\n        pass\n\nclass OracleWMSAdapter(WMSRepository):\n    \"\"\"Oracle WMS REST API adapter implementation.\"\"\"\n    \n    def __init__(self, base_url: str, authenticator: WMSAuthenticator):\n        self.base_url = base_url\n        self.authenticator = authenticator\n        self.session = requests.Session()\n    \n    async def get_order(self, order_id: str) -> Optional[WMSOrder]:\n        \"\"\"Retrieve order from Oracle WMS.\"\"\"\n        url = f\"{self.base_url}/entity/order_hdr/{order_id}\"\n        headers = self.authenticator.get_auth_headers()\n        \n        response = self.session.get(url, headers=headers)\n        \n        if response.status_code == 404:\n            return None\n        \n        response.raise_for_status()\n        order_data = response.json()\n        \n        # Convert API response to domain entity\n        return self._map_to_domain_order(order_data)\n    \n    async def create_order(self, order: WMSOrder) -> WMSOrder:\n        \"\"\"Create new order in Oracle WMS.\"\"\"\n        url = f\"{self.base_url}/entity/order_hdr\"\n        headers = self.authenticator.get_auth_headers()\n        \n        # Convert domain entity to API payload\n        payload = self._map_from_domain_order(order)\n        \n        response = self.session.post(url, headers=headers, json=payload)\n        response.raise_for_status()\n        \n        created_order_data = response.json()\n        return self._map_to_domain_order(created_order_data)\n    \n    def _map_to_domain_order(self, api_data: dict) -> WMSOrder:\n        \"\"\"Map API response to domain entity.\"\"\"\n        return WMSOrder(\n            order_id=api_data['order_id'],\n            order_number=api_data['order_number'],\n            order_type=api_data['order_type'],\n            customer_id=api_data['customer_id'],\n            facility_id=api_data['facility_id'],\n            order_status=api_data['order_status'],\n            priority=api_data.get('priority', 5),\n            order_date=api_data['order_date']\n        )\n    \n    def _map_from_domain_order(self, order: WMSOrder) -> dict:\n        \"\"\"Map domain entity to API payload.\"\"\"\n        return {\n            'order_number': order.order_number,\n            'order_type': order.order_type,\n            'customer_id': order.customer_id,\n            'facility_id': order.facility_id,\n            'order_status': order.order_status,\n            'priority': order.priority,\n            'order_date': order.order_date\n        }\n\nclass WMSService:\n    \"\"\"Application service for WMS operations.\"\"\"\n    \n    def __init__(self, wms_repository: WMSRepository):\n        self.wms_repository = wms_repository\n    \n    async def process_new_order(self, order_data: dict) -> WMSOrder:\n        \"\"\"Process new order with business logic.\"\"\"\n        \n        # Business validation\n        if not order_data.get('customer_id'):\n            raise ValueError(\"Customer ID is required\")\n        \n        # Create domain entity\n        order = WMSOrder(\n            order_id=None,  # Will be assigned by WMS\n            order_number=order_data['order_number'],\n            order_type=order_data.get('order_type', 'SALES'),\n            customer_id=order_data['customer_id'],\n            facility_id=order_data['facility_id'],\n            order_status='OPEN',\n            priority=order_data.get('priority', 5),\n            order_date=order_data.get('order_date', datetime.now().isoformat())\n        )\n        \n        # Create in WMS\n        created_order = await self.wms_repository.create_order(order)\n        \n        # Business logic (e.g., notifications, auditing)\n        await self._notify_order_created(created_order)\n        \n        return created_order\n    \n    async def _notify_order_created(self, order: WMSOrder):\n        \"\"\"Handle order creation notifications.\"\"\"\n        # Implementation for notifications\n        pass\n```\n\n### Configuration Management\n\n```python\nfrom pydantic import BaseSettings, Field\nfrom typing import Optional\n\nclass WMSConfig(BaseSettings):\n    \"\"\"WMS configuration with validation.\"\"\"\n    \n    # Environment configuration\n    environment: str = Field(default=\"production\", description=\"Environment: production or test\")\n    \n    # WMS API configuration\n    wms_base_url: str = Field(..., description=\"WMS API base URL\")\n    wms_tenant: str = Field(..., description=\"WMS tenant identifier\")\n    wms_api_version: str = Field(default=\"v10\", description=\"API version\")\n    \n    # Authentication configuration\n    idcs_url: str = Field(..., description=\"IDCS URL for OAuth2\")\n    client_id: str = Field(..., description=\"OAuth2 client ID\")\n    client_secret: str = Field(..., description=\"OAuth2 client secret\")\n    \n    # Connection configuration\n    connection_timeout: int = Field(default=30, description=\"Connection timeout in seconds\")\n    read_timeout: int = Field(default=60, description=\"Read timeout in seconds\")\n    max_retries: int = Field(default=3, description=\"Maximum retry attempts\")\n    \n    # Rate limiting\n    rate_limit_requests: int = Field(default=100, description=\"Requests per minute\")\n    rate_limit_burst: int = Field(default=20, description=\"Burst requests allowed\")\n    \n    class Config:\n        env_file = \".env\"\n        env_prefix = \"WMS_\"\n    \n    @property\n    def entity_base_url(self) -> str:\n        \"\"\"Complete entity API base URL.\"\"\"\n        return f\"{self.wms_base_url}/{self.wms_tenant}/wms/lgfapi/{self.wms_api_version}/entity\"\n    \n    @property\n    def data_extract_base_url(self) -> str:\n        \"\"\"Complete data extract API base URL.\"\"\"\n        return f\"{self.wms_base_url}/{self.wms_tenant}/wms/lgfapi/{self.wms_api_version}/data_extract\"\n\n# Usage\nconfig = WMSConfig()\nwms_adapter = OracleWMSAdapter(\n    base_url=config.entity_base_url,\n    authenticator=WMSAuthenticator(\n        idcs_url=config.idcs_url,\n        client_id=config.client_id,\n        client_secret=config.client_secret\n    )\n)\n```\n\n---\n\n## 📚 Related Documentation\n\n### Core Integration Guides\n- [Oracle OAuth2 Authentication Guide](oracle-oauth2-authentication-guide.md) - Complete OAuth2 implementation\n- [Oracle WMS Commands Reference](oracle-wms-commands-reference.md) - CLI command reference\n- [Oracle WMS Integration Project Plan](oracle-wms-integration-project-plan.md) - Business implementation plan\n\n### Architecture Documentation\n- [Oracle Integration Comprehensive Guide](oracle-integration-comprehensive-guide.md) - High-level architecture\n- [Infrastructure Architecture](../architecture/infrastructure-architecture.md) - System infrastructure\n- [Hexagonal Architecture Guide](../architecture/unified-architecture-guide.md) - Architecture patterns\n\n### Implementation Guides\n- [Oracle WMS Dynamic Integration](oracle-wms-dynamic-integration.md) - Advanced dynamic discovery\n- [FLEXT HTTP Oracle WMS Adapter](flext-http-oracle-wms-adapter.md) - Adapter implementation\n- [Testing Guide](testing-guide.md) - Testing strategies\n\n---\n\n**Document Status**: Consolidated Reference (January 2025)  \n**Source Documents**: oracle-integration-api-guide.md, oracle-wms-rest-api-guide.md, oracle-wms-api-entities-reference.md  \n**Maintainer**: FLEXT Framework Documentation Team  \n**Next Review**: Q2 2025

---

## 🔗 **Cross-References**

### **Prerequisites**
- [Getting Started Hub](../../getting-started/index.md) - Essential FLEXT Framework installation and setup before Oracle integration
- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns for effective Oracle WMS integration
- [Oracle OAuth2 Authentication Guide](./oracle-oauth2-authentication-guide.md) - Required authentication setup before API usage

### **Next Steps**
- [Examples Hub](../../examples/index.md) - Working code examples demonstrating Oracle WMS integration patterns
- [Development Hub](../../development/index.md) - Testing frameworks and development tools for Oracle integration development
- [Infrastructure Hub](../../infrastructure/index.md) - Production infrastructure setup for Oracle WMS integrations

### **Related Topics**
- [API Reference Hub](../../api-reference/index.md) - Complete FLEXT Framework API documentation for adapter development
- [Security Hub](../../security/index.md) - Security patterns and authentication strategies for Oracle integrations
- [Migration Hub](../../migration/index.md) - Migration considerations for upgrading Oracle integration implementations
- [Deployment Hub](../../deployment/index.md) - Production deployment strategies for Oracle WMS integration systems

---

**📂 Hub**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
````
