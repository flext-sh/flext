# 🔐 GrupoNOS OIC OAuth2 Authentication Guide

> **Function**: OAuth2 authentication implementation for GrupoNOS Oracle Integration Cloud | **Audience**: GrupoNOS integration teams | **Status**: Production-ready

[![OAuth2](https://img.shields.io/badge/auth-oauth2-green.svg)](../oracle/oracle-oauth2-authentication-guide.md)
[![GrupoNOS](https://img.shields.io/badge/project-gruponos-blue.svg)](./index.md)
[![OIC](https://img.shields.io/badge/oracle-integration%20cloud-red.svg)](../oracle/oracle-integration-comprehensive-guide.md)

**Complete OAuth2 authentication implementation guide for GrupoNOS Oracle Integration Cloud integration using client credentials flow and enterprise automation patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 GrupoNOS**: [GrupoNOS Hub](./index.md) → **📄 Current**: OIC OAuth2 Guide

### **📍 Learning Path Position**

```
[GrupoNOS Hub](./index.md) → **[OIC OAuth2 Guide]** → [WMS CLI Guide](./gruponos-oic-wms-cli-guide.md)
```

## Overview

This document describes the authentication options available for integration with Oracle Integration Cloud and how to use them correctly with the GrupoNOS OIC automation library.

## 1. Client Credentials Method (recommended for automation)

The Client Credentials flow is the recommended method for machine-to-machine integration, as it does not require user interaction and works even with MFA enabled.

### 1.1 When to use Client Credentials

Choose this flow when:

- You need automation without user intervention
- You are implementing CI/CD integrations
- The system has MFA enabled
- Your integration has no interface for user login
- You need server-to-server integration

### 1.2 Configuration in IDCS (Identity Cloud Service)

1. Access the IDCS console associated with your OIC environment
2. Go to Applications > Add > Confidential Application
3. Configure a name for the application
4. In the Configuration > General Information tab, check "Configure this application as a client now"
5. In the Grant Types section, select "Client Credentials"
6. In Resources > Primary Audience, add the base URL of your OIC (e.g., <https://instance-name.integration.ocp.oraclecloud.com:443>)
7. In Resources > Scope, add the scopes:
   - `urn:opc:resource:consumer::all` (to call integrations)
   - `/ic/api/` (to call administrative APIs)
8. Finalize the creation and activate the application
9. Assign the application to the "ServiceUser" role in the OIC application in IDCS

### 1.3 Required Environment Variables

```bash
IDCS_URL=idcs-xxxx.identity.oraclecloud.com
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here
RESOURCE_AUD=https://XXXX.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all
API_AUD=https://XXXX.integration.ocp.oraclecloud.com:443/ic/api/
OIC_URL=https://instance-name.integration.ocp.oraclecloud.com
```

Note that in RESOURCE_AUD there is no slash between the port (443) and "urn", while in API_AUD there is a slash after the port.

### 1.4 Using the oic.sh library

Our `scripts/lib/oic.sh` library offers a complete implementation of the Client Credentials flow:

```bash
# Include the library in your script
source "scripts/lib/oic.sh"

# Get a token automatically
oic_get_token

# Use the token to call APIs
response=$(oic_api_get '/ic/api/integration/v1/integrations')

# Test specific endpoints
health=$(oic_check_health)
connections=$(oic_list_connections)
```

Complete example in `scripts/oic_client_credentials_example.sh`.

### 1.5 Debugging Client Credentials issues

If the token is obtained successfully, but API calls fail:

1. Check if OIC_URL is correct (must include https://)
2. Confirm that the OAuth client has the correct role (ServiceUser) in IDCS
3. Verify that RESOURCE_AUD and API_AUD scopes are correct
4. Set DEBUG=true to get more information
5. Execute: `scripts/oic_client_credentials_example.sh --debug`

## 2. Authorization Code Method (for interactive flows)

This method is useful when you want the user to log in explicitly. However, it is not recommended for automation, especially if MFA is enabled.

### 2.1 When to use Authorization Code

Choose this flow when:

- Explicit user interaction is desired or required
- You need to authenticate with specific user context
- You implement a web application or client with UI
- You want more granular permissions based on user

### 2.2 Additional Configuration in IDCS

1. In the application configuration in IDCS, in addition to previous steps:
2. In Grant Types, add "Authorization Code"
3. In Web Tier Policy > Redirect URL, add your callback URL (e.g., <https://idcs-xxxx.identity.oraclecloud.com/callback>)
4. Save and activate the application

### 2.3 Additional Environment Variables

In addition to the Client Credentials method variables, add:

```bash
REDIRECT_URI=https://idcs-xxxx.identity.oraclecloud.com/callback
SCOPE="${RESOURCE_AUD} offline_access"
```

### 2.4 Using the oic.sh library with Authorization Code

```bash
# Include the library in your script
source "scripts/lib/oic.sh"

# Get authorization URL
auth_url=$(oic_auth_url)
echo "Visit this URL and log in: $auth_url"

# After receiving the authorization code
oic_exchange_code "code_received_after_login"

# Use the token for API calls
response=$(oic_api_get '/ic/api/integration/v1/integrations')
```

## 3. Troubleshooting

### 3.1 "invalid_redirect_uri" Error

If you receive the error:

```
"error": "invalid_redirect_uri", 
"error_description": "Client xxxx requested an invalid redirect URL..."
```

This means that the configured REDIRECT_URI is not authorized in IDCS. Solutions:

1. Check if the REDIRECT_URI in .env exactly matches the one configured in IDCS
2. Add the URI to the OAuth client in IDCS (Web Tier Policy > Redirect URL)
3. **Recommended solution:** Use the Client Credentials flow which does not require REDIRECT_URI

### 3.2 Issues with Audience and Scopes

The RESOURCE_AUD and API_AUD values must be correct. The simplest way to get the correct values is:

1. In IDCS, access the OIC application (not your client application)
2. Note the "Resource URI" and "Primary Audience"
3. Build the values using the format shown above

#### Correct format

- RESOURCE_AUD: `https://XXXX.integration.ocp.oraclecloud.com:443urn:opc:resource:consumer::all`
- API_AUD: `https://XXXX.integration.ocp.oraclecloud.com:443/ic/api/`

### 3.3 Integration with MFA enabled

If MFA is enabled in IDCS:

- **Client Credentials**: Works normally, as it does not go through the user login flow
- **Authorization Code**: Will require the user to complete MFA during login

### 3.4 Useful commands for diagnosis

```bash
# Check configuration
./scripts/oic_client_credentials_example.sh --config

# Execute with debug
DEBUG=true ./scripts/oic_client_credentials_example.sh

# Test token acquisition directly
curl -X POST https://$IDCS_URL/oauth2/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic $BASIC_AUTH" \
  -d "grant_type=client_credentials&scope=$RESOURCE_AUD%20$API_AUD"
```

## 4. Alternative Authentication Methods

### 4.1 JWT Assertion

For environments that support JWT Assertion, consult the official documentation:
[Using JWT Assertion with OIC](https://docs.oracle.com/en/cloud/paas/integration-cloud/soap-adapter/using-oauth-2.0-grants-oracle-identity-cloud-service-environments.html)

### 4.2 Basic Authentication for WMS API

For WMS APIs, basic authentication is generally also supported:

```bash
curl -X GET "$WMS_URL/resource" \
  -u "$WMS_USER:$WMS_PASS" \
  -H "Content-Type: application/json"
```

## 5. References

- [Official Oracle Documentation - OAuth 2.0 Grants](https://docs.oracle.com/en/cloud/paas/integration-cloud/soap-adapter/using-oauth-2.0-grants-oracle-identity-cloud-service-environments.html)
- [OAuth Configuration using Client Credentials](https://docs.oracle.com/en/cloud/paas/integration-cloud/oracle-integration-gov/configure-oauth-authentication-using-client-credentials.html)
- [OAuth 2.0 Documentation](https://oauth.net/2/)
- [RFC 6749 - OAuth 2.0 Framework](https://tools.ietf.org/html/rfc6749)
