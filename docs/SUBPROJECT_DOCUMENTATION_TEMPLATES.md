# FLEXT Ecosystem - Subproject Documentation Templates

**Version 2.0.0** | **Scope**: All 33 FLEXT Projects | **Standard**: Enterprise Documentation

Comprehensive documentation templates for standardizing documentation across all FLEXT ecosystem projects with enterprise-grade consistency, professional English, and complete integration alignment.

---

## 🎯 TEMPLATE OVERVIEW

### **Purpose**

Provides standardized documentation templates for ensuring consistent, professional documentation across all 33 FLEXT ecosystem projects. Templates cover all project types with appropriate customization for Python, Go, Singer/DBT, and specialized projects.

### **Template Categories**

- **Foundation Projects**: flext-core, flext-observability
- **Core Services**: FlexCore (Go), FLEXT Service (Go/Python), Control Panel (Python)
- **Application Services**: flext-api, flext-auth, flext-web, flext-cli, flext-quality
- **Infrastructure**: flext-db-oracle, flext-ldap, flext-ldif, flext-oracle-wms, flext-grpc, flext-meltano
- **Singer Ecosystem**: 5 Taps, 5 Targets, 4 DBT projects, 1 Extension
- **Specialized**: client-a-oud-mig, client-b-meltano-native

---

## 📋 TEMPLATE 1: Python APPLICATION SERVICES

### **README.md Template**

````markdown
# [Project Name] - [Brief Description]

**Version [X.Y.Z]** | **Type: [Service Type]** | **Integration: FLEXT Ecosystem**

[Comprehensive description of the project purpose and capabilities within the FLEXT ecosystem]

## 📋 Project Overview

### **Purpose**

[Clear statement of what this project does and why it exists in the FLEXT ecosystem]

### **Architecture Position**

- **Layer**: [Application/Infrastructure/Domain] Layer
- **Dependencies**: [List key dependencies like flext-core, etc.]
- **Consumers**: [Who uses this service]
- **Ecosystem Role**: [Role in the broader FLEXT ecosystem]

## 🎯 Key Features

### **Core Capabilities**

- **[Feature 1]**: [Description with technical details]
- **[Feature 2]**: [Description with technical details]
- **[Feature 3]**: [Description with technical details]

### **Technical Specifications**

- **Python Version**: 3.13+
- **Framework**: [FastAPI/Flask/etc.]
- **Architecture**: Clean Architecture + DDD + CQRS
- **Error Handling**: FlextResult patterns
- **Testing**: pytest with 90%+ coverage

## 🚀 Quick Start

### **Installation**

```bash
# Install dependencies
poetry install

# Install development dependencies
poetry install --with dev

# Setup pre-commit hooks
pre-commit install
```
````

### **Basic Usage**

```python
from [project_name] import [MainClass]
from flext_core import FlextResult

# Basic usage example
service = [MainClass]()
result = service.[main_method]()

if result.success:
    print(f"Success: {result.value}")
else:
    print(f"Error: {result.error}")
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Required environment variables
[PROJECT]_HOST=localhost
[PROJECT]_PORT=8080
[PROJECT]_DATABASE_URL=postgresql://localhost:5432/[project]

# Optional environment variables
[PROJECT]_LOG_LEVEL=INFO
[PROJECT]_DEBUG=false
```

### **Configuration Files**

- **config/development.YAML**: Development environment configuration
- **config/production.YAML**: Production environment configuration
- **config/testing.YAML**: Testing environment configuration

## 🧪 Development

### **Development Commands**

```bash
# Quality checks
make check                 # Lint + type check + test
make lint                  # Run ruff linting
make type-check           # Run mypy type checking
make test                 # Run pytest with coverage
make format               # Format code with ruff

# Build and deployment
make build                # Build project
make docker-build         # Build Docker image
make docker-run           # Run in Docker

# Database operations (if applicable)
make db-migrate           # Run database migrations
make db-seed              # Seed database with test data
```

### **Testing Strategy**

- **Unit Tests**: 90%+ coverage with comprehensive mocking
- **Integration Tests**: Service integration and database testing
- **E2E Tests**: Complete workflow validation
- **Performance Tests**: Load testing and benchmarking

## 🔗 Integration

### **FLEXT Ecosystem Integration**

- **flext-core**: [Describe integration patterns]
- **flext-observability**: [Describe monitoring integration]
- **Other Services**: [List and describe service dependencies]

### **External Integrations**

- **[External Service 1]**: [Description of integration]
- **[External Service 2]**: [Description of integration]

## 📚 API Documentation

### **REST Endpoints** (if applicable)

