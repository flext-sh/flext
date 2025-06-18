# oracle-oic-ext

Meltano extension for Oracle Integration Cloud lifecycle management and monitoring.

Built with the [Meltano Extension Developer Kit (EDK)](https://github.com/meltano/edk).

## Features

- **Lifecycle Management**: Activate, deactivate, and validate integrations
- **Monitoring**: Health checks, performance metrics, error analysis
- **Advanced Extraction**: Extract artifacts, logs, and metadata
- **Bulk Operations**: Process multiple integrations at once
- **Usage Analytics**: Track integration usage patterns

## Commands

### Lifecycle Management

```bash
# Activate an integration
meltano invoke oracle-oic-ext lifecycle:activate INTEGRATION_ID [VERSION]

# Deactivate an integration
meltano invoke oracle-oic-ext lifecycle:deactivate INTEGRATION_ID [VERSION]

# Check integration status
meltano invoke oracle-oic-ext lifecycle:status INTEGRATION_ID [VERSION]

# Bulk activate integrations
meltano invoke oracle-oic-ext lifecycle:bulk-activate --file integrations.json
```

### Monitoring

```bash
# Check OIC instance health
meltano invoke oracle-oic-ext monitor:health [--detailed]

# Get performance metrics
meltano invoke oracle-oic-ext monitor:performance [--window HOURS]

# Analyze error patterns
meltano invoke oracle-oic-ext monitor:errors [--window HOURS] [--integration INTEGRATION_ID]

# Get usage analytics
meltano invoke oracle-oic-ext monitor:usage [--window DAYS]
```

### Advanced Extraction

```bash
# Extract integration artifacts
meltano invoke oracle-oic-ext extract:artifacts --output-dir ./artifacts [--integration INTEGRATION_ID]

# Extract execution logs
meltano invoke oracle-oic-ext extract:logs --output-dir ./logs [--window HOURS]

# Extract comprehensive metadata
meltano invoke oracle-oic-ext extract:metadata --output-dir ./metadata
```

## Configuration

### Required Configuration

- `base_url`: OIC instance base URL
- `oauth_client_id`: OAuth2 client ID from IDCS
- `oauth_client_secret`: OAuth2 client secret from IDCS
- `oauth_token_url`: IDCS token endpoint URL

### Example meltano.yml

```yaml
project_id: your-project-id
environments:
  - name: dev
extensions:
  - name: oracle-oic-ext
    namespace: oracle_oic_ext
    pip_url: oracle-oic-ext
    config:
      base_url: https://your-instance.integration.ocp.oraclecloud.com
      oauth_client_id: ${ORACLE_OIC_CLIENT_ID}
      oauth_client_secret: ${ORACLE_OIC_CLIENT_SECRET}
      oauth_token_url: https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token
```

## Installation

### Using Meltano

```bash
meltano add utility oracle-oic-ext
```

### Using pip

```bash
pip install oracle-oic-ext
```

## Development

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black oracle_oic_ext/
poetry run isort oracle_oic_ext/

# Lint code
poetry run ruff oracle_oic_ext/

# Type check
poetry run mypy oracle_oic_ext/
```

## Integration File Format

For bulk operations, use a JSON file with the following format:

```json
[
  {
    "id": "INTEGRATION_ID_1",
    "version": "01.00.0000"
  },
  {
    "id": "INTEGRATION_ID_2",
    "version": "01.00.0001"
  }
]
```
