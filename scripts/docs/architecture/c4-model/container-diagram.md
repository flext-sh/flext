# Container Diagram


<!-- TOC START -->
- [Overview](#overview)
- [Container Descriptions](#container-descriptions)
  - [User-Facing Containers](#user-facing-containers)
  - [Core Containers](#core-containers)
  - [External Systems](#external-systems)
<!-- TOC END -->

## Overview

FLEXT container architecture showing the high-level technology choices and deployment units:

```plantuml
@startuml FLEXT Container Diagram
!include <C4/C4_Container>

Person(user, "User", "Data engineers, REDACTED_LDAP_BIND_PASSWORDistrators, developers")

System_Boundary(flext_system, "FLEXT Platform") {

    Container(api_gateway, "API Gateway", "Python/FastAPI", "REST API gateway with OpenAPI documentation")
    Container(cli_interface, "CLI Interface", "Python/Click+Rich", "Command-line interface with rich formatting")

    Container(flext_core, "FLEXT Core", "Python", "Foundation library with Clean Architecture patterns")

    Container(domain_services, "Services", "Python", "Business logic and domain services") {
        Container(ldap_service, "LDAP Service", "Python", "LDAP directory operations")
        Container(ldif_service, "LDIF Service", "Python", "LDIF processing and migration")
        Container(oracle_service, "Oracle Service", "Python", "Oracle database operations")
        Container(api_service, "API Service", "Python", "REST API framework")
    }

    Container(data_integration, "Data Integration", "Python/Singer", "ETL pipelines and data transformation") {
        Container(taps, "Data Taps", "Python", "Data extraction from sources")
        Container(targets, "Data Targets", "Python", "Data loading to destinations")
        Container(transforms, "Transformations", "DBT", "Data transformation and modeling")
    }

    Container(runtime_container, "Runtime Container", "Go", "Plugin execution and orchestration")
}

Container_Ext(ldap_directory, "LDAP Directory", "OpenLDAP/Active Directory", "Corporate directory services")
Container_Ext(oracle_database, "Oracle Database", "Oracle RDBMS", "Enterprise database systems")
Container_Ext(data_warehouse, "Data Warehouse", "Snowflake/BigQuery", "Analytics data warehouse")
Container_Ext(monitoring, "Monitoring", "Prometheus/Grafana", "Observability platform")

Rel(user, api_gateway, "Uses", "HTTP/REST")
Rel(user, cli_interface, "Uses", "CLI")

Rel(api_gateway, domain_services, "Routes to", "HTTP")
Rel(cli_interface, domain_services, "Commands", "Function calls")

Rel(domain_services, flext_core, "Uses", "Library imports")
Rel(data_integration, flext_core, "Uses", "Library imports")

Rel(domain_services, ldap_directory, "Queries", "LDAP")
Rel(domain_services, oracle_database, "Queries", "JDBC")

Rel(data_integration, ldap_directory, "Extracts", "LDAP")
Rel(data_integration, oracle_database, "Extracts", "JDBC")
Rel(data_integration, data_warehouse, "Loads", "Various")

Rel(runtime_container, monitoring, "Reports", "Metrics")
Rel_D(domain_services, monitoring, "Reports", "Logs")

@enduml
```

## Container Descriptions

### User-Facing Containers

#### API Gateway

- **Technology**: Python/FastAPI
- **Purpose**: REST API gateway with OpenAPI documentation
- **Responsibilities**:
  - Request routing and load balancing
  - API documentation generation
  - Authentication and rate limiting
  - Request/response transformation

#### CLI Interface

- **Technology**: Python/Click+Rich
- **Purpose**: Command-line interface with rich formatting
- **Responsibilities**:
  - Command parsing and execution
  - Interactive user experience
  - Progress reporting and error handling
  - Configuration management

### Core Containers

#### FLEXT Core

- **Technology**: Python
- **Purpose**: Foundation library with Clean Architecture patterns
- **Responsibilities**:
  - FlextResult[T] error handling
  - FlextContainer dependency injection
  - FlextModels domain patterns
  - FlextLogger structured logging

#### Services

- **Technology**: Python
- **Purpose**: Business logic and domain services
- **Responsibilities**:
  - LDAP directory operations
  - LDIF processing and migration
  - Oracle database integration
  - REST API framework

#### Data Integration

- **Technology**: Python/Singer+DBT
- **Purpose**: ETL pipelines and data transformation
- **Responsibilities**:
  - Data extraction (Taps)
  - Data loading (Targets)
  - Data transformation (DBT)

#### Runtime Container

- **Technology**: Go
- **Purpose**: Plugin execution and orchestration
- **Responsibilities**:
  - Plugin lifecycle management
  - Service orchestration
  - Health monitoring
  - Container management

### External Systems

#### LDAP Directory

- **Technology**: OpenLDAP/Active Directory/Oracle OID
- **Purpose**: Corporate directory services
- **Interfaces**: LDAP protocol (RFC 4511)

#### Oracle Database

- **Technology**: Oracle RDBMS
- **Purpose**: Enterprise database systems
- **Interfaces**: JDBC, OCI

#### Data Warehouse

- **Technology**: Snowflake/BigQuery/Redshift
- **Purpose**: Analytics data warehouse
- **Interfaces**: Various ETL protocols

#### Monitoring

- **Technology**: Prometheus/Grafana
- **Purpose**: Observability platform
- **Interfaces**: Metrics, logs, traces

---

**Generated:** 2025-10-10 15:19:05
**Version:** 0.9.0