```
GET    /health                    # Health check
GET    /api/v1/[resource]        # List resources
POST   /api/v1/[resource]        # Create resource
GET    /api/v1/[resource]/{id}   # Get resource by ID
PUT    /api/v1/[resource]/{id}   # Update resource
DELETE /api/v1/[resource]/{id}   # Delete resource
```

### **CLI Commands** (if applicable)

```bash
[project-name] --help             # Show help
[project-name] [command] --help   # Show command help
[project-name] status             # Show service status
```

## 🚀 Deployment

### **Docker Deployment**

```bash
# Build image
docker build -t [project-name]:latest .

# Run container
docker run -p 8080:8080 -e [PROJECT]_DATABASE_URL=... [project-name]:latest
```

### **Production Considerations**

- **Scaling**: [Scaling recommendations]
- **Monitoring**: [Monitoring setup]
- **Security**: [Security considerations]
- **Backup**: [Backup strategies]

## 📊 Monitoring

### **Health Checks**

- **Endpoint**: `GET /health`
- **Dependencies**: [List health check dependencies]
- **SLA**: [Service level agreements]

### **Metrics**

- **Performance**: Response time, throughput, error rate
- **Business**: [Business-specific metrics]
- **Infrastructure**: CPU, memory, disk usage

## 🔧 Troubleshooting

### **Common Issues**

1. **[Issue 1]**: [Description and solution]
2. **[Issue 2]**: [Description and solution]
3. **[Issue 3]**: [Description and solution]

### **Debugging**

```bash
# Enable debug logging
export [PROJECT]_LOG_LEVEL=DEBUG

# Check service status
[project-name] status

# View logs
docker logs [container-name]
```

## 📚 Documentation

- **[API Documentation](docs/api.md)** - Complete API reference
- **[Architecture](docs/architecture.md)** - System architecture and design
- **[Development Guide](docs/development.md)** - Development setup and guidelines

## 🤝 Contributing

See the main [FLEXT Contributing Guide](../CONTRIBUTING.md) for development standards and procedures.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**FLEXT Ecosystem**: [Project Name] | **Documentation**: Enterprise Standard | **Quality**: Production Ready

````

### **CLAUDE.md Template**

```markdown
# CLAUDE.md - [Project Name] Development Guide

**Hierarchy**: PROJECT - Project-specific development guidance
**Reference**: `/home/user/CLAUDE.md` → Universal development methodology
**Last Updated**: [YYYY-MM-DD]
**Project Type**: [Python Application Service/Infrastructure/etc.]

---

## 🎯 PROJECT OVERVIEW

### **Project Identity**
- **Name**: [Project Name]
- **Purpose**: [Clear purpose within FLEXT ecosystem]
- **Technology Stack**: Python 3.13+, [Framework], [Other key technologies]
- **Architecture**: Clean Architecture + DDD + CQRS patterns
- **Ecosystem Position**: [Position in 33-project ecosystem]

### **Development Priorities**
1. **Enterprise Standards**: 100% professional documentation and code quality
2. **FLEXT Integration**: Deep integration with flext-core and ecosystem patterns
3. **Performance**: High-performance, scalable service implementation
4. **Reliability**: Comprehensive error handling and monitoring integration

---

## 🏗️ ARCHITECTURE STANDARDS

### **Clean Architecture Implementation**

````

[Project Name]/
├── src/[project_name]/
│ ├── domain/ # Domain layer (entities, value objects, domain services)
│ │ ├── entities/ # Domain entities
│ │ ├── value_objects/ # Value objects
│ │ └── services/ # Domain services
│ ├── application/ # Application layer (use cases, handlers)
│ │ ├── handlers/ # CQRS command/query handlers
│ │ ├── services/ # Application services
│ │ └── dto/ # Data Transfer Objects
│ ├── infrastructure/ # Infrastructure layer (repositories, external services)
│ │ ├── repositories/ # Repository implementations
│ │ ├── external/ # External service integrations
│ │ └── config/ # Configuration management
│ └── interfaces/ # Interface layer (API, CLI, etc.)
├── api/ # REST API interfaces
└── cli/ # CLI interfaces

````

### **Required Patterns**
- **FlextResult**: All service methods must return FlextResult<T>
- **Dependency Injection**: Use FlextContainer for all dependencies
- **CQRS**: Separate command and query operations
- **Domain Events**: Use domain events for cross-boundary communication
- **Repository Pattern**: Abstract all data access through repositories

---

## 🔧 DEVELOPMENT STANDARDS

### **Code Quality Requirements**
- **Type Coverage**: 95%+ type annotation coverage
- **Test Coverage**: 90%+ unit test coverage, 80%+ integration test coverage
- **Documentation**: Enterprise-grade docstrings for all public interfaces
- **Error Handling**: Comprehensive error handling with FlextResult patterns
- **Performance**: All operations must meet performance benchmarks

### **Required Tools and Validation**
```bash
# Before committing (MANDATORY)
make check                    # Complete validation pipeline
make lint                     # Ruff linting (must pass)
make type-check              # MyPy type checking (must pass)
make test                    # Test suite (must pass with 90%+ coverage)
make security                # Security scanning (must pass)
````

