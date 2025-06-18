# tap-oracle-oic

Singer tap for Oracle Integration Cloud (OIC).

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `name`
* `schema`
* `record`
* `activate_version`

## Supported Streams

### Core Streams (Always Available)
- **integrations**: Oracle Integration Cloud integrations
- **connections**: Integration connections and adapters
- **packages**: Integration packages
- **lookups**: Lookup tables
- **libraries**: JavaScript and other libraries
- **certificates**: Security certificates

### Infrastructure Streams (Optional)
- **adapters**: Available adapter types
- **agent_groups**: Integration agent groups

## Configuration

### Required Configuration

- `base_url`: OIC instance base URL (e.g., https://myinstance-region.integration.ocp.oraclecloud.com)
- `oauth_client_id`: OAuth2 client ID from IDCS application
- `oauth_client_secret`: OAuth2 client secret from IDCS application
- `oauth_token_url`: IDCS token endpoint URL

### Optional Configuration

- `oauth_client_aud`: IDCS client audience URL for scope building
- `include_extended`: Include infrastructure streams (default: false)
- `page_size`: Number of records per page (default: 100)
- `request_timeout`: Request timeout in seconds (default: 30)
- `max_retries`: Maximum number of retries for failed requests (default: 3)
- `start_date`: Start date for incremental replication
- `stream_maps`: Configure stream maps for transformation
- `stream_map_config`: Additional stream map configuration

## Usage

### Standalone

```bash
# Install
pip install tap-oracle-oic

# Discover available streams
tap-oracle-oic --config config.json --discover > catalog.json

# Run tap
tap-oracle-oic --config config.json --catalog catalog.json
```

### With Meltano

```bash
# Add to Meltano project
meltano add extractor tap-oracle-oic

# Configure
meltano config tap-oracle-oic set base_url "https://your-instance.integration.ocp.oraclecloud.com"
meltano config tap-oracle-oic set oauth_client_id "your_client_id"
meltano config tap-oracle-oic set oauth_client_secret "your_client_secret"
meltano config tap-oracle-oic set oauth_token_url "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token"

# Run
meltano run tap-oracle-oic target-jsonl
```

### Example Configuration

```json
{
  "base_url": "https://myinstance-region.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token",
  "include_extended": true,
  "page_size": 100,
  "start_date": "2024-01-01T00:00:00Z"
}
```

## Authentication

This tap uses OAuth2 authentication with Oracle Identity Cloud Service (IDCS). You need to:

1. Create an IDCS application
2. Grant it access to your OIC instance
3. Use the client ID and secret in the tap configuration

## Advanced Features

For advanced features like lifecycle management, monitoring, and artifact extraction, use the `oracle-oic-ext` Meltano extension:

```bash
meltano add utility oracle-oic-ext
```

## Development

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black src/
poetry run isort src/

# Lint
poetry run ruff src/

# Type check
poetry run mypy src/
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License

Apache 2.0
