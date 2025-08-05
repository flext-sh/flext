# FLEXT Ecosystem Architecture

**Comprehensive architectural overview of the FLEXT enterprise data integration ecosystem**

**Version**: 0.9.0
**Status**: Production Ready  
**Last Updated**: 2025-08-02  
**Authority**: FLEXT Architecture Team

---

## 🏗️ Architectural Overview

The FLEXT ecosystem implements a **layered architecture** with **32 interconnected projects** following **Clean Architecture**, **Domain-Driven Design (DDD)**, and **CQRS patterns**. This document provides the definitive architectural reference for the entire ecosystem.

### **Ecosystem Classification and Structure**

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEXT ECOSYSTEM ARCHITECTURE                 │
├─════════════════════════════════════════════════════════════════┤
│  🔥 CORE SERVICES LAYER (3 projects)                           │
│  ├─ FlexCore (Go:8080)     - Runtime container & plugin system │
│  ├─ FLEXT Service (Go:8081) - Data platform orchestration      │
│  └─ Control Panel (Main)   - Enterprise control interface      │
├─────────────────────────────────────────────────────────────────┤
│  🚀 APPLICATION SERVICES LAYER (5 projects)                    │
│  ├─ flext-api             - REST API services foundation       │
│  ├─ flext-auth            - Authentication & authorization      │
│  ├─ flext-web             - Web interface & dashboard           │
│  ├─ flext-cli             - Command-line tools                  │
│  └─ flext-quality         - Code quality analysis              │
├─────────────────────────────────────────────────────────────────┤
│  🔗 INTEGRATION LAYER (1 project)                              │
│  └─ flext-meltano         - Singer/Meltano/DBT orchestration   │
├─────────────────────────────────────────────────────────────────┤
│  🏗️ INFRASTRUCTURE LAYER (6 projects - parallel)              │
│  ├─ flext-db-oracle       - Oracle database connectivity       │
│  ├─ flext-ldap            - LDAP directory services            │
│  ├─ flext-ldif            - LDIF file processing               │
│  ├─ flext-oracle-wms      - Oracle WMS API integration         │
│  ├─ flext-grpc            - gRPC communication protocols       │
│  └─ flext-observability   - Monitoring, metrics, tracing       │
├─════════════════════════════════════════════════════════════════┤
│  🎵 SINGER ECOSYSTEM LAYER (15 projects)                       │
│  ├─ EXTRACTORS (5 taps)   - Data source extraction            │
│  ├─ LOADERS (5 targets)   - Data destination loading          │
│  ├─ TRANSFORMERS (4 DBT)  - Data transformation & modeling     │
│  └─ EXTENSIONS (1 project) - Specialized utilities            │
├─────────────────────────────────────────────────────────────────┤
│  🏢 SPECIALIZED LAYER (2 projects)                             │
│  ├─ client-a-oud-mig         - client-a Oracle migration project     │
│  └─ client-b-meltano-native - client-b implementation         │
├─════════════════════════════════════════════════════════════════┤
│  🎯 FOUNDATION LAYER (2 projects)                              │
│  ├─ flext-core            - Architectural patterns & types     │
│  └─ [observability moved to infrastructure layer]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Project Classification

### **📚 Libraries (flext-\* projects)**

All `flext-*` projects are **reusable libraries** providing specialized functionality:

#### **Foundation Libraries (2 projects)**

```
FOUNDATION LAYER:
├── flext-core              # Base patterns, FlextResult, DI container
└── flext-observability     # Monitoring, metrics, tracing foundation
```

#### **Infrastructure Libraries (6 projects)**

```
INFRASTRUCTURE LAYER (parallel libraries - no cross-dependencies):
├── flext-db-oracle         # Oracle database connectivity & optimization
├── flext-ldap              # LDAP server connectivity & directory ops
├── flext-ldif              # LDIF file processing & validation
├── flext-oracle-wms        # Oracle WMS API connectivity & data models
├── flext-grpc              # gRPC communication protocols
└── [flext-observability]   # Monitoring infrastructure
```

#### **Integration Libraries (1 project)**

```
INTEGRATION LAYER:
└── flext-meltano           # Singer/Meltano/DBT orchestration platform
```

#### **Application Libraries (5 projects)**

```
APPLICATION LAYER:
├── flext-api               # REST API services with FastAPI
├── flext-auth              # Authentication & authorization
├── flext-web               # Web interface & dashboard components
├── flext-cli               # Command-line tools & utilities
└── flext-quality           # Code quality analysis & reporting
```

