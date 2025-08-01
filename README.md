# FLEXT - Enterprise Data Integration Platform

Enterprise-grade distributed data integration platform built with Go 1.24+ and Python 3.13+, implementing Clean Architecture, Domain-Driven Design (DDD), and CQRS patterns.

## Architecture Overview

The FLEXT ecosystem consists of 32 interconnected projects organized into distinct architectural layers:

- **Core Services**: FlexCore (Go runtime container) + FLEXT Service (Go/Python data processing)
- **Foundation Libraries**: flext-core (Python), flext-observability
- **Infrastructure Libraries**: Database connectivity, LDAP/LDIF processing, gRPC communication
- **Application Services**: REST APIs, authentication, web interface, CLI tools
- **Singer Ecosystem**: 15 data taps, targets, and DBT transformers
- **Legacy Integration**: client-a migration tools, client-b-specific implementations

## Technology Stack

- **Go 1.24+**: High-performance services with Clean Architecture + DDD + CQRS + Event Sourcing
- **Python 3.13+**: Data processing with Singer SDK, Meltano 3.8.0, and DBT
- **FastAPI**: REST API framework with automatic OpenAPI documentation
- **PostgreSQL**: Application database (port 5433)
- **Redis**: Caching and session storage (port 6380)
- **Docker**: Containerization and deployment infrastructure

## Quick Start

### Prerequisites

- Go 1.24+
- Python 3.13+
- Docker and Docker Compose
- Make utility

### Development Environment Setup

```bash
# Complete workspace setup
make setup                    # Install tools, dependencies, and pre-commit hooks
make workspace-install        # Install all project dependencies
make dev-setup               # Full development environment setup

# Start core services
make docker-up               # Start PostgreSQL, Redis, and core services

# Verify services
curl http://localhost:8080/health  # FlexCore health check
curl http://localhost:8081/health  # FLEXT service health check
```

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 FLEXT Ecosystem                             │
├─────────────────────────────────────────────────────────────┤
│  FlexCore (Go)              │  FLEXT Service (Go/Python)   │
│  Port: 8080                 │  Port: 8081                   │
│  ├─ Plugin System           │  ├─ Meltano Integration       │
│  ├─ Event Sourcing          │  ├─ Singer Taps/Targets      │
│  ├─ CQRS Implementation     │  ├─ DBT Transformations      │
│  └─ Health Monitoring       │  └─ Python Bridge            │
└─────────────────────────────────────────────────────────────┘
```

## Development Commands

### Workspace-Level Operations

```bash
# Quality gates (run before committing)
make validate                # Complete validation (lint + type + security + test)
make check                   # Quick health check (lint + type)
make lint-all                # Lint all Python projects
make type-check-all          # MyPy type checking on all projects
make test-all                # Run tests on all projects

# Build and deployment
make build-all               # Build all projects (Python + Go)
make build-python            # Build Python projects only
make build-go                # Build Go projects only

# Docker operations
make docker-up               # Start full platform with dependencies
make docker-down             # Stop all services
make docker-logs             # View aggregated logs
```

### Individual Project Commands

```bash
# Navigate to any project directory and use:
make check                   # Lint + type check + test
make test                    # Run pytest with coverage
make lint                    # Run ruff linting
make type-check              # Run mypy type checking
make format                  # Format code
make build                   # Build project
```

## Project Structure

### Core Services (2 projects)

- **FlexCore** (`flexcore/`): Go runtime container service with plugin system
- **FLEXT Service** (`cmd/flext/`): Main data platform service with Python bridge

### Foundation Libraries (2 projects)

- **flext-core**: Base patterns, dependency injection, result handling
- **flext-observability**: Monitoring, metrics, tracing, health checks

### Infrastructure Libraries (6 projects)

- **flext-db-oracle**: Oracle database connectivity and operations
- **flext-ldap**: LDAP server connectivity and directory operations
- **flext-ldif**: LDIF file processing and validation
- **flext-oracle-wms**: Oracle WMS API connectivity and data models
- **flext-grpc**: gRPC communication protocols
- **flext-meltano**: Singer/Meltano/DBT orchestration platform

### Application Services (5 projects)

- **flext-api**: REST API services with FastAPI
- **flext-auth**: Authentication and authorization services
- **flext-web**: Web interface and dashboard
- **flext-quality**: Code quality analysis and reporting
- **flext-cli**: Command-line interface tools

### Singer Ecosystem (15 projects)

- **Taps (5)**: flext-tap-ldap, flext-tap-ldif, flext-tap-oracle, flext-tap-oracle-oic, flext-tap-oracle-wms
- **Targets (5)**: flext-target-ldap, flext-target-ldif, flext-target-oracle, flext-target-oracle-oic, flext-target-oracle-wms
- **DBT Projects (4)**: flext-dbt-ldap, flext-dbt-ldif, flext-dbt-oracle, flext-dbt-oracle-wms
- **Extensions (1)**: flext-oracle-oic-ext

### Legacy/Specialized (2 projects)

- **client-a-oud-mig**: client-a Oracle Unified Directory migration
- **client-b-meltano-native**: client-b-specific Meltano implementation

## Configuration Management

### Environment Variables

```bash
# Core service configuration
export FLEXT_MODE="server"                    # Operating mode
export FLEXT_SERVER_PORT="8081"              # FLEXT service port
export FLEXCORE_PORT="8080"                  # FlexCore port
export FLEXT_DATABASE_URL="postgresql://localhost:5433/flext"
export FLEXT_REDIS_URL="redis://localhost:6380"

