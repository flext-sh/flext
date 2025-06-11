# Oracle Integration Cloud (OIC) Complete Guide - Guides

> **Function**: Complete Oracle Integration Cloud integration with FLX Framework | **Audience**: Integration developers, Oracle specialists | **Status**: Stable

[![OIC](https://img.shields.io/badge/Oracle-OIC-red.svg)](./oracle-integration-hub.md)
[![Integration](https://img.shields.io/badge/integration-cloud-blue.svg)](../integration/index.md)
[![OAuth2](https://img.shields.io/badge/auth-OAuth2-green.svg)](./authentication-complete-guide.md)

**Complete Oracle Integration Cloud (OIC) integration guide covering OAuth2 authentication, REST API integration, and hexagonal architecture implementation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides](../index.md) → **📂 Oracle**: [Oracle Hub](./oracle-integration-hub.md) → **📄 Current**: OIC Complete Guide

### **📍 Learning Path Position**

```
[Oracle Integration Hub](./oracle-integration-hub.md) → **[OIC COMPLETE GUIDE]** → [WMS Integration](./oracle-wms-comprehensive-guide.md)
```

## 🎯 **Quick Links**

- **📂 Oracle Hub**: [Oracle Integration Hub](./oracle-integration-hub.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Authentication Guide](./authentication-complete-guide.md), [WMS Guide](./oracle-wms-comprehensive-guide.md)

---

## 📋 **Overview**

Complete Oracle Integration Cloud (OIC) integration guide for the FLX framework, covering OAuth2 authentication, REST API integration, advanced patterns, and hexagonal architecture implementation.

## 🎯 Quick Navigation

- [**Getting Started**](#-getting-started) - Setup and basic configuration
- [**Authentication**](#-authentication) - OAuth2 and security patterns
- [**FLX Framework Integration**](#-flx-framework-integration) - Modern Python integration
- [**API Operations**](#-api-operations) - Integration and connection management
- [**Advanced Patterns**](#-advanced-patterns) - Enterprise integration patterns
- [**Troubleshooting**](#-troubleshooting) - Common issues and solutions

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Oracle Cloud account with OIC access
- IDCS (Identity Cloud Service) application configured
- FLX Framework installed

### Installation

```bash
# Install Oracle OIC adapter
pip install flx-http-oracle-oic

# Or install from source
cd flx-http-oracle-oic
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

### Environment Configuration

Create a `.env` file with your OIC configuration:

```env
# IDCS Configuration
OIC_IDCS_URL=your-idcs-domain.oracle.com
OIC_IDCS_CLIENT_ID=your-client-id
OIC_IDCS_CLIENT_SECRET=your-client-secret
OIC_IDCS_CLIENT_AUD=https://your-idcs-aud.oracle.com

# OIC Instance Configuration
OIC_INSTANCE_ID=your-instance-id
OIC_REGION=us-ashburn-1
OIC_ENVIRONMENT=dev

# Optional Settings
OIC_TIMEOUT=60.0
OIC_MAX_RETRIES=3
OIC_API_VERSION=v1
OIC_VERIFY_SSL=true
```

### Basic Connection Test

```bash
# Test configuration
python -m flx_http_oracle_oic.cli config validate --test-connection

# View configuration
python -m flx_http_oracle_oic.cli config view

# Health check
python -m flx_http_oracle_oic.cli monitoring health
```

## 🔐 Authentication

### OAuth2 Client Credentials (Recommended)

The Client Credentials flow is the **recommended method** for machine-to-machine integration, especially for automation and production environments.

#### When to Use Client Credentials

Choose this flow when:

- **Automation without user intervention** is required
- Implementing **CI/CD integrations**
- System has **MFA enabled**
- Integration has **no user interface** for login
- Need **server-to-server integration**
- **Production environments** with high security requirements

#### IDCS Configuration Steps

1. **Access IDCS Console**: Navigate to the IDCS console for your OIC environment
2. **Create Application**: Go to Applications > Add > Confidential Application
3. **Configure Application**: Set a descriptive name
4. **Client Configuration**: Check "Configure this application as a client now"
5. **Grant Types**: Select "Client Credentials"
6. **Primary Audience**: Add your OIC base URL:

   ```
   https://instance-name.integration.ocp.oraclecloud.com:443
   ```

7. **Scope Configuration**: Add required scopes:

   ```
   urn:opc:resource:consumer::all     # For calling integrations
   /ic/api/                           # For calling REDACTED_LDAP_BIND_PASSWORDistrative APIs
   ```

8. **Role Assignment**: Assign application to "ServiceUser" role in OIC

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
```

**⚠️ CRITICAL FORMAT NOTE**:

- In `RESOURCE_AUD`: NO slash between port (443) and "urn"
- In `API_AUD`: There IS a slash after port (443)

### OAuth2 Authorization Code (For Interactive Flows)

This method is useful when you want explicit user login, but **not recommended for automation**.

#### Additional IDCS Configuration

1. **Grant Types**: Add "Authorization Code" to Grant Types
2. **Redirect URL**: Add your callback URL:

   ```
   https://idcs-xxxx.identity.oraclecloud.com/callback
   ```

#### Additional Environment Variables

```bash
# Authorization Code flow variables
REDIRECT_URI=https://idcs-xxxx.identity.oraclecloud.com/callback
SCOPE="${RESOURCE_AUD} offline_access"
```

## 🏗️ FLX Framework Integration

### Modern Python API Usage

```python
import asyncio
from flx_http_oracle_oic import OicConfig, flx_create_oic_context

async def main():
    # Load configuration
    config = OicConfig.from_env()
    
    # Use factory pattern with context manager
    async with flx_create_oic_context(config) as factory:
        service = factory.create_oic_service()
        
        # Health check
        is_healthy = await service.health_check()
        
        # List integrations
        integrations = await service.list_integrations()
        for integration in integrations:
            print(f"{integration.name}: {integration.status}")
        
        # List connections
        connections = await service.list_connections()
        for connection in connections:
            print(f"{connection.name}: {connection.type}")

asyncio.run(main())
```

### Advanced Authentication Patterns

#### Token Caching and Refresh

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

#### Error Handling and Retry Logic

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

### Hexagonal Architecture Implementation

```python
from flx.core.entities import AggregateRoot
from flx.core.value_objects import ValueObject

# Domain entity for OIC integrations
class OicIntegration(AggregateRoot):
    integration_id: str
    name: str
    status: str
    version: str
    created_by: str
    
    def activate(self) -> None:
        if self.status == "CONFIGURED":
            self.status = "ACTIVATED"
            self.increment_version()
            
            # Add domain event
            self.add_event(DomainEvent(
                event_type="IntegrationActivated",
                aggregate_id=self.entity_id,
                data={
                    "integration_id": self.integration_id,
                    "name": self.name,
                    "activated_at": datetime.now()
                }
            ))
    
    def deactivate(self) -> None:
        if self.status == "ACTIVATED":
            self.status = "CONFIGURED"
            self.increment_version()
            
            # Add domain event
            self.add_event(DomainEvent(
                event_type="IntegrationDeactivated",
                aggregate_id=self.entity_id,
                data={
                    "integration_id": self.integration_id,
                    "name": self.name,
                    "deactivated_at": datetime.now()
                }
            ))

# Value object for OIC connection
class OicConnection(ValueObject):
    connection_id: str
    name: str
    connection_type: str
    adapter_type: str
    
    @property
    def is_database_connection(self) -> bool:
        return self.adapter_type.lower() in ["oracle", "mysql", "postgresql"]
    
    @property
    def is_rest_connection(self) -> bool:
        return self.adapter_type.lower() == "rest"
```

## 🖥️ API Operations

### CLI Interface

The OIC adapter provides a comprehensive CLI for all operations:

#### Configuration Management

```bash
# Validate configuration with connection test
python -m flx_http_oracle_oic.cli config validate --test-connection

# View current configuration
python -m flx_http_oracle_oic.cli config view

# Show configuration with secrets (careful!)
python -m flx_http_oracle_oic.cli config view --show-secrets
```

#### Integration Management

```bash
# List all integrations
python -m flx_http_oracle_oic.cli integrations list --format table

# Get specific integration details
python -m flx_http_oracle_oic.cli integrations get INTEGRATION_ID

# List integrations with filters
python -m flx_http_oracle_oic.cli integrations list --status ACTIVATED --format json

# Export integration details
python -m flx_http_oracle_oic.cli integrations export INTEGRATION_ID --output integration.json
```

#### Connection Management

```bash
# List all connections
python -m flx_http_oracle_oic.cli connections list

# List connections by type
python -m flx_http_oracle_oic.cli connections list --type REST

# Test specific connection
python -m flx_http_oracle_oic.cli connections test CONNECTION_ID

# Get connection details
python -m flx_http_oracle_oic.cli connections get CONNECTION_ID --format yaml
```

#### Monitoring and Health Checks

```bash
# Overall system health
python -m flx_http_oracle_oic.cli monitoring health

# Monitoring overview for last 24 hours
python -m flx_http_oracle_oic.cli monitoring overview --hours 24

# Integration flow monitoring
python -m flx_http_oracle_oic.cli monitoring flows --integration-id INTEGRATION_ID

# Real-time monitoring
python -m flx_http_oracle_oic.cli monitoring real-time --refresh-interval 30
```

#### JWT Token Management

```bash
# Check JWT token status
python -m flx_http_oracle_oic.cli jwt status

# Get new token (shows token details without exposing secret)
python -m flx_http_oracle_oic.cli jwt token

# Show actual token (use with caution)
python -m flx_http_oracle_oic.cli jwt token --show-token

# Refresh token
python -m flx_http_oracle_oic.cli jwt refresh
```

### REST API Integration

#### Core API Categories

**Integration Management APIs**

- **List Integrations**: `/ic/api/integration/v1/integrations`
- **Get Integration**: `/ic/api/integration/v1/integrations/{id}`
- **Activate/Deactivate**: `/ic/api/integration/v1/integrations/{id}/activate`

**Connection Management APIs**

- **List Connections**: `/ic/api/integration/v1/connections`
- **Test Connection**: `/ic/api/integration/v1/connections/{id}/test`
- **Get Connection**: `/ic/api/integration/v1/connections/{id}`

**Monitoring APIs**

- **Health Check**: `/ic/api/integration/v1/health`
- **Flow Instances**: `/ic/api/integration/v1/flows/instances`
- **Activity Stream**: `/ic/api/integration/v1/activitystream`

#### API Usage Examples

```python
from flx_http_oracle_oic import OracleOicService, OicConfig

# Initialize service
config = OicConfig.from_env()
service = OracleOicService(config)

# List integrations
integrations = await service.list_integrations()

# Get specific integration
integration = await service.get_integration("MY_INTEGRATION_ID")

# Activate integration
result = await service.activate_integration("MY_INTEGRATION_ID")

# Test connection
test_result = await service.test_connection("MY_CONNECTION_ID")

# Get monitoring data
monitoring_data = await service.get_monitoring_data(
    hours=24,
    integration_id="MY_INTEGRATION_ID"
)
```

## 🚀 Advanced Patterns

### Event-Driven Integration

```python
from flx.core.events import DomainEvent
from flx.application.services import ApplicationService

class OicIntegrationService(ApplicationService):
    def __init__(self, oic_client, event_publisher):
        self.oic = oic_client
        self.event_publisher = event_publisher
    
    async def handle_integration_flow_trigger(self, event: DomainEvent):
        """Handle domain events by triggering OIC flows."""
        
        if event.event_type == "OrderCreated":
            # Trigger order processing integration
            result = await self.oic.trigger_integration(
                "ORDER_PROCESSING_FLOW",
                payload=event.data
            )
            
            # Publish integration result event
            await self.event_publisher.publish(DomainEvent(
                event_type="OrderProcessingTriggered",
                data={
                    "order_id": event.data["order_id"],
                    "integration_id": "ORDER_PROCESSING_FLOW",
                    "result": result
                }
            ))
```

### Batch Processing Pattern

```python
class BatchOicProcessor:
    async def process_daily_integration_sync(self):
        """Daily batch processing for OIC integrations."""
        
        # 1. Get failed integrations
        failed_flows = await self.oic.get_failed_flows(
            since=datetime.now() - timedelta(days=1)
        )
        
        # 2. Retry failed flows
        for flow in failed_flows:
            try:
                await self.oic.retry_flow(flow.flow_id)
            except Exception as e:
                logger.error(f"Failed to retry flow {flow.flow_id}: {e}")
        
        # 3. Generate daily report
        report = await self.oic.generate_integration_report(
            date=datetime.now().date()
        )
        
        return report
```

### Recipe Integration Patterns

Oracle provides pre-built integration recipes for common scenarios:

#### WMS to Inventory Management Flow

```python
class ReceiptAdviceIntegration:
    def __init__(self, oic_service: OracleOicService):
        self.oic = oic_service
    
    async def process_receipt_advice(self, purchase_order_id: str):
        """Process receipt advice from IM to WMS."""
        
        # 1. Generate receipt advice in IM
        receipt_advice = await self.oic.trigger_integration(
            "GENERATE_RECEIPT_ADVICE",
            payload={"po_id": purchase_order_id}
        )
        
        # 2. Send to WMS for processing
        wms_receipt = await self.oic.trigger_integration(
            "WMS_RECEIPT_PROCESSING", 
            payload=receipt_advice
        )
        
        # 3. Confirm receipt back to IM
        confirmation = await self.oic.trigger_integration(
            "RECEIPT_CONFIRMATION",
            payload={
                "receipt_id": wms_receipt["receipt_id"],
                "status": "COMPLETED"
            }
        )
        
        return confirmation
```

### Circuit Breaker Pattern

```python
from flx.infrastructure.resilience import CircuitBreaker

class ResilientOicClient:
    def __init__(self, oic_service):
        self.oic = oic_service
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=OICConnectionError
        )
    
    async def call_integration_with_breaker(self, integration_id, payload):
        """Call integration with circuit breaker protection."""
        
        @self.circuit_breaker
        async def protected_call():
            return await self.oic.trigger_integration(integration_id, payload)
        
        try:
            return await protected_call()
        except CircuitBreakerOpenError:
            # Fallback mechanism
            logger.warning(f"Circuit breaker open for {integration_id}")
            return await self.handle_fallback(integration_id, payload)
```

## 🔧 Production Configuration

### Security Best Practices

#### Credential Management

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

#### Environment Variable Security

```bash
# Use secure environment loading
source <(gpg --decrypt credentials.env.gpg)

# Or use dedicated secret management
export CLIENT_SECRET=$(vault kv get -field=client_secret secret/oic/credentials)
```

### Monitoring and Auditing

#### Authentication Monitoring

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

### Configuration Management

```yaml
# config/oic.yaml
oracle_oic:
  authentication:
    method: client_credentials
    idcs_url: ${IDCS_URL}
    client_id: ${CLIENT_ID}
    client_secret: ${CLIENT_SECRET}
    scopes:
      - "urn:opc:resource:consumer::all"
      - "/ic/api/"
  
  instance:
    url: ${OIC_URL}
    region: ${OIC_REGION}
    environment: ${OIC_ENVIRONMENT}
  
  security:
    token_cache_enabled: true
    token_refresh_threshold: 300  # seconds
    max_retry_attempts: 3
    ssl_verify: true
    
  monitoring:
    health_check_interval: 300
    failed_flow_retry_enabled: true
    audit_logging_enabled: true
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Token Acquisition Issues

**Issue**: `invalid_client` error

```bash
# Verify client credentials
curl -X POST https://$IDCS_URL/oauth2/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$CLIENT_ID:$CLIENT_SECRET" \
  -d "grant_type=client_credentials&scope=$RESOURCE_AUD%20$API_AUD"
```

**Issue**: `insufficient_scope` error

```bash
# Check scope configuration in IDCS application
# Ensure both scopes are configured:
# - urn:opc:resource:consumer::all
# - /ic/api/
```

**Issue**: Token obtained but API calls fail

```bash
# Verify OIC_URL format (must include https://)
echo "OIC_URL: $OIC_URL"

# Check client has correct role in IDCS
echo "Verify ServiceUser role assignment in IDCS"

# Validate audience configuration
echo "RESOURCE_AUD: $RESOURCE_AUD"
echo "API_AUD: $API_AUD"
```

### Diagnostic Commands

```bash
# Configuration validation
python -m flx_http_oracle_oic.cli config validate --verbose

# Full debug execution
export OIC_DEBUG=true
export OIC_LOG_LEVEL=DEBUG
python -m flx_http_oracle_oic.cli monitoring health

# Network connectivity test
curl -v https://$OIC_URL/ic/api/integration/v1/integrations

# Token validation test
python -m flx_http_oracle_oic.cli jwt status --verbose
```

### Error Resolution Matrix

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_redirect_uri` | REDIRECT_URI not configured in IDCS | Add URI to IDCS application or use Client Credentials |
| `invalid_client` | Wrong client credentials | Verify CLIENT_ID and CLIENT_SECRET |
| `insufficient_scope` | Missing scopes in IDCS | Add required scopes to IDCS application |
| `token_expired` | Access token expired | Implement automatic token refresh |
| `connection_timeout` | Network connectivity issue | Check firewall rules and DNS resolution |
| `integration_not_found` | Invalid integration ID | Verify integration exists and is accessible |
| `connection_test_failed` | Connection configuration issue | Check connection parameters and credentials |

## 📖 Related Documentation

- [Oracle Integration Hub](README.md) - Main Oracle documentation hub
- [Oracle WMS Integration](wms-complete-guide.md) - WMS integration patterns
- [Oracle Database Integration](database-complete-guide.md) - Database connections
- [Oracle Authentication](authentication-complete-guide.md) - Complete auth guide
- [FLX Architecture](../../architecture/infrastructure-architecture.md) - Framework architecture
- [Testing Oracle Integrations](../../development/testing/oracle-testing.md) - Testing strategies

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Integration Hub](./oracle-integration-hub.md) - Overview of Oracle integration patterns and entry point
- [Authentication Complete Guide](./authentication-complete-guide.md) - OAuth2 and IDCS authentication fundamentals
- [Getting Started](../../getting-started/index.md) - FLX Framework installation and basic configuration

### **Next Steps**

- [Oracle WMS Integration](./oracle-wms-comprehensive-guide.md) - Apply OIC patterns to Warehouse Management System integration
- [Oracle Database Integration](./oracle-database-adapter-VALIDATED.md) - Combine OIC with database adapter patterns
- [Integration Testing](../../development/testing/index.md) - Test Oracle integration implementations

### **Related Topics**

- [HTTP Adapter Patterns](../adapters/flx-http-oracle-oic-adapter.md) - FLX HTTP adapter implementation for OIC
- [Security Framework](../../security/index.md) - Enterprise security patterns for Oracle integrations
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure services supporting Oracle integrations

---

## 🆘 **Troubleshooting**

### **Common OIC Integration Issues**

**Authentication Problems**:

```bash
# Check JWT token status
flx-oic auth status --debug
```

**Connection Issues**:

```bash
# Validate configuration
flx-oic test-connection --config-path config.yaml
```

**Integration Flow Problems**:

```bash
# Monitor real-time flows
flx-oic monitor --flow-id integration-flow-123
```

---

**📂 Hub**: [Oracle Integration Hub](./oracle-integration-hub.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
