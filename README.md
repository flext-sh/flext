# FLEXT - Enterprise Data Integration Platform

**Version**: 2.0.0-dev | **Status**: ACTIVE DEVELOPMENT | **Last Updated**: 2025-08-13

## Overview

FLEXT is an enterprise-grade data integration platform under active development that will orchestrate, monitor, and manage distributed data pipelines. Built with a hybrid Go/Python architecture implementing Clean Architecture, DDD, and CQRS patterns.

> ⚠️ **Development Status**: This project is currently under active development with significant architectural work in progress. See individual project READMEs and TODO.md files for current status and limitations.

## 🚀 Quick Start

- **New Developers**: [Getting Started Guide](docs/guides/getting-started/README.md)
- **Quick Reference**: [Patterns & API Quick Reference](docs/quick-reference.md)
- **Architecture Overview**: [System Architecture](docs/architecture/overview.md)
- **Python-Go Integration**: [Integration Architecture](docs/architecture/python-go-integration.md)

## 📚 Documentation Index

### [Architecture](docs/architecture/README.md)

System design, patterns, and technical architecture documentation.

- [Overview](docs/architecture/overview.md) - High-level architecture
- [Clean Architecture](docs/architecture/clean-architecture.md) - Design principles
- [Ecosystem](docs/architecture/ecosystem.md) - Complete ecosystem
- [Services](docs/architecture/services.md) - Service design
- [Python-Go Integration](docs/architecture/python-go-integration.md) - Go-Python integration patterns
- [Integration](docs/architecture/integration.md) - Integration patterns
- [Package Structure](docs/architecture/pkg-structure.md) - Go package organization
- [Workspace](docs/architecture/workspace.md) - Workspace organization

### [Patterns](docs/patterns/README.md)

Semantic patterns and coding standards for the FLEXT ecosystem.

- [Foundation](docs/patterns/foundation.md) - Core patterns
- [Type System](docs/patterns/types.md) - Type architecture
- [Configuration](docs/patterns/config-cli.md) - Config & CLI
- [Error Handling](docs/patterns/error-observability.md) - Errors & observability
- [Constants](docs/patterns/constants.md) - Semantic constants
- [Utilities](docs/patterns/utilities.md) - Helper patterns

### [API Reference](docs/api/README.md)

Complete API documentation and contracts.

- [REST API](docs/api/contracts.md) - RESTful endpoints
- [OpenAPI Specs](docs/api/openapi/) - Machine-readable specifications

### [User Guides](docs/guides/README.md)

Step-by-step guides for common tasks.

- [Getting Started](docs/guides/getting-started/README.md) - First-time setup
- [Configuration](docs/guides/configuration/README.md) - Configuration management
- [Deployment](docs/guides/deployment/README.md) - Deployment options
- [Troubleshooting](docs/guides/troubleshooting/README.md) - Problem resolution

### [Standards](docs/standards/README.md)

Coding standards and best practices.

- [Documentation](docs/standards/documentation.md) - Documentation standards
- [Python](docs/standards/python.md) - Python coding standards
- [PEP Semantic](docs/standards/pep-semantic.md) - PEP compliance matrix

### [Development](docs/development/README.md)

Development planning and status.

- [Implementation Plan](docs/development/implementation-plan.md) - Roadmap
- [Documentation Status](docs/development/documentation-status.md) - Current status

## 🏗️ Technology Stack

- **Go 1.24+**: Control plane and orchestration
- **Python 3.13+**: Data processing (Singer SDK, Meltano, DBT)
- **PostgreSQL 15**: Primary data store
- **Redis 7**: Caching and message broker
- **Docker**: Containerization

## 🌐 Ecosystem Components

### Core Services

- **FLEXT Control Panel** (`flext-sh/flext`) - Port 8081
- **FlexCore Runtime** (`flext-sh/flexcore`) - Port 8080

### Library Ecosystem (30+ Projects)

- **Foundation**: flext-core, flext-observability
- **Singer Taps/Targets**: LDAP, LDIF, Oracle, Oracle-OIC, Oracle-WMS
- **DBT Projects**: LDAP, LDIF, Oracle, Oracle-WMS
- **Infrastructure**: DB-Oracle, LDAP, LDIF, Oracle-WMS, gRPC
- **Application Services**: API, Auth, Web, CLI, Meltano, Plugin, Quality

