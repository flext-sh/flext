# 🎯 Core APIs Hub - Domain & Business Logic

> **Function**: Core domain and business logic APIs | **Audience**: Backend developers, domain experts | **Status**: ✅ Source Validated

[![Core APIs](https://img.shields.io/badge/core-domain_apis-green.svg)](./base-classes.md)
[![DDD](https://img.shields.io/badge/ddd-domain_driven-blue.svg)](./entities.md)
[![Source Validated](https://img.shields.io/badge/source-validated-green.svg)](#source-validation)
[![Type Safety](https://img.shields.io/badge/types-strict-purple.svg)](./events.md)

**Core domain APIs for FLX Framework 0.4.0+ implementing Domain-Driven Design with complete source validation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Section**: [API Reference](../index.md) → **📄 Current**: Core APIs Hub

### **📍 Learning Path Position**

```
[API Reference Hub](../index.md) → **[CORE APIS HUB]** → [Adapters APIs](../adapters/index.md)
```

## 🎯 **Quick Links**

- **📂 Parent Hub**: [API Reference Hub](../index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🎯 Base Classes**: [Base Classes API](./base-classes.md)

---

## 📊 **Overview**

The Core APIs Hub provides complete domain and business logic API documentation for FLX Framework 0.4.0+. All APIs implement Domain-Driven Design principles with complete isolation from infrastructure concerns and are validated against actual source code.

### **Core API Categories**

| **API Documentation**                 | **Domain Area** | **Validation**   | **Status**    | **Key Features**                         |
| ------------------------------------- | --------------- | ---------------- | ------------- | ---------------------------------------- |
| **[Base Classes](./base-classes.md)** | Foundation      | Source Validated | ✅ Production | DomainObject, Entity, AggregateRoot      |
| **[Entities](./entities.md)**         | Domain Entities | Source Validated | ✅ Production | Business logic, identity, lifecycle      |
| **[Events](./events.md)**             | Domain Events   | Source Validated | ✅ Production | Event-driven architecture, state changes |

### **🚀 Core API Features**

- **Domain-Driven Design**: Pure domain logic isolation
- **Source Validation**: Validated against `/flx/src/flx/core/`
- **Type Safety**: Strict Python 3.13+ annotations with Pydantic
- **Event-Driven**: Complete domain event system
- **SOLID Principles**: Enterprise architecture patterns

## 🎓 **Learning Paths**

### **🆕 New Domain Developers**

1. **Foundation**: [Base Classes](./base-classes.md)
2. **Core Concepts**: [Entities](./entities.md)
3. **Event System**: [Events](./events.md)

### **🏗️ Domain Experts**

1. **Advanced Entities**: [Entities](./entities.md)
2. **Event Architecture**: [Events](./events.md)
3. **Domain Patterns**: [Base Classes](./base-classes.md)

## 🔗 **Cross-References**

### **Prerequisites**

- [API Reference Hub](../index.md) - Complete API documentation overview
- [Architecture Hub](../../architecture/index.md) - Domain-driven design patterns
- [Getting Started Hub](../../getting-started/index.md) - Framework installation

### **Next Steps**

- [Framework APIs](../framework/index.md) - Framework-level APIs using core domain
- [Adapters APIs](../adapters/index.md) - Integration adapters built on core domain
- [Examples Hub](../../examples/index.md) - Domain implementation examples

### **Related Topics**

- [Development Testing](../../development/testing/index.md) - Domain testing strategies
- [Architecture Patterns](../../architecture/patterns/index.md) - Domain design patterns
- [Guides Hub](../../guides/index.md) - Implementation guides using core APIs

---

## 📊 **Source Validation**

- **Validation Source**: `/flx/src/flx/core/` codebase
- **Coverage**: Domain APIs (100%)
- **DDD Compliance**: Complete domain isolation
- **Last Validation**: 2025-06-11

---

**📂 Hub**: [Core APIs Hub](#) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
