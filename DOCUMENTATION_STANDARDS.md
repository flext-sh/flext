# PyAuto Documentation Standards
## Code-First Documentation Integration

**Version**: 1.0  
**Created**: 2025-01-06  
**Token**: `.doc-reorg`

## Overview

This document establishes standards for integrating documentation directly into code, eliminating the separation between `/docs/` and implementation. Documentation lives where developers work, improving discoverability and maintenance.

## Core Principles

### 1. **Code-First Documentation**
```
✅ Documentation lives in code directories
✅ Docstrings contain comprehensive API docs
✅ README.md files provide navigation and context
✅ Examples are executable and tested
❌ Separate /docs/ directory structure
❌ Disconnected documentation
```

### 2. **Three-Layer Documentation Structure**

#### **Layer 1: Inline Docstrings** 
- **Location**: Function/class docstrings in `.py` files
- **Content**: API reference, usage examples, parameters
- **Format**: Google-style docstrings with Markdown

```python
def create_adapter(config: AdapterConfig) -> BaseAdapter:
    """Create and configure an adapter instance.
    
    This function implements the factory pattern for adapter creation,
    supporting dynamic adapter discovery and configuration validation.
    
    Args:
        config: Adapter configuration including type, connection params,
               and feature flags. See `AdapterConfig` for details.
    
    Returns:
        Configured adapter instance ready for use.
        
    Raises:
        ConfigurationError: If config validation fails
        AdapterNotFoundError: If adapter type is not registered
        
    Examples:
        Basic adapter creation:
        ```python
        config = AdapterConfig(type="postgresql", host="localhost")
        adapter = create_adapter(config)
        await adapter.connect()
        ```
        
        With advanced configuration:
        ```python
        config = AdapterConfig(
            type="postgresql",
            host="db.example.com",
            pool_size=20,
            retry_strategy="exponential"
        )
        adapter = create_adapter(config)
        ```
    
    Note:
        This function is thread-safe and can be called concurrently.
        Adapters are registered via `register_adapter()` function.
        
    See Also:
        - `register_adapter()`: For registering custom adapters
        - `AdapterConfig`: For configuration options
        - `../examples/adapters/`: For complete examples
    """
```

#### **Layer 2: Module README.md Files**
- **Location**: `README.md` in each code directory
- **Content**: Module overview, architecture, navigation, examples
- **Format**: Structured Markdown with navigation links

#### **Layer 3: Code Comments**
- **Location**: Inline `#` comments in complex logic
- **Content**: Implementation details, architectural decisions
- **Format**: Clear, concise explanations

### 3. **Navigation Structure**

#### **Root Level Navigation**
```
/pyauto/
├── README.md                    # 🏠 Main project overview + navigation
├── flx/README.md               # 🔧 Core framework documentation
├── flx-database-oracle/README.md   # 🗄️ Database integration docs
├── oud-automation/README.md    # 🔐 Directory automation docs
└── dc-code-analyzer/README.md  # 📊 Code analysis tool docs
```

#### **Module Level Navigation**
```
/flx/src/flx/
├── README.md                   # 🏗️ Framework overview + API index
├── core/README.md             # 🎯 Domain layer documentation
├── adapters/README.md         # 🔌 Adapters development guide
├── ports/README.md            # 🚪 Ports interface documentation
├── application/README.md      # 🚀 Application layer guide
└── testing/README.md          # 🧪 Testing framework guide
```

### 4. **Content Migration Strategy**

#### **From `/docs/` to Code Integration**

**Current Structure** → **New Structure**
```
docs/api-reference/core/         → flx/src/flx/core/README.md + docstrings
docs/guides/testing/             → flx/src/flx/testing/README.md + examples/
docs/architecture/adapters/      → flx/src/flx/adapters/README.md
docs/examples/                   → {module}/examples/ + README.md
docs/getting-started/            → flx/README.md + quickstart section
```

#### **Migration Process**
1. **Extract**: Copy relevant content from `/docs/`
2. **Transform**: 
   - API docs → docstrings
   - Guides → README.md
   - Examples → `examples/` subdirectories
3. **Integrate**: Embed into code structure
4. **Link**: Create navigation between modules
5. **Validate**: Ensure discoverability
6. **Remove**: Delete original `/docs/` files