## 🔗 Integration Architecture

### Python-Go Integration

FLEXT implements a hybrid architecture where Go services orchestrate Python libraries:

- **Go Control Plane**: Service orchestration, API management, workflow coordination
- **Python Ecosystem**: Data processing, ETL operations, domain-specific logic
- **Integration Patterns**: gRPC, HTTP/REST, subprocess execution
- **Service Coordination**: Distributed tracing, load balancing, failover

### Key Integration Points

- **gRPC Services**: High-performance service-to-service communication
- **REST APIs**: External API exposure with Go as gateway
- **Subprocess Execution**: Direct Python script execution from Go
- **Event Coordination**: Distributed event streaming across services

## 📊 Current Development Status

### Architecture Progress

- **flext-core (Foundation)**: Significant progress - 1,249 MyPy errors (71% reduction, only 4 in src/)
- **FlexCore (Go Runtime)**: Clean Architecture violations being fixed - 30% compliance
- **FLEXT Service (Go Control Panel)**: Multi-modal architecture in development
- **Python Ecosystem**: Singer/Meltano/DBT integration in progress
- **Documentation**: Being standardized and aligned with actual code state

### Ready for Development Use

- **Core Patterns**: FlextResult, FlextContainer, basic DDD patterns working
- **Docker Environment**: Development infrastructure operational
- **CI/CD Pipeline**: Quality gates and validation working
- **Basic Services**: HTTP APIs and database connectivity functional

### Not Yet Production Ready

- **Clean Architecture**: Significant refactoring needed across services
- **Type Safety**: Major MyPy error resolution in progress
- **Event Sourcing**: Foundation exists but needs complete implementation
- **Plugin System**: Basic framework exists, security and isolation needed
- **Cross-Service Integration**: APIs exist but need comprehensive testing

## 🚀 Development Setup

### Prerequisites

```bash
# Required software
- Go 1.24+
- Python 3.13+
- Docker & Docker Compose
- Make utility
- Git

# Verify installations
go version        # Should show 1.24+
python --version  # Should show 3.13+
docker --version  # Should show 24.0+
make --version    # Any recent version
```

### Development Environment Setup

```bash
# 1. Clone and setup workspace
git clone https://github.com/flext-sh/flext.git
cd flext

# 2. Complete development setup
make setup                    # Install tools, dependencies, pre-commit hooks
make workspace-install        # Install all project dependencies
make dev-setup               # Configure development environment

# 3. Start infrastructure services
make docker-up               # PostgreSQL, Redis, monitoring stack

# 4. Start FLEXT services
make run-all                 # Start all FLEXT services

# 5. Verify installation
make health-check            # Verify all services are healthy
curl http://localhost:8081/health  # FLEXT Control Panel
curl http://localhost:8080/health  # FlexCore Runtime
```

### First Pipeline Setup

```bash
# Configure your first data pipeline
flext pipeline create \
  --name "sample-etl" \
  --source "postgres://localhost/source" \
  --target "postgres://localhost/target" \
  --schedule "daily"

# Monitor pipeline execution
flext pipeline status sample-etl
flext logs pipeline sample-etl --follow
```

## 🛠️ Development Commands

### Workspace-Level Operations

```bash
# Quality Gates (mandatory before commits)
make validate                # Complete validation pipeline
make check                   # Quick lint + type check
make security-scan          # Security vulnerability analysis
make test-all               # Run all test suites
make coverage-report        # Generate coverage reports

# Build Operations
make build-all              # Build all components
make build-go               # Build Go services only
make build-python           # Build Python packages only
make docker-build           # Build Docker images

# Development Workflow
make dev-setup              # Setup development environment
make dev-run                # Start development servers
make dev-test               # Run tests in watch mode
make dev-clean              # Clean development artifacts
```

### Individual Service Commands

```bash
# Navigate to any service directory (cmd/flext, cmd/flext-cli, etc.)
make build                  # Build specific service
make test                   # Run service tests
make run                    # Start service locally
make debug                  # Start with debugging enabled
make benchmark              # Run performance benchmarks
```

### Docker & Infrastructure