### **🔌 Singer Plugins (15 projects)**

All tap/target/dbt/ext projects are **Meltano plugins** implementing Singer specification:

#### **Data Extractors - Taps (5 projects)**

```
SINGER TAPS:
├── flext-tap-ldap          # LDAP server data extraction
├── flext-tap-ldif          # LDIF file data extraction
├── flext-tap-oracle        # Oracle database extraction
├── flext-tap-oracle-oic    # Oracle Integration Cloud extraction
└── flext-tap-oracle-wms    # Oracle WMS system extraction
```

#### **Data Loaders - Targets (5 projects)**

```
SINGER TARGETS:
├── flext-target-ldap       # LDAP server data loading
├── flext-target-ldif       # LDIF file data loading
├── flext-target-oracle     # Oracle database loading
├── flext-target-oracle-oic # Oracle Integration Cloud loading
└── flext-target-oracle-wms # Oracle WMS system loading
```

#### **Data Transformers - DBT (4 projects)**

```
DBT PROJECTS:
├── flext-dbt-ldap          # LDAP data transformations & business rules
├── flext-dbt-ldif          # LDIF data transformations & validation
├── flext-dbt-oracle        # Oracle data transformations & modeling
└── flext-dbt-oracle-wms    # Oracle WMS transformations & KPIs
```

#### **Extensions (1 project)**

```
SINGER EXTENSIONS:
└── flext-oracle-oic-ext    # Oracle Integration Cloud utilities & helpers
```

### **⚙️ Core Services (3 projects)**

High-performance services providing runtime and orchestration:

```
CORE SERVICES:
├── FlexCore (Go)           # Runtime container with plugin system (port 8080)
├── FLEXT Service (Go/Py)   # Data platform service (port 8081)
└── FLEXT Control Panel     # Enterprise control panel (main repository)
```

### **🏢 Specialized Services (2 projects)**

Customer-specific implementations:

```
SPECIALIZED SERVICES:
├── client-a-oud-mig           # client-a Oracle Unified Directory migration
└── client-b-meltano-native # client-b-specific Meltano implementation
```

---

## 🔄 Dependency Flow and Architecture Rules

### **Layered Architecture Dependencies**

Dependencies must flow **downward only** through architectural layers:

```
APPLICATION LAYER
     ↓ (can import from all lower layers)
INTEGRATION LAYER
     ↓ (can import from infrastructure and foundation)
INFRASTRUCTURE LAYER (parallel - no cross-imports)
     ↓ (can import from foundation only)
FOUNDATION LAYER (no external dependencies)
```

### **✅ Permitted Dependencies**

#### **Higher Layers → Lower Layers**

```bash
# Application layer can import from all lower layers
flext-api → flext-meltano, flext-auth, flext-observability, flext-core
flext-auth → flext-ldap, flext-core
flext-web → flext-api, flext-auth, flext-core

# Integration layer can import from infrastructure and foundation
flext-meltano → flext-db-oracle, flext-ldap, flext-ldif, flext-oracle-wms, flext-core

# Infrastructure can import from foundation only
flext-db-oracle → flext-core
flext-ldap → flext-core
flext-grpc → flext-core
```

### **❌ Prohibited Cross-Dependencies**

#### **Infrastructure Layer Cross-Imports (Strictly Forbidden)**

```bash
# These imports are NEVER allowed:
flext-db-oracle ↔ flext-ldap          # Infrastructure cross-dependency
flext-ldap ↔ flext-ldif               # Infrastructure cross-dependency
flext-oracle-wms ↔ flext-grpc         # Infrastructure cross-dependency
flext-observability ↔ flext-db-oracle # Infrastructure cross-dependency
```

#### **Upward Dependencies (Strictly Forbidden)**

```bash
# Lower layers cannot import from higher layers:
flext-core → flext-api                # Foundation → Application (FORBIDDEN)
flext-ldap → flext-meltano            # Infrastructure → Integration (FORBIDDEN)
flext-meltano → flext-web             # Integration → Application (FORBIDDEN)
```

---

## 🎵 Singer/Meltano/DBT Consolidation

### **✅ Successful Consolidation Architecture**

All Singer/Meltano/DBT functionality is properly consolidated in **flext-meltano** as the central orchestration platform:

#### **flext-meltano Core Components**

**Singer Integration Classes:**

```python
from flext_meltano import (
    FlextMeltanoTap,           # Tap execution and management
    FlextMeltanoTarget,        # Target execution and management
    FlextMeltanoStream,        # Stream processing utilities
    FlextMeltanoCatalog,       # Schema catalog management
)
```

