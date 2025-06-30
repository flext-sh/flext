# JWT Service Guide - Authentication Guide

> **Function**: JWT authentication service implementation | **Audience**: Security engineers, developers | **Status**: Production-Ready

[![JWT](https://img.shields.io/badge/auth-jwt-green.svg)](https://jwt.io/)
[![OAuth2](https://img.shields.io/badge/oauth2-compliant-blue.svg)](https://oauth.net/2/)
[![Security](https://img.shields.io/badge/security-production-red.svg)](../security/index.md)

**Complete guide for implementing and using the FLEXT JWT Service for OAuth2 authentication and token management**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Section**: [Authentication](./index.md) → **📄 Current**: JWT Service Guide

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Getting Started Hub](../../getting-started/index.md) - FLEXT Framework installation and basic configuration required
- [Security Hub](../../security/index.md) - Understanding security architecture patterns and authentication principles
- [Architecture Hub](../../architecture/index.md) - Hexagonal architecture fundamentals underlying the JWT service

### **➡️ Next Steps**

- [Oracle OAuth2 Authentication](../oracle/oracle-oauth2-authentication-guide.md) - Oracle-specific OAuth2 implementation patterns
- [Oracle Guides Hub](../oracle/index.md) - Oracle integration patterns using JWT authentication
- [Security Implementation](../../security/authentication/index.md) - Advanced security implementation patterns

### **🔗 Related Topics**

- [API Reference Hub](../../api-reference/index.md) - JWT service APIs and authentication interfaces
- [Examples Hub](../../examples/index.md) - Working JWT authentication examples and code templates
- [Infrastructure Hub](../../infrastructure/index.md) - HTTP infrastructure services supporting JWT authentication
- [Development Hub](../../development/index.md) - Testing frameworks for authentication services
- [Deployment Hub](../../deployment/index.md) - Production deployment patterns for authenticated services

---

## 📋 **Overview**

This guide demonstrates how to use the **FLEXT JWT Service** infrastructure that provides OAuth2 JWT authentication and token management as a reusable service within the FLEXT ecosystem.

## Key Features

- 🔑 **Automatic Token Management** - Handles token acquisition, refresh, and expiry
- 🛡️ **Security Best Practices** - Uses OAuth2 client credentials flow with proper validation
- 🔄 **Auto-Refresh** - Automatically refreshes tokens before expiry
- 📊 **Health Monitoring** - Built-in health checks and service monitoring
- 🏗️ **Multiple Patterns** - Supports Oracle OIC, generic OAuth2, and custom configurations
- 🎯 **FLEXT Integration** - Seamlessly integrates with FLEXT HTTP infrastructure

## Architecture

The JWT service is implemented in the FLEXT HTTP infrastructure layer:

```
FLEXT Infrastructure
├── HTTP Layer
│   ├── FlextHttpAuthManager (Extended with OAuth2 JWT)
│   ├── FlextJwtService (New high-level service)
│   └── FlextOAuth2TokenData (Token data model)
└── Applications
    └── flext-http-oracle-oic (Uses JWT service)
```

## Basic Usage

### 1. Oracle OIC Configuration

For Oracle Integration Cloud, use the specialized factory method:

```python
from flext.infrastructure.http import FlextJwtService

# Create JWT service for Oracle OIC
jwt_service = FlextJwtService.create_for_oracle_oic(
    client_id="your-idcs-client-id",
    client_secret="your-idcs-client-secret",
    idcs_url="your-idcs-domain.identity.oracle.com",
    audience="your-client-audience",
    instance_id="your-oic-instance-id",
    service_name="my-oic-jwt-service"
)

# Get valid token
token = await jwt_service.get_valid_token()

# Get authentication headers
auth_headers = await jwt_service.get_auth_headers()

# Make authenticated request
headers = {
    "Accept": "application/json",
    **auth_headers
}
```

### 2. Generic OAuth2 Configuration

For any OAuth2 provider:

```python
jwt_service = FlextJwtService.create_generic(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_url="https://auth.example.com/oauth2/token",
    scope="api:read api:write",
    audience="api.example.com",
    service_name="my-jwt-service"
)
```

### 3. Environment-Based Configuration

```python
import os

jwt_service = FlextJwtService.create_for_oracle_oic(
    client_id=os.getenv("IDCS_CLIENT_ID"),
    client_secret=os.getenv("IDCS_CLIENT_SECRET"),
    idcs_url=os.getenv("IDCS_URL"),
    audience=os.getenv("IDCS_CLIENT_AUD"),
    instance_id=os.getenv("OIC_INSTANCE_ID")
)
```

## Advanced Features

### Health Monitoring

```python
# Check service health
is_healthy = await jwt_service.health_check()

# Get service information
service_info = jwt_service.get_service_info()
print(f"Service: {service_info['service_name']}")
print(f"Token expires in: {service_info.get('expires_in')} seconds")
```

### Token Management

```python
# Force token refresh
success = await jwt_service.refresh_token()

# Get token information
token_info = jwt_service.get_token_info()
print(f"Has token: {token_info['has_token']}")
print(f"Is expired: {token_info['is_expired']}")
print(f"Expires in: {token_info['expires_in']} seconds")
```

### Multiple Services

```python
# Manage multiple JWT services
services = {
    "dev": FlextJwtService.create_generic(...),
    "staging": FlextJwtService.create_generic(...),
    "prod": FlextJwtService.create_for_oracle_oic(...)
}

# Use appropriate service based on environment
current_env = os.getenv("ENVIRONMENT", "dev")
jwt_service = services[current_env]
```

## Integration with FLEXT HTTP Client

The JWT service integrates seamlessly with FLEXT HTTP infrastructure:

```python
from flext.infrastructure.http import FlextHttpClient, FlextHttpConfig

# Create JWT service
jwt_service = FlextJwtService.create_for_oracle_oic(...)

# Create HTTP client
http_config = FlextHttpConfig(
    base_url="https://api.example.com",
    timeout=30.0
)
http_client = FlextHttpClient(http_config)

# Make authenticated requests
auth_headers = await jwt_service.get_auth_headers()
response = await http_client.get("/api/data", headers=auth_headers)
```

## Oracle OIC Specific Usage

### Working with OIC APIs

```python
from flext_http_oracle_oic import OracleOicService, load_oic_config

# Load configuration
config = load_oic_config()

# Create OIC service (automatically uses JWT service)
oic_service = OracleOicService(config)

# Use OIC service methods
integrations = await oic_service.list_integrations()
connections = await oic_service.list_connections()

# Health check
is_healthy = await oic_service.health_check()
```

### Following Bash Script Pattern

The JWT service follows the exact OAuth2 pattern from the working bash script:

```bash
# Original bash script pattern
OAUTH2_SCOPE="${IDCS_CLIENT_AUD}:443urn:opc:resource:consumer::all ${IDCS_CLIENT_AUD}:443/ic/api/"
BASIC_AUTH=$(echo -n "${IDCS_CLIENT_ID}:${IDCS_CLIENT_SECRET}" | base64)

curl -X POST "${IDCS_URL}/oauth2/v1/token" \
  -H "Authorization: Basic ${BASIC_AUTH}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=${OAUTH2_SCOPE}"
```

The JWT service automatically:

- Builds the correct OAuth2 scope
- Encodes client credentials as Basic Auth
- Makes token requests to IDCS
- Handles token expiry and refresh

## Configuration Reference

### FlextJwtServiceConfig

| Field                 | Type        | Description                                                     | Required |
| --------------------- | ----------- | --------------------------------------------------------------- | -------- |
| `client_id`           | str         | OAuth2 client ID                                                | Yes      |
| `client_secret`       | SecretStr   | OAuth2 client secret                                            | Yes      |
| `token_url`           | str         | OAuth2 token endpoint URL                                       | Yes      |
| `scope`               | str \| None | OAuth2 scope                                                    | No       |
| `audience`            | str \| None | OAuth2 audience                                                 | No       |
| `grant_type`          | str         | OAuth2 grant type (default: "client_credentials")               | No       |
| `token_expiry_buffer` | int         | Buffer in seconds before token expiry to refresh (default: 300) | No       |
| `service_name`        | str         | Service name for identification                                 | No       |

### Environment Variables for Oracle OIC

```bash
# Required
export IDCS_CLIENT_ID="your-client-id"
export IDCS_CLIENT_SECRET="your-client-secret"
export IDCS_URL="your-idcs-domain.identity.oracle.com"
export IDCS_CLIENT_AUD="your-client-audience"
export OIC_INSTANCE_ID="your-oic-instance-id"

# Optional
export OIC_REGION="us-phoenix-1"  # Oracle Cloud region
```

## Error Handling

```python
from flext.infrastructure.http.exceptions import FlextHttpAuthenticationError

try:
    token = await jwt_service.get_valid_token()
except FlextHttpAuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    # Handle authentication error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle other errors
```

## Best Practices

### 1. Service Lifecycle Management

```python
# Initialize once at application startup
jwt_service = FlextJwtService.create_for_oracle_oic(...)

# Use throughout application lifecycle
async def make_api_call():
    auth_headers = await jwt_service.get_auth_headers()
    # ... make request

# No explicit cleanup needed - tokens are managed automatically
```

### 2. Health Monitoring

```python
# Regular health checks
async def monitor_jwt_service():
    while True:
        is_healthy = await jwt_service.health_check()
        if not is_healthy:
            logger.warning("JWT service unhealthy")
            # Alert or take corrective action

        await asyncio.sleep(60)  # Check every minute
```

### 3. Configuration Management

```python
# Use environment variables for secrets
jwt_service = FlextJwtService.create_for_oracle_oic(
    client_id=os.getenv("IDCS_CLIENT_ID"),
    client_secret=os.getenv("IDCS_CLIENT_SECRET"),
    # ... other config from environment
)

# Validate configuration at startup
assert jwt_service.get_service_info()["client_id"], "Client ID must be configured"
```

### 4. Error Recovery

```python
async def robust_api_call():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            auth_headers = await jwt_service.get_auth_headers()
            response = await http_client.get("/api/data", headers=auth_headers)
            return response
        except FlextHttpAuthenticationError:
            if attempt < max_retries - 1:
                # Force token refresh and retry
                await jwt_service.refresh_token()
                continue
            raise
```

## Testing

### Unit Testing

```python
import pytest
from flext.infrastructure.http import FlextJwtService

@pytest.mark.asyncio
async def test_jwt_service_creation():
    jwt_service = FlextJwtService.create_generic(
        client_id="test-client",
        client_secret="test-secret",
        token_url="https://test.auth.com/token"
    )

    service_info = jwt_service.get_service_info()
    assert service_info["client_id"] == "test-client"
    assert service_info["service_name"] == "generic-jwt"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_oic_integration(oic_test_config):
    jwt_service = FlextJwtService.create_for_oracle_oic(**oic_test_config)

    # Test health check
    is_healthy = await jwt_service.health_check()
    assert is_healthy

    # Test token acquisition
    token = await jwt_service.get_valid_token()
    assert token
    assert len(token) > 20  # JWT tokens are long
```

## Migration Guide

### From Direct FlextHttpAuthManager

Before:

```python
from flext.infrastructure.http import FlextHttpAuthManager, FlextHttpAuthConfig

auth_config = FlextHttpAuthConfig(
    auth_type=FlextHttpAuthType.OAUTH2_JWT,
    client_id="...",
    client_secret="...",
    token_url="..."
)
auth_manager = FlextHttpAuthManager(auth_config)
```

After:

```python
from flext.infrastructure.http import FlextJwtService

jwt_service = FlextJwtService.create_generic(
    client_id="...",
    client_secret="...",
    token_url="..."
)
```

### From Custom OAuth2 Implementation

Before:

```python
# Custom OAuth2 token management
async def get_token():
    # Custom implementation...
    pass
```

After:

```python
# Use FLEXT JWT service
jwt_service = FlextJwtService.create_for_oracle_oic(...)
token = await jwt_service.get_valid_token()
```

## Performance Considerations

- **Token Caching**: Tokens are automatically cached and reused until near expiry
- **Concurrent Requests**: Multiple requests can safely use the same JWT service instance
- **Memory Usage**: Minimal overhead - only stores current token and configuration
- **Network Calls**: Token refresh only happens when needed (near expiry or forced)

## Security Considerations

- **Secret Management**: Use environment variables for client secrets
- **Token Expiry**: Automatic refresh with configurable buffer time
- **Scope Limitation**: Use minimal required OAuth2 scopes
- **Audit Logging**: All authentication events are logged
- **Error Handling**: Sensitive information is not exposed in error messages

## Troubleshooting

### Common Issues

1. **Authentication Failed**

   - Check client credentials
   - Verify token URL is accessible
   - Confirm OAuth2 scope is correct

2. **Token Refresh Errors**

   - Check network connectivity
   - Verify client credentials haven't expired
   - Review OAuth2 scope permissions

3. **Service Unhealthy**
   - Run health check to get detailed status
   - Check logs for specific error messages
   - Verify configuration parameters

### Debug Mode

```python
import logging
logging.getLogger("flext.infrastructure.http").setLevel(logging.DEBUG)

# This will show detailed OAuth2 flow information
jwt_service = FlextJwtService.create_for_oracle_oic(...)
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Security Hub](../security/index.md) - Security fundamentals and best practices
- [Installation Guide](../getting-started/installation-guide.md) - Environment setup

### **Next Steps**

- [Oracle OAuth2 Authentication](./oracle/oracle-oauth2-authentication-guide.md) - Oracle-specific authentication
- [Oracle WMS Integration](./oracle/oracle-wms-comprehensive-guide.md) - WMS system integration

### **Related Topics**

- [HTTP Infrastructure](../../architecture/infrastructure/infrastructure-architecture.md) - HTTP layer architecture
- [Security Patterns](../../architecture/patterns/index.md) - Security design patterns

---

**📄 Content Document** | **🏠 Parent**: [Authentication Hub](./index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
