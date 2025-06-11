# Meltano Plugins Integration Guide

> **Related Documentation:**
>
> - [Oracle Platform Resources](./oracle-platform-resources.md) - Oracle systems documentation
> - [Development Tools](./development-tools.md) - Development and testing tools
> - [WMS CLI Guide](./wms-cli-guide.md) - Oracle WMS command-line operations
> - [JWT Service Guide](./jwt-service-guide.md) - Authentication patterns

A comprehensive guide for integrating Oracle systems with Meltano using custom extractors, loaders, and transformers. This guide covers the complete data pipeline for Oracle Integration Cloud (OIC), Oracle WMS Cloud, and Oracle Database integration.

## Overview

The Meltano plugins in this workspace provide comprehensive data extraction and loading capabilities for Oracle systems:

- **tap-oic**: Oracle Integration Cloud (OIC) extractor for integration metadata and monitoring
- **tap-oic-wms**: Oracle WMS Cloud extractor with multiple extraction modes
- **tap-oracle-adb**: Oracle Autonomous Database extractor
- **target-oracle**: Oracle Database loader with bulk operations
- **transform-oic**: Data transformation mappings for OIC data
- **orchestrator-oic**: Workflow orchestration utility

## Oracle Integration Cloud (OIC) Extractor

### Features

- **Integration Metadata Extraction**: Extract metadata from OIC integrations and flows
- **Execution Status Monitoring**: Monitor integration execution status and performance
- **Event and Log Capture**: Capture integration events and detailed logs
- **Payload Processing**: Extract processed payload data from OIC integrations
- **Incremental Extraction**: Support for pagination and incremental data extraction

### Prerequisites

- Python 3.8 or higher
- Access to Oracle Integration Cloud (OIC) v3
- OAuth2 or Basic Auth credentials configured

### Installation

```bash
# Via pip
pip install tap-oic

# Via Meltano
meltano add extractor tap-oic
```

### Configuration

#### Basic Configuration

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-oic
      variant: custom
      pip_url: tap-oic
      config:
        oic_url: https://instance-name.integration.ocp.oraclecloud.com
        auth_method: oauth2
        client_id: YOUR_CLIENT_ID
        client_secret: YOUR_CLIENT_SECRET
        idcs_url: idcs-xxxx.identity.oraclecloud.com
        resource_aud: https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
        api_aud: https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/
```

#### Advanced Configuration

```yaml
# config.json
{
  "oic_url": "https://instance-name.integration.ocp.oraclecloud.com",
  "auth_method": "oauth2",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "idcs_url": "idcs-xxxx.identity.oraclecloud.com",
  "resource_aud": "https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all",
  "api_aud": "https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/",
  "start_date": "2023-01-01T00:00:00Z",
  "integration_filter": "WMS_*",
  "batch_size": 100,
  "include_payload": true,
  "include_logs": true,
  "payload_format": "json",
  "request_timeout": 300
}
```

#### Basic Authentication Configuration

```yaml
# For Basic Auth
plugins:
  extractors:
    - name: tap-oic
      variant: custom
      pip_url: tap-oic
      config:
        oic_url: https://instance-name.integration.ocp.oraclecloud.com
        auth_method: basic
        username: YOUR_USERNAME
        password: YOUR_PASSWORD
```

### Available Streams

The OIC extractor provides the following data streams:

- **integrations**: Metadata for all integrations
- **instances**: Integration execution instances
- **logs**: Detailed execution logs
- **connections**: Configured connections in OIC
- **lookups**: Available lookup tables
- **payloads**: Input/output payloads from integrations (optional)

### Data Filtering and Selection

Filter integrations by patterns using globbing, for example `WMS_*` to capture only WMS-related integrations:

```yaml
config:
  integration_filter: "WMS_*"