**Meltano Platform Classes:**

```python
from flext_meltano import (
    FlextMeltanoPlatform,      # Core Meltano platform integration
    FlextMeltanoOrchestrator,  # Pipeline orchestration engine
    FlextMeltanoProjectManager, # Project lifecycle management
    FlextMeltanoJobManager,    # Job execution and monitoring
)
```

**DBT Integration Classes:**

```python
from flext_meltano import (
    FlextMeltanoDbtProject,    # DBT project management
    FlextMeltanoDbtRunner,     # DBT execution engine
    FlextMeltanoDbtModel,      # DBT model utilities
    FlextMeltanoDbtProfiler,   # DBT profiling and validation
)
```

**Configuration and Management:**

```python
from flext_meltano import (
    FlextMeltanoSettings,      # Configuration management
    FlextMeltanoConfigLoader,  # Dynamic configuration loading
    FlextMeltanoPluginManager, # Plugin lifecycle management
    FlextMeltanoExtensionManager, # Extension management
)
```

### **Hybrid Architecture Pattern**

**Orchestration Responsibility**: `flext-meltano`

- Tap/Target configuration and execution
- Project and environment management
- Job scheduling and monitoring
- Plugin lifecycle management

**Implementation Responsibility**: `singer-sdk`

- Stream/Sink base classes
- Type utilities and validation
- Protocol implementation details

**Dependencies**: `flext-meltano` includes `singer-sdk` as transitive dependency, providing seamless integration without duplication.

---

## 📋 Project Specializations

### **Oracle Ecosystem (Specialized, Not Duplicated)**

Each Oracle project serves distinct purposes:

#### **flext-tap-oracle** - Direct Database Access

- **Purpose**: Direct Oracle database SQL stream extraction
- **Technology**: Oracle SQL, native drivers, query optimization
- **Use Cases**: Raw database tables, views, stored procedures
- **Performance**: High-throughput SQL-based extraction

#### **flext-tap-oracle-oic** - Integration Cloud APIs

- **Purpose**: Oracle Integration Cloud REST API extraction
- **Technology**: REST APIs, OAuth2, integration adapters
- **Use Cases**: Integration flows, message queues, adapter configs
- **Performance**: API rate-limited, real-time integration data

#### **flext-tap-oracle-wms** - Warehouse Management APIs

- **Purpose**: Oracle WMS specialized API extraction
- **Technology**: WMS-specific APIs, inventory protocols
- **Use Cases**: Inventory tracking, shipment data, logistics KPIs
- **Performance**: Real-time warehouse operations data

#### **flext-db-oracle** - Shared Connectivity Library

- **Purpose**: Common Oracle database connectivity patterns
- **Technology**: Connection pooling, transaction management
- **Use Cases**: Shared by all Oracle taps/targets/transformers
- **Performance**: Optimized connection management and caching

### **LDAP Ecosystem (Specialized, Not Duplicated)**

#### **flext-tap-ldap** - Live Directory Extraction

- **Purpose**: Live LDAP server data extraction
- **Technology**: LDAP protocol, directory queries, authentication
- **Use Cases**: User management, organizational structure, groups
- **Performance**: Real-time directory synchronization

#### **flext-tap-ldif** - File Processing

- **Purpose**: Static LDIF file processing and extraction
- **Technology**: LDIF parsing, file validation, batch processing
- **Use Cases**: Directory backups, bulk imports, migration data
- **Performance**: High-throughput file processing

#### **flext-ldap** - Directory Services Library

- **Purpose**: Shared LDAP connectivity and operations
- **Technology**: LDAP client, search utilities, authentication
- **Use Cases**: Shared by LDAP-related taps/targets
- **Performance**: Optimized directory operations

#### **flext-ldif** - File Format Library

- **Purpose**: Shared LDIF parsing and generation utilities
- **Technology**: LDIF format parsing, validation, generation
- **Use Cases**: Shared by LDIF-related projects
- **Performance**: Efficient file format handling

---

## 🏛️ Clean Architecture Implementation

### **Layer Boundaries and Responsibilities**

#### **Domain Layer (Core Business Logic)**

```
Location: pkg/domain/
Dependencies: None (only Go standard library)
Responsibility: Pure business logic, entities, value objects, domain services
```

**Example Structure:**

```
pkg/domain/
├── entities/           # Business entities with behavior
├── events/            # Domain events for communication
├── repositories/      # Repository interfaces (ports)
├── services/          # Domain services with business rules
└── [bounded-contexts]/ # DDD bounded contexts
```

