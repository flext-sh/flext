# FLEXT Ecosystem Documentation Index

**Complete Cross-Reference Guide for All 33 FLEXT Projects**

**Version**: 0.9.0
**Last Updated**: 2025-08-01  
**Status**: 🔄 Active Development (Documentation Standardization)

---

## 🌐 Ecosystem Overview

The FLEXT ecosystem consists of **33 interconnected projects** implementing enterprise-grade data integration with **Clean Architecture**, **Domain-Driven Design**, and **CQRS patterns**.

### **Architecture Layers**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM (33 Projects)                 │
├─────────────────────────────────────────────────────────────────┤
│ Foundation (2): flext-core | flext-observability                │
├─────────────────────────────────────────────────────────────────┤
│ Runtime Services (1): flexcore (Go)                             │
├─────────────────────────────────────────────────────────────────┤
│ Application Services (7): API | Auth | Web | CLI | Meltano      │
│                          Plugin | Quality                        │
├─────────────────────────────────────────────────────────────────┤
│ Infrastructure (5): DB-Oracle | LDAP | LDIF | Oracle-WMS | gRPC │
├─────────────────────────────────────────────────────────────────┤
│ Singer Taps (5): LDAP | LDIF | Oracle | Oracle-OIC | Oracle-WMS │
├─────────────────────────────────────────────────────────────────┤
│ Singer Targets (5): LDAP | LDIF | Oracle | Oracle-OIC | Oracle-WMS │
├─────────────────────────────────────────────────────────────────┤
│ DBT Projects (4): LDAP | LDIF | Oracle | Oracle-WMS             │
├─────────────────────────────────────────────────────────────────┤
│ Client Projects (2): algar-oud-mig | gruponos-meltano-native    │
├─────────────────────────────────────────────────────────────────┤
│ Extensions (2): oracle-oic-ext | demo                           │
├═════════════════════════════════════════════════════════════════┤
│              FLEXT CORE - ARCHITECTURAL FOUNDATION               │
│  FlextResult | FlextContainer | Domain Patterns | Config        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Core Foundation (2 Projects)

### **1. flext-core** - Architectural Foundation

- **Path**: [`flext-core/`](../flext-core/)
- **Type**: Foundation Library (Python 3.13)
- **Purpose**: Architectural patterns, type-safe error handling, DDD foundation
- **Key Exports**: FlextResult[T], FlextContainer, FlextEntity, FlextService
- **Dependencies**: None (foundation layer)
- **Used By**: All 32 other projects
- **Documentation**:
  - [README](../flext-core/README.md) | [CLAUDE.md](../flext-core/CLAUDE.md)
  - [API Reference](../flext-core/docs/api/) | [Examples](../flext-core/examples/)

### **2. flext-observability** - Monitoring Foundation