### **Pre-commit Requirements**

- **Ruff**: Code formatting and linting
- **MyPy**: Type checking in strict mode
- **Tests**: Unit tests must pass
- **Security**: Bandit security scanning
- **Import sorting**: isort for import organization

---

## 🔗 FLEXT ECOSYSTEM INTEGRATION

### **Required Dependencies**

```toml
[tool.poetry.dependencies]
python = "^3.13"
flext-core = "^2.0.0"           # MANDATORY: Core patterns and utilities
flext-observability = "^2.0.0"  # MANDATORY: Monitoring and logging
# Project-specific dependencies...
```

### **Integration Patterns**

- **Error Handling**: Use FlextResult for all service boundaries
- **Logging**: Use flext-observability structured logging
- **Configuration**: Use flext-core configuration patterns
- **Monitoring**: Integrate with ecosystem health checks
- **Events**: Use domain events for inter-service communication

### **Service Discovery Integration**

- **Health Endpoint**: Implement `/health` endpoint for monitoring
- **Metrics Endpoint**: Implement `/metrics` for Prometheus integration
- **Service Registration**: Register with service discovery if applicable

---

## 🧪 TESTING REQUIREMENTS

### **Testing Architecture**

```
tests/
├── unit/                    # Unit tests (90%+ coverage required)
│   ├── domain/             # Domain layer tests
│   ├── application/        # Application layer tests
│   └── infrastructure/     # Infrastructure layer tests (with mocks)
├── integration/            # Integration tests
│   ├── api/               # API integration tests
│   ├── database/          # Database integration tests
│   └── external/          # External service integration tests
├── e2e/                   # End-to-end tests
│   └── workflows/         # Complete workflow tests
└── performance/           # Performance tests
    └── benchmarks/        # Performance benchmarks
```

### **Testing Standards**

- **Unit Tests**: Fast, isolated, comprehensive mocking
- **Integration Tests**: Real database/service integration
- **E2E Tests**: Complete user journey validation
- **Performance Tests**: Load testing and benchmarking

---

## 🚀 DEPLOYMENT STANDARDS

### **Docker Configuration**

```dockerfile
# Multi-stage build (required)
FROM python:3.13-slim as builder
# Build stage...

FROM python:3.13-slim as runtime
# Runtime stage with minimal dependencies
```

### **Environment Configuration**

- **Development**: Local development with hot reloading
- **Testing**: Isolated testing environment
- **Staging**: Production-like staging environment
- **Production**: High-availability production configuration

### **Monitoring Integration**

- **Health Checks**: Comprehensive health check implementation
- **Metrics**: Prometheus metrics for all key operations
- **Logging**: Structured logging with correlation IDs
- **Alerting**: Integration with ecosystem alerting systems

---

## 📊 PERFORMANCE REQUIREMENTS

### **Performance Benchmarks**

- **API Response Time**: < 100ms for simple operations, < 500ms for complex
- **Throughput**: Minimum [X] requests/second under normal load
- **Memory Usage**: Maximum [X] MB under normal operation
- **CPU Usage**: < 70% under normal load

### **Scalability Requirements**

- **Horizontal Scaling**: Support for multiple instances
- **Database Scaling**: Efficient database query patterns
- **Caching**: Implement caching for frequently accessed data
- **Async Processing**: Use async patterns for I/O operations

---

## 🔒 SECURITY REQUIREMENTS

### **Security Standards**

- **Input Validation**: Comprehensive input validation and sanitization
- **Authentication**: Integration with flext-auth if applicable
- **Authorization**: Role-based access control implementation
- **Data Protection**: Encryption of sensitive data at rest and in transit
- **Audit Logging**: Comprehensive audit trails for security events

### **Security Scanning**

```bash
# Required security checks
bandit -r src/                # Security vulnerability scanning
safety check                  # Dependency vulnerability checking
pip-audit                     # Additional dependency audit
```

---

## 📚 DOCUMENTATION REQUIREMENTS

### **Required Documentation**

- **README.md**: Complete project overview and setup instructions
- **API Documentation**: OpenAPI/Swagger specification for REST APIs
- **Architecture Documentation**: System design and component interaction
- **Deployment Guide**: Production deployment instructions
- **Troubleshooting Guide**: Common issues and solutions

