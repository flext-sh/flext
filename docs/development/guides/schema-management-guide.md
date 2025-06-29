# Schema Management Guide - Development

> **Function**: Comprehensive API schema management and data validation | **Audience**: Developers, integration engineers | **Status**: ✅ Production Ready

[![Schema](https://img.shields.io/badge/schema-JSON_Schema-blue.svg)](#schema-format)
[![Validation](https://img.shields.io/badge/validation-automated-green.svg)](#schema-validation-adapter)
[![Integration](https://img.shields.io/badge/integration-FLX_Framework-orange.svg)](#integration-with-flext-framework)

**Enterprise schema management for API integration projects using FLX Framework 0.4.0+ with schema extraction, caching, validation, and hexagonal architecture integration**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Guides**: [Guides Hub](./index.md) → **📄 Current**: Schema Management

### **📍 Learning Path Position**

```
[Environment Configuration](./environment-configuration.md) → **[SCHEMA MANAGEMENT]** → [Development Tools](../tools/index.md)
```

## 🎯 **Quick Links**

- **📂 Section Hub**: [Guides Hub](./index.md)
- **🏠 Documentation Root**: [Root Index](../../index.md)
- **🔧 Related**: [API Integration Patterns](../../guides/integration/index.md)

---

## 📋 **Overview**

The FLX framework provides robust schema management capabilities for API integration projects. This guide covers schema extraction, caching, validation, and integration patterns within the hexagonal architecture.

## Schema Directory Structure

```
schemas/
├── README.md
├── {entity_name}.schema.json     # Entity-specific schemas
├── api.schema.json               # API-wide schema definitions
└── cache/                        # Cached schema files
    ├── extracted/
    └── generated/
```

## Schema Extraction

### Using CLI Tools

```bash
# Extract all schemas from API
flext schema extract --all --output-dir ./schemas

# Extract specific entity schema
flext schema extract --entity users --output-dir ./schemas

# Extract with validation
flext schema extract --entity users --validate --output-dir ./schemas
```

### Using Make Commands

```bash
# Extract all schemas
make extract-schemas

# Extract specific entity schema
make extract-schema ENTITY=users

# Validate existing schemas
make validate-schemas
```

### Programmatic Extraction

```python
from flext.adapters.schema import SchemaAdapter
from flext.core.config import Config

async def extract_schemas():
    config = Config.from_env()
    schema_adapter = SchemaAdapter(config=config)

    # Extract all entity schemas
    schemas = await schema_adapter.extract_all_schemas()

    # Extract specific entity schema
    user_schema = await schema_adapter.extract_schema("users")

    # Save to cache
    await schema_adapter.cache_schema("users", user_schema)
```

## Schema Format

Schemas follow JSON Schema specification:

```json
{
  "type": "object",
  "title": "user",
  "description": "User entity schema",
  "properties": {
    "id": {
      "type": "string",
      "description": "Unique identifier",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    },
    "name": {
      "type": "string",
      "description": "User's full name",
      "minLength": 1,
      "maxLength": 255
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User's email address"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp"
    }
  },
  "required": ["id", "name", "email"],
  "additionalProperties": false
}
```

## Integration with FLX Framework

### Schema Validation Adapter

```python
from flext.adapters.base import BaseAdapter
from flext.core.exceptions import ValidationError
import jsonschema

class SchemaValidationAdapter(BaseAdapter):
    """Adapter for schema validation within FLX framework."""

    def __init__(self, schema_cache_dir: str = "./schemas"):
        self.schema_cache_dir = schema_cache_dir
        self.schemas = {}

    async def load_schema(self, entity_name: str) -> dict:
        """Load schema from cache."""
        if entity_name not in self.schemas:
            schema_path = f"{self.schema_cache_dir}/{entity_name}.schema.json"
            with open(schema_path, 'r') as f:
                self.schemas[entity_name] = json.load(f)
        return self.schemas[entity_name]

    async def validate_data(self, entity_name: str, data: dict) -> bool:
        """Validate data against entity schema."""
        schema = await self.load_schema(entity_name)
        try:
            jsonschema.validate(data, schema)
            return True
        except jsonschema.ValidationError as e:
            raise ValidationError(f"Schema validation failed: {e.message}")
```

### Model Generation from Schemas

```python
from flext.core.entities import BaseEntity
from pydantic import create_model
import json

class SchemaModelGenerator:
    """Generate Pydantic models from JSON schemas."""

    @staticmethod
    def generate_model_from_schema(schema_path: str, model_name: str):
        """Generate Pydantic model from JSON schema."""
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Convert JSON schema to Pydantic field definitions
        fields = {}
        for prop_name, prop_def in schema.get('properties', {}).items():
            field_type = SchemaModelGenerator._get_python_type(prop_def)
            fields[prop_name] = (field_type, ...)

        # Create dynamic Pydantic model
        return create_model(model_name, **fields, __base__=BaseEntity)

    @staticmethod
    def _get_python_type(prop_def: dict):
        """Convert JSON schema type to Python type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': float,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        return type_map.get(prop_def.get('type'), str)
```

## Configuration

### Environment Variables

```bash
# Schema extraction settings
API_SCHEMA_PATH=api/schemas
API_SCHEMA_CACHE_DIR=./schemas
API_SCHEMA_VALIDATION_ENABLED=true

# Logging for schema operations
SCHEMA_LOG_LEVEL=INFO
SCHEMA_LOG_FILE=./logs/schema.log
```

### FLX Configuration

```python
from flext.core.config import Config

class SchemaConfig(Config):
    """Configuration for schema management."""

    schema_cache_dir: str = "./schemas"
    schema_validation_enabled: bool = True
    schema_auto_refresh: bool = False
    schema_cache_ttl: int = 3600  # 1 hour
```

## Logging and Monitoring

Log files are generated with specific naming conventions:

- `schema.log` - Main schema operations log
- `validation.log` - Schema validation events
- `extraction.log` - Schema extraction operations

### Log Configuration

```python
import logging
from flext.core.logging import configure_logging

# Configure schema-specific logging
configure_logging({
    'schema': {
        'level': 'INFO',
        'file': './logs/schema.log',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    },
    'validation': {
        'level': 'DEBUG',
        'file': './logs/validation.log'
    }
})
```

## Best Practices

### Schema Versioning

- Use semantic versioning for schema files
- Maintain backward compatibility
- Document breaking changes

### Performance Optimization

- Cache frequently used schemas
- Use async operations for schema loading
- Implement schema validation at adapter boundaries

### Error Handling

- Provide clear validation error messages
- Implement fallback mechanisms for missing schemas
- Log schema operations for debugging

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Environment Configuration](./environment-configuration.md) - Environment setup for schema management configuration
- [Development Hub](../index.md) - Development fundamentals before working with schemas
- [API Reference Hub](../../api-reference/index.md) - Understanding FLX Framework API for schema integration

### **Next Steps**

- [Development Tools](../tools/index.md) - Tools that work with schema management systems
- [Architecture Hub](../../architecture/index.md) - Hexagonal architecture patterns using schema validation
- [Oracle Integration Guides](../../guides/oracle/index.md) - Oracle-specific schema applications

### **Related Topics**

- [Integration Examples](../../examples/index.md) - Working examples using schema validation patterns
- [API Integration Patterns](../../guides/integration/index.md) - Integration strategies with schema management
- [Infrastructure Services](../../infrastructure/index.md) - Infrastructure supporting schema caching and validation
- [Security Hub](../../security/index.md) - Security considerations for schema validation and data handling

---

**📂 Hub**: [Guides Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
