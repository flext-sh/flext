# tap-oracle-wms

Singer tap for Oracle Warehouse Management System (WMS) Cloud, built with the [Singer SDK](https://sdk.meltano.com).

## Features

- **Dynamic Entity Discovery**: Automatically discovers all available WMS entities via the `/entity` endpoint
- **Dynamic Schema Generation**: Generates Singer schemas from WMS entity metadata - no hardcoded schemas
- **Flexible Authentication**: Supports both Basic Authentication and OAuth2
- **Advanced Filtering**: Entity-specific and global filtering capabilities
- **Optimized Pagination**: Support for both offset and cursor-based pagination
- **Field Selection**: Select specific fields to optimize data transfer
- **Incremental Extraction**: Track state for efficient incremental syncs
- **Enterprise Ready**: Production-grade error handling, retries, and logging

## Installation

### Install from PyPI

```bash
pip install tap-oracle-wms
```

### Install from Source

```bash
git clone https://github.com/your-org/tap-oracle-wms.git
cd tap-oracle-wms
pip install -e .
```

### Install with Poetry

```bash
poetry install
```

## Configuration

### Required Settings

| Setting | Type | Description |
|---------|------|-------------|
| `base_url` | string | Oracle WMS instance URL (e.g., `https://instance.wms.ocs.oraclecloud.com/tenant`) |
| `auth_method` | string | Authentication method: `basic` or `oauth2` |

### Authentication Settings

#### Basic Authentication

| Setting | Type | Description |
|---------|------|-------------|
| `username` | string | WMS username |
| `password` | string | WMS password |

#### OAuth2 Authentication

| Setting | Type | Description |
|---------|------|-------------|
| `oauth_client_id` | string | OAuth2 client ID |
| `oauth_client_secret` | string | OAuth2 client secret |
| `oauth_token_url` | string | OAuth2 token endpoint URL |
| `oauth_scope` | string | OAuth2 scope (optional) |

### Optional Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `company_code` | string | `*` | WMS company code for context headers (`*` = all companies) |
| `facility_code` | string | `*` | WMS facility code for context headers (`*` = all facilities) |
| `start_date` | string | null | Start date for data extraction (ISO 8601 format) |
| `entities` | array | [] | Specific entities to extract (empty = all entities) |
| `excluded_entities` | array | [] | Entities to exclude from extraction |
| `page_size` | integer | 100 | Number of records per page |
| `pagination_mode` | string | offset | Pagination mode: `offset` or `cursor` |
| `max_pages_per_stream` | integer | null | Maximum pages to extract per stream |
| `request_timeout` | integer | 30 | Request timeout in seconds |
| `retry_limit` | integer | 3 | Number of retries for failed requests |
| `schema_discovery_method` | string | auto | Schema discovery: `auto`, `describe`, or `sample` |
| `log_level` | string | INFO | Logging level |

## Usage

### Discover Available Entities

```bash
tap-oracle-wms --config config.json --discover > catalog.json
```

### Run a Sync

```bash
tap-oracle-wms --config config.json --catalog catalog.json
```

### Incremental Sync with State

```bash
tap-oracle-wms --config config.json --catalog catalog.json --state state.json
```

### Example Configuration

```json
{
  "base_url": "https://your-instance.wms.ocs.oraclecloud.com/your-tenant",
  "auth_method": "basic",
  "username": "${WMS_USERNAME}",
  "password": "${WMS_PASSWORD}",
  "company_code": "DEMO",
  "facility_code": "DC01",
  "start_date": "2024-01-01T00:00:00Z",
  "page_size": 1000,
  "pagination_mode": "cursor",
  "entities": ["item", "location", "inventory", "order_hdr", "order_dtl"]
}
```

## Development

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)
- Make (for development commands)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/tap-oracle-wms.git
cd tap-oracle-wms

# Install development dependencies
make install-dev

# Set up pre-commit hooks
make setup-pre-commit
```

### Running Tests

```bash
# Run unit tests
make test

# Run all tests with coverage
make coverage

# Run integration tests (requires WMS instance)
make test-integration
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all checks
make check
```

### Building Documentation

```bash
# Build docs
make docs

# Serve docs locally
make serve-docs
```

## Advanced Usage

### Filtering Entities

```json
{
  "entities": ["inventory", "order_hdr"],
  "entity_filters": {
    "inventory": {
      "on_hand_qty__gt": 0,
      "location_id__startswith": "A"
    },
    "order_hdr": {
      "status__in": "PENDING,PROCESSING",
      "order_date__gte": "2024-01-01T00:00:00Z"
    }
  }
}
```

### Field Selection

```json
{
  "field_selection": {
    "inventory": ["id", "item_id", "location_id", "on_hand_qty", "allocated_qty"],
    "order_hdr": ["id", "order_nbr", "status", "order_date", "customer_id"]
  }
}
```

### Performance Optimization

```json
{
  "pagination_mode": "cursor",
  "page_size": 1000,
  "request_concurrency": 5,
  "field_selection": {
    "large_entity": ["id", "key_field_1", "key_field_2"]
  }
}
```

## Integration with Meltano

Add to your `meltano.yml`:

```yaml
project_id: your-project-id
plugins:
  extractors:
  - name: tap-oracle-wms
    namespace: tap_oracle_wms
    pip_url: tap-oracle-wms
    capabilities:
    - catalog
    - discover
    - state
    settings:
    - name: base_url
      kind: string
      description: Oracle WMS instance URL
    - name: auth_method
      kind: options
      options:
      - basic
      - oauth2
    - name: username
      kind: string
      description: WMS username (for basic auth)
    - name: password
      kind: password
      description: WMS password (for basic auth)
    config:
      base_url: ${WMS_BASE_URL}
      auth_method: basic
      username: ${WMS_USERNAME}
      password: ${WMS_PASSWORD}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify credentials are correct
   - Check if OAuth2 token URL is accessible
   - Ensure user has API access permissions

2. **Entity Discovery Fails**
   - Verify base URL is correct
   - Check if `/entity` endpoint is accessible
   - Ensure user has permission to list entities

3. **Schema Generation Issues**
   - Try different `schema_discovery_method` settings
   - Check if entity has describe endpoint available
   - Verify sample data is available for the entity

4. **Performance Issues**
   - Use cursor pagination for large datasets
   - Increase page size (up to 1000)
   - Use field selection to reduce data transfer
   - Enable request concurrency

### Debug Mode

Enable debug logging:

```json
{
  "log_level": "DEBUG"
}
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-org/tap-oracle-wms/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/tap-oracle-wms/discussions)

## Acknowledgments

- Built with [Singer SDK](https://sdk.meltano.com)
- Inspired by the Singer community
- Oracle WMS REST API documentation
