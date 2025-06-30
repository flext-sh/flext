# 🌱 Basic Examples - FLEXT Framework Fundamentals

> **Document Type**: Example Collection | **Audience**: New developers, framework beginners | **Scope**: Foundational FLEXT Framework patterns

[![Examples](https://img.shields.io/badge/examples-basic-green.svg)](../index.md)
[![Framework](https://img.shields.io/badge/framework-FLEXT%200.4.0-blue.svg)](../../index.md)
[![Beginner](https://img.shields.io/badge/level-beginner-brightgreen.svg)](../../getting-started/index.md)

**Foundational examples demonstrating core FLEXT Framework concepts and hexagonal architecture patterns**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Examples](../index.md) → **📂 Basic**: [Index](./index.md) → **📂 Current**: Basic Examples

## 📋 Overview

The basic examples serve as your entry point to understanding FLEXT's hexagonal architecture, showcasing:

- **Core Framework Patterns**: Fundamental usage of FLEXT's client, adapters, and lifecycle management
- **Hexagonal Architecture**: Clear separation between domain logic and infrastructure adapters
- **Production-Ready Patterns**: Best practices for configuration, error handling, and logging
- **Essential Integrations**: HTTP clients, CLI interfaces, and adapter management

## 📁 Examples Structure

### `quickstart.py` - Framework Fundamentals

**Purpose**: Demonstrates minimal yet production-ready FLEXT setup

- ✅ Basic client configuration and lifecycle management
- ✅ HTTP adapter setup with production configurations
- ✅ Structured logging with FlextLogger
- ✅ Health monitoring and metrics collection
- ✅ Comprehensive error handling and resource cleanup

### `multi_protocol.py` - Multi-Adapter Integration

**Purpose**: Shows how FLEXT coordinates multiple input/output mechanisms

- ✅ Multiple adapter registration (HTTP, CLI, Database)
- ✅ Adapter lifecycle coordination and dependency management
- ✅ Cross-adapter communication patterns
- ✅ Configuration management for multiple services
- ✅ Advanced error handling and fallback strategies

### `quickstart_unified.py` - Modern Unified API

**Purpose**: Demonstrates the latest unified API patterns

- ✅ Simplified client setup with unified interfaces
- ✅ Modern async/await patterns throughout
- ✅ Enhanced configuration and validation
- ✅ Built-in observability and monitoring

## 🚀 Running Examples

### Prerequisites

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify FLEXT installation
python -c "import flext; print('FLEXT framework loaded successfully')"

# Set Python path for examples
export PYTHONPATH=/home/marlonsc/pyauto/flext/src:$PYTHONPATH
```

### Execution Methods

```bash
# Method 1: Direct execution
python examples/basic/quickstart.py
python examples/basic/multi_protocol.py
python examples/basic/quickstart_unified.py

# Method 2: Module execution (recommended)
python -m examples.basic.quickstart
python -m examples.basic.multi_protocol
python -m examples.basic.quickstart_unified

# Method 3: With custom configuration
ENVIRONMENT=development python examples/basic/quickstart.py
FLX_LOG_LEVEL=DEBUG python examples/basic/multi_protocol.py
```

## 🎯 Learning Path

### 1. **Start Here**: `quickstart.py`

Begin with the quickstart example to understand:

- Basic FLEXT client setup and configuration
- HTTP adapter integration with production settings
- Structured logging and observability patterns
- Proper resource management and cleanup
- Error handling and recovery strategies

### 2. **Multi-Protocol**: `multi_protocol.py`

Progress to multi-protocol integration:

- Managing multiple adapters simultaneously
- Adapter lifecycle coordination and dependencies
- Cross-adapter communication patterns
- Configuration strategies for complex setups
- Advanced error handling across multiple services

### 3. **Modern Patterns**: `quickstart_unified.py`

Explore the latest framework capabilities:

- Unified API patterns and simplified interfaces
- Modern async patterns and best practices
- Enhanced configuration and validation
- Built-in monitoring and health checks

## 🔧 Key Concepts Demonstrated

### Hexagonal Architecture Patterns

- **Inbound Ports**: CLI interfaces and API endpoints
- **Outbound Ports**: HTTP clients, database connections, external services
- **Domain Logic**: Business logic isolated from infrastructure concerns
- **Adapter Management**: Proper lifecycle and dependency coordination

### Production-Ready Features

- **Structured Logging**: Consistent logging with metadata and context
- **Health Monitoring**: Built-in health checks and status reporting
- **Metrics Collection**: Performance monitoring and operational insights
- **Error Handling**: Comprehensive error handling with proper recovery
- **Resource Management**: Proper connection lifecycle and cleanup

### Configuration Strategies

- **Environment-Based**: Configuration through environment variables
- **Hierarchical Config**: Layered configuration with validation
- **Type Safety**: Strongly-typed configuration with validation
- **Default Values**: Sensible defaults with override capabilities

## 💡 Best Practices Shown

### 1. **Client Setup**

```python
# Production-ready client configuration
client = ApiClient()

# Structured adapter registration with monitoring
http_adapter = HttpClientAdapter(
    name="production_api",
    timeout=30.0,
    headers={"User-Agent": "FLEXT/1.0"},
    max_connections=10,
    enable_metrics=True
)
client.register_adapter("http", http_adapter)
```

### 2. **Lifecycle Management**

```python
# Proper async context management
async with client:
    # Health check before operations
    health = await http_adapter.health_check()
    logger.info("Adapter health", extra=health)

    # Business operations
    response = await client.http.get(url)

    # Metrics collection
    metrics = await http_adapter.get_metrics()
```

### 3. **Error Handling**

```python
try:
    async with client:
        result = await business_operation()
except AdapterConnectionError as e:
    logger.error("Connection failed", extra={
        "adapter": e.adapter_name,
        "error": str(e)
    })
    # Implement fallback strategy
except Exception as e:
    logger.exception("Unexpected error", extra={
        "operation": "business_operation",
        "error_type": type(e).__name__
    })
    raise
```

### 4. **Structured Logging**

```python
# Initialize structured logger
logger = FlextLogger("flext.examples.quickstart")

# Log with structured metadata
logger.info("Operation completed", extra={
    "duration_ms": duration,
    "records_processed": count,
    "status": "success"
})
```

## 🔍 Code Quality Indicators

### Architecture Compliance

- ✅ Clean separation of concerns
- ✅ Dependency injection patterns
- ✅ Interface-based programming
- ✅ Proper abstraction layers

### Production Readiness

- ✅ Comprehensive error handling
- ✅ Structured logging throughout
- ✅ Health monitoring integration
- ✅ Metrics collection and reporting
- ✅ Proper resource cleanup

### Code Quality

- ✅ Type hints and validation
- ✅ Async/await patterns
- ✅ Configuration management
- ✅ Documentation and comments

## 🧪 Testing the Examples

```bash
# Run with test mode for validation
TEST_MODE=true python examples/basic/quickstart.py

# Enable debug logging for troubleshooting
FLX_LOG_LEVEL=DEBUG python examples/basic/multi_protocol.py

# Validate configuration without execution
python -c "
from examples.basic.quickstart import main
import asyncio
# Configuration validation only
"
```

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Getting Started Hub](../../getting-started/index.md) - Framework installation and basic concepts required to run examples
- [Architecture Hub](../../architecture/index.md) - Understanding hexagonal architecture patterns demonstrated in examples
- [Examples Hub](../index.md) - Examples navigation and overview for accessing basic framework patterns

### **➡️ Next Steps**

- [Advanced Examples](../advanced/index.md) - Complex scenarios building on basic framework patterns
- [Oracle Real Examples](../oracle-integration-real-examples.md) - Real Oracle integration patterns using basic concepts
- [Development Hub](../../development/index.md) - Development practices for implementing patterns shown in examples

### **🔗 Related Sections**

- [API Reference Hub](../../api-reference/index.md) - Complete API documentation for classes and methods used in examples
- [Guides Hub](../../guides/index.md) - Implementation tutorials expanding on example concepts and patterns
- [Infrastructure Hub](../../infrastructure/index.md) - Infrastructure service patterns demonstrated in framework examples
- [Testing Guide](../../development/testing/index.md) - Testing strategies for applications based on these example patterns

---

**📂 Examples**: [Basic Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
