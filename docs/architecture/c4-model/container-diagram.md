# FLEXT Container Diagram

## Table of Contents

- [FLEXT Container Diagram](#flext-container-diagram)
  - [Overview](#overview)
  - [Container Diagram](#container-diagram)
  - [Container Responsibilities](#container-responsibilities)
    - [Web Layer](#web-layer)
      - [FLEXT Web UI](#flext-web-ui)
    - [API Layer](#api-layer)
      - [API Gateway (flext-api)](#api-gateway-flext-api)
      - [Authentication Service (flext-auth)](#authentication-service-flext-auth)
    - [Core Services](#core-services)
      - [Core Service (flext-core)](#core-service-flext-core)
    - [Data Integration Services](#data-integration-services)
      - [LDAP Service (flext-ldap)](#ldap-service-flext-ldap)
      - [LDIF Service (flext-ldif)](#ldif-service-flext-ldif)
      - [Oracle Service (flext-oracle-\*)](#oracle-service-flext-oracle-)
    - [Singer Platform](#singer-platform)
      - [Singer Taps (flext-tap-\*)](#singer-taps-flext-tap-)
      - [Singer Targets (flext-target-\*)](#singer-targets-flext-target-)
      - [DBT Transformations (flext-dbt-\*)](#dbt-transformations-flext-dbt-)
    - [Runtime Service](#runtime-service)
      - [Pipeline Runtime](#pipeline-runtime)
    - [Quality and Observability](#quality-and-observability)
      - [Quality Service (flext-quality)](#quality-service-flext-quality)
      - [Observability Service (flext-observability)](#observability-service-flext-observability)
    - [CLI and Tools](#cli-and-tools)
      - [CLI Tool (flext-cli)](#cli-tool-flext-cli)
  - [Data Storage Layer](#data-storage-layer)
    - [PostgreSQL](#postgresql)
    - [Redis](#redis)
    - [File Storage](#file-storage)
  - [Communication Patterns](#communication-patterns)
    - [Synchronous Communication](#synchronous-communication)
    - [Asynchronous Communication](#asynchronous-communication)
    - [Data Flow Patterns](#data-flow-patterns)
  - [Technology Decisions](#technology-decisions)
    - [Programming Languages](#programming-languages)
    - [Frameworks and Libraries](#frameworks-and-libraries)
    - [Data Storage](#data-storage)
    - [Integration Protocols](#integration-protocols)

## Overview

The FLEXT platform is composed of multiple containers that work together to provide enterprise data integration
capabilities. Each container has specific responsibilities and communicates through well-defined interfaces.

## Container Diagram

```mermaid
graph TB
    %% External Users
    DataEngineers[Data Engineers]
    SystemAdmins[System Administrators]
    BusinessUsers[Business Users]
    Developers[Developers]

    %% External Systems
    LDAPSystems[LDAP Systems]
    OracleSystems[Oracle Systems]
    FileSystems[File Systems]
    MonitoringSystems[Monitoring Systems]

    %% FLEXT Platform Containers
    subgraph FLEXT["FLEXT Enterprise Data Integration Platform"]
        %% Web Layer
        WebUI[FLEXT Web UI<br/>React/TypeScript<br/>Port 3000]

        %% API Layer
        APIGateway[API Gateway<br/>flext-api<br/>Port 8081]

        %% Authentication
        AuthService[Authentication Service<br/>flext-auth<br/>Port 8082]

        %% Core Services
        CoreService[Core Service<br/>flext-core<br/>Foundation Library]

        %% Data Integration Services
        LDAPService[LDAP Service<br/>flext-ldap<br/>Port 8083]
        LDIFService[LDIF Service<br/>flext-ldif<br/>Port 8084]
        OracleService[Oracle Service<br/>flext-oracle-*<br/>Port 8085]

        %% Singer Platform
        SingerTaps[Singer Taps<br/>flext-tap-*<br/>Data Extraction]
        SingerTargets[Singer Targets<br/>flext-target-*<br/>Data Loading]
        DBTTransformations[DBT Transformations<br/>flext-dbt-*<br/>Data Transformation]

        %% Runtime Service
        PipelineRuntime[Pipeline Runtime<br/>Python 3.13+<br/>Service Layer]

        %% Quality and Observability
        QualityService[Quality Service<br/>flext-quality<br/>Port 8086]
        ObservabilityService[Observability Service<br/>flext-observability<br/>Port 8087]

        %% CLI and Tools
        CLITool[CLI Tool<br/>flext-cli<br/>Command Line Interface]
    end

    %% Data Storage
    subgraph DataStorage["Data Storage Layer"]
        PostgreSQL[(PostgreSQL<br/>Metadata & Configuration)]
        Redis[(Redis<br/>Cache & Sessions)]
        FileStorage[(File Storage<br/>LDIF & Config Files)]
    end

    %% External Integrations
    subgraph ExternalSystems["External Systems"]
        LDAPSystems
        OracleSystems
        FileSystems
        MonitoringSystems
    end

    %% User Interactions
    DataEngineers --> WebUI
    DataEngineers --> CLITool
    SystemAdmins --> WebUI
    SystemAdmins --> CLITool
    BusinessUsers --> WebUI
    Developers --> CLITool

    %% Internal Communication
    WebUI --> APIGateway
    CLITool --> APIGateway
    APIGateway --> AuthService
    APIGateway --> CoreService
    APIGateway --> LDAPService
    APIGateway --> LDIFService
    APIGateway --> OracleService
    APIGateway --> QualityService
    APIGateway --> ObservabilityService

    %% Runtime Integration
    PipelineRuntime --> APIGateway
    PipelineRuntime --> SingerTaps
    PipelineRuntime --> SingerTargets
    PipelineRuntime --> DBTTransformations

    %% Service Dependencies
    LDAPService --> CoreService
    LDIFService --> CoreService
    OracleService --> CoreService
    QualityService --> CoreService
    ObservabilityService --> CoreService

    %% Data Storage Connections
    CoreService --> PostgreSQL
    AuthService --> PostgreSQL
    QualityService --> PostgreSQL
    ObservabilityService --> PostgreSQL

    APIGateway --> Redis
    AuthService --> Redis

    LDIFService --> FileStorage
    SingerTaps --> FileStorage
    SingerTargets --> FileStorage

    %% External System Connections
    LDAPService --> LDAPSystems
    OracleService --> OracleSystems
    LDIFService --> FileSystems
    ObservabilityService --> MonitoringSystems

    %% Styling
    classDef user fill:#e1f5fe
    classDef container fill:#e8f5e8
    classDef storage fill:#fff3e0
    classDef external fill:#f3e5f5

    class DataEngineers,SystemAdmins,BusinessUsers,Developers user
    class WebUI,APIGateway,AuthService,CoreService,LDAPService,LDIFService,OracleService,SingerTaps,SingerTargets,
    DBTTransformations,PipelineRuntime,QualityService,ObservabilityService,CLITool container
    class PostgreSQL,Redis,FileStorage storage
    class LDAPSystems,OracleSystems,FileSystems,MonitoringSystems external
```

## Container Responsibilities

### Web Layer

#### FLEXT Web UI

- **Technology**: React/TypeScript
- **Port**: 3000
- **Responsibilities**:
  - User interface for data pipeline management
  - Data quality dashboards and reports
  - System Administration interface
  - Real-time monitoring and alerting

### API Layer

#### API Gateway (flext-api)

- **Technology**: Python 3.13+ with FastAPI
- **Port**: 8081
- **Responsibilities**:
  - Central API endpoint for all client requests
  - Request routing and load balancing
  - API versioning and documentation
  - Rate limiting and throttling
  - OpenAPI specification generation

#### Authentication Service (flext-auth)

- **Technology**: Python 3.13+ with flext-core
- **Port**: 8082
- **Responsibilities**:
  - User authentication and session management
  - OAuth2/OIDC integration
  - Role-based access control (RBAC)
  - JWT token generation and validation
  - Multi-factor authentication support

### Core Services

#### Core Service (flext-core)

- **Technology**: Python 3.13+ foundation library
- **Responsibilities**:
  - Railway-oriented programming patterns
  - Dependency injection container
  - Domain-driven design patterns
  - Configuration management
  - Structured logging and context propagation
  - Event bus and messaging

### Data Integration Services

#### LDAP Service (flext-ldap)

- **Technology**: Python 3.13+ with ldap3
- **Port**: 8083
- **Responsibilities**:
  - LDAP directory connectivity
  - User and group management
  - Directory synchronization
  - LDAP query optimization
  - Connection pooling and failover

#### LDIF Service (flext-ldif)

- **Technology**: Python 3.13+ with RFC 2849/4512 compliance
- **Port**: 8084
- **Responsibilities**:
  - LDIF file parsing and generation
  - Data migration and synchronization
  - Schema validation and transformation
  - Batch processing and optimization
  - Error handling and recovery

#### Oracle Service (flext-oracle-\*)

- **Technology**: Python 3.13+ with cx_Oracle
- **Port**: 8085
- **Responsibilities**:
  - Oracle database connectivity
  - WMS (Warehouse Management) integration
  - OIC (Integration Cloud) connectivity
  - Data extraction and loading
  - Transaction management and rollback

### Singer Platform

#### Singer Taps (flext-tap-\*)

- **Technology**: Python 3.13+ with Singer SDK
- **Responsibilities**:
  - Data extraction from various sources
  - Schema discovery and cataloging
  - Incremental data synchronization
  - State management and checkpointing
  - Error handling and retry logic

#### Singer Targets (flext-target-\*)

- **Technology**: Python 3.13+ with Singer SDK
- **Responsibilities**:
  - Data loading to various destinations
  - Schema evolution and migration
  - Data validation and quality checks
  - Batch and streaming processing
  - Performance optimization

#### DBT Transformations (flext-dbt-\*)

- **Technology**: Python 3.13+ with DBT Core
- **Responsibilities**:
  - Data transformation and modeling
  - SQL generation and optimization
  - Dependency management
  - Testing and validation
  - Documentation generation

### Runtime Service

#### Pipeline Runtime

- **Technology**: Python 3.13+ with FLEXT service abstractions
- **Responsibilities**:
  - Pipeline runtime coordination
  - Plugin execution and management
  - Service orchestration and coordination
  - Event sourcing and CQRS patterns
  - Distributed coordination and scaling

### Quality and Observability

#### Quality Service (flext-quality)

- **Technology**: Python 3.13+ with flext-core
- **Port**: 8086
- **Responsibilities**:
  - Data quality validation and monitoring
  - Schema validation and compliance
  - Data lineage tracking
  - Quality metrics and reporting
  - Automated quality checks

#### Observability Service (flext-observability)

- **Technology**: Python 3.13+ with OpenTelemetry
- **Port**: 8087
- **Responsibilities**:
  - Metrics collection and aggregation
  - Distributed tracing and correlation
  - Log aggregation and analysis
  - Alerting and notification
  - Performance monitoring

### CLI and Tools

#### CLI Tool (flext-cli)

- **Technology**: Python 3.13+ with Click
- **Responsibilities**:
  - Command-line interface for all operations
  - Pipeline configuration and management
  - System Administration tasks
  - Development and debugging tools
  - Batch operations and scripting

## Data Storage Layer

### PostgreSQL

- **Purpose**: Primary database for metadata and configuration
- **Data**: User accounts, pipeline configurations, system settings, audit logs
- **Access**: All services except Redis and file storage

### Redis

- **Purpose**: Caching and session management
- **Data**: Session tokens, cached API responses, temporary data
- **Access**: API Gateway, Authentication Service

### File Storage

- **Purpose**: LDIF files and configuration storage
- **Data**: LDIF files, configuration files, logs, temporary data
- **Access**: LDIF Service, Singer Taps/Targets

## Communication Patterns

### Synchronous Communication

- **REST APIs**: Primary communication between containers
- **gRPC**: High-performance internal communication
- **Database Queries**: Direct database access for data operations

### Asynchronous Communication

- **Event Bus**: Event-driven communication via flext-core
- **Message Queues**: Reliable message delivery (planned)
- **Webhooks**: External system notifications

### Data Flow Patterns

- **Request-Response**: API calls and database queries
- **Event Streaming**: Real-time data processing
- **Batch Processing**: Scheduled data pipeline execution
- **File Transfer**: LDIF and configuration file handling

## Technology Decisions

### Programming Languages

- **Python 3.13+**: Primary language for business logic and data processing
- **TypeScript**: Frontend web application

### Frameworks and Libraries

- **flext-core**: Foundation library with architectural patterns
- **FastAPI**: Modern Python web framework
- **React**: Frontend user interface framework

### Data Storage

- **PostgreSQL**: Reliable relational database for metadata
- **Redis**: High-performance in-memory cache
- **File System**: Simple file storage for LDIF and configuration

### Integration Protocols

- **LDAP/LDIF**: Directory service integration
- **SQL**: Database connectivity
- **REST/OpenAPI**: Web service integration
- **gRPC**: High-performance service communication

---

**Last Updated**: 2025-01-XX
**Version**: 1.0.0
**Maintainer**: FLEXT Architecture Team
