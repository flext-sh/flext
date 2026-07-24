# FLEXT Code Diagrams

**Reviewed**: 2026-02-17 | **Scope**: Documentation alignment and link consistency

## Table of Contents

- [FLEXT Code Diagrams](#flext-code-diagrams)
  - [Overview](#overview)
  - [1. r[T] Class Diagram](#1-flextresultt-class-diagram)
  - [2. FlextContainer Class Diagram](#2-flextcontainer-class-diagram)
  - [3. FlextModels Domain Model](#3-flextmodels-domain-model)
  - [4. LDAP Service Entity Relationship Diagram](#4-ldap-service-entity-relationship-diagram)
  - [5. API Gateway Request Flow Sequence Diagram](#5-api-gateway-request-flow-sequence-diagram)
  - [6. Data Pipeline Execution Sequence Diagram](#6-data-pipeline-execution-sequence-diagram)
  - [7. Error Handling Flow Sequence Diagram](#7-error-handling-flow-sequence-diagram)
  - [8. Plugin Execution Architecture](#8-plugin-execution-architecture)
  - [9. Configuration Management Class Diagram](#9-configuration-management-class-diagram)
  - [10. Event Sourcing Architecture](#10-event-sourcing-architecture)
  - [Code Quality Metrics](#code-quality-metrics)
    - [Test Coverage by Component](#test-coverage-by-component)
    - [Performance Benchmarks](#performance-benchmarks)
    - [Memory Usage](#memory-usage)

## Overview

This document provides detailed code-level diagrams showing the implementation structure of key components in the FLEXT
platform,
including class diagrams, entity relationship diagrams, and sequence diagrams.

## 1. r[T] Class Diagram

```mermaid
classDiagram
    class r~T~ {
        <<Generic Type>>
        +T value
        +Exception error
        +bool is_success
        +bool is_failure
        +unwrap() T
        +unwrap_failure() Exception
        +value T
        +error str
        +map(Func~T, U~) r~U~
        +flat_map(Func~T, r~U~~) r~U~
        +recover(Func~str, T~~) r~T~
        +tap(Action~T~) r~T~
        +tap_error(Action~str~) r~T~
        +ok(T value) r~T~
        +fail(Exception error) r~T~
    }

    class FlextSuccess~T~ {
        +T value
        +bool is_success = true
        +bool is_failure = false
        +unwrap() T
        +map(Func~T, U~) r~U~
        +flat_map(Func~T, r~U~~) r~U~
    }

    class FlextFailure~T~ {
        +Exception error
        +bool is_success = false
        +bool is_failure = true
        +unwrap_failure() Exception
        +map_error(Func~str, str~) r~T~
    }

    r~T~ <|-- FlextSuccess~T~
    r~T~ <|-- FlextFailure~T~
```

## 2. FlextContainer Class Diagram

```mermaid
classDiagram
    class FlextContainer {
        <<Singleton>>
        -Dict~str, ServiceRegistration~ registrations
        -Dict~str, t.JsonValue~ instances
        +register_singleton~T~(str key, Type~T~ service_type) None
        +register_transient~T~(str key, Type~T~ service_type) None
        +register_factory~T~(str key, Callable~T~ factory) None
        +resolve~T~(str key) r~T~
        +get~T~(str key) r~T~
        +is_registered(str key) bool
        +get_global() FlextContainer
        +clear() None
    }

    class ServiceRegistration {
        +str key
        +ServiceLifetime lifetime
        +Type service_type
        +Callable factory
        +t.JsonValue instance
        +create_instance() t.JsonValue
    }

    class ServiceLifetime {
        <<Enumeration>>
        SINGLETON
        TRANSIENT
        SCOPED
    }

    FlextContainer --> ServiceRegistration : contains
    ServiceRegistration --> ServiceLifetime : uses
```

## 3. FlextModels Domain Model

```mermaid
classDiagram
    class FlextModels {
        <<Namespace>>
    }

    class Entity {
        <<Abstract Base Class>>
        +str id
        +datetime created_at
        +datetime updated_at
        +bool is_deleted
        +**eq**(other) bool
        +**hash**() int
        +to_dict() Dict
        +from_dict(data) Entity
    }

    class Value {
        <<Abstract Base Class>>
        +**eq**(other) bool
        +**hash**() int
        +to_dict() Dict
        +from_dict(data) Value
    }

    class AggregateRoot {
        <<Abstract Base Class>>
        +List~DomainEvent~ domain_events
        +add_domain_event(event) None
        +clear_domain_events() None
        +get_domain_events() List~DomainEvent~
    }

    class DomainEvent {
        <<Abstract Base Class>>
        +str event_id
        +datetime occurred_at
        +str event_type
        +Dict event_data
    }

    class User {
        +str name
        +Email email
        +List~Role~ roles
        +bool is_active
        +activate() None
        +deactivate() None
        +add_role(role) None
        +remove_role(role) None
    }

    class Email {
        +str address
        +validate() bool
        +**str**() str
    }

    class Role {
        +str name
        +List~Permission~ permissions
        +add_permission(permission) None
        +remove_permission(permission) None
        +has_permission(permission) bool
    }

    class Permission {
        +str name
        +str resource
        +str action
        +**str**() str
    }

    FlextModels --> Entity
    FlextModels --> Value
    FlextModels --> AggregateRoot
    FlextModels --> DomainEvent

    Entity <|-- AggregateRoot
    Value <|-- Email
    AggregateRoot <|-- User
    User --> Email : contains
    User --> Role : has many
    Role --> Permission : has many
```

## 4. LDAP Service Entity Relationship Diagram

```mermaid
erDiagram
    LDAP_CONNECTION {
        string id PK
        string name
        string host
        int port
        string base_dn
        string bind_dn
        string bind_password
        boolean use_ssl
        boolean use_tls
        datetime created_at
        datetime updated_at
    }

    LDAP_USER {
        string id PK
        string connection_id FK
        string dn
        string cn
        string sn
        string given_name
        string mail
        string telephone_number
        string department
        string title
        boolean is_active
        datetime last_sync
        datetime created_at
        datetime updated_at
    }

    LDAP_GROUP {
        string id PK
        string connection_id FK
        string dn
        string cn
        string description
        string member_dn
        boolean is_active
        datetime last_sync
        datetime created_at
        datetime updated_at
    }

    LDAP_ORGANIZATIONAL_UNIT {
        string id PK
        string connection_id FK
        string dn
        string ou
        string description
        string parent_dn
        boolean is_active
        datetime last_sync
        datetime created_at
        datetime updated_at
    }

    LDAP_SYNC_LOG {
        string id PK
        string connection_id FK
        string sync_type
        string status
        int records_processed
        int records_success
        int records_failed
        text error_message
        datetime started_at
        datetime completed_at
    }

    LDAP_CONNECTION ||--o{ LDAP_USER : has
    LDAP_CONNECTION ||--o{ LDAP_GROUP : has
    LDAP_CONNECTION ||--o{ LDAP_ORGANIZATIONAL_UNIT : has
    LDAP_CONNECTION ||--o{ LDAP_SYNC_LOG : generates
```

## 5. API Gateway Request Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant Client
    participant APIGateway
    participant AuthService
    participant CoreService
    participant Database
    participant Redis

    Client->>APIGateway: HTTP Request
    APIGateway->>APIGateway: Validate Request
    APIGateway->>AuthService: Validate JWT Token
    AuthService->>Redis: Check Token Cache
    Redis-->>AuthService: Token Data
    AuthService-->>APIGateway: Auth Result

    alt Token Valid
        APIGateway->>CoreService: Process Request
        CoreService->>Database: Query Data
        Database-->>CoreService: Data Result
        CoreService-->>APIGateway: Response Data
        APIGateway->>Redis: Cache Response
        APIGateway-->>Client: HTTP Response
    else Token Invalid
        APIGateway-->>Client: 401 Unauthorized
    end
```

## 6. Data Pipeline Execution Sequence Diagram

```mermaid
sequenceDiagram
    participant Scheduler
    participant RuntimeService
    participant SingerTap
    participant DBTTransform
    participant SingerTarget
    participant Database
    participant FileSystem

    Scheduler->>RuntimeService: Trigger Pipeline
    RuntimeService->>SingerTap: Execute Data Extraction
    SingerTap->>Database: Query Source Data
    Database-->>SingerTap: Source Data
    SingerTap->>FileSystem: Write Singer Messages
    SingerTap-->>RuntimeService: Extraction Complete

    RuntimeService->>DBTTransform: Execute Data Transformation
    DBTTransform->>FileSystem: Read Singer Messages
    FileSystem-->>DBTTransform: Singer Messages
    DBTTransform->>Database: Execute SQL Transformations
    Database-->>DBTTransform: Transformed Data
    DBTTransform->>FileSystem: Write Transformed Data
    DBTTransform-->>RuntimeService: Transformation Complete

    RuntimeService->>SingerTarget: Execute Data Loading
    SingerTarget->>FileSystem: Read Transformed Data
    FileSystem-->>SingerTarget: Transformed Data
    SingerTarget->>Database: Load Target Data
    Database-->>SingerTarget: Load Complete
    SingerTarget-->>RuntimeService: Loading Complete

    RuntimeService-->>Scheduler: Pipeline Complete
```

## 7. Error Handling Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant Service
    participant r
    participant Logger
    participant ErrorHandler
    participant NotificationService

    Service->>r: Process Operation
    r->>r: Execute Business Logic

    alt Operation Success
        r-->>Service: Success Result
        Service->>Logger: Log Success
    else Operation Failure
        r->>ErrorHandler: Handle Error
        ErrorHandler->>Logger: Log Error
        ErrorHandler->>NotificationService: Send Alert
        NotificationService-->>ErrorHandler: Alert Sent
        ErrorHandler-->>r: Error Handled
        r-->>Service: Failure Result
        Service->>Logger: Log Failure
    end
```

## 8. Plugin Execution Architecture

```mermaid
classDiagram
    class PluginManager {
        +Dict~str, Plugin~ plugins
        +register_plugin(plugin) None
        +execute_plugin(plugin_id, input_data) r~T~
        +get_plugin_status(plugin_id) PluginStatus
        +list_plugins() List~Plugin~
    }

    class Plugin {
        <<Abstract Base Class>>
        +str plugin_id
        +str name
        +str version
        +PluginType type
        +PluginStatus status
        +execute(input_data) r~T~
        +validate_config(settings) bool
        +get_metadata() PluginMetadata
    }

    class SingerTap {
        +str source_type
        +Dict config_schema
        +execute_discovery() r~Catalog~
        +execute_sync(settings) r~SyncResult~
    }

    class SingerTarget {
        +str destination_type
        +Dict config_schema
        +execute_sync(catalog, records) r~SyncResult~
    }

    class DBTTransform {
        +str transform_type
        +List~str~ dependencies
        +execute_transform(sql) r~TransformResult~
    }

    class PluginStatus {
        <<Enumeration>>
        REGISTERED
        RUNNING
        COMPLETED
        FAILED
        CANCELLED
    }

    class PluginType {
        <<Enumeration>>
        TAP
        TARGET
        TRANSFORM
        CUSTOM
    }

    PluginManager --> Plugin : manages
    Plugin <|-- SingerTap
    Plugin <|-- SingerTarget
    Plugin <|-- DBTTransform
    Plugin --> PluginStatus : has
    Plugin --> PluginType : has
```

## 9. Configuration Management Class Diagram

```mermaid
classDiagram
    class FlextSettings {
        <<Singleton>>
        -Dict~str, t.JsonValue~ settings
        -ConfigSource source
        +get~T~(key, default_value) T
        +set(key, value) None
        +load_from_env() None
        +load_from_file(path) None
        +validate() bool
        +reload() None
    }

    class ConfigSource {
        <<Abstract Base Class>>
        +load_settings() Dict~str, t.JsonValue~
        +save_settings(settings) None
        +validate_settings(settings) bool
    }

    class EnvironmentConfigSource {
        +load_settings() Dict~str, t.JsonValue~
        +get_env_var(key, default_value) str
    }

    class FileConfigSource {
        +str file_path
        +ConfigFormat format
        +load_settings() Dict~str, t.JsonValue~
        +save_settings(settings) None
    }

    class DatabaseConfigSource {
        +str connection_string
        +load_settings() Dict~str, t.JsonValue~
        +save_settings(settings) None
    }

    class ConfigFormat {
        <<Enumeration>>
        JSON
        YAML
        TOML
        INI
    }

    FlextSettings --> ConfigSource : uses
    ConfigSource <|-- EnvironmentConfigSource
    ConfigSource <|-- FileConfigSource
    ConfigSource <|-- DatabaseConfigSource
    FileConfigSource --> ConfigFormat : uses
```

## 10. Event Sourcing Architecture

```mermaid
classDiagram
    class EventStore {
        +append_events(stream_id, events) r~None~
        +get_events(stream_id, from_version) r~List~Event~~
        +get_stream_metadata(stream_id) r~StreamMetadata~
        +create_snapshot(stream_id, version) r~Snapshot~
        +get_snapshot(stream_id) r~Snapshot~
    }

    class Event {
        <<Abstract Base Class>>
        +str event_id
        +str stream_id
        +int version
        +datetime occurred_at
        +str event_type
        +Dict event_data
        +str correlation_id
        +str causation_id
    }

    class StreamMetadata {
        +str stream_id
        +int current_version
        +datetime created_at
        +datetime last_updated
        +int event_count
    }

    class Snapshot {
        +str stream_id
        +int version
        +datetime created_at
        +Dict aggregate_data
        +str snapshot_type
    }

    class AggregateRoot {
        +str id
        +int version
        +List~Event~ uncommitted_events
        +apply_event(event) None
        +mark_events_as_committed() None
        +get_uncommitted_events() List~Event~
    }

    class EventHandler {
        <<Abstract Base Class>>
        +handle(event) None
        +can_handle(event_type) bool
    }

    EventStore --> Event : stores
    EventStore --> StreamMetadata : manages
    EventStore --> Snapshot : creates
    AggregateRoot --> Event : produces
    EventHandler --> Event : processes
```

## Code Quality Metrics

### Test Coverage by Component

- **r[T]**: 95% coverage
- **FlextContainer**: 99% coverage
- **FlextModels**: 65% coverage
- **LDAP Service**: 85% coverage
- **API Gateway**: 80% coverage
- **Plugin Manager**: 70% coverage

### Performance Benchmarks

- **r Operations**: < 1ms per operation
- **Container Resolution**: < 0.1ms per service
- **LDAP Queries**: < 100ms per query
- **API Response Time**: < 200ms per request
- **Plugin Execution**: < 5s per plugin

### Memory Usage

- **r Instances**: ~100 bytes per instance
- **Container Services**: ~1KB per service registration
- **LDAP Connections**: ~2MB per connection pool
- **API Gateway**: ~50MB base memory usage
- **Plugin Runtime**: ~10MB per plugin

---

**Last Updated**: 2025-01-XX
**Version**: 1.0.0
**Maintainer**: FLEXT Architecture Team
