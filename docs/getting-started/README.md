# Getting Started with FLEXT

**Category**: Getting Started | **Status**: Published | **Version**: 1.0.0 | **Last Updated**: 2025-08-07

Welcome to FLEXT! This section will help you get up and running quickly, whether you're a new user, developer, or system REDACTED_LDAP_BIND_PASSWORDistrator.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [Installation](#installation)
- [First Steps](#first-steps)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Quick Navigation

### For New Users

1. **[Installation Guide](./installation.md)** - Complete setup instructions
2. **[Quick Start Guide](./quick-start.md)** - Get running in 10 minutes
3. **[Prerequisites](./prerequisites.md)** - System requirements

### For Developers

1. **[Development Setup](./development-setup.md)** - Development environment
2. **[Architecture Overview](../developer/architecture/README.md)** - System design
3. **[API Reference](../reference/api/README.md)** - Complete API docs

### For System Administrators

1. **[Production Deployment](./production-deployment.md)** - Production setup
2. **[Configuration Guide](../user-guides/configuration/README.md)** - System configuration
3. **[Monitoring Setup](../user-guides/troubleshooting/monitoring.md)** - Observability

## Installation

### Prerequisites

Before installing FLEXT, ensure you have:

- **Python 3.8+** and **Go 1.19+**
- **Docker** and **Docker Compose** (for containerized deployment)
- **Git** for version control
- **PostgreSQL** or **Oracle** database (depending on your needs)

### Installation Options

#### Option 1: Quick Install (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/flext-sh/flext.git
cd flext

# Install Python dependencies
pip install -r requirements.txt

# Install Go dependencies
go mod download

# Start with Docker Compose
docker-compose up -d
```

#### Option 2: Manual Installation

Follow the [detailed installation guide](./installation.md) for step-by-step instructions.

#### Option 3: Cloud Deployment

Use our [cloud deployment guides](./cloud-deployment.md) for AWS, Azure, or GCP.

## First Steps

### 1. Verify Installation

```bash
# Check FLEXT CLI
flext --version

# Check API server
curl http://localhost:8080/health

# Check FlexCore (Go service)
curl http://localhost:8081/health
```

### 2. Create Your First Configuration

```yaml
# config/flext.yaml
flext:
  api:
    host: "0.0.0.0"
    port: 8080
  database:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "flext"
    username: "flext_user"
    password: "your_password"
```

### 3. Run Your First Data Integration

```python
from flext import FlextClient

# Initialize client
client = FlextClient(config_path="config/flext.yaml")

# Create a simple data pipeline
pipeline = client.create_pipeline(
    name="my-first-pipeline",
    source="oracle",
    target="postgresql"
)

# Run the pipeline
result = pipeline.run()
print(f"Pipeline completed: {result.status}")
```

## Next Steps

### For Data Engineers

- **[Data Integration Guide](../user-guides/data-integration/README.md)** - ETL/ELT workflows
- **[Oracle Integration](../user-guides/data-integration/oracle.md)** - Oracle-specific setup
- **[LDAP Integration](../user-guides/data-integration/ldap.md)** - LDAP data extraction

### For Developers

- **[API Development](../developer/api/README.md)** - Building and extending APIs
- **[Coding Patterns](../developer/patterns/README.md)** - Standard patterns
- **[Testing Guide](../developer/testing.md)** - Testing strategies

### For DevOps Engineers

- **[Deployment Guide](../developer/deployment/README.md)** - Production deployment
- **[Monitoring Setup](../user-guides/troubleshooting/monitoring.md)** - Observability
- **[Security Configuration](../user-guides/authentication/security.md)** - Security setup

## Troubleshooting

### Common Issues

#### Installation Problems

- **Python dependencies fail**: Check Python version and virtual environment
- **Go modules fail**: Ensure Go version is 1.19+ and GOPATH is set
- **Docker issues**: Verify Docker and Docker Compose are installed

#### Connection Issues

- **Database connection fails**: Check database credentials and network access
- **API server won't start**: Verify port availability and configuration
- **Services can't communicate**: Check Docker network configuration

#### Performance Issues

- **Slow data processing**: Review database indexes and query optimization
- **Memory usage high**: Adjust configuration limits and resource allocation
- **Network timeouts**: Check network configuration and firewall settings

### Getting Help

1. **Check the logs**: `docker-compose logs -f [service-name]`
2. **Verify configuration**: `flext config validate`
3. **Run diagnostics**: `flext diagnose`
4. **Search documentation**: Use the search function in this documentation
5. **Ask the community**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions)

## Related Documentation

- **[User Guides](../user-guides/README.md)** - Complete user documentation
- **[Developer Documentation](../developer/README.md)** - Technical implementation details
- **[API Reference](../reference/api/README.md)** - Complete API documentation
- **[Configuration Reference](../reference/configuration/README.md)** - All configuration options

---

**Contributors**: FLEXT Documentation Team  
**Last Updated**: 2025-08-07  
**Version**: 1.0.0