# Observability
export OTEL_SERVICE_NAME="flext-platform"
export PROMETHEUS_ENDPOINT="http://localhost:9090"
export JAEGER_COLLECTOR_ENDPOINT="http://localhost:14268/api/traces"
```

### Docker Services

- **PostgreSQL**: localhost:5433 (application database)
- **Redis**: localhost:6380 (caching and session storage)
- **Prometheus**: localhost:9090 (metrics collection)
- **Grafana**: localhost:3000 (monitoring dashboards)
- **Jaeger**: localhost:16686 (distributed tracing)

## Quality Standards

### Zero Tolerance Quality Gates

- **Coverage**: Minimum 90% test coverage for all projects
- **Type Safety**: Strict MyPy configuration (Python) and Go type safety
- **Linting**: Comprehensive rule sets (Ruff for Python, golangci-lint for Go)
- **Security**: Automated security scanning with Bandit and gosec
- **Pre-commit**: Automated quality checks prevent low-quality commits

### Testing Strategy

- **Unit Tests**: Comprehensive test suites for all business logic
- **Integration Tests**: Database and service integration testing
- **E2E Tests**: Full pipeline testing with Docker
- **Performance Tests**: Benchmark critical data processing paths

## Deployment

### Production Deployment

```bash
# Build production images
make docker-build-prod

# Deploy with orchestration
docker-compose -f docker-compose.prod.yml up -d

# Health verification
make health-check-all
```

### Kubernetes Support

The platform includes Kubernetes manifests for production deployment with:

- Horizontal pod autoscaling
- Service mesh integration
- Persistent volume management
- ConfigMap and Secret management

## Monitoring and Observability

### Built-in Monitoring

- **Health Checks**: All services expose `/health` endpoints
- **Metrics**: Prometheus-compatible metrics collection
- **Tracing**: OpenTelemetry distributed tracing
- **Logging**: Structured JSON logging with correlation IDs

### Performance Monitoring

```bash
# Monitor system performance
make metrics-check              # Check metrics collection
make trace-analysis            # Analyze distributed traces
make performance-benchmark     # Run performance benchmarks
```

## Common Workflows

### Adding New Services

1. Follow Clean Architecture patterns from flext-core
2. Implement dependency injection with FlextContainer
3. Add comprehensive test coverage (90% minimum)
4. Include observability with flext-observability
5. Register with service discovery mechanisms

### Data Pipeline Development

1. Create Singer tap for data extraction
2. Implement DBT models for transformations
3. Configure target for data loading
4. Register pipeline with Meltano orchestration
5. Add monitoring and alerting rules

## Troubleshooting

### Common Issues

```bash
# Service connectivity issues
make diagnose                  # Complete system diagnostics
make service-status           # Check all service statuses

# Database connection problems
make db-health-check          # Verify database connectivity
make db-reset                 # Reset database (development only)

# Performance issues
make performance-analysis     # Analyze system performance
make resource-usage          # Check resource utilization
```

### Debug Mode

```bash
# Enable debug logging
export FLEXT_LOG_LEVEL=debug

# Start services in debug mode
make debug-all

# Generate diagnostic reports
make debug-report
```

## Contributing

1. Fork the repository
2. Create a feature branch following naming conventions
3. Implement changes with comprehensive tests
4. Run quality gates: `make validate`
5. Submit pull request with detailed description

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: Individual project README files contain specific implementation details
- **Architecture**: See [CLAUDE.md](CLAUDE.md) for development guidance
- **Issues**: Use GitHub Issues for bug reports and feature requests
