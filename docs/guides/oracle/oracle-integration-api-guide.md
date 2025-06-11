# 🔗 Oracle Integration API Guide

> **Function**: Oracle WMS Cloud integration APIs and implementation patterns | **Audience**: API developers, integration engineers | **Status**: Production-ready

[![WMS](https://img.shields.io/badge/Oracle-WMS%20Cloud-red.svg)](./oracle-wms-comprehensive-guide.md)
[![API](https://img.shields.io/badge/api-REST%2BSOAP-blue.svg)](./index.md)
[![Integration](https://img.shields.io/badge/integration-hexagonal-green.svg)](../../architecture/index.md)

**Comprehensive guide covering Oracle Warehouse Management Cloud integration capabilities, REST APIs, OAuth 2.0 authentication, and technical implementation guidelines for external systems integration within hexagonal architecture**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: Integration API Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[Integration API Guide]** → [WMS Comprehensive Guide](./oracle-wms-comprehensive-guide.md)
```

---

## Table of Contents

1. [Overview](#overview)
2. [Integration Categories](#integration-categories)
3. [OAuth 2.0 Support](#oauth-20-support)
4. [WMS Web Service APIs](#wms-web-service-apis)
5. [Technical Implementation](#technical-implementation)
6. [API Examples and Usage](#api-examples-and-usage)
7. [Integration Architecture Considerations](#integration-architecture-considerations)

---

## Overview

Oracle Fusion Cloud Warehouse Management supports comprehensive integration capabilities for external systems, automated operations, and data exchange. This guide provides detailed specifications for implementing integrations within hexagonal architecture patterns.

### Key Integration Areas

- **Automation and Operations**: MHE systems, voice technologies, and externally triggered WMS operations
- **Parcel Carrier Integration**: FedEx, UPS, and ConnectShip web services
- **Setup and Transactional Data**: Master data, orders, shipments, and inventory management

### Communication Protocols

The system supports multiple communication methods:

- **REST Web Services over HTTPS**: Primary integration method for real-time operations
- **Secure FTP (SFTP)**: File-based data exchange using external SFTP sites
- **SOAP APIs**: Specialized support for parcel carrier integrations

### Supported Data Formats

- **XML**: Structured data with XSD schema definitions
- **Delimited flat files**: Pipe-delimited and CSV formats
- **JSON**: For modern REST API implementations

---

## Integration Categories

### Automation and Operations

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

### Parcel Carrier Integration

#### Supported Carriers

- **FedEx**: Direct web service integration
- **UPS**: Native web service support
- **ConnectShip**: Multi-carrier gateway for UPS, DHL GlobalMail

#### Integration Requirements

- Carrier account and credentials
- Oracle WMS Cloud configuration
- Label generation and tracking capabilities
- Rate calculation and service selection

### Setup and Transactional Data

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

## OAuth 2.0 Support

### Authentication Overview

Oracle WMS Cloud supports OAuth 2.0 for secure API access and integration with Oracle Integration Cloud (OIC) and external systems.

### Input Interface Authentication

#### Supported Grant Types

- **Resource Owner Password Credentials**: Username/password authentication
- **Authorization Code**: Redirect-based authentication
- **Client Credentials**: Service-to-service authentication

#### Configuration Steps

1. **Create OAuth Application**
   - Navigate to `api/oauth2/applications` screen
   - Register new application with required parameters
   - Generate Client ID and Client Secret

2. **OIC Connection Setup**
   - Configure REST adapter security policy
   - Set appropriate grant type and credentials
   - Configure redirect URIs for authorization code flow

#### OAuth Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Client ID | String | Yes | Generated application identifier |
| Client Secret | String | Yes | Secure application credential |
| Access Token URI | URL | Yes | Token endpoint for authentication |
| Authorization Code URI | URL | Conditional | Required for authorization code flow |
| Scope | String | Yes | Access scope definition |

### Output Interface Authentication

#### OAuth 2.0 Fields for Output Interfaces

- **Interface Authentication Type**: Basic Auth or OAuth 2.0
- **Client ID**: Application identifier
- **Client Secret**: Secure credential
- **Token URL**: OAuth token endpoint
- **Scope**: Required access permissions

#### Supported Interface Types

All interface types except "Bill of Lading" and "Commercial Invoice" support OAuth 2.0 authentication.

---

## WMS Web Service APIs

### Authentication and Authorization

#### Required Permissions

- **User Authentication**: Valid WMS username and password via BasicAuth
- **API Permission**: `can_run_ws_stage_interface` for legacy APIs
- **LGFAPI Permissions**: Granular CRUD permissions for new APIs
  - `lgfapi_read_access`: GET, HEAD operations
  - `lgfapi_create_access`: POST operations
  - `lgfapi_update_access`: PATCH operations
  - `lgfapi_delete_access`: DELETE operations

#### Facility/Company Access

Users must have eligibility to access facility/company combinations represented in the data.

### Core API Categories

#### Setup and Transactional Data APIs

**Init Stage Interface**

- **Purpose**: Load and process data into stage tables
- **Supported Formats**: XML and flat file data
- **URL**: `/wms/api/init_stage_interface/`
- **Entities**: Items, orders, purchase orders, shipments, vendors

**Run Stage Interface**

- **Purpose**: Process data already in staging tables
- **URL**: `/wms/api/run_stage_interface/`
- **Parameters**: Optional file_group_nbr for targeted processing

#### Automation and Operations APIs

**Update OBLPN Tracking Number**

- **Purpose**: Update carrier tracking information
- **URL**: `/wms/api/update_oblpn_tracking_nbr/`
- **Parameters**: Container number, tracking number, weight, carrier details

**Assign OBLPN to Load**

- **Purpose**: Assign outbound containers to shipping loads
- **URL**: `/wms/api/assign_oblpn_to_load/`
- **Features**: Bulk assignment, load creation, trailer assignment

**Create LPN**

- **Purpose**: Create inbound containers with cross-dock capability
- **URL**: `/wms/api/create_lpn/`
- **Features**: Single SKU creation, automatic cross-docking

#### MHE Integration APIs

**Induct LPN**

- **Purpose**: Induct containers into MHE conveyor systems
- **URL**: `/wms/api/induct_lpn/`
- **Features**: Automatic route instruction generation

**Divert Confirm**

- **Purpose**: Confirm container diversion by MHE systems
- **URL**: `/wms/api/divert_confirm/`
- **Features**: Location updates, putaway completion

**Load LPN**

- **Purpose**: Load outbound containers onto vehicles
- **URL**: `/wms/api/assign_and_load_oblpn/`
- **Features**: Assignment and loading in single operation

#### Entity Management APIs

**Entity Update API**

- **Purpose**: Update specific entity attributes
- **URL**: `/wms/api/entity/{entity_name}/{key}/`
- **Method**: PATCH
- **Entities**: Orders, purchase orders, active inventory

**From MHE Distribution APIs**

- **Pack**: `/wms/api/from_mhe_distribution_pack/`
- **Short**: `/wms/api/from_mhe_distribution_short/`
- **Purpose**: Handle MHE packing and shortage reporting

### Response Structure

#### Success Response

```xml
<?xml version="1.0" encoding="utf-8"?>
<root>
    <success>True</success>
    <response>
        <message>Process completed successfully</message>
        <errors/>
        <data/>
    </response>
</root>
```

#### Error Response

```xml
<?xml version="1.0" encoding="utf-8"?>
<root>
    <success>False</success>
    <response>
        <message>Error description</message>
    </response>
</root>
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Successful operation |
| 201 | Created | Resource successfully created |
| 204 | No Content | Successful with no response body |
| 400 | Bad Request | Invalid data or request structure |
| 401 | Unauthorized | Invalid login credentials |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Concurrent modification conflict |
| 500 | Server Error | Unhandled error condition |

---

## Technical Implementation

### REST API Principles

#### HTTP Methods

- **GET**: Read-only resource retrieval
- **POST**: Create resources or submit data
- **PATCH**: Modify existing resources
- **DELETE**: Remove or deactivate resources
- **HEAD**: Check resource existence

#### Request Requirements

- **Method**: POST for most operations
- **Content-Type**: `application/x-www-form-urlencoded` or `application/xml`
- **Authentication**: BasicAuth with valid WMS credentials
- **Data Encoding**: URL encoding for special characters

#### Request Headers

- **Authorization**: Basic authentication header
- **Content-Type**: Data format specification
- **User-Agent**: Client identification (optional)

### Data Formats

#### Key-Value Pairs

- Format: `key1=value1&key2=value2`
- Encoding: URL encoding for special characters
- Separation: Ampersand (&) between pairs

#### XML Payload

- Well-formed XML structure
- Schema validation available
- Header information in `<Header>` tag
- Entity data in appropriate XML elements

### API Versioning

#### LGFAPI Versioning

- **Current Version**: v10
- **Format**: `/lgfapi/v{number}/`
- **Compatibility**: Previous versions supported for one year
- **Migration**: Recommended to use latest version

---

## API Examples and Usage

### Basic Authentication Example

```bash
curl -X POST \
  https://example.wms.ocs.oraclecloud.com/env/wms/api/init_stage_interface/ \
  -H 'Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'xml_data=<xml>...</xml>&async=true'
```

### OAuth 2.0 Token Request

```bash
curl -X POST \
  https://example.wms.ocs.oraclecloud.com/env/api/oauth2/token/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET'
```

### XML Data Example

```xml
<LgfData>
    <Header>
        <DocumentVersion>25B</DocumentVersion>
        <OriginSystem>External</OriginSystem>
        <Entity>item</Entity>
        <TimeStamp>2025-01-01T12:00:00</TimeStamp>
    </Header>
    <ListOfItems>
        <item>
            <item_code>SKU001</item_code>
            <description>Sample Item</description>
            <item_category>Standard</item_category>
        </item>
    </ListOfItems>
</LgfData>
```

### Error Handling Best Practices

1. **Check Response Status**: Always verify success/failure
2. **Parse Error Messages**: Extract meaningful error information
3. **Implement Retry Logic**: Handle temporary failures
4. **Log All Transactions**: Maintain audit trail

---

## Integration Architecture Considerations

### Hexagonal Architecture Alignment

#### Port Definitions for WMS Integration

**Inbound Ports**

- **REST API Port**: Handle incoming HTTP requests
- **File Processing Port**: Process uploaded files
- **OAuth Authentication Port**: Manage token-based authentication

**Outbound Ports**

- **WMS API Client Port**: Communicate with Oracle WMS Cloud APIs
- **File Transfer Port**: Handle SFTP operations
- **Carrier Integration Port**: Interface with shipping carriers

#### Adapter Patterns

**REST API Adapters**

- **Authentication Adapter**: Handle OAuth 2.0 and BasicAuth
- **Data Transformation Adapter**: Convert between formats
- **Error Handling Adapter**: Process API responses and errors

**Data Integration Adapters**

- **XML Processing Adapter**: Handle XML parsing and generation
- **File Processing Adapter**: Manage flat file operations
- **Batch Processing Adapter**: Handle large data volumes

### Domain Service Implementation

#### Integration Services

- **API Client Service**: Centralized WMS API communication
- **Authentication Service**: Token management and credential handling
- **Data Transformation Service**: Format conversion and validation

#### Business Logic Services

- **Order Processing Service**: Handle order lifecycle management
- **Inventory Service**: Manage stock movements and adjustments
- **Shipping Service**: Coordinate carrier integrations

### Implementation Best Practices

#### Security Considerations

- **Credential Management**: Secure storage of API keys and tokens
- **Token Refresh**: Automatic OAuth token renewal
- **Access Control**: Role-based API permission management

#### Performance Optimization

- **Connection Pooling**: Reuse HTTP connections
- **Batch Operations**: Group related API calls
- **Async Processing**: Handle long-running operations

#### Error Recovery

- **Circuit Breaker**: Handle API unavailability
- **Retry Strategies**: Exponential backoff for failures
- **Dead Letter Queues**: Manage failed operations

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before API implementation
- [Oracle Authentication Guide](./oracle-authentication-comprehensive-guide.md) - OAuth2 and security setup required for API access
- [Architecture Hub](../../architecture/index.md) - Hexagonal architecture patterns for API integration

### **Next Steps**

- [Oracle WMS Guide](./oracle-wms-comprehensive-guide.md) - Complete WMS implementation using these API patterns
- [Oracle OAuth2 Guide](./oracle-oauth2-authentication-guide.md) - Detailed authentication implementation for API access
- [Development Testing](../../development/testing/index.md) - API testing strategies and validation patterns

### **Related Topics**

- [API Reference Hub](../../api-reference/index.md) - Complete API documentation and method references
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure patterns supporting API integration
- [Security Hub](../../security/index.md) - API security patterns and best practices
- [Examples Hub](../../examples/index.md) - Working API integration examples and implementations

---

## 📊 **Document Metrics**

- **Implementation Status**: ✅ Production Ready (Release 25B)
- **API Coverage**: REST, SOAP, SFTP integration patterns
- **Authentication Methods**: OAuth 2.0, Basic Auth, Token-based
- **Integration Categories**: 3 major areas (Automation, Carriers, Data)
- **Architecture Pattern**: Hexagonal with ports and adapters
- **Last Updated**: June 11, 2025

---

**📂 Guide**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