### 5. **Content Types and Placement**

| Content Type | Destination | Format | Example |
|-------------|-------------|---------|---------|
| **API Reference** | Docstrings | Google-style | Function/class docs |
| **Architecture Guides** | Module README.md | Markdown sections | `/flx/core/README.md` |
| **Usage Examples** | `examples/` subdirs | Executable Python | `/flx/core/examples/` |
| **Getting Started** | Root README.md | Markdown tutorial | `/flx/README.md` |
| **Configuration** | Module README.md | YAML/JSON examples | Config sections |
| **Troubleshooting** | Module README.md | FAQ format | Common issues |

### 6. **Docstring Standards**

#### **Module Docstrings**
```python
"""FLX Core Domain Layer.

This module implements the domain layer of hexagonal architecture, providing
pure business logic abstractions with no external dependencies.

Architecture:
    The domain layer contains:
    - Entities and value objects (DDD patterns)
    - Domain events for business logic
    - Pure interfaces (protocols)
    - Business rule validation

Key Components:
    - AggregateRoot: Domain aggregate pattern
    - Entity: Domain entity with identity
    - ValueObject: Immutable value objects
    - DomainEvent: Business event publishing
    
Examples:
    Basic domain entity creation:
    ```python
    from flx.core import Entity, ValueObject
    
    class OrderId(ValueObject):
        value: str
    
    class Order(Entity[OrderId]):
        def __init__(self, order_id: OrderId, customer_id: str):
            super().__init__(order_id)
            self.customer_id = customer_id
    ```

See Also:
    - README.md: Complete domain layer guide
    - examples/: Domain modeling examples
    - ../ports/: Port interfaces for domain
"""
```

#### **Class Docstrings**
```python
class AggregateRoot(Entity[T]):
    """Domain aggregate root with event publishing capabilities.
    
    Aggregates are consistency boundaries in domain-driven design,
    responsible for maintaining business invariants and publishing
    domain events when state changes occur.
    
    This implementation provides:
    - Event collection and publishing
    - Invariant validation
    - Transaction boundary management
    
    Attributes:
        _domain_events: Collection of unpublished domain events
        
    Examples:
        Creating a custom aggregate:
        ```python
        class OrderAggregate(AggregateRoot[OrderId]):
            def __init__(self, order_id: OrderId):
                super().__init__(order_id)
                self._items: List[OrderItem] = []
            
            def add_item(self, item: OrderItem) -> None:
                self._items.append(item)
                self._record_event(OrderItemAdded(self.id, item.id))
        ```
    
    Note:
        Aggregates should be designed as consistency boundaries.
        Keep aggregates small and focused on a single business concept.
        
    See Also:
        - Entity: Base entity implementation
        - DomainEvent: Event publishing mechanism
        - examples/domain/: Complete aggregate examples
    """
```

#### **Function Docstrings**
```python
async def create_adapter(
    adapter_type: str, 
    config: AdapterConfig,
    *,
    registry: Optional[AdapterRegistry] = None
) -> BaseAdapter:
    """Create and configure an adapter instance.
    
    Factory function for creating adapters with proper configuration
    validation and dependency injection. Supports both built-in and
    custom adapter types through the adapter registry.
    
    Args:
        adapter_type: Type identifier for the adapter (e.g., "postgresql", 
                     "redis", "http_client"). Must be registered in registry.
        config: Configuration object containing adapter-specific settings.
                Validated before adapter creation.
        registry: Optional adapter registry. Uses global registry if None.
        
    Returns:
        Configured adapter instance, ready for connection and use.
        
    Raises:
        AdapterNotFoundError: If adapter_type is not in registry
        ConfigurationError: If config validation fails
        DependencyError: If required dependencies are missing
        
    Examples:
        Database adapter creation:
        ```python
        config = PostgreSQLConfig(
            host="localhost",
            port=5432,
            database="myapp"
        )
        adapter = await create_adapter("postgresql", config)
        await adapter.connect()
        ```
        
        Custom adapter with registry:
        ```python
        registry = AdapterRegistry()
        registry.register("custom", CustomAdapter)
        
        adapter = await create_adapter(
            "custom", 
            config, 
            registry=registry
        )
        ```
    
    Note:
        This function is async to support adapter initialization that
        may require I/O operations (e.g., connection validation).
        
    See Also:
        - register_adapter(): Register custom adapter types
        - AdapterConfig: Base configuration class
        - examples/adapters/: Complete adapter examples
    """
```