### **Docstring Standards**

```python
"""
[Function/Class Name] - Brief Description

Comprehensive description following FLEXT enterprise standards with
purpose, integration patterns, and usage examples.

Args:
    param_name (Type): Description with constraints and defaults

Returns:
    FlextResult[ReturnType]: Success with data or failure with error context

Raises:
    SpecificException: When this exception occurs

Example:
    Basic usage with error handling:

    >>> from [project] import [Function]
    >>> result = [Function](param="value")
    >>> if result.success:
    ...     print(f"Success: {result.value}")
    ... else:
    ...     print(f"Error: {result.error}")

Integration:
    - Built on flext-core FlextResult patterns
    - Integrates with flext-observability for monitoring
    - Coordinates with [other ecosystem services]
"""
```

---

## 🚨 CRITICAL REQUIREMENTS

### **NEVER Do**

- ❌ Modify flext-core interfaces without ecosystem-wide coordination
- ❌ Break FlextResult patterns in service boundaries
- ❌ Bypass type checking or reduce type coverage
- ❌ Ignore security scanning failures
- ❌ Deploy without comprehensive testing

### **ALWAYS Do**

- ✅ Use FlextResult for all service boundaries
- ✅ Implement comprehensive error handling
- ✅ Follow Clean Architecture patterns strictly
- ✅ Maintain 90%+ test coverage
- ✅ Use enterprise-grade documentation standards

---

## 🔄 MAINTENANCE PROCEDURES

### **Regular Maintenance**

- **Weekly**: Dependency security updates
- **Monthly**: Performance benchmarking and optimization
- **Quarterly**: Architecture review and refactoring

### **Incident Response**

- **Critical Issues**: Follow enterprise incident response procedures
- **Performance Issues**: Use integrated monitoring for diagnosis
- **Security Issues**: Immediate escalation and patching procedures

---

**Authority**: Project-level development guidance within FLEXT ecosystem  
**Scope**: [Project Name] development, testing, and deployment  
**Integration**: Full alignment with FLEXT enterprise standards and ecosystem patterns

````

---

## 📋 TEMPLATE 2: GO SERVICES (FlexCore, FLEXT Service)

### **README.md Template**

```markdown
# [Go Service Name] - [Brief Description]

**Version [X.Y.Z]** | **Language: Go 1.24+** | **Integration: FLEXT Core Services**

[Comprehensive description of the Go service purpose and capabilities within the FLEXT ecosystem]

## 📋 Service Overview

### **Purpose**
[Clear statement of what this Go service does and its role in the FLEXT ecosystem]

### **Architecture Position**
- **Layer**: Core Services (Runtime/Infrastructure)
- **Language**: Go 1.24+ with enterprise patterns
- **Architecture**: Clean Architecture + DDD + CQRS + Event Sourcing
- **Dependencies**: [List key dependencies]
- **Consumers**: [List consuming services and interfaces]
- **Ports**: [Service ports and protocols]

## 🎯 Key Capabilities

### **Core Features**
- **[Feature 1]**: [High-performance Go implementation details]
- **[Feature 2]**: [Concurrent processing capabilities]
- **[Feature 3]**: [Integration patterns with Python services]

### **Technical Specifications**
- **Go Version**: 1.24+
- **Concurrency**: Goroutines with structured concurrency patterns
- **Memory Management**: Efficient memory allocation and GC optimization
- **Network**: gRPC and HTTP/REST API support
- **Integration**: Python bridge for FLEXT ecosystem coordination

## 🚀 Quick Start

### **Build and Run**

```bash
# Build the service
make build

# Run in development mode
make run-dev

# Run tests
make test

# Run with race detection
make test-race
````

### **Docker Deployment**

```bash
# Build Docker image
make docker-build

# Run in Docker
make docker-run

# Docker Compose (with dependencies)
docker-compose up -d
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Service configuration
[SERVICE]_HOST=0.0.0.0
[SERVICE]_PORT=8080
[SERVICE]_LOG_LEVEL=info

# Database configuration (if applicable)
[SERVICE]_DB_HOST=localhost
[SERVICE]_DB_PORT=5432

# Integration configuration
[SERVICE]_PYTHON_BRIDGE_HOST=localhost
[SERVICE]_PYTHON_BRIDGE_PORT=8081
```

### **Configuration Files**

- **config/development.YAML**: Development environment
- **config/production.YAML**: Production environment
- **config/testing.YAML**: Testing environment

## 🏗️ Architecture

### **Clean Architecture Structure**