```

## Oracle WMS Cloud Extractor

### Features

- **Order Data Extraction**: Extract orders (headers and details)
- **Inventory Allocation Extraction**: Extract stock allocations
- **Incremental Load Support**: Support for incremental loads and change data capture
- **Webhook Support**: Real-time event processing via auxiliary webhook server
- **CSV Export Support**: High-volume initial loads via CSV export

### Prerequisites

- Python 3.8 or higher
- Access to Oracle WMS Cloud v25A/25B or higher
- Basic Auth credentials for WMS APIs
- SFTP server configured (optional, for CSV extractions)

### Installation

```bash
# Via pip
pip install tap-wms

# Via Meltano
meltano add extractor tap-wms
```

### Configuration

#### Basic Configuration

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-wms
      variant: custom
      pip_url: tap-wms
      config:
        wms_url: https://tenantname.wms.ocs.oraclecloud.com/env/wms/api
        username: INT_OIC  # Integration user created in WMS
        password: YOUR_PASSWORD
        start_date: '2023-01-01T00:00:00Z'
```

#### Advanced Configuration

```yaml
# Complete config.json
{
  "wms_url": "https://tenantname.wms.ocs.oraclecloud.com/env/wms/api",
  "username": "INT_OIC",
  "password": "YOUR_PASSWORD",
  "start_date": "2023-01-01T00:00:00Z",
  "company_code": "YOURCO",
  "facility_code": "WH1",
  "batch_size": 100,
  "request_timeout": 300,
  "extraction_mode": "api",  # Options: "api", "csv", "webhook"
  "sftp_config": {
    "host": "sftp.example.com",
    "port": 22,
    "username": "sftp_user",
    "password": "sftp_password",
    "directory": "/WMSInitialLoad"
  },
  "webhook_config": {
    "listen_port": 5000,
    "endpoint_path": "/wms-events",
    "auth_required": true,
    "webhook_username": "webhook_user",
    "webhook_password": "webhook_password"
  },
  "enable_metadata_columns": true,
  "retry_count": 3,
  "connection_timeout": 60
}
```

### Extraction Modes

The WMS extractor supports three extraction modes:

#### 1. API Mode (Default)

Extracts data directly through WMS Cloud REST APIs.

```yaml
config:
  extraction_mode: "api"
```

#### 2. CSV Mode (For Large Volumes)

Uses CSV exports via SFTP for initial loads or large data volumes. This mode requires scheduled Meltano jobs that periodically check for new files on the SFTP server:

```yaml
config:
  extraction_mode: "csv"
  sftp_config:
    host: "sftp.example.com"
    port: 22
    username: "sftp_user"
    password: "sftp_password"
    directory: "/WMSInitialLoad"
```

#### 3. Webhook Mode (For Real-time Events)

Configures a local webhook server to receive events from WMS:

```yaml
config:
  extraction_mode: "webhook"
  webhook_config:
    listen_port: 5000
    endpoint_path: "/wms-events"
    auth_required: true
    webhook_username: "webhook_user"
    webhook_password: "webhook_password"
```

After configuring this mode, you'll need to configure Output Interfaces in WMS Cloud to point to this endpoint.

### Available Streams

The WMS extractor provides the following main streams:

- **order_hdr**: Order headers
- **order_dtl**: Order details (lines)
- **allocations**: Stock allocations
- **inventory_history**: Inventory transaction history
- **facilities**: Facilities/warehouses
- **items**: Items/products
- **lpns**: Logical Packaging Numbers (LPNs)
- **locations**: Warehouse locations

### WMS Cloud Configuration

To use this extractor, you must configure the following in WMS Cloud:

#### For API Extraction

- Create an integration user with `can_run_ws_stage_interface` permission
- Assign the user access to the required companies/facilities

#### For Webhook Extraction

1. Access the Endpoint menu in WMS (Output Interface Configuration)
2. Configure Output Interfaces for Orders and Allocations:
   - Select REST Web Service as protocol
   - Point to your webhook server endpoint
   - Configure Basic Auth with the configured credentials
   - Activate the interfaces

## Oracle Autonomous Database (ADB) Extractor

