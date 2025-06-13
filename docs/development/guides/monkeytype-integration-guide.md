# MonkeyType Integration for Type Discovery

This project includes integration with [MonkeyType](https://github.com/Instagram/MonkeyType), a runtime type collection tool that helps improve mypy and Pydantic type annotations.

## Overview

MonkeyType collects runtime types during test execution and can then apply them back to your code as type annotations. This is especially useful for:

1. Discovering types in existing untyped code
2. Generating Pydantic model field types based on actual usage
3. Improving mypy coverage with minimal effort
4. Finding type inconsistencies in your codebase

## Prerequisites

MonkeyType has been added to the project's dev dependencies. Make sure your environment is up to date by running:

```bash
make install-dev
```

## Usage

The integration provides several make targets to work with MonkeyType:

### Collecting Types

To collect types by running tests with MonkeyType instrumentation:

```bash
make monkeytype-test PROJECT=<project_name> [TEST_PATH=<test_file_or_directory>]
```

For example:

```bash
# Run all tests in a project with MonkeyType
make monkeytype-test PROJECT=flx

# Run a specific test file with MonkeyType
make monkeytype-test PROJECT=flx TEST_PATH=tests/unit/test_entities.py
```

### Viewing Collected Types

To list modules that have type information collected:

```bash
make monkeytype-list PROJECT=<project_name>
```

### Applying Types

To apply the collected types to a specific module:

```bash
make monkeytype-apply PROJECT=<project_name> MODULE=<module_path>
```

For example:

```bash
make monkeytype-apply PROJECT=flx MODULE=flx.core.entities
```

### Generating Type Stubs

To generate stub files with the collected types (without modifying your code):

```bash
make monkeytype-stub PROJECT=<project_name> MODULE=<module_path>
```

## Integration with FLX Framework

MonkeyType is particularly valuable for the FLX framework because:

### **Domain-Driven Design Types**

MonkeyType can help improve type annotations in:

```python
# Before MonkeyType
class Order:
    def __init__(self, customer_id, items):
        self.customer_id = customer_id
        self.items = items

# After MonkeyType collection
class Order:
    def __init__(self, customer_id: str, items: List[Dict[str, Any]]) -> None:
        self.customer_id = customer_id
        self.items = items
```

### **Pydantic Model Enhancement**

Convert discovered types to proper Pydantic models:

```python
# MonkeyType discovers these types
class UserData:
    def __init__(self, name: str, email: str, age: Optional[int] = None) -> None:
        self.name = name
        self.email = email
        self.age = age

# Convert to FLX Entity
from flx.core.entities import Entity

class User(Entity):
    name: str
    email: str
    age: Optional[int] = None
    
    def change_email(self, new_email: str) -> None:
        self.email = new_email
        self.touch()
```

### **Adapter Type Discovery**

MonkeyType helps with adapter interfaces:

```python
# Before: Adapter without proper types
class OracleWmsAdapter:
    def list_items(self, facility_id, filters):
        # Implementation...
        pass

# After MonkeyType: Proper types discovered
class OracleWmsAdapter:
    def list_items(self, facility_id: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implementation...
        pass

# Convert to proper FLX adapter
from flx.ports.outbound import WmsPort

class OracleWmsAdapter(WmsPort):
    async def list_items(self, facility_id: str, filters: Dict[str, Any]) -> List[WmsItem]:
        # Implementation...
        pass
```

## Working with Pydantic

When working with Pydantic models, MonkeyType can help discover field types. However, you will need to manually convert the standard Python annotations to Pydantic field definitions:

Before:

```python
class MyModel:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value or {}
```

After MonkeyType:

```python
class MyModel:
    def __init__(self, name: str, value: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.value = value or {}
```

Convert to FLX Value Object:

```python
from flx.core.domain.value_objects import ValueObject
from pydantic import Field

class MyModel(ValueObject):
    name: str
    value: Dict[str, Any] = Field(default_factory=dict)
```

## Best Practices for FLX Development

1. **Run with Comprehensive Tests**: Make sure your tests exercise a wide range of code paths for the most accurate type collection.

2. **Focus on Core Domain**: Use MonkeyType primarily on core domain logic where types are most critical:

   ```bash
   make monkeytype-test PROJECT=flx TEST_PATH=tests/unit/core/
   ```

3. **Review Applied Types**: Always review the types applied by MonkeyType and refine them for FLX patterns:
   - Convert to proper Entity/ValueObject/AggregateRoot
   - Use proper port interfaces
   - Follow hexagonal architecture patterns

4. **Integration with Type Checking**: After applying types, run the FLX type checking:

   ```bash
   make lint  # Includes mypy
   make typecheck
   ```

5. **Iterative Process**: Type collection and application is an iterative process. You may need to run MonkeyType multiple times with different tests to get comprehensive coverage.

## FLX-Specific Workflow

1. **Domain Layer Types**:

   ```bash
   # Collect types from domain tests
   make monkeytype-test PROJECT=flx TEST_PATH=tests/unit/core/
   
   # Apply to core entities
   make monkeytype-apply PROJECT=flx MODULE=flx.core.entities
   
   # Apply to value objects
   make monkeytype-apply PROJECT=flx MODULE=flx.core.domain.value_objects
   ```

2. **Application Layer Types**:

   ```bash
   # Collect from application service tests
   make monkeytype-test PROJECT=flx TEST_PATH=tests/unit/application/
   
   # Apply to services
   make monkeytype-apply PROJECT=flx MODULE=flx.application.services
   ```

3. **Infrastructure Layer Types**:

   ```bash
   # Collect from adapter tests
   make monkeytype-test PROJECT=flx-http-oracle-wms TEST_PATH=tests/
   
   # Apply to adapters
   make monkeytype-apply PROJECT=flx-http-oracle-wms MODULE=flx_http_oracle_wms.adapters
   ```

## Customization

The underlying implementation is in `scripts/monkeytype_runner.py`, which you can customize as needed for more advanced usage.

## Example Workflow with Oracle Integration

1. Write tests for Oracle WMS integration:

   ```python
   def test_wms_item_listing():
       client = WmsClient(config)
       items = client.list_items("FACILITY_001")
       assert len(items) > 0
   ```

2. Run MonkeyType collection:

   ```bash
   make monkeytype-test PROJECT=flx-http-oracle-wms
   ```

3. View collected modules:

   ```bash
   make monkeytype-list PROJECT=flx-http-oracle-wms
   ```

4. Apply types to WMS client:

   ```bash
   make monkeytype-apply PROJECT=flx-http-oracle-wms MODULE=flx_http_oracle_wms.client
   ```

5. Convert to proper FLX patterns:

   ```python
   # Before
   def list_items(self, facility_id):
       # ...
   
   # After MonkeyType
   def list_items(self, facility_id: str) -> List[Dict[str, Any]]:
       # ...
   
   # After FLX conversion
   async def list_items(self, facility_id: str) -> List[WmsItem]:
       # ...
   ```

6. Run FLX validation:

   ```bash
   make lint
   make test
   ```

## Integration with Development Workflow

MonkeyType integrates with the FLX development workflow:

```bash
# 1. Development cycle with type discovery
make monkeytype-test PROJECT=flx
make monkeytype-apply PROJECT=flx MODULE=flx.core.entities

# 2. Validate with FLX standards
make lint
make typecheck

# 3. Sync dependencies if needed
make sync-dependencies

# 4. Full test suite
make test
```

## Limitations

- MonkeyType can only detect types that are actually used during test execution
- Some complex types (generics, unions) may need manual refinement
- Pydantic-specific features (Field, validator, etc.) need to be added manually
- Types for functions or methods never called in tests won't be collected
- FLX-specific patterns (Entity lifecycle, domain events) need manual implementation

## Related Documentation

- [Development Standardization Plan](standardization-plan.md) - Type checking standards
- [Dependency Synchronization Guide](dependency-synchronization-guide.md) - Managing dependencies
- [FLX Core API Reference](../api-reference/core-api-reference.md) - Type patterns to follow

---

**Implementation Status**: ✅ Current and Active  
**Script Location**: `/scripts/monkeytype_runner.py`  
**Last Updated**: January 2025  
**Maintained By**: FLX Development Team

---

MonkeyType integration helps maintain type safety across the FLX hexagonal architecture while reducing manual type annotation effort.
