# target-oracle-oic

Singer target for Oracle Integration Cloud (OIC).

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `about`
* `stream-maps`
* `schema-flattening`
* `validate-records`

## Supported Streams

This target can receive and process the following streams:

- **connections**: Create or update OIC connections
- **integrations**: Import or update integrations (with .iar archive support)
- **packages**: Import packages (with .par archive support)
- **lookups**: Create or update lookup tables

## Configuration

### Required Configuration

- `base_url`: OIC instance base URL
- `oauth_client_id`: OAuth2 client ID from IDCS
- `oauth_client_secret`: OAuth2 client secret from IDCS
- `oauth_token_url`: IDCS token endpoint URL

### Optional Configuration

- `oauth_client_aud`: IDCS client audience URL for scope building
- `import_mode`: Import mode: 'create_only', 'update_only', or 'create_or_update' (default: 'create_or_update')
- `activate_integrations`: Automatically activate integrations after import (default: false)
- `validate_connections`: Validate connections before creating/updating (default: true)
- `archive_directory`: Directory to read integration archives from
- `request_timeout`: Request timeout in seconds (default: 30)
- `max_retries`: Maximum number of retries for failed requests (default: 3)

## Usage

You can use this target with any Singer tap that produces compatible streams:

```bash
# Using with tap-oracle-oic
tap-oracle-oic --config tap-config.json | target-oracle-oic --config target-config.json

# Using with Meltano
meltano run tap-oracle-oic target-oracle-oic
```

### Example Configuration

```json
{
  "base_url": "https://myinstance-region.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token",
  "import_mode": "create_or_update",
  "activate_integrations": true
}
```

## Development

```bash
poetry install
poetry run pytest
```

### Testing with Meltano

```bash
meltano add loader target-oracle-oic --from-ref target-oracle-oic.yml
meltano config target-oracle-oic set base_url "https://your-instance.integration.ocp.oraclecloud.com"
# ... set other required config
meltano run tap-oracle-oic target-oracle-oic
```