### Configuration

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-oracle-adb
      variant: custom
      pip_url: tap-oracle-adb
      config:
        connection_string: "your_adb_connection_string"
        username: YOUR_USERNAME
        password: YOUR_PASSWORD
        wallet_location: "/path/to/wallet"
        service_name: "your_service_name"
```

## Oracle Database Loader (Target)

### Configuration

```yaml
# meltano.yml
plugins:
  loaders:
    - name: target-oracle
      variant: custom
      pip_url: target-oracle
      config:
        connection_string: "oracle://username:password@host:port/service_name"
        default_target_schema: "PUBLIC"
        batch_config:
          batch_size: 1000
          flush_all_streams: true
```

## Data Transformation (Transform-OIC)

### Configuration

```yaml
# meltano.yml
plugins:
  transformers:
    - name: transform-oic
      variant: custom
      pip_url: transform-oic
      config:
        mapping_rules:
          - source_field: "oic_integration_id"
            target_field: "integration_identifier"
            transformation: "uppercase"
          - source_field: "execution_timestamp"
            target_field: "processed_at"
            transformation: "datetime_format"
            format: "YYYY-MM-DD HH:MM:SS"
```

## Orchestration Utility (Orchestrator-OIC)

### Configuration

```yaml
# meltano.yml
plugins:
  utilities:
    - name: orchestrator-oic
      variant: custom
      pip_url: orchestrator-oic
      config:
        workflow_definition: "/path/to/workflow.yaml"
        execution_mode: "sequential"
        retry_policy:
          max_attempts: 3
          backoff_factor: 2
        notification_config:
          email_enabled: true
          webhook_enabled: true
```

## Complete Pipeline Examples

### 1. OIC Monitoring Pipeline

```bash
# Extract OIC data and load into Oracle Database
meltano elt tap-oic target-oracle --job-id=oic_monitoring

# Extract only WMS integrations and load into Oracle
meltano elt tap-oic target-oracle --select="integrations" --job-id=wms_integrations
```

### 2. WMS Data Pipeline

```bash
# Initial extraction via CSV and loading into Oracle Database
meltano elt tap-wms target-oracle --job-id=wms_initial_load

# Continuous extraction via API
meltano elt tap-wms target-oracle --job-id=wms_daily_sync
```

### 3. Complete Data Warehouse Pipeline

```yaml
# meltano.yml
schedules:
  - name: oic_monitoring_daily
    extractor: tap-oic
    loader: target-oracle
    interval: '@daily'
    start_date: 2023-01-01
    config:
      integration_filter: "*"
      include_logs: true

  - name: wms_continuous_sync
    extractor: tap-wms
    loader: target-oracle
    interval: '@hourly'
    start_date: 2023-01-01
    config:
      extraction_mode: "api"
      batch_size: 500

  - name: wms_initial_load
    extractor: tap-wms
    loader: target-oracle
    interval: '@once'
    config:
      extraction_mode: "csv"
```

### 4. Real-time Event Processing

```yaml
# Webhook-based real-time processing
schedules:
  - name: wms_realtime_events
    extractor: tap-wms
    loader: target-oracle
    interval: '@continuous'
    config:
      extraction_mode: "webhook"
      webhook_config:
        listen_port: 5000
        endpoint_path: "/wms-events"
```

## Development and Architecture

All plugins are developed using the [Meltano SDK](https://sdk.meltano.com/) to ensure compatibility and follow extractor construction best practices.

### Code Structure

```
tap_oic/
├── __init__.py
├── auth.py        # Authentication logic (OAuth2, Basic)
├── client.py      # HTTP client for OIC API
├── streams.py     # Data stream definitions
└── tap.py         # Main extractor class

