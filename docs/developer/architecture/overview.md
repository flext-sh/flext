# FLEXT Architecture Overview

**Version**: 0.9.0-dev | **Status**: Under Development | **Last Updated**: 2025-08-05

This document provides a overview of the FLEXT ecosystem architecture, current implementation status, and development roadmap.

---

## 🏗️ System Architecture

### Service Layer Overview

FLEXT implements a **dual-service distributed architecture** designed for business scalability:

```
┌─────────────────────────────────────────────────────┐
│                FLEXT Ecosystem                      │
├─────────────────────────────────────────────────────┤
│  🔥 CORE SERVICES (2 services)                     │
│  ├─ FlexCore (Go:8080)     - Runtime container     │
│  ├─ FLEXT Service (Go:8081) - Control panel        │
├─────────────────────────────────────────────────────┤
│  📚 FOUNDATION LIBRARIES (2 projects)              │
│  ├─ flext-core            - Base patterns & types  │
│  └─ flext-observability   - Monitoring foundation  │
├─────────────────────────────────────────────────────┤
│  🏗️ INFRASTRUCTURE LIBRARIES (6 projects)          │
│  ├─ flext-db-oracle       - Oracle connectivity    │
│  ├─ flext-ldap            - LDAP directory services│
│  ├─ flext-ldif            - LDIF file processing   │
│  ├─ flext-oracle-wms      - Oracle WMS integration │
│  ├─ flext-grpc            - gRPC communication     │
│  └─ [observability moved to foundation]            │
├─────────────────────────────────────────────────────┤
│  🔗 INTEGRATION LAYER (1 project)                  │
│  └─ flext-meltano         - Singer/Meltano/DBT     │
├─────────────────────────────────────────────────────┤
│  🚀 APPLICATION SERVICES (5 projects)              │
│  ├─ flext-api             - REST API services      │
│  ├─ flext-auth            - Authentication         │
│  ├─ flext-web             - Web interface          │
│  ├─ flext-cli             - Command-line tools     │
│  └─ flext-quality         - Code quality analysis  │
├─────────────────────────────────────────────────────┤
│  🎵 SINGER ECOSYSTEM (15 projects)                 │
│  ├─ TAPS (5): Oracle, LDAP, LDIF, OIC, WMS        │
│  ├─ TARGETS (5): Oracle, LDAP, LDIF, OIC, WMS     │
│  ├─ DBT (4): Transformation projects               │
│  └─ EXTENSIONS (1): Oracle OIC utilities           │
├─────────────────────────────────────────────────────┤
│  🏢 SPECIALIZED SERVICES (2 projects)              │
│  ├─ client-a-oud-mig         - client-a migration        │
│  └─ client-b-meltano-native - client-b platform    │
└─────────────────────────────────────────────────────┘
```

### Architectural Patterns

**Clean Architecture**: Strict layer separation with dependency inversion
**Domain-Driven Design**: Rich domain models with clear bounded contexts  
**CQRS**: Command/query separation for scalability
**Event Sourcing**: Immutable event streams for audit and recovery

---

## 🎯 Core Services Status

### FlexCore (Go Runtime Container - Port 8080)

**Purpose**: Runtime container and orchestration engine
**Technology**: Go 1.24+ with plugin system
**Current Status**: ⚠️ Under Major Refactoring

**Responsibilities**:

- Plugin orchestration and secure execution
- Event sourcing with PostgreSQL persistence
- CQRS implementation for command/query separation
- Multi-node coordination via Redis

**Critical Issues** (See [Technical Debt](../technical-debt.md)):

- Clean Architecture violations (HTTP server in Application layer)
- Multiple conflicting CQRS implementations
- In-memory event store (data loss risk)
- Plugin system lacks security isolation

**Architecture Compliance**:

- Clean Architecture: 30% (Target: 90%)
- Domain-Driven Design: 40% (Target: 85%)
- CQRS: 25% (Target: 80%)
- Event Sourcing: 20% (Target: 75%)

### FLEXT Service (Go/Python Bridge - Port 8081)

**Purpose**: Control panel and Python ecosystem integration
**Technology**: Go service with Python business logic bridge
**Current Status**: ✅ Basic Implementation Complete

**Responsibilities**:

- Service orchestration and management
- Python ecosystem integration (Meltano, Singer, DBT)
- Configuration distribution and monitoring
- Web interface coordination

---

## 📚 Library Ecosystem

### Foundation Layer (Stable)

**flext-core**: Base patterns, FlextResult, DI container, logging

- Status: ✅ Implementation available (MyPy errors being resolved)
- Usage: Imported by all other Python projects
- Patterns: Railway-oriented programming, dependency injection

**flext-observability**: Monitoring, metrics, tracing foundation

- Status: ✅ Basic Implementation
- Integration: OpenTelemetry, Prometheus, structured logging

### Infrastructure Layer (Parallel Libraries)

All infrastructure libraries are **independent** with no cross-dependencies:

**Database & Directory**:

- `flext-db-oracle`: Oracle database connectivity and optimization
- `flext-ldap`: LDAP server connectivity and directory operations
- `flext-ldif`: LDIF file processing and validation

**Integration & Communication**:

- `flext-oracle-wms`: Oracle WMS API connectivity and data models
- `flext-grpc`: gRPC communication protocols
- `flext-meltano`: Singer/Meltano/DBT orchestration platform

### Application Layer

**Service Libraries**:

- `flext-api`: REST API services with FastAPI
- `flext-auth`: Authentication and authorization
- `flext-web`: Web interface and dashboard components
- `flext-cli`: Command-line tools and utilities
- `flext-quality`: Code quality analysis and reporting

**Current Status**: Basic implementations, requires standardization

---

## 🎵 Singer/Meltano/DBT Integration

### Consolidated Architecture ✅

All Singer functionality is **properly consolidated** in `flext-meltano`:

**Core Components**:

```python
from flext_meltano import (
    FlextMeltanoTap,           # Tap execution and management
    FlextMeltanoTarget,        # Target execution and management
    FlextMeltanoPlatform,      # Core platform integration
    FlextMeltanoDbtProject,    # DBT project management
    FlextMeltanoSettings,      # Configuration management
)
```

**Singer Ecosystem Projects**:

**Extractors (5 taps)**:

- `flext-tap-ldap`, `flext-tap-ldif`, `flext-tap-oracle`, `flext-tap-oracle-oic`, `flext-tap-oracle-wms`

**Loaders (5 targets)**:

- `flext-target-ldap`, `flext-target-ldif`, `flext-target-oracle`, `flext-target-oracle-oic`, `flext-target-oracle-wms`

**Transformers (4 DBT projects)**:

- `flext-dbt-ldap`, `flext-dbt-ldif`, `flext-dbt-oracle`, `flext-dbt-oracle-wms`

**Extensions (1 project)**:

- `flext-oracle-oic`: Oracle Integration Cloud utilities

### Project Specializations (Not Duplications)

**Oracle Ecosystem**:

- `flext-tap-oracle`: Direct database SQL extraction
- `flext-tap-oracle-oic`: Integration Cloud REST APIs
- `flext-tap-oracle-wms`: Warehouse Management specialized APIs
- `flext-db-oracle`: Shared connectivity library

**LDAP Ecosystem**:

- `flext-tap-ldap`: Live LDAP server extraction
- `flext-tap-ldif`: Static LDIF file processing
- `flext-ldap`: Shared LDAP connectivity
- `flext-ldif`: Shared LDIF parsing utilities

---

## 🔄 Dependency Architecture

### Layer Dependencies (Enforced)

```
APPLICATION LAYER
     ↓ (can import from all lower layers)
INTEGRATION LAYER
     ↓ (can import from infrastructure and foundation)
INFRASTRUCTURE LAYER (parallel - no cross-imports)
     ↓ (can import from foundation only)
FOUNDATION LAYER (no external dependencies)
```

### ✅ Permitted Dependencies

```bash
# Higher layers can import from lower layers
flext-api → flext-meltano, flext-auth, flext-core
flext-meltano → flext-db-oracle, flext-ldap, flext-core
flext-db-oracle → flext-core
```

### ❌ Prohibited Cross-Dependencies

