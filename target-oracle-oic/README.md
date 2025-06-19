# 📥 Target Oracle OIC - Enterprise Integration Cloud Data Loading

> **Function**: Production-grade Singer target for Oracle Integration Cloud artifact deployment and synchronization | **Audience**: Integration Engineers, DevOps Teams | **Status**: Production Ready

[![Singer](https://img.shields.io/badge/singer-target-blue.svg)](https://www.singer.io/)
[![Oracle](https://img.shields.io/badge/oracle-OIC-red.svg)](https://www.oracle.com/integration/oracle-integration-cloud/)
[![Meltano](https://img.shields.io/badge/meltano-compatible-green.svg)](https://meltano.com/)
[![Python](https://img.shields.io/badge/python-3.9%2B-orange.svg)](https://www.python.org/)

## 📋 **Overview**

Enterprise Singer target for deploying integrations, connections, and configurations to Oracle Integration Cloud with CI/CD support

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../README.md) → **📂 Current**: Target Oracle OIC

---

## 🎯 **Core Purpose**

This Singer target enables enterprise-grade deployment and synchronization of Oracle Integration Cloud artifacts. It receives configuration streams from any Singer tap and manages the complete lifecycle of OIC components including creation, updates, validation, and activation.

### **Key Capabilities**

- **Artifact Deployment**: Integrations, connections, lookups, packages
- **Lifecycle Management**: Create, update, activate, deactivate
- **Archive Support**: Direct .iar and .par file deployment
- **CI/CD Integration**: GitOps-friendly deployment workflows
- **Validation**: Pre-deployment connection and configuration testing

### **Production Features**

- **Transaction Safety**: Rollback on deployment failures
- **Version Control**: Integration versioning and history
- **Audit Trail**: Complete deployment tracking
- **Error Recovery**: Automatic retry with conflict resolution

---

## 🚀 **Quick Start**

### **Installation**

```bash
# Install via pip (recommended for production)
pip install target-oracle-oic

# Install via Meltano
meltano add loader target-oracle-oic

# Install from source
git clone https://github.com/datacosmos-br/target-oracle-oic
cd target-oracle-oic
poetry install
```

### **Basic Configuration**

```json
{
  "base_url": "https://myinstance-region.integration.ocp.oraclecloud.com",
  "oauth_client_id": "your_client_id",
  "oauth_client_secret": "your_client_secret",
  "oauth_token_url": "https://idcs-tenant.identity.oraclecloud.com/oauth2/v1/token",
  "import_mode": "create_or_update",
  "activate_integrations": true,
  "validate_connections": true
}
```

### **Running the Target**

```bash
# Deploy from tap
tap-oracle-oic --config tap_config.json | \
  target-oracle-oic --config target_config.json

# Deploy from file
cat integrations.jsonl | target-oracle-oic --config config.json

# With Meltano
meltano run tap-oracle-oic target-oracle-oic
```

---

## 🏗️ **Architecture**

### **Deployment Pipeline**

```
┌─────────────────────────────────────────┐
│         Singer Tap (Any)                │
│      (Configuration Source)             │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Singer Protocol                  │
│      (JSON Lines Input)                 │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       Target Oracle OIC                 │
│    (Deployment Orchestrator)            │
├─────────────────────────────────────────┤
│ • Stream Router                         │
│ • Validation Engine                     │
│ • Deployment Manager                    │
│ • State Tracker                         │
│ • Rollback Handler                      │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Specialized Sinks                  │
├─────────────────────────────────────────┤
│ • ConnectionSink                        │
│ • IntegrationSink                       │
│ • LookupSink                           │
│ • PackageSink                          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Oracle Integration Cloud             │
│      (Target Environment)               │
└─────────────────────────────────────────┘
```

### **Component Structure**

```
target-oracle-oic/
├── src/target_oracle_oic/
│   ├── __init__.py          # Package initialization
│   ├── target.py            # Main target class
│   ├── client.py            # OIC API client
│   ├── auth.py              # OAuth2/IDCS auth
│   ├── sinks/               # Specialized sinks
│   │   ├── base.py          # Base sink class
│   │   ├── connection.py    # Connection sink
│   │   ├── integration.py   # Integration sink
│   │   ├── lookup.py        # Lookup sink
│   │   └── package.py       # Package sink
│   ├── validators/          # Pre-deployment validation
│   │   ├── connection.py    # Connection testing
│   │   └── integration.py   # Integration validation
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── examples/                # Usage examples
└── meltano.yml             # Meltano config
```

---

## 🔧 **Core Features**

### **1. Stream-Specific Processing**

Intelligent routing and handling per artifact type:

```python
# Stream to sink mapping
STREAM_SINKS = {
    "connections": ConnectionSink,
    "integrations": IntegrationSink,
    "lookups": LookupSink,
    "packages": PackageSink,
    "libraries": LibrarySink,
    "certificates": CertificateSink
}
```

### **2. Deployment Modes**

Flexible deployment strategies:

```json
{
  "import_mode": "create_or_update", // Options: create_only, update_only, create_or_update
  "conflict_resolution": "skip", // Options: skip, overwrite, version
  "deployment_strategy": "rolling", // Options: rolling, blue_green, canary
  "activation_policy": "auto" // Options: auto, manual, scheduled
}
```

### **3. Connection Management**

```json
{
  "connection": {
    "id": "REST_CONN_01",
    "name": "REST API Connection",
    "adapterType": "REST",
    "connectionUrl": "https://api.example.com",
    "securityPolicy": "OAUTH2_CLIENT_CREDENTIALS",
    "connectionProperties": {
      "connectionType": "REST_API",
      "clientId": "${OIC_CLIENT_ID}",
      "clientSecret": "${OIC_CLIENT_SECRET}",
      "scope": "api.read api.write"
    }
  }
}
```

### **4. Integration Deployment**

```python
# Integration deployment with activation
{
  "integration": {
    "id": "HELLO_WORLD_01",
    "name": "HelloWorld",
    "version": "01.00.0000",
    "package": "com.example.integrations",
    "pattern": "Orchestration",
    "archive_path": "/archives/HELLO_WORLD_01.iar",
    "connections": {
      "REST_CONN": "REST_CONN_01",
      "DB_CONN": "DB_CONN_01"
    },
    "activation": {
      "enable": true,
      "tracing": "production",
      "payload_validation": true
    }
  }
}
```

### **5. Archive Management**

Direct archive deployment support:

```json
{
  "archive_config": {
    "archive_directory": "/path/to/archives",
    "archive_format": "iar", // iar for integrations, par for packages
    "validation": {
      "checksum": true,
      "signature": true,
      "dependencies": true
    },
    "deployment": {
      "overwrite": true,
      "backup_existing": true,
      "preserve_credentials": true
    }
  }
}
```

---

## 📊 **Deployment Scenarios**

### **CI/CD Pipeline Integration**

```yaml
# .github/workflows/oic-deploy.yml
name: Deploy to OIC
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Extract OIC Configurations
        run: |
          tap-git-oic --config tap_config.json > oic_artifacts.jsonl

      - name: Deploy to OIC
        run: |
          cat oic_artifacts.jsonl | \
          target-oracle-oic --config target_config.json
```

### **Blue-Green Deployment**

```python
# examples/blue_green_deploy.py
def blue_green_deployment(artifacts):
    """Implement blue-green deployment strategy."""
    # Deploy to green environment
    green_target = TargetOracleOIC(config={
        "base_url": GREEN_OIC_URL,
        "deployment_prefix": "GREEN_"
    })
    green_target.deploy(artifacts)

    # Validate green deployment
    if validate_deployment(GREEN_OIC_URL):
        # Switch traffic to green
        switch_traffic_to_green()
        # Deactivate blue
        deactivate_blue_artifacts()
```

### **Canary Deployment**

```python
# examples/canary_deploy.py
def canary_deployment(integration):
    """Deploy integration with canary strategy."""
    # Deploy canary version
    canary_config = {
        "integration_id": f"{integration['id']}_CANARY",
        "traffic_percentage": 10,
        "monitoring_enabled": true
    }
    deploy_canary(integration, canary_config)

    # Monitor and gradually increase traffic
    for percentage in [25, 50, 100]:
        if canary_metrics_healthy():
            update_traffic_split(percentage)
        else:
            rollback_canary()
            break
```

---

## 🔐 **Security & Governance**

### **Authentication**

- **OAuth2/IDCS**: Enterprise SSO integration
- **Service Accounts**: Automated deployment credentials
- **Token Management**: Automatic refresh and caching
- **mTLS Support**: Certificate-based authentication

### **Access Control**

- **Role-Based**: Integration developer, deployer, REDACTED_LDAP_BIND_PASSWORD roles
- **Environment Isolation**: Dev/Test/Prod separation
- **Audit Logging**: Complete deployment history
- **Change Approval**: Optional approval workflows

### **Compliance**

- **Version Control**: All deployments tracked
- **Rollback Capability**: Point-in-time recovery
- **Configuration Drift**: Detection and alerting
- **Security Scanning**: Pre-deployment vulnerability checks

---

## 🧪 **Testing**

### **Test Coverage**

- Unit Tests: 94%+ coverage
- Integration Tests: Mock OIC API
- End-to-End Tests: Sandbox deployments
- Security Tests: Auth and encryption

### **Running Tests**

```bash
# Unit tests
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# E2E tests (requires OIC sandbox)
poetry run pytest tests/e2e --oic-sandbox

# All tests with coverage
poetry run pytest --cov=target_oracle_oic
```

---

## 📚 **Configuration Reference**

### **Required Settings**

| Setting               | Type   | Description         | Example                                    |
| --------------------- | ------ | ------------------- | ------------------------------------------ |
| `base_url`            | string | OIC instance URL    | `https://oic.company.com`                  |
| `oauth_client_id`     | string | IDCS client ID      | abc123                                     |
| `oauth_client_secret` | string | IDCS client secret  | xyz789                                     |
| `oauth_token_url`     | string | IDCS token endpoint | `https://idcs.company.com/oauth2/v1/token` |

### **Optional Settings**

| Setting                 | Type    | Description       | Default          |
| ----------------------- | ------- | ----------------- | ---------------- |
| `oauth_client_aud`      | string  | Token audience    | Auto-detected    |
| `import_mode`           | string  | Deployment mode   | create_or_update |
| `activate_integrations` | boolean | Auto-activate     | false            |
| `validate_connections`  | boolean | Pre-validate      | true             |
| `archive_directory`     | string  | Archive location  | -                |
| `request_timeout`       | integer | Timeout (seconds) | 30               |
| `max_retries`           | integer | Retry attempts    | 3                |

---

## 🔗 **Integration Ecosystem**

### **Compatible Sources**

| Tap              | Purpose            | Status    |
| ---------------- | ------------------ | --------- |
| `tap-oracle-oic` | OIC to OIC sync    | ✅ Tested |
| `tap-git`        | GitOps deployment  | ✅ Tested |
| `tap-github`     | GitHub integration | ✅ Tested |
| `tap-s3-csv`     | S3 configurations  | ✅ Tested |

### **PyAuto Integration**

| Component                                      | Integration | Purpose                  |
| ---------------------------------------------- | ----------- | ------------------------ |
| [tap-oracle-oic](../tap-oracle-oic/)           | Source tap  | Configuration extraction |
| [flx-http-oracle-oic](../flx-http-oracle-oic/) | HTTP client | API operations           |
| [oracle-oic-ext](../oracle-oic-ext/)           | Extensions  | Advanced features        |

### **Deployment Targets**

| Environment | Purpose             | Features          |
| ----------- | ------------------- | ----------------- |
| Development | Local testing       | Sandbox mode      |
| Test        | Integration testing | Full validation   |
| Staging     | Pre-production      | Production mirror |
| Production  | Live deployment     | HA, monitoring    |

---

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Import Conflicts**

   - **Symptom**: Integration already exists error
   - **Solution**: Use `import_mode: update_only` or enable versioning

2. **Connection Validation Failures**

   - **Symptom**: Connection test failed
   - **Solution**: Verify credentials, endpoints, and network access

3. **Activation Errors**
   - **Symptom**: Integration fails to activate
   - **Solution**: Check connection mappings and dependencies

### **Debug Mode**

```bash
# Enable debug logging
export TARGET_ORACLE_OIC_LOG_LEVEL=DEBUG

# Dry run mode
target-oracle-oic --config config.json --dry-run

# Validation only
target-oracle-oic --config config.json --validate-only
```

---

## 🛠️ **CLI Reference**

```bash
# Basic deployment
target-oracle-oic --config config.json

# Specific streams
target-oracle-oic --config config.json --streams connections,integrations

# Archive deployment
target-oracle-oic --config config.json --archive-dir /path/to/archives

# Validation mode
target-oracle-oic --config config.json --validate

# Version info
target-oracle-oic --version
```

---

## 📖 **Advanced Usage**

### **Custom Deployment Logic**

```python
# custom_target.py
from target_oracle_oic import TargetOracleOIC

class CustomOICTarget(TargetOracleOIC):
    """Extended target with custom deployment logic."""

    def pre_deployment_hook(self, artifact):
        """Custom validation before deployment."""
        # Environment-specific checks
        if self.config.get("environment") == "production":
            require_approval(artifact)

        # Custom validation
        validate_naming_convention(artifact)
        check_security_compliance(artifact)

    def post_deployment_hook(self, artifact, result):
        """Custom actions after deployment."""
        # Send notifications
        notify_team(artifact, result)

        # Update CMDB
        update_configuration_database(artifact)
```

### **Multi-Environment Deployment**

```yaml
# meltano.yml
project_id: oic_deployments
environments:
  - name: dev
    config:
      target-oracle-oic:
        base_url: ${DEV_OIC_URL}
        activate_integrations: true
  - name: prod
    config:
      target-oracle-oic:
        base_url: ${PROD_OIC_URL}
        activate_integrations: false
        validate_connections: true
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Singer Specification](https://hub.meltano.com/singer/spec) - Singer protocol specification
- [Oracle OIC Documentation](https://docs.oracle.com/en/cloud/paas/integration-cloud/) - Official OIC docs
- [OAuth2 RFC](https://datatracker.ietf.org/doc/html/rfc6749) - OAuth2 specification

### **Next Steps**

- [OIC Deployment Guide](../docs/guides/oic-deployment.md) - Deployment strategies
- [CI/CD Integration](../docs/guides/cicd-oic.md) - Pipeline setup
- [Production Checklist](../docs/deployment/oic-production.md) - Go-live guide

### **Related Topics**

- [Singer Best Practices](../docs/patterns/singer.md) - Target patterns
- [GitOps Patterns](../docs/patterns/gitops.md) - Git-based deployments
- [Blue-Green Deployments](../docs/patterns/blue-green.md) - Zero-downtime strategies

---

**📂 Component**: Target Oracle OIC | **🏠 Root**: [PyAuto Home](../README.md) | **Framework**: Singer SDK 0.39.0+ | **Updated**: 2025-06-19
