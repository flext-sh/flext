# FlexCore Architecture - Current State Analysis

**Version**: 0.9.0 | **Status**: Under Refactoring | **Last Updated**: 2025-08-05

This document provides an honest assessment of FlexCore's current architecture, identifying critical violations and implementation gaps.

> ⚠️ **Critical Notice**: FlexCore is currently undergoing major architectural refactoring due to significant violations of Clean Architecture, DDD, CQRS, and Event Sourcing principles. See [Technical Debt Analysis](../technical-debt.md) for detailed issues and remediation plan.

## 🎯 System Overview

### Purpose and Scope

FlexCore serves as the **enterprise runtime container service** and **primary orchestration engine** for the entire FLEXT data integration ecosystem. It bridges high-performance Go services with Python business logic while maintaining strict architectural boundaries.

### Key Responsibilities

- **Plugin Orchestration**: Secure, isolated execution of data processing plugins
- **Event Sourcing**: Immutable event streams with complete audit trails
- **CQRS Implementation**: Separate command and query processing paths
- **Distributed Coordination**: Multi-node coordination via Redis and PostgreSQL
- **Service Integration**: Bridge between Go performance layer and Python business logic

### FLEXT Ecosystem Position

```
┌─────────────────────────────────────────────────────┐
│                FLEXT Ecosystem                      │
├─────────────────────────────────────────────────────┤
│  Singer Ecosystem (15+ projects)                   │
│  ├─ Taps (5): Oracle, LDAP, LDIF, OIC, WMS        │
│  ├─ Targets (5): Oracle, LDAP, LDIF, OIC, WMS     │
│  └─ DBT (4): Transformation projects               │
├─────────────────────────────────────────────────────┤
│  Application Services                               │
│  ├─ flext-api (FastAPI)                           │
│  ├─ flext-auth (Authentication)                   │
│  ├─ flext-web (Web Interface)                     │
│  └─ flext-cli (Command Line Tools)                │
├─────────────────────────────────────────────────────┤
│  🎯 FLEXCORE (THIS PROJECT)                        │
│     Runtime Container & Orchestration Engine       │
├─────────────────────────────────────────────────────┤
│  Infrastructure Services                            │
│  ├─ flext-db-oracle (Database Connectivity)       │
│  ├─ flext-ldap (Directory Services)               │
│  ├─ flext-grpc (Communication Protocols)          │
│  └─ flext-observability (Monitoring)              │
├─────────────────────────────────────────────────────┤
│  Foundation Libraries                               │
│  ├─ flext-core (Python Base Patterns)             │
│  └─ flext-observability (Monitoring Foundation)   │
└─────────────────────────────────────────────────────┘
```

## 🏗️ Current Architecture (Problems Identified)

### Layer Structure (Current Implementation)

```
┌─────────────────────────────────────────────────────┐
│            HTTP Layer (Port 8080)                  │
│         Gin Framework - RESTful API                │
├─────────────────────────────────────────────────────┤
│          Application Layer (VIOLATED)              │
│   ⚠️ HTTP Server directly embedded here             │
│   ⚠️ Direct config dependencies                     │
│   ✅ Basic command/query separation                 │
├─────────────────────────────────────────────────────┤
│            Domain Layer (ANEMIC)                   │
│   ✅ Entities and Aggregates defined               │
│   ⚠️ Lacks rich domain behavior                     │
│   ⚠️ Event sourcing poorly implemented              │
├─────────────────────────────────────────────────────┤
│         Infrastructure Layer (CHAOTIC)             │
│   ❌ 3 different CQRS implementations               │
│   ❌ In-memory event store for production           │
│   ✅ PostgreSQL and Redis integration               │
│   ⚠️ Plugin system lacks security isolation         │
└─────────────────────────────────────────────────────┘
```

### Critical Architecture Violations

#### 1. Clean Architecture Boundary Violations

**Location**: `internal/app/application.go:15-20`

```go
type Application struct {
    config *config.Config     // ❌ Infrastructure dependency
    server *http.Server       // ❌ HTTP in Application layer
    mux    *http.ServeMux     // ❌ Web framework in Application
}
```

**Impact**:

- Impossible to test application logic without HTTP server
- Coupling between business logic and web infrastructure
- Violation of Dependency Inversion Principle

#### 2. Multiple CQRS Implementations

**Implementations Found**:

- `internal/app/commands/command_bus.go` - Generic implementation
- `internal/infrastructure/cqrs/cqrs_bus.go` - SQLite-based implementation
- `internal/infrastructure/command_bus.go` - Function-based implementation

**Impact**:

- Architectural inconsistency and confusion
- Maintenance burden with multiple implementations
- No clear separation of concerns

#### 3. Inadequate Event Sourcing

**Location**: `internal/infrastructure/event_store.go:24-36`

```go
type MemoryEventStore struct {
    events map[string][]EventEntry  // ❌ In-memory for production
    mu     sync.RWMutex              // ❌ Single-node only
}

func (ar *AggregateRoot[T]) ClearEvents() {
    ar.domainEvents = make([]DomainEvent, 0)  // ❌ Mutable events
}
```

**Impact**:

- Data loss on service restart
- No replay capability
- Events are mutable (violates Event Sourcing principles)

#### 4. Plugin System Security Gaps

**Issues**:

- No process isolation between plugins
- No resource limits or sandboxing
- Shared memory space allows cross-plugin interference
- No capability-based security model

## 📊 Architecture Compliance Assessment

### Current State Analysis

| Pattern                  | Compliance | Issues                                                        |
| ------------------------ | ---------- | ------------------------------------------------------------- |
| **Clean Architecture**   | 30%        | HTTP in Application layer, direct infrastructure dependencies |
| **Domain-Driven Design** | 40%        | Anemic domain model, weak aggregate boundaries                |
| **CQRS**                 | 25%        | Multiple conflicting implementations, no clear separation     |
| **Event Sourcing**       | 20%        | In-memory store, mutable events, no replay capability         |
| **Plugin Architecture**  | 35%        | No isolation, security gaps, resource management missing      |

### Critical Blockers for Production

1. **Data Loss Risk**: In-memory event store loses all data on restart
2. **Security Vulnerabilities**: Plugin system has no isolation
3. **Architectural Chaos**: Multiple CQRS implementations create confusion
4. **Testing Impossibility**: HTTP server embedded in application layer

## 🎯 Immediate Actions Required

### Phase 1: Critical Architecture Fixes (Weeks 1-2)

1. **Move HTTP Server to Infrastructure Layer**

   - Extract HTTP server from Application struct
   - Create proper adapter interfaces
   - Implement dependency injection

2. **Unify CQRS Implementation**

   - Choose single implementation strategy
   - Remove conflicting implementations
   - Implement proper type safety

3. **Fix Event Sourcing**
   - Replace in-memory store with PostgreSQL
   - Make events immutable
   - Add replay capability

### Phase 2: Domain Enhancement (Weeks 3-4)

1. **Implement Rich Domain Model**

   - Add business logic to entities
   - Create domain services
   - Define aggregate boundaries

2. **Secure Plugin System**
   - Add process isolation
   - Implement resource limits
   - Add security sandboxing

## ⚠️ Production Readiness Status

### **Current Status: NOT PRODUCTION READY**

**Critical Blockers**:

- Data loss on restart (in-memory event store)
- Security vulnerabilities in plugin system
- Architectural violations make system untestable
- Multiple implementations create maintenance burden

**Estimated Time to Production Readiness**: 8-12 weeks with dedicated team

---

This analysis is based on actual source code inspection and represents the honest current state of the FlexCore architecture.
