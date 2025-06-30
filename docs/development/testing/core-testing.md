# Core Domain Testing Guide

> **Function**: Domain layer testing strategies and patterns | **Audience**: Domain developers, QA engineers | **Status**: Stable

[![Testing](https://img.shields.io/badge/testing-core_domain-blue.svg)](./index.md)
[![Domain](https://img.shields.io/badge/layer-domain-purple.svg)](../../architecture/core-domain-layer.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT_0.4.0-orange.svg)](../../index.md)

**Comprehensive guide for testing FLEXT Framework core domain components with business logic validation**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Testing Hub](./index.md) → **📄 Current**: Core Testing

### **📍 Learning Path Position**

```
[Testing Hub](./index.md) → **[CORE TESTING]** → [Adapters Testing](./adapters-testing.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Testing Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Related**: [Core API Reference](../../api-reference/framework/core-api-reference-validated.md)

---

## 📋 **Overview**

Core domain testing ensures the correctness and integrity of business logic, domain entities, value objects, and domain services in the FLEXT Framework.

### **Testing Objectives**

- **Business Logic Correctness**: Verify domain calculations and rules
- **Entity Behavior**: Test entity lifecycle and state transitions
- **Value Object Validation**: Ensure immutability and validation rules
- **Domain Service Logic**: Test orchestration and coordination
- **Business Rule Enforcement**: Verify constraint enforcement
- **Domain Event Handling**: Test event publication and handling

### **Testing Scope**

```python
# Core domain components being tested
from flext.core.entities import Entity, AggregateRoot
from flext.core.domain.value_objects import ValueObject
from flext.core.services import DomainService
from flext.core.events import DomainEvent
```

---

## 🧪 **Testing Framework Integration**

### **Domain Test Structure**

Based on validated implementation in `/flext/src/flext/testing/`:

```python
from flext.testing.engines import ComprehensiveTestEngine
from flext.core.entities import Entity

class TestDomainEntity:
    def setup_method(self):
        self.test_engine = ComprehensiveTestEngine()

    def test_entity_immutability(self):
        """Test entity follows immutable patterns."""
        customer = CustomerEntity(name="John", email="john@example.com")
        updated_customer = customer.change_email("new@example.com")

        # Original remains unchanged
        assert customer.email == "john@example.com"
        # New instance has updated data
        assert updated_customer.email == "new@example.com"
```

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Testing Hub](./index.md) - Understanding FLEXT testing framework architecture
- [Core API Reference](../../api-reference/framework/core-api-reference-validated.md) - Core domain APIs being tested

### **Next Steps**

- [Adapters Testing](./adapters-testing.md) - Testing adapter implementations
- [Integration Testing](./integration-testing.md) - Testing domain integration with infrastructure
- [Testing Engines](./testing-engines.md) - Advanced testing engine usage

### **Related Topics**

- [Domain Architecture](../../architecture/core-domain-layer.md) - Understanding what you're testing
- [Ports Testing](./ports-testing.md) - Testing port interfaces used by domain
- [Testing Framework Guide](./testing-framework-comprehensive-guide.md) - Complete testing reference

---

**📂 Hub**: [Testing Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
