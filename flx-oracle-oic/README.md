# flx-oracle-oic

Unified FLX adapter and CLI for Oracle Integration Cloud operations.

This package combines:

- **tap-oracle-oic**: Singer tap for data extraction
- **target-oracle-oic**: Singer target for data loading
- **oracle-oic-ext**: Meltano extension for lifecycle and monitoring
- **FLX adapter**: Native FLX integration

## Features

### Data Operations

- Extract data from Oracle OIC (integrations, connections, packages, etc.)
- Load data into Oracle OIC (create/update integrations, connections, etc.)
- Full Singer protocol support with catalog and state management

### Lifecycle Management

- Activate/deactivate integrations
- Bulk operations support
- Integration status monitoring

### Monitoring & Analytics

- Health checks
- Performance metrics
- Error analysis
- Usage analytics

### FLX Integration

- Native FLX adapter for hexagonal architecture
- Async operations support
- Built-in retry and error handling

## Installation

```bash
pip install flx-oracle-oic
```

## Configuration

Create a configuration file (`config.json`):

```json
{
  "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token",
  "page_size": 100,
  "request_timeout": 30
}
```

## Usage

### TAP Operations (Data Extraction)

```bash
# Discover available streams
flx-oracle-oic tap discover --config config.json --output catalog.json

# Extract data
flx-oracle-oic tap extract --config config.json --catalog catalog.json --output data.jsonl

# Extract with state management
flx-oracle-oic tap extract --config config.json --state state.json --output data.jsonl
```

### Target Operations (Data Loading)

```bash
# Load data from file
flx-oracle-oic target load --config config.json --input data.jsonl

# Load data from stdin (pipe from tap)
flx-oracle-oic tap extract --config config.json | flx-oracle-oic target load --config config.json
```

### Extension Operations

#### Lifecycle Management

```bash
# Activate an integration
flx-oracle-oic ext lifecycle activate INTEGRATION_ID --config config.json

# Deactivate an integration
flx-oracle-oic ext lifecycle deactivate INTEGRATION_ID --version 01.00.0001 --config config.json

# Check integration status
flx-oracle-oic ext lifecycle status INTEGRATION_ID --config config.json
```

#### Monitoring

```bash
# Check instance health
flx-oracle-oic ext monitor health --config config.json --detailed

# Get performance metrics
flx-oracle-oic ext monitor performance --config config.json --window 48

# Analyze errors
flx-oracle-oic ext monitor errors --config config.json --window 24

# Get usage analytics
flx-oracle-oic ext monitor usage --config config.json --window 7
```

### FLX Adapter Operations

```bash
# Check adapter status
flx-oracle-oic adapter status --config config.json
```

### Pipeline Operations

Run a complete ETL pipeline:

```bash
# Create pipeline configuration
cat > pipeline.json << EOF
{
  "tap": {
    "base_url": "https://source.integration.ocp.oraclecloud.com",
    "oauth_client_id": "source_client_id",
    "oauth_client_secret": "source_client_secret",
    "oauth_token_url": "https://source-idcs.identity.oraclecloud.com/oauth2/v1/token"
  },
  "target": {
    "base_url": "https://target.integration.ocp.oraclecloud.com",
    "oauth_client_id": "target_client_id",
    "oauth_client_secret": "target_client_secret",
    "oauth_token_url": "https://target-idcs.identity.oraclecloud.com/oauth2/v1/token",
    "activate_integrations": true
  },
  "transformations": {
    "rename_prefix": "MIGRATED_"
  }
}
EOF

# Run pipeline (dry run)
flx-oracle-oic pipeline --config pipeline.json --dry-run

# Run pipeline
flx-oracle-oic pipeline --config pipeline.json
```

### Utility Commands

```bash
# Validate configuration
flx-oracle-oic validate-config --config config.json

# Show version
flx-oracle-oic --version
```

## Advanced Usage

### Programmatic Usage

```python
from flx_oracle_oic.adapter import OracleOICAdapter

# Create adapter
adapter = OracleOICAdapter(
    base_url="https://your-instance.integration.ocp.oraclecloud.com",
    oauth_client_id="client_id",
    oauth_client_secret="client_secret",
    oauth_token_url="https://idcs.identity.oraclecloud.com/oauth2/v1/token"
)

# Use adapter
async def main():
    await adapter.connect()

    # Get integrations
    integrations = await adapter.get_integrations()

    # Activate integration
    await adapter.activate_integration("MY_INTEGRATION", "01.00.0000")

    await adapter.disconnect()
```

### Meltano Integration

```yaml
project_id: my-project

extractors:
  - name: tap-oracle-oic
    pip_url: flx-oracle-oic
    executable: flx-oracle-oic
    capabilities:
      - catalog
      - discover
      - state
    settings:
      - name: base_url
        kind: string
      - name: oauth_client_id
        kind: string
      - name: oauth_client_secret
        kind: password

loaders:
  - name: target-oracle-oic
    pip_url: flx-oracle-oic
    executable: flx-oracle-oic
    settings:
      - name: base_url
        kind: string
      - name: oauth_client_id
        kind: string
      - name: oauth_client_secret
        kind: password

utilities:
  - name: oracle-oic-ext
    pip_url: flx-oracle-oic
    executable: flx-oracle-oic
    commands:
      lifecycle: "flx-oracle-oic ext lifecycle"
      monitor: "flx-oracle-oic ext monitor"
```

## Architecture

```
flx-oracle-oic/
├── tap_oracle_oic/      # Singer tap (extraction)
├── target_oracle_oic/   # Singer target (loading)
├── oracle_oic_ext/      # Meltano extension (lifecycle/monitoring)
└── flx_oracle_oic/      # FLX adapter and unified CLI
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

## Documentation

For detailed documentation on each component:

- [TAP Documentation](../tap-oracle-oic/README.md)
- [Target Documentation](../target-oracle-oic/README.md)
- [Extension Documentation](../oracle-oic-ext/README.md)
- [API Reference](docs/api-reference.md)

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License

Apache 2.0
