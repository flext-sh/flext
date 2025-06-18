# API Reference

## TAP Streams

### Core Streams

#### IntegrationsStream
Extracts Oracle Integration Cloud integrations.

**Schema**:
- `id` (string): Integration identifier
- `name` (string): Integration name
- `version` (string): Integration version
- `status` (string): Current status (ACTIVE, CONFIGURED, etc.)
- `description` (string): Integration description
- `pattern` (string): Integration pattern type
- `created_by` (string): Creator username
- `created_time` (datetime): Creation timestamp
- `updated_by` (string): Last modifier username
- `updated_time` (datetime): Last update timestamp

#### ConnectionsStream
Extracts integration connections.

**Schema**:
- `id` (string): Connection identifier
- `name` (string): Connection name
- `adapter_type` (string): Adapter type identifier
- `status` (string): Connection status
- `description` (string): Connection description
- `properties` (object): Connection-specific properties

#### PackagesStream
Extracts integration packages.

**Schema**:
- `id` (string): Package identifier
- `name` (string): Package name
- `description` (string): Package description
- `integrations` (array): List of contained integrations

### Infrastructure Streams

#### AdaptersStream
Extracts available adapter types.

**Schema**:
- `id` (string): Adapter identifier
- `name` (string): Adapter name
- `version` (string): Adapter version
- `type` (string): Adapter type category

## Target Sinks

### ConnectionsSink
Creates or updates OIC connections.

**Supported Operations**:
- Create new connection
- Update existing connection
- Validate connection properties

### IntegrationsSink
Imports or updates integrations.

**Supported Operations**:
- Create integration from metadata
- Import integration from archive (.iar)
- Update integration properties

### PackagesSink
Imports packages.

**Supported Operations**:
- Import package from archive (.par)

### LookupsSink
Manages lookup tables.

**Supported Operations**:
- Create new lookup
- Update lookup rows
- Replace lookup data

## Extension Commands

### Lifecycle Management

#### activate
```bash
oracle_oic_extension invoke lifecycle:activate INTEGRATION_ID [VERSION]
```

#### deactivate
```bash
oracle_oic_extension invoke lifecycle:deactivate INTEGRATION_ID [VERSION]
```

#### status
```bash
oracle_oic_extension invoke lifecycle:status INTEGRATION_ID [VERSION]
```

### Monitoring

#### health
```bash
oracle_oic_extension invoke monitor:health [--detailed]
```

Returns:
- API health status
- Component health (connections, integrations, execution)
- Instance metrics

#### performance
```bash
oracle_oic_extension invoke monitor:performance [--window HOURS]
```

Returns:
- Execution counts
- Success/failure rates
- Average duration
- Throughput metrics

#### errors
```bash
oracle_oic_extension invoke monitor:errors [--window HOURS] [--integration INTEGRATION_ID]
```

Returns:
- Top error messages
- Error patterns
- Affected integrations
- Error frequency

#### usage
```bash
oracle_oic_extension invoke monitor:usage [--window DAYS]
```

Returns:
- Top integrations by usage
- Daily execution trends
- Unique integration count
- Average daily executions

## FLX Adapter Methods

### Connection Management

#### connect()
```python
await adapter.connect()
```
Establishes connection to OIC instance.

#### disconnect()
```python
await adapter.disconnect()
```
Closes connection and cleans up resources.

#### health_check()
```python
health = await adapter.health_check()
```
Returns adapter health status.

### Data Operations

#### get_integrations()
```python
integrations = await adapter.get_integrations(
    limit=100,
    offset=0,
    status="ACTIVE"
)
```

#### get_connections()
```python
connections = await adapter.get_connections(
    limit=100,
    offset=0
)
```

### Lifecycle Operations

#### activate_integration()
```python
result = await adapter.activate_integration(
    integration_id="MY_INTEGRATION",
    version="01.00.0000"
)
```

#### deactivate_integration()
```python
result = await adapter.deactivate_integration(
    integration_id="MY_INTEGRATION",
    version="01.00.0000"
)
```

## Configuration Schema

### Common Configuration

```json
{
  "base_url": "https://instance.integration.ocp.oraclecloud.com",
  "oauth_client_id": "client_id",
  "oauth_client_secret": "client_secret",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
  "oauth_client_aud": "optional_audience_url",
  "request_timeout": 30,
  "max_retries": 3
}
```

### TAP-Specific Configuration

```json
{
  "include_extended": false,
  "page_size": 100,
  "start_date": "2024-01-01T00:00:00Z",
  "stream_maps": {},
  "stream_map_config": {}
}
```

### Target-Specific Configuration

```json
{
  "import_mode": "create_or_update",
  "activate_integrations": false,
  "validate_connections": true,
  "archive_directory": "/path/to/archives"
}
```

## Error Codes

### Authentication Errors
- `401`: Invalid credentials or expired token
- `403`: Insufficient permissions

### API Errors
- `404`: Resource not found
- `409`: Resource conflict (duplicate)
- `422`: Validation error

### Network Errors
- `500`: Internal server error
- `502`: Bad gateway
- `503`: Service unavailable
- `504`: Gateway timeout
