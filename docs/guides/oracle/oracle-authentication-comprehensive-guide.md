# 🔐 Oracle Authentication Comprehensive Guide

> **Function**: Complete Oracle Cloud authentication and security implementation | **Audience**: Security engineers, integration engineers | **Status**: Production-ready

[![OAuth2](https://img.shields.io/badge/auth-oauth2-green.svg)](./oracle-oauth2-authentication-guide.md)
[![JWT](https://img.shields.io/badge/jwt-service-blue.svg)](../authentication/jwt-service-guide.md)
[![Security](https://img.shields.io/badge/security-enterprise-red.svg)](../../security/index.md)

**Complete authentication guide for Oracle Cloud services including OAuth2, JWT, SAML2 SSO, and legacy authentication methods covering Oracle Integration Cloud (OIC), Oracle WMS Cloud, and FLX framework integration patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: Authentication Comprehensive Guide

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[Authentication Comprehensive Guide]** → [OAuth2 Guide](./oracle-oauth2-authentication-guide.md)
```

## Table of Contents

1. [Authentication Overview](#authentication-overview)
2. [OAuth2 Configuration and Patterns](#oauth2-configuration-and-patterns)
3. [JWT Service Implementation (FLX)](#jwt-service-implementation-flext)
4. [SAML2 SSO Setup and Configuration](#saml2-sso-setup-and-configuration)
5. [Oracle WMS Authentication](#oracle-wms-authentication)
6. [OIC-Specific Authentication](#oic-specific-authentication)
7. [Troubleshooting and Security Best Practices](#troubleshooting-and-security-best-practices)

## Authentication Overview

Oracle Cloud services support multiple authentication methods to accommodate different integration patterns and security requirements:

### Available Authentication Methods

- **OAuth2 Client Credentials** - Recommended for machine-to-machine integration
- **OAuth2 Resource Owner Password Credentials (ROPC)** - For user authentication with delegation
- **SAML2 Single Sign-On (SSO)** - Web-based single sign-on
- **JWT Service (FLX)** - Managed JWT authentication within FLX framework
- **Basic Authentication** - Legacy authentication for older integrations
- **Native Authentication** - Direct username/password authentication

### Method Selection Criteria

| Use Case              | Recommended Method        | Alternative               |
| --------------------- | ------------------------- | ------------------------- |
| **Automation/CI/CD**  | OAuth2 Client Credentials | JWT Service (FLX)         |
| **Server-to-Server**  | OAuth2 Client Credentials | Basic Auth (legacy)       |
| **MFA Environments**  | OAuth2 Client Credentials | JWT Service (FLX)         |
| **Web Applications**  | SAML2 SSO                 | OAuth2 ROPC               |
| **Mobile/RF Devices** | OAuth2 ROPC               | Native Authentication     |
| **FLX Framework**     | JWT Service               | OAuth2 Client Credentials |

## OAuth2 Configuration and Patterns

### 🚨 CRITICAL SECURITY NOTICE

Proper OAuth2 authentication is **CRITICAL** for secure system-to-system communication. Misconfiguration can lead to security vulnerabilities and service disruptions.

### Client Credentials Flow (Recommended)

#### When to Use Client Credentials

Choose this flow when:

- **Automation without user intervention** is required
- Implementing **CI/CD integrations**
- System has **MFA enabled**
- Integration has **no user interface** for login
- Need **server-to-server integration**
- **Production environments** with high security requirements

#### IDCS (Identity Cloud Service) Configuration

**Step-by-Step IDCS Setup:**

1. **Access IDCS Console**

   - Navigate to the IDCS console associated with your Oracle Cloud environment
   - URL format: `https://idcs-[hash].identity.oraclecloud.com`

2. **Create Confidential Application**

   ```
   Applications > Add > Confidential Application
   ```

3. **Basic Configuration**

   - Set descriptive name for the application
   - Description should include purpose and owner information

4. **Client Configuration**

   ```
   Configuration > General Information
   ✓ Configure this application as a client now
   ```

5. **Grant Types Selection**

   ```
   Grant Types Section:
   ✓ Client Credentials (for automation)
   ✓ Resource Owner Password Credentials (if user auth needed)
   ```

6. **Primary Audience Configuration**

   ```
   Resources > Primary Audience
   Add: https://instance-name.integration.ocp.oraclecloud.com:443
   ```

7. **Scope Configuration**

   ```
   Resources > Scope
   Add the following scopes:
   - urn:opc:resource:consumer::all (for calling integrations)
   - /ic/api/ (for administrative APIs)
   ```

8. **Application Activation**
   - Finalize creation and activate the application
   - Assign application to "ServiceUser" role in OIC application

#### Environment Variables Configuration

**For OAuth2 Client Credentials:**

```bash
# IDCS Configuration
export IDCS_URL="idcs-xxxx.identity.oraclecloud.com"
export CLIENT_ID="your_client_id_here"
export CLIENT_SECRET="your_client_secret_here"

# Resource Audience (OIC Base URL + Resource Identifier)
export RESOURCE_AUD="https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all"

# API Audience (OIC Base URL + API Path)
export API_AUD="https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/"

# OIC Instance Configuration
export OIC_HOST="instance-name.integration.ocp.oraclecloud.com"
export OIC_PORT="443"
export OIC_USE_SSL="true"
```

#### Python Implementation Example

```python
import requests
from typing import Dict, Optional
import base64
import json

class OracleOAuth2Client:
    def __init__(self, idcs_url: str, client_id: str, client_secret: str):
        self.idcs_url = idcs_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.token_type: str = "Bearer"

    def get_access_token(self, resource_aud: str) -> Dict:
        """Get OAuth2 access token using client credentials flow."""

        # Prepare token request
        token_url = f"https://{self.idcs_url}/oauth2/v1/token"

        # Basic authentication header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials",
            "scope": resource_aud
        }

        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]

        return token_data

    def make_authenticated_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make authenticated request to Oracle services."""

        if not self.access_token:
            raise ValueError("No access token available. Call get_access_token() first.")

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"{self.token_type} {self.access_token}"
        kwargs["headers"] = headers

        return requests.request(method, url, **kwargs)
```

### Resource Owner Password Credentials (ROPC) Flow

#### Configuration for ROPC

```bash
# Additional environment variables for ROPC
export USERNAME="oracle_username"
export PASSWORD="oracle_password"
export X_USER_IDENTITY_DOMAIN_NAME="domain_name"
```

#### ROPC Implementation

```python
def get_access_token_ropc(self, username: str, password: str, resource_aud: str) -> Dict:
    """Get OAuth2 access token using Resource Owner Password Credentials flow."""

    token_url = f"https://{self.idcs_url}/oauth2/v1/token"

    credentials = f"{self.client_id}:{self.client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": resource_aud
    }

    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    return response.json()
```

## JWT Service Implementation (FLX)

### Overview

The **FLX JWT Service** provides OAuth2 JWT authentication and token management as a reusable service within the FLX ecosystem.

### Key Features

- 🔑 **Automatic Token Management** - Handles token acquisition, refresh, and expiry
- 🛡️ **Security Best Practices** - Uses OAuth2 client credentials flow with proper validation
- 🔄 **Auto-Refresh** - Automatically refreshes tokens before expiry
- 📊 **Health Monitoring** - Built-in health checks and service monitoring
- 🏗️ **Multiple Patterns** - Supports Oracle OIC, generic OAuth2, and custom configurations
- 🎯 **FLX Integration** - Seamlessly integrates with FLX HTTP infrastructure

### FLX Architecture Integration

```
FLX Infrastructure
├── HTTP Layer
│   ├── FlxHttpAuthManager (Extended with OAuth2 JWT)
│   ├── FlxJwtService (New high-level service)
│   └── FlxOAuth2TokenData (Token data model)
└── Applications
    └── flext-http-oracle-oic (Uses JWT service)
```

### Basic FLX JWT Usage

#### Oracle OIC Configuration

```python
from flext.infrastructure.http.auth import FlxJwtService

# For Oracle Integration Cloud
jwt_service = FlxJwtService.for_oracle_oic(
    idcs_url="idcs-xxxx.identity.oraclecloud.com",
    client_id="your_client_id",
    client_secret="your_client_secret",
    oic_base_url="https://instance-name.integration.ocp.oraclecloud.com"
)
```

#### Generic OAuth2 Configuration

```python
# For generic OAuth2 providers
jwt_service = FlxJwtService.for_oauth2(
    token_url="https://provider.com/oauth2/token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    scope="your_scope"
)
```

#### Advanced Configuration

```python
from flext.infrastructure.http.auth import FlxOAuth2Config

# Custom configuration
config = FlxOAuth2Config(
    token_url="https://idcs-xxxx.identity.oraclecloud.com/oauth2/v1/token",
    client_id="your_client_id",
    client_secret="your_client_secret",
    grant_type="client_credentials",
    scope="urn:opc:resource:consumer::all",
    additional_params={
        "resource": "https://instance.ocp.oraclecloud.com:443"
    },
    token_refresh_margin_seconds=300,  # Refresh 5 minutes before expiry
    max_retries=3,
    timeout_seconds=30
)

jwt_service = FlxJwtService(config)
```

### Using JWT Service in Applications

```python
import asyncio
from flext.adapters.outbound.http import HTTPAdapter

async def main():
    # Initialize JWT service
    jwt_service = FlxJwtService.for_oracle_oic(
        idcs_url="idcs-xxxx.identity.oraclecloud.com",
        client_id="your_client_id",
        client_secret="your_client_secret",
        oic_base_url="https://instance-name.integration.ocp.oraclecloud.com"
    )

    # Create HTTP adapter with JWT authentication
    http_adapter = HTTPAdapter(auth_manager=jwt_service)

    # Make authenticated requests
    response = await http_adapter.get("https://instance-name.integration.ocp.oraclecloud.com/ic/api/integrations")

    # JWT service handles token refresh automatically
    data = response.json()
    print(f"Found {len(data.get('items', []))} integrations")

asyncio.run(main())
```

### JWT Health Monitoring

```python
# Check JWT service health
health_status = await jwt_service.health_check()
print(f"JWT Service Status: {health_status}")

# Monitor token status
token_info = jwt_service.get_token_info()
print(f"Token expires in: {token_info.expires_in} seconds")
print(f"Token will refresh in: {token_info.refresh_in} seconds")
```

## SAML2 SSO Setup and Configuration

### Overview

SAML2 Single Sign-On provides web-based authentication by redirecting users to an Identity Provider (IDP) and returning a SAML token.

### Supported Identity Providers

- **Oracle Identity Cloud Service (IDCS)**
- **Azure Active Directory (Azure AD)**
- **Generic SAML2-compatible providers**

### Configuration Process

#### 1. WMS Cloud Configuration

**Associate users with alternate usernames:**

```
User Format: <username>@<domain>
Example: john.doe@company.com
```

**Key Points:**

- Users can maintain local authentication while others use SSO
- Alternate username mapping is required for SSO users
- Domain configuration must match IDP settings

#### 2. Metadata Exchange

**Items required from client:**

- SAML2.0 Metadata (XML file or URL)
- Certificate in PEM format for signature validation
- Issuer ID
- Single Sign-On URL
- Assertion Consumer Service URL

**Oracle provides:**

- Service Provider metadata
- Entity ID and endpoints
- Certificate for encryption (if required)

#### 3. Service Request Parameters

When requesting SAML2 SSO setup, provide:

```
- IDP Name and description
- Metadata URL or XML file
- Signing certificate (PEM format)
- Issuer identifier
- SSO endpoint URL
- ACS endpoint URL
- X-USER-IDENTITY-DOMAIN-NAME for user mapping
```

### SAML2 Technical Implementation

```xml
<!-- Example SAML2 Metadata Structure -->
<md:EntityDescriptor entityID="https://your-idp.com/saml2">
  <md:IDPSSODescriptor>
    <md:KeyDescriptor use="signing">
      <ds:KeyInfo>
        <ds:X509Data>
          <ds:X509Certificate>MII...</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </md:KeyDescriptor>
    <md:SingleSignOnService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
      Location="https://your-idp.com/sso"/>
  </md:IDPSSODescriptor>
</md:EntityDescriptor>
```

## Oracle WMS Authentication

### Supported Methods in WMS Cloud Release 25B

#### 1. Native Authentication

**For:** Web access, Mobile App, RF devices

- Traditional username/password authentication
- Local user management
- No external dependencies

#### 2. OAuth2 (ROPC Flow)

**For:** Web, Mobile App, RF devices

- Delegates credential validation to Identity Provider
- Resource Owner Password Credentials flow
- Supports MFA through IDP

#### 3. SAML2 SSO

**For:** Web access only

- Single Sign-On experience
- Redirects to IDP for authentication
- Returns SAML token for session

### WMS OAuth2 Configuration

#### Required Parameters for Service Request

```
IDP Name: Azure AD / IDCS / Custom
Token Endpoint: https://provider.com/oauth2/token
Client ID: application_client_id
Client Secret: application_client_secret
Resource/Scope: target_resource_identifier
X-USER-IDENTITY-DOMAIN-NAME: domain_for_user_mapping
```

#### Environment Variables for WMS OAuth2

```bash
# WMS OAuth2 Configuration
export WMS_IDP_NAME="AzureAD"
export WMS_TOKEN_ENDPOINT="https://login.microsoftonline.com/tenant/oauth2/v2.0/token"
export WMS_CLIENT_ID="wms_client_id"
export WMS_CLIENT_SECRET="wms_client_secret"
export WMS_RESOURCE="https://wms.company.com"
export WMS_USER_DOMAIN="company.com"
```

### WMS Authentication Implementation

```python
class WMSAuthenticator:
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()

    def authenticate_oauth2(self, username: str, password: str) -> Dict:
        """Authenticate using OAuth2 ROPC flow for WMS."""

        token_data = {
            "grant_type": "password",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "username": f"{username}@{self.config['user_domain']}",
            "password": password,
            "scope": self.config["resource"]
        }

        response = self.session.post(
            self.config["token_endpoint"],
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        response.raise_for_status()
        return response.json()

    def authenticate_native(self, username: str, password: str) -> Dict:
        """Authenticate using native WMS authentication."""

        auth_data = {
            "username": username,
            "password": password,
            "company_code": self.config.get("company_code"),
            "facility_code": self.config.get("facility_code")
        }

        response = self.session.post(
            f"{self.config['wms_url']}/authenticate",
            json=auth_data
        )

        response.raise_for_status()
        return response.json()
```

## OIC-Specific Authentication

### Oracle Integration Cloud Authentication Patterns

#### Environment Configuration

```bash
# OIC Instance Configuration
export OIC_URL="https://instance-name.integration.ocp.oraclecloud.com"
export OIC_USERNAME="integration_user"
export OIC_PASSWORD="integration_password"

# OAuth2 Configuration for OIC
export IDCS_URL="idcs-xxxx.identity.oraclecloud.com"
export OIC_CLIENT_ID="oic_client_id"
export OIC_CLIENT_SECRET="oic_client_secret"

# Resource and API Audiences
export OIC_RESOURCE_AUD="https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all"
export OIC_API_AUD="https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/"
```

#### Shell Script Integration (oic.sh Library)

```bash
#!/bin/bash
# OIC Authentication Script

source ./oic.sh

# OAuth2 Client Credentials
oic_auth_oauth2() {
    local token_response
    token_response=$(curl -s -X POST \
        "https://${IDCS_URL}/oauth2/v1/token" \
        -H "Authorization: Basic $(echo -n "${CLIENT_ID}:${CLIENT_SECRET}" | base64)" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=client_credentials&scope=${RESOURCE_AUD}")

    ACCESS_TOKEN=$(echo "$token_response" | jq -r '.access_token')
    export ACCESS_TOKEN
}

# Make authenticated OIC API call
oic_api_call() {
    local endpoint="$1"
    local method="${2:-GET}"

    curl -s -X "$method" \
        "https://${OIC_HOST}${endpoint}" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json"
}

# Usage example
oic_auth_oauth2
integrations=$(oic_api_call "/ic/api/integrations/v1/integrations")
echo "Integrations: $integrations"
```

### OIC Integration Patterns

#### Integration Monitoring

```python
async def monitor_oic_integrations(jwt_service: FlxJwtService):
    """Monitor OIC integrations using JWT authentication."""

    http_adapter = HTTPAdapter(auth_manager=jwt_service)

    # Get all integrations
    integrations_response = await http_adapter.get(
        "https://instance-name.integration.ocp.oraclecloud.com/ic/api/integrations/v1/integrations"
    )

    integrations = integrations_response.json()

    for integration in integrations.get("items", []):
        integration_id = integration["id"]

        # Get integration status
        status_response = await http_adapter.get(
            f"https://instance-name.integration.ocp.oraclecloud.com/ic/api/integrations/v1/integrations/{integration_id}/status"
        )

        status = status_response.json()
        print(f"Integration {integration['name']}: {status['state']}")
```

#### Error Handling for OIC

```python
from flext.core.exceptions import AuthenticationError, ConnectionError

async def handle_oic_authentication_errors():
    try:
        jwt_service = FlxJwtService.for_oracle_oic(
            idcs_url="idcs-xxxx.identity.oraclecloud.com",
            client_id="invalid_client",
            client_secret="invalid_secret",
            oic_base_url="https://instance-name.integration.ocp.oraclecloud.com"
        )

        await jwt_service.get_access_token()

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        # Handle invalid credentials

    except ConnectionError as e:
        print(f"Connection failed: {e}")
        # Handle network issues

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle other errors
```

## Troubleshooting and Security Best Practices

### Common Authentication Issues

#### 1. OAuth2 Token Issues

**Symptoms:**

- 401 Unauthorized responses
- "invalid_client" errors
- Token expiration errors

**Solutions:**

```bash
# Verify IDCS configuration
curl -v "https://${IDCS_URL}/.well-known/openid_configuration"

# Test token endpoint
curl -X POST "https://${IDCS_URL}/oauth2/v1/token" \
  -H "Authorization: Basic $(echo -n "${CLIENT_ID}:${CLIENT_SECRET}" | base64)" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=${RESOURCE_AUD}"

# Validate token
curl -X POST "https://${IDCS_URL}/oauth2/v1/introspect" \
  -H "Authorization: Basic $(echo -n "${CLIENT_ID}:${CLIENT_SECRET}" | base64)" \
  -d "token=${ACCESS_TOKEN}"
```

#### 2. Audience Configuration Errors

**Common Issues:**

- Incorrect resource audience format
- Missing port in URL
- Wrong protocol (http vs https)

**Correct Formats:**

```bash
# Correct Resource Audience (no slash between port and urn)
RESOURCE_AUD="https://instance-name.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all"

# Correct API Audience (slash before /ic/api/)
API_AUD="https://instance-name.integration.ocp.oraclecloud.com:443/ic/api/"
```

#### 3. IDCS Application Configuration

**Checklist:**

- ✅ Application is activated
- ✅ Client Credentials grant type enabled
- ✅ Correct scopes configured
- ✅ Primary audience matches OIC URL
- ✅ Application assigned to ServiceUser role

#### 4. Certificate and SSL Issues

**Debugging:**

```bash
# Test SSL connection
openssl s_client -connect idcs-xxxx.identity.oraclecloud.com:443

# Verify certificate chain
curl -vvv "https://${IDCS_URL}/oauth2/v1/token"

# Test with insecure flag (debugging only)
curl -k "https://${IDCS_URL}/oauth2/v1/token"
```

### Security Best Practices

#### 1. Credential Management

```bash
# Use environment variables for secrets
export CLIENT_SECRET="$(cat /secure/path/client_secret)"

# Use vault or secrets manager in production
# aws secretsmanager get-secret-value --secret-id oic-client-secret
# kubectl get secret oic-credentials -o jsonpath='{.data.client-secret}' | base64 -d
```

#### 2. Token Security

- **Never log access tokens**
- **Implement token rotation**
- **Use short-lived tokens when possible**
- **Secure token storage**

```python
import logging

# Configure logging to avoid token exposure
class TokenFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            # Remove tokens from log messages
            record.msg = re.sub(r'Bearer [A-Za-z0-9\-_=]+', 'Bearer [REDACTED]', str(record.msg))
        return True

logging.getLogger().addFilter(TokenFilter())
```

#### 3. Network Security

```bash
# Use TLS 1.2 or higher
export SSL_VERSION="TLSv1.2"

# Verify SSL certificates
export SSL_VERIFY="true"

# Use connection timeouts
export CONNECTION_TIMEOUT="30"
export READ_TIMEOUT="60"
```

#### 4. Error Handling Security

```python
def secure_error_handling(func):
    """Decorator to handle authentication errors securely."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            # Log error without exposing credentials
            logger.error(f"Authentication failed for user: {getattr(e, 'username', 'unknown')}")
            raise AuthenticationError("Authentication failed. Check credentials.")
        except Exception as e:
            # Generic error without implementation details
            logger.error(f"Service error: {type(e).__name__}")
            raise ServiceError("Service temporarily unavailable")

    return wrapper
```

### Performance Optimization

#### 1. Token Caching

```python
import time
from typing import Optional

class TokenCache:
    def __init__(self):
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None

    def get_token(self) -> Optional[str]:
        if self._token and self._expires_at:
            # Return token if still valid (with 5-minute buffer)
            if time.time() < (self._expires_at - 300):
                return self._token
        return None

    def set_token(self, token: str, expires_in: int):
        self._token = token
        self._expires_at = time.time() + expires_in
```

#### 2. Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_http_session() -> requests.Session:
    """Create optimized HTTP session for authentication."""

    session = requests.Session()

    # Configure retries
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    # Configure adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session
```

### Monitoring and Alerting

#### Authentication Metrics

```python
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AuthMetrics:
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    last_success: Optional[float] = None
    last_failure: Optional[float] = None

class AuthMonitor:
    def __init__(self):
        self.metrics = AuthMetrics()
        self.response_times: List[float] = []

    def record_success(self, response_time: float):
        self.metrics.success_count += 1
        self.metrics.last_success = time.time()
        self.response_times.append(response_time)
        self._update_avg_response_time()

    def record_failure(self):
        self.metrics.failure_count += 1
        self.metrics.last_failure = time.time()

    def _update_avg_response_time(self):
        if self.response_times:
            self.metrics.avg_response_time = sum(self.response_times) / len(self.response_times)

    def get_health_status(self) -> Dict:
        total_requests = self.metrics.success_count + self.metrics.failure_count
        success_rate = self.metrics.success_count / total_requests if total_requests > 0 else 0

        return {
            "success_rate": success_rate,
            "avg_response_time": self.metrics.avg_response_time,
            "total_requests": total_requests,
            "status": "healthy" if success_rate > 0.95 else "degraded" if success_rate > 0.8 else "unhealthy"
        }
```

## Configuration Examples

### Complete Environment Configuration

#### Production Environment

```bash
#!/bin/bash
# Oracle Authentication Production Configuration

# Oracle Integration Cloud (OIC)
export OIC_HOST="production-instance.integration.ocp.oraclecloud.com"
export OIC_PORT="443"
export OIC_USE_SSL="true"

# IDCS Configuration
export IDCS_URL="idcs-abcd1234.identity.oraclecloud.com"
export CLIENT_ID="$(vault kv get -field=client_id secret/oic/production)"
export CLIENT_SECRET="$(vault kv get -field=client_secret secret/oic/production)"

# Audiences
export RESOURCE_AUD="https://production-instance.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all"
export API_AUD="https://production-instance.integration.ocp.oraclecloud.com:443/ic/api/"

# Oracle WMS Configuration
export WMS_HOST="production-tenant.wms.ocs.oraclecloud.com"
export WMS_USERNAME="$(vault kv get -field=username secret/wms/production)"
export WMS_PASSWORD="$(vault kv get -field=password secret/wms/production)"
export WMS_COMPANY_CODE="PROD"
export WMS_FACILITY_CODE="MAIN"

# Security Settings
export SSL_VERIFY="true"
export CONNECTION_TIMEOUT="30"
export READ_TIMEOUT="300"
export MAX_RETRIES="3"

# Monitoring
export ENABLE_METRICS="true"
export METRICS_PORT="9090"
export LOG_LEVEL="INFO"
```

#### Development Environment

```bash
#!/bin/bash
# Oracle Authentication Development Configuration

# Development OIC Instance
export OIC_HOST="dev-instance.integration.ocp.oraclecloud.com"
export OIC_PORT="443"
export OIC_USE_SSL="true"

# Development IDCS
export IDCS_URL="idcs-dev5678.identity.oraclecloud.com"
export CLIENT_ID="dev_client_id_here"
export CLIENT_SECRET="dev_client_secret_here"

# Development Audiences
export RESOURCE_AUD="https://dev-instance.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all"
export API_AUD="https://dev-instance.integration.ocp.oraclecloud.com:443/ic/api/"

# Development WMS
export WMS_HOST="dev-tenant.wms.ocs.oraclecloud.com"
export WMS_USERNAME="dev_user"
export WMS_PASSWORD="dev_password"
export WMS_COMPANY_CODE="DEV"
export WMS_FACILITY_CODE="TEST"

# Development Settings
export SSL_VERIFY="false"  # Only for dev
export CONNECTION_TIMEOUT="60"
export READ_TIMEOUT="600"
export LOG_LEVEL="DEBUG"
```

### FLX Framework Integration Example

```python
from flext.infrastructure.http.auth import FlxJwtService
from flext.adapters.outbound.http import HTTPAdapter
from flext.core.config import Config
import asyncio

async def setup_flext_authentication():
    """Complete FLX authentication setup example."""

    # Load configuration
    config = Config.from_env()

    # Setup JWT service for OIC
    oic_jwt_service = FlxJwtService.for_oracle_oic(
        idcs_url=config.get("IDCS_URL"),
        client_id=config.get("CLIENT_ID"),
        client_secret=config.get("CLIENT_SECRET"),
        oic_base_url=f"https://{config.get('OIC_HOST')}"
    )

    # Setup HTTP adapter with authentication
    oic_adapter = HTTPAdapter(
        base_url=f"https://{config.get('OIC_HOST')}",
        auth_manager=oic_jwt_service,
        timeout=config.get("CONNECTION_TIMEOUT", 30),
        max_retries=config.get("MAX_RETRIES", 3)
    )

    # Setup WMS authentication (basic auth for legacy)
    wms_adapter = HTTPAdapter(
        base_url=f"https://{config.get('WMS_HOST')}",
        auth=(config.get("WMS_USERNAME"), config.get("WMS_PASSWORD")),
        timeout=config.get("CONNECTION_TIMEOUT", 30)
    )

    return {
        "oic_adapter": oic_adapter,
        "wms_adapter": wms_adapter,
        "jwt_service": oic_jwt_service
    }

# Usage
adapters = await setup_flext_authentication()
oic_response = await adapters["oic_adapter"].get("/ic/api/integrations")
wms_response = await adapters["wms_adapter"].get("/wms/api/orders")
```

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before authentication setup
- [Security Hub](../../security/index.md) - Security architecture patterns and authentication policies
- [Getting Started Hub](../../getting-started/index.md) - FLX Framework installation and basic configuration

### **Next Steps**

- [Oracle OAuth2 Guide](./oracle-oauth2-authentication-guide.md) - Detailed OAuth2 implementation patterns and troubleshooting
- [Oracle WMS Guide](./oracle-wms-comprehensive-guide.md) - WMS authentication integration and workflow patterns
- [Oracle OIC Guide](./oracle-integration-comprehensive-guide.md) - OIC authentication and integration patterns

### **Related Topics**

- [JWT Authentication](../authentication/jwt-service-guide.md) - JWT service implementation and token management
- [Development Testing](../../development/testing/index.md) - Authentication testing strategies and security validation
- [API Reference Hub](../../api-reference/index.md) - Authentication API documentation and integration methods
- [Infrastructure Hub](../../infrastructure/index.md) - Security infrastructure and operational authentication patterns

---

## 📊 **Document Metrics**

- **Implementation Status**: ✅ Production Ready
- **Authentication Methods**: 6 comprehensive methods (OAuth2, JWT, SAML2, Basic, Native, ROPC)
- **Security Level**: Enterprise-grade with MFA support
- **Integration Coverage**: Oracle OIC, WMS, IDCS, and FLX Framework
- **Testing Coverage**: Comprehensive with production examples
- **Last Updated**: June 11, 2025

---

**📂 Guide**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