### 7. **README.md Structure Template**

```markdown
# {Module Name}

**{Brief description}**

## Quick Start

{30-second usage example}

## Architecture

{High-level design explanation}

## Components

{List of main components with links}

## Examples

{Links to examples/ subdirectory}

## API Reference

{Links to key classes/functions with brief descriptions}

## Configuration

{Configuration examples and options}

## Common Patterns

{Frequently used patterns and best practices}

## Troubleshooting

{Common issues and solutions}

## Navigation

{Links to related modules and parent/child documentation}
```

### 8. **Examples Structure**

```
{module}/examples/
├── README.md                   # Examples index and navigation
├── basic/
│   ├── README.md              # Basic usage examples
│   ├── quickstart.py          # Minimal working example
│   └── configuration.py       # Basic configuration
├── advanced/
│   ├── README.md              # Advanced usage patterns
│   ├── custom_adapter.py      # Custom implementation
│   └── performance.py         # Performance optimization
├── integrations/
│   ├── README.md              # Integration examples
│   └── with_fastapi.py        # Framework integration
└── testing/
    ├── README.md              # Testing examples
    ├── unit_tests.py          # Unit testing patterns
    └── integration_tests.py   # Integration testing
```

### 9. **Cross-Reference System**

#### **Link Patterns**
```markdown
# Internal Links (within same project)
[Core Domain](../core/README.md)
[Adapter API](adapters.py#L45)

# Cross-Project Links (between projects)
[Oracle Integration](../../flx-database-oracle/README.md)
[WMS Integration](../../flx-http-oracle-wms/README.md)

# Code References
[`create_adapter()`](adapters.py#create_adapter)
[`BaseAdapter`](base.py#BaseAdapter)
```

#### **Navigation Breadcrumbs**
```markdown
🏠 [PyAuto](../../../README.md) > 🔧 [FLX](../../README.md) > 🎯 [Core](README.md)
```

### 10. **Migration Checklist**

#### **Per Module Migration**
- [ ] Create module `README.md` with overview
- [ ] Extract API docs to docstrings
- [ ] Create `examples/` subdirectory with working code
- [ ] Add navigation links to parent/child modules
- [ ] Move relevant content from `/docs/`
- [ ] Validate examples are executable
- [ ] Test navigation links
- [ ] Remove original `/docs/` files

#### **Quality Gates**
- [ ] All public APIs have comprehensive docstrings
- [ ] Examples run without errors
- [ ] Navigation links work correctly
- [ ] README.md files are comprehensive
- [ ] Cross-references are accurate
- [ ] Content is discoverable from code

### 11. **Implementation Priority**

#### **Phase 1: Core Framework (FLX)**
1. `flx/src/flx/core/` - Domain layer documentation
2. `flx/src/flx/adapters/` - Adapter framework docs
3. `flx/src/flx/ports/` - Ports interface docs
4. `flx/src/flx/testing/` - Testing framework docs

#### **Phase 2: Extensions**
1. `flx-database-oracle/` - Database integration
2. `flx-http-oracle-oic/` - OIC integration
3. `flx-http-oracle-wms/` - WMS integration

#### **Phase 3: Projects**
1. `oud-automation/` - Directory automation
2. `dc-code-analyzer/` - Code analysis tools
3. `client-b-poc-oic-wms/` - Implementation projects

### 12. **Validation Process**

#### **Documentation Quality**
- Comprehensive docstrings for all public APIs
- Working examples that can be executed
- Clear navigation between modules
- Accurate cross-references

#### **Developer Experience**
- Quick discovery of relevant documentation
- Examples that solve real problems
- Clear troubleshooting guidance
- Consistent structure across modules

---

## Implementation Notes

This standard enables:
- ✅ **Developer-friendly**: Documentation where developers work
- ✅ **Always current**: Docs updated with code changes
- ✅ **Discoverable**: No separate documentation site needed
- ✅ **Executable**: Examples that actually work
- ✅ **Navigable**: Clear paths between related concepts
- ✅ **Maintainable**: Single source of truth for features