tap_wms/
├── __init__.py
├── auth.py        # Authentication logic
├── client.py      # HTTP client for WMS API
├── streams.py     # Data stream definitions
├── webhook.py     # Webhook server implementation
├── csv_reader.py  # CSV processing logic
└── tap.py         # Main extractor class
```

## Troubleshooting

### Authentication Errors

**OIC Authentication Issues:**

- Ensure OAuth2 credentials are correct
- Verify OAuth2 client has adequate permissions in IDCS
- Check resource_aud and api_aud formats are correct (no slash between port and "urn" in resource_aud)

**WMS Authentication Issues:**

- Verify user has correct permissions in WMS
- Confirm user has access to configured companies/facilities

### Timeouts with Large Volumes

Increase `request_timeout` to handle long API calls:

```yaml
config:
  request_timeout: 600  # 10 minutes
```

For WMS large volume extractions:

- Use `csv` mode for initial loads
- Increase `request_timeout` and `connection_timeout`
- Reduce `batch_size` to smaller values

### Rate Limiting

OIC may have request rate limitations. Configure:

```yaml
config:
  max_requests_per_minute: 60
```

### Webhook Issues

- Verify webhook server is externally accessible
- Confirm firewall allows access to configured port
- Check server logs to ensure receiving calls
- Validate Output Interface configuration in WMS Cloud

## State Management and Bookmarks

Extractors maintain state to enable incremental extractions:

### OIC State Format

```json
{
  "bookmarks": {
    "integrations": {
      "last_modified": "2023-06-01T12:34:56Z"
    },
    "instances": {
      "execution_time": "2023-06-01T12:34:56Z"
    }
  }
}
```

### WMS State Format

```json
{
  "bookmarks": {
    "order_hdr": {
      "modified_date": "2023-06-01T12:34:56Z"
    },
    "allocations": {
      "allocation_time": "2023-06-01T12:34:56Z"
    }
  }
}
```

## API Response Examples

### OIC Integration Response

```json
{
  "integration_id": "WMS_ORDER_SYNC_01.00.0000",
  "integration_name": "WMS Order Synchronization",
  "status": "ACTIVE",
  "last_modified": "2023-06-01T10:00:00Z",
  "execution_count": 1250,
  "success_rate": 99.8
}
```

### WMS Order Header Response

```json
{
  "company_code": "YOURCO",
  "facility_code": "WH1",
  "order_nbr": "ORD12345",
  "order_type": "SO",
  "order_date": "2023-06-01T10:00:00",
  "destination": "STORE123",
  "status": "Created"
}
```

## Performance Optimization

### Batch Configuration

```yaml
config:
  batch_size: 1000          # Optimize for your data volume
  max_requests_per_minute: 100
  connection_timeout: 60
  request_timeout: 300
```

### Parallel Processing

```yaml
# Enable parallel extraction for multiple streams
config:
  stream_parallelism: 4
  batch_parallelism: 2
```

### Memory Management

```yaml
config:
  max_memory_usage: "2GB"
  enable_compression: true
  buffer_size: 8192
```

## Security Best Practices

### Credential Management

- Use environment variables for sensitive configuration
- Implement credential rotation policies
- Use least-privilege access principles

### Network Security

- Configure TLS/SSL for all connections
- Use VPN or private network connections when possible
- Implement IP whitelisting for webhook endpoints

### Audit and Monitoring

- Enable comprehensive logging
- Monitor extraction performance and failures
- Implement alerting for critical issues

## Integration Patterns

### Event-Driven Architecture

```yaml
# Real-time event processing
extraction_mode: "webhook"
processing:
  - validate_payload
  - transform_data
  - route_to_destination
  - send_acknowledgment
```

### Batch Processing

```yaml
# Scheduled batch processing
extraction_mode: "api"
schedule: "@daily"
processing:
  - extract_incremental
  - validate_data_quality
  - apply_transformations
  - load_to_warehouse
```

### Hybrid Approach

```yaml
# Combination of batch and real-time
initial_load:
  extraction_mode: "csv"
  schedule: "@once"
continuous_sync:
  extraction_mode: "webhook"
  schedule: "@continuous"
daily_reconciliation:
  extraction_mode: "api"
  schedule: "@daily"
```
