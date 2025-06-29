# Oracle Authentication Complete Guide

> **Part of Oracle Integration Hub** | [← Back to Oracle Hub](README.md)

## Overview

Complete Oracle authentication guide for the FLX framework, covering OAuth2, JWT, SSO, database authentication, and security best practices for all Oracle systems including OIC, WMS, and Database integrations.

## 🎯 Quick Navigation

- [**Authentication Methods**](#-authentication-methods) - Overview of all methods
- [**OAuth2 Client Credentials**](#-oauth2-client-credentials) - Recommended for automation
- [**OAuth2 Authorization Code**](#-oauth2-authorization-code) - Interactive flows
- [**Database Authentication**](#-database-authentication) - Oracle Database security
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
- **Production environments** with high security requirements

### IDCS (Identity Cloud Service) Configuration

#### Step-by-Step IDCS Setup

1. **Access IDCS Console**

   ```
   Navigate to: https://cloud.oracle.com
   → Identity & Security → Identity Cloud Service
   ```

2. **Create Confidential Application**

   ```
   Applications → Add → Confidential Application
   Name: "FLX-Oracle-Integration"
   Description: "FLX Framework Oracle Integration Client"
   ```

3. **Configure Client Settings**

   ```
   Configuration → General Information
   ✅ Configure this application as a client now
   ```

4. **Grant Types Configuration**

   ```
   Grant Types:
   ✅ Client Credentials
   ☐ Authorization Code (optional for interactive flows)
   ```

5. **Resource Configuration**

   ```
   Resources → Primary Audience:
   https://instance-name.integration.ocp.oraclecloud.com:443

   Resources → Scope:
   urn:opc:resource:consumer::all     # For calling integrations
   /ic/api/                           # For calling administrative APIs
   ```

6. **Role Assignment**

   ```
   Go to OIC Application in IDCS
   → Application Roles → ServiceUser
   → Assign Users → Add your Client Application
   ```

7. **Activate Application**

   ```
   Activate the application and note:
   - Client ID
   - Client Secret
   ```

### Environment Configuration

#### Critical Environment Variables

```bash
# IDCS Configuration
IDCS_URL=idcs-xxxx.identity.oraclecloud.com
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Resource Audiences (CRITICAL - Format is important!)
RESOURCE_AUD=https://XXXX.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
API_AUD=https://XXXX.integration.ocp.oraclecloud.com:443/ic/api/

# OIC Instance URL
OIC_URL=https://instance-name.integration.ocp.oraclecloud.com

# WMS Configuration (if using WMS)
WMS_BASE_URL=https://your-wms.oracle.com
WMS_USERNAME=wms_user
WMS_PASSWORD=wms_password
```

**⚠️ CRITICAL FORMAT NOTES**:

- In `RESOURCE_AUD`: NO slash between port (443) and "urn"
- In `API_AUD`: There IS a slash after port (443)
- URLs must include `https://`

### FLX Framework Implementation

#### Using FLX OAuth2 Service

```python
from flext.adapters.oracle.auth import OracleAuthenticationService
from flext.infrastructure.http import FlxJwtService

# Initialize OAuth2 authentication
auth_service = OracleAuthenticationService(
    idcs_url=os.getenv('IDCS_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    resource_aud=os.getenv('RESOURCE_AUD'),
    api_aud=os.getenv('API_AUD')
)

# Get authenticated client for OIC
oic_client = await auth_service.get_oic_client()

# Get authenticated client for WMS
wms_client = await auth_service.get_wms_client()

# Use clients for API calls
integrations = await oic_client.list_integrations()
orders = await wms_client.get_orders()
```

#### Token Management with Caching

```python
from flext.adapters.oracle.oic import OICAuthenticator

# Initialize with automatic token management
auth = OICAuthenticator(
    idcs_url=os.getenv('IDCS_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    resource_aud=os.getenv('RESOURCE_AUD'),
    api_aud=os.getenv('API_AUD'),
    cache_tokens=True,      # Enable token caching
    auto_refresh=True,      # Automatic token refresh
    cache_duration=3300     # 55 minutes (tokens expire in 1 hour)
)

# Get authenticated session
session = await auth.get_authenticated_session()

# Session automatically handles token refresh
response = await session.get('/ic/api/integration/v1/integrations')
```

#### Error Handling and Resilience

```python
import asyncio
from flext.adapters.oracle.oic import OICClient, OICAuthError
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def robust_oauth_call(endpoint, max_retries=3):
    """Make OAuth-authenticated API call with robust error handling."""

    try:
        # Initialize OIC client with OAuth2
        client = OICClient()

        # Authenticate and make call
        response = await client.authenticated_request('GET', endpoint)
        return response

    except OICAuthError as e:
        logger.error(f"OAuth authentication failed: {e}")
        # Token might be expired, force refresh
        await client.refresh_token()
        raise

    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise

# Usage with automatic retry
try:
    integrations = await robust_oauth_call('/ic/api/integration/v1/integrations')
    print(f"Successfully retrieved integrations: {integrations}")
except Exception as e:
    print(f"Failed to retrieve integrations after retries: {e}")
```

### Shell Script Integration

```bash
#!/bin/bash
# oauth2_client_credentials.sh

# Load environment variables
source .env

# Function to get OAuth2 token
get_oauth_token() {
    local token_response
    token_response=$(curl -s -X POST "https://${IDCS_URL}/oauth2/v1/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -u "${CLIENT_ID}:${CLIENT_SECRET}" \
        -d "grant_type=client_credentials&scope=${RESOURCE_AUD}%20${API_AUD}")

    echo "$token_response" | jq -r '.access_token'
}

# Function to make authenticated API call
oic_api_call() {
    local endpoint="$1"
    local token
    token=$(get_oauth_token)

    if [[ "$token" == "null" || -z "$token" ]]; then
        echo "❌ Failed to get OAuth token"
        return 1
    fi

    curl -s -H "Authorization: Bearer $token" \
         -H "Content-Type: application/json" \
         "${OIC_URL}${endpoint}"
}

# Example usage
echo "🔐 Getting OAuth2 token..."
TOKEN=$(get_oauth_token)

if [[ "$TOKEN" != "null" && -n "$TOKEN" ]]; then
    echo "✅ OAuth2 authentication successful"

    # List integrations
    echo "📋 Listing integrations..."
    INTEGRATIONS=$(oic_api_call "/ic/api/integration/v1/integrations")
    echo "$INTEGRATIONS" | jq '.items[].name'
else
    echo "❌ OAuth2 authentication failed"
    exit 1
fi
```

## 👤 OAuth2 Authorization Code

### For Interactive Applications

This method requires user interaction and is **not recommended for automation**, especially if MFA is enabled.

### When to Use Authorization Code

- **Explicit user interaction** is desired or necessary
- Need to **authenticate with specific user context**
- Implementing a **web application or client with UI**
- Want **granular permissions** based on user

### Additional IDCS Configuration

In addition to Client Credentials setup:

1. **Grant Types**: Add "Authorization Code" to Grant Types
2. **Redirect URL**: Add your callback URL:

   ```
   https://your-app.com/oauth/callback
   ```

3. **Public Key**: Configure if using PKCE
4. **Logout URL**: Configure post-logout redirect

### Environment Variables

```bash
# Additional variables for Authorization Code flow
REDIRECT_URI=https://your-app.com/oauth/callback
SCOPE="${RESOURCE_AUD} offline_access"
STATE=random_secure_state_value
```

### Implementation Example

```python
from flext.adapters.oracle.auth import OAuthAuthorizationCodeFlow

# Initialize authorization code flow
auth_flow = OAuthAuthorizationCodeFlow(
    idcs_url=os.getenv('IDCS_URL'),
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    redirect_uri=os.getenv('REDIRECT_URI'),
    scope=os.getenv('SCOPE')
)

# Step 1: Get authorization URL
auth_url = auth_flow.get_authorization_url(state="secure_random_state")
print(f"Visit this URL to authorize: {auth_url}")

# Step 2: User visits URL and authorizes
# Step 3: User is redirected to redirect_uri with authorization code

# Step 4: Exchange authorization code for tokens
authorization_code = "code_received_from_redirect"
tokens = await auth_flow.exchange_code_for_tokens(authorization_code)

# Step 5: Use access token for API calls
authenticated_client = auth_flow.get_authenticated_client(tokens.access_token)
integrations = await authenticated_client.list_integrations()
```

## 💾 Database Authentication

### Oracle Database Security

For direct Oracle Database connections, use secure authentication methods:

#### Connection String Authentication

```python
from flext_database_oracle import DatabaseConfig, DatabasePlugin

# Secure database configuration
config = DatabaseConfig(
    host="oracle-db.company.com",
    port=1521,
    service_name="ORCL",
    username="flext_service_user",
    password=os.getenv("ORACLE_PASSWORD"),  # From secure storage
    # SSL Configuration
    ssl_mode=True,
    ssl_verify=True,
    ssl_ca_cert="/path/to/ca-cert.pem",
    # Connection security
    connect_timeout=30,
    pool_min=2,
    pool_max=10,
    # Additional security
    enable_monitoring=True,
    log_performance=True,
    log_queries=False  # Don't log queries in production
)

plugin = DatabasePlugin(config)
```

#### Wallet-Based Authentication

```python
# Using Oracle Wallet for authentication
config = DatabaseConfig(
    # Connection via wallet
    wallet_location="/path/to/wallet",
    wallet_password=os.getenv("WALLET_PASSWORD"),
    connect_string="tcps://oracle-cloud.com:1522/service_name",
    # Security settings
    ssl_mode=True,
    ssl_verify=True,
)
```

#### Environment Variables for Database

```bash
# Oracle Database Authentication
ORACLE_HOST=oracle-db.company.com
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=ORCL
ORACLE_USERNAME=flext_service_user
ORACLE_PASSWORD=secure_password_from_vault

# SSL Configuration
ORACLE_SSL_MODE=true
ORACLE_SSL_VERIFY=true
ORACLE_SSL_CA_CERT=/path/to/ca-cert.pem

# Wallet Configuration (for cloud)
ORACLE_WALLET_LOCATION=/path/to/wallet
ORACLE_WALLET_PASSWORD=wallet_password
```

## 🔒 Security Best Practices

### Production Security Standards

#### 1. Credential Management

**Secure Storage**

```bash
# Use encrypted credential storage
python -m flext.security create-credential-store \
    --encrypted \
    --output ./secure/credentials.enc \
    --key-file ./secure/encryption.key

# Set secure file permissions
chmod 600 ./secure/credentials.enc
chmod 600 ./secure/encryption.key
chmod 700 ./secure/
```

**Environment Variable Security**

```bash
# Use secure environment loading
source <(gpg --decrypt credentials.env.gpg)

# Or use dedicated secret management
export CLIENT_SECRET=$(vault kv get -field=client_secret secret/oracle/credentials)
export ORACLE_PASSWORD=$(aws ssm get-parameter --name "/oracle/password" --with-decryption --query 'Parameter.Value' --output text)
```

**Secret Rotation**

```python
from flext.security import CredentialRotationService

# Automatic credential rotation
rotation_service = CredentialRotationService(
    rotation_interval=timedelta(days=30),
    providers={
        'oracle_oauth': OAuthCredentialProvider(),
        'oracle_db': DatabaseCredentialProvider()
    }
)

# Schedule automatic rotation
await rotation_service.schedule_rotation()
```

#### 2. Network Security

**SSL/TLS Configuration**

```python
# Enforce SSL for all connections
config = {
    'ssl_mode': True,
    'ssl_verify': True,
    'ssl_ca_cert': '/path/to/ca-bundle.pem',
    'ssl_cert': '/path/to/client-cert.pem',
    'ssl_key': '/path/to/client-key.pem'
}
```

**Certificate Pinning**

```python
import ssl
from flext.security import CertificatePinner

# Pin Oracle Cloud certificates
cert_pinner = CertificatePinner([
    'oracle.com',
    'oraclecloud.com',
    'integration.ocp.oraclecloud.com'
])

# Use in HTTP clients
ssl_context = ssl.create_default_context()
cert_pinner.configure_context(ssl_context)
```

**IP Whitelisting**

```bash
# Configure network access control
# In Oracle Cloud Console:
# 1. Go to Networking → Security Lists
# 2. Add ingress rules for your application IPs
# 3. Configure IDCS IP restrictions
```

#### 3. Authentication Monitoring

**Monitor Authentication Events**

```python
from flext.adapters.oracle.auth import AuthenticationMonitor

# Initialize monitoring
auth_monitor = AuthenticationMonitor(
    log_successful_auth=True,
    log_failed_auth=True,
    alert_on_suspicious_activity=True
)

# Track authentication events
await auth_monitor.log_event(
    event_type='oauth_token_acquired',
    client_id=client_id,
    success=True,
    timestamp=datetime.now(),
    source_ip=request.remote_addr
)

# Generate security reports
security_report = await auth_monitor.generate_security_report(
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)
```

**Audit Logging**

```python
from flext.logging import SecurityAuditLogger

# Configure security audit logging
audit_logger = SecurityAuditLogger(
    log_level='INFO',
    output_format='json',
    include_sensitive_data=False,
    retention_days=90
)

# Log security events
await audit_logger.log_security_event(
    event_type='authentication_attempt',
    user_id=user_id,
    client_id=client_id,
    result='success',
    metadata={
        'authentication_method': 'oauth2_client_credentials',
        'resource_accessed': '/ic/api/integration/v1/integrations',
        'timestamp': datetime.now().isoformat()
    }
)
```

#### 4. Token Security

**Token Lifecycle Management**

```python
from flext.adapters.oracle.auth import TokenManager

# Secure token management
token_manager = TokenManager(
    cache_duration=3300,  # 55 minutes (tokens expire in 1 hour)
    refresh_threshold=300,  # Refresh 5 minutes before expiry
    secure_storage=True,
    encryption_key=os.getenv('TOKEN_ENCRYPTION_KEY')
)

# Get token with automatic refresh
token = await token_manager.get_valid_token(
    client_id=client_id,
    client_secret=client_secret,
    scopes=['urn:opc:resource:consumer::all']
)
```

**Token Validation**

```python
from flext.adapters.oracle.auth import TokenValidator

# Validate token before use
validator = TokenValidator()

if await validator.is_token_valid(token):
    # Use token for API call
    response = await make_authenticated_request(token, endpoint)
else:
    # Token is invalid, refresh
    token = await token_manager.refresh_token()
```

### Security Configuration Template

```yaml
# config/security.yaml
oracle_security:
  authentication:
    # OAuth2 settings
    oauth2:
      token_cache_enabled: true
      token_refresh_threshold: 300
      max_retry_attempts: 3

    # Database settings
    database:
      ssl_required: true
      ssl_verify_certificates: true
      connection_timeout: 30

  network:
    # SSL/TLS settings
    ssl:
      enforce_tls: true
      min_tls_version: "1.2"
      certificate_pinning: true

    # Access control
    access_control:
      ip_whitelist_enabled: true
      allowed_ips:
        - "192.168.1.0/24"
        - "10.0.0.0/8"

  monitoring:
    # Audit settings
    audit:
      log_authentication_events: true
      log_api_calls: true
      alert_on_failures: true
      retention_days: 90

    # Security alerts
    alerts:
      failed_auth_threshold: 5
      suspicious_activity_detection: true
      notification_channels:
        - "security-team@company.com"
        - "slack://security-alerts"
```

## 🚨 Troubleshooting

### Common Authentication Issues

#### OAuth2 Token Issues

**Issue**: `invalid_client` error

```bash
# Verify client credentials
curl -X POST "https://${IDCS_URL}/oauth2/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=${RESOURCE_AUD}%20${API_AUD}"

# Check response for specific error details
```

**Solution**:

- Verify CLIENT_ID and CLIENT_SECRET are correct
- Ensure client application is activated in IDCS
- Check that client has proper grant types configured

**Issue**: `insufficient_scope` error

```bash
# Verify scope configuration in IDCS
echo "Configured scopes in IDCS application:"
echo "- urn:opc:resource:consumer::all"
echo "- /ic/api/"

# Check actual requested scopes
echo "RESOURCE_AUD: $RESOURCE_AUD"
echo "API_AUD: $API_AUD"
```

**Solution**:

- Add missing scopes to IDCS application
- Verify scope format in environment variables
- Ensure client has access to requested resources

**Issue**: Token obtained but API calls fail (403 Forbidden)

```bash
# Verify OIC_URL format
echo "OIC_URL: $OIC_URL"

# Check ServiceUser role assignment
echo "Verify ServiceUser role assignment in IDCS"

# Test API endpoint directly
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     "$OIC_URL/ic/api/integration/v1/integrations"
```

**Solution**:

- Assign client application to ServiceUser role in IDCS
- Verify OIC_URL includes https:// and correct domain
- Check that target API endpoints are accessible

#### Database Authentication Issues

**Issue**: Connection refused or timeout

```python
# Test basic connectivity
import socket

def test_oracle_connectivity(host, port):
    try:
        socket.create_connection((host, port), timeout=10)
        print(f"✅ Successfully connected to {host}:{port}")
        return True
    except Exception as e:
        print(f"❌ Cannot connect to {host}:{port}: {e}")
        return False

test_oracle_connectivity("oracle-db.company.com", 1521)
```

**Solution**:

- Check network connectivity and firewall rules
- Verify database host and port are correct
- Ensure database service is running

**Issue**: Authentication failed (ORA-01017)

```python
# Test credentials with minimal connection
import oracledb

try:
    connection = oracledb.connect(
        user="your_username",
        password="your_password",
        dsn="host:port/service_name"
    )
    print("✅ Database authentication successful")
    connection.close()
except Exception as e:
    print(f"❌ Database authentication failed: {e}")
```

**Solution**:

- Verify username and password are correct
- Check if account is locked or expired
- Ensure user has necessary privileges

### Diagnostic Commands

#### OAuth2 Diagnostics

```bash
# Configuration validation
echo "=== OAuth2 Configuration Check ==="
echo "IDCS_URL: $IDCS_URL"
echo "CLIENT_ID: $CLIENT_ID"
echo "CLIENT_SECRET: ${CLIENT_SECRET:0:4}***" # Show only first 4 chars
echo "OIC_URL: $OIC_URL"
echo "RESOURCE_AUD: $RESOURCE_AUD"
echo "API_AUD: $API_AUD"

# Test IDCS connectivity
echo "=== IDCS Connectivity Test ==="
curl -v "https://${IDCS_URL}/.well-known/openid_configuration"

# Test token acquisition
echo "=== Token Acquisition Test ==="
TOKEN_RESPONSE=$(curl -s -X POST "https://${IDCS_URL}/oauth2/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=${RESOURCE_AUD}%20${API_AUD}")

echo "$TOKEN_RESPONSE" | jq '.'

# Extract and test token
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')
if [[ "$ACCESS_TOKEN" != "null" ]]; then
    echo "=== API Access Test ==="
    curl -H "Authorization: Bearer $ACCESS_TOKEN" \
         -H "Content-Type: application/json" \
         "$OIC_URL/ic/api/integration/v1/integrations" | jq '.'
fi
```

#### Database Diagnostics

```bash
# Database connectivity test
echo "=== Database Connectivity Test ==="
python -c "
import oracledb
import os

try:
    conn = oracledb.connect(
        user=os.getenv('ORACLE_USERNAME'),
        password=os.getenv('ORACLE_PASSWORD'),
        dsn=f\"{os.getenv('ORACLE_HOST')}:{os.getenv('ORACLE_PORT')}/{os.getenv('ORACLE_SERVICE_NAME')}\"
    )
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION FROM v\$instance')
    version = cursor.fetchone()[0]
    print(f'✅ Connected to Oracle Database version: {version}')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

#### Network Diagnostics

```bash
# Network connectivity tests
echo "=== Network Diagnostics ==="

# Test IDCS connectivity
echo "Testing IDCS connectivity..."
nc -zv $(echo $IDCS_URL | cut -d'/' -f3) 443

# Test OIC connectivity
echo "Testing OIC connectivity..."
nc -zv $(echo $OIC_URL | cut -d'/' -f3) 443

# Test Oracle Database connectivity
echo "Testing Oracle Database connectivity..."
nc -zv $ORACLE_HOST $ORACLE_PORT

# DNS resolution test
echo "Testing DNS resolution..."
nslookup $(echo $IDCS_URL | cut -d'/' -f3)
nslookup $(echo $OIC_URL | cut -d'/' -f3)
nslookup $ORACLE_HOST
```

### Error Resolution Matrix

| Error Code           | System   | Cause                   | Solution                |
| -------------------- | -------- | ----------------------- | ----------------------- |
| `invalid_client`     | OAuth2   | Wrong credentials       | Verify CLIENT_ID/SECRET |
| `insufficient_scope` | OAuth2   | Missing permissions     | Add scopes to IDCS app  |
| `token_expired`      | OAuth2   | Token expired           | Implement auto-refresh  |
| `ORA-01017`          | Database | Auth failed             | Check credentials       |
| `ORA-12541`          | Database | Connection refused      | Check network/firewall  |
| `403 Forbidden`      | API      | Insufficient privileges | Check role assignment   |
| `Connection timeout` | Network  | Network issue           | Check connectivity/DNS  |

## 📖 Related Documentation

- [Oracle Integration Hub](README.md) - Main Oracle documentation hub
- [Oracle WMS Integration](wms-complete-guide.md) - WMS authentication patterns
- [Oracle OIC Integration](oic-complete-guide.md) - OIC OAuth2 implementation
- [Oracle Database Integration](database-complete-guide.md) - Database security
- [FLX Security Architecture](../../architecture/security-architecture.md) - Framework security
- [Production Deployment](../../deployment/oracle-deployment.md) - Production security

## 🆘 Support

For authentication support:

1. Use diagnostic commands to identify specific issues
2. Check Oracle Cloud Console for IDCS configuration
3. Verify network connectivity with network diagnostic tools
4. Review audit logs for authentication attempts
5. Test with minimal configurations to isolate problems

---

**Security Level**: 🔒 **Enterprise Grade**
**Compliance**: OAuth2 RFC 6749, Oracle Cloud Security Standards
**Last Updated**: January 2025

---

_This comprehensive authentication guide provides complete security implementation for all Oracle integrations within the FLX framework, ensuring enterprise-grade security and compliance._