```
cmd/[service]/              # Main application
├── main.go                # Service entry point
├── config.go              # Configuration management
└── server.go              # Server setup and lifecycle

internal/                   # Internal packages (private to service)
├── domain/                # Domain layer
│   ├── entities/          # Domain entities
│   ├── valueobjects/      # Value objects
│   └── services/          # Domain services
├── application/           # Application layer
│   ├── commands/          # CQRS commands
│   ├── queries/           # CQRS queries
│   ├── handlers/          # Command/query handlers
│   └── services/          # Application services
├── infrastructure/        # Infrastructure layer
│   ├── repositories/      # Repository implementations
│   ├── external/          # External service clients
│   └── persistence/       # Database persistence
└── interfaces/            # Interface layer
    ├── grpc/              # gRPC service implementations
    ├── http/              # HTTP/REST handlers
    └── events/            # Event handlers

pkg/                       # Public packages (can be imported)
├── client/                # Service clients
├── types/                 # Shared types
└── utils/                 # Utility functions
```

### **Integration Patterns**

- **Python Bridge**: gRPC/HTTP bridge for Python service integration
- **Event Sourcing**: Event store for state management and audit trail
- **CQRS**: Separate read/write models for performance optimization
- **Plugin Architecture**: Hot-pluggable components with proxy adapters

## 🧪 Testing

### **Testing Strategy**

```bash
# Unit tests
go test ./...

# Integration tests
go test -tags=integration ./...

# End-to-end tests
go test -tags=e2e ./...

# Performance tests
go test -bench=. ./...

# Race condition testing
go test -race ./...
```

### **Testing Structure**

```
tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
├── e2e/                   # End-to-end tests
├── performance/           # Performance benchmarks
└── fixtures/              # Test fixtures and data
```

## 🔗 Integration

### **FLEXT Ecosystem Integration**

- **Python Services**: [Describe Python bridge patterns]
- **Database Integration**: [Database connectivity patterns]
- **Monitoring**: [Integration with observability systems]
- **Service Discovery**: [Service registration and discovery]

### **API Interfaces**

#### **gRPC Services**

```protobuf
service [ServiceName] {
    rpc [Method1](Request1) returns (Response1);
    rpc [Method2](Request2) returns (Response2);
}
```

#### **REST Endpoints**

```
GET    /health                    # Health check
GET    /metrics                   # Prometheus metrics
GET    /api/v1/[resource]        # List resources
POST   /api/v1/[resource]        # Create resource
```

## 🚀 Deployment

### **Production Deployment**

```bash
# Build optimized binary
CGO_ENABLED=0 GOOS=linux go build -ldflags="-w -s" -o bin/[service] cmd/[service]/main.go

# Run with production configuration
./bin/[service] -config=config/production.yaml
```

### **Container Deployment**

```dockerfile
# Multi-stage build for minimal production image
FROM golang:1.24-alpine AS builder
# Build stage...

FROM alpine:latest AS runtime
# Minimal runtime with security updates
```

## 📊 Performance

### **Performance Characteristics**

- **Latency**: < 1ms for simple operations
- **Throughput**: [X] requests/second under load
- **Memory**: Efficient memory usage with Go GC optimization
- **Concurrency**: High concurrency with goroutine pools

### **Monitoring and Metrics**

- **Prometheus Metrics**: Performance and business metrics
- **Health Checks**: Comprehensive health validation
- **Distributed Tracing**: Integration with Jaeger/Zipkin
- **Profiling**: Go pprof integration for performance analysis

## 🔧 Development

### **Development Commands**

```bash
# Development workflow
make dev-setup              # Setup development environment
make build                  # Build the service
make test                   # Run test suite
make lint                   # Run linting (golangci-lint)
make format                 # Format code (gofmt, goimports)

# Quality checks
make check                  # Complete validation pipeline
make security               # Security scanning (gosec)
make dependency-check       # Dependency vulnerability check
```

### **Code Quality Requirements**

- **Test Coverage**: 90%+ coverage for critical paths
- **Linting**: golangci-lint with comprehensive rule set
- **Security**: gosec security scanning
- **Documentation**: Comprehensive godoc documentation

## 🔒 Security

### **Security Implementation**

- **Input Validation**: Comprehensive input validation and sanitization
- **Authentication**: Integration with authentication systems
- **Authorization**: Role-based access control
- **TLS**: Mandatory TLS for all network communication
- **Secrets Management**: Secure secret handling and rotation

## 📚 Documentation

- **[API Documentation](docs/api.md)** - gRPC and REST API reference
- **[Architecture Guide](docs/architecture.md)** - Service architecture and design
- **[Integration Guide](docs/integration.md)** - Integration patterns with ecosystem
- **[Performance Guide](docs/performance.md)** - Performance optimization and tuning

---

**FLEXT Ecosystem**: [Service Name] | **Technology**: Go 1.24+ | **Quality**: Enterprise Grade

