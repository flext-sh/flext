# FLEXT Control Panel - Data Integration Platform

**Version 2.0.0** | **Status: Active Development** | **Ecosystem Projects: 32+**

Data integration platform built with Go 1.24+ and Python 3.13+, implementing Clean Architecture and Domain-Driven Design patterns. FLEXT provides data pipeline orchestration and management capabilities for distributed data integration workflows.

## Project Overview

FLEXT is the **Control Panel** component of a comprehensive data integration ecosystem, designed to orchestrate, monitor, and manage distributed data pipelines across enterprise environments. It provides a unified interface for managing data taps, targets, transformations, and pipeline executions.

### 🎯 Core Objectives

- **Unified Control**: Single control plane for managing all data integration operations
- **Enterprise Scale**: Handle thousands of concurrent data pipelines with high reliability
- **Clean Architecture**: Maintainable, testable, and extensible codebase following DDD principles
- **Observable**: Comprehensive monitoring, metrics, and tracing for operational visibility
- **Extensible**: Plugin-based architecture supporting custom data connectors and transformations

## Architecture Overview

FLEXT implements a hybrid Go/Python architecture optimized for both performance and flexibility:

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM                              │
├─────────────────────────────────────────────────────────────────┤
│  FLEXT Control Panel       │  FlexCore Runtime                 │
│  (flext-sh/flext)          │  (flext-sh/flexcore)              │
│  Port: 8081                │  Port: 8080                       │
│  ├─ Pipeline Management    │  ├─ Plugin Execution             │
│  ├─ Data Source Config     │  ├─ Event Sourcing               │
│  ├─ Monitoring Dashboard   │  ├─ CQRS Commands                │
│  ├─ REST API               │  ├─ Distributed Coordination     │
│  └─ CLI Interface          │  └─ Performance Monitoring       │
└─────────────────────────────────────────────────────────────────┘
```

### 🏗️ Clean Architecture Structure

```
pkg/                              # Public API following Go standards
├── adapters/                     # Interface Adapters Layer
│   ├── controllers/http/         # REST API Controllers + DTOs
│   ├── gateways/                 # External System Gateways
│   └── presenters/               # Response Presentation Logic
├── application/                  # Application Business Logic
│   ├── commands/                 # CQRS Commands
│   ├── queries/                  # CQRS Queries
│   ├── services/                 # Application Services
│   ├── dbt/                      # DBT Transformation Management
│   ├── meltano/                  # Meltano Orchestration
│   ├── pipeline/                 # Pipeline Lifecycle Management
│   ├── plugin/                   # Plugin Management
│   └── singer/                   # Singer Tap/Target Management
├── domain/                       # Domain Business Logic
│   ├── entities/                 # Core Business Entities
│   ├── events/                   # Domain Events
│   ├── repositories/             # Repository Interfaces
│   ├── services/                 # Domain Services
│   └── [bounded-contexts]/       # DDD Bounded Contexts
├── infrastructure/               # Infrastructure Concerns
│   ├── database/                 # Database Access + Migrations
│   ├── http/                     # HTTP Infrastructure
│   ├── messaging/                # Message Bus Implementation
│   ├── cache/                    # Caching Layer
│   └── logging/                  # Structured Logging
├── interfaces/                   # External Interfaces
│   ├── api/                      # REST API Definitions
│   ├── cli/                      # Command Line Interface
│   └── web/                      # Web Interface
└── utils/                        # Shared Utilities
    ├── shared_kernel/            # DDD Shared Kernel
    └── gopy/                     # Go-Python Integration Bridge
