# FLEXT Documentation Hub

**Category**: Documentation Hub | **Status**: Active Development | **Version**: 2.0.0-dev | **Last Updated**: 2025-08-10

Welcome to the FLEXT documentation hub. This comprehensive guide provides everything you need to understand, use, and contribute to the FLEXT ecosystem.

## Table of Contents

- [Quick Start](#quick-start)
- [Documentation Structure](#documentation-structure)
- [User Documentation](#user-documentation)
- [Developer Documentation](#developer-documentation)
- [Reference Documentation](#reference-documentation)
- [Standards and Guidelines](#standards-and-guidelines)
- [Getting Help](#getting-help)

## Quick Start

### For New Users

1. **Start Here**: [Installation Guide](./getting-started/installation.md)
2. **Quick Tutorial**: [Quick Start Guide](./getting-started/quick-start.md)
3. **First Project**: [Data Integration Guide](./user-guides/data-integration/README.md)

### For Developers

1. **Architecture**: [System Overview](./developer/architecture/README.md)
2. **API Reference**: [Complete API Docs](./reference/api/README.md)
3. **Contributing**: [Development Guidelines](./developer/contributing/README.md)

### For System Administrators

1. **Deployment**: [Deployment Guide](./developer/deployment/README.md)
2. **Configuration**: [System Configuration](./user-guides/configuration/README.md)
3. **Monitoring**: [Observability Guide](./user-guides/troubleshooting/monitoring.md)

## Documentation Structure

Our documentation is organized into logical sections to help you find what you need quickly:

```
docs/
├── getting-started/          # Quick start guides and installation
├── user-guides/             # End-user documentation by use case
├── developer/               # Technical implementation details
├── reference/               # Complete API and configuration reference
├── standards/               # Documentation standards and templates
└── archive/                 # Deprecated content
```

## User Documentation

### Getting Started

- **[Installation Guide](./getting-started/installation.md)** - Complete installation instructions
- **[Quick Start Guide](./getting-started/quick-start.md)** - Get up and running in 10 minutes
- **[Prerequisites](./getting-started/prerequisites.md)** - System requirements and dependencies

### User Guides

- **[Data Integration](./user-guides/data-integration/README.md)** - ETL/ELT workflows and patterns
- **[Authentication](./user-guides/authentication/README.md)** - User authentication and authorization
- **[Configuration](./user-guides/configuration/README.md)** - System configuration and customization
- **[Troubleshooting](./user-guides/troubleshooting/README.md)** - Common issues and solutions

## Developer Documentation

### Architecture

- **[System Overview](./developer/architecture/README.md)** - High-level architecture and design
- **[Clean Architecture](./developer/architecture/clean-architecture.md)** - Design principles and patterns
- **[Python-Go Integration](./developer/architecture/python-go-integration.md)** - Cross-language integration
- **[Package Structure](./developer/architecture/pkg-structure.md)** - Code organization

### Development

- **[API Development](./developer/api/README.md)** - Building and extending APIs
- **[Coding Patterns](./developer/patterns/README.md)** - Standard patterns and practices
- **[Deployment](./developer/deployment/README.md)** - Deployment strategies and infrastructure
- **[Contributing](./developer/contributing/README.md)** - How to contribute to FLEXT

## Reference Documentation

### API Reference

- **[REST API](./reference/api/rest-api.md)** - Complete REST API documentation
- **[Python SDK](./reference/api/python-sdk.md)** - Python client library reference
- **[Go SDK](./reference/api/go-sdk.md)** - Go client library reference
- **[OpenAPI Specs](./reference/api/openapi/)** - Machine-readable API specifications

### Configuration Reference

- **[Configuration Files](./reference/configuration/files.md)** - All configuration options
- **[Environment Variables](./reference/configuration/environment.md)** - Environment variable reference
- **[CLI Options](./reference/cli/README.md)** - Command-line interface reference

## Standards and Guidelines

### Documentation Standards

- **[Documentation Standards](./standards/README.md)** - How to write and maintain documentation
- **[Writing Guide](./standards/writing-guide.md)** - Detailed writing guidelines
- **[Style Guide](./standards/style-guide.md)** - Visual and formatting standards
- **[Templates](./standards/templates/)** - Standard document templates

### Development Standards

- **[Python Standards](./standards/python.md)** - Python coding conventions
- **[Go Standards](./standards/go.md)** - Go coding conventions
- **[API Standards](./standards/api.md)** - API design and documentation standards

## Project-Specific Documentation

### Core Components

- **[FlexCore](./flexcore/README.md)** - Go-based core system
- **[FLEXT API](./flext-api/README.md)** - Python API server
- **[FLEXT CLI](./flext-cli/README.md)** - Command-line interface
- **[FLEXT Web](./flext-web/README.md)** - Web interface

### Data Integration

- **[FLEXT TAP Oracle](./flext-tap-oracle/README.md)** - Oracle data extraction
- **[FLEXT TAP LDAP](./flext-tap-ldap/README.md)** - LDAP data extraction
- **[FLEXT Target Oracle](./flext-target-oracle/README.md)** - Oracle data loading
- **[FLEXT DBT Projects](./flext-dbt-oracle/README.md)** - Data transformation

### Authentication & Security

- **[FLEXT Auth](./flext-auth/README.md)** - Authentication system
- **[FLEXT LDAP](./flext-ldap/README.md)** - LDAP integration
- **[FLEXT LDIF](./flext-ldif/README.md)** - LDIF processing

## Getting Help

### Documentation Status

- **Current Version**: 2.0.0-dev
- **Last Updated**: 2025-08-10
- **Coverage**: Major components documented; sections in progress
- **Status**: Active development

### Support Channels

- **GitHub Issues**: [Report bugs or request features](https://github.com/flext-sh/flext/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/flext-sh/flext/discussions)
- **Documentation Issues**: [Report documentation problems](https://github.com/flext-sh/flext/issues?q=label%3Adocumentation)

### Contributing to Documentation

1. **Fork the repository**
2. **Create a feature branch**: `docs/your-improvement`
3. **Follow the [documentation standards](./standards/README.md)**
4. **Submit a pull request** with clear description

### Documentation Roadmap

- **Q1 2025**: Complete API reference documentation
- **Q2 2025**: Add video tutorials and interactive examples
- **Q3 2025**: Implement documentation search and analytics
- **Q4 2025**: Add multilingual support

## Related Resources

- **[Main Project README](../README.md)** - Project overview and quick start
- **[Development Guide](../docs/development/README.md)** - Development planning and status
- **[Architecture Overview](../docs/architecture/README.md)** - System architecture details

---

**Contributors**: FLEXT Documentation Team  
**Last Updated**: 2025-08-07  
**Version**: 2.1.0