````

---

## 📋 TEMPLATE 3: SINGER ECOSYSTEM PROJECTS

### **Singer Tap Template (README.md)**

```markdown
# [Tap Name] - Singer Tap for [Data Source]

**Version [X.Y.Z]** | **Type: Singer Tap** | **Integration: FLEXT Data Pipeline**

Singer-compliant tap for extracting data from [Data Source] with enterprise-grade reliability, performance optimization, and comprehensive data validation for the FLEXT ecosystem.

## 📋 Tap Overview

### **Purpose**
Extracts data from [Data Source] following Singer specification with FLEXT ecosystem integration for reliable, scalable data pipeline operations.

### **Data Source Details**
- **Source Type**: [Database/API/File System/etc.]
- **Connection Method**: [JDBC/REST API/Direct Access/etc.]
- **Authentication**: [Auth methods supported]
- **Data Types**: [Types of data extracted]
- **Update Methods**: [Full/Incremental/CDC/etc.]

## 🎯 Key Features

### **Core Capabilities**
- **[Feature 1]**: [Singer-compliant data extraction]
- **[Feature 2]**: [Incremental replication with bookmarking]
- **[Feature 3]**: [Schema discovery and validation]
- **[Feature 4]**: [Performance optimization for large datasets]

### **FLEXT Integration**
- **Error Handling**: FlextResult patterns for robust error management
- **Monitoring**: Integration with flext-observability
- **Configuration**: FLEXT configuration management patterns
- **Quality**: Enterprise-grade data validation and testing

## 🚀 Quick Start

### **Installation**

```bash
# Install the tap
pip install [tap-name]

# Or with Poetry
poetry add [tap-name]
````

### **Configuration**

```yaml
# config.json
{
  "host": "[source-host]",
  "port": [port],
  "username": "[username]",
  "password": "[password]",
  "database": "[database-name]",
  "tables": ["table1", "table2"],
  "start_date": "2025-01-01T00:00:00Z",
}
```

### **Basic Usage**

```bash
# Discover schema
[tap-name] --config config.json --discover > catalog.json

# Extract data
[tap-name] --config config.json --catalog catalog.json
```

## 🔧 Configuration

### **Required Configuration**

- **host**: [Description]
- **port**: [Description]
- **username**: [Description]
- **password**: [Description]
- **database**: [Description]

### **Optional Configuration**

- **tables**: [Description with defaults]
- **start_date**: [Description of incremental replication]
- **batch_size**: [Performance tuning parameter]

### **Advanced Configuration**

```json
{
  "connection_pool_size": 10,
  "query_timeout": 300,
  "incremental_strategy": "replication_key",
  "replication_keys": {
    "table1": "updated_at",
    "table2": "modified_date"
  }
}
```

## 📊 Schema Discovery

### **Automatic Discovery**

The tap automatically discovers:

- **Tables**: All accessible tables in the data source
- **Columns**: Column names, types, and constraints
- **Primary Keys**: Automatic primary key detection
- **Replication Keys**: Timestamp columns for incremental replication

### **Schema Customization**

```json
{
  "streams": [
    {
      "tap_stream_id": "table_name",
      "schema": {
        "type": "object",
        "properties": {
          "column1": { "type": "string" },
          "column2": { "type": "integer" }
        }
      },
      "metadata": {
        "inclusion": "selected",
        "replication-method": "INCREMENTAL",
        "replication-key": "updated_at"
      }
    }
  ]
}
```

## 🔄 Replication Methods

### **Full Table Replication**

- **Use Case**: Small tables, complete refresh required
- **Performance**: [Performance characteristics]
- **Configuration**: Set `replication-method` to `FULL_TABLE`

### **Incremental Replication**

- **Use Case**: Large tables with timestamp columns
- **Performance**: [Performance characteristics]
- **Configuration**: Set `replication-method` to `INCREMENTAL`

### **Change Data Capture** (if supported)

- **Use Case**: Real-time data synchronization
- **Performance**: [Performance characteristics]
- **Configuration**: Set `replication-method` to `LOG_BASED`

## 🧪 Testing

### **Data Validation**

```bash
# Test connection
[tap-name] --config config.json --test-connection

# Validate schema
[tap-name] --config config.json --validate-schema

# Test data extraction
[tap-name] --config config.json --test-extraction --limit 100
```

### **Performance Testing**

```bash
# Benchmark extraction performance
[tap-name] --config config.json --benchmark --table table_name

# Test large dataset handling
[tap-name] --config config.json --stress-test
```

## 🔗 Meltano Integration

### **Meltano Configuration**