#### **Application Layer (Use Cases)**

```
Location: pkg/application/
Dependencies: Domain layer only
Responsibility: Application business rules, use cases, commands/queries
```

**Example Structure:**

```
pkg/application/
├── commands/          # CQRS commands
├── queries/           # CQRS queries
├── services/          # Application services
├── pipeline/          # Pipeline management use cases
└── plugin/            # Plugin management use cases
```

#### **Adapters Layer (Interface Implementations)**

```
Location: pkg/adapters/
Dependencies: Application and Domain layers
Responsibility: Interface implementations, controllers, gateways
```

**Example Structure:**

```
pkg/adapters/
├── controllers/http/  # REST API controllers
├── gateways/          # External system gateways
└── presenters/        # Response presentation logic
```

#### **Infrastructure Layer (Technical Concerns)**

```
Location: pkg/infrastructure/
Dependencies: Can import from any layer for implementation
Responsibility: Database, HTTP, messaging, external integrations
```

**Example Structure:**

```
pkg/infrastructure/
├── database/          # Database implementations
├── http/              # HTTP infrastructure
├── messaging/         # Message bus implementations
└── cache/             # Caching implementations
```

#### **Interfaces Layer (External Communication)**

```
Location: pkg/interfaces/
Dependencies: Orchestrates all layers
Responsibility: External communication protocols (REST, CLI, Web)
```

### **CQRS Pattern Implementation**

#### **Command Side (Write Operations)**

```go
// Command definition
type CreatePipelineCommand struct {
    Name        string `json:"name" validate:"required"`
    Description string `json:"description"`
    CreatedBy   string `json:"created_by" validate:"required"`
}

// Command handler
type CreatePipelineHandler struct {
    repo     ports.PipelineRepository
    eventBus ports.EventBus
}

func (h *CreatePipelineHandler) Handle(cmd CreatePipelineCommand) error {
    // Business logic implementation
    pipeline := entities.NewPipeline(cmd.Name, cmd.Description)

    if err := h.repo.Save(pipeline); err != nil {
        return err
    }

    // Publish domain events
    return h.eventBus.Publish(pipeline.Events()...)
}
```

#### **Query Side (Read Operations)**

```go
// Query definition
type GetPipelineQuery struct {
    ID     string `json:"id" validate:"required,uuid"`
    UserID string `json:"user_id" validate:"required"`
}

// Query result
type PipelineQueryResult struct {
    ID          string    `json:"id"`
    Name        string    `json:"name"`
    Description string    `json:"description"`
    Status      string    `json:"status"`
    CreatedAt   time.Time `json:"created_at"`
}

// Query handler
type GetPipelineQueryHandler struct {
    readModel ports.PipelineReadModel
}

func (h *GetPipelineQueryHandler) Handle(query GetPipelineQuery) (*PipelineQueryResult, error) {
    return h.readModel.GetPipeline(query.ID, query.UserID)
}
```

---

## 🔗 Integration Patterns

### **FlexCore ↔ FLEXT Service Communication**

#### **HTTP REST Integration**

```
FlexCore (Go:8080) ←→ FLEXT Service (Go/Python:8081)

Communication Patterns:
├── Plugin Management    # FlexCore manages plugins, FLEXT executes
├── Event Coordination   # Distributed event sourcing
├── Health Monitoring    # Cross-service health checks
└── Performance Metrics  # Shared observability data
```

#### **Python Bridge Integration**

```go
// Go service calling Python functionality
type PythonBridge interface {
    ExecuteMeltanoPipeline(config MeltanoConfig) (*PipelineResult, error)
    RunDBTModels(project string, models []string) (*DBTResult, error)
    ValidateSingerSchema(schema SingerSchema) error
}

// Implementation with process isolation
type ProcessPythonBridge struct {
    pythonPath string
    timeout    time.Duration
}
```

### **Cross-Service Event Communication**

#### **Domain Events Pattern**

```go
// Event definition
type PipelineExecutionStarted struct {
    BaseEvent
    PipelineID   string    `json:"pipeline_id"`
    ExecutionID  string    `json:"execution_id"`
    StartedBy    string    `json:"started_by"`
    StartedAt    time.Time `json:"started_at"`
}

// Event publishing
func (p *Pipeline) StartExecution(userID string) error {
    event := NewPipelineExecutionStarted(p.ID, userID)
    p.raiseEvent(event)
    return nil
}

// Event handling across services
type PipelineEventHandler struct {
    logger      ports.Logger
    notifier    ports.NotificationService
}

func (h *PipelineEventHandler) Handle(event PipelineExecutionStarted) error {
    // Handle cross-service coordination
    return h.notifier.NotifyPipelineStarted(event.PipelineID, event.StartedBy)
}
```

