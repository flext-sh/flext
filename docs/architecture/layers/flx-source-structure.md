# 📁 FLEXT Source Structure - Architecture Guide

> **Function**: Source code organization and hexagonal architecture implementation | **Audience**: Developers, Architects | **Status**: Stable

[![Structure](https://img.shields.io/badge/structure-hexagonal-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-validated-green.svg)](../index.md)
[![Organization](https://img.shields.io/badge/organization-DDD-orange.svg)](./core-domain-layer.md)

**Complete guide to FLEXT Framework source code organization following hexagonal architecture and domain-driven design principles**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Architecture Hub](../index.md) → **📂 Layers**: [Layers Hub](./index.md) → **📄 Current**: FLEXT Source Structure

### **📍 Learning Path Position**

```
[Architecture Hub](../index.md) → **[Source Structure]** → [Core Domain Layer](./core-domain-layer.md)
```

## 🎯 **Quick Links**

- **📂 Layers Hub**: [Layers Hub](./index.md)
- **🏛️ Architecture Root**: [Architecture Hub](../index.md)
- **🏠 Documentation Root**: [Documentation Home](../../index.md)
- **🔗 Related**: [Core Domain Layer](./core-domain-layer.md)

---

## 📋 **Overview**

This is the main source directory for the FLEXT framework, organized following Hexagonal Architecture principles with clear separation of concerns and dependency management.

## Directory Structure

```
flext/
├── core/       # Domain layer (pure business logic)
├── ports/      # Port interfaces (contracts)
├── adapters/   # Adapter implementations
├── infra/      # Infrastructure services
├── plugins/    # Plugin system
└── app/        # Application layer
```

## Architecture Layers

### 1. Core Domain (`core/`)

The heart of the application containing pure business logic:

- Entities, Value Objects, Aggregates
- Domain Events and Commands
- Domain Services
- No external dependencies

### 2. Ports (`ports/`)

Interface definitions that connect layers:

- Inbound ports (driven by external actors)
- Outbound ports (drive external systems)
- Pure abstractions using Python protocols

### 3. Adapters (`adapters/`)

Concrete implementations of ports:

- Inbound adapters (CLI, API, event consumers)
- Outbound adapters (database, cache, HTTP clients)
- Bidirectional plugin adapters

### 4. Infrastructure (`infra/`)

Supporting services and utilities:

- Async messaging (Dramatiq)
- Caching with multiple backends
- Configuration management
- Database infrastructure (SQLAlchemy)
- Runtime management

### 5. Plugins (`plugins/`)

Extensibility layer using Pluggy:

- Plugin interfaces and hooks
- Plugin manager and registry
- Dynamic adapter loading

## Key Design Principles

1. **Dependency Rule**: Dependencies point inward (infra → adapters → ports → core)
2. **Isolation**: Domain logic is completely isolated from infrastructure
3. **Testability**: Each layer can be tested independently
4. **Flexibility**: Easy to swap implementations via ports/adapters
5. **Extensibility**: Plugin system for adding functionality

## Quick Navigation

- Start with `core/` to understand the domain
- Check `ports/` for available interfaces
- See `adapters/` for implementation examples
- Use `infra/` services in your adapters
- Extend via `plugins/` for custom functionality

## 📈 **Development Guidelines**

### **Architecture Rules**

1. **Domain Purity**: Domain logic goes in `core/` only - no infrastructure dependencies
2. **Interface First**: Define interfaces in `ports/` before implementing in `adapters/`
3. **Single Responsibility**: Keep adapters focused on single responsibilities
4. **Reuse Infrastructure**: Use infrastructure services, don't reinvent wheels
5. **Plugin Extension**: Consider plugins for optional features and extensibility

### **Code Organization Patterns**

```python
# Correct: Domain in core, interface in ports, implementation in adapters
# /flext/src/flext/core/entities.py
class Customer(Entity):
    """Pure domain entity."""
    pass

# /flext/src/flext/ports/repository.py
class CustomerRepository(Protocol):
    """Repository interface."""
    async def save(self, customer: Customer) -> None: ...

# /flext/src/flext/adapters/database/customer_repository.py
class PostgresCustomerRepository:
    """Concrete repository implementation."""
    async def save(self, customer: Customer) -> None:
        # Database-specific implementation
        pass
```

### **Dependency Management**

```python
# Dependencies flow inward: infra → adapters → ports → core
# Core depends on nothing
# Ports depend only on core
# Adapters depend on ports and core
# Infrastructure provides services to adapters
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Hub](../index.md) - Understanding hexagonal architecture principles and layer separation
- [Getting Started Guide](../../getting-started/index.md) - Basic FLEXT Framework concepts before diving into source structure

### **Next Steps**

- [Core Domain Layer](./core-domain-layer.md) - Detailed domain layer implementation patterns
- [Application Layer](./application-layer.md) - Application services that orchestrate domain objects
- [Ports and Adapters](../ports/index.md) - Interface definitions and adapter implementations

### **Related Topics**

- [Infrastructure Architecture](../infrastructure/index.md) - Infrastructure services supporting the framework
- [Development Standards](../../development/standards/standardization-plan.md) - Code quality standards for all layers
- [Testing Strategies](../../development/testing/index.md) - Testing patterns for each architectural layer
- [Advanced Patterns](../patterns/index.md) - Advanced architectural patterns building on this foundation

---

## 🆘 **Troubleshooting**

### **Common Architecture Violations**

**Issue**: Domain code importing infrastructure dependencies
**Solution**: Move infrastructure concerns to adapters, use dependency injection
**Prevention**: Enforce dependency rules with import analysis

### **Circular Dependencies**

**Issue**: Layers depending on each other in cycles
**Solution**: Introduce interfaces in ports layer, use dependency inversion
**Prevention**: Follow strict layering with inward-pointing dependencies

---

**📂 Hub**: [Layers Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