```yaml
plugins:
  extractors:
    - name: [tap-name]
      namespace: [tap_namespace]
      pip_url: [tap-name]
      settings:
        - name: host
          kind: string
        - name: port
          kind: integer
        - name: username
          kind: string
        - name: password
          kind: password
      select:
        - "table1.*"
        - "table2.column1"
        - "table2.column2"
```

### **Pipeline Example**

```bash
# Run with Meltano
meltano run [tap-name] [target-name]

# Schedule execution
meltano schedule [tap-name] [schedule-name] --interval @daily
```

## 📊 Monitoring

### **Performance Metrics**

- **Extraction Rate**: Records per second
- **Data Volume**: Bytes extracted per run
- **Error Rate**: Failed extractions percentage
- **Latency**: Time to first record

### **Health Checks**

- **Connection Health**: Source system connectivity
- **Schema Drift**: Schema change detection
- **Data Quality**: Data validation and profiling

## 🔧 Troubleshooting

### **Common Issues**

1. **Connection Timeout**: [Solution]
2. **Schema Changes**: [Solution]
3. **Performance Issues**: [Solution]
4. **Memory Usage**: [Solution]

### **Debugging**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
[tap-name] --config config.json --catalog catalog.json

# Connection diagnostics
[tap-name] --config config.json --diagnose
```

## 📚 Documentation

- **[Singer Specification](https://hub.meltano.com/singer/spec)** - Singer tap standards
- **[Data Source Documentation]** - [Data source] specific documentation
- **[FLEXT Integration Guide](../docs/singer-integration.md)** - FLEXT ecosystem integration

---

**Singer Ecosystem**: [Tap Name] | **FLEXT Integration**: Enterprise Grade | **Data Quality**: Validated

````

---

## 📋 TEMPLATE 4: INFRASTRUCTURE PROJECTS

### **Infrastructure Project Template (README.md)**

```markdown
# [Infrastructure Project] - [Brief Description]

**Version [X.Y.Z]** | **Type: Infrastructure Library** | **Integration: FLEXT Ecosystem**

Enterprise-grade infrastructure library providing [specific capabilities] for the FLEXT ecosystem with high-performance implementation, comprehensive error handling, and production-ready reliability.

## 📋 Infrastructure Overview

### **Purpose**
[Clear statement of what this infrastructure library provides to the FLEXT ecosystem]

### **Architecture Position**
- **Layer**: Infrastructure Library
- **Type**: [Database/Network/Storage/etc.] Infrastructure
- **Dependencies**: flext-core, [other dependencies]
- **Consumers**: [List projects that use this infrastructure]
- **Performance**: [Performance characteristics]

## 🎯 Key Capabilities

### **Core Infrastructure Features**
- **[Feature 1]**: [High-performance implementation details]
- **[Feature 2]**: [Reliability and error handling]
- **[Feature 3]**: [Integration patterns]
- **[Feature 4]**: [Configuration and management]

### **Technical Specifications**
- **Python Version**: 3.13+
- **Performance**: [Specific performance metrics]
- **Scalability**: [Scaling characteristics]
- **Reliability**: [Availability and error handling]

## 🚀 Quick Start

### **Installation**

```bash
# Install with Poetry
poetry add [infrastructure-project]

# Install with pip
pip install [infrastructure-project]
````

### **Basic Usage**

```python
from [infrastructure_project] import [MainClass]
from flext_core import FlextResult

# Initialize infrastructure component
component = [MainClass](
    host="localhost",
    port=5432,
    connection_pool_size=10
)

# Use infrastructure component
result = component.[method]()
if result.success:
    print(f"Success: {result.value}")
else:
    print(f"Error: {result.error}")
```

## 🔧 Configuration

### **Connection Configuration**

```python
# Database connection example
connection_config = {
    "host": "localhost",
    "port": 5432,
    "username": "user",
    "password": "password",
    "database": "flext",
    "pool_size": 10,
    "timeout": 30,
    "ssl_mode": "require"
}
```

### **Performance Configuration**

```python
# Performance tuning options
performance_config = {
    "connection_pool_size": 20,
    "query_timeout": 30,
    "batch_size": 1000,
    "retry_attempts": 3,
    "backoff_strategy": "exponential"
}
```

## 🏗️ Architecture

### **Component Design**

- **Connection Management**: [Description of connection handling]
- **Error Handling**: [Error handling patterns with FlextResult]
- **Performance Optimization**: [Performance optimization strategies]
- **Monitoring Integration**: [Integration with observability systems]

### **Design Patterns**

- **Factory Pattern**: [Usage for component creation]
- **Repository Pattern**: [Data access abstraction]
- **Circuit Breaker**: [Failure handling and recovery]
- **Connection Pooling**: [Resource management]

## 🔗 Integration Patterns

### **FLEXT Ecosystem Integration**

```python
# Integration with flext-core
from flext_core import FlextContainer, FlextResult
from [infrastructure_project] import [Component]

