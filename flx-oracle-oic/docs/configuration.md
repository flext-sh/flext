# Configuration Guide

## Overview

The flx-oracle-oic package uses a unified configuration approach that works across all components (TAP, Target, Extension, and FLX adapter).

## Authentication Configuration

### Required Fields

```json
{
  "base_url": "https://your-instance.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token"
}
```

### Optional Authentication Fields

```json
{
  "oauth_client_aud": "https://your-instance.integration.ocp.oraclecloud.com:443/urn:opc:resource:consumer::all"
}
```

## Component-Specific Configuration

### TAP Configuration

```json
{
  "base_url": "https://source.integration.ocp.oraclecloud.com",
  "oauth_client_id": "source_client_id",
  "oauth_client_secret": "source_client_secret",
  "oauth_token_url": "https://source-idcs.identity.oraclecloud.com/oauth2/v1/token",

  "include_extended": true,
  "page_size": 100,
  "request_timeout": 30,
  "max_retries": 3,
  "start_date": "2024-01-01T00:00:00Z",

  "stream_maps": {
    "integrations": {
      "id": "_value",
      "integration_id": "id"
    }
  },
  "stream_map_config": {
    "datetime_error_treatment": "max"
  }
}
```

### Target Configuration

```json
{
  "base_url": "https://target.integration.ocp.oraclecloud.com",
  "oauth_client_id": "target_client_id",
  "oauth_client_secret": "target_client_secret",
  "oauth_token_url": "https://target-idcs.identity.oraclecloud.com/oauth2/v1/token",

  "import_mode": "create_or_update",
  "activate_integrations": true,
  "validate_connections": true,
  "archive_directory": "/path/to/iar/files",
  "request_timeout": 60,
  "max_retries": 5
}
```

### Extension Configuration

```json
{
  "base_url": "https://instance.integration.ocp.oraclecloud.com",
  "oauth_client_id": "client_id",
  "oauth_client_secret": "client_secret",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",

  "lifecycle_force_operations": false,
  "monitoring_window_hours": 24,
  "extract_artifacts": true,
  "artifact_directory": "./artifacts"
}
```

## Environment Variables

All configuration values can be set via environment variables:

```bash
export TAP_ORACLE_OIC_BASE_URL="https://instance.integration.ocp.oraclecloud.com"
export TAP_ORACLE_OIC_OAUTH_CLIENT_ID="your_client_id"
export TAP_ORACLE_OIC_OAUTH_CLIENT_SECRET="your_client_secret"
export TAP_ORACLE_OIC_OAUTH_TOKEN_URL="https://idcs.identity.oraclecloud.com/oauth2/v1/token"
```

## Meltano Configuration

### meltano.yml

```yaml
version: 1
default_environment: dev
project_id: oic-integration

environments:
- name: dev
  config:
    extractors:
      tap-oracle-oic:
        base_url: ${OIC_DEV_BASE_URL}
        oauth_client_id: ${OIC_DEV_CLIENT_ID}
        oauth_client_secret: ${OIC_DEV_CLIENT_SECRET}
        oauth_token_url: ${OIC_DEV_TOKEN_URL}

- name: prod
  config:
    extractors:
      tap-oracle-oic:
        base_url: ${OIC_PROD_BASE_URL}
        oauth_client_id: ${OIC_PROD_CLIENT_ID}
        oauth_client_secret: ${OIC_PROD_CLIENT_SECRET}
        oauth_token_url: ${OIC_PROD_TOKEN_URL}

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
    env: OIC_BASE_URL
  - name: oauth_client_id
    kind: string
    env: OIC_CLIENT_ID
  - name: oauth_client_secret
    kind: password
    env: OIC_CLIENT_SECRET
  - name: oauth_token_url
    kind: string
    env: OIC_TOKEN_URL
  select:
  - integrations.*
  - connections.*
  - packages.*

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
  - name: oauth_token_url
    kind: string
  - name: import_mode
    kind: options
    options:
    - create_only
    - update_only
    - create_or_update
```

## Pipeline Configuration

### pipeline.json

```json
{
  "tap": {
    "base_url": "https://source.integration.ocp.oraclecloud.com",
    "oauth_client_id": "source_client_id",
    "oauth_client_secret": "source_client_secret",
    "oauth_token_url": "https://source-idcs.identity.oraclecloud.com/oauth2/v1/token",
    "include_extended": true,
    "page_size": 200
  },
  "transformations": {
    "rename_prefix": "MIGRATED_",
    "exclude_patterns": ["TEST_*", "TEMP_*"],
    "status_filter": ["ACTIVE", "CONFIGURED"]
  },
  "target": {
    "base_url": "https://target.integration.ocp.oraclecloud.com",
    "oauth_client_id": "target_client_id",
    "oauth_client_secret": "target_client_secret",
    "oauth_token_url": "https://target-idcs.identity.oraclecloud.com/oauth2/v1/token",
    "import_mode": "create_or_update",
    "activate_integrations": false,
    "validate_connections": true
  }
}
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Rotate credentials** regularly
4. **Use least privilege** - grant only necessary permissions
5. **Enable audit logging** in OIC
6. **Use HTTPS only** - never disable SSL verification
7. **Store secrets securely** using tools like:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Kubernetes Secrets

## Configuration Validation

Use the validate-config command to check your configuration:

```bash
flx-oracle-oic validate-config --config config.json
```

This will verify:
- Required fields are present
- URLs use HTTPS protocol
- JSON is valid
- Component-specific requirements