---

## ✅ Architectural Validation

### **✅ Consolidation Status: COMPLETE**

- ✅ **Singer/Meltano/DBT centralized** in `flext-meltano`
- ✅ **No problematic code duplication** found across ecosystem
- ✅ **Proper separation of concerns** maintained in all layers
- ✅ **Hybrid architecture** working correctly with singer-sdk integration
- ✅ **Clean Architecture boundaries** properly enforced

### **✅ Dependency Status: VALIDATED**

- ✅ **All projects have proper dependencies** following layer rules
- ✅ **No inappropriate cross-library imports** in infrastructure layer
- ✅ **Layer hierarchy respected** across all 32 projects
- ✅ **Foundation layer isolation** maintained (flext-core)
- ✅ **Integration layer consolidation** achieved (flext-meltano)

### **✅ Quality Status: ENFORCED**

- ✅ **Clean Architecture patterns** implemented consistently
- ✅ **Domain-Driven Design** with proper bounded contexts
- ✅ **CQRS implementation** for command/query separation
- ✅ **Event-driven communication** between services
- ✅ **Type-safe error handling** with FlextResult pattern

### **📊 Architecture Metrics**

| Metric                            | Current | Target | Status         |
| --------------------------------- | ------- | ------ | -------------- |
| **Clean Architecture Compliance** | 85%     | 95%    | 🔄 In Progress |
| **Layer Dependency Violations**   | 0       | 0      | ✅ Complete    |
| **Cross-Infrastructure Imports**  | 0       | 0      | ✅ Complete    |
| **CQRS Pattern Implementation**   | 70%     | 90%    | 🔄 In Progress |
| **Event Sourcing Coverage**       | 40%     | 80%    | 🔄 In Progress |

---

## 🎓 Architectural Principles

### **Core Design Principles**

1. **Clean Architecture Enforcement**

   - Strict layer separation with dependency inversion
   - Domain layer isolation from external concerns
   - Interface-based design with port/adapter pattern

2. **Domain-Driven Design**

   - Rich domain models with business logic
   - Bounded contexts for complex domains
   - Ubiquitous language across team communication

3. **CQRS + Event Sourcing**

   - Command/query separation for scalability
   - Event-driven communication between services
   - Eventual consistency with domain events

4. **Specialization over Duplication**

   - Each project serves distinct business purposes
   - Shared functionality consolidated in appropriate layers
   - Clear boundaries between similar projects

5. **Library vs Service Separation**
   - Libraries provide reusable functionality
   - Services provide runtime execution and orchestration
   - Clear distinction in deployment and lifecycle

### **Quality Assurance Principles**

1. **Zero Tolerance Quality Gates**

   - All architecture violations must be fixed
   - No exceptions for convenience or speed
   - Automated validation in CI/CD pipelines

2. **Dependency Management**

   - Explicit dependency declarations
   - Regular dependency audits and updates
   - No circular dependencies allowed

3. **Documentation and Communication**
   - Architecture decisions recorded and communicated
   - Regular architecture reviews and validation
   - Clear escalation path for architectural questions

---

## 🔮 Future Architecture Evolution

### **Planned Enhancements**

#### **Enhanced Event Sourcing (Q4 2025)**

- Complete event store implementation with persistence
- Event replay capabilities for system recovery
- Advanced event versioning and migration strategies

#### **Advanced CQRS (Q1 2026)**

- Query bus implementation with optimization
- Command/query middleware pipeline
- Advanced caching strategies for read models

#### **Microservices Evolution (Q2 2026)**

- Service mesh integration (Istio/Linkerd)
- Advanced service discovery and load balancing
- Distributed transaction patterns

#### **Performance Optimization (Q3 2026)**

- Advanced caching strategies across layers
- Database query optimization and indexing
- Horizontal scaling patterns for high throughput

---

**Architecture Version**: 2.0.0  
**Next Review**: 2025-09-02  
**Status**: PRODUCTION READY  
**Maintained By**: FLEXT Architecture Team

This document serves as the **SOURCE OF TRUTH** for FLEXT ecosystem architecture. All architectural decisions and changes must be reflected in this document and communicated to the development team.
