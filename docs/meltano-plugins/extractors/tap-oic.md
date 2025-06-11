# tap-oic

This Meltano extractor for Oracle Integration Cloud (OIC) allows extracting data from OIC integrations and flows for use in data pipelines.

## Features

- OIC integration metadata extraction
- Integration execution status retrieval
- Integration events and logs capture
- Payload data extraction processed by OIC
- Support for pagination and incremental extraction

## Requirements

- Python 3.8 or higher
- Access to Oracle Integration Cloud (OIC) v3
- OAuth2 or Basic Auth credentials configured

## Installation

```bash
# Via pip
pip install tap-oic

# Via Meltano
meltano add extractor tap-oic
```

## Configuration

### Basic Configuration

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

### Advanced Configuration

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

### Configuration for Basic Auth

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

## Available Streams

This extractor provides the following streams:

- **integrations**: Metadata of all integrations
- **instances**: Integration execution instances
- **logs**: Detailed execution logs
- **connections**: Connections configured in OIC
- **lookups**: Available lookups
- **payloads**: Input/output payloads of integrations (optional)

## Data Filtering and Selection

You can filter integrations by patterns (using globbing), for example `WMS_*` to capture only WMS-related integrations:

```yaml
config:
  integration_filter: "WMS_*"
```

## Integration with Meltano Workflow

This extractor works seamlessly with Meltano, enabling:

1. Extract data from OIC for analysis and monitoring
2. Feed operational dashboards
3. Integrate with other systems via appropriate loaders
4. Monitor integration health and performance

## Complete Pipeline Example

```bash
# Extract data from OIC and load into Oracle Database
meltano elt tap-oic target-oracle --job-id=oic_monitoring

# Extract only WMS integrations and load into Oracle
meltano elt tap-oic target-oracle --select="integrations" --job-id=wms_integrations
```

## Development

This plugin was developed using the [Meltano SDK](https://sdk.meltano.com/) to ensure compatibility and follow best practices for extractor development.

### Code Structure

```
tap_oic/
├── __init__.py
├── auth.py        # Authentication logic (OAuth2, Basic)
├── client.py      # HTTP client for OIC API
├── streams.py     # Data stream definitions
└── tap.py         # Main extractor class
```

## Troubleshooting

### Authentication Error

Make sure that:

- OAuth2 credentials are correct
- OAuth2 client has adequate permissions in IDCS
- resource_aud and api_aud formats are correct (no slash between port and "urn" in resource_aud)

### Timeouts with Large Volumes

Increase `request_timeout` to handle long API calls:

```yaml
config:
  request_timeout: 600  # 10 minutes
```

### Rate Limiting

OIC may have request rate limitations. Configure:

```yaml
config:
  max_requests_per_minute: 60
```

## Performance Considerations

- Use `integration_filter` to limit scope when possible
- Configure appropriate `batch_size` for optimal performance
- Monitor memory usage when extracting large payloads
- Consider incremental extraction for frequent updates

## Security Notes

- Store credentials in environment variables or secure configuration
- Use OAuth2 over Basic Auth when possible
- Validate SSL certificates in production
- Monitor authentication token expiration and refresh

## Monitoring and Observability

The extractor provides detailed logging for:

- Authentication events
- API request/response cycles
- Error conditions and retry attempts
- Data extraction progress and statistics
