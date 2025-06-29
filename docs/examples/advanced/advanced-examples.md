# Advanced Examples - Enterprise-Grade FLX Patterns

This directory showcases sophisticated architectural patterns and enterprise-grade implementations using the FLX framework's advanced capabilities.

## 🏗️ Architecture Focus

The advanced examples demonstrate enterprise-level patterns for:

- **Domain-Driven Design (DDD)**: Rich domain models with complex business logic
- **Event-Driven Architecture**: Event sourcing and CQRS patterns
- **Plugin Extensibility**: Custom adapter development and plugin systems
- **Declarative Configuration**: Modern configuration-driven development
- **Enterprise Integration**: Complex adapter coordination and orchestration

## 📁 Examples Structure

### `domain_example.py` - Domain-Driven Design Excellence

**Enterprise DDD Implementation**

- 🎯 **Rich Domain Models**: Complex aggregates with business invariants
- 🔄 **Event Sourcing**: Domain events and event-driven workflows
- 📊 **CQRS Patterns**: Command and query responsibility segregation
- 🏛️ **Repository Pattern**: Data access abstraction with Unit of Work
- ⚡ **Business Rules Engine**: Complex validation and business logic
- 📈 **Performance Monitoring**: Domain-level metrics and observability

### `plugin_example.py` - Custom Adapter Development

**Advanced Plugin Architecture**

- 🔌 **Plugin Lifecycle**: Complete plugin development workflow
- 🎣 **Hook System**: Event-driven plugin integration
- ⚙️ **Configuration Management**: Plugin-specific configuration patterns
- 🧪 **Plugin Testing**: Comprehensive testing strategies
- 📦 **Distribution**: Plugin packaging and deployment
- 🔒 **Security**: Plugin isolation and security patterns

### `declarative_example.py` - Modern Declarative Patterns

**Configuration-Driven Development**

- 🎨 **Declarative Setup**: `@flext_project` decorator patterns
- 🧩 **Mixin Architecture**: Composable functionality mixins
- 🧪 **Testing Framework**: Integrated testing with coverage
- 📊 **Metrics Integration**: Built-in performance monitoring
- 🔧 **Configuration Validation**: Type-safe configuration management
- 🚀 **Rapid Development**: Zero-boilerplate application setup

## 🚀 Running Examples

### Prerequisites

```bash
# Ensure all dependencies are installed
source .venv/bin/activate
pip install -e . --no-deps

# Verify advanced features are available
python -c "
import flext
from flext.declarative import FlxProject
from flext.core.events import DomainEvent
print('Advanced FLX features loaded successfully')
"

# Set up environment
export PYTHONPATH=/home/marlonsc/pyauto/flext/src:$PYTHONPATH
export ENVIRONMENT=development
```

### Execution Methods

```bash
# Method 1: Direct execution with enhanced logging
FLX_LOG_LEVEL=DEBUG python examples/advanced/domain_example.py
FLX_LOG_LEVEL=INFO python examples/advanced/plugin_example.py
FLX_LOG_LEVEL=DEBUG python examples/advanced/declarative_example.py

# Method 2: Module execution (recommended for imports)
python -m examples.advanced.domain_example
python -m examples.advanced.plugin_example
python -m examples.advanced.declarative_example

# Method 3: Interactive exploration
python -i examples/advanced/domain_example.py
# >>> warehouse.add_inventory(SKU("LAPTOP-001"), 50, "A1-B2")
# >>> print(warehouse.events)
```

## 🎯 Learning Path & Progression

### 1. **Domain Mastery**: `domain_example.py`

**Prerequisites**: Basic FLX knowledge, understanding of DDD concepts

**Learning Objectives**:

- Master complex aggregate design patterns
- Implement event-driven domain logic
- Apply CQRS and event sourcing patterns
- Design repository and Unit of Work patterns
- Build comprehensive business rule engines

**Key Concepts**:

```python
# Rich aggregate with business logic
class Warehouse(AggregateRoot):
    def process_order(self, order: Order) -> OrderResult:
        # Complex business logic with events
        if not self.can_fulfill_order(order):
            raise InsufficientInventoryError(order.id)

        # Generate domain events
        self.add_event(OrderProcessingStartedEvent(
            aggregate_id=self.id,
            order_id=order.id,
            items=order.items
        ))

        return self._allocate_inventory(order)
```

### 2. **Plugin Development**: `plugin_example.py`

**Prerequisites**: Understanding of FLX adapters and dependency injection

**Learning Objectives**:

- Design extensible plugin architectures
- Implement hook-based integration systems
- Create production-ready custom adapters
- Master plugin lifecycle management
- Build secure plugin isolation patterns

**Key Concepts**:

```python
# Custom adapter with plugin capabilities
class CustomProtocolAdapter(BaseAdapter):
    """Enterprise-grade custom adapter implementation."""

    def __init__(self, config: CustomProtocolConfig):
        super().__init__(config)
        self.hooks = PluginHookRegistry()
        self.security = PluginSecurityManager()

    async def process_with_plugins(self, data: Any) -> Any:
        # Plugin hook integration
        data = await self.hooks.execute("pre_process", data)
        result = await self._core_processing(data)
        return await self.hooks.execute("post_process", result)
```

### 3. **Declarative Mastery**: `declarative_example.py`

**Prerequisites**: Familiarity with modern Python patterns and decorators

**Learning Objectives**:

- Master declarative configuration patterns
- Implement mixin-based architecture design
- Integrate comprehensive testing frameworks
- Build observable applications with metrics
- Design zero-configuration deployment patterns

**Key Concepts**:

```python
# Declarative project setup with mixins
@flext_project
class EnterpriseApplication(
    FlxProject,
    FlxDatabaseMixin,
    FlxHttpClientMixin,
    FlxMonitoringMixin,
    FlxSecurityMixin
):
    """Enterprise application with declarative configuration."""

    # Auto-configured through mixins
    database_url = "postgresql://localhost/enterprise"
    monitoring_enabled = True
    security_level = "enterprise"
```

## 🔧 Advanced Patterns Demonstrated

### Domain-Driven Design Patterns

- **Strategic Design**: Bounded contexts and domain modeling
- **Tactical Patterns**: Aggregates, entities, value objects, and services
- **Event Sourcing**: Event streams and aggregate reconstruction
- **CQRS**: Command-query separation with read/write models
- **Saga Patterns**: Long-running business processes

### Enterprise Architecture Patterns

- **Hexagonal Architecture**: Advanced port-adapter patterns
- **Event-Driven Architecture**: Asynchronous event processing
- **Microservices Integration**: Service mesh and communication patterns
- **Plugin Architecture**: Extensible system design
- **Configuration Management**: Environment-specific configurations

### Performance & Scalability Patterns

- **Async Processing**: Non-blocking I/O and concurrent operations
- **Caching Strategies**: Multi-level caching with invalidation
- **Connection Pooling**: Resource management and optimization
- **Batch Processing**: Efficient bulk operations
- **Monitoring & Observability**: Comprehensive metrics and tracing

## 💡 Production-Ready Features

### 1. **Advanced Error Handling**

```python
# Comprehensive error handling with context
try:
    async with transaction:
        result = await complex_business_operation(order)
        await publish_domain_events(result.events)
except BusinessRuleViolationError as e:
    logger.warning("Business rule violated", extra={
        "rule": e.rule_name,
        "context": e.context,
        "suggested_action": e.recovery_action
    })
    await handle_business_exception(e)
except ConcurrencyError as e:
    logger.info("Concurrent modification detected", extra={
        "aggregate_id": e.aggregate_id,
        "expected_version": e.expected_version,
        "actual_version": e.actual_version
    })
    await retry_with_fresh_aggregate(e.aggregate_id)
```

### 2. **Enterprise Monitoring**

```python
# Domain-level metrics and observability
class OrderProcessingService(DomainService):
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics

    @self.metrics.timer("order_processing_duration")
    @self.metrics.counter("orders_processed")
    async def process_order(self, order: Order) -> OrderResult:
        with self.metrics.context(order_id=order.id):
            return await self._execute_order_processing(order)
```

### 3. **Plugin Security**

```python
# Secure plugin isolation
class SecurePluginManager:
    def __init__(self, security_policy: SecurityPolicy):
        self.sandbox = PluginSandbox(security_policy)
        self.validator = PluginValidator()

    async def load_plugin(self, plugin_path: Path) -> Plugin:
        # Validate plugin security
        await self.validator.validate_plugin_signature(plugin_path)

        # Load in secure sandbox
        return await self.sandbox.load_isolated_plugin(plugin_path)
```

## 🧪 Testing Advanced Examples

### Domain Testing

```bash
# Test domain logic with event verification
python -m pytest examples/advanced/test_domain_example.py -v
python -m pytest examples/advanced/test_domain_example.py::test_aggregate_event_sourcing -s

# Test business rules and invariants
python -m pytest examples/advanced/test_domain_example.py::test_business_rules -v
```

### Plugin Testing

```bash
# Test plugin lifecycle and integration
python -m pytest examples/advanced/test_plugin_example.py -v
python -m pytest examples/advanced/test_plugin_example.py::test_plugin_security -s

# Test hook system and plugin communication
python -m pytest examples/advanced/test_plugin_example.py::test_hook_system -v
```

### Declarative Testing

```bash
# Test declarative configuration and mixins
python -m pytest examples/advanced/test_declarative_example.py -v

# Test integrated testing framework
python -m pytest examples/advanced/test_declarative_example.py::test_testing_framework -v
```

## 🔍 Performance Benchmarking

```bash
# Benchmark domain operations
python -m examples.advanced.domain_example --benchmark

# Benchmark plugin performance
python -m examples.advanced.plugin_example --performance-test

# Benchmark declarative setup overhead
python -m examples.advanced.declarative_example --benchmark-setup
```

## 🚦 Next Steps

After mastering the advanced examples:

1. **Enterprise Deployment**: Study production deployment patterns
2. **Microservices**: Build distributed systems with FLX
3. **Event Streaming**: Implement event-driven microservices
4. **Cloud Integration**: Deploy to cloud platforms with observability
5. **Custom Framework**: Build domain-specific frameworks on FLX

## 📚 Related Documentation

- [Domain-Driven Design Guide](../../docs/guides/domain-driven-design.md)
- [Plugin Development Guide](../../docs/guides/plugin-development.md)
- [Event-Driven Architecture](../../docs/architecture/event-driven.md)
- [Enterprise Deployment](../../docs/deployment/enterprise.md)
- [Performance Optimization](../../docs/guides/performance.md)
- [Security Best Practices](../../docs/security/)

## 🎓 Certification Path

These advanced examples prepare you for:

- **FLX Enterprise Architect**: Advanced architectural patterns
- **FLX Plugin Developer**: Custom adapter and plugin development
- **FLX Domain Expert**: Domain-driven design mastery
- **FLX Performance Engineer**: Optimization and scalability patterns

The advanced examples represent the culmination of FLX framework capabilities, demonstrating how to build enterprise-grade, scalable, and maintainable applications using sophisticated architectural patterns.
