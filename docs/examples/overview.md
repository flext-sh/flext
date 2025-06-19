# 🎯 FLX Examples Overview

> **Function**: Comprehensive examples guidance and framework demonstrations | **Audience**: All developers, learners | **Status**: Production-Ready

[![Examples](https://img.shields.io/badge/examples-comprehensive-green.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-hexagonal-blue.svg)](../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../index.md)

**Comprehensive guidance for FLX framework examples demonstrating hexagonal architecture, declarative systems, and enterprise-grade patterns - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Examples](./index.md) → **📄 Current**: Examples Overview

### **📍 Learning Path Position**

```
[Examples Hub](./index.md) → **[Examples Overview]** → [Basic Examples](./basic/index.md)
```

## Overview

This document provides comprehensive guidance for understanding and using the FLX framework examples that demonstrate hexagonal architecture, declarative systems, and enterprise-grade patterns.

## Related Documentation

- [Getting Started Guide](../getting-started/) - Basic framework introduction
- [Architecture Overview](../architecture/) - Core architectural principles
- [API Reference](../api-reference/) - Complete API documentation
- [Development Guide](../development/) - Development best practices

## Example Categories

### Basic Usage (`basic/`)

Enhanced examples for getting started with current FLX structure:

- **`quickstart.py`** - Basic FLX usage with enhanced HTTP client, health checks, and structured logging
- **`multi_protocol.py`** - Multi-protocol integration with comprehensive error handling and metrics

### Advanced Patterns (`advanced/`)

Complex scenarios showcasing current framework capabilities:

- **`domain_example.py`** - Enhanced domain modeling with DDD patterns and structured logging
- **`plugin_example.py`** - Creating custom adapters and plugins with current architecture
- **`declarative_example.py`** - Declarative system showcase with mixins and testing framework

## Running Examples

### Environment Setup

```bash
# Set up environment (from project root)
source .venv/bin/activate
export PYTHONPATH=/home/marlonsc/pyauto/flx/src:$PYTHONPATH

# Verify FLX installation
python -c "import flx; print('FLX framework loaded successfully')"
```

### Basic Examples

```bash
# Basic examples
python examples/basic/quickstart.py
python examples/basic/multi_protocol.py

# Advanced examples
python examples/advanced/domain_example.py
python examples/advanced/plugin_example.py
python examples/advanced/declarative_example.py

# Alternative: Run as modules
python -m examples.basic.quickstart
python -m examples.basic.multi_protocol
python -m examples.advanced.domain_example
python -m examples.advanced.plugin_example
python -m examples.advanced.declarative_example
```

## Key Example Implementations

### Enhanced Basic Application

```python
# examples/basic/quickstart.py (current version)
import asyncio
from typing import Any

from flx import ApiClient
from flx.adapters.outbound.http import HttpClientAdapter
from flx.core.logging import FlxLogger

async def main() -> None:
    """Enhanced FLX usage example with current structure."""
    # Setup structured logging
    logger = FlxLogger("flx.examples.quickstart")

    # Create client
    client = ApiClient()

    # Register HTTP adapter with proper configuration
    http_adapter = HttpClientAdapter(
        name="github_api",
        timeout=30.0,
        headers={"Accept": "application/vnd.github.v3+json"},
        max_connections=10
    )
    client.register_adapter("http", http_adapter)

    try:
        async with client:
            # Demonstrate health check
            health = await http_adapter.health_check()
            logger.info("HTTP adapter health check - Status: %s", health.status)

            # HTTP request with comprehensive error handling
            response = await client.http.get("https://api.github.com/users/github")
            logger.info("API response received - Login: %s, Repos: %s, Followers: %s",
                       response.get("login"), response.get("public_repos"), response.get("followers"))

            # Show adapter metrics
            metrics = await http_adapter.get_metrics()
            logger.info("Adapter metrics - Requests: %s, Errors: %s",
                       metrics.get("requests_total"), metrics.get("errors_total"))

    except Exception as e:
        logger.exception("Example failed - Error: %s", str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

### Enhanced Domain-Driven Design

```python
# examples/advanced/domain_example.py (enhanced version)
from flx import AggregateRoot, Entity, DomainEvent, ValueObject
from flx.core.exceptions import BusinessRuleViolationError
from flx.core.logging import FlxLogger

# Enhanced with structured logging
logger = FlxLogger("flx.examples.domain")

# Value Object with validation
class SKU(ValueObject):
    value: str

    @property
    def category(self) -> str:
        return self.value.split("-")[0]

# Entity with business logic
class InventoryItem(Entity):
    sku: SKU
    quantity: int
    location: str
    reserved_quantity: int = 0

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.reserved_quantity

    def reserve(self, quantity: int) -> None:
        if quantity > self.available_quantity:
            raise BusinessRuleViolationError(
                f"Cannot reserve {quantity}, only {self.available_quantity} available",
                rule="inventory.reservation.insufficient"
            )
        self.reserved_quantity += quantity

# Aggregate Root with event handling
class Warehouse(AggregateRoot):
    name: str
    code: str
    items: dict[str, InventoryItem] = {}

    def add_inventory(self, sku: SKU, quantity: int, location: str) -> None:
        # Enhanced business logic with event sourcing
        if sku.value in self.items:
            old_quantity = self.items[sku.value].quantity
            self.items[sku.value].quantity += quantity
            event = InventoryAdjustedEvent(
                aggregate_id=self.id,
                sku=sku.value,
                old_quantity=old_quantity,
                new_quantity=self.items[sku.value].quantity,
                adjustment=quantity,
                reason="RECEIPT"
            )
        else:
            item = InventoryItem(sku=sku, quantity=quantity, location=location)
            self.items[sku.value] = item
            event = InventoryAdjustedEvent(
                aggregate_id=self.id,
                sku=sku.value,
                old_quantity=0,
                new_quantity=quantity,
                adjustment=quantity,
                reason="INITIAL"
            )
        self.add_event(event)

# Domain Event with metadata
class InventoryAdjustedEvent(DomainEvent):
    sku: str
    old_quantity: int
    new_quantity: int
    adjustment: int
    reason: str
```

### Declarative System Example

```python
# examples/advanced/declarative_example.py (new)
from flx import FlxProject, flx_project
from flx.declarative.mixins import (
    FlxApiMixin, FlxDatabaseMixin, FlxHttpClientMixin, FlxIntegrationMixin
)
from flx.declarative.testing import run_full_test_suite, validate_test_coverage

@flx_project
class ECommerceProject(
    FlxProject,
    FlxApiMixin,
    FlxDatabaseMixin,
    FlxHttpClientMixin,
    FlxIntegrationMixin
):
    """E-commerce project with declarative configuration."""

    project_name = "ecommerce-api"
    version = "1.0.0"

    # Auto-configured through mixins
    database_url = "postgresql://user:pass@localhost/ecommerce"
    api_host = "0.0.0.0"
    api_port = 8000
    http_timeout = 30.0

async def main():
    project = ECommerceProject()
    await project.setup()

    # Run comprehensive testing
    test_results = await run_full_test_suite(project)
    coverage_valid = validate_test_coverage(test_results)

    print(f"Project: {project.project_name} v{project.version}")
    print(f"Test coverage valid: {coverage_valid}")
```

## Key Features Demonstrated

### Core Architecture

1. **Enhanced Hexagonal Architecture** - Clear separation with comprehensive lifecycle management
2. **Enhanced Adapter Pattern** - BaseAdapter and EnhancedAdapter with health monitoring
3. **Structured Logging** - FlxLogger integration for observability
4. **Dependency Injection** - Flexible configuration with declarative setup

### Framework Features

5. **Declarative System** - Project setup using `@flx_project` and mixins
6. **Testing Framework** - Comprehensive testing with coverage validation
7. **Health Monitoring** - Built-in health checks and metrics collection
8. **Plugin Architecture** - Enhanced plugin system with proper hook management

### Production Features

9. **Error Handling** - Comprehensive error handling with structured logging
10. **Configuration Management** - Hierarchical configuration with validation
11. **Resource Management** - Proper lifecycle management and cleanup
12. **Performance Monitoring** - Metrics collection and performance tracking

## Configuration Approaches

### Traditional Configuration

```python
# Environment variables with fallbacks
import os

http_adapter = HttpClientAdapter(
    name="api_client",
    timeout=float(os.getenv("HTTP_TIMEOUT", "30.0")),
    max_connections=int(os.getenv("MAX_CONNECTIONS", "100"))
)
```

### Declarative Configuration

```python
# Using mixins and decorators
@flx_project
class MyProject(FlxProject, FlxHttpClientMixin):
    http_timeout = 30.0
    http_max_connections = 100
```

### Enhanced Adapter Configuration

```python
# With validation and defaults
adapter = HttpClientAdapter(
    name="production_api",
    timeout=60.0,
    headers={"User-Agent": "FLX/1.0"},
    verify_ssl=True,
    max_connections=200
)
```

## Testing Examples

### Unit Testing

```bash
# Run unit tests
make test PROJECT=flx
pytest tests/unit/test_adapters.py -v

# Run integration tests
pytest tests/integration/ -v

# Run hexagonal architecture tests
pytest tests/hexagonal/ -v

# Run with coverage
make test-cov
```

### Example Test Implementation

```python
import pytest
from unittest.mock import AsyncMock
from flx.examples.advanced.domain_example import Warehouse, SKU

@pytest.fixture
def warehouse():
    """Test warehouse fixture."""
    return Warehouse(name="Main Warehouse", code="MAIN-001")

async def test_warehouse_inventory_addition(warehouse):
    """Test adding inventory to warehouse."""
    # Arrange
    sku = SKU(value="PROD-001")

    # Act
    warehouse.add_inventory(sku, 100, "A1-01")

    # Assert
    assert sku.value in warehouse.items
    assert warehouse.items[sku.value].quantity == 100
    assert len(warehouse.events) == 1

    # Verify event
    event = warehouse.events[0]
    assert event.sku == "PROD-001"
    assert event.new_quantity == 100
    assert event.reason == "INITIAL"
```

## Common Patterns

### Enhanced Patterns

- **Lifecycle Management** - Proper connection/disconnection with health monitoring
- **Structured Logging** - Consistent logging with metadata throughout the stack
- **Error Handling** - Comprehensive error handling with context and recovery
- **Configuration** - Hierarchical configuration with validation and type safety
- **Testing** - Declarative testing with coverage and metrics

### Production Patterns

- **Health Monitoring** - Built-in health checks and status reporting
- **Metrics Collection** - Performance monitoring and operational insights
- **Circuit Breaker** - Fault tolerance for external service calls
- **Retry Logic** - Configurable retry strategies with exponential backoff
- **Graceful Shutdown** - Proper resource cleanup and connection termination

## Learning Path

### 1. Start with Basics

Run `quickstart.py` to understand current client usage:

- Basic FLX setup and configuration
- HTTP adapter integration
- Health check implementation
- Structured logging patterns

### 2. Multi-Protocol Integration

Explore `multi_protocol.py` for adapter integration:

- Multiple adapter registration
- Protocol-specific configurations
- Error handling across adapters
- Metrics collection patterns

### 3. Domain Modeling

Study `domain_example.py` for DDD patterns:

- Value objects and entities
- Aggregate roots and events
- Business rule validation
- Event sourcing patterns

### 4. Plugin Development

Learn `plugin_example.py` for custom adapters:

- Custom adapter implementation
- Plugin registration and discovery
- Configuration management
- Testing strategies

### 5. Declarative System

Explore `declarative_example.py` for framework features:

- Project configuration with mixins
- Declarative testing frameworks
- Automated setup and teardown
- Coverage validation

### 6. Build Applications

Create your own projects using demonstrated patterns:

- Apply learned patterns to real scenarios
- Implement production-ready configurations
- Add comprehensive testing
- Include monitoring and observability

## Prerequisites

### System Requirements

- **Python 3.13+** (as specified in project requirements)
- **FLX framework** installed with all dependencies
- **Virtual environment** activated (`.venv`)
- **Optional**: External services for testing (PostgreSQL, Redis, etc.)

### Development Environment

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify FLX installation
python -c "import flx; print('FLX framework loaded successfully')"

# Set Python path for examples
export PYTHONPATH=/home/marlonsc/pyauto/flx/src:$PYTHONPATH

# Install development dependencies
pip install -r requirements-dev.txt
```

## Contributing Examples

When adding examples, follow these guidelines:

### 1. Focus and Clarity

- Keep examples focused on demonstrating specific concepts
- Use clear, descriptive variable names
- Include comprehensive comments explaining demonstrated concepts

### 2. Architecture Compliance

- Use current FLX architecture patterns and imports
- Follow hexagonal architecture principles
- Implement proper separation of concerns

### 3. Production Readiness

- Include structured logging with FlxLogger
- Implement comprehensive error handling with proper context
- Show both basic and production-ready configuration approaches

### 4. Testing and Quality

- Include or reference test patterns where applicable
- Implement proper resource management and cleanup
- Add health checks and metrics collection

### 5. Documentation

- Provide clear documentation for each example
- Include usage instructions and prerequisites
- Document configuration options and alternatives

## Architecture Evolution

These examples showcase the evolution of FLX from a basic hexagonal architecture framework to a comprehensive enterprise-grade platform featuring:

### Core Evolution

- **Declarative Configuration** - Simplified project setup and configuration
- **Enhanced Adapters** - Production-ready adapters with comprehensive capabilities
- **Structured Logging** - Consistent observability across all components
- **Testing Framework** - Built-in testing with coverage and metrics

### Enterprise Features

- **Health Monitoring** - Comprehensive health checks and performance monitoring
- **Plugin Architecture** - Enhanced plugin system for extensibility
- **Resource Management** - Proper lifecycle management and cleanup
- **Error Handling** - Production-grade error handling and recovery

### Development Experience

- **Type Safety** - Full type annotations and runtime validation
- **Developer Tools** - Enhanced debugging and development tools
- **Configuration Management** - Hierarchical configuration with validation
- **Testing Support** - Comprehensive testing frameworks and utilities

The examples demonstrate both the foundational patterns and the latest framework capabilities, providing a complete learning path for FLX development from basic concepts to enterprise-grade implementations.

## See Also

- [Quick Start Tutorial](../getting-started/quick-start.md) - Step-by-step framework introduction
- [Architecture Patterns](../architecture/patterns.md) - Detailed architectural guidance
- [Testing Guidelines](../development/testing-guidelines.md) - Comprehensive testing strategies
- [Production Deployment](../deployment/production-guide.md) - Production deployment patterns

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Getting Started Foundation**](../getting-started/index.md) - Framework installation and basic concepts required for running examples
- [**Architecture Understanding**](../architecture/design/unified-architecture-guide.md) - Hexagonal architecture patterns demonstrated in examples
- [**Development Environment Setup**](../development/guides/environment-configuration.md) - Development environment configuration for example execution

### **➡️ Implementation Next Steps**

- [**Basic Examples**](./basic/index.md) - Start with fundamental examples demonstrating core framework features
- [**Real-World Implementations**](./real-world-implementations.md) - Production-verified examples with complete implementation patterns
- [**Oracle Integration Examples**](./oracle-integration-real-examples.md) - Oracle-specific examples demonstrating enterprise integration patterns

### **🔗 Related Implementation Topics**

- [**Testing Examples**](../development/testing/hexagonal-testing-guide.md) - Testing strategies and frameworks demonstrated in example implementations
- [**Infrastructure Examples**](../infrastructure/service-patterns.md) - Infrastructure service patterns and production configurations shown in examples
- [**API Reference Usage**](../api-reference/core-api-reference.md) - Complete API documentation for classes and methods used in examples
- [**Performance Examples**](../optimization/performance/optimization-guide.md) - Performance optimization techniques demonstrated in advanced examples
- [**Security Implementation Examples**](../security/architecture/security-architecture.md) - Security patterns and authentication examples
- [**Deployment Examples**](../deployment/kubernetes-deployment.md) - Production deployment patterns for example applications

---

**📂 Content Document** | **🏠 Parent**: [Examples Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11

**Status**: Production Ready
**Python Support**: 3.13+
