# 📤 Tap Oracle OIC - Enterprise Integration Cloud Data Extraction

> **Function**: Production-grade Singer tap for Oracle Integration Cloud data extraction with OAuth2/IDCS | **Audience**: Integration Engineers, Data Architects | **Status**: Production Ready

[![Singer](https://img.shields.io/badge/singer-tap-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-OIC-red.svg)](https://www.oracle.com/integration/oracle-integration-cloud/)
[![Meltano](https://img.shields.io/badge/meltano-compatible-green.svg)](https://meltano.com/)
[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)

Enterprise Singer tap for extracting integration metadata and configurations from Oracle Integration Cloud with OAuth2 authentication and production-grade reliability.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Tap Oracle OIC

---

## 🎯 **Core Purpose**

This Singer tap provides enterprise-grade data extraction from Oracle Integration Cloud, enabling integration governance, documentation automation, and cross-system synchronization. It implements the Singer specification with advanced OAuth2/IDCS authentication.

### **Key Capabilities**

- **Integration Metadata**: Extract integration flows, mappings, and configurations
- **Connection Discovery**: Catalog all connections and adapters
- **Security Artifacts**: Certificate and credential management
- **Lookup Management**: Extract and sync lookup tables
- **Package Export**: Integration package metadata extraction

### **Production Features**

- **OAuth2/IDCS Authentication**: Enterprise-grade security
- **Incremental Sync**: Efficient change detection
- **Schema Discovery**: Automatic catalog generation
- **Rate Limiting**: Intelligent request throttling

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install via pip (recommended for production)
pip install tap-oracle-oic

# Install via Meltano
meltano add extractor tap-oracle-oic

# Install from source
git clone https://github.com/datacosmos-br/tap-oracle-oic
cd tap-oracle-oic
poetry install
```

### **Basic Configuration**

```json
{
  "base_url": "https://myinstance-region.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token",
  "include_extended": true,
  "page_size": 100,
  "start_date": "2024-01-01T00:00:00Z"
}
```

### **Running the Tap**

```bash
# Discover available streams
tap-oracle-oic --config config.json --discover > catalog.json

# Run extraction
tap-oracle-oic --config config.json --catalog catalog.json

# With state management
tap-oracle-oic --config config.json --catalog catalog.json --state state.json

# Pipe to target
tap-oracle-oic --config config.json | target-postgres --config target-config.json
```

---

## 🏗️ **Architecture**

### **Singer Specification Compliance**

```text
┌─────────────────────────────────────────┐
│      Oracle Integration Cloud           │
│        (Source System)                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       OAuth2/IDCS Authentication        │
│      (Enterprise Security Layer)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│          Tap Oracle OIC                 │
│     (Singer Data Extractor)             │
├─────────────────────────────────────────┤
│ • Schema Discovery Engine               │
│ • Stream Processors                     │
│ • State Management                      │
│ • OAuth Token Management                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Singer Protocol                  │
│     (JSON Lines Output)                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Target System (Any)                │
│   (Database, Data Lake, etc.)           │
└─────────────────────────────────────────┘
```

### **Component Structure**

```text
tap-oracle-oic/
├── src/tap_oracle_oic/
│   ├── __init__.py          # Package initialization
│   ├── tap.py               # Main tap class
│   ├── client.py            # OIC API client
│   ├── auth.py              # OAuth2/IDCS auth
│   ├── streams/             # Stream definitions
│   │   ├── integrations.py  # Integration flows
│   │   ├── connections.py   # Connections
│   │   ├── packages.py      # Packages
│   │   ├── lookups.py       # Lookup tables
│   │   └── certificates.py  # Certificates
│   ├── schemas/             # JSON schemas
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── examples/                # Usage examples
└── meltano.yml             # Meltano config
```

---

## 🔧 **Core Features**

### **1. OAuth2/IDCS Authentication**

Enterprise-grade authentication with Oracle Identity Cloud Service:

```python
# OAuth2 configuration
config = {
    "oauth_client_id": "your_client_id",
    "oauth_client_secret": "your_client_secret",
    "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
    "oauth_client_aud": "https://integration.ocp.oraclecloud.com:443"
}

# Automatic token refresh
# Token caching and renewal
# Secure credential management
```

### **2. Stream Catalog**

#### **Core Streams** (Always Available)

| Stream         | Description               | Key Fields                |
| -------------- | ------------------------- | ------------------------- |
| `integrations` | Integration flows         | id, name, version, status |
| `connections`  | Adapter connections       | id, name, type, status    |
| `packages`     | Integration packages      | id, name, version         |
| `lookups`      | Lookup tables             | name, type, values        |
| `libraries`    | JavaScript/XSLT libraries | name, type, content       |
| `certificates` | Security certificates     | alias, type, expiry       |

#### **Infrastructure Streams** (Optional)

| Stream         | Description        | Key Fields                  |
| -------------- | ------------------ | --------------------------- |
| `adapters`     | Available adapters | type, version, capabilities |
| `agent_groups` | Integration agents | name, status, members       |

### **3. Incremental Synchronization**

Efficient change data capture:

```json
{
  "bookmarks": {
    "integrations": {
      "replication_key": "lastUpdatedTime",
      "replication_key_value": "2024-06-19T10:30:00Z"
    },
    "connections": {
      "replication_key": "modifiedDate",
      "replication_key_value": "2024-06-19T09:45:00Z"
    }
  }
}
```

### **4. Advanced Configuration**

```json
{
  "base_url": "https://oic-prod.integration.ocp.oraclecloud.com",
  "oauth_client_id": "client_id",
  "oauth_client_secret": "client_secret",
  "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token",
  "oauth_client_aud": "https://integration.ocp.oraclecloud.com:443",
  "include_extended": true,
  "page_size": 100,
  "request_timeout": 30,
  "max_retries": 3,
  "start_date": "2024-01-01T00:00:00Z",
  "stream_maps": {
    "integrations": {
      "name": "_value.upper()"
    }
  }
}
```

### **5. Performance Optimization**

Built-in performance features:

```json
{
  "performance": {
    "page_size": 100,
    "concurrent_requests": 5,
    "cache_ttl": 300,
    "connection_pool_size": 10,
    "keep_alive": true
  }
}
```

---

## 📊 **Data Models**

### **Integration Model**

```json
{
  "id": "HELLO_WORLD_01",
  "name": "HelloWorld",
  "version": "01.00.0000",
  "status": "ACTIVATED",
  "lastUpdatedTime": "2024-06-19T10:30:00Z",
  "createdBy": "admin.user",
  "description": "Sample integration flow",
  "connections": ["REST_CONN_01", "DB_CONN_01"],
  "pattern": "Orchestration",
  "trackingFields": ["orderNumber", "customerId"]
}
```

### **Connection Model**

```json
{
  "id": "REST_CONN_01",
  "name": "REST_API_Connection",
  "adapterType": "REST",
  "status": "CONFIGURED",
  "connectionUrl": "https://api.example.com",
  "securityPolicy": "OAUTH2_CLIENT_CREDENTIALS",
  "connectionProperties": {
    "connectionType": "REST_API",
    "tlsVersion": "TLSv1.2"
  }
}
```

---

## 🔐 **Security**

### **Authentication Setup**

1. **Create IDCS Application**

   ```bash
   # In Oracle Identity Console
   # 1. Create confidential application
   # 2. Enable client credentials grant
   # 3. Add OIC scope
   ```

2. **Grant OIC Access**

   ```bash
   # In OIC Console
   # 1. Add IDCS app to ServiceInvoker role
   # 2. Configure API access
   ```

3. **Configure Tap**

   ```json
   {
     "oauth_client_id": "idcs_app_client_id",
     "oauth_client_secret": "idcs_app_secret",
     "oauth_token_url": "https://idcs.identity.oraclecloud.com/oauth2/v1/token"
   }
   ```

### **Security Features**

- **Token Encryption**: Secure token storage
- **Certificate Validation**: TLS/SSL verification
- **Credential Masking**: Sensitive data protection
- **Audit Logging**: Complete access trail

---

## 🧪 **Testing**

### **Test Coverage**

- Unit Tests: 95%+ coverage
- Integration Tests: Mock OIC server
- End-to-End Tests: Real OIC sandbox
- Security Tests: Auth validation

### **Running Tests**

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# E2E tests (requires OIC access)
poetry run pytest tests/e2e --oic-instance

# All tests with coverage
poetry run pytest --cov=tap_oracle_oic
```

---

## 📚 **Usage Examples**

### **Basic Extraction**

```python
# examples/basic_extraction.py
import json
from tap_oracle_oic import TapOIC

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Create tap instance
tap = TapOIC(config=config)

# Run discovery
catalog = tap.discover_streams()

# Select all streams
for stream in catalog.streams:
    stream.selected = True

# Run sync
tap.sync(catalog)
```

### **Filtered Extraction**

```python
# examples/filtered_extraction.py
# Extract only active integrations
config = {
    "base_url": "https://oic.company.com",
    "oauth_client_id": "client",
    "oauth_client_secret": "secret",
    "oauth_token_url": "https://idcs.company.com/oauth2/v1/token",
    "filters": {
        "integrations": {
            "status": "ACTIVATED"
        }
    }
}

tap = TapOIC(config=config)
tap.sync_all()
```

### **Meltano Project**

```yaml
# meltano.yml
project_id: integration_governance
environments:
  - name: prod
    config:
      plugins:
        extractors:
          - name: tap-oracle-oic
            variant: datacosmos
            pip_url: tap-oracle-oic
            config:
              base_url: ${OIC_BASE_URL}
              oauth_client_id: ${OIC_CLIENT_ID}
              oauth_client_secret: ${OIC_CLIENT_SECRET}
              oauth_token_url: ${IDCS_TOKEN_URL}
            select:
              - integrations.*
              - connections.*
              - lookups.*
```

---

## 🔗 **Integration Ecosystem**

### **Compatible Targets**

| Target              | Purpose              | Status    |
| ------------------- | -------------------- | --------- |
| `target-postgres`   | PostgreSQL warehouse | ✅ Tested |
| `target-snowflake`  | Snowflake cloud      | ✅ Tested |
| `target-oracle-oic` | OIC synchronization  | ✅ Tested |
| `target-jsonl`      | File-based storage   | ✅ Tested |

### **PyAuto Integration**

| Component                                      | Integration | Purpose               |
| ---------------------------------------------- | ----------- | --------------------- |
| [flx-http-oracle-oic](../flx-http-oracle-oic/) | Shared auth | OAuth2 implementation |
| [target-oracle-oic](../target-oracle-oic/)     | Round-trip  | Bidirectional sync    |
| [oracle-oic-ext](../oracle-oic-ext/)           | Extensions  | Advanced features     |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Authentication Failures**

   - **Symptom**: 401 Unauthorized
   - **Solution**: Verify IDCS app configuration and scopes

2. **Discovery Timeout**

   - **Symptom**: Timeout during catalog discovery
   - **Solution**: Increase `request_timeout` setting

3. **Rate Limiting**
   - **Symptom**: 429 Too Many Requests
   - **Solution**: Reduce `page_size` or add delays

### **Debug Mode**

```bash
# Enable debug logging
export TAP_ORACLE_OIC_LOG_LEVEL=DEBUG

# Run with verbose output
tap-oracle-oic --config config.json -v

# Log HTTP requests
export TAP_ORACLE_OIC_LOG_REQUESTS=true
```

---

## 🛠️ **CLI Reference**

```bash
# Discovery
tap-oracle-oic --config config.json --discover > catalog.json

# Full sync
tap-oracle-oic --config config.json --catalog catalog.json

# Incremental sync
tap-oracle-oic --config config.json --catalog catalog.json --state state.json

# Test connection
tap-oracle-oic --config config.json --test

# Version info
tap-oracle-oic --version
```

---

## 📖 **Configuration Reference**

### **Required Settings**

| Setting               | Type   | Description         | Example                                    |
| --------------------- | ------ | ------------------- | ------------------------------------------ |
| `base_url`            | string | OIC instance URL    | `https://oic.company.com`                  |
| `oauth_client_id`     | string | IDCS client ID      | abc123                                     |
| `oauth_client_secret` | string | IDCS client secret  | xyz789                                     |
| `oauth_token_url`     | string | IDCS token endpoint | `https://idcs.company.com/oauth2/v1/token` |

### **Optional Settings**

| Setting            | Type    | Description                    | Default       |
| ------------------ | ------- | ------------------------------ | ------------- |
| `oauth_client_aud` | string  | Token audience                 | Auto-detected |
| `include_extended` | boolean | Include infrastructure streams | false         |
| `page_size`        | integer | Records per page               | 100           |
| `request_timeout`  | integer | Request timeout (seconds)      | 30            |
| `max_retries`      | integer | Retry attempts                 | 3             |
| `start_date`       | string  | Sync start date                | 2020-01-01    |

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Singer Specification](https://hub.meltano.com/singer/spec) - Singer protocol specification
- [Oracle OIC Documentation](https://docs.oracle.com/en/cloud/paas/integration-cloud/) - Official OIC docs
- [OAuth2 RFC](https://datatracker.ietf.org/doc/html/rfc6749) - OAuth2 specification

### **Next Steps**

- [OIC Integration Guide](../docs/guides/oic-integration.md) - Complete integration guide
- [Data Pipeline Setup](../docs/guides/pipeline-setup.md) - Pipeline configuration
- [Production Deployment](../docs/deployment/tap-deployment.md) - Production setup

### **Related Topics**

- [Singer Best Practices](../docs/patterns/singer.md) - Singer tap patterns
- [OAuth2 Patterns](../docs/patterns/oauth2.md) - Authentication patterns
- [ETL Strategies](../docs/patterns/etl.md) - ETL design patterns

---

**📂 Component**: Tap Oracle OIC | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: Singer SDK 0.41.0+ | **Updated**: 2025-06-19