```

## Technology Stack

### Core Technologies

- **Go 1.24+**: High-performance control plane with Clean Architecture
- **Python 3.13+**: Data processing integration with Singer SDK, Meltano, DBT
- **PostgreSQL 15**: Primary data store with ACID compliance (port 5433)
- **Redis 7**: Caching, session management, and message broker (port 6380)
- **Docker**: Containerization and development environment

### Data Integration Stack

- **Singer SDK**: Standardized data tap and target framework
- **Meltano 3.8.0**: ELT orchestration and pipeline management
- **DBT**: Data transformation and modeling framework
- **Apache Airflow**: Advanced workflow orchestration (enterprise deployments)

### Observability Stack

- **OpenTelemetry**: Distributed tracing and metrics collection
- **Prometheus**: Metrics storage and alerting (port 9090)
- **Grafana**: Monitoring dashboards and visualization (port 3000)
- **Jaeger**: Distributed tracing UI (port 16686)

## Quick Start

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

## Development Commands

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

## Configuration Management

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

## API Documentation

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

## Quality Standards

### Zero Tolerance Quality Gates

- **Test Coverage**: Minimum 90% coverage enforced for all packages
- **Type Safety**: Strict type checking (MyPy for Python, Go's type system)
- **Code Quality**: Comprehensive linting (Ruff for Python, golangci-lint for Go)
- **Security**: Automated vulnerability scanning (Bandit, gosec, Snyk)
- **Documentation**: All public APIs must have complete documentation
- **Performance**: Automated performance regression testing

### ✅ **Recent Quality Achievement: FLEXT Quality Documentation Standardization Complete**

**Status**: **Enterprise-Grade Documentation Standardization Completed** (2025-08-04)

- ✅ **100% Source Code Documentation**: All Python modules in flext-quality updated to enterprise standards
- ✅ **Comprehensive Architecture Documentation**: Domain, Application, and Infrastructure layers fully documented
- ✅ **Working Examples**: Practical usage examples with tested code samples
- ✅ **Professional English**: All documentation standardized to enterprise professional level
- ✅ **FLEXT Integration**: Complete ecosystem integration patterns and cross-references
- ✅ **Quality Governance**: Automated quality analysis and reporting service fully documented

**Impact**: FLEXT Quality now serves as the **centralized quality governance hub** for all 32+ FLEXT ecosystem projects with enterprise-grade documentation and integration patterns.

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

## Deployment

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

## Monitoring and Observability

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

- **Grafana**: <http://localhost:3000> (admin/admin)
- **Prometheus**: <http://localhost:9090>
- **Jaeger**: <http://localhost:16686>
- **Control Panel**: <http://localhost:8081/dashboard>

## Performance Benchmarks

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

## Troubleshooting

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

## Contributing

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

## Ecosystem Projects

FLEXT Control Panel orchestrates a comprehensive ecosystem of 32+ interconnected projects:

### Foundation Libraries

- **flext-core**: Shared patterns, DI container, result handling
- **flext-observability**: Monitoring, metrics, health checks

### Data Integration

- **Singer Taps** (5): Extract data from various sources
- **Singer Targets** (5): Load data to various destinations
- **DBT Projects** (4): Transform and model data
- **Infrastructure Libraries** (6): Database, LDAP, gRPC connectivity

### Application Services

- **flext-api**: REST API with FastAPI
- **flext-auth**: Authentication and authorization
- **flext-web**: Web interface and dashboard
- **flext-cli**: Command-line tools

## License

MIT License - see [LICENSE](LICENSE) for details.

## 📚 Complete Documentation & Ecosystem

### **Professional Documentation System**

FLEXT implements a **comprehensive documentation standard** across all 32 ecosystem projects with **100% docstring standardization** and enterprise-grade quality gates.

#### **Core Documentation Hub**

- **[CLAUDE.md](CLAUDE.md)** - Development guidance with architectural patterns and quality gates
- **[Documentation Hub](docs/NAVIGATION.md)** - Complete navigation system for all 32 projects
- **[Architecture Guide](docs/architecture/)** - Clean Architecture and DDD implementation
- **[API Documentation](docs/api/)** - OpenAPI specifications and integration patterns
- **[Development Standards](docs/standards/)** - Python module organization and PEP compliance

#### **Standardization Achievements**

- ✅ **Docstring Standardization Complete** - All Python modules follow enterprise patterns
- ✅ **Type Annotation Coverage: 95%+** - Comprehensive type safety across ecosystem
- ✅ **Cross-Reference Integration** - Unified navigation between all projects
- ✅ **Quality Gate Integration** - Automated validation in development workflows
- ✅ **Professional English Standard** - Consistent terminology and presentation

### **Enterprise Architecture Ecosystem**

The FLEXT ecosystem comprises **32 interconnected projects** implementing Clean Architecture, DDD, and CQRS patterns:

#### **Foundation Libraries (2 projects)**

- **[flext-core](flext-core/)** - FlextResult patterns, DI container, domain entities
- **[flext-observability](flext-observability/)** - Monitoring, metrics, distributed tracing

#### **Core Services (3 projects)**

- **[FlexCore](flexcore/)** - Go runtime container (port 8080) with plugin system
- **[FLEXT Service](cmd/flext/)** - Data platform service (port 8081) with Python bridge
- **[FLEXT Control Panel](./)** - Enterprise orchestration and management hub

#### **Application Services (5 projects)**

- **[flext-api](flext-api/)** - REST API foundation with FastAPI and enterprise patterns
- **[flext-auth](flext-auth/)** - Authentication with LDAP integration and security
- **[flext-web](flext-web/)** - Web interface with monitoring dashboards
- **[flext-cli](flext-cli/)** - Command-line tools with workspace management
- **[flext-quality](flext-quality/)** - Code quality analysis and enforcement

#### **Infrastructure Libraries (6 projects)**

- **[flext-db-oracle](flext-db-oracle/)** - **✅ Enterprise Production Ready** - Oracle database integration with 100% documentation standardization, 95%+ type coverage, Clean Architecture, and comprehensive plugin system
- **[flext-ldap](flext-ldap/)** - LDAP directory services and authentication
- **[flext-ldif](flext-ldif/)** - LDIF processing with validation and transformation
- **[flext-oracle-wms](flext-oracle-wms/)** - Warehouse Management System integration
- **[flext-grpc](flext-grpc/)** - High-performance gRPC communication
- **[flext-meltano](flext-meltano/)** - Singer/Meltano/DBT orchestration platform

#### **Singer Data Integration (15 projects)**

- **Extractors (5 taps)**: LDAP, LDIF, Oracle, Oracle OIC, Oracle WMS data sources
- **Loaders (5 targets)**: LDAP, LDIF, Oracle, Oracle OIC, Oracle WMS destinations
- **Transformers (4 DBT)**: Business logic and data modeling for each domain
- **Extensions (1)**: Oracle OIC utilities and custom adapters

#### **Enterprise Implementations (2 projects)**

- **[algar-oud-mig](algar-oud-mig/)** - **✅ Enterprise Documentation Complete** - ALGAR Oracle Unified Directory migration with 100% docstring standardization, comprehensive Clean Architecture + DDD implementation, enterprise-grade README.md files for all layers, and complete integration with FLEXT ecosystem patterns
- **[gruponos-meltano-native](gruponos-meltano-native/)** - GrupoNos-specific orchestration

### **Documentation Quality Standards**

#### **Enterprise Documentation Features**

- 🎯 **Complete Type Safety** - 95%+ type annotation coverage with MyPy validation
- 📚 **Comprehensive Docstrings** - Every module, class, and method fully documented
- 🔗 **Integrated Navigation** - Cross-project linking and ecosystem awareness
- ⚡ **Quality Gate Integration** - Automated validation in CI/CD pipelines
- 🏗️ **Architectural Alignment** - Clear separation of concerns and domain boundaries

## 🆘 Support

### **Documentation Resources**

- **[Complete Ecosystem Index](docs/ECOSYSTEM_INDEX.md)** - Navigation guide for all 32 projects
- **[Documentation Standard](docs/DOCUMENTATION_STANDARD.md)** - Template and guidelines
- **[Implementation Plan](docs/IMPLEMENTATION_PLAN.md)** - Standardization progress and timeline

### **Getting Help**

- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext/issues) with detailed reproduction steps
- **Discussions**: [GitHub Discussions](https://github.com/flext-sh/flext/discussions) for questions
- **Security**: Report security issues privately to maintainers
- **Documentation**: Each project has comprehensive documentation following unified standards

For technical support, create an issue in the relevant project repository with detailed reproduction steps and system information.