```bash
# Infrastructure Management
make docker-up              # Start all infrastructure services
make docker-down            # Stop all services
make docker-restart         # Restart all services
make docker-logs            # View aggregated logs
make docker-clean           # Clean Docker resources

# Database Operations
make db-migrate             # Apply database migrations
make db-reset               # Reset database (development)
make db-backup              # Create database backup
make db-restore             # Restore from backup
```

## ⚙️ Configuration Management

### Environment Configuration

```bash
# Core Service Configuration
export FLEXT_MODE="control_panel"           # Operating mode
export FLEXT_SERVER_PORT="8081"             # Control panel port
export FLEXCORE_RUNTIME_PORT="8080"         # Runtime service port
export FLEXT_LOG_LEVEL="info"               # Logging level

# Database Configuration
export FLEXT_DATABASE_URL="postgresql://flext:password@localhost:5433/flext"
export FLEXT_REDIS_URL="redis://localhost:6380/0"
export FLEXT_CACHE_TTL="3600"               # Cache TTL in seconds

# Integration Configuration
export MELTANO_PROJECT_ROOT="/opt/meltano"
export SINGER_CACHE_DIR="/tmp/singer-cache"
export DBT_PROFILES_DIR="/opt/dbt/profiles"

# Observability Configuration
export OTEL_SERVICE_NAME="flext-control-panel"
export OTEL_RESOURCE_ATTRIBUTES="service.version=2.0.0,deployment.environment=development"
export PROMETHEUS_ENDPOINT="http://localhost:9090"
export JAEGER_COLLECTOR_ENDPOINT="http://localhost:14268/api/traces"
```

### Service Discovery

```yaml
# config/services.yaml
services:
  flext_control_panel:
    port: 8081
    health_endpoint: "/health"
    metrics_endpoint: "/metrics"
  flexcore_runtime:
    port: 8080
    health_endpoint: "/health"
    metrics_endpoint: "/metrics"
  postgresql:
    port: 5433
    health_command: "pg_isready"
  redis:
    port: 6380
    health_command: "redis-cli ping"
```

## 📡 API Documentation

### REST API Endpoints

```bash
# Pipeline Management
GET    /api/v1/pipelines              # List all pipelines
POST   /api/v1/pipelines              # Create new pipeline
GET    /api/v1/pipelines/{id}         # Get pipeline details
PUT    /api/v1/pipelines/{id}         # Update pipeline
DELETE /api/v1/pipelines/{id}         # Delete pipeline
POST   /api/v1/pipelines/{id}/execute # Execute pipeline

# Data Source Management
GET    /api/v1/sources                # List data sources
POST   /api/v1/sources                # Register data source
GET    /api/v1/sources/{id}/schema    # Get source schema
POST   /api/v1/sources/{id}/test      # Test source connection

# Monitoring & Observability
GET    /api/v1/health                 # Service health status
GET    /api/v1/metrics                # Prometheus metrics
GET    /api/v1/logs                   # Query service logs
GET    /api/v1/traces                 # Distributed traces
```

### CLI Interface

```bash
# Pipeline Operations
flext pipeline list                   # List all pipelines
flext pipeline create --config pipeline.yaml
flext pipeline execute sample-etl
flext pipeline status sample-etl --watch

# Data Source Management
flext source add postgres --url "postgresql://..."
flext source test postgres-source
flext source schema postgres-source --output json

# Monitoring Commands
flext health                         # Overall system health
flext logs --service flext-control-panel --follow
flext metrics --service all --export prometheus
```

## 🎯 Quality Standards

### Quality Targets

- **Test Coverage**: 90% target across packages
- **Type Safety**: MyPy strict mode for Python; Go static typing
- **Code Quality**: Comprehensive linting (Ruff for Python, golangci-lint for Go)
- **Security**: Vulnerability scanning (Bandit, gosec, Snyk)
- **Documentation**: Public APIs documented and kept current
- **Performance**: Performance testing with thresholds tracked

### Testing Strategy

```bash
# Test Categories
make test-unit              # Fast unit tests (< 1s per test)
make test-integration       # Integration tests with external dependencies
make test-e2e               # End-to-end pipeline tests
make test-performance       # Performance and load testing
make test-security          # Security penetration testing

# Test Execution Patterns
make test-watch             # Continuous testing during development
make test-coverage          # Generate detailed coverage reports
make test-mutation          # Mutation testing for test quality
```

## 🚀 Deployment

