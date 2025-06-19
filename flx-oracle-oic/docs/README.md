# tap-oic Documentation

> **Oracle Integration Cloud (OIC) Singer Tap** > **Version**: 2.0
> **Last Updated**: June 15, 2025

## Overview

tap-oic is a Singer tap for Oracle Integration Cloud Generation 3 that provides data extraction capabilities for:

- **Extracting** integration metadata, connections, and packages
- **Monitoring** integration execution status and performance metrics
- **Tracking** error rates, success rates, and execution history
- **Retrieving** configuration data and integration artifacts (.iar files)

## Quick Links

| Document                                                | Description                                             |
| ------------------------------------------------------- | ------------------------------------------------------- |
| [OIC Capabilities](OIC_CAPABILITIES.md)                 | Complete guide to OIC Gen3 capabilities and limitations |
| [API Reference](API_REFERENCE.md)                       | Full REST API documentation with examples               |
| [Installation & Setup](INSTALLATION_AND_SETUP.md)       | Getting started guide                                   |
| [Implementation Guide](IMPLEMENTATION_GUIDE.md)         | Architecture and best practices                         |
| [Integration Management](INTEGRATION_GENERATION.md)     | Managing existing integrations and artifacts            |
| [Meltano Integration](MELTANO_INTEGRATION.md)           | Using tap-oic with Meltano                              |
| [Monitoring & Operations](MONITORING_AND_OPERATIONS.md) | Performance and troubleshooting                         |
| [Development Guide](DEVELOPMENT_GUIDE.md)               | Contributing to tap-oic                                 |
| [Examples](EXAMPLES.md)                                 | Code examples and use cases                             |
| [FAQ](FAQ.md)                                           | Frequently asked questions                              |
| [Changelog](CHANGELOG.md)                               | Version history and updates                             |

## Key Features

### 1. Data Extraction (Singer Tap Capabilities)

- Extract integration metadata and configurations
- Monitor integration execution status
- Retrieve performance metrics and statistics
- Track error rates and success rates
- Access connection configurations
- Download integration artifacts (.iar files)

### 2. Monitoring and Analytics

- Real-time integration status monitoring
- Historical execution data analysis
- Performance metrics collection
- Error tracking and reporting
- Success rate calculations

### 3. Configuration Management

- Export integration configurations
- Retrieve connection properties
- Access lookup tables and libraries
- Extract project organization data

## Quick Start

```bash
# Install tap-oic
pip install tap-oic

# Configure authentication
export OIC_HOST="your-instance.integration.ocp.oraclecloud.com"
export OIC_CLIENT_ID="your-oauth-client-id"
export OIC_CLIENT_SECRET="your-oauth-client-secret"
export OIC_TOKEN_URL="https://idcs.identity.oraclecloud.com/oauth2/v1/token"

# Discover available streams
tap-oic --config config.json --discover > catalog.json

# Extract integration data
tap-oic --config config.json --catalog catalog.json

# Pipe to a target for data storage
tap-oic --config config.json --catalog catalog.json | target-postgres --config target-config.json
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    tap-oic (Singer Tap)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │   Core Data     │  │   Monitoring    │  │   Artifacts     ││
│  │   Extraction    │  │   Streams       │  │   Download      ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │            OIC REST API v1 (Read-Only Access)              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
                    Singer Protocol (JSON)
                             ↓
            ┌─────────────────────────────────────┐
            │     Singer Targets (Storage)        │
            │  • target-postgres                  │
            │  • target-snowflake                │
            │  • target-s3                       │
            └─────────────────────────────────────┘
```

## Future Roadmap: Version 3.0

### 🚀 Integration Generator & Workflow Creator (Planned)

We are planning to extend tap-oic beyond data extraction to become a comprehensive integration platform:

- **🔧 Integration Generation**: Create OIC integrations programmatically from YAML/JSON configuration
- **🔄 Workflow Creation**: Define and deploy complex multi-step workflows
- **🎵 Singer Integration**: Generate OIC integrations from any Singer tap/target combination
- **📝 Infrastructure as Code**: Version control and manage OIC integrations like code
- **🚢 GitOps Support**: Full CI/CD pipelines for integration deployment

**See [Integration Generator Roadmap](INTEGRATION_GENERATOR_ROADMAP.md) for detailed implementation plans.**

### Preview of Future Capabilities

```yaml
# Future: Define integrations as code
apiVersion: oic/v1
kind: Integration
metadata:
  name: customer-sync
spec:
  source:
    type: database
    query: SELECT * FROM customers
  target:
    type: rest
    endpoint: https://api.example.com/customers
```

## Support

- **Documentation Issues**: Open an issue in the GitHub repository
- **Oracle Support**: Contact Oracle Support for OIC-specific issues
- **Community**: Join the Singer Slack community

## License

This project is licensed under the Apache License 2.0. See LICENSE file for details.