- **Path**: [`flext-observability/`](../flext-observability/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: Monitoring, metrics, tracing, health checks for ecosystem
- **Key Exports**: FlextLogger, health check patterns, metrics collection
- **Dependencies**: flext-core
- **Used By**: All services and applications
- **Documentation**:
  - [README](../flext-observability/README.md) | [CLAUDE.md](../flext-observability/CLAUDE.md)

---

## 🏢 Core Services (3 Projects)

### **3. FlexCore** - Go Runtime Container

- **Path**: [`flexcore/`](../flexcore/)
- **Type**: Core Service (Go 1.24, Port 8080)
- **Purpose**: Runtime container service with plugin system, Clean Architecture + DDD + CQRS + Event Sourcing
- **Key Features**: Plugin system, proxy adapters, high-performance runtime
- **Dependencies**: flext-core (via Python bridge)
- **Integrates With**: FLEXT Service (port 8081), all plugins
- **Documentation**:
  - [README](../flexcore/README.md) | [Go Documentation](../flexcore/docs/)

### **4. FLEXT Service** - Data Platform Service

- **Path**: [`cmd/flext/`](../cmd/flext/)
- **Type**: Core Service (Go/Python, Port 8081)
- **Purpose**: Main data platform service with Python bridge for Meltano execution
- **Key Features**: Singer/Meltano orchestration, Python-Go bridge
- **Dependencies**: flext-core, flext-meltano, flexcore integration
- **Integrates With**: FlexCore (port 8080), all Singer components
- **Documentation**:
  - [README](../cmd/flext/README.md) | [Integration Guide](../cmd/flext/docs/)

### **5. FLEXT Control Panel** - Main Repository

- **Path**: [`./`](../)
- **Type**: Control Panel (Go, reorganized with pkg/ structure)
- **Purpose**: Enterprise data integration control panel and service orchestration
- **Key Features**: Service management, pipeline orchestration, unified interface
- **Dependencies**: All FLEXT ecosystem components
- **Documentation**:
  - [README](../README.md) | [Architecture](../docs/architecture/)

---

## 🚀 Application Services (5 Projects)

### **6. flext-api** - REST API Services

- **Path**: [`flext-api/`](../flext-api/)
- **Type**: Application Service (Python 3.13, FastAPI)
- **Purpose**: REST API services with FastAPI, unified HTTP client functionality
- **Key Features**: FlextApi class, HTTP client plugins, builder patterns
- **Dependencies**: flext-core, flext-observability, flext-auth
- **Used By**: All services requiring HTTP API functionality
- **Documentation**:
  - [README](../flext-api/README.md) | [CLAUDE.md](../flext-api/CLAUDE.md)
  - [API Reference](../flext-api/docs/api-reference.md) | [Client Guide](../flext-api/docs/client.md)

### **7. flext-auth** - Authentication Services

- **Path**: [`flext-auth/`](../flext-auth/)
- **Type**: Application Service (Python 3.13)
- **Purpose**: Authentication and authorization services for ecosystem
- **Key Features**: JWT tokens, LDAP integration, role-based access
- **Dependencies**: flext-core, flext-ldap, flext-api
- **Used By**: All services requiring authentication
- **Documentation**:
  - [README](../flext-auth/README.md) | [CLAUDE.md](../flext-auth/CLAUDE.md)

### **8. flext-web** - Web Interface

- **Path**: [`flext-web/`](../flext-web/)
- **Type**: Application Service (Python 3.13, Web Framework)
- **Purpose**: Web interface and dashboard for FLEXT ecosystem
- **Key Features**: Pipeline management UI, monitoring dashboards
- **Dependencies**: flext-core, flext-api, flext-auth
- **Used By**: End users, administrators
- **Documentation**:
  - [README](../flext-web/README.md) | [CLAUDE.md](../flext-web/CLAUDE.md)

### **9. flext-cli** - Command-Line Interface

- **Path**: [`flext-cli/`](../flext-cli/)
- **Type**: Application Service (Python 3.13, CLI)
- **Purpose**: Command-line interface tools for FLEXT ecosystem
- **Key Features**: Pipeline management, service control, development tools
- **Dependencies**: flext-core, flext-api
- **Used By**: Developers, DevOps, administrators
- **Documentation**:
  - [README](../flext-cli/README.md) | [CLAUDE.md](../flext-cli/CLAUDE.md)

### **10. flext-quality** - Code Quality Analysis

- **Path**: [`flext-quality/`](../flext-quality/)
- **Type**: Application Service (Python 3.13)
- **Purpose**: Code quality analysis and reporting across ecosystem
- **Key Features**: Quality metrics, compliance reporting, automated analysis
- **Dependencies**: flext-core, flext-observability
- **Used By**: Development team, CI/CD pipelines
- **Documentation**:
  - [README](../flext-quality/README.md) | [CLAUDE.md](../flext-quality/CLAUDE.md)

---

## 🏗️ Infrastructure Libraries (6 Projects)

### **11. flext-db-oracle** - Oracle Database Connectivity

- **Path**: [`flext-db-oracle/`](../flext-db-oracle/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: Oracle database connectivity and operations with enterprise patterns
- **Key Features**: Connection pooling, query optimization, WMS integration
- **Dependencies**: flext-core
- **Used By**: Oracle taps/targets, WMS integration, ALGAR migration
- **Documentation**:
  - [README](../flext-db-oracle/README.md) | [CLAUDE.md](../flext-db-oracle/CLAUDE.md)

### **12. flext-ldap** - LDAP Directory Services

- **Path**: [`flext-ldap/`](../flext-ldap/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: LDAP server connectivity and directory operations
- **Key Features**: Directory search, authentication, user management
- **Dependencies**: flext-core
- **Used By**: flext-auth, LDAP tap/target, ALGAR migration
- **Documentation**:
  - [README](../flext-ldap/README.md) | [CLAUDE.md](../flext-ldap/CLAUDE.md)

### **13. flext-ldif** - LDIF File Processing

- **Path**: [`flext-ldif/`](../flext-ldif/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: LDIF file processing and validation
- **Key Features**: LDIF parsing, validation, transformation
- **Dependencies**: flext-core
- **Used By**: LDIF tap/target, LDAP migration tools
- **Documentation**:
  - [README](../flext-ldif/README.md) | [CLAUDE.md](../flext-ldif/CLAUDE.md)

### **14. flext-oracle-wms** - Oracle WMS Integration

- **Path**: [`flext-oracle-wms/`](../flext-oracle-wms/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: Oracle WMS API connectivity and data models
- **Key Features**: WMS API client, inventory tracking, shipment management
- **Dependencies**: flext-core, flext-db-oracle
- **Used By**: WMS tap/target, warehouse management workflows
- **Documentation**:
  - [README](../flext-oracle-wms/README.md) | [CLAUDE.md](../flext-oracle-wms/CLAUDE.md)

### **15. flext-grpc** - gRPC Communication

- **Path**: [`flext-grpc/`](../flext-grpc/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: gRPC communication protocols and service definitions
- **Key Features**: Service definitions, client/server patterns, streaming
- **Dependencies**: flext-core
- **Used By**: FlexCore integration, distributed services
- **Documentation**:
  - [README](../flext-grpc/README.md) | [CLAUDE.md](../flext-grpc/CLAUDE.md)

### **16. flext-meltano** - Singer/Meltano Orchestration

- **Path**: [`flext-meltano/`](../flext-meltano/)
- **Type**: Infrastructure Library (Python 3.13)
- **Purpose**: Singer/Meltano/DBT orchestration (consolidated platform)
- **Key Features**: Pipeline orchestration, Singer SDK integration, DBT execution
- **Dependencies**: flext-core, all Singer components
- **Used By**: FLEXT Service, all data pipelines
- **Documentation**:
  - [README](../flext-meltano/README.md) | [CLAUDE.md](../flext-meltano/CLAUDE.md)

---

## 🎵 Singer Ecosystem (15 Projects)

### **Data Extractors - Taps (5 Projects)**

#### **17. flext-tap-ldap** - LDAP Data Extractor

- **Path**: [`flext-tap-ldap/`](../flext-tap-ldap/)
- **Type**: Singer Tap (Python 3.13)
- **Purpose**: Extract data from LDAP directories
- **Dependencies**: flext-core, flext-ldap, Singer SDK
- **Targets**: All FLEXT targets
- **Documentation**: [README](../flext-tap-ldap/README.md) | [CLAUDE.md](../flext-tap-ldap/CLAUDE.md)

#### **18. flext-tap-ldif** - LDIF File Extractor

- **Path**: [`flext-tap-ldif/`](../flext-tap-ldif/)
- **Type**: Singer Tap (Python 3.13)
- **Purpose**: Extract data from LDIF files
- **Dependencies**: flext-core, flext-ldif, Singer SDK
- **Targets**: All FLEXT targets
- **Documentation**: [README](../flext-tap-ldif/README.md) | [CLAUDE.md](../flext-tap-ldif/CLAUDE.md)

#### **19. flext-tap-oracle** - Oracle Database Extractor

- **Path**: [`flext-tap-oracle/`](../flext-tap-oracle/)
- **Type**: Singer Tap (Python 3.13)
- **Purpose**: Extract data from Oracle databases
- **Dependencies**: flext-core, flext-db-oracle, Singer SDK
- **Targets**: All FLEXT targets
- **Documentation**: [README](../flext-tap-oracle/README.md) | [CLAUDE.md](../flext-tap-oracle/CLAUDE.md)

#### **20. flext-tap-oracle-oic** - Oracle Integration Cloud Extractor

- **Path**: [`flext-tap-oracle-oic/`](../flext-tap-oracle-oic/)
- **Type**: Singer Tap (Python 3.13)
- **Purpose**: Extract data from Oracle Integration Cloud
- **Dependencies**: flext-core, flext-db-oracle, Singer SDK
- **Targets**: All FLEXT targets
- **Documentation**: [README](../flext-tap-oracle-oic/README.md) | [CLAUDE.md](../flext-tap-oracle-oic/CLAUDE.md)

#### **21. flext-tap-oracle-wms** - Oracle WMS Extractor

- **Path**: [`flext-tap-oracle-wms/`](../flext-tap-oracle-wms/)
- **Type**: Singer Tap (Python 3.13)
- **Purpose**: Extract data from Oracle WMS systems
- **Dependencies**: flext-core, flext-oracle-wms, Singer SDK
- **Targets**: All FLEXT targets
- **Documentation**: [README](../flext-tap-oracle-wms/README.md) | [CLAUDE.md](../flext-tap-oracle-wms/CLAUDE.md)

### **Data Loaders - Targets (5 Projects)**

#### **22. flext-target-ldap** - LDAP Data Loader

- **Path**: [`flext-target-ldap/`](../flext-target-ldap/)
- **Type**: Singer Target (Python 3.13)
- **Purpose**: Load data to LDAP directories
- **Dependencies**: flext-core, flext-ldap, Singer SDK
- **Sources**: All FLEXT taps
- **Documentation**: [README](../flext-target-ldap/README.md) | [CLAUDE.md](../flext-target-ldap/CLAUDE.md)

#### **23. flext-target-ldif** - LDIF File Loader

- **Path**: [`flext-target-ldif/`](../flext-target-ldif/)
- **Type**: Singer Target (Python 3.13)
- **Purpose**: Load data to LDIF files
- **Dependencies**: flext-core, flext-ldif, Singer SDK
- **Sources**: All FLEXT taps
- **Documentation**: [README](../flext-target-ldif/README.md) | [CLAUDE.md](../flext-target-ldif/CLAUDE.md)

#### **24. flext-target-oracle** - Oracle Database Loader

- **Path**: [`flext-target-oracle/`](../flext-target-oracle/)
- **Type**: Singer Target (Python 3.13)
- **Purpose**: Load data to Oracle databases
- **Dependencies**: flext-core, flext-db-oracle, Singer SDK
- **Sources**: All FLEXT taps
- **Documentation**: [README](../flext-target-oracle/README.md) | [CLAUDE.md](../flext-target-oracle/CLAUDE.md)

#### **25. flext-target-oracle-oic** - Oracle Integration Cloud Loader

- **Path**: [`flext-target-oracle-oic/`](../flext-target-oracle-oic/)
- **Type**: Singer Target (Python 3.13)
- **Purpose**: Load data to Oracle Integration Cloud
- **Dependencies**: flext-core, flext-db-oracle, Singer SDK
- **Sources**: All FLEXT taps
- **Documentation**: [README](../flext-target-oracle-oic/README.md) | [CLAUDE.md](../flext-target-oracle-oic/CLAUDE.md)

#### **26. flext-target-oracle-wms** - Oracle WMS Loader

- **Path**: [`flext-target-oracle-wms/`](../flext-target-oracle-wms/)
- **Type**: Singer Target (Python 3.13)
- **Purpose**: Load data to Oracle WMS systems
- **Dependencies**: flext-core, flext-oracle-wms, Singer SDK
- **Sources**: All FLEXT taps
- **Documentation**: [README](../flext-target-oracle-wms/README.md) | [CLAUDE.md](../flext-target-oracle-wms/CLAUDE.md)

### **Data Transformers - DBT (4 Projects)**

#### **27. flext-dbt-ldap** - LDAP Data Transformations

- **Path**: [`flext-dbt-ldap/`](../flext-dbt-ldap/)
- **Type**: DBT Project (SQL/Python)
- **Purpose**: Transform LDAP data with business logic
- **Dependencies**: flext-core, DBT Core
- **Data Sources**: LDAP taps
- **Documentation**: [README](../flext-dbt-ldap/README.md) | [CLAUDE.md](../flext-dbt-ldap/CLAUDE.md)

#### **28. flext-dbt-ldif** - LDIF Data Transformations

- **Path**: [`flext-dbt-ldif/`](../flext-dbt-ldif/)
- **Type**: DBT Project (SQL/Python)
- **Purpose**: Transform LDIF data with validation and cleansing
- **Dependencies**: flext-core, DBT Core
- **Data Sources**: LDIF taps
- **Documentation**: [README](../flext-dbt-ldif/README.md) | [CLAUDE.md](../flext-dbt-ldif/CLAUDE.md)

#### **29. flext-dbt-oracle** - Oracle Data Transformations

- **Path**: [`flext-dbt-oracle/`](../flext-dbt-oracle/)
- **Type**: DBT Project (SQL/Python)
- **Purpose**: Transform Oracle data with enterprise business rules
- **Dependencies**: flext-core, DBT Core
- **Data Sources**: Oracle taps
- **Documentation**: [README](../flext-dbt-oracle/README.md) | [CLAUDE.md](../flext-dbt-oracle/CLAUDE.md)

#### **30. flext-dbt-oracle-wms** - Oracle WMS Data Transformations

- **Path**: [`flext-dbt-oracle-wms/`](../flext-dbt-oracle-wms/)
- **Type**: DBT Project (SQL/Python)
- **Purpose**: Transform WMS data with inventory and logistics rules
- **Dependencies**: flext-core, DBT Core
- **Data Sources**: Oracle WMS taps
- **Documentation**: [README](../flext-dbt-oracle-wms/README.md) | [CLAUDE.md](../flext-dbt-oracle-wms/CLAUDE.md)

### **Extensions (1 Project)**

#### **31. flext-oracle-oic-ext** - Oracle OIC Extensions

- **Path**: [`flext-oracle-oic-ext/`](../flext-oracle-oic-ext/)
- **Type**: Singer Extension (Python 3.13)
- **Purpose**: Extensions and utilities for Oracle Integration Cloud
- **Dependencies**: flext-core, flext-tap-oracle-oic, flext-target-oracle-oic
- **Used By**: Oracle OIC tap/target
- **Documentation**: [README](../flext-oracle-oic-ext/README.md) | [CLAUDE.md](../flext-oracle-oic-ext/CLAUDE.md)

---

## 🏢 Legacy/Specialized Projects (2 Projects)

### **32. algar-oud-mig** - ALGAR Oracle Unified Directory Migration

- **Path**: [`algar-oud-mig/`](../algar-oud-mig/)
- **Type**: Specialized Service (Python 3.13)
- **Purpose**: ALGAR Oracle Unified Directory migration project
- **Key Features**: Legacy system migration, data transformation, validation
- **Dependencies**: flext-core, flext-ldap, flext-db-oracle
- **Status**: Active migration project
- **Documentation**: [README](../algar-oud-mig/README.md) | [CLAUDE.md](../algar-oud-mig/CLAUDE.md)

### **33. gruponos-meltano-native** - GrupoNos Meltano Implementation

- **Path**: [`gruponos-meltano-native/`](../gruponos-meltano-native/)
- **Type**: Specialized Service (Python 3.13)
- **Purpose**: GrupoNos-specific Meltano implementation with FLEXT patterns
- **Key Features**: Custom business logic, specialized transformations
- **Dependencies**: flext-core, flext-meltano, custom requirements
- **Status**: Active implementation
- **Documentation**: [README](../gruponos-meltano-native/README.md) | [CLAUDE.md](../gruponos-meltano-native/CLAUDE.md)

---

## 🔗 Integration Matrix

### **Core Dependencies**

| Project                 | Depends On                      | Used By             | Integration Type    |
| ----------------------- | ------------------------------- | ------------------- | ------------------- |
| **flext-core**          | None                            | All 31 projects     | Foundation patterns |
| **flext-observability** | flext-core                      | All services        | Monitoring          |
| **FlexCore**            | flext-core (bridge)             | FLEXT Service       | Runtime container   |
| **FLEXT Service**       | flext-core, flext-meltano       | FlexCore, pipelines | Orchestration       |
| **flext-api**           | flext-core, flext-observability | All HTTP services   | API foundation      |

### **Service Integration Patterns**

1. **HTTP Communication**: flext-api → All services
2. **Authentication**: flext-auth → All user-facing services
3. **Data Processing**: flext-meltano → All Singer components
4. **Monitoring**: flext-observability → All services
5. **Database Access**: flext-db-oracle → Oracle components

### **Data Flow Patterns**

1. **Extract-Transform-Load**: Taps → DBT → Targets
2. **Service Orchestration**: FlexCore → FLEXT Service → Components
3. **User Interface**: flext-web → flext-api → Services
4. **Command Line**: flext-cli → flext-api → Services

---

## 📊 Documentation Status

### **Standardization Progress**

| Category               | Total  | Standardized | In Progress | Pending |
| ---------------------- | ------ | ------------ | ----------- | ------- |
| **Core Foundation**    | 2      | 2            | 0           | 0       |
| **Core Services**      | 3      | 1            | 1           | 1       |
| **Applications**       | 5      | 1            | 1           | 3       |
| **Infrastructure**     | 6      | 0            | 2           | 4       |
| **Singer Taps**        | 5      | 0            | 1           | 4       |
| **Singer Targets**     | 5      | 0            | 0           | 5       |
| **Singer DBT**         | 4      | 0            | 0           | 4       |
| **Extensions**         | 1      | 0            | 0           | 1       |
| **Legacy/Specialized** | 2      | 0            | 0           | 2       |
| **TOTAL**              | **32** | **4**        | **5**       | **24**  |

### **Priority Implementation Order**

1. **Week 1 (Critical)**: Core services and primary infrastructure
2. **Week 2 (High)**: Applications and remaining infrastructure
3. **Week 3 (Medium)**: Singer ecosystem (taps, targets, DBT)
4. **Week 4 (Low)**: Extensions and specialized projects

---

## 🛠️ Maintenance and Updates

### **Documentation Maintenance**

- **Index Updates**: This index is updated automatically when projects are added/modified
- **Cross-Reference Validation**: All links validated weekly via automated scripts
- **Standard Compliance**: All projects validated against documentation standard monthly
- **Content Reviews**: Technical accuracy review quarterly

### **Ecosystem Evolution**

- **New Projects**: Must follow standard template and be added to this index
- **Deprecated Projects**: Marked as deprecated, removed after 2 release cycles
- **Architecture Changes**: Reflected in integration matrix and dependency graphs
- **Version Updates**: All version references updated with each ecosystem release

---

**Index Version**: 1.0.0  
**Last Validation**: 2025-08-02  
**Next Review**: 2025-09-02  
**Maintained By**: FLEXT Documentation Team
