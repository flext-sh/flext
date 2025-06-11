# Basic Examples - Examples

> **Function**: Foundational FLX framework examples and patterns | **Audience**: New developers, beginners | **Status**: Complete

[![Examples](https://img.shields.io/badge/examples-basic-green.svg)](./index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../index.md)

**Foundational examples demonstrating the core concepts and basic usage patterns of the FLX framework's hexagonal architecture**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Hub**: [Examples](./index.md) → **📄 Current**: Basic Examples

### **📍 Learning Path Position**

```
[Examples Hub](./index.md) → **[BASIC EXAMPLES]** → [Advanced Examples](./advanced-examples.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Examples Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Next Step**: [Advanced Examples](./advanced-examples.md)

---

## 📋 **Overview**

The basic examples serve as your entry point to understanding FLX's hexagonal architecture, showcasing core framework patterns and essential integrations.

- **Core Framework Patterns**: Fundamental usage of FLX's client, adapters, and lifecycle management
- **Hexagonal Architecture**: Clear separation between domain logic and infrastructure adapters
- **Production-Ready Patterns**: Best practices for configuration, error handling, and logging
- **Essential Integrations**: HTTP clients, CLI interfaces, and adapter management

## 📁 Examples Structure

### `quickstart.py` - Framework Fundamentals

**Purpose**: Demonstrates minimal yet production-ready FLX setup

- ✅ Basic client configuration and lifecycle management
- ✅ HTTP adapter setup with production configurations
- ✅ Structured logging with FlxLogger
- ✅ Health monitoring and metrics collection
- ✅ Comprehensive error handling and resource cleanup

### `multi_protocol.py` - Multi-Adapter Integration

**Purpose**: Shows how FLX coordinates multiple input/output mechanisms

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

# Verify FLX installation
python -c "import flx; print('FLX framework loaded successfully')"

# Set Python path for examples
export PYTHONPATH=/home/marlonsc/pyauto/flx/src:$PYTHONPATH
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

- Basic FLX client setup and configuration
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
    headers={"User-Agent": "FLX/1.0"},
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
logger = FlxLogger("flx.examples.quickstart")

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

## 🔗 **Cross-References**

### **Prerequisites**

- [Examples Hub](./index.md) - Examples overview and navigation
- [Getting Started](../getting-started/index.md) - Framework fundamentals and installation

### **Next Steps**

- [Advanced Examples](./advanced-examples.md) - Complex patterns and enterprise scenarios
- [Adapter Template](./adapter-template.md) - Ready-to-use adapter development scaffold

### **Related Topics**

- [FLX Architecture](../architecture/index.md) - Hexagonal architecture patterns
- [Development Guidelines](../development/index.md) - Development practices and standards

---

**📂 Hub**: [Examples Hub](./index.md) | **🏠 Root**: [Documentation Home](../index.md) | **Framework**: FLX 0.4.0+