# Register with dependency injection
container = FlextContainer()
container.register([Component], [ComponentImpl])

# Use in services
class ApplicationService:
    def __init__(self, component: [Component]):
        self.component = component

    def perform_operation(self) -> FlextResult[str]:
        result = self.component.execute()
        return result
```

### **Configuration Integration**

```python
# Integration with FLEXT configuration
from flext_core.config import ConfigManager
from [infrastructure_project] import [Component]

config = ConfigManager()
component_config = config.get_section("infrastructure.[component]")
component = [Component](config=component_config)
```

## 🧪 Testing

### **Testing Strategy**

- **Unit Tests**: Comprehensive unit testing with mocks
- **Integration Tests**: Real infrastructure integration testing
- **Performance Tests**: Load testing and benchmarking
- **Reliability Tests**: Failure simulation and recovery testing

### **Test Configuration**

```python
# Test configuration
test_config = {
    "host": "localhost",
    "port": 5433,  # Test database port
    "database": "flext_test",
    "pool_size": 5
}
```

## 📊 Performance

### **Performance Characteristics**

- **Throughput**: [Operations per second]
- **Latency**: [Response time characteristics]
- **Memory Usage**: [Memory consumption patterns]
- **Scalability**: [Scaling behavior]

### **Benchmarking**

```bash
# Run performance benchmarks
python -m pytest tests/performance/ --benchmark-only

# Load testing
python scripts/load_test.py --connections 100 --duration 300
```

## 🔧 Operations

### **Health Monitoring**

```python
# Health check implementation
health_result = component.health_check()
if health_result.success:
    print("Infrastructure component healthy")
else:
    print(f"Health check failed: {health_result.error}")
```

### **Metrics and Monitoring**

- **Connection Metrics**: Pool usage, connection counts
- **Performance Metrics**: Query latency, throughput
- **Error Metrics**: Error rates, failure patterns
- **Resource Metrics**: Memory, CPU, network usage

## 🔒 Security

### **Security Features**

- **Authentication**: [Authentication mechanisms]
- **Authorization**: [Access control patterns]
- **Encryption**: [Data encryption at rest and in transit]
- **Audit Logging**: [Security event logging]

### **Security Configuration**

```python
# Security configuration
security_config = {
    "ssl_mode": "require",
    "ssl_cert": "/path/to/cert.pem",
    "ssl_key": "/path/to/key.pem",
    "ssl_ca": "/path/to/ca.pem"
}
```

## 🔧 Troubleshooting

### **Common Issues**

1. **Connection Issues**: [Diagnosis and resolution]
2. **Performance Problems**: [Optimization strategies]
3. **Configuration Errors**: [Common misconfigurations]
4. **Resource Exhaustion**: [Resource management solutions]

### **Debugging Tools**

```python
# Debug configuration
debug_config = {
    "log_level": "DEBUG",
    "log_queries": True,
    "trace_connections": True
}
```

## 📚 Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[Performance Guide](docs/performance.md)** - Performance tuning guide
- **[Security Guide](docs/security.md)** - Security configuration and best practices

---

**FLEXT Infrastructure**: [Project Name] | **Performance**: Enterprise Grade | **Reliability**: Production Ready

```

---

## 🎯 IMPLEMENTATION GUIDELINES

### **Template Usage Instructions**

1. **Choose Appropriate Template**: Select template based on project type
2. **Customize Content**: Replace all `[placeholders]` with project-specific content
3. **Maintain Standards**: Follow professional English and enterprise standards
4. **Validate Integration**: Ensure proper FLEXT ecosystem integration
5. **Review Quality**: Complete documentation review before finalization

### **Quality Standards**
- **Professional English**: Business-grade English throughout
- **No Marketing Content**: Factual, technical documentation only
- **Consistent with Reality**: Accurate representation of actual capabilities
- **Enterprise Grade**: Professional documentation suitable for enterprise use
- **FLEXT Integration**: Deep integration with ecosystem patterns and standards

### **Customization Guidelines**
- **Project Identity**: Clearly establish project purpose and ecosystem role
- **Technical Accuracy**: Accurate technical specifications and capabilities
- **Integration Patterns**: Proper integration with flext-core and ecosystem
- **Operational Excellence**: Comprehensive operational and monitoring guidance

---

**Template Authority**: Enterprise Documentation Standard for FLEXT Ecosystem
**Scope**: All 33 FLEXT projects documentation standardization
**Quality**: 100% professional, no marketing content, consistent with reality
```
