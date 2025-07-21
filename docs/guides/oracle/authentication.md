# Oracle Authentication Guide

> **Complete Oracle authentication implementation for FLEXT framework** | [← Back to Oracle Hub](index.md)

## Overview

Complete Oracle authentication guide covering OAuth2, JWT, SSO, database authentication, and security best practices for all Oracle systems including OIC, WMS, and Database integrations.

## 🎯 Quick Navigation

- [**Authentication Methods**](#-authentication-methods) - Overview of all methods
- [**OAuth2 Client Credentials**](#-oauth2-client-credentials) - Recommended for automation
- [**OAuth2 Authorization Code**](#-oauth2-authorization-code) - Interactive flows
- [**Database Authentication**](#-database-authentication) - Oracle Database security
- [**SSO Configuration**](#-sso-configuration) - Single Sign-On setup
- [**Security Best Practices**](#-security-best-practices) - Production security
- [**Troubleshooting**](#-troubleshooting) - Common issues and solutions

## 🔐 Authentication Methods

### Overview of Oracle Authentication Options

| Method                        | Use Case         | Oracle System     | Automation   | MFA Support |
| ----------------------------- | ---------------- | ----------------- | ------------ | ----------- |
| **OAuth2 Client Credentials** | Server-to-server | OIC, WMS API      | ✅ Excellent | ✅ Yes      |
| **OAuth2 Authorization Code** | Interactive apps | OIC, WMS API      | ❌ No        | ✅ Yes      |
| **Basic Authentication**      | Legacy systems   | WMS API, Database | ⚠️ Limited   | ❌ No       |
| **Database Authentication**   | Direct DB access | Oracle Database   | ✅ Yes       | ⚠️ Limited  |
| **JWT Assertion**             | Enterprise SSO   | OIC, Custom       | ✅ Yes       | ✅ Yes      |

### Recommended Authentication Matrix

| Scenario                   | Recommended Method              | Alternative               |
| -------------------------- | ------------------------------- | ------------------------- |
| **Production Automation**  | OAuth2 Client Credentials       | JWT Assertion             |
| **Development/Testing**    | OAuth2 Client Credentials       | Basic Auth                |
| **Web Applications**       | OAuth2 Authorization Code       | OAuth2 Client Credentials |
| **Database Operations**    | Database Authentication         | Connection pooling        |
| **Enterprise Integration** | OAuth2 Client Credentials + SSO | JWT Assertion             |

## 🤖 OAuth2 Client Credentials

### The Recommended Method for Automation

OAuth2 Client Credentials is the **gold standard** for machine-to-machine integration, especially when:

- **Automation without user intervention** is required
- Implementing **CI/CD integrations**
- System has **MFA enabled**
- Integration has **no user interface** for login
- Need **server-to-server integration**

### Implementation Steps

#### 1. IDCS Application Configuration

```bash
# Create IDCS Application
curl -X POST "https://idcs-domain.identity.oraclecloud.com/REDACTED_LDAP_BIND_PASSWORD/v1/Apps" \
     -H "Authorization: Bearer ${ADMIN_TOKEN}" \
     -H "Content-Type: application/scim+json" \
     -d '{
       "displayName": "FLEXT Integration",
       "description": "FLEXT framework Oracle integration",
       "isOAuth2": true,
       "allowedGrants": ["client_credentials"],
       "allowedScopes": [
         "https://oracle.com/scopes/oic",
         "https://oracle.com/scopes/wms"
       ]
     }'
```

#### 2. Client Credentials Configuration

```python
from flext_auth.oauth2 import OAuth2ClientCredentials

# Configure OAuth2 client
oauth_client = OAuth2ClientCredentials(
    client_id="your-client-id",
    client_secret="your-client-secret",
    token_endpoint="https://idcs-domain.identity.oraclecloud.com/oauth2/v1/token",
    scope="https://oracle.com/scopes/oic"
)

# Get access token
token = await oauth_client.get_access_token()
```

#### 3. API Request with OAuth2

```python
import httpx
from flext_oracle_oic import OICClient

# Initialize client with OAuth2
client = OICClient(
    base_url="https://oic-instance.ocp.oraclecloud.com",
    auth_method="oauth2",
    oauth_config={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "token_endpoint": "https://idcs-domain.identity.oraclecloud.com/oauth2/v1/token",
        "scope": "https://oracle.com/scopes/oic"
    }
)

# Make authenticated request
response = await client.get("/ic/api/integration/v1/integrations")
```

## 🌐 OAuth2 Authorization Code

### For Interactive Applications

OAuth2 Authorization Code flow is ideal for:

- **Web applications** with user interface
- **Interactive user authentication**
- Applications requiring **user consent**
- **Third-party application** access

### Implementation Steps

#### 1. Authorization URL Generation

```python
from flext_auth.oauth2 import OAuth2AuthorizationCode

oauth_client = OAuth2AuthorizationCode(
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorization_endpoint="https://idcs-domain.identity.oraclecloud.com/oauth2/v1/authorize",
    token_endpoint="https://idcs-domain.identity.oraclecloud.com/oauth2/v1/token",
    redirect_uri="https://your-app.com/callback"
)

# Generate authorization URL
auth_url = oauth_client.get_authorization_url(
    scope="https://oracle.com/scopes/oic",
    state="random-state-value"
)

# Redirect user to auth_url
```

#### 2. Token Exchange

```python
# After user authorization, exchange code for token
token_response = await oauth_client.exchange_code_for_token(
    authorization_code="received-auth-code",
    state="expected-state-value"
)

access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]
```

## 💾 Database Authentication

### Oracle Database Direct Connection

#### 1. Connection String Authentication

```python
from flext_db_oracle import OracleConnection

# Basic database authentication
connection = OracleConnection(
    host="oracle-db.company.com",
    port=1521,
    service_name="ORCL",
    username="integration_user",
    password="secure_password"
)

# Advanced connection with wallet
connection = OracleConnection(
    dsn="(description=(address=(protocol=tcps)(host=oracle-db.com)(port=1522))(connect_data=(service_name=ORCL)))",
    username="integration_user",
    password="secure_password",
    wallet_location="/path/to/wallet",
    wallet_password="wallet_password"
)
```

#### 2. Connection Pooling

```python
from flext_db_oracle import OraclePool

# Create connection pool
pool = OraclePool(
    dsn="oracle-db.company.com:1521/ORCL",
    username="integration_user",
    password="secure_password",
    min_connections=5,
    max_connections=20,
    increment=2
)

# Use pooled connection
async with pool.acquire() as connection:
    result = await connection.execute("SELECT * FROM integrations")
```

## 🏢 SSO Configuration

### Single Sign-On Setup

#### 1. SAML Configuration

```xml
<!-- SAML SP Configuration -->
<saml:EntityDescriptor entityID="https://flext.company.com/saml">
  <saml:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <saml:AssertionConsumerService 
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        Location="https://flext.company.com/saml/acs"
        index="1" />
  </saml:SPSSODescriptor>
</saml:EntityDescriptor>
```

#### 2. OIDC Configuration

```python
from flext_auth.oidc import OIDCClient

# Configure OIDC SSO
oidc_client = OIDCClient(
    issuer="https://idcs-domain.identity.oraclecloud.com",
    client_id="your-oidc-client-id",
    client_secret="your-oidc-client-secret",
    redirect_uri="https://flext.company.com/oidc/callback"
)

# Initiate SSO login
login_url = oidc_client.get_login_url(
    scope="openid profile email",
    state="random-state"
)
```

## 🔒 Security Best Practices

### Token Management

#### 1. Secure Token Storage

```python
from flext_auth.storage import SecureTokenStorage

# Use secure token storage
token_storage = SecureTokenStorage(
    encryption_key="your-encryption-key",
    storage_backend="redis",  # or "database"
    redis_url="redis://localhost:6379/0"
)

# Store token securely
await token_storage.store_token(
    token_id="user-123",
    token_data={
        "access_token": "encrypted-access-token",
        "refresh_token": "encrypted-refresh-token",
        "expires_at": "2025-01-01T00:00:00Z"
    }
)
```

#### 2. Token Rotation

```python
from flext_auth.rotation import TokenRotator

# Implement automatic token rotation
rotator = TokenRotator(
    oauth_client=oauth_client,
    storage=token_storage,
    rotation_threshold=300  # Rotate 5 minutes before expiry
)

# Get fresh token (automatically rotates if needed)
fresh_token = await rotator.get_fresh_token("user-123")
```

### Network Security

#### 1. TLS Configuration

```python
import ssl
from flext_oracle_oic import OICClient

# Configure strict TLS
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

client = OICClient(
    base_url="https://oic-instance.ocp.oraclecloud.com",
    ssl_context=ssl_context,
    timeout=30
)
```

#### 2. Certificate Pinning

```python
from flext_auth.security import CertificatePinner

# Pin Oracle certificates
cert_pinner = CertificatePinner([
    "sha256/oracle-cert-fingerprint-1",
    "sha256/oracle-cert-fingerprint-2"
])

client = OICClient(
    base_url="https://oic-instance.ocp.oraclecloud.com",
    cert_pinner=cert_pinner
)
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Token Expiry Issues

**Problem**: "HTTP 401 Unauthorized" errors
**Solution**: Implement automatic token refresh

```python
from flext_auth.handlers import TokenExpiryHandler

# Handle token expiry automatically
async def make_authenticated_request(url, **kwargs):
    try:
        response = await client.get(url, **kwargs)
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            # Refresh token and retry
            await oauth_client.refresh_token()
            response = await client.get(url, **kwargs)
            response.raise_for_status()
            return response
        raise
```

#### 2. CORS Issues

**Problem**: CORS errors in web applications
**Solution**: Configure proper CORS headers

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://idcs-domain.identity.oraclecloud.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

#### 3. Certificate Verification Errors

**Problem**: SSL certificate verification failures
**Solution**: Update certificate store or use custom CA bundle

```python
import certifi
import httpx

# Use updated certificate bundle
client = httpx.AsyncClient(
    verify=certifi.where(),
    timeout=30
)
```

### Debugging Tools

#### 1. Token Inspection

```python
import jwt
from datetime import datetime

def inspect_jwt_token(token):
    """Inspect JWT token without verification."""
    try:
        # Decode without verification for debugging
        payload = jwt.decode(token, options={"verify_signature": False})
        
        print(f"Issuer: {payload.get('iss')}")
        print(f"Subject: {payload.get('sub')}")
        print(f"Audience: {payload.get('aud')}")
        print(f"Expires: {datetime.fromtimestamp(payload.get('exp', 0))}")
        print(f"Scopes: {payload.get('scope', 'N/A')}")
        
        return payload
    except Exception as e:
        print(f"Token inspection failed: {e}")
        return None
```

#### 2. Request Logging

```python
import logging
import httpx

# Enable detailed HTTP logging
logging.basicConfig(level=logging.DEBUG)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.DEBUG)

# All HTTP requests will be logged with full details
```

## 📚 Reference Implementation

### Complete Integration Example

```python
"""
Complete Oracle authentication integration example.
Demonstrates OAuth2, error handling, and security best practices.
"""

from flext_auth.oauth2 import OAuth2ClientCredentials
from flext_oracle_oic import OICClient
from flext_auth.storage import SecureTokenStorage
from flext_auth.security import CertificatePinner
import httpx
import asyncio

class OracleIntegration:
    """Complete Oracle integration with authentication."""
    
    def __init__(self, config):
        self.config = config
        self.oauth_client = OAuth2ClientCredentials(**config.oauth2)
        self.token_storage = SecureTokenStorage(**config.storage)
        self.cert_pinner = CertificatePinner(config.cert_pins)
        
    async def initialize(self):
        """Initialize integration with authentication."""
        # Get or refresh access token
        token = await self.get_fresh_token()
        
        # Initialize OIC client
        self.oic_client = OICClient(
            base_url=self.config.oic_url,
            access_token=token,
            cert_pinner=self.cert_pinner
        )
        
    async def get_fresh_token(self):
        """Get fresh access token with automatic refresh."""
        stored_token = await self.token_storage.get_token("system")
        
        if stored_token and not self.is_token_expired(stored_token):
            return stored_token["access_token"]
        
        # Get new token
        token_data = await self.oauth_client.get_access_token()
        
        # Store securely
        await self.token_storage.store_token("system", token_data)
        
        return token_data["access_token"]
        
    async def make_integration_request(self, endpoint, **kwargs):
        """Make authenticated request with automatic retry."""
        try:
            response = await self.oic_client.request(endpoint, **kwargs)
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token expired, refresh and retry
                await self.initialize()
                response = await self.oic_client.request(endpoint, **kwargs)
                return response.json()
            raise

# Usage example
async def main():
    config = {
        "oauth2": {
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
            "token_endpoint": "https://idcs.oraclecloud.com/oauth2/v1/token",
            "scope": "https://oracle.com/scopes/oic"
        },
        "storage": {
            "encryption_key": "your-encryption-key",
            "storage_backend": "redis",
            "redis_url": "redis://localhost:6379/0"
        },
        "cert_pins": ["sha256/oracle-cert-pin"],
        "oic_url": "https://oic-instance.ocp.oraclecloud.com"
    }
    
    integration = OracleIntegration(config)
    await integration.initialize()
    
    # Make authenticated requests
    integrations = await integration.make_integration_request(
        "/ic/api/integration/v1/integrations"
    )
    
    print(f"Found {len(integrations)} integrations")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔗 Related Documentation

- [Oracle Integration Hub](index.md) - Main Oracle documentation hub
- [Database Integration](database-integration.md) - Oracle Database connectivity
- [OIC Integration](oic-integration.md) - Oracle Integration Cloud
- [WMS Integration](wms-integration.md) - Warehouse Management System
- [Security Policies](../../security/policies/security-policy.md) - Enterprise security policies

---

**Navigation**: [Oracle Hub](index.md) | **Updated**: 2025-01-20 | **Version**: 2.0.0