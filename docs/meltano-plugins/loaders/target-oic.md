# target-oic

This Meltano loader for Oracle Integration Cloud (OIC) allows sending data to integration endpoints in OIC from any Meltano/Singer extractor.

## Features

- Send data to REST integrations in Oracle Integration Cloud
- Support for OAuth2 and Basic Auth authentication
- Data transformation from Singer format to OIC expected format
- Record batching for better performance
- Flexible field mapping with template support
- Delivery status monitoring

## Requirements

- Python 3.8 or higher
- Access to Oracle Integration Cloud (OIC) v3
- OAuth2 or Basic Auth credentials configured
- REST endpoints in OIC configured to receive data

## Installation

```bash
# Via pip
pip install target-oic

# Via Meltano
meltano add loader target-oic
```

## Configuration

### Basic Configuration

```yaml
# meltano.yml
plugins:
  loaders:
    - name: target-oic
      variant: custom
      pip_url: target-oic
      config:
        oic_url: https://instance-name.integration.ocp.oraclecloud.com
        auth_method: oauth2
        client_id: YOUR_CLIENT_ID
        client_secret: YOUR_CLIENT_SECRET
        idcs_url: idcs-xxxx.identity.oraclecloud.com
        resource_aud: https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
        api_aud: https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/
        endpoint_path: /ic/api/integration/v1/flows/rest/WMS_ORDER_INBOUND/1.0/orders
```

### Advanced Configuration

```yaml
# Complete config.json
{
  "oic_url": "https://instance-name.integration.ocp.oraclecloud.com",
  "auth_method": "oauth2",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "idcs_url": "idcs-xxxx.identity.oraclecloud.com",
  "resource_aud": "https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all",
  "api_aud": "https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/",
  "endpoint_path": "/ic/api/integration/v1/flows/rest/WMS_ORDER_INBOUND/1.0/orders",
  "batch_size": 100,
  "batch_wait_limit_seconds": 60,
  "request_timeout": 300,
  "username": null, # For Basic Auth
  "password": null, # For Basic Auth
  "additional_headers":
    { "Content-Type": "application/json", "X-Custom-Header": "value" },
  "stream_maps":
    {
      "order_hdr":
        {
          "endpoint_path": "/ic/api/integration/v1/flows/rest/WMS_ORDER_INBOUND/1.0/orders",
          "method": "POST",
          "template": { "order_hdr": "{{ record }}" },
        },
      "order_dtl":
        {
          "endpoint_path": "/ic/api/integration/v1/flows/rest/WMS_ORDER_DETAIL_INBOUND/1.0/orderDetails",
          "method": "POST",
          "template": { "order_dtl": "{{ record }}" },
        },
      "allocations":
        {
          "endpoint_path": "/ic/api/integration/v1/flows/rest/WMS_ALLOC_INBOUND/1.0/allocations",
          "method": "POST",
          "template": { "allocation": "{{ record }}" },
        },
    },
  "default_stream_map": { "method": "POST", "template": "{{ record }}" },
  "retry_count": 3,
  "retry_backoff_seconds": 10,
  "emit_state_on_batch": true,
  "validate_records": true,
}
```

### Configuration for Basic Auth

```yaml
# For Basic Auth
plugins:
  loaders:
    - name: target-oic
      variant: custom
      pip_url: target-oic
      config:
        oic_url: https://instance-name.integration.ocp.oraclecloud.com
        auth_method: basic
        username: YOUR_USERNAME
        password: YOUR_PASSWORD
        endpoint_path: /ic/api/integration/v1/flows/rest/WMS_ORDER_INBOUND/1.0/orders
```

## Stream Mapping

The loader allows configuring different endpoints for each stream:

```yaml
config:
  stream_maps:
    "order_hdr": # Source stream name
      endpoint_path: "/ic/api/integration/v1/flows/rest/WMS_ORDER_INBOUND/1.0/orders"
      method: "POST"
      template: # Template to transform data before sending
        order_hdr: "{{ record }}"
```

This allows sending different streams to distinct OIC endpoints, with specific transformations for each one.

## Templates

You can use Jinja2 templates to format data before sending:

```yaml
config:
  stream_maps:
    "order_hdr":
      template:
        order:
          header: "{{ record }}"
          meta:
            source: "meltano"
            timestamp: "{{ execution_time }}"
```

Available variables in templates:

- `record`: The current record
- `stream`: Stream name
- `execution_time`: Execution timestamp
- `batch_id`: Current batch ID

## Batch Control

To improve performance, target-oic groups records into batches:

```yaml
config:
  batch_size: 100 # Number of records per batch
  batch_wait_limit_seconds: 60 # Maximum wait time to complete a batch
```

## Example with Meltano

### Basic Pipeline

```bash
# Extract data from Oracle DB and send to OIC integration
meltano elt tap-oracle-db target-oic --job-id=db_to_oic
```

### Filtered Pipeline

```bash
# Extract only specific tables and send to OIC
meltano elt tap-oracle-db target-oic --select="WMSSTAGE.ORDER_HDR_STAGE" --job-id=orders_to_oic
```

### Configuration with Scheduling

```yaml
# meltano.yml
schedules:
  - name: db_to_oic_daily
    extractor: tap-oracle-db
    loader: target-oic
    interval: "@daily"
    start_date: 2023-01-01
```

## Project Structure

```
src/target_oic/
├── __init__.py
├── client.py         # OIC API client
├── sinks.py          # Data collector implementation
├── target.py         # Main target implementation
├── auth/
│   ├── __init__.py
│   ├── oauth2.py     # OAuth2 authentication
│   └── basic.py      # Basic authentication
└── utils/
    ├── __init__.py
    ├── templates.py  # Template processing
    └── exceptions.py # Custom exceptions
```

## Error Handling

The loader implements comprehensive error handling:

- Authentication failures with automatic token refresh
- Network errors with exponential backoff retry
- Data validation errors with detailed logging
- Integration endpoint failures with status tracking

## Monitoring

Available metrics and logs:

- Successful deliveries count
- Failed deliveries with error details
- Processing latency measurements
- Authentication token refresh events

## Testing

```bash
# Install development dependencies
poetry install --dev

# Run tests
poetry run pytest

# Run with specific configuration
poetry run target-oic --config=config.json --input=input.jsonl
```

## Development

### Local Development

```bash
# Install in development mode
pip install -e .

# Run with debug logging
LOG_LEVEL=DEBUG target-oic --config=config.json
```

### Custom Templates

Create custom templates for specific use cases:

```yaml
config:
  stream_maps:
    "custom_stream":
      template:
        data: "{{ record }}"
        metadata:
          processed_at: "{{ execution_time }}"
          source_system: "meltano"
          target_system: "oic"
```

## Security Considerations

- Store credentials in environment variables or secure configuration
- Use OAuth2 over Basic Auth when possible
- Validate SSL certificates in production
- Monitor authentication token expiration and refresh
