# 🧪 Hexagonal Architecture Testing Guide

> **Document Type**: Testing Guide | **Audience**: Test engineers, QA developers, architects | **Scope**: Hexagonal architecture validation strategies

[![Testing](https://img.shields.io/badge/testing-hexagonal-blue.svg)](./index.md)
[![Architecture](https://img.shields.io/badge/architecture-validated-green.svg)](../../architecture/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Comprehensive testing suite ensuring proper hexagonal architecture implementation and separation of concerns in FLX Framework**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Testing**: [Testing Hub](./index.md) → **📄 Current**: Hexagonal Testing Guide

### **📍 Learning Path Position**

```
[Testing Hub](./index.md) → **[HEXAGONAL TESTING]** → [Integration Testing](./integration-testing-guide.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Testing Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔗 Source Code**: [FLX Tests](../../../flx/tests/)
- **🔗 Related**: [Port Testing](./ports-testing.md), [Adapter Testing](./adapters-testing.md)

---

## 📋 **Overview**

This guide provides a comprehensive testing suite to validate hexagonal architecture implementation in the FLX framework. It ensures proper separation of concerns, dependency direction, and architectural boundaries.

### **⬅️ Prerequisites**

- [Architecture Hub](../../architecture/index.md) - Essential hexagonal architecture patterns and port-adapter understanding
- [Testing Hub](./index.md) - Testing framework overview and basic testing concepts
- [Getting Started](../../getting-started/index.md) - Framework installation and setup for testing environment

### **What You'll Learn**

- How to test hexagonal architecture boundaries
- Port contract validation strategies
- Adapter implementation testing
- Dependency injection validation
- End-to-end architectural flow testing

---

## 🏗️ **Test Structure Overview**

### **Hexagonal Testing Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    E2E FLOW TESTS                           │
│            Complete architectural validation                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 BOUNDARY TESTS                              │
│         Domain isolation and dependency direction          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│         PORT CONTRACT TESTS │ ADAPTER IMPLEMENTATION TESTS  │
│     Interface validation    │    Concrete implementation    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 DEPENDENCY INJECTION TESTS                  │
│         Container configuration and binding validation       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Test Implementation Categories**

### **1. Port Contract Tests** - `test_port_contracts.py`

**Purpose**: Validate that port interfaces follow hexagonal architecture principles

```python
import pytest
from typing import get_type_hints
from flx.ports.base import BasePort
from flx.ports.outbound import DatabasePort, CachePort, HttpPort
from flx.ports.inbound import ApiPort, CliPort, CommandPort

class TestPortContracts:
    """Validate port interfaces follow hexagonal principles."""
    
    def test_ports_are_abstract_protocols(self):
        """Test that ports define abstract interfaces only."""
        port_classes = [DatabasePort, CachePort, HttpPort, ApiPort, CliPort]
        
        for port_class in port_classes:
            # Ports should be protocols (abstract interfaces)
            assert hasattr(port_class, '__protocol__') or \
                   port_class.__bases__[0].__name__ == 'Protocol'
    
    def test_ports_have_no_implementation(self):
        """Test that ports contain no concrete implementation."""
        import inspect
        
        for port_class in [DatabasePort, CachePort, HttpPort]:
            methods = inspect.getmembers(port_class, predicate=inspect.isfunction)
            
            for method_name, method in methods:
                if not method_name.startswith('_'):
                    # Check that method body contains only ellipsis or pass
                    source = inspect.getsource(method)
                    assert '...' in source or 'pass' in source, \
                        f"Port method {method_name} should not contain implementation"
    
    def test_ports_use_async_for_io_operations(self):
        """Test that I/O operations are properly async."""
        import inspect
        
        io_methods = ['save', 'find', 'get', 'set', 'connect', 'disconnect']
        
        for port_class in [DatabasePort, CachePort, HttpPort]:
            for method_name in dir(port_class):
                if any(io_method in method_name for io_method in io_methods):
                    method = getattr(port_class, method_name)
                    if callable(method):
                        assert inspect.iscoroutinefunction(method), \
                            f"I/O method {method_name} should be async"
    
    def test_ports_have_proper_type_hints(self):
        """Test that port methods have complete type hints."""
        from flx.ports.outbound.database import DatabasePort
        
        type_hints = get_type_hints(DatabasePort.save)
        assert 'return' in type_hints
        assert type_hints['return'] is not None or str(type_hints['return']) == 'bool'
    
    def test_ports_do_not_import_adapters(self):
        """Test that port modules don't import adapter implementations."""
        import ast
        import inspect
        from pathlib import Path
        
        port_files = Path('flx/ports').glob('**/*.py')
        
        for port_file in port_files:
            if port_file.name.startswith('__'):
                continue
                
            with open(port_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = node.module if hasattr(node, 'module') else ''
                    if module_name and 'adapter' in module_name.lower():
                        pytest.fail(f"Port file {port_file} imports adapter: {module_name}")
```

### **2. Adapter Implementation Tests** - `test_adapter_implementation.py`

**Purpose**: Validate that adapters correctly implement port interfaces

```python
class TestAdapterImplementation:
    """Test adapter implementations follow port contracts."""
    
    @pytest.fixture
    def database_adapter(self):
        """Create test database adapter."""
        from flx.adapters.database import DatabaseAdapter
        return DatabaseAdapter(connection_string="sqlite:///:memory:")
    
    @pytest.fixture
    def cache_adapter(self):
        """Create test cache adapter."""
        from flx.adapters.cache import CacheAdapter
        return CacheAdapter(backend="memory")
    
    def test_adapter_implements_all_port_methods(self, database_adapter):
        """Test adapter implements all required port methods."""
        from flx.ports.outbound.database import DatabasePort
        
        port_methods = [method for method in dir(DatabasePort) 
                       if not method.startswith('_') and callable(getattr(DatabasePort, method))]
        
        for method_name in port_methods:
            assert hasattr(database_adapter, method_name), \
                f"Adapter missing required method: {method_name}"
            
            adapter_method = getattr(database_adapter, method_name)
            assert callable(adapter_method), \
                f"Adapter method {method_name} is not callable"
    
    @pytest.mark.asyncio
    async def test_adapter_lifecycle_methods(self, database_adapter):
        """Test adapter lifecycle (connect/disconnect) works properly."""
        # Test connection
        await database_adapter.connect()
        assert database_adapter.is_connected is True
        
        # Test health check
        health = await database_adapter.health_check()
        assert health['status'] in ['healthy', 'degraded']
        assert 'connection' in health
        
        # Test disconnection
        await database_adapter.disconnect()
        assert database_adapter.is_connected is False
    
    @pytest.mark.asyncio
    async def test_adapter_error_handling(self, database_adapter):
        """Test adapter handles errors gracefully."""
        # Test operation before connection
        with pytest.raises(Exception):  # Should raise appropriate exception
            await database_adapter.save(None)
    
    def test_adapter_substitutability(self):
        """Test that different adapters can substitute each other."""
        from flx.adapters.database import SQLiteAdapter, PostgreSQLAdapter
        from flx.ports.outbound.database import DatabasePort
        
        # Both adapters should implement the same interface
        sqlite_methods = set(method for method in dir(SQLiteAdapter) 
                           if not method.startswith('_'))
        postgres_methods = set(method for method in dir(PostgreSQLAdapter) 
                             if not method.startswith('_'))
        
        # Core methods should be the same
        core_methods = {'save', 'find_by_id', 'connect', 'disconnect', 'health_check'}
        
        assert core_methods.issubset(sqlite_methods)
        assert core_methods.issubset(postgres_methods)
```

### **3. Dependency Injection Tests** - `test_dependency_injection.py`

**Purpose**: Validate dependency injection container configuration

```python
class TestDependencyInjection:
    """Test dependency injection container configuration."""
    
    @pytest.fixture
    def test_container(self):
        """Create clean DI container for testing."""
        from flx.core.container import Container
        container = Container()
        container.config.from_dict({
            'database': {
                'url': 'sqlite:///:memory:'
            },
            'cache': {
                'backend': 'memory'
            }
        })
        return container
    
    def test_container_wires_ports_to_adapters(self, test_container):
        """Test that container correctly binds ports to adapters."""
        test_container.wire()
        
        # Test database port binding
        database_port = test_container.database_port()
        assert database_port is not None
        
        # Test cache port binding
        cache_port = test_container.cache_port()
        assert cache_port is not None
        
        # Verify types
        from flx.ports.outbound.database import DatabasePort
        from flx.ports.outbound.cache import CachePort
        
        assert isinstance(database_port, DatabasePort)
        assert isinstance(cache_port, CachePort)
    
    def test_container_lifecycle_management(self, test_container):
        """Test container manages component lifecycle."""
        test_container.wire()
        
        # Start all components
        test_container.start()
        
        # Verify components are running
        database_port = test_container.database_port()
        assert database_port.is_connected is True
        
        # Stop all components
        test_container.stop()
        assert database_port.is_connected is False
    
    def test_container_plugin_integration(self, test_container):
        """Test container integrates with plugin system."""
        from flx.core.plugins import PluginManager
        
        plugin_manager = PluginManager()
        test_container.register_plugins(plugin_manager)
        
        # Verify plugins are registered
        assert len(plugin_manager.adapters) > 0
        assert len(plugin_manager.brokers) > 0
```

### **4. Architecture Boundary Tests** - `test_architecture_boundaries.py`

**Purpose**: Validate architectural boundaries and dependency direction

```python
class TestArchitectureBoundaries:
    """Test architectural boundaries and dependency direction."""
    
    def test_domain_layer_isolation(self):
        """Test domain layer doesn't depend on infrastructure."""
        import ast
        from pathlib import Path
        
        domain_files = Path('flx/core').glob('**/*.py')
        
        for domain_file in domain_files:
            with open(domain_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = node.module if hasattr(node, 'module') else ''
                    if module_name:
                        # Domain should not import infrastructure
                        forbidden_imports = ['flx.infra', 'flx.adapters', 'requests', 'sqlalchemy']
                        for forbidden in forbidden_imports:
                            assert forbidden not in module_name, \
                                f"Domain file {domain_file} imports infrastructure: {module_name}"
    
    def test_dependency_direction(self):
        """Test dependencies flow inward (toward domain)."""
        # Test that adapters depend on ports, not vice versa
        import ast
        from pathlib import Path
        
        adapter_files = Path('flx/adapters').glob('**/*.py')
        
        for adapter_file in adapter_files:
            with open(adapter_file, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            imports_ports = False
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = node.module if hasattr(node, 'module') else ''
                    if module_name and 'flx.ports' in module_name:
                        imports_ports = True
                        break
            
            # Adapters should import their corresponding ports
            if adapter_file.name != '__init__.py':
                assert imports_ports, f"Adapter {adapter_file} should import its port interface"
    
    def test_no_circular_dependencies(self):
        """Test for circular dependencies between modules."""
        import networkx as nx
        from pathlib import Path
        import ast
        
        # Build dependency graph
        G = nx.DiGraph()
        
        all_files = list(Path('flx').glob('**/*.py'))
        
        for file_path in all_files:
            if file_path.name.startswith('__'):
                continue
                
            module_name = str(file_path).replace('/', '.').replace('.py', '')
            G.add_node(module_name)
            
            with open(file_path, 'r') as f:
                content = f.read()
                
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        imported_module = node.module if hasattr(node, 'module') else ''
                        if imported_module and imported_module.startswith('flx'):
                            G.add_edge(module_name, imported_module)
            except SyntaxError:
                continue
        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(G))
            assert len(cycles) == 0, f"Circular dependencies found: {cycles}"
        except nx.NetworkXError:
            pass  # No cycles found
    
    def test_layer_boundaries(self):
        """Test that layers don't skip levels inappropriately."""
        # Application layer should not directly import infrastructure
        # Domain should not import application
        # etc.
        
        layer_dependencies = {
            'flx.core': [],  # Domain depends on nothing FLX-related
            'flx.ports': ['flx.core'],  # Ports can depend on domain
            'flx.adapters': ['flx.ports', 'flx.core'],  # Adapters depend on ports and domain
            'flx.infra': ['flx.adapters', 'flx.ports', 'flx.core'],  # Infrastructure depends on all
        }
        
        for layer, allowed_deps in layer_dependencies.items():
            self._check_layer_dependencies(layer, allowed_deps)
    
    def _check_layer_dependencies(self, layer_path: str, allowed_dependencies: list):
        """Helper to check layer dependency compliance."""
        import ast
        from pathlib import Path
        
        layer_files = Path(layer_path.replace('.', '/')).glob('**/*.py')
        
        for file_path in layer_files:
            if file_path.name.startswith('__'):
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
                
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        module_name = node.module if hasattr(node, 'module') else ''
                        if module_name and module_name.startswith('flx'):
                            # Check if this import is allowed
                            allowed = any(module_name.startswith(dep) for dep in allowed_dependencies)
                            assert allowed, \
                                f"Layer {layer_path} illegally imports {module_name} in {file_path}"
            except SyntaxError:
                continue
```

### **5. End-to-End Flow Tests** - `test_e2e_hexagonal_flow.py`

**Purpose**: Test complete architectural flow and integration

```python
class TestE2EHexagonalFlow:
    """Test end-to-end flow through hexagonal architecture."""
    
    @pytest.fixture
    async def complete_application(self):
        """Set up complete application for E2E testing."""
        from flx.core.container import Container
        from flx.core.application import Application
        
        container = Container()
        container.config.from_dict({
            'database': {'url': 'sqlite:///:memory:'},
            'cache': {'backend': 'memory'},
            'http': {'base_url': 'http://test.example.com'}
        })
        
        app = Application(container=container)
        await app.start()
        
        try:
            yield app
        finally:
            await app.stop()
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_user_creation_flow(self, complete_application):
        """Test complete flow from API request to persistence."""
        app = complete_application
        
        # Simulate API request (inbound port)
        api_adapter = app.container.api_adapter()
        
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User'
        }
        
        # Execute complete flow
        response = await api_adapter.post('/users', data=user_data)
        
        # Verify response
        assert response.status_code == 201
        assert 'user_id' in response.json()
        
        # Verify persistence (outbound port)
        database_adapter = app.container.database_port()
        saved_user = await database_adapter.find_by_username('testuser')
        
        assert saved_user is not None
        assert saved_user.email.value == 'test@example.com'
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_resilience_and_recovery(self, complete_application):
        """Test system resilience when components fail."""
        app = complete_application
        
        # Simulate database failure
        database_adapter = app.container.database_port()
        await database_adapter.disconnect()
        
        # System should handle gracefully
        api_adapter = app.container.api_adapter()
        response = await api_adapter.get('/users/health')
        
        # Should return degraded status, not crash
        assert response.status_code in [200, 503]
        if response.status_code == 503:
            health_data = response.json()
            assert health_data['status'] == 'degraded'
            assert 'database' in health_data['issues']
    
    @pytest.mark.e2e
    @pytest.mark.asyncio 
    async def test_adapter_communication_patterns(self, complete_application):
        """Test communication patterns between adapters."""
        app = complete_application
        
        # Test event flow between adapters
        user_service = app.container.user_application_service()
        
        user_data = {
            'username': 'eventuser',
            'email': 'event@example.com',
            'full_name': 'Event User'
        }
        
        # Create user (should trigger events)
        result = await user_service.create_user(user_data)
        
        # Give time for async event processing
        await asyncio.sleep(0.1)
        
        # Verify cache was updated via event
        cache_adapter = app.container.cache_port()
        cached_user = await cache_adapter.get(f"user:{result.user_id}")
        
        assert cached_user is not None
        assert cached_user['username'] == 'eventuser'
```

---

## 🚀 **Running the Tests**

### **Complete Test Suite**

```bash
# Run all hexagonal architecture tests
pytest tests/hexagonal/ -v

# With coverage reporting
pytest tests/hexagonal/ --cov=flx --cov-report=html

# Generate XML report for CI
pytest tests/hexagonal/ --junit-xml=reports/hexagonal-tests.xml
```

### **Category-Specific Tests**

```bash
# Port contract validation
pytest tests/hexagonal/test_port_contracts.py -v

# Adapter implementation tests
pytest tests/hexagonal/test_adapter_implementation.py -v

# Dependency injection tests
pytest tests/hexagonal/test_dependency_injection.py -v

# Architecture boundary validation
pytest tests/hexagonal/test_architecture_boundaries.py -v

# End-to-end flow tests
pytest tests/hexagonal/test_e2e_hexagonal_flow.py -v
```

### **Test Markers**

```bash
# Integration tests only
pytest tests/hexagonal/ -m integration

# E2E tests only  
pytest tests/hexagonal/ -m e2e

# Quick tests (exclude slow E2E)
pytest tests/hexagonal/ -m "not e2e and not slow"

# Boundary tests only
pytest tests/hexagonal/ -m boundaries

# Port tests only
pytest tests/hexagonal/ -m ports
```

---

## 📊 **Test Configuration**

### **Fixtures** (from `conftest.py`)

- **test_config_manager**: Standard test configuration
- **test_di_container**: Clean dependency injection container
- **test_database_adapter**: In-memory database adapter
- **test_cache_adapter**: In-memory cache adapter  
- **test_http_adapter**: Mock HTTP adapter
- **test_application**: Complete configured application

### **Quality Metrics**

1. **Code Coverage**: >90% for critical components
2. **Architectural Compliance**: 100% boundary adherence
3. **Port Substitutability**: All adapters interchangeable
4. **System Resilience**: Graceful failure recovery
5. **Performance**: Operations within acceptable limits

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Architecture Overview](../../architecture/index.md) - Understanding hexagonal architecture principles
- [Port Implementation Guide](../../architecture/ports/index.md) - Port interface design
- [Adapter Patterns](../../architecture/adapters/index.md) - Adapter implementation strategies

### **Next Steps**

- [Integration Testing](./integration-testing-guide.md) - Cross-component integration tests
- [Performance Testing](./performance-testing.md) - System performance validation
- [E2E Testing](./e2e-testing-guide.md) - Complete user journey testing

### **Related Topics**

- [Testing Ports](./ports-testing.md) - Focused port testing strategies
- [Testing Adapters](./adapters-testing.md) - Adapter-specific testing approaches
- [Unit Testing Guide](./unit-testing-guide.md) - Component-level testing

---

## 🆘 **Troubleshooting**

### **Common Issues**

**Port Contract Failures**:

```python
# Problem: Port imports adapter implementation
# Solution: Remove adapter imports from port modules
```

**Adapter Implementation Failures**:

```python  
# Problem: Adapter missing required methods
# Solution: Implement all port interface methods
```

**Dependency Injection Failures**:

```python
# Problem: No binding found for port
# Solution: Register adapter in DI container correctly
```

**Boundary Violations**:

```python
# Problem: Domain imports infrastructure
# Solution: Remove infrastructure dependencies from domain layer
```

### **Performance Issues**

- Use `-m "not slow"` to skip E2E tests during development
- Run tests in parallel with `pytest-xdist`
- Use test containers for realistic database testing

---

**📂 Hub**: [Testing Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
