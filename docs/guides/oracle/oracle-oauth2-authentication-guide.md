# 🔐 Oracle OAuth2 Authentication Complete Guide

> **Function**: Complete OAuth2 authentication implementation for Oracle systems | **Audience**: Security engineers, integration developers | **Status**: Production-ready

[![OAuth2](https://img.shields.io/badge/auth-OAuth2-green.svg)](https://oauth.net/2/)
[![Oracle](https://img.shields.io/badge/Oracle-Integration-red.svg)](./index.md)
[![Security](https://img.shields.io/badge/security-critical-red.svg)](../../security/index.md)

**Complete OAuth2 authentication implementation guide for Oracle Integration Cloud (OIC), IDCS configuration, and secure system-to-system communication patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: OAuth2 Authentication Complete Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[OAuth2 Authentication Complete Guide]** → [Oracle Security Guide](./oracle-security-guide.md)
```

## 🎯 **Quick Navigation**

- **📂 Section Hub**: [Oracle Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Security Hub](../../security/index.md) | [Integration Hub](./oracle-integration-comprehensive-guide.md)

---

## 🚨 **Critical Security Notice**

This document describes OAuth2 authentication options for Oracle Integration Cloud (OIC) integration. **Proper authentication is CRITICAL** for secure system-to-system communication.

---

## 📋 **Authentication Methods Overview**

## 1. Client Credentials Method (Recommended for Automation)

The Client Credentials flow is the **recommended method** for machine-to-machine integration, as it doesn't require user interaction and works even with MFA enabled.

### 1.1 When to Use Client Credentials

Choose this flow when:

- **Automation without user intervention** is required
- Implementing **CI/CD integrations**
- System has **MFA enabled**
- Integration has **no user interface** for login
- Need **server-to-server integration**
- **Production environments** with high security requirements

### 1.2 IDCS (Identity Cloud Service) Configuration

#### Step-by-Step IDCS Setup

1. **Access IDCS Console:** Navigate to the IDCS console associated with your OIC environment
2. **Create Application:** Go to Applications > Add > Confidential Application
3. **Configure Application:** Set a descriptive name for the application
4. **Client Configuration:** In Configuration > General Information, check "Configure this application as a client now"
5. **Grant Types:** In Grant Types section, select "Client Credentials"
6. **Primary Audience:** In Resources > Primary Audience, add your OIC base URL:

   ```
   https://instance-name.integration.ocp.oraclecloud.com:443
   ```

7. **Scope Configuration:** In Resources > Scope, add the following scopes:

   ```
   urn:opc:resource:consumer::all     # For calling integrations
   /ic/api/                           # For calling REDACTED_LDAP_BIND_PASSWORDistrative APIs
   ```

8. **Finalize Setup:** Complete creation and activate the application
9. **Role Assignment:** Assign the application to "ServiceUser" role in the OIC application within IDCS

### 1.3 Required Environment Variables

```bash
# IDCS Configuration
IDCS_URL=idcs-xxxx.identity.oraclecloud.com
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Resource Audiences (Critical - Format is important!)
RESOURCE_AUD=https://XXXX.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
API_AUD=https://XXXX.integration.ocp.oraclecloud.com:443/ic/api/

# OIC Instance URL
OIC_URL=https://instance-name.integration.ocp.oraclecloud.com
```

**⚠️ CRITICAL FORMAT NOTE:**

- In `RESOURCE_AUD`: NO slash between port (443) and "urn"
- In `API_AUD`: There IS a slash after port (443)

### 1.4 Implementation with FLX Framework

#### 1.4.1 Using the OIC Library

```bash
# Include the library in your script
source "scripts/lib/oic.sh"

# Get token automatically
oic_get_token

# Use token for API calls
response=$(oic_api_get '/ic/api/integration/v1/integrations')

# Test specific endpoints
health=$(oic_check_health)
connections=$(oic_list_connections)
```

#### 1.4.2 Complete Example Implementation

```bash
#!/bin/bash
# oic_integration_example.sh

# Load environment variables
source .env

# Include OIC library
source "scripts/lib/oic.sh"

# Main execution
main() {
    echo "🔐 Authenticating with OIC..."

    # Get OAuth2 token
    if oic_get_token; then
        echo "✅ Authentication successful"
    else
        echo "❌ Authentication failed"
        exit 1
    fi

    # Test API connectivity
    echo "🔍 Testing API connectivity..."

    # Check OIC health
    if health=$(oic_check_health); then
        echo "✅ OIC Health Check: $health"
    else
        echo "❌ Health check failed"
    fi

    # List available integrations
    echo "📋 Listing integrations..."
    integrations=$(oic_api_get '/ic/api/integration/v1/integrations')
    echo "✅ Found integrations: $integrations"

    # List connections
    echo "🔗 Listing connections..."
    connections=$(oic_list_connections)
    echo "✅ Available connections: $connections"
}

# Execute main function
main "$@"
```

### 1.5 Advanced Authentication Patterns

#### 1.5.1 Token Caching and Refresh

```python
from flx.adapters.oracle.oic import OICAuthenticator

# Initialize authenticator with automatic token management
auth = OICAuthenticator(
    idcs_url=os.getenv('IDCS_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    resource_aud=os.getenv('RESOURCE_AUD'),
    api_aud=os.getenv('API_AUD'),
    cache_tokens=True,  # Enable token caching
    auto_refresh=True   # Automatic token refresh
)

# Get authenticated session
session = await auth.get_authenticated_session()

# Use session for API calls
response = await session.get('/ic/api/integration/v1/integrations')
```

#### 1.5.2 Error Handling and Retry Logic

```python
import asyncio
from flx.adapters.oracle.oic import OICClient, OICAuthError

async def robust_oic_call(endpoint, max_retries=3):
    """Make OIC API call with robust error handling."""

    for attempt in range(max_retries):
        try:
            # Initialize OIC client
            client = OICClient()

            # Authenticate and make call
            response = await client.authenticated_request('GET', endpoint)
            return response

        except OICAuthError as e:
            if attempt < max_retries - 1:
                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                continue
            else:
                raise e
        except Exception as e:
            # Log error and continue
            logger.error(f"OIC call failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise e

# Usage
try:
    integrations = await robust_oic_call('/ic/api/integration/v1/integrations')
    print(f"Successfully retrieved integrations: {integrations}")
except Exception as e:
    print(f"Failed to retrieve integrations after retries: {e}")
```

### 1.6 Troubleshooting Client Credentials

#### 1.6.1 Common Issues and Solutions

**Issue 1: Token obtained successfully but API calls fail**

```bash
# Verify OIC_URL format (must include https://)
echo "OIC_URL: $OIC_URL"

# Check client has correct role in IDCS
echo "Verify ServiceUser role assignment in IDCS"

# Validate audience configuration
echo "RESOURCE_AUD: $RESOURCE_AUD"
echo "API_AUD: $API_AUD"

# Enable debug mode
DEBUG=true scripts/oic_client_credentials_example.sh --debug
```

**Issue 2: "invalid_client" error**

```bash
# Verify client credentials
curl -X POST https://$IDCS_URL/oauth2/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d "grant_type=client_credentials&scope=$RESOURCE_AUD%20$API_AUD"
```

**Issue 3: "insufficient_scope" error**

```bash
# Check scope configuration in IDCS application
# Ensure both scopes are configured:
# - urn:opc:resource:consumer::all
# - /ic/api/
```

#### 1.6.2 Diagnostic Commands

```bash
# Configuration validation
./scripts/oic_client_credentials_example.sh --config

# Full debug execution
DEBUG=true ./scripts/oic_client_credentials_example.sh

# Network connectivity test
curl -v https://$OIC_URL/ic/api/integration/v1/integrations

# Token validation test
curl -X POST https://$IDCS_URL/oauth2/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic $BASIC_AUTH" \
  -d "grant_type=client_credentials&scope=$RESOURCE_AUD%20$API_AUD"
```

## 2. Authorization Code Method (For Interactive Flows)

This method is useful when you want explicit user login. However, it's **not recommended for automation**, especially if MFA is enabled.

### 2.1 When to Use Authorization Code

Choose this flow when:

- **Explicit user interaction** is desired or necessary
- Need to **authenticate with specific user context**
- Implementing a **web application or client with UI**
- Want **granular permissions** based on user

### 2.2 Additional IDCS Configuration

In addition to Client Credentials setup:

1. **Grant Types:** Add "Authorization Code" to Grant Types
2. **Redirect URL:** In Web Tier Policy > Redirect URL, add your callback URL:

   ```
   https://idcs-xxxx.identity.oraclecloud.com/callback
   ```

3. **Save and Activate:** Save and activate the application

### 2.3 Additional Environment Variables

```bash
# Additional variables for Authorization Code flow
REDIRECT_URI=https://idcs-xxxx.identity.oraclecloud.com/callback
SCOPE="${RESOURCE_AUD} offline_access"
```

### 2.4 Implementation Example

```bash
# Include the library in your script
source "scripts/lib/oic.sh"

# Get authorization URL
auth_url=$(oic_auth_url)
echo "Visit this URL and login: $auth_url"

# After receiving authorization code
oic_exchange_code "code_received_after_login"

# Use token for API calls
response=$(oic_api_get '/ic/api/integration/v1/integrations')
```

## 3. Production Security Best Practices

### 3.1 Credential Management

#### 3.1.1 Secure Storage

```bash
# Use encrypted credential storage
python -m flx.security create-credential-store \
    --encrypted \
    --output ./secure/credentials.enc \
    --key-file ./secure/encryption.key

# Set secure file permissions
chmod 600 ./secure/credentials.enc
chmod 600 ./secure/encryption.key
chmod 700 ./secure/
```

#### 3.1.2 Environment Variable Security

```bash
# Use secure environment loading
source <(gpg --decrypt credentials.env.gpg)

# Or use dedicated secret management
export CLIENT_SECRET=$(vault kv get -field=client_secret secret/oic/credentials)
```

### 3.2 Network Security

#### 3.2.1 SSL/TLS Configuration

```bash
# Verify SSL certificates in production
curl -v --cacert ca-bundle.pem https://$OIC_URL/ic/api/health

# Use certificate pinning for additional security
export SSL_CERT_BUNDLE=/path/to/trusted-ca-bundle.pem
```

#### 3.2.2 IP Whitelisting

```bash
# Configure IP restrictions in IDCS
# Add OIC public IP ranges to allowed list
# Monitor and log authentication attempts
```

### 3.3 Monitoring and Auditing

#### 3.3.1 Authentication Monitoring

```python
from flx.adapters.oracle.oic import OICAuthMonitor

# Initialize monitoring
monitor = OICAuthMonitor()

# Track authentication events
await monitor.log_auth_event(
    event_type='token_acquired',
    client_id=client_id,
    timestamp=datetime.now(),
    success=True
)

# Generate audit reports
audit_report = await monitor.generate_audit_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)
```

#### 3.3.2 Security Alerting

```bash
# Set up alerts for authentication failures
# Monitor for unusual authentication patterns
# Track token usage and expiration
```

## 4. Alternative Authentication Methods

### 4.1 JWT Assertion

For environments supporting JWT Assertion:

```python
from flx.adapters.oracle.oic import JWTAssertion

# Configure JWT assertion
jwt_auth = JWTAssertion(
    issuer=client_id,
    subject=service_account,
    audience=idcs_url,
    private_key_path='path/to/private_key.pem'
)

# Generate and use assertion
token = await jwt_auth.get_access_token()
```

### 4.2 Basic Authentication for WMS API

For WMS APIs, basic authentication is often supported:

```bash
# WMS API with basic auth
curl -X GET "$WMS_URL/resource" \
  -u "$WMS_USER:$WMS_PASS" \
  -H "Content-Type: application/json"
```

## 5. Integration with FLX Framework

### 5.1 Unified Authentication Service

```python
from flx.adapters.oracle import OracleAuthenticationService

# Initialize unified auth service
auth_service = OracleAuthenticationService(
    oic_config={
        'idcs_url': os.getenv('IDCS_URL'),
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET')
    },
    wms_config={
        'base_url': os.getenv('WMS_URL'),
        'username': os.getenv('WMS_USER'),
        'password': os.getenv('WMS_PASS')
    }
)

# Get authenticated clients
oic_client = await auth_service.get_oic_client()
wms_client = await auth_service.get_wms_client()

# Use clients for API calls
integrations = await oic_client.list_integrations()
orders = await wms_client.get_orders()
```

### 5.2 Configuration Management

```yaml
# config/authentication.yaml
oracle_authentication:
  oic:
    method: client_credentials
    idcs_url: ${IDCS_URL}
    client_id: ${CLIENT_ID}
    client_secret: ${CLIENT_SECRET}
    scopes:
      - "urn:opc:resource:consumer::all"
      - "/ic/api/"

  wms:
    method: basic_auth
    base_url: ${WMS_URL}
    username: ${WMS_USER}
    password: ${WMS_PASS}

  security:
    token_cache_enabled: true
    token_refresh_threshold: 300 # seconds
    max_retry_attempts: 3
    ssl_verify: true
```

## 6. Troubleshooting Guide

### 6.1 Error Resolution Matrix

| Error                  | Cause                               | Solution                                              |
| ---------------------- | ----------------------------------- | ----------------------------------------------------- |
| `invalid_redirect_uri` | REDIRECT_URI not configured in IDCS | Add URI to IDCS application or use Client Credentials |
| `invalid_client`       | Wrong client credentials            | Verify CLIENT_ID and CLIENT_SECRET                    |
| `insufficient_scope`   | Missing scopes in IDCS              | Add required scopes to IDCS application               |
| `token_expired`        | Access token expired                | Implement automatic token refresh                     |
| `connection_timeout`   | Network connectivity issue          | Check firewall rules and DNS resolution               |

### 6.2 Debug Procedures

#### 6.2.1 Step-by-Step Debugging

```bash
# 1. Verify environment variables
echo "IDCS_URL: $IDCS_URL"
echo "CLIENT_ID: $CLIENT_ID"
echo "OIC_URL: $OIC_URL"

# 2. Test IDCS connectivity
curl -v https://$IDCS_URL/.well-known/openid_configuration

# 3. Test token acquisition
DEBUG=true oic_get_token

# 4. Test OIC API access
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     https://$OIC_URL/ic/api/integration/v1/integrations

# 5. Enable comprehensive logging
export OIC_DEBUG=true
export OIC_LOG_LEVEL=DEBUG
```

#### 6.2.2 Common Fix Commands

```bash
# Reset authentication state
unset ACCESS_TOKEN
rm -f /tmp/oic_token_cache

# Regenerate client credentials in IDCS
# Re-download wallet file for database connections
# Clear browser cache if using Authorization Code flow

# Test with minimal configuration
export MINIMAL_TEST=true
./scripts/oic_auth_test.sh
```

## 📚 **References**

### **Official Oracle Documentation**

- [Oracle OAuth 2.0 Documentation](https://docs.oracle.com/en/cloud/paas/integration-cloud/soap-adapter/using-oauth-2.0-grants-oracle-identity-cloud-service-environments.html)
- [Client Credentials Configuration](https://docs.oracle.com/en/cloud/paas/integration-cloud/oracle-integration-gov/configure-oauth-authentication-using-client-credentials.html)
- [IDCS Authentication Guide](https://docs.oracle.com/en/cloud/paas/identity-cloud/uaids/use-oauth-authentication.html)

### **Standards and Specifications**

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [RFC 6749 - OAuth 2.0 Framework](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

---

## 🆘 **Troubleshooting**

### **Common Authentication Issues**

- **🔑 Token Expiration**: Implement proper token refresh mechanisms with adequate time buffers
- **🔒 Scope Limitations**: Verify IDCS application scopes match required permissions exactly
- **🌐 Network Issues**: Check firewall rules, proxy configurations, and DNS resolution
- **📜 Certificate Problems**: Validate SSL/TLS certificates and trust stores configuration

### **Security Best Practices**

- **💾 Secure Storage**: Store credentials using environment variables or enterprise secret management
- **🔄 Token Management**: Implement proper token refresh and retry logic with exponential backoff
- **⚡ Least Privilege**: Use minimum required scopes for IDCS application permissions
- **📋 Audit Logging**: Enable comprehensive logging for security audit trails

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before implementing authentication
- [Security Hub](../../security/index.md) - Framework security patterns and enterprise security concepts
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and basic configuration

### **Next Steps**

- [Oracle Security Guide](./oracle-security-guide.md) - Implement comprehensive security controls for Oracle environments
- [Integration Comprehensive Guide](./oracle-integration-comprehensive-guide.md) - Use OAuth2 for secure Oracle integrations
- [WMS Integration Project Plan](./oracle-wms-integration-project-plan.md) - Apply OAuth2 authentication in WMS integration projects

### **Related Topics**

- [WMS Commands Reference](./oracle-wms-commands-reference.md) - WMS-specific authentication and API access patterns
- [Implementation Patterns](./oracle-implementation-patterns.md) - Enterprise integration patterns with OAuth2 security
- [Development Standards](../../development/standards/index.md) - Security coding standards and best practices
- [Architecture Security](../../architecture/security/index.md) - Security architecture patterns for enterprise systems
- [Infrastructure Security](../../infrastructure/security/index.md) - Infrastructure security patterns for OAuth2 implementations

---

**📂 Hub**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