```bash
# Infrastructure cross-imports (STRICTLY FORBIDDEN)
flext-db-oracle ↔ flext-ldap          # Violates layer isolation
flext-ldap ↔ flext-ldif               # Creates circular dependencies
flext-oracle-wms ↔ flext-grpc         # Breaks parallel architecture

# Upward dependencies (STRICTLY FORBIDDEN)
flext-core → flext-api                # Foundation → Application
flext-ldap → flext-meltano            # Infrastructure → Integration
```

---

## 🚧 Current Development Status

### Production Readiness Assessment

**✅ Ready for Use**:

- Singer/Meltano/DBT ecosystem (consolidated architecture)
- Basic FLEXT Service functionality
- Infrastructure libraries (database connectivity)
- Foundation patterns (flext-core base functionality)

**⚠️ Under Development**:

- FlexCore architectural refactoring (8-12 weeks estimated)
- Application service standardization
- Documentation and testing improvements
- Performance optimization and monitoring

**❌ Critical Blockers**:

- FlexCore architectural violations prevent production deployment
- Plugin system security gaps require immediate attention
- Event sourcing implementation needs PostgreSQL persistence
- CQRS implementation needs unification

### Development Priorities

**Phase 1 (Weeks 1-2): Critical Architecture Fixes**

1. Fix FlexCore Clean Architecture violations
2. Unify CQRS implementation
3. Replace in-memory event store with PostgreSQL
4. Implement proper dependency injection

**Phase 2 (Weeks 3-4): Domain Enhancement**

1. Implement rich domain model with business logic
2. Create domain services for complex orchestration
3. Add plugin system security and isolation
4. Complete event sourcing with replay capability

**Phase 3 (Weeks 5-8): Production Readiness**

1. Performance optimization and caching
2. Comprehensive testing coverage
3. Security hardening and audit
4. Documentation completion and API stabilization

---

## 🎓 Architectural Principles

### Core Design Principles

1. **Clean Architecture Enforcement**: Strict layer separation with dependency inversion
2. **Domain-Driven Design**: Rich domain models with clear bounded contexts
3. **CQRS + Event Sourcing**: Scalable command/query separation with event streams
4. **Specialization over Duplication**: Each project serves distinct business purposes
5. **Library vs Service Separation**: Clear distinction in deployment and lifecycle

### Quality Assurance

- **Zero Tolerance Quality Gates**: All violations must be fixed
- **Automated Validation**: CI/CD pipeline enforcement
- **Dependency Management**: Regular audits and security updates
- **Documentation Standards**: Architecture decisions recorded and communicated

---

## 🔮 Technology Stack

### Primary Technologies

- **Go 1.24+**: High-performance services with modern language features
- **Python 3.13+**: Data processing with rich ecosystem integration
- **PostgreSQL 15+**: Event sourcing and application database (port 5433)
- **Redis 7+**: Distributed coordination and caching (port 6380)
- **Docker**: Multi-stage containerization for all services

### Framework Integration

- **FastAPI**: Python REST API services with automatic documentation
- **Gin Framework**: Go HTTP routing and middleware
- **Singer SDK**: Data integration standard implementation
- **Meltano 3.8.0**: Data orchestration platform
- **DBT**: Data transformation and modeling

### Observability

- **OpenTelemetry**: Distributed tracing and metrics collection
- **Prometheus**: Metrics storage and alerting
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Checks**: Comprehensive service monitoring

---

## 📋 Integration Patterns

### Service Communication

**HTTP/REST**: Synchronous API calls for immediate operations
**Event Streams**: hronous coordination via PostgreSQL event store
**Redis Pub/Sub**: Real-time state synchronization
**gRPC**: High-performance service-to-service communication

### Data Flow Architecture

```
External Request → HTTP/gRPC Adapter → Use Case Handler →
Domain Service → Repository/Event Store → PostgreSQL/Redis
```

### Cross-Service Patterns

- **FlextResult Pattern**: Railway-oriented programming for error handling
- **Dependency Injection**: Centralized container with type safety
- **Domain Events**: Event-driven communication between services
- **Command/Query Buses**: CQRS implementation across services

---

**Architecture Status**: UNDER DEVELOPMENT  
**Next Review**: 2025-09-05  
**Critical Path**: FlexCore architectural refactoring completion

This document represents the current state and development roadmap for the FLEXT ecosystem architecture. For specific implementation details and current issues, refer to project-specific documentation and the [Technical Debt Analysis](../technical-debt.md).
