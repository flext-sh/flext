# Usage Guide

## Getting Started

### Installation

```bash
# Install from PyPI
pip install flx-oracle-oic

# Install from source
git clone https://github.com/pyauto/flx-oracle-oic
cd flx-oracle-oic
poetry install
```

### Quick Start

1. Create configuration file:
```bash
cat > config.json << EOF
{
  "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token"
}
EOF
```

2. Discover available streams:
```bash
flx-oracle-oic tap discover --config config.json --output catalog.json
```

3. Extract data:
```bash
flx-oracle-oic tap extract --config config.json --catalog catalog.json --output data.jsonl
```

## Common Use Cases

### 1. Migration Between OIC Instances

Migrate integrations from development to production:

```bash
# Extract from dev
flx-oracle-oic tap extract \
  --config dev-config.json \
  --catalog catalog.json \
  --output dev-data.jsonl

# Load to prod
flx-oracle-oic target load \
  --config prod-config.json \
  --input dev-data.jsonl
```

### 2. Backup and Restore

Create backups of your integrations:

```bash
# Backup
flx-oracle-oic tap extract \
  --config config.json \
  --output backup-$(date +%Y%m%d).jsonl

# Restore
flx-oracle-oic target load \
  --config config.json \
  --input backup-20240101.jsonl
```

### 3. Selective Extraction

Extract only specific streams:

```bash
# Create custom catalog
cat > custom-catalog.json << EOF
{
  "streams": [
    {
      "tap_stream_id": "integrations",
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "inclusion": "available",
            "selected": true
          }
        }
      ]
    }
  ]
}
EOF

# Extract only integrations
flx-oracle-oic tap extract \
  --config config.json \
  --catalog custom-catalog.json \
  --output integrations.jsonl
```

### 4. Lifecycle Management

Manage integration lifecycle:

```bash
# Activate integration
flx-oracle-oic ext lifecycle activate MY_INTEGRATION \
  --config config.json \
  --version 01.00.0000

# Deactivate integration
flx-oracle-oic ext lifecycle deactivate MY_INTEGRATION \
  --config config.json

# Check status
flx-oracle-oic ext lifecycle status MY_INTEGRATION \
  --config config.json
```

### 5. Monitoring and Health Checks

Monitor your OIC instance:

```bash
# Health check
flx-oracle-oic ext monitor health \
  --config config.json \
  --detailed

# Performance metrics (last 48 hours)
flx-oracle-oic ext monitor performance \
  --config config.json \
  --window 48

# Error analysis
flx-oracle-oic ext monitor errors \
  --config config.json \
  --window 24

# Usage analytics (last 7 days)
flx-oracle-oic ext monitor usage \
  --config config.json \
  --window 7
```

### 6. Complete Pipeline

Run a complete extraction, transformation, and loading pipeline:

```bash
# Create pipeline config
cat > pipeline.json << EOF
{
  "tap": {
    "base_url": "https://dev.integration.ocp.oraclecloud.com",
    "oauth_client_id": "dev_client_id",
    "oauth_client_secret": "dev_secret",
    "oauth_token_url": "https://dev-idcs.identity.oraclecloud.com/oauth2/v1/token"
  },
  "target": {
    "base_url": "https://prod.integration.ocp.oraclecloud.com",
    "oauth_client_id": "prod_client_id",
    "oauth_client_secret": "prod_secret",
    "oauth_token_url": "https://prod-idcs.identity.oraclecloud.com/oauth2/v1/token",
    "activate_integrations": true
  }
}
EOF

# Run pipeline (dry run first)
flx-oracle-oic pipeline --config pipeline.json --dry-run

# Run actual pipeline
flx-oracle-oic pipeline --config pipeline.json
```

## Advanced Usage

### State Management

Use state files for incremental extraction:

```bash
# First run - creates state file
flx-oracle-oic tap extract \
  --config config.json \
  --state state.json \
  --output data1.jsonl

# Subsequent runs - uses state file
flx-oracle-oic tap extract \
  --config config.json \
  --state state.json \
  --output data2.jsonl
```

### Stream Maps

Transform data during extraction:

```json
{
  "stream_maps": {
    "integrations": {
      "id": "_value",
      "name": "_value | upper",
      "environment": "'PRODUCTION'"
    }
  }
}
```

### Parallel Processing

Extract multiple streams in parallel:

```bash
# Extract integrations
flx-oracle-oic tap extract \
  --config config.json \
  --catalog integrations-catalog.json \
  --output integrations.jsonl &

# Extract connections
flx-oracle-oic tap extract \
  --config config.json \
  --catalog connections-catalog.json \
  --output connections.jsonl &

# Wait for all
wait
```

### Programmatic Usage

Use in Python scripts:

```python
import asyncio
from flx_oracle_oic.adapter import OracleOICAdapter

async def main():
    # Create adapter
    adapter = OracleOICAdapter(
        base_url="https://instance.integration.ocp.oraclecloud.com",
        oauth_client_id="client_id",
        oauth_client_secret="secret",
        oauth_token_url="https://idcs.identity.oraclecloud.com/oauth2/v1/token"
    )

    # Connect
    await adapter.connect()

    # Get integrations
    integrations = await adapter.get_integrations(status="ACTIVE")

    # Process each integration
    for integration in integrations:
        print(f"Processing {integration['id']}")

        # Get details
        details = await adapter.get_integration_details(
            integration['id'],
            integration['version']
        )

        # Do something with details
        process_integration(details)

    # Disconnect
    await adapter.disconnect()

# Run
asyncio.run(main())
```

## Troubleshooting

### Authentication Issues

```bash
# Test authentication
curl -X POST $OAUTH_TOKEN_URL \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "scope=$BASE_URL/urn:opc:resource:consumer::all"
```

### Network Issues

```bash
# Test connectivity
curl -I $BASE_URL/ic/api/integration/v1/integrations

# Use verbose mode
flx-oracle-oic tap discover --config config.json -v
```

### Performance Tuning

```json
{
  "page_size": 200,
  "request_timeout": 60,
  "max_retries": 5,
  "backoff_factor": 2
}
```

## Best Practices

1. **Always use catalog files** for production extractions
2. **Test in dry-run mode** before running pipelines
3. **Use state files** for incremental updates
4. **Monitor performance** and adjust page_size
5. **Validate configurations** before running
6. **Keep logs** for troubleshooting
7. **Use version control** for configurations
8. **Document your pipelines** for team members