### Development Deployment

```bash
# Local development with hot reload
make dev-start              # Start all services in development mode
make dev-migrate            # Apply database migrations
make dev-seed               # Seed with sample data
make dev-monitor            # Open monitoring dashboard
```

### Production Deployment

```bash
# Container-based deployment
make docker-build-prod      # Build production-optimized images
make docker-deploy-prod     # Deploy to production environment
make health-check-prod      # Verify production deployment

# Kubernetes deployment
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
```

### Infrastructure as Code

```bash
# Terraform deployment
cd infrastructure/terraform
terraform init
terraform plan -var-file="prod.tfvars"
terraform apply

# Helm chart deployment
helm install flext-platform ./charts/flext \
  --namespace flext-platform \
  --values values.prod.yaml
```

## 📊 Monitoring and Observability

### Built-in Monitoring

```bash
# Health Monitoring
curl http://localhost:8081/health     # Control panel health
curl http://localhost:8080/health     # Runtime health
make health-check-all                 # Comprehensive health check

# Metrics Collection
curl http://localhost:8081/metrics    # Prometheus metrics
make metrics-export                   # Export metrics to file
make metrics-dashboard                # Open Grafana dashboard

# Distributed Tracing
make trace-analysis                   # Analyze request traces
make trace-performance               # Performance bottleneck analysis
```

### Dashboard Access

- **Grafana**: <http://localhost:3000> (REDACTED_LDAP_BIND_PASSWORD/REDACTED_LDAP_BIND_PASSWORD)
- **Prometheus**: <http://localhost:9090>
- **Jaeger**: <http://localhost:16686>
- **Control Panel**: <http://localhost:8081/dashboard>

## ⚡ Performance Benchmarks

### Expected Performance Characteristics

```bash
# Pipeline Throughput
- Small datasets (< 10MB): 1000+ records/second
- Medium datasets (10MB-1GB): 500+ records/second
- Large datasets (> 1GB): 100+ records/second

# API Response Times
- Health checks: < 10ms
- Pipeline status: < 100ms
- Pipeline creation: < 500ms
- Data source queries: < 2s

# Resource Usage
- Memory: < 512MB per service instance
- CPU: < 50% utilization under normal load
- Storage: Configurable with automatic cleanup
```

## 🔧 Troubleshooting

### Common Issues

```bash
# Service Startup Issues
make diagnose               # Comprehensive system diagnostics
make logs-all              # View all service logs
make port-check            # Check for port conflicts

# Database Connection Issues
make db-diagnose           # Database connectivity diagnosis
make db-connection-test    # Test database connections
psql -h localhost -p 5433 -U flext -d flext  # Direct database access

# Performance Issues
make performance-profile   # Profile application performance
make resource-monitor      # Monitor resource usage
make bottleneck-analysis   # Identify performance bottlenecks
```

### Debug Mode

```bash
# Enable comprehensive debugging
export FLEXT_LOG_LEVEL=debug
export FLEXT_DEBUG_MODE=true
export FLEXT_TRACE_REQUESTS=true

# Start services with debugging enabled
make debug-all

# Generate diagnostic reports
make debug-report          # Generate comprehensive debug report
make debug-export          # Export debug data for analysis
```

## 🤝 Contributing

### Development Workflow

1. **Fork & Clone**: Fork repository and clone locally
2. **Branch**: Create feature branch: `git checkout -b feature/pipeline-optimization`
3. **Develop**: Implement changes following Clean Architecture principles
4. **Test**: Ensure 90%+ test coverage: `make test-coverage`
5. **Quality**: Pass all quality gates: `make validate`
6. **Document**: Update relevant documentation
7. **Submit**: Create pull request with detailed description

### Code Standards

```bash
# Before submitting changes
make format-all            # Auto-format all code
make lint-all              # Fix linting issues
make test-all              # Ensure all tests pass
make security-scan         # Check for security vulnerabilities
make validate              # Run complete validation pipeline
```

## 📋 Contributing

1. Fork the repository
2. Create feature branch: `feat/your-feature`
3. Follow [coding standards](docs/standards/README.md)
4. Submit pull request with clear description

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions)
- **Development**: See [CLAUDE.md](CLAUDE.md) for AI guidance

---

**Maintainers**: FLEXT Development Team | **License**: MIT
